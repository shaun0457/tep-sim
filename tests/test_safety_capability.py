"""A4 capability registry, semantic scenario compilation, and safety evaluation."""
import ast
import json
import math
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

import tep_sim
from tep_sim import (REGISTRY, SAFETY_LIMITS, UPSTREAM_REVISION, AmbiguousScenario,
                     AmbiguousScenarioError, ArtifactRef, ControlMode, DisturbanceIntervention,
                     EnvironmentConfig, InvalidEnvironmentState, InvalidScenario,
                     InvalidScenarioError, MVIntervention, ScenarioRequest, SupportedScenario,
                     TEPEnvironment, UnsupportedCapability, UnsupportedScenario,
                     UnsupportedScenarioError, build_capability_registry, compile_scenario,
                     evaluate_safety)
from tep_sim import scenario as scenario_module

UNSUPPORTED = ("pipe_rupture", "fire", "toxic_dispersion", "blast_overpressure",
               "personnel_casualty")
COOLING_LOSS = ScenarioRequest("reactor_cooling_water_flow_reduction",
                               {"valve_position_percent": 0.0})


def make_config(tmp_path, mode=ControlMode.CLOSED_LOOP, interval=10):
    return EnvironmentConfig(13579, "python", mode, interval, UPSTREAM_REVISION, tmp_path)


def state(env):
    provenance = json.loads((Path(env.config.artifact_directory) / env.run_id
                             / "provenance.json").read_text())
    return (env.observe(), env._sim.step_count, env._sim.get_disturbances().tolist(),
            dict(env._constraints), provenance["intervention_schedule"],
            provenance["scenarios"])


# -- acceptance 1: capability registry against vendored runtime metadata ------------
def test_capabilities_match_vendored_runtime_metadata(tmp_path):
    env = TEPEnvironment(make_config(tmp_path))
    registry = env.capabilities()
    from tep import constants
    disturbances = [e.capability_id for e in registry.domain("supported_disturbances")]
    assert disturbances == [f"disturbance:IDV({i})"
                            for i in range(1, constants.NUM_DISTURBANCES + 1)]
    for entry in registry.domain("supported_disturbances"):
        variable = REGISTRY[entry.capability_id.split(":")[1]]
        assert entry.description == variable.name
        assert entry.details["semantics_documented"] == (variable.name != "Unknown")
    mvs = registry.domain("supported_mv_interventions")
    assert [e.description for e in mvs] == list(constants.MANIPULATED_VAR_NAMES)
    assert all(e.preconditions["control_mode"] == ("manual",) for e in mvs)
    assert len(registry.domain("runtime_variables")) == len(REGISTRY)
    assert {e.capability_id.split(":")[1] for e in registry.domain("runtime_variables")} \
        == set(REGISTRY)


def test_registry_exposes_every_spec_domain_and_honest_unsupported_domains():
    registry = build_capability_registry()
    data = registry.to_json()
    for domain in ("runtime_variables", "supported_disturbances",
                   "supported_mv_interventions", "supported_constraints",
                   "supported_semantic_scenarios", "snapshot_fidelity",
                   "consequence_domains", "unsupported_domains"):
        assert data[domain], domain
    assert data["capability_version"] == tep_sim.CAPABILITY_VERSION
    assert data["upstream_revision"] == UPSTREAM_REVISION
    unsupported = registry.domain("unsupported_domains")
    assert sorted(e.capability_id for e in unsupported) == sorted(
        f"consequence:{name}" for name in UNSUPPORTED)
    assert not any(e.supported for e in unsupported)
    assert not registry.supports("consequence:fire")
    limits = [e for e in registry.domain("supported_constraints")
              if e.details.get("kind") == "shutdown_limit"]
    assert len(limits) == len(SAFETY_LIMITS)
    scenarios = {e.capability_id: e for e in registry.domain("supported_semantic_scenarios")}
    assert scenarios["scenario:reactor_cooling_water_flow_reduction"].preconditions == {
        "control_mode": ("manual",)}
    assert json.loads(json.dumps(data)) == build_capability_registry().to_json()
    assert not build_capability_registry("fortran").supports("snapshot:fortran")


