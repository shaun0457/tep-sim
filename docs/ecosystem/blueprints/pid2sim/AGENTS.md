# AGENTS.md

Rules for coding agents working on `pid2sim`.

## Product boundary

This repository transforms engineering representations into validated simulation-ready models. It is not a general LLM-agent runtime and not a TEP simulator implementation.

## Hard rules

1. Preserve provenance for every extracted, converted, inferred, assumed, and human-confirmed value.
2. Never silently invent missing engineering parameters.
3. Separate extraction errors from semantic/model-generation errors in tests and reports.
4. Keep DEXPI/library-specific objects behind adapters; the internal canonical graph is versioned independently.
5. Topology validation precedes simulation generation.
6. Generated models declare fidelity and assumptions.
7. A model compiling/running is not sufficient validation; compare behavior to reference data/scenarios.
8. Human review is a first-class workflow state, not an exceptional failure.
9. Agents/LLMs may propose mappings or retrieve evidence but may not convert uncertainty into unlabelled ground truth.
10. Keep raster/vector P&ID recognition optional until graph-to-simulation generation is validated.
11. Do not copy `tep-sim` physics. Use it as an external benchmark.
12. Do not add generic agent orchestration here; use a narrow helper interface or external runtime if reasoning is needed.

## Confidence/provenance states

Every nontrivial engineering datum should be representable as one of:

```text
SOURCE_CONFIRMED
DERIVED_DETERMINISTIC
MODEL_SUGGESTED
HUMAN_CONFIRMED
ASSUMED_EXPLICITLY
UNRESOLVED
```

Simulation compilation policy decides which states are acceptable for each fidelity level.

## Testing layers

Keep separate suites for:

- DEXPI/input parsing;
- graph normalization;
- topology validation;
- component mapping;
- parameter/enrichment validation;
- code/model generation;
- simulation execution;
- reference behavior comparison;
- drawing recognition (later).

A failure in one layer should not be hidden by later automatic repair.
