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

- Pinned fixtures. Both are curated equivalent graphs (`CURATED_EQUIVALENT_GRAPH`),
  not the official DEXPI `TennesseeEastman.xml`:
  - `tep-process-graph` 0.1.0 (`src/tep_sim/fixtures/tep_process_graph_v0.json`):
    the immutable curated baseline, `PENDING_HUMAN_REVIEW`, all bindings
    `CURATED_MAPPING`.
  - `tep-process-graph` 0.2.0 (`src/tep_sim/fixtures/tep_process_graph_v0_2_0.json`):
    the canonical `HUMAN_VERIFIED` graph and the `load_process_graph()` default. See
    "Human-verified fixture 0.2.0" below.
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
  upstream variable name.
- The human reviewer retained the condenser attachment (Q1, Option A). It is
  `HUMAN_VERIFIED_MAPPING` in `tep-process-graph` 0.2.0 and stays `CURATED_MAPPING`
  in the immutable 0.1.0 baseline. The runtime name stays authoritative as a name.
- A human-verified mapping is published only as a **new fixture version with its own
  provenance and pin**. The pinned `tep-process-graph` 0.1.0 content must never be
  silently modified; its pinned hash rejects in-place edits.
- `tests/test_process_graph.py::test_xmeas22_known_nomenclature_disagreement_is_verified_without_renaming`
  locks this state so any re-binding is an explicit, reviewed change.

### Human-verification review package (status: HUMAN_SIGNOFF_RECORDED, promoted to 0.2.0)

The evidence package for the D0 human review lives in
`docs/reviews/a3-process-graph-human-verification.md`, with the machine-readable
matrix in `docs/reviews/a3-process-graph-binding-review-v0.json`. It covers every
Agent-visible binding and graph entity, plus a separate XMEAS(22) adjudication
package. An automated agent prepared it. The decisions of human reviewer
`chengting` (2026-10-01) are recorded there: 88/88 rows ACCEPT, and XMEAS(22)
Option A.

The signed package stays immutable historical decision evidence; its own text
predates the promotion. `tests/test_a3_review_package.py` checks that the evidence
and the decision record are complete and consistent. The promotion below implements
the record without making any new decision.

### Human-verified fixture 0.2.0 (frozen)

**Status values.** `source.review_status` is required and takes exactly one of:

- `PENDING_HUMAN_REVIEW`: curated, not yet signed off (0.1.0).
- `HUMAN_VERIFIED`: every binding was explicitly accepted in a signed human review
  record (0.2.0). A `HUMAN_VERIFIED` graph holds only `HUMAN_VERIFIED_MAPPING`
  bindings and carries a `review_record`.

Status, `review_record` and binding methods are either all verified or all not
verified. The loader rejects any other combination (`REVIEW_STATUS_MISMATCH` /
`MISSING_PROVENANCE`).

**`review_record` contract.** A verified fixture points to the signed record. It
does not copy the record's notes. `review_record` is an optional top-level object
with exactly these non-empty string fields (`tep_sim.ReviewRecordRef`):

| Field | Meaning |
|---|---|
| `review_package_id` | id of the signed review package |
| `review_package_version` | version of the signed package |
| `reviewer` | the human reviewer who signed |
| `signed_on` | ISO date of the sign-off |
| `locator` | repository path of the machine-readable record |
| `signed_record_sha256` | `canonical_sha256` of `{status, version, signoff, missing_sources, rows}` |

In that hash, `version` is `review_package_version`, and `rows` is the list of
`(review_id, human_reviewer_decision, reviewer, review_notes)` over all binding,
node and edge rows. It is the same hash that `tests/test_a3_review_package.py` pins.
Each `HUMAN_VERIFIED_MAPPING` binding corresponds to the record row with the same
`semantic_entity_id`. Free-text provenance fields are not allowed, either here or
in `sources`. The graph `source` object allows only `kind`, `description` and
`review_status`. A binding `provenance` allows only `method` and `source_refs`.