def test_capability_entries_are_immutable():
    entry = build_capability_registry().entry("disturbance:IDV(4)")
    with pytest.raises(FrozenInstanceError):
        entry.supported = False
    with pytest.raises(TypeError):
        entry.details["values"] = (0,)


# -- acceptance 2: supported reactor-cooling scenario -------------------------------
def test_compile_supported_reactor_cooling_scenarios():
    result = compile_scenario(
        ScenarioRequest("reactor_cooling_water_inlet_temperature_step"),
        ControlMode.CLOSED_LOOP)
    assert isinstance(result, SupportedScenario)
    assert result.interventions == (DisturbanceIntervention("IDV(4)", 1),)
    assert result.provenance["mapping_version"] == tep_sim.SCENARIO_MAPPING_VERSION
    assert result.provenance["capability_version"] == tep_sim.CAPABILITY_VERSION
    assert result.provenance["upstream_revision"] == UPSTREAM_REVISION
    manual = compile_scenario(ScenarioRequest("reactor_cooling_water_flow_reduction",
                                              {"valve_position_percent": 12}),
                              ControlMode.MANUAL)
    assert manual.interventions == (MVIntervention("XMV(10)", 12.0),)
    assert manual.provenance["parameters"] == {"valve_position_percent": 12}


def test_every_catalog_mapping_targets_registry_variables():
    for mapping in scenario_module.scenario_catalog():
        for mode in mapping.control_modes:
            params = {name: low for name, (low, _, _) in mapping.parameters.items()}
            result = compile_scenario(ScenarioRequest(mapping.scenario_id, params), mode)
            assert isinstance(result, SupportedScenario)
            assert all(i.target in REGISTRY for i in result.interventions)


def test_apply_supported_scenario_records_provenance(tmp_path):
    env = TEPEnvironment(make_config(tmp_path))
    env.reset()
    env.apply_scenario(ScenarioRequest("reactor_cooling_water_inlet_temperature_step"))
    assert env.observe().active_disturbances == ("IDV(4)",)
    _, _, _, _, schedule, scenarios = state(env)
    assert [item["target"] for item in schedule] == ["IDV(4)"]
    assert scenarios[0]["scenario_id"] == "reactor_cooling_water_inlet_temperature_step"
    provenance = json.loads((tmp_path / env.run_id / "provenance.json").read_text())
    assert provenance["capability_version"] == tep_sim.CAPABILITY_VERSION
    assert provenance["safety_limits_version"] == tep_sim.SAFETY_LIMITS_VERSION
    assert provenance["scenario_mapping_version"] == tep_sim.SCENARIO_MAPPING_VERSION


# -- acceptance 3: unsupported consequence physics ---------------------------------
@pytest.mark.parametrize("name", UNSUPPORTED)
def test_consequence_physics_requests_are_unsupported(name):
    result = compile_scenario(ScenarioRequest(name, {"anything": 1}), ControlMode.MANUAL)
    assert isinstance(result, UnsupportedScenario)
    assert result.missing_capability == f"consequence:{name}"


def test_unknown_and_mode_incompatible_scenarios_are_unsupported():
    unknown = compile_scenario(ScenarioRequest("reactor_runaway"), ControlMode.MANUAL)
    assert isinstance(unknown, UnsupportedScenario)
    assert unknown.missing_capability == "scenario:reactor_runaway"
    closed = compile_scenario(COOLING_LOSS, ControlMode.CLOSED_LOOP)
    assert isinstance(closed, UnsupportedScenario)
    assert closed.missing_capability == "control_mode:manual"


def test_ambiguous_terms_are_returned_not_resolved():
    result = compile_scenario(ScenarioRequest("loss_of_cooling"), ControlMode.MANUAL)
    assert isinstance(result, AmbiguousScenario)
    assert len(result.candidates) > 1
    catalog = {m.scenario_id for m in scenario_module.scenario_catalog()}
    for term, candidates in scenario_module.ambiguous_terms().items():
        assert set(candidates) <= catalog, term


