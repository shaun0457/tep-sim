# Investigation State v0

Status: proposal  
Owner repo: `tep-agent-lab`  
Implements: `industrial-agent-runtime` `TaskStateStore`

## Goal

Define the first domain state used by the TEP lab without making the generic runtime understand TEP/RCA fields.

v0 implements **RCA state first**. HAZOP, Recovery, and AutoResearch may reuse a small generic shell later but receive their own domain-state schemas when implemented.

## Generic/runtime boundary

`industrial-agent-runtime` owns:

```text
TaskStatus
StateDelta envelope
ContextProjection
TaskStateStore protocol
```

`tep-agent-lab` owns the RCA-specific fields and validates legal field/path updates.

The runtime Coordinator calls the interface; it never imports `RcaState`.

## `RcaState`

```text
RcaState
  investigation_id
  case_id?
  goal
  incident_ref
  current_time_ref?

  hypothesis_refs[]
  observation_refs[]
  evidence_link_refs[]
  open_questions[]

  planned_experiment_refs[]
  completed_experiment_refs[]
  delegated_task_refs[]

  current_best_explanation?
  uncertainty_summary?
  safety_state_ref?

  artifact_refs[]
  conclusion_ref?

  generic_status: TaskStatus
  revision
```

Budget authority remains in generic runtime `Budget`/budget accounting. The lab may expose a compact budget summary in the projection but does not maintain a competing authoritative budget counter.

## Generic status

Use runtime status only:

```text
RUNNING
WAITING
READY
DONE
FAILED
EXHAUSTED
CANCELLED
```

RCA-specific investigation phase, if useful for reporting, is metadata rather than a second authoritative status machine.

## Observation versus evidence

The state explicitly separates what the system observed from what the Agent uses as evidence.

### `ObservationRecord`

Every successful relevant tool/simulator/analysis result may be registered as an immutable observation/result reference:

```text
ObservationRecord
  observation_id
  producer_request_ref
  tool_or_service_ref
  summary
  artifact_refs[]
  information_refs[]
  provenance
  visibility
  created_at
```

An observation is not automatically supporting evidence.

### `HypothesisEvidenceLink`

A model/application may propose an explicit relation from an existing visible observation to a hypothesis/claim:

```text
hypothesis_ref
observation_ref
relation: SUPPORT | CONTRADICT | CONTEXT | NEUTRAL
strength?
reason_summary
producer
```

The deterministic verifier checks ref existence/visibility/provenance. It does not decide open-ended scientific truth.

This separation enables distinct metrics for irrelevant queries, unused observations, and evidence quality.

## Hypothesis state

`hypothesis_refs` point to typed `Hypothesis` objects defined in `hypothesis-experiment-v0.md`.

State may project compact active summaries but does not duplicate full hypothesis history.

## Open questions

```text
OpenQuestion
  question_id
  question
  why_it_matters
  related_hypotheses[]
  resolvable_by: TOOL | EXPERIMENT | SUBTASK | EXTERNAL_KNOWLEDGE | HUMAN
  priority
  status
```

Questions are useful working state, but evaluation must not reward the Agent for creating trivial questions merely to close them.

## Experiment state

Planned and completed experiments are referenced separately.

Exact duplicate detection is a lab pre-execution policy over canonical experiment keys; it is not a generic runtime Coordinator responsibility.

## Delegation state

Each `delegated_task_ref` points to runtime subtask trace/result metadata. Full subagent transcripts are not copied into RCA state.

## Working explanation

```text
WorkingExplanation
  leading_hypothesis_ref?
  current_rank_or_score_summary?
  key_evidence_link_refs[]
  key_counterevidence_link_refs[]
  remaining_uncertainties[]
  last_updated_revision
```

It is working state, not final truth.

## `TaskStateStore` implementation

The lab implements:

```text
revision() -> Revision
status() -> TaskStatus
project(policy) -> ContextProjection
apply(delta, expected_revision) -> NewRevision
```

### `apply`

Lab validates:

- target path/field exists and is legal;
- ref visibility/ownership is allowed;
- append-only records are not silently rewritten;
- transition does not expose evaluator-only truth;
- expected revision matches current revision;
- domain invariants for RCA state remain valid.

Every accepted update increments revision and is retained as an append-only event/delta.

## Model-facing projection

The lab owns a deterministic/reference-aware projection function:

```text
project_rca_state(state, policy) -> ContextProjection
```

The projection may include:

- goal/incident summary;
- active hypotheses;
- selected recent/high-value observations/evidence links;
- unresolved high-priority questions;
- planned/completed experiment summaries;
- delegated-work summary;
- remaining runtime budget summary;
- relevant process/safety refs.

The generic runtime validates projection metadata/visibility/token limits but does not choose what chemical/process evidence is relevant.

Every model turn persists the exact immutable ContextProjection ref.

## v0 stopping semantics

There is no formal information-gain estimator in v0.

Stopping is:

```text
Main Agent proposes final result / READY
 -> deterministic structural verification
 -> DONE or return structured deficiency
```

Minimum deterministic readiness checks may include:

- output schema can be populated;
- no failed mandatory work remains active;
- no critical unresolved verifier error exists;
- selected cause/conclusion references valid visible evidence/observations;
- required experiment/result refs exist when the benchmark requires them;
- uncertainty/remaining questions are represented when conclusion is non-certain.

Whether the evidence is substantively sufficient is part of the Agent capability being evaluated. Formal expected-information-gain stopping is OPEN_RESEARCH and requires an explicit belief/probability model before implementation.

## Ground-truth isolation

Evaluator truth is stored outside agent-visible RcaState. The lab projection function and runtime visibility checks both fail closed on `EVALUATOR` refs.

## Persistence

v0 requires durable per-run state reconstruction from append-only events plus artifacts.

Cross-incident retrieval/learned memory is out of scope for the first RCA benchmark.

## Invariants

- Conversation transcript is not canonical state.
- Runtime never imports RcaState.
- Generic runtime budget counters remain authoritative.
- Observation is not automatically Evidence.
- Hidden truth is not agent-visible state.
- State updates are revision checked.
- Subagent transcripts are not merged into parent state.
- Final report is linked to the exact state revision and evidence/experiment refs used.

## Acceptance tests

1. Initialize blind RCA state without hidden truth leakage.
2. Apply validated StateDelta through TaskStateStore without runtime importing RcaState.
3. Reject stale StateDelta by expected revision.
4. Register an observation and verify it does not become evidence until a HypothesisEvidenceLink is added.
5. Add two hypotheses/evidence links and preserve append-only provenance.
6. Complete a subtask and retain only SubtaskResult/ref metadata.
7. Plan/execute an experiment and move refs from planned to completed through legal deltas.
8. Materialize an exact bounded ContextProjection with no EVALUATOR refs.
9. Reconstruct final RcaState from saved events deterministically.
10. Reject final readiness when required evidence/artifact refs are missing.
