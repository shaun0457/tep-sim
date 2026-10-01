import hashlib
import json
import sys
from dataclasses import replace, FrozenInstanceError
from pathlib import Path

import pytest
from tep_sim import (EnvironmentConfig, ControlMode, TEPEnvironment, UPSTREAM_REVISION,
                     REGISTRY, DisturbanceIntervention, MVIntervention, MVConstraint,
                     UnknownVariable, InvalidIntervention, IncompatibleControlMode,
                     InvalidEnvironmentState, UnsupportedCapability, SimulationFailure)


@pytest.fixture
def config(tmp_path):
    return EnvironmentConfig(12345, "python", ControlMode.CLOSED_LOOP, 3,
                             UPSTREAM_REVISION, tmp_path)


def trajectory(env, intervention=None):
    result = [env.reset()]
    if intervention:
        env.apply(intervention)
    result.extend(env.step().observation for _ in range(30))
    return result


def test_same_seed_reset_and_disturbance_reproduce(config):
    env = TEPEnvironment(config)
    assert trajectory(env) == trajectory(env)
    disturbance = DisturbanceIntervention("IDV(4)", 1)
    first = trajectory(env, disturbance)
    assert first == trajectory(env, disturbance)
    assert first[-1].active_disturbances == ("IDV(4)",)
    assert first[-1].measurements != trajectory(env)[-1].measurements
    env.close()


@pytest.mark.parametrize("intervention,error", [
    (MVIntervention("XMV(99)", 5), UnknownVariable),
    (MVIntervention("XMV(1)", 5), IncompatibleControlMode),
    (MVIntervention("XMV(1)", 101), InvalidIntervention),
    (MVIntervention("XMV(1)", float("nan")), InvalidIntervention),
    (DisturbanceIntervention("IDV(1)", 0.5), InvalidIntervention),
    (DisturbanceIntervention("IDV(1)", True), InvalidIntervention),
    ({"target": "XMV(1)", "value": 3}, InvalidIntervention),
])
def test_validation_failure_has_no_state_or_provenance_mutation(config, intervention, error):
    env, control = TEPEnvironment(config), TEPEnvironment(config)
    before = env.reset()
    control.reset()
    path = Path(config.artifact_directory) / env.run_id / "provenance.json"
    persisted = path.read_bytes()
    with pytest.raises(error):
        env.apply(intervention)
    assert env.observe() == before
    assert path.read_bytes() == persisted
    assert env.step() == control.step()


def test_immutable_observations_and_manual_constraints(config):
    env = TEPEnvironment(replace(config, control_mode=ControlMode.MANUAL))
    obs = env.reset()
    with pytest.raises(TypeError):
        obs.measurements["XMEAS(1)"] = 0
    with pytest.raises(FrozenInstanceError):
        obs.simulation_time = 100
    env.apply(MVConstraint("XMV(1)", 0, 80))
    env.apply(MVIntervention("XMV(1)", 50))
    assert env.step().observation.manipulated_variables["XMV(1)"] == 50
    before = env.observe()
    with pytest.raises(InvalidIntervention):
        env.apply(MVIntervention("XMV(1)", 90))
    with pytest.raises(InvalidIntervention):
        env.apply(MVConstraint("XMV(1)", 60, 80))
    assert before == env.observe()


def test_rollout_provenance_artifacts_and_no_agent_dependencies(config):
    env = TEPEnvironment(config)
    env.reset()
    env.apply(DisturbanceIntervention("IDV(4)", 1))
    result = env.rollout(10 / 3600)
    data = json.loads(Path(result.provenance.path).read_text())
    assert data["upstream_revision"] == UPSTREAM_REVISION
    assert data["seed"] == config.seed
    assert data["environment_version"] and data["run_id"] == env.run_id
    assert data["branch_id"] == "root"
    assert data["config"]["control_mode"] == "closed_loop"
    assert data["termination_reason"] == "horizon_reached"
    assert data["intervention_schedule"][0]["target"] == "IDV(4)"
    rows = [json.loads(row) for row in Path(result.telemetry.path).read_text().splitlines()]
    assert len(rows) == 5  # initial, 3, 6, 9, final 10
    assert rows[-1]["simulation_time"] == pytest.approx(10 / 3600)
    assert data["artifacts"][0]["sha256"] == result.telemetry.sha256
    env.rollout(1 / 3600)
    env.close()
    for artifact in (result.telemetry, result.provenance):
        assert hashlib.sha256(Path(artifact.path).read_bytes()).hexdigest() == artifact.sha256
    assert not any(name.startswith(("industrial_agent_runtime", "tep_agent_lab", "langgraph"))
                   for name in sys.modules)


def test_registry_matches_upstream(config):
    from tep import constants
    assert len(REGISTRY) == 41 + 12 + 20
    for i, name in enumerate(constants.MEASUREMENT_NAMES, 1):
        assert REGISTRY[f"XMEAS({i})"].name == name
        assert REGISTRY[f"XMEAS({i})"].unit == constants.MEASUREMENT_UNITS[i - 1]
    for i, name in enumerate(constants.DISTURBANCE_NAMES, 1):
        assert REGISTRY[f"IDV({i})"].name == name


def test_lifecycle_capabilities_and_numerical_failure(config, monkeypatch):
    env = TEPEnvironment(config)
    with pytest.raises(InvalidEnvironmentState):
        env.step()
    env.reset()
    assert env.capabilities().supports("consequence:process_limit_margin")
    with pytest.raises(InvalidEnvironmentState):
        env.rollout(0.5 / 3600)
    monkeypatch.setattr(env._sim, "step", lambda: False)
    with pytest.raises(SimulationFailure):
        env.step()
    with pytest.raises(InvalidEnvironmentState):
        env.step()
    env.close()
    with pytest.raises(InvalidEnvironmentState):
        env.reset()
    for field, value in [("backend", "fortran"), ("upstream_revision", "other")]:
        with pytest.raises(UnsupportedCapability):
            TEPEnvironment(replace(config, **{field: value}))


def test_failed_rollout_retains_partial_telemetry(config, monkeypatch):
    env = TEPEnvironment(config)
    env.reset()
    monkeypatch.setattr(env._sim, "step", lambda: False)
    with pytest.raises(SimulationFailure):
        env.rollout(5 / 3600)
    data = json.loads((Path(config.artifact_directory) / env.run_id / "provenance.json").read_text())
    assert data["termination_reason"] == "simulation_failure"
    artifact = data["artifacts"][0]
    assert hashlib.sha256(Path(artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
    assert len(Path(artifact["path"]).read_text().splitlines()) == 1
