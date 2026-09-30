# Cross-Repository Implementation Plan

This plan follows the independent design review, `design-review-adjudication.md`, focused re-review, and `design-freeze-record.md`.

**Phase 0 Design Freeze is complete.** `tep-sim`, `industrial-agent-runtime`, and `tep-agent-lab` implementation may proceed according to the dependency graph below.

Implementation evidence may still reopen a contract through `SPEC_CONFLICT`; coding agents must not silently invent product architecture.

## Phase 0 — Design Review Closure — COMPLETE

### Closed architecture/spec issues

- pre-execution request validation vs post-execution result verification;
- generic runtime `InformationRef`, `ContextProjection`, `TaskStateStore`;
- explicit `ModelTurn` + `ModelStateUpdateProposal` path for internal investigation-state updates;
- atomic revision-bound model state updates plus deterministic result-ingestion updates;
- automatic ObservationRecord registration for successful agent-visible ToolResults;
- dependency-aware `WorkBatch` replacing full Dynamic DAG as v0 infrastructure;
- extensible Budget dimensions and compound Tool resource accounting;
- `SubtaskResult` instead of runtime `EvidenceBundle`;
- Observation versus Evidence lifecycle;
- typed Prediction/ExperimentResult/Interpretation separation;
- Rule `origin × validation × authority` model;
- blind RCA candidate-binding restrictions;
- mandatory strong deterministic C0 baseline;
- Engineering Record archive contracts;
- canonical/deconfounded evaluation matrices;
- LangGraph/MCP removed from v0 critical path.

### Review evidence

- full review: `reviews/2026-09-15-independent-spec-review.md`;
- adjudication: `design-review-adjudication.md`;
- focused re-review: `reviews/2026-09-15-focused-re-review.md`;
- final closure: `design-freeze-record.md`.

The focused re-review closed all original BLOCKERs and all but one implementation-defining MAJOR. The remaining R1 state-update path has now been specified in the owning runtime/lab contracts, satisfying the reviewer's stated condition for READY FOR DESIGN FREEZE.

---

# Phase A — `tep-sim`: trusted world — GO

## A1 — Environment adapter

Branch: `feat/environment-api-v0`  
Spec: `docs/specs/environment-api-v0.md`

Deliver:

- `TEPEnvironment`;
- canonical config/observation/intervention/result contracts;
- provenance;
- deterministic baseline tests.

## A2 — Snapshot / fork / replay

Branch: `feat/snapshot-fork-v0`  
Spec: `docs/specs/snapshot-fork-replay-v0.md`

Deliver:

- snapshot-fidelity investigation;
- branch isolation;
- replay/provenance;
- explicit fidelity status.

## A3 — DEXPI / ProcessGraph binding

Branch: `feat/dexpi-binding-v0`  
Spec: `docs/specs/dexpi-binding-v0.md`

Deliver:

- pinned TEP semantic fixture;
- normalized ProcessGraph;
- topology queries;
- canonical variable/binding registry;
- validation tests.

## A4 — Capability / hard environment truth

Branch: `feat/capability-safety-v0`  
Spec: `docs/specs/safety-capability-v0.md`

Deliver:

- capability registry;
- minimal deterministic scenario compilation;
- environment/safety evaluation;
- explicit unsupported-physics behavior.

---

# Phase B — `industrial-agent-runtime`: generic control plane — GO

## B1 — Core contracts / reference loop

Branch: `feat/contracts-runtime-v0`

Specs:

- `docs/specs/runtime-v0.md`
- `docs/specs/hybrid-orchestration-v0.md`

Deliver:

- InformationRef;
- Task;
- Budget with extra dimensions;
- ToolSpec/ToolCallRequest/ToolResult;
- TaskStatus/StateDelta/ModelStateUpdateProposal/ModelTurn;
- ContextProjection/TaskStateStore `apply_batch` protocol;
- WorkBatch/WorkItem;
- RuntimeResult/TraceEvent;
- deterministic fake provider;
- reference runtime loop/dispatcher;
- exact model-turn projection/state-update tracing.

Required semantics:

```text
ContextProjection
 -> ModelTurn
      -> optional ModelStateUpdateProposal
           -> atomic TaskStateStore.apply_batch
      -> one action: NONE | TOOL_REQUEST | WORK_BATCH | FINISH_PROPOSAL
```

