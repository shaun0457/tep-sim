# AGENTS.md

Rules for coding agents working on the TEP agent integration lab.

## Product boundary

This repository owns TEP-specific agent experiments and evaluation. It does not own the simulator implementation or generic agent-runtime internals.

## Dependency rules

- import/pin `tep-sim`; do not copy its physics or variable registry;
- import/pin `industrial-agent-runtime`; do not fork its orchestration into local variants unless an experiment explicitly studies that difference;
- optional knowledge services stay behind tool adapters.

## Hard experimental rules

1. Preserve hidden ground truth. Fault IDs used for scoring must not leak into blind agent context.
2. Every experiment must record simulator revision, agent-runtime revision, model/provider config, seed, scenario config, tool policy, and run ID.
3. Agent environment mutations use typed proposals and deterministic gates; no direct arbitrary simulator mutation from model text/code.
4. Counterfactual experiments use isolated forks, never the live/reference branch.
5. HAZOP findings must distinguish simulated evidence from inferred/non-simulable consequences.
6. Unsupported environment physics must be reported as unsupported, not filled in by the model.
7. Store large telemetry as artifacts; provide compact task-specific features to agents.
8. Cap model calls, subagents, rollout branches, horizon, and retries.
9. Evaluate deterministic baselines before claiming agent benefit.
10. Keep evaluation code independent of agent self-report/confidence.

## Dynamic subagent policy

Subagents are allowed for bounded, independently useful work. Each must receive:

```text
goal
input evidence/context slice
allowed tools
budget
output schema
```

Examples:

- compare two hypotheses;
- analyze a selected signal window;
- inspect retrieved process evidence;
- review a candidate HAZOP finding;
- summarize one counterfactual branch.

Do not send the complete experiment transcript to every subagent.

## HAZOP safety boundary

Simulation-backed HAZOP in this lab is research/decision support. Do not describe it as replacing formal plant HAZOP or engineering safety review.

A finding must state:

```text
deviation
simulability
implemented intervention
observed process consequence
safety-limit outcome
inferred consequences (if any, clearly labelled)
unsupported consequence domains
provenance
```

## Reporting

Every benchmark report should include both successful and failed runs, token/latency cost, environment rollout count, and deterministic baseline comparison.
