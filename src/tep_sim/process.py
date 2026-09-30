"""Static ProcessGraph topology: normalization, validation, queries, Agent projection.

The graph is engineering semantics only. It holds no simulator state, performs no
simulation, and never carries disturbance (IDV) bindings: those live in the
evaluator-scope registry in ``evaluator_bindings`` so a blind Agent-visible
projection cannot enumerate the injected-fault candidate space.
"""
import hashlib
import json
import re
from collections import deque
from dataclasses import dataclass
from enum import Enum
from importlib import resources
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .bindings import (VISIBLE_RELATIONS, BindingRelation, ValidationIssue, VariableBinding,
                       check_unique_bindings, parse_binding, runtime_kind)
from .errors import ProcessGraphValidationError, UnknownProcessEntity
from .registry import REGISTRY, UPSTREAM_REVISION

GRAPH_SCHEMA_VERSION = "tep-sim.process-graph/v0"
PACKAGED_GRAPH_FIXTURE = "tep_process_graph_v0.json"
# (fixture_id, fixture_version) -> canonical content sha256. A pinned version whose
# content changes is rejected: new content requires a new fixture version.
PINNED_FIXTURES = MappingProxyType({
    ("tep-process-graph", "0.1.0"):
        "2b4adf9406674fd7c91f3ee48a6a96ef23992d682036059dcb6706e825d01f2b",
    ("tep-evaluator-disturbance-bindings", "0.1.0"):
        "b497fdca4c4e436ba084bd120b989fe51e0b33a449164fe553be1f0c6b9b6a22",
})

_ID = re.compile(r"^[a-z][a-z0-9_]*$")
# Any spelling of a disturbance id (IDV(4), IDV6, idv_1, IDV-3, ...), even inside a
# larger token; the visible graph never needs one.
_DISTURBANCE_REF = re.compile(r"(?<![A-Za-z])IDV[\s_\-(]*\d+", re.IGNORECASE)
_SCALAR = (str, int, float, bool, type(None))
_TOP_KEYS = {"schema_version", "fixture_id", "fixture_version", "upstream_revision", "source",
             "sources", "expected_runtime_variables", "nodes", "edges", "bindings",
             "unbound_entities"}
_NODE_KEYS = {"node_id", "kind", "name", "tag", "attributes", "source_refs"}
_EDGE_KEYS = {"edge_id", "kind", "source_node", "target_node", "name", "stream_number",
              "attributes", "source_refs"}


class NodeKind(str, Enum):
    FEED_SOURCE = "FEED_SOURCE"
    MIXER = "MIXER"
    REACTOR = "REACTOR"
    CONDENSER = "CONDENSER"
    SEPARATOR = "SEPARATOR"
    COMPRESSOR = "COMPRESSOR"
    STRIPPER = "STRIPPER"
    PRODUCT_SINK = "PRODUCT_SINK"
    UTILITY_SOURCE = "UTILITY_SOURCE"
    UTILITY_SINK = "UTILITY_SINK"


class EdgeKind(str, Enum):
    MATERIAL_STREAM = "MATERIAL_STREAM"
    UTILITY_STREAM = "UTILITY_STREAM"


@dataclass(frozen=True)
class ProcessNode:
    node_id: str
    kind: NodeKind
    name: str
    tag: str | None
    attributes: Mapping[str, Any]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class ProcessEdge:
    edge_id: str
    kind: EdgeKind
    source_node: str
    target_node: str
    name: str
    stream_number: int | None
    attributes: Mapping[str, Any]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    title: str
    locator: str
    revision: str | None


@dataclass(frozen=True)
class GraphProvenance:
    schema_version: str
    fixture_id: str
    fixture_version: str
    upstream_revision: str
    source_kind: str
    review_status: str
    content_sha256: str
    pinned: bool
    sources: tuple[SourceRef, ...]


@dataclass(frozen=True)
class StreamTrace:
    edge: ProcessEdge
    source: ProcessNode
    target: ProcessNode
    bindings: tuple[VariableBinding, ...]


