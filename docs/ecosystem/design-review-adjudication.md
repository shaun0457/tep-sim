# Design Review Adjudication — 2026-09-15

Status: review record (not a spec)

## Source review

Independent review:

`docs/ecosystem/reviews/2026-09-15-independent-spec-review.md`

Reviewed ref: `architecture/hybrid-agent-runtime` at commit `9a1316d`.

The independent reviewer concluded **NOT READY FOR DESIGN FREEZE**, while explicitly allowing `tep-sim` A1–A4 to proceed independently.

This document records the program owner's adjudication. It is not a replacement for owning specs/ADRs.

## Current closure status

The accepted findings have been propagated into canonical program/runtime/lab specs and entry documents.

A focused independent re-review was then performed at:

`docs/ecosystem/reviews/2026-09-15-focused-re-review.md`

That review returned **READY WITH CONDITIONS**:

- all original BLOCKERs closed;
- nine of ten original implementation-defining MAJOR findings closed;
- no new cross-document contradiction found;
- one remaining MAJOR-R1: the Main Agent state-proposal -> `StateDelta` path was unspecified.

The reviewer explicitly stated that closing R1 is sufficient for **READY FOR DESIGN FREEZE**.

R1 is now closed in the owning specs. Final release status:

- `tep-sim` A1–A4: **GO**;
- runtime B1–B5: **GO in dependency order**;
- lab C1–C5: **GO in dependency order**;
- D0 benchmark pilot: **GO once upstream dependencies exist**;
- later HAZOP/Recovery/AutoResearch remain ordered by their prerequisite milestones/specs.

See `design-freeze-record.md` for the final Phase 0 release record.

## Adjudication policy

- **ACCEPT** — finding/direction adopted;
- **ACCEPT WITH MODIFICATION** — problem accepted, chosen solution adjusted;
- **REJECT** — not adopted with rationale;
- **DEFER** — valid concern but not required for current v0 slice;
- **OPEN_RESEARCH** — answer through pilot/ablation rather than architecture preference.

## Top findings

| Review finding | Decision | Adjudicated action / current contract |
|---|---|---|
| Verifier pre/post ambiguity | ACCEPT | Pre-execution = G0–G3 + consumer `validate_request`; post-execution = deterministic `verify_result`. |
| Runtime Coordinator owns lab state without interface | ACCEPT | Runtime owns generic `TaskStateStore`/`ContextProjection`; lab implements with RcaState. |
| Dynamic DAG node semantics incomplete | ACCEPT WITH MODIFICATION | v0 full graph engine replaced by dependency-aware `WorkBatch` of `TOOL | SUBTASK` items. Rich Dynamic DAG is future research. |
| Compound Tool Bridge bypasses simulation budgets | ACCEPT | Runtime Budget supports extra dimensions; ToolSpec declares/reserves nested draw; simulator-running compound tools are SIMULATE. |
| Free-text expected outcomes block deterministic scoring | ACCEPT | Typed `Prediction`/PredictionEvaluation introduced. |
| TEP bindings may expose trivial candidate set | ACCEPT | Blind tools hide canonical candidate bindings by default; mandatory strong C0 enumerate/simulate/match baseline. |
| K0–K4 mixes origin/validation/authority | ACCEPT | Canonical Rule schema split to `origin × validation × authority`; K-labels are shorthand only. |
| Capability/orchestration ablations confounded | ACCEPT | `evaluation-v0.md` is sole matrix; subagents orchestration-only; tool exposure fixed across orchestration comparisons. |
| Trace summaries insufficient | ACCEPT | Every model turn references exact immutable ContextProjection + prompt/model/tool/config metadata. |
| Semantic stopping uses undefined information gain | ACCEPT | v0 = Agent finish proposal + deterministic structural checks; formal information-gain stopping is OPEN_RESEARCH. |

## Missing contracts disposition

