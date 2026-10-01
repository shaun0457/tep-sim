"""Deterministic semantic scenario compilation.

A semantic request compiles to TEP interventions only through an explicit, tested
mapping in this table. Ambiguous requests are returned to the caller as
``AmbiguousScenario``; the environment never resolves them with a model.
"""
import math
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Mapping

from .capability import CAPABILITY_VERSION, UNSUPPORTED_CONSEQUENCE_DOMAINS
from .contracts import ControlMode, DisturbanceIntervention, MVIntervention
from .frozen import deep_freeze
from .registry import REGISTRY, UPSTREAM_REVISION

SCENARIO_MAPPING_VERSION = "tep-sim.scenarios/v0"
_ALL_MODES = frozenset(ControlMode)


@dataclass(frozen=True)
class ScenarioRequest:
    scenario_id: str
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SupportedScenario:
    scenario_id: str
    interventions: tuple
    provenance: Mapping[str, Any]

    def __post_init__(self):
        object.__setattr__(self, "interventions", tuple(self.interventions))
        object.__setattr__(self, "provenance", deep_freeze(dict(self.provenance)))


@dataclass(frozen=True)
class UnsupportedScenario:
    scenario_id: str
    reason: str
    missing_capability: str


@dataclass(frozen=True)
class AmbiguousScenario:
    scenario_id: str
    candidates: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class InvalidScenario:
    reason: str
    scenario_id: str | None = None


@dataclass(frozen=True)
class ScenarioMapping:
    scenario_id: str
    description: str
    source: str
    control_modes: frozenset
    parameters: Mapping[str, tuple[float, float, str]]
    build: Callable[[Mapping[str, float]], tuple]
    # (description, check(values, observation) -> violation reason | None)
    state_precondition: tuple[str, Callable] | None = None


def _idv(index):
    return lambda _: (DisturbanceIntervention(f"IDV({index})", 1),)


def _idv_source(index):
    return f"vendored DISTURBANCE_NAMES IDV({index}): {REGISTRY[f'IDV({index})'].name}"


_SCENARIOS = (
    ScenarioMapping(
        "reactor_cooling_water_inlet_temperature_step",
        "Step increase of the reactor cooling-water inlet temperature",
        _idv_source(4), _ALL_MODES, {}, _idv(4)),
    ScenarioMapping(
        "reactor_cooling_water_inlet_temperature_random_variation",
        "Random variation of the reactor cooling-water inlet temperature",
        _idv_source(11), _ALL_MODES, {}, _idv(11)),
    ScenarioMapping(
        "reactor_cooling_water_flow_reduction",
        "Hold the reactor cooling-water valve at a reduced manual position",
        f"vendored MANIPULATED_VAR_NAMES XMV(10): {REGISTRY['XMV(10)'].name}",
        frozenset({ControlMode.MANUAL}),
        {"valve_position_percent": (0.0, 100.0, "%")},
        lambda p: (MVIntervention("XMV(10)", float(p["valve_position_percent"])),),
        ("valve_position_percent < current XMV(10)",
         lambda p, obs: None if p["valve_position_percent"]
         < obs.manipulated_variables["XMV(10)"]
         else "a reduction must close XMV(10) below its current position")),
    ScenarioMapping(
        "condenser_cooling_water_inlet_temperature_step",
        "Step increase of the condenser cooling-water inlet temperature",
        _idv_source(5), _ALL_MODES, {}, _idv(5)),
)
_BY_ID = MappingProxyType({s.scenario_id: s for s in _SCENARIOS})

# Semantic terms that name more than one tested mapping. Returned, never resolved.
_AMBIGUOUS = MappingProxyType({
    "loss_of_cooling": ("condenser_cooling_water_inlet_temperature_step",
                        "reactor_cooling_water_flow_reduction",
                        "reactor_cooling_water_inlet_temperature_step"),
    "reactor_cooling_degradation": ("reactor_cooling_water_flow_reduction",
                                    "reactor_cooling_water_inlet_temperature_random_variation",
                                    "reactor_cooling_water_inlet_temperature_step"),
})


def scenario_catalog() -> tuple[ScenarioMapping, ...]:
    return _SCENARIOS


def ambiguous_terms() -> Mapping[str, tuple[str, ...]]:
    return _AMBIGUOUS


def compile_scenario(request: Any, control_mode: ControlMode, observation=None):
    """Total, deterministic compilation. Never raises for malformed input.

    ``observation`` (the current environment state) enables state preconditions;
    without it they are recorded as unchecked in provenance.
    """
    if not isinstance(request, ScenarioRequest):
        return InvalidScenario("ScenarioRequest required")
    scenario_id = request.scenario_id
    if type(scenario_id) is not str or not scenario_id:
        return InvalidScenario("scenario_id must be a nonempty string")
    if not isinstance(control_mode, ControlMode):
        return InvalidScenario("explicit ControlMode required", scenario_id)
    if scenario_id in UNSUPPORTED_CONSEQUENCE_DOMAINS:
        return UnsupportedScenario(
            scenario_id, UNSUPPORTED_CONSEQUENCE_DOMAINS[scenario_id],
            f"consequence:{scenario_id}")
    if scenario_id in _AMBIGUOUS:
        return AmbiguousScenario(scenario_id, _AMBIGUOUS[scenario_id],
                                 "term maps to several tested scenarios; caller must choose")
    mapping = _BY_ID.get(scenario_id)
    if mapping is None:
        return UnsupportedScenario(scenario_id, "no tested deterministic mapping exists",
                                   f"scenario:{scenario_id}")
    parameters = request.parameters
    if not isinstance(parameters, Mapping):
        return InvalidScenario("parameters must be a mapping", scenario_id)
    unknown = sorted(str(key) for key in parameters if key not in mapping.parameters)
    if unknown:
        return InvalidScenario(f"unknown parameters {unknown}", scenario_id)
    values = {}
    for name, (low, high, _unit) in mapping.parameters.items():
        if name not in parameters:
            return InvalidScenario(f"missing parameter {name!r}", scenario_id)
        value = parameters[name]
        if type(value) not in (int, float) or not math.isfinite(value):
            return InvalidScenario(f"parameter {name!r} must be a finite number", scenario_id)
        if not low <= value <= high:
            return InvalidScenario(f"parameter {name!r} outside [{low}, {high}]", scenario_id)
        values[name] = value
    if control_mode not in mapping.control_modes:
        modes = ",".join(sorted(m.value for m in mapping.control_modes))
        return UnsupportedScenario(
            scenario_id, f"requires control mode {modes}; configured {control_mode.value}",
            f"control_mode:{modes}")
    precondition = None
    if mapping.state_precondition is not None:
        description, check = mapping.state_precondition
        precondition = {"condition": description, "checked": observation is not None}
        if observation is not None:
            violation = check(values, observation)
            if violation:
                return InvalidScenario(violation, scenario_id)
    return SupportedScenario(scenario_id, mapping.build(values), {
        "scenario_id": scenario_id, "mapping_version": SCENARIO_MAPPING_VERSION,
        "capability_version": CAPABILITY_VERSION, "upstream_revision": UPSTREAM_REVISION,
        "control_mode": control_mode.value, "parameters": dict(sorted(values.items())),
        "state_precondition": precondition, "source": mapping.source})