def _canonical(value: Any) -> str:
    # Arrays in these fixtures are unordered sets, so element order is normalized too.
    if isinstance(value, Mapping):
        items = (f"{json.dumps(str(k))}:{_canonical(v)}" for k, v in sorted(value.items()))
        return "{" + ",".join(items) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(sorted(_canonical(item) for item in value)) + "]"
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def canonical_sha256(data: Any) -> str:
    """Content hash independent of whitespace, key order, and array order."""
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from _strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item)


@dataclass(frozen=True)
class TopologyProjection:
    """Compact, immutable, local Agent-facing view of one node. Never raw source data."""
    graph: Mapping[str, Any]
    node: Mapping[str, Any]
    incident_edges: tuple[Mapping[str, Any], ...]
    neighbors: tuple[Mapping[str, Any], ...]
    bindings: tuple[Mapping[str, Any], ...]

    def __post_init__(self):
        for binding in self.bindings:
            if binding["runtime_variable_kind"] not in ("XMEAS", "XMV"):
                raise ValueError("projection cannot carry non-visible runtime bindings")
        for name in ("graph", "node", "incident_edges", "neighbors", "bindings"):
            object.__setattr__(self, name, _freeze(getattr(self, name)))

    def as_dict(self) -> dict[str, Any]:
        return {name: _thaw(getattr(self, name))
                for name in ("graph", "node", "incident_edges", "neighbors", "bindings")}