| Contract | Decision | Current v0 action |
|---|---|---|
| `TaskStateStore` | ACCEPT | Defined in runtime-v0; RcaState implements it. |
| Observation/evidence lifecycle | ACCEPT | Successful agent-visible ToolResult -> immutable ObservationRecord; explicit HypothesisEvidenceLink makes evidence. |
| `Prediction` | ACCEPT | Defined in hypothesis/experiment contract. |
| Root-cause vocabulary | ACCEPT WITH MODIFICATION | Structured `CausalClaim`; evaluator truth uses same fields; full candidate list is not Agent-visible; `NO_ABNORMAL_CAUSE` explicit. |
| Consumer budget dimensions | ACCEPT | `Budget.extra_dimensions`; ToolSpec declared/max draw; actual usage reconciled. |
| Dynamic DAG node semantics | ACCEPT WITH MODIFICATION | WorkBatch replaces v0 full DAG engine. |
| Macro-stage enum | REJECT FOR V0 | Stage-dependent tool exposure removed; exposure can be separate later ablation. |
| `ContextProjection` | ACCEPT | Generic runtime schema; consumer constructs domain-relevant projection; runtime enforces generic visibility/ref/size. |
| Knowledge-promotion five-object workflow | DEFER | Rule metadata supports future promotion, but workflow implementation waits for a real knowledge study. |
| Lab policy rule contract | ACCEPT | Explicit POLICY origin/validation/authority metadata; not prompt-only. |
| `RecoveryStrategy` DSL/schema | DEFER | Required before recovery/AutoResearch implementation, not first RCA. |
| Engineering records | ACCEPT WITH MODIFICATION | v0 InvestigationReport/DecisionRecord/ExperimentRecord; lessons/runbooks/manual proposals later. |
| Experiment dedup identity | ACCEPT | Canonical content/config/seed/scorer-based experiment key. |
| C0 deterministic baseline | ACCEPT | Mandatory first-family baseline. |
| `InformationRef` owner | ACCEPT | Generic envelope owned by runtime; content remains producer-owned. |
| Approval/revision binding | ACCEPT | Any enabled MUTATE requires expected reference-state revision binding. |

## Simplification decisions

### Dependency-aware WorkBatch before full Dynamic DAG

```text
Main Agent
 -> WorkBatch
      WorkItem(kind=TOOL | SUBTASK, depends_on=[...])
 -> deterministic validation/topological scheduling
 -> execution + post-result verification
 -> next Main Agent turn integrates results
```

No v0 `ANALYSIS` or `MERGE` graph node types.

- deterministic analysis = TOOL;
- simulation = TOOL with `side_effect_class=SIMULATE`;
- open-ended integration/merge = next Main Agent turn;
- full mutable graph revision/cancellation/replanning = future research.

### Information Plane as logical boundary, not five services

Valid v0 persistence may be:

```text
runs/<run_id>/
  manifest.json
  events.jsonl
  artifacts/
  investigation-report.json
```

Evidence/experiment/state/decision/trace are typed views/records. Separate backing services require a demonstrated second-consumer/scale need.

### LangGraph and MCP

Neither is a v0 dependency or scheduled delivery.

- contracts stay serializable/framework-neutral;
- LangGraph may be considered for concrete durable checkpoint/resume/interrupt requirements;
- MCP may later be one external Tool Provider protocol, never the authorization layer.

## Rule authority decision

Canonical dimensions:

```text
origin      = SIMULATOR | FORMAL_DERIVATION | POLICY | LITERATURE | EXPERIMENT | AGENT
validation  = NONE | CORROBORATED | SIMULATION_VALIDATED | ROBUST_VALIDATED | REVIEWED
authority   = REFERENCE | ADVISORY | PLANNING | OPERATIONAL_PROPOSAL | HARD_GATE
```

K0–K4 is documentation shorthand only.

Promotion evidence may increase validation. Authority is assigned independently by explicit policy and cannot be self-promoted by model prose.

## Evidence lifecycle

```text
ToolResult / simulator result
  -> ObservationRecord

ObservationRecord
  -> explicit HypothesisEvidenceLink
  -> evidence for a claim/hypothesis
```

Unused/unlinked observations remain query/work records and can be scored as irrelevant/unused.

Subagent output is `SubtaskResult`, not EvidenceBundle; the parent/lab decides which observation refs become evidence links.

## Evaluation decisions

`evaluation-v0.md` is the sole canonical matrix.

### Capability

```text
C0 deterministic enumerate/simulate/match
C1 static LLM
C2 + telemetry
C3 + non-answer-leaking topology
C4 + analysis bridge
C5 + counterfactual simulation
C6/C7 later knowledge/research tools
```

### Orchestration

