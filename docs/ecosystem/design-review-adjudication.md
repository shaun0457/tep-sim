# Design Review Adjudication — 2026-09-15

Status: review record (not a spec)

## Source review

Independent review:

`docs/ecosystem/reviews/2026-09-15-independent-spec-review.md`

Reviewed ref: `architecture/hybrid-agent-runtime` at commit `9a1316d`.

The independent reviewer concluded **NOT READY FOR DESIGN FREEZE**, while explicitly allowing `tep-sim` A1–A4 to proceed independently.

This document records the program owner's adjudication. It is not a replacement for owning specs/ADRs.

## Current closure status

The accepted findings below have now been propagated into the canonical program/runtime/lab specs and entry documents on `architecture/hybrid-agent-runtime`.

Current release policy:

- `tep-sim` A1–A4: **GO** independently;
- runtime/lab implementation: **HOLD pending focused independent re-review**;
- the re-review should check blocker/major closure and contradictions, not redesign the full program from scratch.

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
| Observation/evidence lifecycle | ACCEPT | Tool/simulator result -> immutable ObservationRecord; explicit HypothesisEvidenceLink makes evidence. |
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

## Implementation release decision

### GO now

`tep-sim` A1–A4:

- environment API;
- snapshot/fork/replay;
- DEXPI/process binding;
- capability/safety.

### HOLD pending focused re-review

- runtime implementation;
- lab implementation.

The canonical alignment work itself is complete enough to request the focused re-review; the hold is removed only if that review finds no remaining BLOCKER or unresolved implementation-defining MAJOR contradiction.

## Focused re-review contract

The independent reviewer should verify only:

1. each original BLOCKER is closed or explicitly downgraded with defensible rationale;
2. each accepted implementation-defining MAJOR finding appears in the owning canonical spec;
3. no new cross-document/cross-repo contradiction was introduced;
4. runtime B1 and lab C1 could be implemented without inventing product architecture;
5. deferred/open-research items are clearly non-blocking;
6. old terms (`EvidenceBundle`, full-DAG v0 requirement, K0–K4 as canonical schema, scheduled LangGraph adapter, SIMULATE reference mutation) do not remain authoritative in current entry/canonical docs.
