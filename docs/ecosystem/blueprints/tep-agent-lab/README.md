# tep-agent-lab

Integration and benchmark laboratory for autonomous reasoning over the Tennessee Eastman Process.

This repository combines pinned versions of:

- `tep-sim` — trusted process environment + DEXPI/process semantic layer;
- `industrial-agent-runtime` — generic main-agent / ephemeral-subagent harness.

It owns TEP-specific tools, domain-policy gates, workflows, scenarios, evaluation, and research reports.

## Research questions

1. Can an agent diagnose abnormal TEP behavior without seeing evaluator-only fault truth?
2. Can it select useful process signals and traverse topology instead of consuming the entire plant state?
3. Can it design discriminating counterfactual experiments in forked simulations?
4. Can simulation-backed HAZOP produce evidence-grounded findings while clearly reporting unsupported physics?
5. Can recovery strategies be tested in forks before a bounded proposal reaches the reference branch?
6. When do dynamic subagents improve quality enough to justify additional cost/latency/context?
7. Which parts of the workflow should remain deterministic rather than agentic?

## Core experiment families

### RCA

```text
incident projection
 -> query topology/history
 -> ranked hypotheses
 -> discriminating experiment(s)
 -> fork/rollout
 -> update ranking
 -> evidence-backed diagnosis
```

### Simulation-backed HAZOP

```text
node + parameter + guide word
 -> candidate deviation
 -> capability check
 -> deterministic scenario compilation
 -> fork/rollout
 -> deterministic process/safety evidence
 -> structured finding
```

### Recovery

```text
abnormal state
 -> candidate strategies
 -> fork each candidate + no-action baseline
 -> deterministic outcome metrics
 -> recommendation
 -> layered gate / optional approval
 -> bounded reference action + verification (when enabled)
```

## Agent model

Use one main agent by default. It may create bounded ephemeral subagents for independent hypothesis testing, signal analysis, branch evaluation, retrieval, or verification.

Do not pre-create Supervisor / MachineExpert / DataEngineer / DataScientist roles.

v0 proposed defaults are inherited from the runtime policy: subagent depth 1, at most 3 children per parent, and no child reference-world mutation authority.

## Suggested repository layout

```text
src/tep_agent_lab/
  contracts/
  tools/
    observation.py
    history.py
    topology.py
    simulation.py
    recovery.py
  policies/
    experiment.py
    recovery.py
  workflows/
    rca.py
    hazop.py
    recovery.py
  evals/
    common.py
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

## Ground-truth policy

Scenario truth is evaluator-only in blind experiments. The runtime receives a derived agent-visible projection and registered tools that do not expose hidden fault IDs.

## First benchmark direction

Start with the reactor/cooling-water subsystem because the topology/runtime relationships are known and suitable for exercising telemetry, topology, counterfactual simulation, and recovery.

Do **not** permanently hard-code one IDV as the benchmark before measuring whether the chosen scenario is appropriately diagnosable. Exact disturbance, timing, and magnitude belong in versioned fixtures.

## Optional knowledge integration

`manufacturing-kg-agent` may later provide read-only evidence from papers/manuals/SOPs. Establish clean no-KG baselines first so its contribution can be measured.

## Documentation

- `docs/architecture.md` — integration architecture
- `docs/roadmap.md` — implementation sequence
- `docs/specs/tool-surface-v0.md` — agent-visible environment tools
- `docs/specs/rca-v0.md` — RCA benchmark contract
- `docs/specs/hazop-v0.md` — simulation-backed HAZOP contract
- `docs/specs/recovery-v0.md` — recovery contract
- `docs/specs/evaluation-v0.md` — evaluation/ablation/ground-truth contract
- `docs/open-questions.md` — unresolved research decisions
- `docs/decisions/` — ADRs
