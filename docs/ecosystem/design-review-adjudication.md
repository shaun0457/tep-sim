# Design Review Adjudication — 2026-09-15

Status: review record (not a spec)

## Source review

Independent review basis: `review-report.md`, reviewing `architecture/hybrid-agent-runtime` at commit `9a1316d`.

The independent reviewer concluded **NOT READY FOR DESIGN FREEZE**, while explicitly allowing `tep-sim` A1–A4 to proceed independently.

This document records the program owner's adjudication. It is not a replacement for the owning specs; accepted findings are implemented by updating the canonical specs and ADRs.

## Adjudication policy

Each finding is classified as:

- **ACCEPT** — reviewer finding and proposed direction are adopted;
- **ACCEPT WITH MODIFICATION** — problem is accepted but the chosen solution differs;
- **REJECT** — finding is not adopted, with rationale;
- **DEFER** — valid concern but not required for v0 implementation;
- **OPEN_RESEARCH** — must be answered by pilot/ablation rather than architecture preference.

## Top findings

| Review finding | Decision | Adjudicated action |
|---|---|---|
| Verifier pre/post execution ambiguity | ACCEPT | Pre-execution checks belong to G0–G3 plus consumer `validate_request`; deterministic Verifier is post-execution `verify_result` over result/state/provenance/evidence. |
| Runtime Coordinator owns lab InvestigationState transitions without interface | ACCEPT | Add generic runtime `TaskStateStore` and `ContextProjection` contracts. Lab implements domain state; runtime never imports lab state types. |
| Dynamic DAG node semantics incomplete | ACCEPT WITH MODIFICATION | v0 replaces the full `TOOL/ANALYSIS/SIMULATION/SUBTASK/MERGE` DAG engine with a dependency-aware `WorkBatch` of `TOOL` or `SUBTASK` work items. Full model-revisable Dynamic DAG remains an orchestration research condition, not required v0 infrastructure. |
| Compound Tool Bridge calls bypass simulation budgets | ACCEPT | Add extensible budget dimensions and declared/max budget draw to tool contracts. Any bridge tool that internally executes simulator rollouts is `SIMULATE` and reserves rollout/horizon/trial budget before execution. |
| Free-text expected outcomes cannot support deterministic experiment scoring | ACCEPT | Add typed `Prediction` objects and use them for discrimination/falsification metrics. |
| TEP bindings may leak a trivial candidate-cause set | ACCEPT | Define C0 as deterministic enumerate/simulate/trajectory-match. Benchmark difficulty must be measured against C0; a case C0 solves trivially cannot be claimed as medium/hard investigation. Blind Agent tool policy does not expose canonical IDV answer labels by default. |
| K0–K4 mixes origin, validation maturity, and authority | ACCEPT | Canonical Rule schema becomes `origin × validation × authority`; K0–K4 remains documentation shorthand/presets only. Promotion changes validation; authority is assigned independently by policy. |
| Capability and orchestration ablation axes are confounded | ACCEPT | `evaluation-v0.md` is sole canonical matrix. Subagents belong to orchestration, not capability. Tool exposure policy is held fixed across orchestration comparisons unless exposure is the explicit independent variable. |
| Trace summaries are insufficient for leakage/replay | ACCEPT | Every model turn references the exact `ContextProjection` artifact plus prompt/template/model/sampling metadata. Summaries remain display aids only. |
| Semantic stopping claims an undefined information-gain estimator | ACCEPT | v0 stopping is Main Agent finish proposal plus deterministic structural verification. Formal information-gain stopping is OPEN_RESEARCH. |

## Missing contracts

| Contract | Decision | v0 action |
|---|---|---|
| `TaskStateStore` | ACCEPT | Add to runtime contract. |
| Observation/evidence lifecycle | ACCEPT | Every successful query/tool output yields an immutable observation/result record; evidence is an explicit link from a claim/hypothesis to an observed result. `Observation != Evidence`. |
| `Prediction` | ACCEPT | Add to hypothesis/experiment contract. |
| Root-cause answer vocabulary | ACCEPT WITH MODIFICATION | Do not expose a complete multiple-choice candidate list. Agent emits structured `CausalClaim`; evaluator represents hidden truth in the same structured fields and performs deterministic matching. `NO_ABNORMAL_CAUSE` is explicit. |
| Consumer budget dimensions | ACCEPT | Runtime Budget supports named extra dimensions; ToolSpec declares/reserves draw. |
| Dynamic DAG node semantics | ACCEPT WITH MODIFICATION | Replace v0 engine with `WorkBatch + depends_on`; full DAG semantics are deferred research. |
| Macro-stage enum | REJECT FOR V0 | Remove stage-dependent tool exposure from core v0. If later studied, define it as a separate exposure-policy ablation. |
| `ContextProjection` | ACCEPT | Runtime owns minimal generic schema; consumer constructs it, runtime enforces size/visibility metadata. |
| Knowledge-promotion five-object workflow | DEFER | Preserve architectural direction but do not implement in first RCA. Rule metadata must support future promotion. |
| Lab policy rule contract | ACCEPT | Represent policy rules explicitly with `origin=POLICY`, validation/authority metadata; do not hide limits only in prompts. |
| `RecoveryStrategy` DSL | DEFER | Define when recovery/AutoResearch implementation begins. |
| Engineering records | ACCEPT WITH MODIFICATION | v0 requires typed `InvestigationReport`, `DecisionRecord`, and `ExperimentRecord`. Lesson Learned / Runbook / Manual promotion is later research. Records are archive-only in v0 and are not automatically retrieved into future benchmark contexts. |
| Experiment dedup identity | ACCEPT | Canonical experiment key is based on content/state checksum + resolved interventions/config + horizon + seed policy + scorer/tool versions, not opaque snapshot IDs. |
| C0 deterministic baseline | ACCEPT | Mandatory baseline for first RCA family. |
| `InformationRef` owner | ACCEPT | Generic `InformationRef` belongs to runtime contracts; domain content ownership remains with producing repo. |
| Approval/revision binding | ACCEPT | Any enabled `MUTATE` request must bind validation to an expected reference-state revision/version. |

