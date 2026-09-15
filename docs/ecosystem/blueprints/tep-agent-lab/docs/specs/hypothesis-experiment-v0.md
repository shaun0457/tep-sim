# Hypothesis and Experiment Contracts v0

Status: accepted direction / v0 contract proposal  
Owner repo: `tep-agent-lab`

## Goal

Represent hypotheses and experiments as first-class typed objects so RCA, Dynamic DAG planning, AutoResearch, evidence integration, and evaluation do not depend on free-form chat history.

## `Hypothesis`

```text
Hypothesis
  hypothesis_id
  investigation_id
  claim
  hypothesis_type
  scope_refs[]
  status
  prior_weight?
  current_score_or_rank?
  supporting_evidence_refs[]
  contradicting_evidence_refs[]
  experiment_refs[]
  assumptions[]
  falsification_conditions[]
  created_by
  created_at
  last_updated_revision
```

### Hypothesis status

```text
PROPOSED
ACTIVE
SUPPORTED
WEAKENED
REJECTED
UNTESTABLE
UNRESOLVED
```

Status transitions are recorded; old state is not silently rewritten.

### Hypothesis types

Initial examples:

```text
ROOT_CAUSE
MECHANISM
PROCESS_RELATION
RECOVERY_EFFECT
HAZOP_CAUSE
RESEARCH_IDEA
```

Types are semantic metadata, not fixed agent roles.

## Evidence attachment

An evidence item may support, contradict, or remain neutral to a hypothesis.

```text
HypothesisEvidenceLink
  hypothesis_ref
  evidence_ref
  relation: SUPPORT | CONTRADICT | CONTEXT | NEUTRAL
  strength?
  reason_summary
  producer
```

The model may propose links; deterministic verification checks that referenced evidence exists and visibility/provenance is valid.

## `ExperimentProposal`

```text
ExperimentProposal
  experiment_id
  investigation_id
  goal
  hypothesis_refs[]
  experiment_type
  rationale
  discriminating_question
  expected_outcomes[]
  scenario_or_intervention
  required_input_refs[]
  requested_tools[]
  seed_policy
  horizon
  metrics[]
  budget
  safety_constraints[]
  status
```

## Experiment types

```text
COUNTERFACTUAL_ROLLOUT
PARAMETER_SWEEP
SENSITIVITY_ANALYSIS
SIGNAL_ANALYSIS
RULE_VALIDATION
RECOVERY_COMPARISON
AUTORESEARCH_TRIAL
```

## Discriminating experiment principle

For RCA, an experiment should state what result would distinguish competing explanations where possible.

Example:

```text
Question:
Does a reactor cooling-water disturbance reproduce the observed XMEAS(9)/XMEAS(21) trajectory better than a feed-temperature disturbance?

Expected outcomes:
- H1 predicts temperature rise with cooling-water signature A
- H2 predicts temperature/feed signature B

Metric:
trajectory similarity + direction/lag checks
```

The system should reward useful discrimination rather than raw experiment count.

## Experiment compilation

A proposal is data until validated/compiled:

```text
ExperimentProposal
 -> schema/policy/budget gate
 -> capability check
 -> scenario compiler / Tool Bridge resolution
 -> concrete `ExperimentRunSpec`
 -> isolated execution
```

### `ExperimentRunSpec`

```text
run_spec_id
experiment_id
branch/snapshot_ref
resolved_tool/config versions
resolved_interventions
seeds
horizon
metric/scorer versions
resource limits
```

The exact run spec is frozen before execution.

## `ExperimentResult`

```text
ExperimentResult
  experiment_id
  run_spec_ref
  status
  metric_values
  evidence_refs[]
  rollout/artifact_refs[]
  safety_summary_ref?
  failure_class?
  cost_usage
  started_at
  completed_at
```

The model does not author metric values that deterministic tools/scorers can compute.

## Result interpretation

After execution, the Main Agent may propose:

```text
ExperimentInterpretation
  experiment_ref
  hypothesis_updates[]
  conclusion_summary
  residual_uncertainty
  next_questions[]
```

The interpretation is distinct from the deterministic result.

## Duplicate / low-value experiment control

Before execution, the Coordinator/lab policy SHOULD compare a proposal with the Experiment Ledger for:

- identical run spec;
- equivalent hypothesis/question already tested;
- overlapping parameter search already exhausted;
- insufficient expected discrimination;
- budget disproportionate to expected value.

v0 may only block exact duplicates and annotate likely redundancy; stronger semantic duplicate detection is an evaluated feature.

## Parameter-search boundary

When the research question is numerical optimization rather than mechanism reasoning, the Agent SHOULD specify:

```text
search variables
bounds/constraints
objective(s)
why these variables matter
```

Then a deterministic optimizer/search tool performs the numeric search.

The Agent should not spend repeated model calls guessing individual floating-point values when grid/random/Bayesian/evolutionary search is more appropriate.

## Provenance

Every experiment must bind:

- hypothesis/question motivating it;
- exact environment snapshot/config;
- tool/library/scorer versions;
- seeds;
- rule versions used in validation;
- artifacts/results;
- model/subagent that proposed/interpreted it.

## Invariants

- Hypotheses are not persistent rules.
- Proposed experiments do not execute before deterministic validation.
- Experiment results are separate from model interpretation.
- Counterfactual experiments do not mutate the reference branch.
- Numeric metrics come from deterministic/scoped evaluators when available.
- Failed/negative experiments remain in the ledger.

## Acceptance tests

1. Create two competing root-cause hypotheses and attach evidence.
2. Propose a discriminating counterfactual experiment referencing both.
3. Reject an unsupported scenario before rollout.
4. Freeze and execute a valid run spec in an isolated branch.
5. Attach deterministic result evidence to both hypotheses with opposite relation labels.
6. Reject exact duplicate experiment execution from the ledger.
7. Hand a bounded numeric tuning problem to an optimizer tool rather than repeated model-value guessing.
