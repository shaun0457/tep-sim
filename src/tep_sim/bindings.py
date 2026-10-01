"""Deterministic semantic-entity <-> runtime-variable binding contracts.

Runtime identity comes only from ``registry.REGISTRY``; fixtures may name process
entities but can never introduce, rename, or override XMEAS/XMV/IDV identities.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .registry import REGISTRY


class BindingRelation(str, Enum):
    MEASURES = "MEASURES"
    ACTUATES = "ACTUATES"
    DISTURBS = "DISTURBS"  # evaluator-scope only; never part of an Agent-visible graph


class BindingMethod(str, Enum):
    UPSTREAM_CONSTANTS = "UPSTREAM_CONSTANTS"
    SOURCE_METADATA = "SOURCE_METADATA"
    CURATED_MAPPING = "CURATED_MAPPING"
    HUMAN_VERIFIED_MAPPING = "HUMAN_VERIFIED_MAPPING"


RELATION_KIND = {
    BindingRelation.MEASURES: "XMEAS",
    BindingRelation.ACTUATES: "XMV",
    BindingRelation.DISTURBS: "IDV",
}
VISIBLE_RELATIONS = frozenset({BindingRelation.MEASURES, BindingRelation.ACTUATES})


def runtime_kind(runtime_variable_id: str) -> str:
    return runtime_variable_id.split("(", 1)[0]


@dataclass(frozen=True)
class BindingProvenance:
    method: BindingMethod
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class VariableBinding:
    semantic_entity_id: str
    attached_to: str
    relation: BindingRelation
    runtime_variable_id: str
    runtime_variable_kind: str
    quantity: str
    provenance: BindingProvenance

    def describe(self) -> dict[str, Any]:
        variable = REGISTRY[self.runtime_variable_id]
        return {
            "semantic_entity_id": self.semantic_entity_id,
            "attached_to": self.attached_to,
            "relation": self.relation.value,
            "runtime_variable_id": self.runtime_variable_id,
            "runtime_variable_kind": self.runtime_variable_kind,
            "runtime_variable_name": variable.name,
            "unit": variable.unit,
            "quantity": self.quantity,
        }


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    ref: str
    message: str


def parse_binding(raw: Any, index: int, known_sources: Mapping[str, Any],
                  issues: list[ValidationIssue]) -> VariableBinding | None:
    """Normalize one raw binding; append every problem instead of dropping silently."""
    ref = f"bindings[{index}]"
    if not isinstance(raw, Mapping):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, "binding is not an object"))
        return None
    ref = str(raw.get("semantic_entity_id") or ref)
    fields = ("semantic_entity_id", "attached_to", "relation", "runtime_variable_id",
              "quantity")
    if any(not isinstance(raw.get(name), str) or not raw.get(name) for name in fields):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref,
                                      f"binding requires non-empty string fields {fields}"))
        return None
    try:
        relation = BindingRelation(raw["relation"])
    except ValueError:
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref,
                                      f"unknown relation {raw['relation']!r}"))
        return None
    provenance = raw.get("provenance")
    if not isinstance(provenance, Mapping):
        issues.append(ValidationIssue("MISSING_PROVENANCE", ref, "binding has no provenance"))
        return None
    extra = sorted(set(provenance) - {"method", "source_refs"})
    if extra:
        issues.append(ValidationIssue("MISSING_PROVENANCE", ref,
                                      f"unknown provenance fields {extra}"))
        return None
    try:
        method = BindingMethod(provenance.get("method"))
    except ValueError:
        issues.append(ValidationIssue("MISSING_PROVENANCE", ref,
                                      f"unknown provenance method {provenance.get('method')!r}"))
        return None
    source_refs = provenance.get("source_refs")
    if (not isinstance(source_refs, list) or not source_refs
            or not all(isinstance(item, str) for item in source_refs)):
        issues.append(ValidationIssue("MISSING_PROVENANCE", ref,
                                      "provenance.source_refs must be a non-empty string list"))
        return None
    for item in source_refs:
        if item not in known_sources:
            issues.append(ValidationIssue("UNKNOWN_SOURCE_REF", ref, f"unknown source {item!r}"))
    runtime_id = raw["runtime_variable_id"]
    if runtime_id not in REGISTRY:
        issues.append(ValidationIssue("UNKNOWN_RUNTIME_VARIABLE", ref,
                                      f"{runtime_id} is absent from the vendored simulator"))
        return None
    if runtime_kind(runtime_id) != RELATION_KIND[relation]:
        issues.append(ValidationIssue("RUNTIME_KIND_MISMATCH", ref,
                                      f"{relation.value} cannot bind {runtime_id}"))
        return None
    return VariableBinding(raw["semantic_entity_id"], raw["attached_to"], relation, runtime_id,
                           runtime_kind(runtime_id), raw["quantity"],
                           BindingProvenance(method, tuple(source_refs)))


def check_unique_bindings(bindings: list[VariableBinding],
                          issues: list[ValidationIssue]) -> None:
    """Semantic entities and bound runtime variables are one-to-one."""
    entities: dict[str, str] = {}
    runtime: dict[str, str] = {}
    for binding in bindings:
        if binding.semantic_entity_id in entities:
            issues.append(ValidationIssue("DUPLICATE_ID", binding.semantic_entity_id,
                                          "semantic entity bound more than once"))
        entities[binding.semantic_entity_id] = binding.runtime_variable_id
        previous = runtime.get(binding.runtime_variable_id)
        if previous is not None and previous != binding.semantic_entity_id:
            issues.append(ValidationIssue(
                "CONFLICTING_BINDING", binding.runtime_variable_id,
                f"bound by both {previous} and {binding.semantic_entity_id}"))
        runtime[binding.runtime_variable_id] = binding.semantic_entity_id