## Simplification decisions

### Dependency-aware work before full Dynamic DAG

v0 orchestration supports:

```text
Main Agent
  -> WorkBatch
       WorkItem(type=TOOL | SUBTASK, depends_on=[...])
  -> deterministic validation/topological scheduling
  -> post-execution verification
  -> Main Agent integrates results on the next turn
```

There is no separate `ANALYSIS` or `MERGE` node type in v0. Simulation is a `TOOL` work item whose registered side-effect class is `SIMULATE`.

Full dynamic graph revision/cancellation/replanning remains an evaluated architecture extension.

### Information Plane as logical boundary, not five storage systems

v0 may persist one append-only run log plus artifact files:

```text
runs/<run_id>/
  manifest.json
  events.jsonl
  artifacts/
  investigation-report.json
```

Evidence, experiment ledger, state deltas, decisions, and trace are typed views/indexes over that durable record. Separate services/stores are introduced only when a second consumer or scale requirement justifies them.

### LangGraph and MCP

Neither is a v0 core dependency.

- Public runtime contracts stay serializable/framework-neutral.
- LangGraph may be evaluated later if checkpoint/resume/interrupt requirements become concrete.
- MCP may be used later as one Tool Provider protocol for remote/external tools; it is never the authorization/safety layer.

## Rule authority decision

K0–K4 is no longer the canonical machine schema.

Canonical dimensions:

```text
origin      = SIMULATOR | FORMAL_DERIVATION | POLICY | LITERATURE | EXPERIMENT | AGENT
validation  = NONE | CORROBORATED | SIMULATION_VALIDATED | ROBUST_VALIDATED | REVIEWED
authority   = REFERENCE | ADVISORY | PLANNING | OPERATIONAL_PROPOSAL | HARD_GATE
```

Authority never increases because an Agent says a claim is important. Promotion evidence may increase `validation`; a separate deterministic policy maps `(origin, validation, scope)` to the maximum allowed authority.

## Evidence lifecycle decision

```text
ToolResult / simulator result
  -> immutable ObservationRecord

ObservationRecord
  -> explicit HypothesisEvidenceLink
  -> evidence for a claim
```

A queried observation that the Agent never links to a hypothesis remains an observation and can be scored as irrelevant/unused work.

Subagent output is renamed from `EvidenceBundle` to `SubtaskResult`; the parent/lab decides which referenced observations become evidence links.

## Evaluation decisions

`evaluation-v0.md` is the only canonical ablation source.

Capability axis excludes subagents. Orchestration axis contains subagent conditions. AutoProcessResearch is a separate task family, not simply another orchestration mode.

The same tool exposure policy must be used across orchestration modes being compared unless tool exposure itself is the independent variable.

C0 is a strong deterministic baseline, not a strawman:

```text
enumerate evaluator-known supported candidate causes
 -> instantiate/fork candidates
 -> compare trajectories/features
 -> choose best/no-abnormal result
```

If C0 solves a case cheaply/reliably, the result is evidence that an Agent is unnecessary for that case, not a reason to weaken C0.

## Engineering records and future organizational memory

v0 records engineering work but does not yet learn across incidents.

```text
Trace != Observation != Evidence != EngineeringRecord != Knowledge != Context
```

Minimum archive records:

- InvestigationReport;
- DecisionRecord;
- ExperimentRecord.

Future Lesson Learned / Runbook promotion must use evidence-driven validation and independent authority policy. Historical records are not automatically injected into benchmark prompts.

## Implementation release decision

### May start now

`tep-sim` A1–A4 remain independent of the review blockers:

- environment API;
- snapshot/fork/replay;
- DEXPI/process binding;
- capability/safety.

### Hold until canonical specs are aligned

- runtime contracts/gates/subagents;
- lab tool/state/evaluation implementation.

The hold is removed after the accepted review findings are reflected in canonical specs and a focused independent re-review reports no remaining BLOCKER and no unresolved implementation-defining MAJOR contradiction.

## Re-review contract

The independent re-review should not repeat the full architecture review. It should verify only:

1. each original BLOCKER is closed or explicitly downgraded with rationale;
2. each accepted MAJOR finding is reflected in its owning canonical spec;
3. no new contradiction was introduced by the fixes;
4. coding agents can implement runtime B1 and lab C1 without inventing product architecture;
5. deferred/open-research items are clearly marked as non-blocking.