A rejected/stale model state update prevents same-turn execution dispatch.

Exit:

- fake-provider tasks run without domain imports;
- fake provider emits every action variant and state-update proposal;
- consumer fake TaskStateStore works without runtime knowing its state class;
- multi-delta state updates are atomic/revision checked;
- dependency-aware TOOL WorkBatch executes deterministically;
- parallel result-ingestion updates bind current revision and do not false-fail stale;
- no LangGraph/MCP dependency required.

## B2 — Deterministic pre-execution gates

Branch: `feat/deterministic-gates-v0`  
Spec: `docs/specs/deterministic-gates-v0.md`

Deliver:

- G0 schema;
- G1 allowlist/authority;
- G2 standard + extra-dimensional resource reservation;
- G3 side-effect policy;
- consumer `validate_request` hook;
- revision-bound MUTATE validation contract;
- GateDecision tracing.

Internal ModelStateUpdateProposal processing remains a separate TaskStateStore path and consumes no tool-call budget.

## B3 — Post-execution verification / deterministic ingestion

May be implemented in B1/B2 modules or a small dedicated module; do not invent another agent/service.

Deliver deterministic:

- result/ref/provenance checks;
- actual-budget reconciliation;
- consumer `verify_result` hook;
- deterministic result-ingestion delta hook/order;
- final-output structural readiness checks.

## B4 — Ephemeral subagents

Branch: `feat/subagents-v0`  
Spec: `docs/specs/subagents-v0.md`

Deliver:

- bounded child tasks;
- cumulative per-task child budget;
- scoped context/tools;
- `SubtaskResult`;
- no child MUTATE;
- no nested SUBTASK bypass at depth limit;
- parent-child trace.

## B5 — First real provider

Branch: `feat/provider-adapter-v0`

Add one provider only after fake-provider contracts pass. Provider SDK types stay behind the internal model interface.

## Explicitly not scheduled in B v0

- LangGraph adapter;
- MCP runtime dependency;
- general mutable Dynamic DAG engine.

These require concrete later evidence/requirements.

---

# Phase C — `tep-agent-lab`: first RCA information/investigation plane — GO

## C1 — RCA state / run log / projection

Branch: `feat/investigation-state-v0`

Specs:

- `docs/specs/investigation-state-v0.md`
- `docs/specs/engineering-records-v0.md`
- program `information-plane.md`

Deliver:

- RcaState implementing runtime TaskStateStore;
- allowlisted RCA StateDelta operations;
- atomic `apply_batch` with revision/visibility/domain validation;
- append-only per-run events/log/artifacts;
- automatic ObservationRecord registration for every successful agent-visible ToolResult;
- explicit HypothesisEvidenceLink lifecycle;
- deterministic result-ingestion ordering for parallel WorkBatch results;
- deterministic `project_rca_state` ContextProjection;
- InvestigationReport / DecisionRecord / ExperimentRecord;
- ground-truth visibility tests.

Do not build five physical information databases/services.

## C2 — Rule/policy metadata

Branch: `feat/rule-registry-v0`  
Spec: `docs/specs/knowledge-rule-registry-v0.md`

Deliver a small representative registry using:

```text
origin × validation × authority
```

Include:

- simulator/environment refs where consumed;
- explicit reviewed lab policy rules;
- advisory test examples;
- provenance/versioning.

Do not implement the full cross-incident promotion engine yet.

## C3 — Hypothesis / Prediction / Experiment

Branch: `feat/hypothesis-experiment-v0`  
Spec: `docs/specs/hypothesis-experiment-v0.md`

Deliver:

- Hypothesis;
- typed Prediction;
- explicit evidence links as StateDelta operations;
- ExperimentProposal/RunSpec/Result/Interpretation;
- Interpretation -> StateDelta mapping;
- canonical experiment dedup key;
- deterministic prediction feature evaluation where supported.

## C4 — TEP tool surface

Branch: `feat/tool-surface-v0`  
Spec: `docs/specs/tool-surface-v0.md`

Initial blind RCA surface:

- observations/history;
- variable/process metadata;
- topology measurements/actuators without canonical hidden cause list;
- snapshot/fork/rollout/capability;
- no MUTATE;
- no default canonical `get_related_disturbances` answer leakage.

## C5 — Minimal Tool Bridge

Branch: `feat/tool-bridge-v0`  
Spec: `docs/specs/tool-bridge-v0.md`

First implementation only:

1. response-feature extraction/trajectory comparison;
2. cross-correlation/lag;
3. optional existing TEP detector baseline if required.

Defer SALib/Optuna/PCA/PLS/Granger until a concrete experiment requires them.

---

# Phase D — first RCA research

## D0 — Benchmark/identifiability/C0 pilot

Branch: `exp/rca-benchmark-pilot-v0`

Specs:

- `docs/specs/benchmark-design-v0.md`
- `docs/specs/evaluation-v0.md`
- `docs/specs/rca-v0.md`

Deliver before Agent superiority claims:

- scenario variants;
- strong C0 enumerate/simulate/match baseline;
- healthy/no-abnormal case;
- candidate/topology leakage audit;
- data-informed difficulty labels;
- at least one non-local/nontrivial case for medium/hard investigation claims.

## D1 — Blind RCA capability ladder

Branch: `exp/rca-reactor-v0`

Use the canonical capability axis in `evaluation-v0.md`.

Start with C1–C5 as infrastructure becomes available. Do not add subagents as a capability row.

## D2 — Orchestration ablation

Branch: `exp/orchestration-ablation-v0`

Canonical conditions:

```text
O0 one-shot
O1 ReAct
O2 fixed workflow
O3 Hybrid reference loop
O4 O3 + dependency-aware TOOL WorkBatch
O5 O4 + bounded SUBTASK work
```

Use identical Agent-visible capability/tool policy across O1–O5 unless tool exposure is explicitly being studied.

The value of WorkBatch/subagents is measured rather than assumed.

---

# Phase E — later task families

Only after RCA environment/tracing/evaluation contracts are stable.

## E1 — Simulation-backed HAZOP

Branch: `exp/hazop-reactor-v0`

Use capability honesty and evidence/provenance contracts. Do not claim formal plant HAZOP completion.

## E2 — Recovery planning

Branch: `exp/recovery-reactor-v0`

Rank forked strategies first. Reference MUTATE remains disabled until state-revision-bound validation/gates are proven.

## E3 — AutoProcessResearch

Branch: `exp/autoresearch-recovery-v0`

Only after deterministic recovery/scoring/search-space contracts exist.

AutoProcessResearch remains a separate research task family, not an orchestration-ablation condition.

Numeric search may later add Optuna/SALib-style bridge tools with SIMULATE nested-budget accounting.

---

# Phase F — optional knowledge / organizational memory

After clean no-KG/no-memory baselines:

- connect `manufacturing-kg-agent` through read-only evidence adapters;
- validate literature/document candidates;
- implement KnowledgePromotionProposal/ValidationPlan/ValidationResult/PromotionDecision if needed;
- study structured Engineering Record retrieval across incidents;
- compare no-history vs record retrieval vs approved rule/runbook retrieval;
- add subsystem/fault families;
- detector-triggered start;
- 2D investigation UI if useful.

Lesson Learned/Runbook/manual promotion must be evaluated/authority-governed rather than automatically generated from one incident.

Still out of scope: generic P&ID OCR/model generation and 3D reconstruction.

---

# Parallel development after freeze

Use `development-agent-orchestration.md` and `development-workflow.md`.

A coding agent receives:

```text
repo/branch
canonical spec
owned files/modules
dependencies
acceptance tests
handoff contract
```

On spec conflict it reports `SPEC_CONFLICT`; it does not silently redesign architecture.

## Dependency graph

```text
tep-sim A1 -> A2 -> A3/A4

runtime B1 -> B2/B3 -> B4 -> B5 provider

lab C1 + C2 + C3
       \   |   /
        C4/C5
          |
         D0 benchmark pilot
          |
         D1 RCA capability
          |
         D2 orchestration
          |
      E1/E2 later tasks
          |
      E3 AutoResearch
          |
      F knowledge/memory studies
```

Independent branches may run in parallel when their upstream frozen contracts are available and file/module ownership does not overlap. Completion race does not change integration order.
