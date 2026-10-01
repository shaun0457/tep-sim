# A3 promotion handoff: human-verified ProcessGraph 0.2.0

Task: A3 promotion. Branch: `feat/a3-verified-fixture-v0.2.0`. Base: `main` `657e05e`.
Owning specification: `docs/specs/dexpi-binding-v0.md` ("Human-verified fixture 0.2.0").

This change publishes the fixture implied by the signed review record. It makes no
new semantic decision. The review package itself (`docs/reviews/`) is unchanged.

## Fixture versions

| Fixture | Version | Canonical sha256 | Status |
|---|---|---|---|
| `tep-process-graph` | 0.1.0 (`tep_process_graph_v0.json`) | `2b4adf9406674fd7c91f3ee48a6a96ef23992d682036059dcb6706e825d01f2b` | unchanged, `PENDING_HUMAN_REVIEW`, `CURATED_MAPPING` |
| `tep-evaluator-disturbance-bindings` | 0.1.0 (`tep_evaluator_disturbance_bindings_v0.json`) | `b497fdca4c4e436ba084bd120b989fe51e0b33a449164fe553be1f0c6b9b6a22` | unchanged, bound to graph 0.1.0 |
| `tep-process-graph` | **0.2.0** (`tep_process_graph_v0_2_0.json`) | `cc8ccc81e9f421238863457438465877850b19d9760740279e54a52468fe9a87` | `HUMAN_VERIFIED`, 53/53 `HUMAN_VERIFIED_MAPPING` |
| `tep-evaluator-disturbance-bindings` | **0.2.0** (`tep_evaluator_disturbance_bindings_v0_2_0.json`) | `25e4c60885d273c4abb3214411bf1d99a392ebe2d540f9d716624205b13a9cb5` | `EVALUATOR_ONLY`, bound to graph 0.2.0 |

All four are in `PINNED_FIXTURES`. The hashes were computed with
`canonical_sha256`, and the tests pin them.

## Signed review record reference

The fixture field `review_record` is typed as `tep_sim.ReviewRecordRef`:

- `review_package_id`: `a3-process-graph-human-verification`
- `review_package_version`: `0.2.0`
- `reviewer`: `chengting`
- `signed_on`: `2026-10-01`
- `locator`: `docs/reviews/a3-process-graph-binding-review-v0.json`
- `signed_record_sha256`: `f76210a9a59db110b50b57c147e5596e1f46d5fa7cd8fcb88ec1851484a00a7a`
  (the same hash `tests/test_a3_review_package.py` pins)

No review notes are copied into the fixture, and there is no free-text field.

## Decisions carried forward (no change to topology or bindings)

- **Q1, XMEAS(22).** `condenser_cooling.outlet_temperature` stays on
  `condenser_cooling_water_out`. The runtime name "Separator Cooling Water Outlet
  Temp" is not renamed.
- **Q2, XMEAS(16).** `stripper.pressure_measurement` stays on `stripper`. The value
  comes from the runtime `PTV` vapor-zone pressure. That is recorded in row B-16 of
  the referenced record, and the spec freezes the rule: a semantic attachment does
  not imply a distinct simulator state at that node.
- **Q3, XMV(10)/XMV(11).** They stay on `*_cooling_water_in`. The spec freezes the
  rule: `ACTUATES` v0 is functional control of the path, not a valve-glyph location.
- **Q4.** The cooling-water `stream_number` stays `null`.
- **Q5.** No condensate-return edge.
- **Q7.** The curated equivalent graph is the accepted source form.

A test proves 0.1.0 and 0.2.0 are identical once the provenance-only fields are
removed: version, source, `review_record`, sources, `source_refs` and binding
provenance. Nodes, edges, bindings, projections and warnings all match.

## F-10 provenance additions

The source entries are copied verbatim from the record's `sources`. Papers carry
the new typed `sha256` field. New citations:

- `sim_python_backend`
- `sim_fortran`
- `bathelt_ricker_jelali_2015`

`downs_vogel_1993` and `upstream_constants` are still cited, now with the record's
identities. Every node, edge and binding cites the `source_id`s of its own record
row's evidence. Every binding cites the vendored model source and Bathelt Fig. 3.

## Evaluator binding

