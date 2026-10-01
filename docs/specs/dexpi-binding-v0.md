# DEXPI / TEP Binding v0

Status: proposal  
Version: v0  
Owner repo: `tep-sim`  
Depends on: machine-readable TEP process representation, canonical TEP variable registry

## Goal

Provide a compact, queryable process-semantic layer for the Tennessee Eastman environment without building P&ID OCR or a generic plant-model generator.

DEXPI/process data describes **what exists and how it is connected**. The TEP simulator describes **how the dynamic state evolves**. A deterministic binding registry connects the two.

## Input boundary

v0 starts from machine-readable process data only. Accepted sources may include:

- DEXPI Process / DEXPI-compatible XML;
- a curated equivalent graph fixture derived from an authoritative TEP representation.

Raster/vector P&ID recognition is explicitly out of scope.

## `ProcessGraph`

The normalized graph MUST provide stable internal IDs independent of source-file formatting.

Minimum conceptual model:

```text
ProcessNode
- node_id
- kind
- name/tag
- attributes
- source_refs

ProcessEdge
- edge_id
- kind
- source_node
- target_node
- stream/tag metadata
- source_refs

VariableBinding
- semantic_entity_id
- relation
- runtime_variable_id
- runtime_variable_kind
- confidence/provenance
```

## Required query surface

The environment SHOULD expose or support adapters for:

```text
get_process_nodes()
get_node(node_id)
get_neighbors(node_id)
get_upstream(node_id)
get_downstream(node_id)
trace_stream(stream_id)
get_measurements(node_id)
get_actuators(node_id)
get_related_disturbances(node_id)
get_binding(runtime_variable_id | semantic_entity_id)
```

Exact Python naming may differ.

## Binding registry

Bindings MUST be explicit deterministic data/code, not inferred at runtime by an LLM.

Example relationships:

```text
reactor.temperature_measurement -> XMEAS(9)
reactor_cooling.outlet_temperature -> XMEAS(21)
reactor_cooling.flow_actuator -> XMV(10)
```

Every binding MUST carry provenance indicating how it was established, for example source metadata, upstream constants, or human-verified mapping.

## Validation

The importer/binder MUST detect at least:

- duplicate canonical IDs;
- dangling graph edges;
- bindings to unknown XMEAS/XMV/IDV IDs;
- conflicting one-to-one bindings where uniqueness is required;
- source entities that cannot be normalized;
- runtime variables expected by a fixture but absent in the vendored simulator.

Warnings may be allowed for intentionally unbound entities; silent dropping is not allowed.

## Source of truth

Runtime variable identity and current XMEAS/XMV/IDV metadata come from the vendored simulator/constants. DEXPI/process data may provide semantics/topology but MUST NOT override runtime IDs based on a literature table when the simulator disagrees.

## Agent-facing projection

Agent tools SHOULD receive a compact graph projection rather than raw DEXPI XML. Raw XML may be retained for provenance/debugging.

A projection returned for a node should contain only relevant local topology and bindings unless a broader traversal is requested.

## Invariants

- No model/LLM call is required to parse an already supported structured source.
- Graph queries are deterministic for a fixed source/version.
- Runtime bindings are validated against the canonical variable registry.
- Missing/ambiguous bindings are explicit.
- DEXPI presence does not imply a corresponding dynamic model exists beyond what TEP supports.

## Acceptance tests

1. Load the chosen TEP structured representation into `ProcessGraph`.
2. Validate graph connectivity with no silent dangling references.
3. Resolve reactor-related topology and the known XMEAS(9)/XMEAS(21)/XMV(10) relationships.
4. Reject an intentionally corrupted runtime-variable binding.
5. Produce a compact local topology projection for an agent tool without raw XML.
6. Record source/version provenance for every imported graph fixture.

## Open questions

- Which exact DEXPI representation/version becomes the pinned v0 fixture?
- Do process-control-loop concepts live directly in `ProcessGraph` v0 or in a later extension?
- Which topology traversal library, if any, is worth adding versus a small internal graph representation?

## A3 implementation notes (v0)

Implemented in `tep_sim.process`, `tep_sim.bindings`, and `tep_sim.evaluator_bindings`.

- Pinned v0 fixture: `src/tep_sim/fixtures/tep_process_graph_v0.json`. It is a
  curated equivalent graph (`CURATED_EQUIVALENT_GRAPH`) derived from Downs & Vogel
  (1993) and the vendored upstream constants, not the official DEXPI
  `TennesseeEastman.xml`. `review_status` stays `PENDING_HUMAN_REVIEW` and bindings
  use method `CURATED_MAPPING` until a human reviewer upgrades them to
  `HUMAN_VERIFIED_MAPPING` under a new fixture version.
- Versioning: every fixture carries `fixture_id`, `fixture_version`,
  `upstream_revision`, and declared sources. A canonical content hash
  (independent of whitespace, key order, and array order) is recorded in
  provenance. Pinned `(fixture_id, fixture_version)` pairs reject content drift.
- Query-name mapping: `nodes/node/edges/edge`, `neighbors`, `upstream`,
  `downstream` (bounded or transitive, cycle-safe), `trace_stream(edge_id)`,
  `measurements`, `actuators`, `binding(runtime id | semantic entity id)`, and
  `project_local(node_id)` for the compact Agent projection.
- `get_related_disturbances` is **not** part of `ProcessGraph` or its projection.
  Per D-014 and the design-review adjudication ("Blind tools hide canonical
  candidate bindings by default"), IDV bindings live only in the separate
  `EVALUATOR_ONLY` registry (`load_evaluator_disturbance_bindings`), which is bound
  to one exact graph content hash, is not re-exported from `tep_sim`, and must not
  be wrapped as an Agent-visible tool. The visible graph rejects any `DISTURBS`
  binding or `IDV(n)` reference at load time.
- Process-control loops are not modeled in v0; no traversal library is added.

### Known source/nomenclature disagreement: XMEAS(22)

- Upstream/Fortran (vendored `REGISTRY`) names XMEAS(22)
  `Separator Cooling Water Outlet Temp`.
- The curated v0 topology attaches it to `condenser_cooling_water_out`
  (`condenser_cooling.outlet_temperature`) based on the TEP flowsheet.
- This is a recorded source/nomenclature disagreement, not an error that is
  corrected by renaming. The binding is deliberately **not** changed to match the
  upstream variable name and remains `CURATED_MAPPING` / `PENDING_HUMAN_REVIEW`.
- A3 development may proceed on the curated graph. **D0 benchmark freeze requires a
  human review** of the curated topology and all bindings, including XMEAS(22).
- A human-verified mapping must be published as a **new fixture version with its own
  provenance and pin** (`HUMAN_VERIFIED_MAPPING`, updated `review_status`). The
  pinned `tep-process-graph` 0.1.0 content must never be silently modified; its
  pinned hash rejects in-place edits.
- `tests/test_process_graph.py::test_xmeas22_known_nomenclature_disagreement_stays_pending_review`
  locks the current state so any re-binding is an explicit, reviewed change.