@pytest.mark.parametrize("request_", [
    "reactor_cooling_water_inlet_temperature_step",
    ScenarioRequest(""),
    ScenarioRequest(None),
    ScenarioRequest("reactor_cooling_water_flow_reduction", []),
    ScenarioRequest("reactor_cooling_water_flow_reduction", {}),
    ScenarioRequest("reactor_cooling_water_flow_reduction", {"valve_position_percent": True}),
    ScenarioRequest("reactor_cooling_water_flow_reduction",
                    {"valve_position_percent": math.nan}),
    ScenarioRequest("reactor_cooling_water_flow_reduction", {"valve_position_percent": 101}),
    ScenarioRequest("reactor_cooling_water_flow_reduction", {"valve_position_percent": "0"}),
    ScenarioRequest("reactor_cooling_water_flow_reduction",
                    {"valve_position_percent": 5, "extra": 1}),
    ScenarioRequest("reactor_cooling_water_inlet_temperature_step", {"magnitude": 2}),
])
def test_malformed_scenarios_are_invalid(request_):
    assert isinstance(compile_scenario(request_, ControlMode.MANUAL), InvalidScenario)


# -- acceptance 6: capability rejection before state mutation -----------------------
@pytest.mark.parametrize("request_,error", [
    (ScenarioRequest("pipe_rupture"), UnsupportedScenarioError),
    (ScenarioRequest("fire"), UnsupportedScenarioError),
    (ScenarioRequest("loss_of_cooling"), AmbiguousScenarioError),
    (ScenarioRequest("reactor_cooling_water_flow_reduction",
                     {"valve_position_percent": 200}), InvalidScenarioError),
    (COOLING_LOSS, UnsupportedScenarioError),  # CLOSED_LOOP config
])
def test_rejected_scenarios_never_mutate_state(tmp_path, request_, error):
    env = TEPEnvironment(make_config(tmp_path))
    env.reset()
    env.step()
    before = state(env)
    with pytest.raises(error) as raised:
        env.apply_scenario(request_)
    assert raised.value.result == env.compile_scenario(request_)
    assert state(env) == before


def test_rejection_error_classes_keep_environment_taxonomy():
    assert issubclass(UnsupportedScenarioError, UnsupportedCapability)
    assert issubclass(AmbiguousScenarioError, tep_sim.InvalidIntervention)
    assert issubclass(InvalidScenarioError, tep_sim.InvalidIntervention)


def test_multi_intervention_scenario_validates_all_before_mutating(tmp_path, monkeypatch):
    bad = scenario_module.ScenarioMapping(
        "fixture_two_step", "fixture", "test", frozenset(ControlMode), {},
        lambda _: (DisturbanceIntervention("IDV(4)", 1), MVIntervention("XMV(10)", 5.0)))
    monkeypatch.setattr(scenario_module, "_BY_ID", {"fixture_two_step": bad})
    env = TEPEnvironment(make_config(tmp_path))  # CLOSED_LOOP: the MV step is illegal
    env.reset()
    before = state(env)
    with pytest.raises(tep_sim.IncompatibleControlMode):
        env.apply_scenario(ScenarioRequest("fixture_two_step"))
    assert state(env) == before


def test_terminated_environment_rejects_scenario_before_mutation(tmp_path):
    env = TEPEnvironment(make_config(tmp_path, ControlMode.MANUAL))
    env.reset()
    env.apply_scenario(COOLING_LOSS)
    env.rollout(0.25)
    before = state(env)
    with pytest.raises(InvalidEnvironmentState):
        env.apply_scenario(ScenarioRequest("reactor_cooling_water_inlet_temperature_step"))
    assert state(env) == before


# -- acceptance 4: deterministic safety events on a threshold crossing --------------
def cooling_loss_rollout(tmp_path):
    env = TEPEnvironment(make_config(tmp_path, ControlMode.MANUAL))
    env.reset()
    env.apply_scenario(COOLING_LOSS)
    return env, env.rollout(0.25)


