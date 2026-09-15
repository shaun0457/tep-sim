# AutoProcessResearch v0

Status: accepted direction / v0 contract proposal  
Owner repo: `tep-agent-lab`

## Goal

Adapt the autonomous experiment-loop pattern popularized by Karpathy's `autoresearch` to a process-simulation playground without allowing the agent to modify TEP physics, scoring code, or safety policies.

The mode is intended for autonomous engineering research over a frozen evaluation setup:

```text
Research goal
 -> hypothesis
 -> bounded experiment
 -> deterministic score
 -> keep/reject/update best
 -> record result
 -> repeat until stop condition
```

## What we borrow from autoresearch

The useful design pattern is:

- keep the research surface deliberately small;
- freeze preparation/evaluation logic;
- define a measurable objective;
- use a fixed/bounded budget per experiment;
- keep failures and negative results;
- maintain a persistent experiment record;
- make accepted improvements monotonic relative to the declared metric/constraints.

Unlike code-training autoresearch, the mutable artifact here is normally a process/recovery/controller/experiment configuration, not simulator source code.

## `ResearchSpec`

```text
ResearchSpec
  research_id
  goal
  research_mode
  mutable_surface
  frozen_evaluator_ref
  baseline_ref
  primary_objective
  direction: MINIMIZE | MAXIMIZE
  hard_constraints[]
  secondary_metrics[]
  scenario_distribution_ref
  parameter/search bounds?
  per_trial_budget
  total_budget
  seed_policy
  acceptance_policy
  stop_policy
  tool_policy
```

The human/research harness owns the `ResearchSpec`. The Agent cannot silently change the frozen evaluator, objective, constraints, benchmark scenarios, or authority policy.

## Candidate v0 research modes

### Recovery strategy search

Agent proposes mechanisms/strategy structure; deterministic simulation and scorer evaluate safety/recovery/production/control-effort outcomes.

### Controller/parameter tuning

Agent chooses relevant parameters, bounds, objectives, and rationale. A deterministic optimizer Tool Bridge performs numeric search where appropriate.

### Detector/policy tuning

Agent may investigate threshold/window/feature choices against frozen train/dev scenarios. Hidden evaluation remains separate to reduce benchmark overfitting.

### Experimental design research

Agent searches for experiment policies that discriminate hypotheses efficiently, scored by diagnosis quality versus rollout/tool budget.

## Explicit non-goals for v0

AutoProcessResearch does not allow the Agent to:

- edit TEP physics/source implementation;
- alter hidden ground truth;
- edit the scoring/evaluator implementation during a session;
- widen its own tool/authority budgets;
- redefine hard safety constraints;
- change benchmark cases to make the metric easier;
- install arbitrary dependencies;
- self-modify generic runtime code during an experiment campaign.

Agent/runtime/prompt optimization may be studied later as a separate meta-research mode with stronger leakage/overfitting controls.

## Experiment loop

```text
INITIALIZE
 -> evaluate baseline
 -> load Experiment Ledger / best-known candidate
 -> MAIN AGENT proposes one research hypothesis
 -> compile one conceptual experiment
 -> validate mutable surface + budget + constraints
 -> execute isolated simulation/search
 -> deterministic scorer
 -> verifier checks artifacts/constraints/provenance
 -> append result to ledger
 -> ACCEPT / REJECT / NEUTRAL
 -> update best-known candidate if accepted
 -> STOP_CHECK
 -> repeat
```

### One conceptual change per trial

v0 SHOULD prefer one clearly attributable mechanism/change per trial. A deterministic numerical optimizer may evaluate multiple numeric points inside that one experiment when the conceptual change is "search this bounded parameter space."

This preserves attribution without forcing the LLM to guess one floating-point value per model turn.

## Candidate contract

```text
ResearchCandidate
  candidate_id
  parent_candidate_ref?
  hypothesis_ref
  change_set
  mutable_surface_refs
  rationale
  complexity_delta?
```

`change_set` must be expressible within the allowed mutable surface.

## Scoring

v0 uses one primary scalar objective plus hard constraints and recorded secondary metrics.

Example recovery score:

```text
hard constraints:
  no invalid operation
  no prohibited safety violation

primary objective:
  weighted recovery loss

secondary metrics:
  min safety margin
  time to recover
  production deviation
  control effort
  shutdown
```

The scalarization/weights are frozen in `ResearchSpec`, not invented per trial by the Agent.

Multi-objective Pareto tracking may be added later, but v0 should remain easy to interpret.

## Acceptance policy

Default monotonic policy:

```text
ACCEPT if:
  hard constraints pass
  AND primary objective improves by configured minimum delta
  AND run validity checks pass

REJECT if:
  constraint violation, failure, or objective regression

NEUTRAL if:
  statistically/meaningfully indistinguishable under configured tolerance
```

No result is deleted; acceptance only changes `best_candidate_ref`.

## Stochastic/noisy metrics

If a metric is noisy, `ResearchSpec` may require repeated seeds/replications before acceptance.

Acceptance must use a frozen deterministic statistical policy, e.g. mean/quantile/worst-case over the declared seed set.

The Agent may observe uncertainty but cannot choose only favorable seeds after seeing results.

## Deterministic optimizer delegation

For bounded numeric search:

```text
Main Agent:
  identifies mechanism
  selects variables/bounds
  defines why they matter
          |
          v
Tool Bridge optimizer:
  grid/random/TPE/evolutionary/etc.
  evaluates objective through isolated rollouts
          |
          v
best numeric candidate + trial history
          |
          v
Main Agent interprets result
```

Optimizer method/version/seed/trials are pinned in provenance.

## Experiment Ledger

Every trial is append-only and records:

```text
trial_id
candidate_ref
hypothesis_ref
parent_best_ref
resolved run/search spec
objective + secondary metrics
constraint verdict
status: ACCEPT | REJECT | NEUTRAL | FAILED
failure class?
artifact refs
model/tool/library versions
budget usage
notes/interpretation refs
```

Failed experiments are valuable negative knowledge and prevent repeated dead ends.

## Ideas backlog

The research state MAY maintain an explicit backlog:

```text
ResearchIdea
  idea_id
  hypothesis
  expected benefit
  required tools
  estimated cost
  dependencies
  status
```

The Agent chooses among untested ideas based on evidence, remaining budget, and expected value rather than rediscovering ideas from transcript history.

## Stopping conditions

A session stops when any deterministic condition is met:

- total trial/model/tool/simulation budget exhausted;
- wall/compute budget exhausted if configured;
- maximum accepted improvements reached;
- plateau: no meaningful improvement over N valid trials;
- no valid candidate remains in backlog and Main Agent returns no bounded proposal;
- configured target metric reached;
- human cancellation.

The Agent may recommend stopping, but deterministic budget/backstop rules remain authoritative.

## Benchmark-overfitting protection

Research scenarios are separated into:

```text
DEV/RESEARCH scenarios — visible through declared feedback
HIDDEN EVAL scenarios — evaluator-only final generalization check
```

An accepted candidate may improve dev performance but must not be claimed generally better until hidden evaluation confirms it.

## Interaction with Dynamic DAG

A single research trial may use a bounded Dynamic DAG for parallel independent rollouts/analysis. The trial remains one ledger item with child run refs.

Dynamic DAG expansion is constrained by the trial's fixed budget.

## Suggested first AutoProcessResearch campaign

Research question:

> Find a robust bounded recovery strategy for a curated reactor cooling-water disturbance family.

Mutable surface:

- selected recovery strategy structure;
- approved actuator targets/sequence;
- bounded numeric controller/action parameters through optimizer tool.

Frozen:

- TEP simulator revision;
- scenario set/seeds;
- safety constraints;
- objective/scorer;
- tool/rule policy.

Compare:

- no action;
- deterministic hand-designed baseline;
- Agent manual candidate loop;
- Agent + deterministic optimizer;
- optional Dynamic DAG parallel evaluation.

## Evaluation metrics

- best hidden-eval objective;
- experiments to first improvement;
- accepted/rejected/failed counts;
- duplicate/redundant trial rate;
- total simulated horizon;
- model/tool/tokens/cost;
- safety/constraint violations attempted;
- robustness across scenarios/seeds;
- complexity of accepted strategy.

## Invariants

- Evaluator/scoring logic is frozen per campaign version.
- Agent cannot mutate world/reference physics or its own authority policy.
- Every trial is reproducible and retained.
- Numeric search is delegated to deterministic optimizers when appropriate.
- Improvements are only relative to the declared metric/scenario distribution.
- Hidden evaluation remains inaccessible to the research agent.

## Acceptance tests

1. Run baseline and create first best-candidate ref.
2. Execute one valid candidate and accept an improvement.
3. Execute one regression and reject it without losing history.
4. Block an attempt to change evaluator/objective/safety constraints.
5. Delegate bounded numeric tuning to an optimizer bridge and preserve all trial provenance.
6. Stop deterministically on plateau/budget.
7. Evaluate final best candidate on hidden scenarios unavailable to the Agent.
