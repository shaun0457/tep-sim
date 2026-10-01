"""Deterministic adapter over the pinned Python TEPSimulator."""
import hashlib
import json
import math
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from uuid import uuid4

from tep.simulator import TEPSimulator, ControlMode as UpstreamControlMode
from .contracts import (EnvironmentConfig, ControlMode, Observation,
                        DisturbanceIntervention, MVIntervention, MVConstraint,
                        EnvironmentEvent, StepResult, ArtifactRef, RolloutResult,
                        Branch, BranchRandomnessPolicy, ReplaySpec, Snapshot,
                        SnapshotFidelity)
from .errors import (InvalidIntervention, UnknownVariable, UnsupportedCapability,
                     IncompatibleControlMode, InvalidEnvironmentState,
                     SimulationFailure, SnapshotFailure, UnsupportedScenarioError,
                     AmbiguousScenarioError, InvalidScenarioError)
from .capability import CAPABILITY_VERSION, build_capability_registry
from .registry import REGISTRY, UPSTREAM_REVISION
from .safety import SAFETY_LIMITS_VERSION, evaluate_safety, safety_margins
from .scenario import (SCENARIO_MAPPING_VERSION, AmbiguousScenario, InvalidScenario,
                       SupportedScenario, UnsupportedScenario, compile_scenario)
