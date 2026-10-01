"""Machine-readable World Plane capability registry.

Every entry is derived deterministically from the vendored runtime metadata
(``REGISTRY``), the pinned upstream simulator behavior, and the versioned scenario
and safety-limit tables in this package. Nothing here is inferred by a model.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .registry import REGISTRY, UPSTREAM_REVISION

CAPABILITY_VERSION = "tep-sim.capabilities/v0"

DOMAINS = ("runtime_variables", "supported_disturbances", "supported_mv_interventions",
           "supported_constraints", "supported_semantic_scenarios", "snapshot_fidelity",
           "consequence_domains", "unsupported_domains")

# Consequence physics the TEP model does not contain. The environment must never
# report these as simulated facts.
UNSUPPORTED_CONSEQUENCE_DOMAINS = MappingProxyType({
    "pipe_rupture": "TEP has no mechanical integrity or loss-of-containment model",
    "fire": "TEP has no ignition, combustion, or fire model",
    "toxic_dispersion": "TEP has no atmospheric release or dispersion model",
    "blast_overpressure": "TEP has no explosion or overpressure propagation model",
    "personnel_casualty": "TEP has no exposure, vulnerability, or personnel model",
})

# Consequences the environment can state deterministically from simulator output.
SUPPORTED_CONSEQUENCE_DOMAINS = MappingProxyType({
    "process_trajectory": "numeric XMEAS/XMV trajectories from the pinned simulator",
    "process_shutdown": "upstream safety-shutdown (ISD) occurrence and time",
    "process_limit_margin": "deterministic margins to versioned shutdown limits",
})


@dataclass(frozen=True)
class CapabilityEntry:
    capability_id: str
    domain: str
    supported: bool
    description: str
    source: str
    preconditions: Mapping[str, Any] = field(default_factory=dict)
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "preconditions", MappingProxyType(dict(self.preconditions)))
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))

    def to_json(self) -> dict:
        return {"capability_id": self.capability_id, "domain": self.domain,
                "supported": self.supported, "description": self.description,
                "source": self.source, "preconditions": _plain(self.preconditions),
                "details": _plain(self.details)}


def _plain(value):
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


class CapabilityRegistry:
    """Immutable, versioned capability entries grouped by domain."""

    def __init__(self, backend: str, entries):
        self.version = CAPABILITY_VERSION
        self.upstream_revision = UPSTREAM_REVISION
        self.backend = backend
        groups = {domain: [] for domain in DOMAINS}
        for entry in entries:
            groups[entry.domain].append(entry)
        self._domains = MappingProxyType({d: tuple(e) for d, e in groups.items()})
        self._index = MappingProxyType({e.capability_id: e for e in entries})

    def domain(self, name: str) -> tuple[CapabilityEntry, ...]:
        if name not in self._domains:
            raise KeyError(f"unknown capability domain {name!r}")
        return self._domains[name]

    def entry(self, capability_id: str) -> CapabilityEntry:
        return self._index[capability_id]

    def supports(self, capability_id: str) -> bool:
        entry = self._index.get(capability_id)
        return entry is not None and entry.supported

    def to_json(self) -> dict:
        return {"capability_version": self.version,
                "upstream_revision": self.upstream_revision, "backend": self.backend,
                **{d: [e.to_json() for e in entries] for d, entries in self._domains.items()}}


MANUAL_ONLY = {"control_mode": ("manual",)}
_REGISTRY_SOURCE = f"vendored tep.constants @ {UPSTREAM_REVISION}"


def build_capability_registry(backend: str = "python") -> CapabilityRegistry:
    from .safety import SAFETY_LIMITS, SAFETY_LIMITS_VERSION
    from .scenario import SCENARIO_MAPPING_VERSION, scenario_catalog

    entries: list[CapabilityEntry] = []
    for variable in REGISTRY.values():
        kind = variable.canonical_id.split("(")[0]
        entries.append(CapabilityEntry(
            f"runtime_variable:{variable.canonical_id}", "runtime_variables", True,
            variable.name, _REGISTRY_SOURCE,
            details={"kind": kind, "index": variable.index, "unit": variable.unit,
                     "observable": kind in ("XMEAS", "XMV"),
                     "writable": kind in ("XMV", "IDV")}))
        if kind == "IDV":
            documented = variable.name != "Unknown"
            entries.append(CapabilityEntry(
                f"disturbance:{variable.canonical_id}", "supported_disturbances", True,
                variable.name, _REGISTRY_SOURCE,
                details={"values": (0, 1), "semantics_documented": documented,
                         "intervention": "DisturbanceIntervention"}))
        elif kind == "XMV":
            entries.append(CapabilityEntry(
                f"mv_intervention:{variable.canonical_id}", "supported_mv_interventions",
                True, variable.name, _REGISTRY_SOURCE, MANUAL_ONLY,
                {"min_value": 0.0, "max_value": 100.0, "unit": "%",
                 "intervention": "MVIntervention",
                 "reason": "CLOSED_LOOP PI control overwrites manual MV changes"}))
            entries.append(CapabilityEntry(
                f"mv_constraint:{variable.canonical_id}", "supported_constraints", True,
                f"manual admissibility bounds for {variable.name}", _REGISTRY_SOURCE,
                MANUAL_ONLY, {"min_value": 0.0, "max_value": 100.0, "unit": "%",
                              "intervention": "MVConstraint"}))
    for limit in SAFETY_LIMITS:
        entries.append(CapabilityEntry(
            f"safety_limit:{limit.limit_id}", "supported_constraints", True,
            limit.description, limit.source,
            details={"kind": "shutdown_limit", "variable": limit.variable,
                     "direction": limit.direction, "threshold": limit.threshold,
                     "unit": limit.unit, "limits_version": SAFETY_LIMITS_VERSION}))
    for scenario in scenario_catalog():
        entries.append(CapabilityEntry(
            f"scenario:{scenario.scenario_id}", "supported_semantic_scenarios", True,
            scenario.description, scenario.source,
            {"control_mode": tuple(sorted(m.value for m in scenario.control_modes))},
            {"parameters": {name: {"minimum": lo, "maximum": hi, "unit": unit}
                            for name, (lo, hi, unit) in scenario.parameters.items()},
             "mapping_version": SCENARIO_MAPPING_VERSION}))
    exact = backend == "python"
    entries.append(CapabilityEntry(
        f"snapshot:{backend}", "snapshot_fidelity", exact,
        "snapshot/fork of the complete simulator object", "tep_sim.snapshot (A2)",
        details={"fidelity": "exact" if exact else "unsupported",
                 "fork_randomness_policy": "cloned_state" if exact else None}))
    for name, description in SUPPORTED_CONSEQUENCE_DOMAINS.items():
        entries.append(CapabilityEntry(f"consequence:{name}", "consequence_domains", True,
                                       description, "tep_sim.safety"))
    for name, reason in UNSUPPORTED_CONSEQUENCE_DOMAINS.items():
        entries.append(CapabilityEntry(f"consequence:{name}", "unsupported_domains", False,
                                       reason, "pinned TEP model scope"))
    return CapabilityRegistry(backend, entries)
