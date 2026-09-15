# Roadmap: TEP Process Sandbox

This roadmap deliberately stops at the environment boundary. Agent orchestration, HAZOP reasoning, and P&ID digitization live in separate repositories.

## Phase 0 — Lock the upstream simulator contract

**Goal:** establish a trustworthy baseline.

Deliverables:

- pin and record the upstream submodule commit;
- verify the pure-Python backend on the target Windows environment;
- document `step()`, XMEAS/XMV access, disturbance injection, controller modes, and shutdown behavior;
- generate canonical runtime variable metadata from upstream;
- add a registry consistency test;
- correct/deprecate literature-derived tables that disagree with runtime mapping.

Exit criteria:

```text
initialize -> step -> observe -> inject IDV -> reproduce with same seed
```

## Phase 1 — Stable environment adapter

**Goal:** external callers no longer depend directly on upstream internals.

Implement:

- `TEPEnvironment` facade;
- `EnvironmentConfig`;
- immutable `Observation`;
- typed `DisturbanceIntervention` and `MVIntervention`;
- explicit reset/step/rollout lifecycle;
- run ID and provenance metadata;
- explicit exception hierarchy.

Exit criteria:

- normal scripts use only the public adapter;
- invalid variable IDs/values fail before upstream mutation;
- a one-hour run can be stored and replayed from config.

## Phase 2 — Snapshot / fork / replay

**Goal:** make counterfactual experiments first-class.

Implement:

- `Snapshot` contract;
- environment cloning/forking;
- RNG/state handling;
- parent/child provenance;
- branch isolation tests;
- replay from stored run metadata when exact binary snapshotting is not available.

Exit criteria:

```text
snapshot S
-> fork A + fork B
-> different interventions
-> isolated rollouts
-> reproducible comparison
```

## Phase 3 — Capability registry

**Goal:** make simulation limits machine-readable.

Implement:

- supported disturbances;
- supported manipulated variables;
- supported high-level scenario semantics;
- unsupported consequence domains;
- versioned capability schema.

Exit criteria:

- a caller can query support before running an experiment;
- unsupported hazard requests fail explicitly;
- no generic fallback silently substitutes missing physics.

## Phase 4 — Scenario compiler

**Goal:** translate higher-level process scenarios into TEP interventions without an LLM.

Implement:

- canonical process-node registry;
- parameter/deviation vocabulary;
- `ProcessDeviation` schema;
- mapping rules from supported deviation -> intervention(s);
- ambiguity handling;
- scenario provenance.

Initial examples:

```text
reactor cooling loop + flow + LESS
reactor cooling-water inlet temperature + MORE
feed flow + NO/LESS
selected valve + STUCK
reaction kinetics + DRIFT
```

Exit criteria:

- at least five representative deviation classes compile deterministically;
- mappings have tests;
- impossible mappings return an explicit error.

## Phase 5 — Deterministic safety evaluator

**Goal:** expose process safety state as structured data.

Implement:

- current shutdown/limit state;
- safety margins;
- limit-crossing events;
- unsafe interval summaries;
- rollout-level `SafetyEvaluation`;
- clear declaration of unsupported consequence models.

Exit criteria:

- a scenario run produces a machine-readable safety summary;
- the result distinguishes `process unsafe/shutdown` from unmodeled leak/fire/explosion consequences.

## Phase 6 — HAZOP-friendly experiment primitives

**Goal:** make the environment convenient for external HAZOP agents without putting HAZOP reasoning here.

Implement:

- guide-word normalization;
- node/parameter enumeration;
- compile-only mode;
- batch scenario runner;
- branch comparison result;
- experiment budget controls (max branches/horizon) as environment safeguards.

Exit criteria:

An external caller can do:

```text
list process nodes
-> list parameters
-> submit deviation
-> check simulability
-> fork
-> rollout
-> evaluate safety
```

without touching simulator internals.

## Phase 7 — Visualization adapters

**Goal:** observe the playground without changing it.

Implement in increasing complexity:

1. simple process topology + live telemetry dashboard;
2. branch/rollout comparison view;
3. intervention/safety event timeline;
4. optional DEXPI/SVG process representation;
5. optional Blender/Omniverse view if it adds value.

UI remains read-only until a separately reviewed control interface is intentionally designed.

## Phase 8 — Benchmark and performance suite

**Goal:** make this environment useful as a research benchmark.

Create scenario packs for:

- healthy baseline;
- IDV disturbances;
- selected XMV interventions;
- HAZOP-compatible deviations;
- recovery/counterfactual comparisons.

Track:

- reproducibility;
- simulation speed;
- branch creation cost;
- storage cost;
- shutdown/safety outcomes;
- environment API compatibility.

## Not in this roadmap

The following are intentionally separate projects:

- agent runtime and dynamic subagents;
- agent token/context budgeting;
- HAZOP reasoning/evaluation methodology;
- RCA agent workflows;
- P&ID image/vector digitization;
- DEXPI graph generation from arbitrary drawings;
- generation of high-fidelity dynamic models from plant engineering data.

See [`ecosystem/README.md`](ecosystem/README.md) for ownership.
