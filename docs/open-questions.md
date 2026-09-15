# Open Questions — `tep-sim`

These items are intentionally unresolved. They should be closed through experiments/ADRs rather than hidden assumptions.

## OQ-1 — Snapshot fidelity

Can the vendored upstream simulator state be cloned exactly, including all internal integrator/controller/RNG state?

Options:

- exact in-memory/state serialization;
- deterministic replay from a recorded checkpoint/config;
- reconstructed approximation.

Decision criterion: measured branch reproducibility and implementation complexity.

## OQ-2 — Pinned DEXPI fixture

Which Tennessee Eastman machine-readable representation/version becomes the canonical v0 semantic fixture?

Need to verify:

- license/redistribution constraints;
- DEXPI schema/version;
- topology completeness;
- stable IDs/tags;
- compatibility with the chosen parser.

## OQ-3 — Graph representation

Use a lightweight internal adjacency model or adopt a graph library?

Default: start lightweight unless traversal/validation complexity justifies a dependency.

## OQ-4 — Process-deviation compiler scope

How many HAZOP guide-word mappings belong inside `tep-sim`?

Proposed boundary: only deterministic mappings from semantic deviations to simulator-supported interventions. Credibility/risk interpretation remains in `tep-agent-lab`.

## OQ-5 — Dense trace format

Parquet vs NPZ for primary numeric traces. JSONL remains suitable for events/provenance.

Decision criterion: easy inspection, deterministic tests, array shape fidelity, and downstream analysis ergonomics.

## OQ-6 — Nominal controller baseline

Which controller mode should be the canonical healthy/reference baseline for each experiment class?

This likely belongs in experiment fixtures rather than one global default.

## OQ-7 — Read-only visualization boundary

How much topology/dashboard support should live in `tep-sim` versus a downstream UI? Current default: only serialization/adapters needed to expose state and graph; no UI framework dependency.
