"""EVALUATOR-ONLY disturbance (IDV) bindings.

This registry maps process entities to the injected-disturbance space. It exists
for evaluators, C0 baselines, and scenario authors. It is intentionally NOT
reachable from ``ProcessGraph`` or ``TopologyProjection`` and is not re-exported
from the ``tep_sim`` package namespace: exposing it to a blind RCA Agent would
leak the fault candidate/answer set. Consumers that register Agent tools must
never wrap this module.
"""
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .bindings import (BindingRelation, ValidationIssue, VariableBinding,
                       check_unique_bindings, parse_binding)
from .errors import ProcessGraphValidationError, UnknownProcessEntity
from .process import ProcessGraph, check_header, parse_sources, read_fixture
from .registry import REGISTRY, UPSTREAM_REVISION

EVALUATOR_SCHEMA_VERSION = "tep-sim.evaluator-disturbance-bindings/v0"
PACKAGED_EVALUATOR_FIXTURE = "tep_evaluator_disturbance_bindings_v0.json"
EVALUATOR_ONLY = "EVALUATOR_ONLY"
_KEYS = {"schema_version", "fixture_id", "fixture_version", "visibility", "upstream_revision",
         "graph_fixture_id", "graph_fixture_version", "graph_content_sha256", "source",
         "sources", "bindings", "unbound_runtime_variables"}


@dataclass(frozen=True)
class EvaluatorBindingProvenance:
    fixture_id: str
    fixture_version: str
    upstream_revision: str
    content_sha256: str
    pinned: bool
    graph_fixture_id: str
    graph_fixture_version: str
    graph_content_sha256: str


class EvaluatorDisturbanceBindings:
    """Hidden entity <-> IDV registry bound to one exact ProcessGraph content hash."""
    visibility = EVALUATOR_ONLY

    def __init__(self, provenance, bindings, unbound):
        self._provenance = provenance
        self._bindings = tuple(sorted(bindings, key=lambda b: b.runtime_variable_id.split("(")[0]
                                     + b.runtime_variable_id.split("(")[1].rstrip(")").zfill(3)))
        self._unbound = MappingProxyType(dict(unbound))

    @property
    def provenance(self) -> EvaluatorBindingProvenance:
        return self._provenance

    @property
    def unbound_disturbances(self) -> Mapping[str, str]:
        return self._unbound

    def bindings(self) -> tuple[VariableBinding, ...]:
        return self._bindings

    def disturbances_at(self, entity_id: str) -> tuple[VariableBinding, ...]:
        return tuple(b for b in self._bindings if b.attached_to == entity_id)

    def location_of(self, runtime_variable_id: str) -> VariableBinding:
        for binding in self._bindings:
            if binding.runtime_variable_id == runtime_variable_id:
                return binding
        raise UnknownProcessEntity(f"no evaluator binding for {runtime_variable_id!r}")


def build_evaluator_disturbance_bindings(
        data: Mapping[str, Any], graph: ProcessGraph) -> EvaluatorDisturbanceBindings:
    if not isinstance(data, Mapping):
        raise ProcessGraphValidationError(
            [ValidationIssue("UNNORMALIZABLE_ENTITY", "<root>", "fixture is not an object")])
    issues: list[ValidationIssue] = []
    extra = sorted(set(data) - _KEYS)
    if extra:
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", "<root>", f"unknown fields {extra}"))
    fixture_id, version, content_sha256, pinned = check_header(
        data, EVALUATOR_SCHEMA_VERSION, issues)
    if data.get("visibility") != EVALUATOR_ONLY:
        issues.append(ValidationIssue("VISIBILITY", "visibility",
                                      "disturbance bindings must be EVALUATOR_ONLY"))
    graph_prov = graph.provenance
    if (data.get("graph_fixture_id"), data.get("graph_fixture_version"),
            data.get("graph_content_sha256")) != (graph_prov.fixture_id,
                                                  graph_prov.fixture_version,
                                                  graph_prov.content_sha256):
        issues.append(ValidationIssue("GRAPH_VERSION_MISMATCH", "graph_content_sha256",
                                      "bindings target a different ProcessGraph version"))
    sources = parse_sources(data, issues)
    entities = {n.node_id for n in graph.nodes()} | {e.edge_id for e in graph.edges()}
    bindings = []
    raw_bindings = data.get("bindings")
    if not isinstance(raw_bindings, list):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", "bindings", "must be a list"))
        raw_bindings = []
    for index, raw in enumerate(raw_bindings):
        binding = parse_binding(raw, index, sources, issues)
        if binding is None:
            continue
        if binding.relation != BindingRelation.DISTURBS:
            issues.append(ValidationIssue("RUNTIME_KIND_MISMATCH", binding.semantic_entity_id,
                                          "evaluator registry holds DISTURBS bindings only"))
            continue
        if binding.attached_to not in entities:
            issues.append(ValidationIssue("DANGLING_ATTACHMENT", binding.semantic_entity_id,
                                          f"attached to unknown entity {binding.attached_to!r}"))
        bindings.append(binding)
    check_unique_bindings(bindings, issues)

    unbound = {}
    raw_unbound = data.get("unbound_runtime_variables")
    if not isinstance(raw_unbound, list):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", "unbound_runtime_variables",
                                      "must be a list"))
        raw_unbound = []
    for index, raw in enumerate(raw_unbound):
        if (not isinstance(raw, Mapping) or raw.get("runtime_variable_id") not in REGISTRY
                or not isinstance(raw.get("reason"), str) or not raw.get("reason")):
            issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY",
                                          f"unbound_runtime_variables[{index}]",
                                          "requires a known runtime_variable_id and reason"))
            continue
        unbound[raw["runtime_variable_id"]] = raw["reason"]
    bound = {b.runtime_variable_id for b in bindings}
    for runtime_id in sorted(set(unbound) & bound):
        issues.append(ValidationIssue("CONFLICTING_BINDING", runtime_id,
                                      "declared unbound but has a binding"))
    for runtime_id in (key for key in REGISTRY if key.startswith("IDV(")):
        if runtime_id not in bound and runtime_id not in unbound:
            issues.append(ValidationIssue("UNACCOUNTED_RUNTIME_VARIABLE", runtime_id,
                                          "disturbance neither bound nor declared unbound"))
    if issues:
        raise ProcessGraphValidationError(issues)
    provenance = EvaluatorBindingProvenance(
        fixture_id, version, UPSTREAM_REVISION, content_sha256, pinned,
        graph_prov.fixture_id, graph_prov.fixture_version, graph_prov.content_sha256)
    return EvaluatorDisturbanceBindings(provenance, bindings, unbound)


def load_evaluator_disturbance_bindings(
        graph: ProcessGraph, path: str | Path | None = None) -> EvaluatorDisturbanceBindings:
    """Evaluator/C0 use only. Never register the result behind an Agent-visible tool."""
    return build_evaluator_disturbance_bindings(
        read_fixture(path, PACKAGED_EVALUATOR_FIXTURE), graph)
