# tep-agent-lab

Integration and benchmark laboratory for autonomous engineering investigation over the Tennessee Eastman Process.

Depends on pinned versions of:

- `tep-sim` — trusted process world + DEXPI/ProcessGraph semantics;
- `industrial-agent-runtime` — generic Main-Agent runtime with deterministic gates/state interfaces, dependency-aware WorkBatch, and bounded subagents.

The lab owns TEP-specific state/projection, tools, policy, experiments, engineering records, benchmark/evaluation logic, and later HAZOP/recovery/AutoResearch studies.

## v0 role

Study an **Autonomous Industrial Process Investigator**.

The Main Agent may:

- inspect process state/topology;
- select observations/analysis tools;
- form/update hypotheses;
- make typed predictions;
- design counterfactual experiments;
- propose dependency-aware TOOL work;
- delegate bounded subtasks in the appropriate orchestration condition;
- explicitly link observations as evidence;
- produce structured CausalClaims/reports.

It does not receive unrestricted reference-world mutation authority.

## Core research questions

1. Can an Agent diagnose hidden TEP incidents without evaluator truth/candidate labels?
2. Can it select useful observations/topology/analysis rather than consume the full plant state?
3. Can it design experiments whose typed predictions meaningfully discriminate plausible causes?
4. Does Hybrid orchestration improve investigation quality/efficiency relative to one-shot/ReAct/fixed workflow?
5. Does dependency-aware WorkBatch/subagent use add value beyond simpler Agent loops?
6. When is a strong deterministic C0 baseline already sufficient, making an Agent unnecessary?
7. Later: can validated knowledge, recovery, HAZOP, AutoResearch, and structured historical records improve engineering work without authority leakage?

## Core architecture

```text
industrial-agent-runtime
 CONTROL PLANE
  Main Agent
  pre-execution gates
  Executor
  post-execution verifier
  WorkBatch / SubtaskResult
            |
            v
tep-agent-lab
 DOMAIN / INFORMATION PLANE
  RcaState implements TaskStateStore
  ObservationRecord / EvidenceLink
  Hypothesis / Prediction / Experiment
  Rule metadata: origin x validation x authority
  Tool Bridge adapters
  Engineering Records
  benchmark / scorer / policy
            |
            v
tep-sim
 WORLD PLANE
  ProcessGraph / VariableRegistry
  simulator truth
  snapshot / fork / rollout
  capability / environment safety
```

## Information model

```text
Trace != Observation != Evidence != EngineeringRecord != Rule/Knowledge != Context
```

v0 may persist one append-only run log plus artifacts rather than separate Evidence/Experiment/Trace database services.

Historical Engineering Records are archive-only in first benchmarks and are not automatically retrieved into later Agent context.

## Rule model

Canonical machine metadata:

```text
origin × validation × authority
```

K0–K4 may appear only as human-facing shorthand. Paper/Agent/simulation evidence cannot self-grant HARD_GATE authority.

## Tool model

Tool Bridge adapters live in the lab, but authorization/budget/dispatch remains in generic runtime.

```text
Agent
 -> runtime ToolSpec/gates/budget
 -> lab validate_request
 -> Executor
 -> Tool Bridge / tep-sim adapter
 -> result + actual resource usage
 -> post-execution verification
```

Any bridge that internally runs TEP trials is `SIMULATE` and consumes explicit rollout/horizon/trial budget.

First RCA bridge set stays small: response features/trajectory comparison, lag/cross-correlation, and optional TEP detector baseline.

No arbitrary Agent Python/shell/import/package-install authority.

## First research family — RCA

```text
incident -> RcaState
 -> observations
 -> hypotheses + typed predictions
 -> evidence links
 -> discriminating analysis/counterfactuals
 -> deterministic ExperimentResults
 -> structured CausalClaim
 -> InvestigationReport
```

Every first-family report includes a strong deterministic C0 enumerate/simulate/match baseline.

Blind RCA does not expose canonical IDV candidate bindings through tools by default.

## Later research families

### Simulation-backed HAZOP

Only after RCA state/tool/evaluation contracts stabilize.

### Recovery

Rank simulated candidate strategies before enabling any reference MUTATE path. SIMULATE never mutates reference state.

### AutoProcessResearch

Later task family with frozen evaluator/search surface, explicit simulation budgets, append-only experiment history, and hidden evaluation. It is not simply another orchestration-ablation row.

## Benchmark philosophy

TEP is public, so do not score fault-name recall alone.

Use:

- strong deterministic C0;
- varied seed/timing/magnitude/operating state;
- healthy/no-abnormal cases;
- non-local/nontrivial alternatives;
- evidence/prediction/experiment requirements;
- hidden variants;
- data-informed difficulty tiers;
- scientific-behavior/resource metrics.

## Suggested v0 repository direction

```text
src/tep_agent_lab/
  contracts/
    rca_state.py
    hypothesis.py
    prediction.py
    experiment.py
    evidence.py
    causal_claim.py
    rules.py
    records.py
  information/
    run_log.py
    projection.py
  tools/
    environment.py
    topology.py
    bridge.py
  policies/
    request_validation.py
    result_verification.py
    benchmark.py
  evals/
    baseline_c0.py
    diagnosis.py
    scientific_behavior.py
    efficiency.py

scenarios/
  development/
  research/
  hidden_eval/

runs/
reports/
tests/
docs/
AGENTS.md
```

Do not pre-create HAZOP/recovery/AutoResearch modules until their phase begins.

## Ground-truth policy

Scenario truth/candidate sets are evaluator-only in blind experiments. ContextProjection, tools, ProcessGraph bindings, Rule metadata, artifacts, and Engineering Record retrieval are leakage-audited.

## Documentation

Canonical spec index: `docs/specs/README.md`.

The most important first-RCA specs are:

- `investigation-state-v0.md`
- `hypothesis-experiment-v0.md`
- `tool-surface-v0.md`
- `tool-bridge-v0.md`
- `engineering-records-v0.md`
- `benchmark-design-v0.md`
- `evaluation-v0.md`
- `rca-v0.md`

Later task specs remain proposals until their implementation phase.
