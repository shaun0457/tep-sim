# tep-agent-lab

Integration and benchmark laboratory for autonomous engineering investigation over the Tennessee Eastman Process.

This repository combines pinned versions of:

- `tep-sim` — trusted process world + DEXPI/ProcessGraph semantics;
- `industrial-agent-runtime` — Hybrid Main-Agent runtime with deterministic Coordinator/Executor/Verifier, Dynamic DAGs, gates, and ephemeral subagents.

It owns TEP-specific Investigation State, information/rule/evidence/experiment contracts, Tool Bridge adapters, research workflows, scenarios, evaluation, and reports.

## Agent role

v0 studies an **Autonomous Industrial Process Investigator**.

The Main Agent may:

- inspect process state/topology;
- select evidence/analysis tools;
- create/update hypotheses;
- design counterfactual experiments;
- propose bounded Dynamic DAGs;
- delegate narrow subtasks;
- integrate evidence;
- decide when evidence is sufficient;
- recommend recovery/research actions.

It does not receive unrestricted reference-world mutation authority.

## Core research questions

1. Can an Agent diagnose abnormal TEP behavior without seeing evaluator-only fault truth?
2. Can it select useful signals/topology/analysis tools instead of consuming the entire plant state?
3. Can it design experiments that discriminate competing hypotheses efficiently?
4. Does Hybrid orchestration outperform pure ReAct/fixed workflows for complex investigation?
5. When does a Dynamic DAG/subagent improve quality enough to justify overhead?
6. Can paper/domain knowledge be promoted into validated machine-usable rules without turning LLM extraction into hard authority?
7. Can simulation-backed HAZOP remain evidence-grounded and honest about unsupported physics?
8. Can recovery strategies be simulated before gated reference action?
9. Can an AutoResearch-style loop discover better bounded engineering strategies under a frozen evaluator?

## Core architecture

```text
Hybrid Agent Runtime / Control Plane
 Main Agent
 deterministic Coordinator / Executor / Verifier
            |
            v
TEP Agent Lab / Information + Research Plane
 Investigation State
 Hypotheses / Evidence / Experiments
 K2/K3 Rule Registry
 Tool Bridge
 Experiment Ledger
 RCA / HAZOP / Recovery / AutoResearch
            |
            v
TEP-Sim / World Plane
 ProcessGraph + Variable Registry
 K0/K1 truth
 snapshot / fork / rollout / capability / safety
```

## Knowledge model

```text
K0 simulator/runtime truth
K1 reviewed physical/safety invariant
K2 simulation-validated engineering relationship
K3 paper/document heuristic
K4 Agent working hypothesis
```

Only high-authority reviewed rules may block execution. K3/K4 never become hard gates directly.

## Tool model

Environment tools expose observations/topology/simulation. A separate Tool Bridge wraps allowlisted open-source scientific functions for signal analysis, PCA/PLS baselines, sensitivity analysis, graph operations, and bounded numeric optimization.

The normal runtime does not give the Agent arbitrary Python/shell/import/package-install authority.

## Research families

### RCA

```text
incident -> Investigation State
 -> hypotheses
 -> evidence/analysis
 -> discriminating counterfactual experiments
 -> deterministic results
 -> hypothesis updates
 -> evidence-backed diagnosis
```

### Simulation-backed HAZOP

```text
node + parameter + guide word
 -> candidate deviation
 -> rule/capability check
 -> deterministic scenario compilation
 -> fork/rollout
 -> process/safety evidence
 -> structured supported/unsupported finding
```

### Recovery

```text
abnormal state
 -> candidate strategies
 -> fork each strategy + no-action baseline
 -> deterministic score
 -> recommendation
 -> layered gates / optional approval
 -> bounded reference action + verification (when enabled)
```

### AutoProcessResearch

```text
frozen ResearchSpec/evaluator
 -> baseline
 -> Agent hypothesis/change
 -> bounded simulation/search trial
 -> deterministic score
 -> Experiment Ledger
 -> keep/reject/neutral
 -> repeat until deterministic stop
 -> hidden evaluation
```

## Benchmark philosophy

TEP is public and well known, so the lab does not score fault-name recall alone. Benchmarks use evidence requirements, varied timing/magnitude/seeds, plausible alternatives, counterfactual experiments, hidden variants, and scientific-behavior metrics.

Scenario families are piloted for identifiability before being frozen.

## Suggested repository layout

```text
src/tep_agent_lab/
  contracts/
    investigation.py
    hypothesis.py
    experiment.py
    evidence.py
    rules.py
  information/
    evidence_store.py
    experiment_ledger.py
    context_projection.py
  tools/
    environment.py
    topology.py
    analysis.py
    bridge.py
    simulation.py
    optimization.py
    recovery.py
  policies/
    experiment.py
    recovery.py
    knowledge.py
  workflows/
    rca.py
    hazop.py
    recovery.py
    autoresearch.py
  evals/
    common.py
    scientific_behavior.py
    diagnosis.py
    hazop.py
    recovery.py
    autoresearch.py

scenarios/
  development/
  research/
  hidden_eval/

configs/
reports/
runs/          # artifact-managed / gitignored
tests/
docs/
AGENTS.md
```

## Ground-truth policy

Scenario truth is evaluator-only in blind experiments. Agent-visible projections, Information Plane refs, tools, rules, and artifact metadata are leakage-audited.

## First benchmark direction

Start with reactor/cooling-water scenario family, but do not permanently hard-code one IDV before identifiability pilot work determines useful competing causes, magnitudes, timings, and difficulty variants.

## Optional knowledge integration

`manufacturing-kg-agent` may later provide read-only evidence from papers/manuals/SOPs. Establish clean no-KG baselines first so its contribution can be measured and paper-derived relations enter as K3 candidates rather than execution truth.

## Documentation

- `docs/architecture.md` — Hybrid/information/world-plane integration
- `docs/roadmap.md` — research implementation sequence
- `docs/specs/README.md` — canonical v0 spec index
- `docs/open-questions.md` — remaining empirical choices
- `docs/decisions/` — ADRs