class ProcessGraph:
    """Read-only normalized topology plus Agent-visible XMEAS/XMV bindings."""

    def __init__(self, provenance, nodes, edges, bindings, warnings):
        self._provenance = provenance
        self._nodes = MappingProxyType(dict(nodes))
        self._edges = MappingProxyType(dict(edges))
        self._bindings = tuple(sorted(bindings, key=lambda b: b.semantic_entity_id))
        self._by_entity = MappingProxyType({b.semantic_entity_id: b for b in self._bindings})
        self._by_runtime = MappingProxyType({b.runtime_variable_id: b for b in self._bindings})
        self._warnings = tuple(warnings)

    def __setattr__(self, name, value):
        if hasattr(self, "_warnings"):
            raise AttributeError("ProcessGraph is immutable")
        super().__setattr__(name, value)

    @property
    def provenance(self) -> GraphProvenance:
        return self._provenance

    @property
    def validation_warnings(self) -> tuple[ValidationIssue, ...]:
        return self._warnings

    # -- entity lookup -------------------------------------------------------------
    def nodes(self, kind: NodeKind | None = None) -> tuple[ProcessNode, ...]:
        return tuple(self._nodes[key] for key in sorted(self._nodes)
                     if kind is None or self._nodes[key].kind == kind)

    def edges(self, kind: EdgeKind | None = None) -> tuple[ProcessEdge, ...]:
        return tuple(self._edges[key] for key in sorted(self._edges)
                     if kind is None or self._edges[key].kind == kind)

    def node(self, node_id: str) -> ProcessNode:
        try:
            return self._nodes[node_id]
        except (KeyError, TypeError):
            raise UnknownProcessEntity(f"unknown process node {node_id!r}") from None

    def edge(self, edge_id: str) -> ProcessEdge:
        try:
            return self._edges[edge_id]
        except (KeyError, TypeError):
            raise UnknownProcessEntity(f"unknown process edge {edge_id!r}") from None

    def incident_edges(self, node_id: str) -> tuple[ProcessEdge, ...]:
        self.node(node_id)
        return tuple(edge for edge in self.edges()
                     if node_id in (edge.source_node, edge.target_node))

    # -- topology --------------------------------------------------------------------
    def _edge_filter(self, edge_kinds):
        if edge_kinds is None:
            return frozenset(EdgeKind)
        kinds = frozenset(edge_kinds)
        if not kinds or not all(isinstance(kind, EdgeKind) for kind in kinds):
            raise ValueError("edge_kinds must be a non-empty collection of EdgeKind")
        return kinds

    def neighbors(self, node_id: str, *, edge_kinds=None) -> tuple[str, ...]:
        kinds = self._edge_filter(edge_kinds)
        found = {edge.target_node if edge.source_node == node_id else edge.source_node
                 for edge in self.incident_edges(node_id) if edge.kind in kinds}
        return tuple(sorted(found))

    def _walk(self, node_id, max_depth, edge_kinds, forward):
        self.node(node_id)
        if max_depth is not None and (isinstance(max_depth, bool)
                                      or not isinstance(max_depth, int) or max_depth < 1):
            raise ValueError("max_depth must be a positive integer or None")
        kinds = self._edge_filter(edge_kinds)
        step = {}
        for edge in self.edges():
            if edge.kind in kinds:
                start, end = ((edge.source_node, edge.target_node) if forward
                              else (edge.target_node, edge.source_node))
                step.setdefault(start, set()).add(end)
        order, seen, queue = [], {node_id}, deque([(node_id, 0)])
        while queue:
            current, depth = queue.popleft()
            if max_depth is not None and depth >= max_depth:
                continue
            for nxt in sorted(step.get(current, ())):
                if nxt not in seen:
                    seen.add(nxt)
                    order.append(nxt)
                    queue.append((nxt, depth + 1))
        return tuple(order)

    def upstream(self, node_id: str, *, max_depth: int | None = 1,
                 edge_kinds=None) -> tuple[str, ...]:
        """Nodes reachable against flow direction, breadth-first, deterministic order."""
        return self._walk(node_id, max_depth, edge_kinds, forward=False)

    def downstream(self, node_id: str, *, max_depth: int | None = 1,
                   edge_kinds=None) -> tuple[str, ...]:
        return self._walk(node_id, max_depth, edge_kinds, forward=True)

    def trace_stream(self, edge_id: str) -> StreamTrace:
        edge = self.edge(edge_id)
        return StreamTrace(edge, self._nodes[edge.source_node], self._nodes[edge.target_node],
                           self._attached(edge_id))

    # -- bindings --------------------------------------------------------------------
    def _attached(self, entity_id, relation=None):
        return tuple(b for b in self._bindings if b.attached_to == entity_id
                     and (relation is None or b.relation == relation))

    def _entity_bindings(self, entity_id, relation, include_incident_streams):
        if entity_id in self._edges:
            return self._attached(entity_id, relation)
        self.node(entity_id)
        entities = [entity_id]
        if include_incident_streams:
            entities += [edge.edge_id for edge in self.incident_edges(entity_id)]
        return tuple(b for entity in entities for b in self._attached(entity, relation))

    def measurements(self, entity_id: str, *,
                     include_incident_streams: bool = False) -> tuple[VariableBinding, ...]:
        return self._entity_bindings(entity_id, BindingRelation.MEASURES,
                                     include_incident_streams)

    def actuators(self, entity_id: str, *,
                  include_incident_streams: bool = False) -> tuple[VariableBinding, ...]:
        return self._entity_bindings(entity_id, BindingRelation.ACTUATES,
                                     include_incident_streams)

    def bindings(self) -> tuple[VariableBinding, ...]:
        return self._bindings

    def binding(self, identifier: str) -> VariableBinding:
        """Resolve by runtime id (XMEAS/XMV) or semantic entity id."""
        found = self._by_runtime.get(identifier) or self._by_entity.get(identifier)
        if found is None:
            raise UnknownProcessEntity(f"no Agent-visible binding for {identifier!r}")
        return found

    # -- Agent-facing projection -------------------------------------------------------
    def project_local(self, node_id: str) -> TopologyProjection:
        node = self.node(node_id)
        edges = self.incident_edges(node_id)
        incident = []
        for edge in edges:
            outgoing = edge.source_node == node_id
            incident.append({
                "edge_id": edge.edge_id, "kind": edge.kind.value, "name": edge.name,
                "stream_number": edge.stream_number,
                "direction": "OUT" if outgoing else "IN",
                "neighbor": edge.target_node if outgoing else edge.source_node,
            })
        neighbors = [{"node_id": item.node_id, "kind": item.kind.value, "name": item.name}
                     for item in (self._nodes[key] for key in self.neighbors(node_id))]
        bindings = [b.describe() for entity in [node_id, *(e.edge_id for e in edges)]
                    for b in self._attached(entity)]
        provenance = self._provenance
        return TopologyProjection(
            graph={"fixture_id": provenance.fixture_id,
                   "fixture_version": provenance.fixture_version,
                   "content_sha256": provenance.content_sha256},
            node={"node_id": node.node_id, "kind": node.kind.value, "name": node.name,
                  "tag": node.tag},
            incident_edges=incident, neighbors=neighbors, bindings=bindings)


