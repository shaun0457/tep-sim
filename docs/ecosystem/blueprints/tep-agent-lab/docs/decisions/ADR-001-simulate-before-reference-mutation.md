# ADR-001 — Simulate before reference-world mutation

Status: proposed  
Date: 2026-09-15

## Context

The TEP sandbox is forkable and intended for counterfactual experimentation. Agent-generated recovery actions are uncertain, while isolated rollouts are cheap relative to reference-world mutation.

## Decision

For v0 recovery experiments, the default path is:

```text
propose candidate
 -> validate for simulation
 -> apply in isolated fork
 -> rollout and score
 -> select candidate
 -> revalidate exact action for reference state
 -> optional approval
 -> apply to reference branch only if experiment policy permits
```

Direct model-to-reference mutation is prohibited.

## Rationale

This design:

- uses the unique value of a simulator rather than treating the agent as a direct controller;
- creates evidence for why an action was selected;
- reduces unsafe/invalid action application;
- enables deterministic comparisons with no-action and alternative strategies;
- makes recovery quality easier to evaluate and debug.

## Consequences

Positive:

- stronger provenance and safety;
- natural counterfactual benchmark;
- clear boundary between reasoning and authority.

Negative:

- additional simulation cost/latency;
- fork fidelity becomes important;
- some time-critical scenarios may eventually need a different policy.

## Exceptions

A future experiment may disable simulate-before-apply only when explicitly specified as an ablation or when the environment/task makes simulation unavailable. Such runs must be labeled accordingly.

## Revisit trigger

Revisit after v0 recovery benchmarks quantify simulation cost versus safety/quality gain, or if a future real-time environment has constraints incompatible with pre-action rollouts.
