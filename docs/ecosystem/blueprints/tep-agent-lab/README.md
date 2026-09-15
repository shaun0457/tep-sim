# tep-agent-lab

Integration and benchmark laboratory for autonomous reasoning over the Tennessee Eastman Process.

This repository combines pinned versions of:

- `tep-sim` — trusted process sandbox;
- `industrial-agent-runtime` — generic agent/subagent harness.

It owns the **domain workflows and evaluations** that should not live in either reusable core.

## Research questions

1. Can an agent diagnose abnormal TEP behavior from process evidence without seeing ground-truth fault IDs?
2. Can an agent use forked counterfactual simulation to test competing root-cause hypotheses?
3. Can HAZOP-style deviations be systematically compiled, simulated, and summarized?
4. Can an agent propose safer recovery/mitigation strategies while deterministic gates retain execution authority?
5. When do dynamic subagents improve quality enough to justify additional token/latency cost?
6. Which tasks are better handled by deterministic logic than by an LLM?

## Core experiment families

### RCA

```text
incident observation
-> retrieve relevant topology/knowledge
-> ranked hypotheses
-> choose discriminating experiment(s)
-> fork/rollout
-> update hypotheses
-> final diagnosis
```

### Simulation-backed HAZOP

```text
node + parameter + guide word
-> candidate deviation
-> environment capability check
-> compile supported scenario
-> fork/rollout
-> safety/process consequence summary
-> HAZOP finding with evidence
```

### Recovery / mitigation

```text
abnormal state
-> generate candidate strategies
-> test candidates in forks
-> compare recovery/safety/production metrics
-> structured recommendation
-> deterministic action gate or human approval
```

## Agent role

Use one main agent by default. It may dynamically create subagents for bounded tasks such as:

- signal analysis;
- process-document retrieval;
- independent hypothesis testing;
- branch simulation analysis;
- critic/verifier.

Do not pre-create Supervisor / MachineExpert / DataEngineer / DataScientist roles.

## Suggested repository layout

```text
src/tep_agent_lab/
  tools/
    observe.py
    history.py
    topology.py
    fork.py
    rollout.py
    knowledge.py
  workflows/
    rca.py
    hazop.py
    recovery.py
  gates/
    action.py
    experiment_budget.py
  evals/
    diagnosis.py
    hazop.py
    recovery.py
    efficiency.py

scenarios/
  baseline/
  rca/
  hazop/
  recovery/

configs/
reports/
runs/          # gitignored or artifact-managed
tests/
docs/
AGENTS.md
```

## Evaluation dimensions

Always separate quality from efficiency:

```text
Task quality
- diagnosis accuracy/rank
- hazard coverage
- evidence correctness
- recovery success
- unsafe-action rejection

Agent efficiency
- model calls
- tokens
- subagents spawned
- environment rollouts
- latency

Environment outcomes
- shutdown
- time to recover
- safety margin
- production deviation
- control effort
```

## Ground-truth policy

Ground-truth fault/disturbance IDs may be stored in scenario metadata for scoring, but must not be exposed to the agent during blind diagnosis experiments.

## First benchmark

Start with reactor cooling-water behavior:

```text
IDV(4) injected as hidden ground truth
-> observe XMEAS trajectory
-> diagnose
-> test hypotheses via sandbox forks
-> optionally propose mitigation involving the reactor cooling-water control path
-> score diagnosis, experiment count, tokens, latency, and safety outcome
```

## Optional knowledge integration

`manufacturing-kg-agent` may later provide a read-only evidence tool for papers/manuals/SOPs. The lab must record which evidence was retrieved and must remain runnable without that service for baseline experiments.
