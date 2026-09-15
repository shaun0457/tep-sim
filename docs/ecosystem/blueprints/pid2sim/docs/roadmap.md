# Roadmap

## Phase 0 — Define canonical graph and provenance

Before choosing AI models or a simulator backend, define:

- graph entities/edges;
- tag identity rules;
- source provenance;
- confidence/review states;
- versioning;
- validation finding format.

Build tiny hand-authored fixtures.

## Phase 1 — Machine-readable DEXPI ingestion

Implement one supported DEXPI input path first.

Goals:

- parse reference examples;
- normalize to canonical graph;
- preserve identifiers/attributes;
- validate topology;
- round-trip selected semantics in tests.

Add DEXPI 2.0 adapter separately when library/schema support is ready; do not force both versions through one opaque parser.

## Phase 2 — Simulation IR + simple executable backend

Create the simulation intermediate representation.

Implement a small component library sufficient for qualitative/low-fidelity flows:

- source/sink;
- valve;
- pump/compressor abstraction;
- tank/vessel;
- simple heat/cooling element;
- sensor/controller signal blocks.

Compile to a simple Python model first.

Exit criterion: clean graph fixtures generate runnable models and deterministic tests.

## Phase 3 — TEP round-trip benchmark

Create a curated TEP process graph at an explicitly chosen fidelity.

Generate the low-fidelity model and compare against `tep-sim` reference scenarios.

Track:

- topology match;
- compilation success;
- steady-state direction/plausibility;
- dynamic response direction/order;
- trajectory error for selected variables;
- required manual assumptions.

## Phase 4 — Modelica backend

Map the stable simulation IR to Modelica components/connectors.

Use reusable libraries where licensing permits and keep backend-specific parameter requirements explicit.

## Phase 5 — Engineering enrichment workflow

Add:

- missing-data report;
- component-model candidates;
- evidence retrieval hooks;
- explicit assumptions;
- human confirmation workflow;
- simulation-readiness score by fidelity level.

## Phase 6 — Vector P&ID ingestion

Before raster CV, exploit structured/vector information where available:

- text extraction;
- vector lines;
- symbol geometry;
- tags;
- connectivity reconstruction.

Feed output into the same canonical graph/validator.

## Phase 7 — Raster/legacy P&ID digitization

Add modular recognition stages:

- OCR/tag recognition;
- symbol detection;
- line extraction;
- ports/nozzles;
- connectivity reconstruction;
- off-page reference handling;
- confidence scoring;
- human correction UI.

Evaluate extraction separately from simulation generation.

## Phase 8 — Agent assistance

Only after deterministic pipeline stages exist, use an agent for bounded ambiguity resolution/evidence work:

- explain validation findings;
- retrieve candidate datasheets;
- rank model candidates;
- propose missing-data questions;
- propose validation experiments.

No silent engineering-fact invention.

## Phase 9 — Industrial pilot

Use a real but bounded process unit with accessible ground truth.

Measure:

- extraction accuracy;
- topology correction time;
- unresolved parameters;
- model generation time;
- human engineering time saved;
- behavior validation quality;
- provenance completeness.