from .snapshot import (ENVIRONMENT_VERSION, RANDOMNESS_POLICY, artifact_ref,
                       create_snapshot_artifacts, load_replay_spec,
                       load_snapshot, load_snapshot_payload, observation_sha256,
                       persist_replay_spec)


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _verify_upstream():
    import tep
    root = Path(tep.__file__).parent
    hashes = json.loads(Path(__file__).with_name("upstream_hashes.json").read_text())
    for name, expected in hashes.items():
        path = root / name
        if not path.is_file() or hashlib.sha256(
                path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != expected:
            raise UnsupportedCapability(f"upstream source differs from pinned revision: {name}")


def _observation_data(obs):
    return {"simulation_time": obs.simulation_time,
            "measurements": dict(obs.measurements),
            "manipulated_variables": dict(obs.manipulated_variables),
            "active_disturbances": obs.active_disturbances,
            "shutdown_state": obs.shutdown_state,
            "safety_margins": dict(obs.safety_margins)}


class TEPEnvironment:
    """One mutable world. Use reset before operating and close when finished.

    Horizons are hours and must be an integral number of one-second steps.
    record_interval counts integration steps. MV constraints are manual-mode
    admissibility bounds; tightening past the current setpoint is rejected.
    """

    def __init__(self, config: EnvironmentConfig):
        if not isinstance(config, EnvironmentConfig):
            raise InvalidEnvironmentState("EnvironmentConfig required")
        if type(config.seed) is not int or not 0 < config.seed <= 2**53:
            raise InvalidEnvironmentState("seed must be a positive exact float64 integer")
        if not isinstance(config.control_mode, ControlMode):
            raise InvalidEnvironmentState("explicit ControlMode required")
        if type(config.record_interval) is not int or config.record_interval < 1:
            raise InvalidEnvironmentState("record_interval must be a positive step count")
        if config.backend != "python":
            raise UnsupportedCapability("A1 supports the pinned Python backend only")
        if config.upstream_revision != UPSTREAM_REVISION:
            raise UnsupportedCapability("upstream revision differs from the supported pin")
        _verify_upstream()
        self.config = config
        self._sim = None
        self._closed = False
        self._terminated = False
        self._constraints = {}
        self._schedule = []
        self._events = []
        self._scenarios = []
        self._artifacts = []
        self._snapshots = []
        self._parent_snapshot_id = None
        self._branch_created_at = None
        self._branch_randomness_policy = None
        self._origin_snapshot = None
        self._replay_of_branch_id = None

    def capabilities(self):
        """Versioned, machine-readable capability registry (no model inference)."""
        return build_capability_registry(self.config.backend)

    def compile_scenario(self, request):
        """Deterministically compile a semantic request for this config. No mutation.

        When the environment is live, state preconditions are checked against the
        current observation; otherwise they are reported as unchecked.
        """
        live = not self._closed and self._sim is not None
        return compile_scenario(request, self.config.control_mode,
                                self.observe() if live else None)

    def apply_scenario(self, request):
        """Compile, validate every intervention, then apply. Rejections never mutate."""
        result = compile_scenario(request, self.config.control_mode, self.observe())
        if isinstance(result, UnsupportedScenario):
            raise UnsupportedScenarioError(result)
        if isinstance(result, AmbiguousScenario):
            raise AmbiguousScenarioError(result)
        if not isinstance(result, SupportedScenario):
            raise InvalidScenarioError(result if isinstance(result, InvalidScenario)
                                       else InvalidScenario("compilation failed"))
        planned = {"constraints": {}, "mv": {}}
        plans = []
        for intervention in result.interventions:
            plan = self._validate(intervention, planned)
            if isinstance(intervention, MVConstraint):
                planned["constraints"][intervention.target] = plan[1:]
            elif isinstance(intervention, MVIntervention):
                planned["mv"][intervention.target] = intervention.value
            plans.append(plan)
        for intervention, plan in zip(result.interventions, plans):
            self._commit(intervention, plan, persist=False)
        self._scenarios.append({"time": self._sim.time, "step_count": self._sim.step_count,
                                **dict(result.provenance)})
        self._events.append(EnvironmentEvent("scenario", self._sim.time, result.scenario_id))
        self._persist(None)
        return result

    def evaluate_safety(self, result):
        """Deterministic safety evaluation of a rollout's checksummed telemetry."""
        return evaluate_safety(result)

    def _ready(self, *, advancing=False):
        if self._closed or self._sim is None:
            raise InvalidEnvironmentState("environment is closed or not reset")
        if advancing and self._terminated:
            raise InvalidEnvironmentState("run has terminated; reset required")

    def reset(self):
        if self._closed:
            raise InvalidEnvironmentState("environment is closed")
        if self._sim is not None:
            self._persist("reset")
        try:
            sim = TEPSimulator(random_seed=self.config.seed,
                               control_mode=UpstreamControlMode(self.config.control_mode.value),
                               backend=self.config.backend)
            sim.initialize()
        except Exception as exc:
            raise SimulationFailure("upstream reset failed") from exc
        self._sim = sim
        self._terminated = False
        self.run_id = uuid4().hex
        self.branch_id = "root"
        self._directory = Path(self.config.artifact_directory) / self.run_id
        self._directory.mkdir(parents=True, exist_ok=False)
        self._constraints, self._schedule, self._artifacts, self._snapshots = {}, [], [], []
        self._parent_snapshot_id = None
        self._branch_created_at = None
        self._branch_randomness_policy = None
        self._origin_snapshot = None
        self._replay_of_branch_id = None
        self._scenarios = []
        self._events = [EnvironmentEvent("reset", 0.0)]
        self._persist(None)
        return self.observe()

    def observe(self):
        self._ready()
        measurements = {f"XMEAS({i})": float(v)
                        for i, v in enumerate(self._sim.get_measurements(), 1)}
        return Observation(self._sim.time, measurements,
            {f"XMV({i})": float(v) for i, v in enumerate(self._sim.get_manipulated_vars(), 1)},
            tuple(f"IDV({i})" for i in self._sim.get_active_disturbances()),
            bool(self._sim.is_shutdown()),
            safety_margins(measurements))

    def apply(self, intervention):
        self._commit(intervention, self._validate(intervention))

    def _validate(self, intervention, planned=None):
        """All checks for one intervention; returns a commit plan without mutating.

        ``planned`` overlays constraints/MV setpoints from earlier interventions of
        the same not-yet-committed scenario so each is checked against its effects.
        """
        planned = planned if planned is not None else {"constraints": {}, "mv": {}}
        # Required ordering: schema -> identity -> capability -> bounds -> mode -> preconditions.
        if type(intervention) not in (DisturbanceIntervention, MVIntervention, MVConstraint):
            raise InvalidIntervention("typed intervention required")
        if type(intervention.target) is not str:
            raise InvalidIntervention("target must be a canonical string")
        constraint = isinstance(intervention, MVConstraint)
        values = ([intervention.min_value, intervention.max_value] if constraint
                  else [intervention.value])
        if any(v is not None and not _finite(v) for v in values):
            raise InvalidIntervention("values must be finite numbers")
        if not constraint and values[0] is None:
            raise InvalidIntervention("value required")
        disturbance = isinstance(intervention, DisturbanceIntervention)
        prefix = "IDV(" if disturbance else "XMV("
        if intervention.target not in REGISTRY or not intervention.target.startswith(prefix):
            raise UnknownVariable(intervention.target)
        if disturbance:
            if type(intervention.value) is not int or intervention.value not in (0, 1):
                raise InvalidIntervention("IDV value must be integer 0 or 1")
        elif any(v is not None and not 0 <= v <= 100 for v in values):
            raise InvalidIntervention("MV bounds are 0..100 percent")
        if constraint:
            lo = 0.0 if intervention.min_value is None else intervention.min_value
            hi = 100.0 if intervention.max_value is None else intervention.max_value
            if lo > hi or all(v is None for v in values):
                raise InvalidIntervention("constraint requires ordered bounds")
        if not disturbance and self.config.control_mode is not ControlMode.MANUAL:
            raise IncompatibleControlMode("direct MV operations require MANUAL")
        self._ready(advancing=True)
        index = REGISTRY[intervention.target].index
        if constraint:
            current = planned["mv"].get(intervention.target)
            if current is None:
                current = self.observe().manipulated_variables[intervention.target]
            if not lo <= current <= hi:
                raise InvalidIntervention("current setpoint violates proposed constraint")
        elif not disturbance:
            low, high = planned["constraints"].get(
                intervention.target, self._constraints.get(intervention.target, (0, 100)))
            if not low <= intervention.value <= high:
                raise InvalidIntervention("setpoint violates active constraint")
        return (index, lo, hi) if constraint else (index, None, None)

    def _commit(self, intervention, plan, persist=True):
        index, lo, hi = plan
        constraint = isinstance(intervention, MVConstraint)
        disturbance = isinstance(intervention, DisturbanceIntervention)
        try:
            if constraint:
                self._constraints[intervention.target] = (lo, hi)
            elif disturbance:
                self._sim.set_disturbance(index, intervention.value)
            else:
                self._sim.set_mv(index, intervention.value)
        except Exception as exc:
            self._terminated = True
            self._persist("simulation_failure")
            raise SimulationFailure("upstream intervention failed") from exc
        self._schedule.append({"time": self._sim.time,
                               "step_count": self._sim.step_count,
                               "type": type(intervention).__name__,
                               **asdict(intervention)})
        self._events.append(EnvironmentEvent("intervention", self._sim.time, repr(intervention)))
        if persist:
            self._persist(None)

    def step(self):
        self._ready(advancing=True)
        try:
            running = self._sim.step()
            if not running and not self._sim.is_shutdown():
                raise ArithmeticError("upstream numerical instability")
            obs = self.observe()
            if not all(math.isfinite(v) for v in (*obs.measurements.values(),
                                                 *obs.manipulated_variables.values())):
                raise ArithmeticError("nonfinite upstream observation")
        except Exception as exc:
            self._terminated = True
            self._events.append(EnvironmentEvent("simulation_failure", self._sim.time))
            self._persist("simulation_failure")
            raise SimulationFailure("upstream step failed") from exc
        events = ()
        if not running:
            self._terminated = True
            events = (EnvironmentEvent("shutdown", self._sim.time),)
            self._events.extend(events)
            self._persist("shutdown")
        return StepResult(obs, events)

    def _artifact(self, path):
        return ArtifactRef(str(path.resolve()), hashlib.sha256(path.read_bytes()).hexdigest())

    def _persist(self, reason):
        config = asdict(self.config)
        config["artifact_directory"] = str(config["artifact_directory"])
        data = {"environment_version": ENVIRONMENT_VERSION,
                "upstream_revision": UPSTREAM_REVISION,
                "capability_version": CAPABILITY_VERSION,
                "scenario_mapping_version": SCENARIO_MAPPING_VERSION,
                "safety_limits_version": SAFETY_LIMITS_VERSION,
                "scenarios": self._scenarios,
                "seed": self.config.seed, "config": config, "run_id": self.run_id,
                "branch_id": self.branch_id, "intervention_schedule": self._schedule,
                "termination_reason": reason, "events": [asdict(e) for e in self._events],
                "artifacts": [asdict(a) for a in self._artifacts],
                "snapshots": [asdict(a) for a in self._snapshots],
                "parent_snapshot_id": self._parent_snapshot_id,
                "branch_randomness_policy": (self._branch_randomness_policy.value
                                             if self._branch_randomness_policy else None),
                "branch_created_at": self._branch_created_at,
                "replay_of_branch_id": self._replay_of_branch_id}
        path = self._directory / "provenance.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, sort_keys=True, allow_nan=False), encoding="utf-8")
        temporary.replace(path)
        return self._artifact(path)

    def rollout(self, horizon):
        self._ready(advancing=True)
        if not _finite(horizon) or horizon <= 0:
            raise InvalidEnvironmentState("horizon must be positive finite hours")
        count = round(horizon * 3600)
        if count < 1 or not math.isclose(horizon * 3600, count, abs_tol=1e-8, rel_tol=0):
            raise InvalidEnvironmentState("horizon must span integral one-second steps")
        path = self._directory / f"telemetry-{len(self._artifacts)}.jsonl"
        reason = "horizon_reached"
        self._events.append(EnvironmentEvent("rollout", self._sim.time, str(horizon)))
        try:
            with path.open("w", encoding="utf-8") as stream:
                stream.write(json.dumps(_observation_data(self.observe())) + "\n")
                for n in range(1, count + 1):
                    result = self.step()
                    if n % self.config.record_interval == 0 or n == count or self._terminated:
                        stream.write(json.dumps(_observation_data(result.observation)) + "\n")
                    if self._terminated:
                        reason = "shutdown"
                        break
        except SimulationFailure:
            self._artifacts.append(self._artifact(path))
            self._persist("simulation_failure")
            raise
        artifact = self._artifact(path)
        self._artifacts.append(artifact)
        provenance = self._persist(reason)
        # A returned checksum must remain valid even when a later operation updates the run log.
        snapshot = self._directory / f"provenance-{len(self._artifacts)}.json"
        snapshot.write_bytes(Path(provenance.path).read_bytes())
        return RolloutResult(self.observe(), artifact, self._artifact(snapshot), reason)

    def close(self):
        if not self._closed and self._sim is not None:
            self._events.append(EnvironmentEvent("close", self._sim.time))
            self._persist("shutdown" if self._sim.is_shutdown() else
                          "simulation_failure" if self._terminated else "closed")
        self._closed = True

    @property
    def branch_metadata(self):
        """Return current immutable branch metadata, or ``None`` for a root run."""
        if self._parent_snapshot_id is None:
            return None
        return Branch(
            branch_id=self.branch_id,
            parent_snapshot_id=self._parent_snapshot_id,
            random_state_policy=self._branch_randomness_policy,
            created_at=self._branch_created_at,
            intervention_schedule=tuple(self._schedule),
        )

    def snapshot(self, snapshot_id=None):
        """Persist an exact, non-advancing snapshot of the pinned Python backend."""
        self._ready()
        if snapshot_id is None:
            snapshot_id = uuid4().hex
        if (type(snapshot_id) is not str or not snapshot_id
                or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
                       for char in snapshot_id)):
            raise SnapshotFailure("snapshot_id must contain only letters, digits, '-' or '_'")
        before_time = self._sim.time
        before_step = self._sim.step_count
        snapshot = create_snapshot_artifacts(self, snapshot_id)
        if self._sim.time != before_time or self._sim.step_count != before_step:
            raise SnapshotFailure("snapshot creation advanced the source simulator")
        return snapshot

    def fork(self, snapshot, branch_id=None):
        """Create an isolated branch from a snapshot owned by this environment."""
        self._ready()
        if isinstance(snapshot, (str, Path, ArtifactRef)):
            snapshot = load_snapshot(snapshot)
        if not isinstance(snapshot, Snapshot):
            raise SnapshotFailure("Snapshot or snapshot metadata artifact required")
        if (snapshot.parent_run_id != self.run_id
                or snapshot.source_branch_id != self.branch_id):
            raise SnapshotFailure("snapshot does not belong to this source environment")
        expected_config = replace(
            self.config,
            artifact_directory=Path(self.config.artifact_directory).resolve(),
        )
        if snapshot.config != expected_config:
            raise SnapshotFailure("snapshot config does not match its source environment")
        return self._fork_from_snapshot(
            snapshot,
            trusted_artifact_root=Path(self.config.artifact_directory),
            branch_id=branch_id,
        )

    @classmethod
    def _fork_from_snapshot(cls, snapshot, trusted_artifact_root,
                            branch_id=None, replay_of=None):
        trusted_artifact_root = Path(trusted_artifact_root).resolve()
        if Path(snapshot.config.artifact_directory).resolve() != trusted_artifact_root:
            raise SnapshotFailure("snapshot config is outside the trusted artifact root")
        if branch_id is None:
            branch_id = uuid4().hex
        if (type(branch_id) is not str or not branch_id
                or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
                       for char in branch_id)):
            raise SnapshotFailure("branch_id must contain only letters, digits, '-' or '_'")
        directory = (trusted_artifact_root / snapshot.parent_run_id
                     / "branches" / branch_id)
        if directory.exists():
            raise SnapshotFailure(f"branch already exists: {branch_id}")
        payload = load_snapshot_payload(snapshot, trusted_artifact_root)
        environment = cls(replace(snapshot.config,
                                  artifact_directory=trusted_artifact_root))
        environment.run_id = snapshot.parent_run_id
        environment.branch_id = branch_id
        environment._directory = directory
        try:
            environment._directory.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise SnapshotFailure(f"branch already exists: {branch_id}") from exc
        environment._sim = payload["simulator"]
        environment._terminated = payload["terminated"]
        environment._constraints = dict(payload["constraints"])
        environment._schedule = []
        environment._scenarios = []
        environment._artifacts = []
        environment._snapshots = []
        environment._parent_snapshot_id = snapshot.snapshot_id
        environment._branch_created_at = datetime.now(timezone.utc).isoformat()
        environment._branch_randomness_policy = RANDOMNESS_POLICY
        environment._origin_snapshot = snapshot
        environment._replay_of_branch_id = replay_of
        environment._events = [EnvironmentEvent("fork", environment._sim.time,
                                                snapshot.snapshot_id)]
        environment._persist("shutdown" if environment._terminated else None)
        return environment

    def replay_spec(self):
        """Capture all post-fork inputs needed to replay this branch exactly."""
        self._ready()
        if self._origin_snapshot is None:
            raise SnapshotFailure("replay specifications are available for forked branches")
        return ReplaySpec(
            source_run_id=self.run_id,
            source_branch_id=self.branch_id,
            snapshot=self._origin_snapshot,
            config=self.config,
            intervention_schedule=tuple(self._schedule),
            target_simulation_time=self._sim.time,
            target_step_count=self._sim.step_count,
            random_state_policy=self._branch_randomness_policy,
            expected_observation_sha256=observation_sha256(self.observe()),
        )

    def persist_replay_spec(self, filename="replay-spec.json"):
        if (type(filename) is not str or Path(filename).name != filename
                or not filename.endswith(".json")):
            raise SnapshotFailure("replay filename must be a local .json filename")
        return persist_replay_spec(self.replay_spec(), self._directory / filename)

    @classmethod
    def replay(cls, replay_spec, trusted_artifact_root=None, branch_id=None):
        """Replay a persisted branch schedule from its exact parent snapshot."""
        if trusted_artifact_root is None:
            raise SnapshotFailure("replay requires an explicit trusted_artifact_root")
        if isinstance(replay_spec, (str, Path, ArtifactRef)):
            replay_spec = load_replay_spec(replay_spec)
        if not isinstance(replay_spec, ReplaySpec):
            raise SnapshotFailure("ReplaySpec or replay specification artifact required")
        _validate_replay_contract(replay_spec)
        environment = cls._fork_from_snapshot(
            replay_spec.snapshot,
            trusted_artifact_root=trusted_artifact_root,
            branch_id=branch_id,
            replay_of=replay_spec.source_branch_id,
        )
        try:
            environment._execute_replay(replay_spec)
        except Exception:
            environment._terminated = True
            environment._events.append(EnvironmentEvent(
                "replay_failure", environment._sim.time,
                replay_spec.source_branch_id,
            ))
            environment._persist("replay_failure")
            raise
        return environment

    def _execute_replay(self, replay_spec):
        schedule = [dict(item) for item in replay_spec.intervention_schedule]
        current = self._sim.step_count
        target = replay_spec.target_step_count
        if type(target) is not int or target < current:
            raise SnapshotFailure("invalid replay target step")
        index = 0
        while current <= target:
            while index < len(schedule) and schedule[index].get("step_count") == current:
                self.apply(_intervention_from_record(schedule[index]))
                index += 1
            if current == target:
                break
            if index < len(schedule):
                next_step = schedule[index].get("step_count")
                if type(next_step) is not int or next_step < current or next_step > target:
                    raise SnapshotFailure("invalid replay intervention schedule")
            self.step()
            current = self._sim.step_count
        if index != len(schedule):
            raise SnapshotFailure("replay schedule extends beyond its target")
        if not math.isclose(self._sim.time, replay_spec.target_simulation_time,
                            rel_tol=0, abs_tol=1e-15):
            raise SnapshotFailure("replay target time does not match target step")
        if observation_sha256(self.observe()) != replay_spec.expected_observation_sha256:
            raise SnapshotFailure("replay observation does not match recorded branch")
        self._events.append(EnvironmentEvent("replay_complete", self._sim.time,
                                             replay_spec.source_branch_id))
        self._persist(None)