What the loader checks and what it does not:

- The loader checks the shape of `review_record`: exact keys, a `YYYY-MM-DD` date,
  and a 64-hex hash.
- The loader does not read the record file, because the packaged library does not
  ship `docs/`.
- That the reference matches the record (hash and per-row correspondence) is
  enforced by `tests/test_a3_promotion.py` and by the fixture's pinned content hash.
- An unpinned fixture that claims `HUMAN_VERIFIED` is unverified; check
  `provenance.pinned`.

**Source identity (F-10).** A `sources` entry allows only `title`, `locator`,
`revision` and an optional lowercase hex `sha256`. The `sha256` pins files that
have no revision, such as papers. In 0.2.0, every node, edge and binding cites the
`source_id`s of the evidence in its record row. Titles, locators, revisions and
hashes are copied verbatim from the record's `sources`. The cited sources are:

- `sim_python_backend`, `sim_fortran` and `upstream_constants` at the vendored
  revision;
- `downs_vogel_1993`;
- `bathelt_ricker_jelali_2015`.

The paper locators keep the record's (misnamed, F-11) file names. The `sha256` is
the identity.

**Semantic equivalence.** 0.2.0 has the same nodes, edges, bindings
(entity, runtime id, relation, attachment, quantity), expected runtime variables
and unbound declarations as 0.1.0. Only these differ:

- `fixture_version`;
- `source`;
- `review_record`;
- `sources`;
- `source_refs`;
- the binding method.

**Semantic attachment vs runtime source (Q2).** A ProcessGraph semantic attachment
identifies the engineering quantity/equipment relation exposed to the Agent. It does
not require the simulator to maintain a distinct physical state variable at that
exact graph node. For XMEAS(16):

- the Agent semantic attachment is the stripper pressure measurement
  (`stripper.pressure_measurement` on `stripper`);
- the simulator numerical source is `PTV`, the modeled vapor-zone pressure;
- this discrepancy is documented provenance (record row B-16, referenced through
  `review_record`), not a reason to rebind the semantic entity to
  `reactor_feed_mixer` or `stream_5`.

**`ACTUATES` semantics (Q3).** `ACTUATES` v0 represents functional control of the
associated process/utility path. It is not a geometric assertion about the exact
valve symbol location in a P&ID. This is why XMV(10)/XMV(11) remain attached to the
cooling-water inlet flow edges (`reactor_cooling_water_in`,
`condenser_cooling_water_in`) even though the figures draw the valve symbols on the
return side.

**Other recorded decisions carried forward unchanged.**

- Q4: `stream_number` holds only D&V process stream numbers 1–11. Figure utility
  line numbers (cooling-water lines 12/13) stay `null`.
- Q5: the stripper condensate return and the reboiler are not modeled in v0.
- Q7: the reviewed curated equivalent graph is an accepted source form. The official
  DEXPI XML is not a D0 requirement.

**Evaluator binding.** `tep-evaluator-disturbance-bindings` 0.2.0 has the same
mappings as 0.1.0. It is bound to the canonical hash of `tep-process-graph` 0.2.0,
and evaluator version N is bound to graph version N. It stays `EVALUATOR_ONLY`. Its
own mappings were outside the human review (boundary check only), so its
`review_status` remains `PENDING_HUMAN_REVIEW`.

**Loading.**

- `load_process_graph()` defaults to 0.2.0.
- `load_evaluator_disturbance_bindings(graph)` defaults to the packaged evaluator
  whose version matches `graph`.
- 0.1.0 remains packaged and pinned. Load it with an explicit path:
  `PACKAGED_GRAPH_FIXTURES["0.1.0"]` and `PACKAGED_EVALUATOR_FIXTURES["0.1.0"]` name
  the files.
- Later versions of a packaged fixture are named `<stem>_v<major>_<minor>_<patch>.json`.
  The 0.1.0 files keep their original `_v0.json` names.