def test_cooling_loss_crosses_shutdown_limit_and_records_events(tmp_path):
    env, rollout = cooling_loss_rollout(tmp_path)
    assert rollout.termination_reason == "shutdown"
    evaluation = env.evaluate_safety(rollout)
    assert evaluation.shutdown_occurred
    assert evaluation.shutdown_time == pytest.approx(rollout.observation.simulation_time)
    assert evaluation.termination_reason == "shutdown"
    assert "reactor_pressure_high" in evaluation.shutdown_limit_ids
    crossing = next(c for c in evaluation.limit_crossings
                    if c.limit_id == "reactor_pressure_high")
    assert crossing.value > crossing.threshold == 3000.0
    assert evaluation.minimum_safety_margins["reactor_pressure_high"].margin < 0
    interval = next(i for i in evaluation.unsafe_intervals
                    if i.limit_id == "reactor_pressure_high")
    assert interval.open_at_end and interval.extreme_value >= crossing.value
    kinds = [e.kind for e in evaluation.relevant_process_events]
    assert "limit_crossed" in kinds and kinds[-1] == "shutdown"
    assert set(evaluation.unsupported_consequence_domains) == set(UNSUPPORTED)
    assert evaluation.limits_version == tep_sim.SAFETY_LIMITS_VERSION
    assert evaluation.telemetry_sha256 == rollout.telemetry.sha256


def test_normal_operation_has_no_crossings_and_positive_margins(tmp_path):
    env = TEPEnvironment(make_config(tmp_path))
    env.reset()
    env.apply(DisturbanceIntervention("IDV(4)", 1))
    evaluation = env.evaluate_safety(env.rollout(0.05))
    assert not evaluation.shutdown_occurred and evaluation.shutdown_time is None
    assert evaluation.limit_crossings == () and evaluation.unsafe_intervals == ()
    assert all(m.margin > 0 for m in evaluation.minimum_safety_margins.values())
    assert set(evaluation.minimum_safety_margins) == {l.limit_id for l in SAFETY_LIMITS}


def test_observation_carries_deterministic_margins(tmp_path):
    env = TEPEnvironment(make_config(tmp_path))
    observation = env.reset()
    for limit in SAFETY_LIMITS:
        value = observation.measurements[limit.variable]
        assert observation.safety_margins[limit.limit_id] == limit.margin(value)


def test_level_limits_match_upstream_shutdown_volumes(tmp_path):
    env = TEPEnvironment(make_config(tmp_path))
    env.reset()
    tp = env._sim.process._teproc
    vessels = {"reactor": ("vlr", 84.6, 666.7), "separator": ("vls", 27.5, 290.0),
               "stripper": ("vlc", 78.25, tp.vtc)}
    for limit in SAFETY_LIMITS:
        vessel = limit.limit_id.split("_")[0]
        if vessel not in vessels or "level" not in limit.limit_id:
            continue
        attribute, offset, span = vessels[vessel]
        original = getattr(tp, attribute)
        volume = limit.threshold / 100.0 * span + offset  # inverse of the XMEAS formula
        outward = 1e-6 if limit.direction == "max" else -1e-6
        for delta, expected in ((outward, True), (-outward, False)):
            setattr(tp, attribute, volume + delta)
            assert env._sim.process.is_shutdown() is expected, (limit.limit_id, delta)
        setattr(tp, attribute, original)


# -- acceptance 5: identical rollouts give equivalent evaluations --------------------
def test_identical_rollouts_give_identical_evaluations(tmp_path):
    _, first = cooling_loss_rollout(tmp_path / "a")
    _, second = cooling_loss_rollout(tmp_path / "b")
    assert first.telemetry.sha256 == second.telemetry.sha256
    assert evaluate_safety(first) == evaluate_safety(second)
    assert evaluate_safety(first) == evaluate_safety(first)


def test_tampered_or_inconsistent_telemetry_is_rejected(tmp_path):
    _, rollout = cooling_loss_rollout(tmp_path)
    with pytest.raises(InvalidEnvironmentState):
        evaluate_safety(replace(rollout, telemetry=ArtifactRef(rollout.telemetry.path, "0" * 64)))
    with pytest.raises(InvalidEnvironmentState):
        evaluate_safety(replace(rollout, termination_reason="horizon_reached"))
    with pytest.raises(InvalidEnvironmentState):
        evaluate_safety("narrative: the plant was safe")