# -- normalization ---------------------------------------------------------------------
def _refs(raw, ref, sources, issues):
    if (not isinstance(raw, list) or not raw
            or not all(isinstance(item, str) for item in raw)):
        issues.append(ValidationIssue("MISSING_PROVENANCE", ref,
                                      "source_refs must be a non-empty string list"))
        return ()
    for item in raw:
        if item not in sources:
            issues.append(ValidationIssue("UNKNOWN_SOURCE_REF", ref, f"unknown source {item!r}"))
    return tuple(raw)


def _attributes(raw, ref, issues):
    if raw is None:
        return MappingProxyType({})
    if (not isinstance(raw, Mapping)
            or not all(isinstance(k, str) and isinstance(v, _SCALAR) for k, v in raw.items())):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref,
                                      "attributes must map strings to JSON scalars"))
        return MappingProxyType({})
    return MappingProxyType(dict(sorted(raw.items())))


def _unexpected(raw, allowed, ref, issues):
    extra = sorted(set(raw) - allowed)
    if extra:
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, f"unknown fields {extra}"))


def _parse_node(raw, index, sources, issues):
    ref = f"nodes[{index}]"
    if not isinstance(raw, Mapping):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, "node is not an object"))
        return None
    ref = str(raw.get("node_id") or ref)
    _unexpected(raw, _NODE_KEYS, ref, issues)
    node_id, name, tag = raw.get("node_id"), raw.get("name"), raw.get("tag")
    if not isinstance(node_id, str) or not _ID.match(node_id):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, "invalid node_id"))
        return None
    if not isinstance(name, str) or not name or not isinstance(tag, (str, type(None))):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, "invalid name/tag"))
        return None
    try:
        kind = NodeKind(raw.get("kind"))
    except ValueError:
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref,
                                      f"unknown node kind {raw.get('kind')!r}"))
        return None
    return ProcessNode(node_id, kind, name, tag, _attributes(raw.get("attributes"), ref, issues),
                       _refs(raw.get("source_refs"), ref, sources, issues))


def _parse_edge(raw, index, sources, issues):
    ref = f"edges[{index}]"
    if not isinstance(raw, Mapping):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, "edge is not an object"))
        return None
    ref = str(raw.get("edge_id") or ref)
    _unexpected(raw, _EDGE_KEYS, ref, issues)
    edge_id, number = raw.get("edge_id"), raw.get("stream_number")
    if not isinstance(edge_id, str) or not _ID.match(edge_id):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, "invalid edge_id"))
        return None
    if not all(isinstance(raw.get(k), str) and raw.get(k)
               for k in ("source_node", "target_node", "name")):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref,
                                      "edge requires source_node, target_node and name"))
        return None
    if number is not None and (isinstance(number, bool) or not isinstance(number, int)
                               or number < 1):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref,
                                      "stream_number must be a positive integer or null"))
        return None
    if raw["source_node"] == raw["target_node"]:
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref, "self-loop edge"))
        return None
    try:
        kind = EdgeKind(raw.get("kind"))
    except ValueError:
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", ref,
                                      f"unknown edge kind {raw.get('kind')!r}"))
        return None
    return ProcessEdge(edge_id, kind, raw["source_node"], raw["target_node"], raw["name"],
                       number, _attributes(raw.get("attributes"), ref, issues),
                       _refs(raw.get("source_refs"), ref, sources, issues))


def parse_sources(data, issues):
    raw = data.get("sources")
    if not isinstance(raw, Mapping) or not raw:
        issues.append(ValidationIssue("MISSING_PROVENANCE", "sources",
                                      "fixture must declare its sources"))
        return {}
    sources = {}
    for source_id, item in sorted(raw.items()):
        if (not isinstance(item, Mapping) or not isinstance(item.get("title"), str)
                or not isinstance(item.get("locator"), str)
                or not isinstance(item.get("revision"), (str, type(None)))):
            issues.append(ValidationIssue("MISSING_PROVENANCE", f"sources.{source_id}",
                                          "source requires title and locator"))
            continue
        sources[source_id] = SourceRef(source_id, item["title"], item["locator"],
                                       item.get("revision"))
    return sources


