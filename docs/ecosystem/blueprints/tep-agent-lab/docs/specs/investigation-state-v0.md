# Investigation State v0

Status: accepted direction / v0 contract proposal  
Owner repo: `tep-agent-lab`

## Goal

Externalize investigation state from chat transcripts so the Main Agent, Coordinator, Dynamic DAG, tools, evaluator, and future resume/checkpoint logic operate on one typed source of truth.

## Core contract

```text
InvestigationState
  investigation_id
  case_id?
  goal
  mode
  status
  incident_ref?
  current_time_ref?
  hypothesis_refs[]
  evidence_refs[]
  open_questions[]
  planned_experiment_refs[]
  completed_experiment_refs[]
  active_plan_ref?
  delegated_task_refs[]
  current_best_explanation?
  uncertainty_summary?
  safety_state_ref?
  budget_state
  artifact_refs[]
  conclusion_ref?
  revision
```

## Modes

v0 supports:

```text
RCA
HAZOP
RECOVERY
AUTORESEARCH
```

The same orchestration mechanics may be reused while mode-specific schemas/tools/policies remain explicit.

## Status

```text
INITIALIZING
INVESTIGATING
WAITING_FOR_WORK
VERIFYING
READY_TO_CONCLUDE
CONCLUDED
BLOCKED
FAILED
BUDGET_EXHAUSTED
CANCELLED
```

Transitions are Coordinator-controlled, not authored directly by model prose.

## Hypothesis state

`hypothesis_refs` point to first-class `Hypothesis` objects. State SHOULD provide compact summaries for active hypotheses, but full evidence relationships live in the hypothesis/evidence objects.

## Evidence state

Evidence is append-only by reference. A model may request that evidence be attached to a hypothesis, but existing evidence artifacts are never rewritten by the model.

Each evidence ref has visibility and provenance.

## Open questions

Open questions are typed investigation gaps, conceptually:

```text
question_id
question
why_it_matters
related_hypotheses[]
resolvable_by: TOOL | EXPERIMENT | SUBTASK | EXTERNAL_KNOWLEDGE | HUMAN
priority
status
```

This gives the Main Agent an explicit representation of uncertainty rather than relying on a narrative scratchpad.

## Experiment state

Planned and completed experiments are referenced separately so the Coordinator can prevent duplicate execution and the evaluator can measure planning/selection quality.

## Delegation state

Each delegated task ref records parent relation, purpose, context slice, budget, status, and result ref. Completed subagent transcripts are not inserted into state; only compact structured results/evidence refs are retained.

## Best explanation

`current_best_explanation` is a structured working conclusion, not the final answer. It may contain:

```text
leading_hypothesis_ref
confidence_or_rank
key_evidence_refs
key_counterevidence_refs
remaining_uncertainties
last_updated_revision
```

It is allowed to change as evidence arrives.

## Budget state

State records remaining/used limits for:

- model turns;
- tool calls;
- subagents;
- dynamic plan revisions;
- simulation rollouts;
- total simulated horizon;
- optional token/cost/wall-time limits.

The Coordinator is authoritative for budget accounting.

## Revision semantics

Every accepted state update increments `revision`. Important requests may carry an expected revision to avoid stale updates.

State updates are events/deltas rather than free replacement of the entire object.

Conceptually:

```text
StateDelta
  base_revision
  operation
  target_ref/field
  value/ref
  producer
  reason_ref?
```

## Model-facing projection

The Main Agent does not necessarily receive the entire state. The Context Broker creates a bounded projection containing:

- goal/mode/status;
- active hypotheses;
- recent/high-value evidence;
- unresolved questions;
- active/completed experiment summaries;
- delegated work summary;
- budgets;
- relevant safety/context refs.

Older/raw artifacts stay addressable through tools.

## Stop readiness

The state supports semantic stopping checks. `READY_TO_CONCLUDE` may be proposed when:

- a mode-specific minimum result schema can be produced;
- no critical unresolved verifier failure exists;
- evidence requirements are satisfied or uncertainty is explicitly declared;
- remaining budget is low or expected information gain from further allowed work is below configured policy;
- no required active work remains.

The deterministic verifier checks structural conditions; the Main Agent supplies the substantive judgment that evidence is sufficient.

## Ground-truth isolation

Evaluator-only truth must never appear in `InvestigationState` agent-visible fields. If the evaluation harness stores linked truth, it uses evaluator-only refs outside the agent projection.

## Persistence

v0 requires durable per-run serialization sufficient to replay/audit the investigation. Cross-incident learned memory remains out of scope.

## Invariants

- Chat transcript is not canonical state.
- Hidden ground truth is not agent-visible state.
- Evidence/experiment refs preserve provenance.
- Coordinator, not model prose, owns status/budget/revision transitions.
- Subagent full transcripts are not merged into parent state.
- Every final conclusion is reproducibly linked to the state revision and evidence refs used.

## Acceptance tests

1. Initialize an RCA state from a blind fixture without hidden truth leakage.
2. Add two hypotheses and evidence through validated deltas.
3. Spawn/complete a subtask and retain only its structured result refs.
4. Plan/execute an experiment and move refs from planned to completed.
5. Reject a stale state delta using revision checking.
6. Materialize a bounded Main Agent projection without full history/artifacts.
7. Reconstruct final state from saved deltas/trace deterministically.
