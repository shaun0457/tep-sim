# Roadmap — TEP Agent Lab

Lab implementation begins after focused Design Freeze re-review. Build the smallest RCA substrate first; HAZOP/Recovery/AutoResearch remain later research phases.

Canonical specs live in `docs/specs/`.

## Phase 0 — Reproducible benchmark shell

Specs:

- `benchmark-design-v0.md`
- `evaluation-v0.md`

Deliver:

- pinned environment/runtime/lab revisions;
- versioned scenario/fixture schema;
- DEVELOPMENT / RESEARCH / HIDDEN_EVAL partitions;
- deterministic Agent-visible projection path;
- append-only run/artifact manifest;
- leakage audit;
- deterministic re-scoring;
- identifiability/C0 pilot utilities.

Exit: a minimal fake run can be projected, traced, leakage-tested, and re-scored reproducibly.

## Phase 1 — RcaState / run log / Engineering Records

Branch: `feat/investigation-state-v0`

Specs:

- `investigation-state-v0.md`
- `engineering-records-v0.md`
- program `information-plane.md`

Deliver:

- RcaState implementing runtime TaskStateStore;
- one append-only run log + artifact layout;
- ObservationRecord and HypothesisEvidenceLink;
- deterministic `project_rca_state` ContextProjection;
- state revisions/deltas;
- InvestigationReport / DecisionRecord / ExperimentRecord;
- evaluator visibility protection.

Exit: one RCA investigation is reconstructable without chat transcript and records do not automatically leak into future context.

## Phase 2 — Rule / policy metadata

Branch: `feat/rule-registry-v0`  
Spec: `knowledge-rule-registry-v0.md`

Deliver only the metadata/authority needed for first RCA/policy tests:

```text
origin × validation × authority
```

Include:

- simulator/environment authoritative refs when consumed;
- explicit reviewed lab policy examples;
- advisory/planning relation examples;
- provenance/versioning/conflict representation.

Do not implement a full K3→K2/organizational-memory promotion engine yet.

Exit: literature/Agent/experiment claims cannot self-grant hard authority and lab intervention policy is explicit data, not prompt-only text.

## Phase 3 — Hypothesis / Prediction / Experiment

Branch: `feat/hypothesis-experiment-v0`  
Spec: `hypothesis-experiment-v0.md`

Deliver:

- Hypothesis;
- typed Prediction;
- HypothesisEvidenceLink;
- ExperimentProposal;
- frozen ExperimentRunSpec;
- canonical experiment dedup key;
- deterministic ExperimentResult/PredictionEvaluation;
- model interpretation as a separate object.

Exit: two plausible hypotheses can make distinct typed predictions and be tested by one traceable experiment.

## Phase 4 — Blind TEP tool surface

Branch: `feat/tool-surface-v0`  
Spec: `tool-surface-v0.md`

Deliver:

- current/history/metadata tools;
- topology measurements/actuators without canonical hidden candidate-cause bindings;
- snapshot/fork/rollout/capability tools;
- runtime ToolSpec/gate registration;
- lab request/result validator hooks;
- leakage tests;
- no MUTATE in blind RCA.

Exit: Agent can inspect/simulate TEP only through typed leakage-audited tools.

## Phase 5 — Minimal Tool Bridge

Branch: `feat/tool-bridge-v0`  
Spec: `tool-bridge-v0.md`

First implementation:

1. response-feature extraction / trajectory comparison;
2. cross-correlation / lag;
3. optional upstream TEP detector adapter for baseline studies.

Defer PCA/PLS/SALib/Optuna/Granger/MCP until a concrete experiment requires them.

Compound tools that run TEP must be SIMULATE and declare nested resource budgets.

Exit: tool/library versions and actual resource draws are fully traceable; arbitrary Agent Python/shell/import is unavailable.

## Phase 6 — Benchmark identifiability + C0

Branch: `exp/rca-benchmark-pilot-v0`

Specs:

- `benchmark-design-v0.md`
- `rca-v0.md`
- `evaluation-v0.md`

Deliver:

- reactor/cooling-related scenario family variants;
- strong C0 enumerate/simulate/match baseline;
- multiple seeds/timings/magnitudes;
- healthy/no-abnormal case;
- local candidate/topology leakage audit;
- data-informed difficulty labeling;
- at least one non-local/nontrivial case before MEDIUM/HARD claims.

Exit: the first Agent benchmark is neither trivially encoded nor physically indistinguishable.

## Phase 7 — Blind RCA capability study

Branch: `exp/rca-reactor-v0`

Use canonical capability conditions from `evaluation-v0.md`:

```text
C0 deterministic baseline
C1 static LLM
C2 + telemetry
C3 + topology
C4 + analysis bridge
C5 + counterfactual simulation
```

Later knowledge/research tools require their own study.

Exit: at least one blind case has complete RcaState, typed predictions/experiments/evidence, structured CausalClaim, InvestigationReport, and deterministic scoring.

## Phase 8 — Orchestration ablation

Branch: `exp/orchestration-ablation-v0`

Hold Agent-visible capability/tool policy fixed and compare:

```text
O0 one-shot
O1 ReAct
O2 fixed workflow
O3 Hybrid reference loop
O4 O3 + dependency-aware TOOL WorkBatch
O5 O4 + bounded SUBTASK work
```

Measure diagnosis, prediction/experiment quality, evidence efficiency, tool/rollout/tokens, work/subtask overhead, and stopping behavior.

A full mutable Dynamic DAG is not a required condition; it needs a separate future spec if studied.

## Phase 9 — Simulation-backed HAZOP

Branch: `exp/hazop-reactor-v0`  
Spec: `hazop-v0.md`

Start only after RCA contracts/tracing/evaluation are stable.

Keep supported/unsupported capability honesty and structured evidence refs.

## Phase 10 — Recovery planning

Branch: `exp/recovery-reactor-v0`  
Spec: `recovery-v0.md`

Start with forked strategy ranking/no-action baseline. SIMULATE never mutates reference state.

Enable reference MUTATE only after revision-bound validation/gate tests and explicit benchmark policy.

## Phase 11 — AutoProcessResearch

Branch: `exp/autoresearch-recovery-v0`  
Spec: `autoresearch-v0.md`

Prerequisites:

- stable recovery/search objective;
- Research/HIDDEN_EVAL split;
- optimizer/search Tool Bridge if needed;
- nested SIMULATE budget accounting;
- append-only experiment history.

AutoResearch is a separate task family, not an orchestration row.

## Phase 12 — Knowledge / organizational memory research

Only after clean no-KG/no-memory baselines:

- connect `manufacturing-kg-agent` read-only;
- extract literature candidates;
- implement evidence-driven validation/promotion workflow if needed;
- create LessonLearned/Runbook candidates from multiple records;
- compare no-history vs structured-record retrieval vs approved rule/runbook retrieval;
- ensure historical records do not contaminate hidden evaluation.

## Not on the first critical path

- full Dynamic DAG engine;
- LangGraph/MCP integration;
- P&ID OCR/model generation;
- 3D visualization;
- plant-wide formal HAZOP automation;
- learned cross-run memory;
- recursive swarms;
- production real-plant control authority.
