"""Deterministic adapter over the pinned Python TEPSimulator."""
import hashlib
import json
import math
from dataclasses import asdict
from pathlib import Path
from types import MappingProxyType
from uuid import uuid4

from tep.simulator import TEPSimulator, ControlMode as UpstreamControlMode
from .contracts import (EnvironmentConfig, ControlMode, Observation,
                        DisturbanceIntervention, MVIntervention, MVConstraint,
                        EnvironmentEvent, StepResult, ArtifactRef, RolloutResult)
from .errors import (InvalidIntervention, UnknownVariable, UnsupportedCapability,
                     IncompatibleControlMode, InvalidEnvironmentState, SimulationFailure)
from .registry import REGISTRY, UPSTREAM_REVISION


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
        self._artifacts = []

    def capabilities(self):
        return MappingProxyType({"disturbance": True, "manual_mv": True,
                                 "manual_mv_constraint": True, "snapshot": False,
                                 "safety_margins": False, "backend": "python"})

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
        self._constraints, self._schedule, self._artifacts = {}, [], []
        self._events = [EnvironmentEvent("reset", 0.0)]
        self._persist(None)
        return self.observe()

    def observe(self):
        self._ready()
        return Observation(self._sim.time,
            {f"XMEAS({i})": float(v) for i, v in enumerate(self._sim.get_measurements(), 1)},
            {f"XMV({i})": float(v) for i, v in enumerate(self._sim.get_manipulated_vars(), 1)},
            tuple(f"IDV({i})" for i in self._sim.get_active_disturbances()),
            bool(self._sim.is_shutdown()))

    def apply(self, intervention):
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
            current = self.observe().manipulated_variables[intervention.target]
            if not lo <= current <= hi:
                raise InvalidIntervention("current setpoint violates proposed constraint")
        elif not disturbance:
            low, high = self._constraints.get(intervention.target, (0, 100))
            if not low <= intervention.value <= high:
                raise InvalidIntervention("setpoint violates active constraint")
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
        self._schedule.append({"time": self._sim.time, "type": type(intervention).__name__,
                               **asdict(intervention)})
        self._events.append(EnvironmentEvent("intervention", self._sim.time, repr(intervention)))
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
        data = {"environment_version": "0.1.0", "upstream_revision": UPSTREAM_REVISION,
                "seed": self.config.seed, "config": config, "run_id": self.run_id,
                "branch_id": self.branch_id, "intervention_schedule": self._schedule,
                "termination_reason": reason, "events": [asdict(e) for e in self._events],
                "artifacts": [asdict(a) for a in self._artifacts]}
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