```text
O0 one-shot
O1 ReAct
O2 fixed workflow
O3 Hybrid reference loop
O4 O3 + dependency-aware TOOL WorkBatch
O5 O4 + bounded SUBTASK work
```

Subagents are not a capability row. Tool exposure is held fixed across orchestration comparisons. AutoProcessResearch is a separate later task family.

C0 remains deliberately strong. If C0 solves a case cheaply/reliably, that is evidence the Agent is unnecessary for that case.

## Engineering records / organizational memory

v0 writes but does not yet learn across incidents.

```text
Trace != Observation != Evidence != EngineeringRecord != Knowledge != Context
```

Minimum records:

- InvestigationReport;
- DecisionRecord;
- ExperimentRecord.

Historical records are not automatically injected into later benchmark contexts. Lesson Learned/Runbook/manual promotion is deferred to an explicit cross-incident knowledge study.

## Focused re-review MAJOR-R1 — CLOSED

### Gap identified by reviewer

The focused re-review found that hypothesis creation, evidence linking, ExperimentInterpretation, and WorkingExplanation updates were model-proposed state changes with no defined route into `StateDelta`/`TaskStateStore`.

It also identified two linked ambiguities:

- whether successful ToolResults are automatically registered as observations;
- how parallel WorkBatch result deltas avoid stale `base_revision` conflicts.

### Final contract

```text
ModelTurn
  context_projection_ref
  base_revision
  state_update?: ModelStateUpdateProposal
  action: NONE | TOOL_REQUEST | WORK_BATCH | FINISH_PROPOSAL
```

#### Model-proposed state update

```text
ModelStateUpdateProposal
 -> generic schema/projection revision validation
 -> consumer TaskStateStore validates legal operation/ref/visibility
 -> atomic apply_batch
 -> trace disposition
 -> action dispatch only if update succeeded
```

Rules:

- bound to the exact `ContextProjection.base_revision` seen by the model;
- all deltas in one proposal apply atomically or none apply;
- consumes one `max_steps` and zero `max_tool_calls`;
- cannot mutate runtime budget/policy/generic status/authority or external/reference state;
- stale/illegal proposal prevents same-turn ToolCall/WorkBatch dispatch.

#### Result ingestion

Every successful agent-visible ToolResult is automatically registered as an `ObservationRecord` by the lab deterministic ingestion path.

Observation registration does not create evidence. The Agent later proposes explicit:

```text
StateDelta(operation=ADD_EVIDENCE_LINK, ...)
```

`ExperimentInterpretation` fields map to explicit StateDelta operations (`ADD_EVIDENCE_LINK`, `UPDATE_HYPOTHESIS`, `ADD_OPEN_QUESTION`, `UPDATE_WORKING_EXPLANATION`, etc.).

For parallel WorkBatch results, deterministic ingestion batches are applied in a stable work-item order and each batch is bound to the **then-current** state revision immediately before application. Model-proposed deltas remain bound to the projection revision the model actually saw.

Owning specs:

- `blueprints/industrial-agent-runtime/docs/specs/runtime-v0.md`;
- `blueprints/industrial-agent-runtime/docs/specs/hybrid-orchestration-v0.md`;
- `blueprints/industrial-agent-runtime/docs/specs/deterministic-gates-v0.md`;
- `blueprints/tep-agent-lab/docs/specs/investigation-state-v0.md`;
- `blueprints/tep-agent-lab/docs/specs/hypothesis-experiment-v0.md`.

Decision Register: D-032.

## Implementation release decision

### GO

- `tep-sim` A1–A4;
- runtime B1–B5 in dependency order;
- lab C1–C5 in dependency order;
- D0 benchmark pilot once upstream dependencies exist.

### Deferred / OPEN_RESEARCH (non-blocking)

- full Dynamic DAG replanning/cancellation;
- LangGraph adapter;
- MCP provider;
- information-gain stopping;
- cross-incident learned memory;
- knowledge-promotion workflow;
- Lesson Learned/Runbook/manual promotion;
- exact subagent limits and benchmark scenario parameters;
- later HAZOP/Recovery/AutoResearch implementation beyond prerequisite milestones.

## Spec-conflict rule after freeze

If implementation reveals a contradiction or missing public contract, coding agents must emit `SPEC_CONFLICT`, preserve evidence, and reopen the owning spec/ADR rather than silently inventing architecture in code.