def check_header(data, schema_version, issues):
    """Shared fixture identity/revision/pin checks. Returns (id, version, sha, pinned)."""
    if data.get("schema_version") != schema_version:
        issues.append(ValidationIssue("SCHEMA_VERSION", "schema_version",
                                      f"expected {schema_version!r}"))
    if data.get("upstream_revision") != UPSTREAM_REVISION:
        issues.append(ValidationIssue(
            "REVISION_MISMATCH", "upstream_revision",
            f"fixture targets {data.get('upstream_revision')!r}, simulator is {UPSTREAM_REVISION}"))
    fixture_id, version = data.get("fixture_id"), data.get("fixture_version")
    if not isinstance(fixture_id, str) or not isinstance(version, str):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", "fixture_id",
                                      "fixture_id and fixture_version are required strings"))
    try:
        content_sha256 = canonical_sha256(data)
    except (TypeError, ValueError):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", "<root>",
                                      "fixture is not JSON-serializable"))
        content_sha256 = ""
    pinned = (PINNED_FIXTURES.get((fixture_id, version))
              if isinstance(fixture_id, str) and isinstance(version, str) else None)
    if pinned is not None and pinned != content_sha256:
        issues.append(ValidationIssue(
            "PINNED_CONTENT_MISMATCH", f"{fixture_id}@{version}",
            "content differs from the pinned fixture version; publish a new fixture_version"))
    return fixture_id, version, content_sha256, pinned is not None