def _intervention_from_record(record):
    try:
        kind = record["type"]
        target = record["target"]
        if kind == "DisturbanceIntervention":
            if set(record) != {"time", "step_count", "type", "target", "value"}:
                raise SnapshotFailure("invalid disturbance replay record fields")
            return DisturbanceIntervention(target, record["value"])
        if kind == "MVIntervention":
            if set(record) != {"time", "step_count", "type", "target", "value"}:
                raise SnapshotFailure("invalid MV replay record fields")
            return MVIntervention(target, record["value"])
        if kind == "MVConstraint":
            if set(record) != {"time", "step_count", "type", "target",
                               "min_value", "max_value"}:
                raise SnapshotFailure("invalid constraint replay record fields")
            return MVConstraint(target, record.get("min_value"), record.get("max_value"))
    except (KeyError, TypeError) as exc:
        raise SnapshotFailure("invalid replay intervention record") from exc
    raise SnapshotFailure(f"unsupported replay intervention type: {kind!r}")


def _validate_replay_contract(replay_spec):
    snapshot = replay_spec.snapshot
    if replay_spec.random_state_policy is not BranchRandomnessPolicy.CLONED_STATE:
        raise SnapshotFailure("unsupported replay randomness policy")
    if replay_spec.config != snapshot.config:
        raise SnapshotFailure("replay config differs from the parent snapshot")
    if replay_spec.source_run_id != snapshot.parent_run_id:
        raise SnapshotFailure("replay run differs from the parent snapshot")
    target = replay_spec.target_step_count
    target_time = replay_spec.target_simulation_time
    if (type(target) is not int or target < snapshot.source_step_count
            or not _finite(target_time)):
        raise SnapshotFailure("invalid replay target")
    expected_target_time = (snapshot.simulation_time
                            + (target - snapshot.source_step_count) / 3600.0)
    if not math.isclose(target_time, expected_target_time,
                        rel_tol=0, abs_tol=1e-12):
        raise SnapshotFailure("replay target time and step disagree")
    digest = replay_spec.expected_observation_sha256
    if (type(digest) is not str or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)):
        raise SnapshotFailure("invalid replay observation checksum")
    previous_step = snapshot.source_step_count
    for record in replay_spec.intervention_schedule:
        intervention = _intervention_from_record(record)
        del intervention  # Construction proves the type is allowlisted.
        step = record.get("step_count")
        time = record.get("time")
        if (type(step) is not int or step < previous_step or step > target
                or not _finite(time)):
            raise SnapshotFailure("invalid replay intervention position")
        expected_time = (snapshot.simulation_time
                         + (step - snapshot.source_step_count) / 3600.0)
        if not math.isclose(time, expected_time, rel_tol=0, abs_tol=1e-12):
            raise SnapshotFailure("replay intervention time and step disagree")
        previous_step = step
