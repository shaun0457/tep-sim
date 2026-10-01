import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from tep_sim import (BranchRandomnessPolicy, ControlMode,
                     DisturbanceIntervention, EnvironmentConfig,
                     SimulationFailure, SnapshotFailure, SnapshotFidelity,
                     TEPEnvironment, UPSTREAM_REVISION, load_replay_spec,
                     load_snapshot)
from tep_sim.contracts import ArtifactRef
import tep_sim.snapshot as snapshot_module


@pytest.fixture
def config(tmp_path):
    return EnvironmentConfig(24681357, "python", ControlMode.CLOSED_LOOP, 5,
                             UPSTREAM_REVISION, tmp_path)


def _step_observations(environment, count):
    return [environment.step().observation for _ in range(count)]


def _max_observation_error(left, right):
    values = []
    for first, second in zip(left, right, strict=True):
        values.extend(abs(first.measurements[key] - second.measurements[key])
                      for key in first.measurements)
        values.extend(abs(first.manipulated_variables[key]
                          - second.manipulated_variables[key])
                      for key in first.manipulated_variables)
    return max(values, default=0.0)


def test_snapshot_does_not_change_source_state_events_or_provenance(config):
    source = TEPEnvironment(config)
    control = TEPEnvironment(config)
    assert source.reset() == control.reset()
    assert _step_observations(source, 17) == _step_observations(control, 17)

    provenance_path = Path(config.artifact_directory) / source.run_id / "provenance.json"
    provenance_before = provenance_path.read_bytes()
    events_before = tuple(source._events)
    schedule_before = tuple(source._schedule)
    observation_before = source.observe()

    snapshot = source.snapshot("healthy-17")

    assert source.observe() == observation_before
    assert tuple(source._events) == events_before
    assert tuple(source._schedule) == schedule_before
    assert provenance_path.read_bytes() == provenance_before
    assert snapshot.fidelity is SnapshotFidelity.EXACT
    assert snapshot.simulation_time == observation_before.simulation_time
    assert snapshot.source_step_count == 17
    assert snapshot.random_state_metadata["fork_policy"] == "cloned_state"
    assert snapshot.checksum == snapshot.state.sha256
    assert load_snapshot(snapshot.metadata) == snapshot
    assert _step_observations(source, 60) == _step_observations(control, 60)


def test_forks_are_isolated_and_cloned_randomness_has_zero_error(config):
    parent = TEPEnvironment(config)
    parent.reset()
    parent.apply(DisturbanceIntervention("IDV(1)", 1))
    _step_observations(parent, 25)
    snapshot = parent.snapshot("random-walk")
    parent_before = parent.observe()

    first = parent.fork(snapshot, "same-a")
    second = parent.fork(snapshot, "same-b")
    first_trace = _step_observations(first, 300)
    second_trace = _step_observations(second, 300)

    assert first_trace == second_trace
    assert _max_observation_error(first_trace, second_trace) == 0.0
    assert first.branch_metadata.random_state_policy is BranchRandomnessPolicy.CLONED_STATE
    assert second.branch_metadata.random_state_policy is BranchRandomnessPolicy.CLONED_STATE
    assert parent.observe() == parent_before

    branch_a = parent.fork(snapshot, "intervention-a")
    branch_b = parent.fork(snapshot, "intervention-b")
    branch_b_before = branch_b.observe()
    branch_a.apply(DisturbanceIntervention("IDV(4)", 1))
    _step_observations(branch_a, 30)

    assert branch_b.observe() == branch_b_before
    assert parent.observe() == parent_before
    assert branch_a.observe() != branch_b.observe()
    assert branch_a._sim is not branch_b._sim
    assert branch_a._sim.process is not branch_b._sim.process


def test_persisted_branch_replays_with_exact_provenance(config):
    parent = TEPEnvironment(config)
    parent.reset()
    _step_observations(parent, 11)
    snapshot = parent.snapshot("replay-origin")
    branch = parent.fork(snapshot, "observed")

    branch.apply(DisturbanceIntervention("IDV(1)", 1))
    _step_observations(branch, 23)
    branch.apply(DisturbanceIntervention("IDV(1)", 0))
    branch.apply(DisturbanceIntervention("IDV(4)", 1))
    _step_observations(branch, 37)
    expected = branch.observe()
    spec_artifact = branch.persist_replay_spec()

    assert hashlib.sha256(Path(spec_artifact.path).read_bytes()).hexdigest() == \
        spec_artifact.sha256
    persisted_spec = load_replay_spec(spec_artifact)
    replayed = TEPEnvironment.replay(
        persisted_spec, config.artifact_directory, "replayed"
    )

    assert replayed.observe() == expected
    assert tuple(map(dict, replayed.branch_metadata.intervention_schedule)) == \
        tuple(map(dict, branch.branch_metadata.intervention_schedule))
    provenance = json.loads((Path(config.artifact_directory) / parent.run_id
                             / "branches" / "replayed" / "provenance.json").read_text())
    assert provenance["run_id"] == parent.run_id
    assert provenance["branch_id"] == "replayed"
    assert provenance["parent_snapshot_id"] == snapshot.snapshot_id
    assert provenance["branch_randomness_policy"] == "cloned_state"
    assert provenance["replay_of_branch_id"] == "observed"
    assert provenance["intervention_schedule"] == [
        dict(item) for item in persisted_spec.intervention_schedule
    ]

    Path(spec_artifact.path).write_bytes(Path(spec_artifact.path).read_bytes() + b" ")
    with pytest.raises(SnapshotFailure, match="replay specification checksum mismatch"):
        TEPEnvironment.replay(spec_artifact, config.artifact_directory, "tampered-spec")