def build_process_graph(data: Mapping[str, Any]) -> ProcessGraph:
    """Normalize and validate a structured fixture. All issues are reported together."""
    if not isinstance(data, Mapping):
        raise ProcessGraphValidationError(
            [ValidationIssue("UNNORMALIZABLE_ENTITY", "<root>", "fixture is not an object")])
    issues: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    _unexpected(data, _TOP_KEYS, "<root>", issues)
    fixture_id, version, content_sha256, pinned = check_header(
        data, GRAPH_SCHEMA_VERSION, issues)
    sources = parse_sources(data, issues)
    source = data.get("source")
    if not isinstance(source, Mapping) or not isinstance(source.get("kind"), str):
        issues.append(ValidationIssue("MISSING_PROVENANCE", "source", "source.kind is required"))
        source = {}
    for text in _strings({k: v for k, v in data.items() if k != "sources"}):
        if _DISTURBANCE_REF.search(text):
            issues.append(ValidationIssue(
                "DISTURBANCE_REFERENCE_IN_VISIBLE_GRAPH", text[:60],
                "disturbance identities belong to the evaluator-scope registry only"))

    nodes, edges = {}, {}
    for index, raw in enumerate(_list(data, "nodes", issues)):
        node = _parse_node(raw, index, sources, issues)
        if node is not None:
            if node.node_id in nodes:
                issues.append(ValidationIssue("DUPLICATE_ID", node.node_id, "duplicate node id"))
            nodes[node.node_id] = node
    stream_numbers = {}
    for index, raw in enumerate(_list(data, "edges", issues)):
        edge = _parse_edge(raw, index, sources, issues)
        if edge is None:
            continue
        if edge.edge_id in edges or edge.edge_id in nodes:
            issues.append(ValidationIssue("DUPLICATE_ID", edge.edge_id, "duplicate entity id"))
        for end in (edge.source_node, edge.target_node):
            if end not in nodes:
                issues.append(ValidationIssue("DANGLING_EDGE", edge.edge_id,
                                              f"references unknown node {end!r}"))
        if edge.stream_number is not None:
            if edge.stream_number in stream_numbers:
                issues.append(ValidationIssue("DUPLICATE_ID", edge.edge_id,
                                              f"stream {edge.stream_number} already defined"))
            stream_numbers[edge.stream_number] = edge.edge_id
        edges[edge.edge_id] = edge

    bindings = []
    for index, raw in enumerate(_list(data, "bindings", issues)):
        binding = parse_binding(raw, index, sources, issues)
        if binding is None:
            continue
        if binding.relation not in VISIBLE_RELATIONS:
            issues.append(ValidationIssue(
                "DISTURBANCE_BINDING_IN_VISIBLE_GRAPH", binding.semantic_entity_id,
                "disturbance bindings belong to the evaluator-scope registry only"))
            continue
        if binding.attached_to not in nodes and binding.attached_to not in edges:
            issues.append(ValidationIssue("DANGLING_ATTACHMENT", binding.semantic_entity_id,
                                          f"attached to unknown entity {binding.attached_to!r}"))
        bindings.append(binding)
    check_unique_bindings(bindings, issues)

    bound_runtime = {b.runtime_variable_id for b in bindings}
    expected = _list(data, "expected_runtime_variables", issues)
    for runtime_id in expected:
        if not isinstance(runtime_id, str) or runtime_id not in REGISTRY:
            issues.append(ValidationIssue("EXPECTED_VARIABLE_ABSENT", str(runtime_id),
                                          "expected runtime variable absent from simulator"))
        elif runtime_kind(runtime_id) not in ("XMEAS", "XMV"):
            issues.append(ValidationIssue("DISTURBANCE_BINDING_IN_VISIBLE_GRAPH", runtime_id,
                                          "visible graph can only expect XMEAS/XMV"))
        elif runtime_id not in bound_runtime:
            issues.append(ValidationIssue("EXPECTED_VARIABLE_UNBOUND", runtime_id,
                                          "expected runtime variable has no binding"))

    bound_entities = {b.attached_to for b in bindings}
    declared = {}
    for index, raw in enumerate(_list(data, "unbound_entities", issues)):
        if (not isinstance(raw, Mapping) or not isinstance(raw.get("entity_id"), str)
                or not isinstance(raw.get("reason"), str) or not raw.get("reason")):
            issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", f"unbound_entities[{index}]",
                                          "requires entity_id and non-empty reason"))
            continue
        entity = raw["entity_id"]
        if entity not in nodes and entity not in edges:
            issues.append(ValidationIssue("DANGLING_ATTACHMENT", entity,
                                          "declared unbound entity does not exist"))
        elif entity in bound_entities:
            issues.append(ValidationIssue("CONFLICTING_BINDING", entity,
                                          "declared unbound but has bindings"))
        declared[entity] = raw["reason"]
    for entity in sorted({*nodes, *edges} - bound_entities):
        if entity in declared:
            warnings.append(ValidationIssue("INTENTIONALLY_UNBOUND", entity, declared[entity]))
        else:
            issues.append(ValidationIssue("UNDECLARED_UNBOUND_ENTITY", entity,
                                          "entity has no binding and no unbound declaration"))

    if issues:
        raise ProcessGraphValidationError(issues)
    provenance = GraphProvenance(
        GRAPH_SCHEMA_VERSION, fixture_id, version, UPSTREAM_REVISION, source["kind"],
        str(source.get("review_status", "UNSPECIFIED")), content_sha256, pinned,
        tuple(sources[key] for key in sorted(sources)))
    return ProcessGraph(provenance, nodes, edges, bindings, warnings)


def _list(data, key, issues):
    value = data.get(key)
    if not isinstance(value, list):
        issues.append(ValidationIssue("UNNORMALIZABLE_ENTITY", key, f"{key} must be a list"))
        return []
    return value


def read_fixture(path: str | Path | None, packaged_name: str) -> Any:
    try:
        if path is None:
            text = resources.files("tep_sim.fixtures").joinpath(packaged_name).read_text(
                encoding="utf-8")
        else:
            text = Path(path).read_text(encoding="utf-8")
        return json.loads(text)
    except (OSError, ValueError) as exc:
        raise ProcessGraphValidationError(
            [ValidationIssue("UNNORMALIZABLE_ENTITY", str(path or packaged_name),
                             f"cannot read structured fixture: {exc}")]) from exc


def load_process_graph(path: str | Path | None = None) -> ProcessGraph:
    """Load the pinned packaged TEP graph, or an explicit structured fixture file."""
    return build_process_graph(read_fixture(path, PACKAGED_GRAPH_FIXTURE))