def test_safety_evaluation_is_immutable(tmp_path):
    env, rollout = cooling_loss_rollout(tmp_path)
    evaluation = env.evaluate_safety(rollout)
    with pytest.raises(FrozenInstanceError):
        evaluation.shutdown_occurred = False
    with pytest.raises(TypeError):
        evaluation.minimum_safety_margins["reactor_pressure_high"] = None


# -- boundary ------------------------------------------------------------------------
def test_a4_modules_have_no_agent_runtime_or_model_imports():
    banned = ("industrial_agent_runtime", "tep_agent_lab", "langgraph", "openai",
              "anthropic", "mcp")
    root = Path(tep_sim.__file__).parent
    for name in ("capability.py", "scenario.py", "safety.py"):
        tree = ast.parse((root / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules = ([a.name for a in node.names] if isinstance(node, ast.Import)
                       else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            assert not any(m.split(".")[0] in banned for m in modules), (name, modules)


# -- review hardening ----------------------------------------------------------------
def test_planned_constraint_is_enforced_within_one_scenario(tmp_path, monkeypatch):
    def mapping(value):
        return scenario_module.ScenarioMapping(
            "fixture_guarded", "fixture", "test", frozenset(ControlMode), {},
            lambda _: (tep_sim.MVConstraint("XMV(10)", 30.0, 60.0),
                       MVIntervention("XMV(10)", value)))
    env = TEPEnvironment(make_config(tmp_path, ControlMode.MANUAL))
    env.reset()
    before = state(env)
    monkeypatch.setattr(scenario_module, "_BY_ID", {"fixture_guarded": mapping(70.0)})
    with pytest.raises(tep_sim.InvalidIntervention, match="active constraint"):
        env.apply_scenario(ScenarioRequest("fixture_guarded"))
    assert state(env) == before
    monkeypatch.setattr(scenario_module, "_BY_ID", {"fixture_guarded": mapping(35.0)})
    env.apply_scenario(ScenarioRequest("fixture_guarded"))
    assert env.observe().manipulated_variables["XMV(10)"] == 35.0
    assert env._constraints["XMV(10)"] == (30.0, 60.0)


def test_flow_reduction_must_actually_reduce_the_current_valve_position(tmp_path):
    pure = compile_scenario(ScenarioRequest("reactor_cooling_water_flow_reduction",
                                            {"valve_position_percent": 95}), ControlMode.MANUAL)
    assert pure.provenance["state_precondition"]["checked"] is False
    env = TEPEnvironment(make_config(tmp_path, ControlMode.MANUAL))
    env.reset()
    before = state(env)
    request = ScenarioRequest("reactor_cooling_water_flow_reduction",
                              {"valve_position_percent": 95})
    assert isinstance(env.compile_scenario(request), InvalidScenario)
    with pytest.raises(InvalidScenarioError):
        env.apply_scenario(request)
    assert state(env) == before
    applied = env.apply_scenario(COOLING_LOSS)
    assert applied.provenance["state_precondition"]["checked"] is True


def test_disturbances_active_at_rollout_start_are_reported(tmp_path):
    env = TEPEnvironment(make_config(tmp_path))
    env.reset()
    env.apply_scenario(ScenarioRequest("reactor_cooling_water_inlet_temperature_step"))
    events = env.evaluate_safety(env.rollout(0.01)).relevant_process_events
    assert events[0].kind == "disturbance_active" and events[0].subject == "IDV(4)"


def test_limit_values_come_from_vendored_upstream_constants():
    from tep.constants import SAFETY_LIMITS as upstream
    limits = {limit.limit_id: limit for limit in SAFETY_LIMITS}
    assert limits["reactor_pressure_high"].threshold == upstream.reactor_pressure_max
    assert limits["reactor_temperature_high"].threshold == upstream.reactor_temp_max
