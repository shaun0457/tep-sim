# Recovery Planning v0

Status: proposal  
Version: v0  
Owner repo: `tep-agent-lab`

## Goal

Evaluate whether an agent can propose and compare bounded recovery strategies using isolated counterfactual rollouts before any reference-world intervention is considered.

## Core policy

**Simulate before apply** is the v0 default for agent-proposed recovery when a scenario is forkable and time permits.

An agent never directly writes XMV values to the reference environment.

## Recovery proposal

```text
proposal_id
incident_id
objective
candidate_intervention(s)
expected_effect
verification_horizon
expected_tradeoffs
confidence
supporting_evidence_refs
```

## Candidate generation

The main agent may generate multiple candidates. Subagents may evaluate independent candidates only in isolated branches.

Candidates must use a lab-provided allowed action space; free-form simulator mutation is not exposed.

## Counterfactual evaluation

For each candidate:

```text
reference snapshot
 -> fork
 -> deterministic capability/policy validation
 -> apply candidate in fork
 -> rollout
 -> deterministic outcome/safety metrics
 -> candidate score artifact
```

A no-action branch SHOULD be included when meaningful.

## Candidate score

v0 should keep scoring explicit rather than hiding it in the LLM. Example metric vector:

```text
recovery_success
max_temperature/pressure excursion
minimum_safety_margin
shutdown occurrence/time
settling/recovery time
production/process deviation proxy
intervention magnitude
number of manipulated variables changed
```

A scalar ranking MAY be defined per experiment, but raw metric vector must be retained.

## Reference-world gate path

If the experiment permits actual application to the reference branch:

```text
selected proposal
 -> runtime generic gates
 -> lab policy gate
 -> tep-sim capability/bounds/control-mode validation
 -> optional human approval
 -> frozen validated intervention token
 -> apply
 -> verification window
 -> deterministic outcome check
```

A failed or stale validation token cannot be reused silently.

## v0 policy constraints

Each recovery fixture SHOULD define:

```text
allowed_actuators
max_delta per actuator
max number of simultaneous actuator changes
max reference-world interventions
cooldown / minimum verification horizon
forbidden states/actions
```

Do not encode these limits only in prompts.

## Post-action verification

After an applied recovery action, deterministic verification classifies outcome, for example:

```text
RECOVERED
IMPROVED_NOT_RECOVERED
NO_EFFECT
WORSENED
SHUTDOWN
INCONCLUSIVE
```

The agent may receive the structured result and replan if fixture budget permits.

## Retry policy

v0 recovery loops MUST be bounded. Fixture defines `max_recovery_rounds`; after exhaustion, the experiment transitions to `SAFE_HOLD`/`STOP`/`HUMAN_REVIEW` as configured rather than allowing indefinite model replanning.

## Baselines

Compare at least:

1. no action;
2. deterministic recovery policy for the chosen scenario;
3. main-agent proposal without counterfactual pre-test;
4. main-agent proposal with counterfactual evaluation;
5. main agent + bounded subagent candidate evaluation.

## Evaluation metrics

- recovery success rate;
- shutdown rate;
- time to recover;
- minimum safety margin;
- intervention magnitude/count;
- invalid/rejected proposal rate;
- number of candidate rollouts;
- model/tool/token/latency cost;
- agreement between predicted and observed recovery effect.

## Invariants

- Candidate rollouts never mutate reference state.
- Agent cannot bypass allowed action space or domain gate.
- Deterministic metric vectors are retained even if the model provides narrative tradeoff reasoning.
- Retry count is deterministic and bounded.
- Every applied action links to proposal, validation decision, exact parameters, and post-action verification.

## Acceptance criteria

1. For one reactor-cooling incident, generate at least two allowed recovery candidates plus no-action baseline.
2. Run isolated rollouts for each candidate.
3. Rank candidates using deterministic metric artifacts plus agent reasoning.
4. Reject one deliberately invalid proposal before reference mutation.
5. Apply one valid frozen intervention in an experiment configured to allow reference action.
6. Produce deterministic post-action outcome classification and complete provenance.
