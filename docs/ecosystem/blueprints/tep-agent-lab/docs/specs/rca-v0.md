# RCA Experiment v0

Status: proposal  
Version: v0  
Owner repo: `tep-agent-lab`

## Goal

Evaluate whether an agent can diagnose a hidden TEP incident by selecting relevant evidence, using process topology, generating hypotheses, and designing discriminating counterfactual experiments.

The target capability is **investigation**, not memorized fault-name classification.

## Scenario fixture

Each RCA case MUST separate evaluator-only truth from agent-visible projection.

Conceptual fixture:

```text
case_id
baseline_config
hidden_disturbance_schedule
reference_run_seed
incident_start_time
agent_visible_trigger
allowed_tool_policy
experiment_budget
scoring_config
ground_truth
```

`ground_truth` MUST never be passed through registered agent tools in blind mode.

## Agent-visible start state

The agent receives a compact incident context, for example:

```text
incident_id
simulation_time
trigger evidence / top abnormal signals
current safety summary
minimal local topology seed
recent action summary
available tools and budgets
```

It does not automatically receive all variables or the hidden IDV.

## Required agent output

Final structured RCA result:

```text
incident_id
ranked_hypotheses[]
  - hypothesis
  - confidence
  - supporting_evidence_refs
  - contradicting_evidence_refs?
  - tested_experiments[]
selected_root_cause
uncertainty
remaining_questions
```

A textual explanation may accompany the structure but scoring uses structured fields/evidence refs.

## Investigation loop

The runtime does not hard-code one reasoning sequence, but a valid run may include:

```text
observe
 -> query relevant topology/history
 -> generate hypotheses
 -> spawn bounded hypothesis subtasks? 
 -> choose discriminating experiment(s)
 -> fork/rollout
 -> compare prediction to observed trajectory
 -> update ranking
 -> finish within budget
```

## Counterfactual semantics

A counterfactual experiment must state what hypothesis it tests and what observation would discriminate it where possible.

The agent may use an isolated branch to instantiate a simulator-supported disturbance or candidate condition. Unsupported hypotheses remain reportable but cannot be scored as simulation-confirmed.

## v0 first case

Recommended first benchmark:

- reference incident involving reactor cooling-water behavior;
- hidden ground truth uses a simulator-supported disturbance;
- initial visible evidence includes abnormal reactor-related telemetry but not the disturbance ID;
- topology permits discovery of XMEAS(9), XMEAS(21), XMV(10), and relevant disturbance relations through tools.

Exact disturbance and magnitude should be fixture-controlled and may vary across seeds/cases to reduce memorization.

## Budgets

Each case records at minimum:

```text
max_model_calls
max_tool_calls
max_subagents
max_simulation_rollouts
max_simulated_horizon_total
```

Simulation budget is application-specific and must be enforced outside model prose.

## Scoring

At minimum:

- top-1 root-cause correctness;
- top-k inclusion;
- evidence quality / evidence-ref validity;
- number of irrelevant variable/history queries;
- number of simulation rollouts;
- model/tool/subagent budget usage;
- total tokens and latency;
- unsupported/hallucinated environment claims;
- calibration of confidence where sample size permits.

A useful secondary metric is **diagnostic efficiency**: correctness per tool/simulation/token budget.

## Baselines / ablations

Run the same case against:

1. static incident context only, no tools;
2. main agent + read tools;
3. main agent + read + topology tools;
4. main agent + counterfactual simulation;
5. main agent + counterfactual simulation + bounded subagents;
6. optional knowledge-service evidence.

This isolates which capabilities produce improvement.

## Invariants

- Ground truth remains evaluator-only in blind mode.
- All supporting evidence refs must point to actually observed/query/simulation artifacts.
- A simulator rollout result cannot be invented in model text.
- Unsupported hypotheses are labeled as untested/unsupported rather than simulated facts.
- Reference state is not mutated during diagnosis.

## Acceptance criteria for first case

1. Deterministic fixture can reproduce the hidden incident.
2. Agent-visible projection contains no direct fault identifier.
3. Single-agent run can complete under a fixed budget.
4. Counterfactual-enabled run can create at least one isolated discriminating rollout.
5. Scorer deterministically compares structured output to hidden truth.
6. Full trace can explain why each tool/model/subagent call occurred.