def test_failure_and_tamper_do_not_corrupt_parent_or_siblings(config, monkeypatch):
    parent = TEPEnvironment(config)
    parent.reset()
    _step_observations(parent, 9)
    snapshot = parent.snapshot("failure-origin")
    parent_before = parent.observe()
    failed = parent.fork(snapshot, "failed")
    sibling = parent.fork(snapshot, "sibling")
    sibling_control = parent.fork(snapshot, "sibling-control")

    monkeypatch.setattr(failed._sim, "step", lambda: False)
    with pytest.raises(SimulationFailure, match="upstream step failed"):
        failed.step()
    assert parent.observe() == parent_before
    assert sibling.step() == sibling_control.step()

    sibling_before = sibling.observe()
    state_path = Path(snapshot.state.path)
    state_path.write_bytes(state_path.read_bytes() + b"tampered")
    with pytest.raises(SnapshotFailure, match="checksum mismatch"):
        parent.fork(snapshot, "must-not-exist")
    assert parent.observe() == parent_before
    assert sibling.observe() == sibling_before
    assert not (Path(config.artifact_directory) / parent.run_id / "branches"
                / "must-not-exist").exists()


def test_forged_path_and_metadata_tamper_are_rejected_before_unpickle(
        config, monkeypatch):
    parent = TEPEnvironment(config)
    parent.reset()
    snapshot = parent.snapshot("trusted")
    external = Path(config.artifact_directory) / "external.pickle"
    external.write_bytes(b"not a trusted snapshot")
    digest = hashlib.sha256(external.read_bytes()).hexdigest()
    forged = replace(
        snapshot,
        state=ArtifactRef(str(external.resolve()), digest),
        checksum=digest,
    )

    def must_not_unpickle(_payload):
        raise AssertionError("unpickle was reached for an untrusted path")

    monkeypatch.setattr(snapshot_module.pickle, "loads", must_not_unpickle)
    with pytest.raises(SnapshotFailure, match="trusted source location"):
        parent.fork(forged, "forged")

    metadata_path = Path(snapshot.metadata.path)
    metadata_path.write_bytes(metadata_path.read_bytes() + b" ")
    with pytest.raises(SnapshotFailure, match="metadata checksum mismatch"):
        parent.fork(snapshot, "metadata-tampered")


def test_replay_rejects_untrusted_root_schedule_and_target_before_loading(config,
                                                                          monkeypatch):
    parent = TEPEnvironment(config)
    parent.reset()
    snapshot = parent.snapshot("replay-validation")
    branch = parent.fork(snapshot, "source")
    branch.apply(DisturbanceIntervention("IDV(4)", 1))
    branch.step()
    spec = branch.replay_spec()

    with pytest.raises(SnapshotFailure, match="trusted_artifact_root"):
        TEPEnvironment.replay(spec, branch_id="missing-root")
    with pytest.raises(SnapshotFailure, match="target time and step disagree"):
        TEPEnvironment.replay(
            replace(spec, target_simulation_time=spec.target_simulation_time + 1.0),
            config.artifact_directory,
            "bad-target",
        )
    invalid_record = dict(spec.intervention_schedule[0])
    invalid_record["type"] = "ArbitraryPython"
    with pytest.raises(SnapshotFailure, match="unsupported replay intervention"):
        TEPEnvironment.replay(
            replace(spec, intervention_schedule=(invalid_record,)),
            config.artifact_directory,
            "bad-schedule",
        )

    untrusted_root = Path(config.artifact_directory) / "elsewhere"
    with pytest.raises(SnapshotFailure, match="outside the trusted artifact root"):
        TEPEnvironment.replay(spec, untrusted_root, "untrusted")


def test_unsupported_fidelity_format_and_duplicate_ids_fail_explicitly(config):
    parent = TEPEnvironment(config)
    parent.reset()
    capabilities = parent.capabilities()
    fidelity = capabilities.entry("snapshot:python")
    assert fidelity.supported is True
    assert fidelity.details["fidelity"] == "exact"
    assert fidelity.details["fork_randomness_policy"] == "cloned_state"
    snapshot = parent.snapshot("one")
    provenance = (Path(config.artifact_directory) / parent.run_id
                  / "provenance.json").read_bytes()

    with pytest.raises(SnapshotFailure, match="already exists"):
        parent.snapshot("one")
    with pytest.raises(SnapshotFailure, match="unsupported snapshot fidelity"):
        parent.fork(replace(snapshot, fidelity=SnapshotFidelity.RECONSTRUCTED),
                    "unsupported-fidelity")
    with pytest.raises(SnapshotFailure, match="state format is unsupported"):
        parent.fork(replace(snapshot, state_format_version="future-v99"),
                    "unsupported-format")

    assert (Path(config.artifact_directory) / parent.run_id
            / "provenance.json").read_bytes() == provenance
    assert parent.observe().simulation_time == 0.0