Evaluator 0.2.0 has the same `DISTURBS` mappings and unbound declarations as 0.1.0.
Only `fixture_version`, `graph_fixture_version` and `graph_content_sha256` differ.
Evaluator version N is bound to graph version N, and each one rejects the other
graph version. Its mappings were not under human review (boundary only), so its
`review_status` stays `PENDING_HUMAN_REVIEW`. Whether D0 needs a human review of
evaluator mappings is a `tep-agent-lab` policy question. It was not decided here.

## Leakage checks (tested)

- The graph 0.2.0 file, all node projections and the `review_record` contain:
  - no `IDV(n)` spelling;
  - no upstream disturbance name;
  - no fault/disturbance/evaluator vocabulary.
- The bindings are `MEASURES`/`ACTUATES` over XMEAS/XMV only.
- The XMEAS(22) projection carries only the measurement fields.
- `tep_sim` re-exports nothing from `evaluator_bindings`, and no package module
  imports it (existing AST test).
- Loading the evaluator does not change any Agent projection.

## Loader behavior (public change)

- `load_process_graph()` now returns 0.2.0 (was 0.1.0).
- `load_evaluator_disturbance_bindings(graph)` defaults to the packaged evaluator
  whose version matches the graph: 0.2.0 for graph 0.2.0, 0.1.0 for graph 0.1.0.
- 0.1.0 stays packaged, pinned and loadable by explicit path:
  `PACKAGED_GRAPH_FIXTURES["0.1.0"]` and `PACKAGED_EVALUATOR_FIXTURES["0.1.0"]`.
- New public types: `ReviewRecordRef`, and `SourceRef` (now exported, with an
  optional `sha256`).
- `GraphProvenance.review_record` is new and defaults to `None`.
- New validation:
  - unknown or free-text keys in `sources` entries and in `review_record` are rejected;
  - `source.review_status` is required and must be `PENDING_HUMAN_REVIEW` or
    `HUMAN_VERIFIED`; before this change a missing value was accepted as `UNSPECIFIED`;
  - status, `review_record` and binding methods must be all verified or all not
    verified;
  - `signed_on` must be `YYYY-MM-DD`, and hashes must be exactly 64 lowercase hex
    characters;
  - the graph `source` object accepts only `kind`, `description` and
    `review_status`, and a binding `provenance` accepts only `method` and
    `source_refs`.

## Verification

Python 3.13 locally: 233 passed.

- 171 `tests/`, of which:
  - 15 new in `tests/test_a3_promotion.py`;
  - 17 new loader negatives.
- 62 pinned upstream tests.

CI runs Python 3.11 and 3.13.

## Downstream impact (action needed outside this repo)

- `tep-agent-lab` `ReferenceWorld` uses the `load_process_graph()` default. Its
  `tests/test_tool_surface.py:242` asserts `PENDING_HUMAN_REVIEW`. Once it moves to
  this `tep-sim`, it will see `HUMAN_VERIFIED` and the new graph hash, and its
  recorded world/tool-set versions change. That assertion must be updated in
  `tep-agent-lab`; this PR does not edit sibling repos.
- The `pyproject.toml` package version stays `0.1.0`. The downstream pin
  `tep-sim==0.1.0` therefore cannot tell the two defaults apart. The graph
  `content_sha256` in provenance does tell them apart. Bumping the package version
  is a release decision and is left open here.

## Review items not adopted

- A `HUMAN_VERIFIED` fixture is not required to be pinned. The loader-negative tests
  build unpinned copies of the verified graph. The spec says an unpinned
  `HUMAN_VERIFIED` claim is unverified; consumers should also check
  `provenance.pinned`.
- Evaluator 0.2.0 keeps the 0.1.0 `sources` entries unchanged. F-10 applied to the
  reviewed graph only.
- There is no single version table yet. A test checks that the
  `PACKAGED_*_FIXTURES` tables and the pins agree.

## Remaining (non-blocking)

- **F-11 PDF rename** (approved in Q8, separate PR). The 0.2.0 sources keep the
  record's current (misnamed) locators, and the PDF `sha256` is the identity. A
  rename must not edit the pinned 0.2.0 fixture. Instead, the rename PR must update
  the tests that resolve the locator, or publish a new version.
- D0 and P0 are not started here.

No `SPEC_CONFLICT`. The spec named no exact verified `review_status` value, so this
change freezes `HUMAN_VERIFIED` in the owning spec.
