# Architecture — TEP Agent Lab

## Purpose

`tep-agent-lab` is the TEP-specific integration/research layer between the generic Agent Runtime and the trusted TEP world. It owns domain state/projection, tools/adapters, policy/rules, experiments, engineering records, benchmark fixtures, and evaluation.

## System boundary

```text
industrial-agent-runtime
  generic control plane
  Main Agent
  pre-execution gates
  Executor
  post-execution verifier
  WorkBatch / SubtaskResult
          |
          v
+------------------------------------------------+
|                 tep-agent-lab                  |
|                                                |
|  RcaState implements TaskStateStore            |
|  ObservationRecord / EvidenceLink              |
|  Hypothesis / Prediction / Experiment          |
|  Rule metadata: origin x validation x authority|
|  Tool Bridge + domain validators               |
|  Engineering Records                           |
|  benchmark / scoring / research workflows      |
+----------------------+-------------------------+
                       |
                       v
                    tep-sim
         ProcessGraph / VariableRegistry
         simulator truth / dynamics
         snapshot / fork / rollout / capability
```

`manufacturing-kg-agent` may later provide read-only evidence as an explicit capability condition.

## Runtime integration

The lab consumes runtime contracts rather than redefining them.

### State

Runtime knows:

```text
TaskStateStore
ContextProjection
StateDelta
TaskStatus
```

Lab implements these with `RcaState` and a deterministic/domain-aware `project_rca_state` function.

Runtime never imports RcaState fields.

### Request path

```text
Main Agent request
 -> runtime G0-G3
 -> lab validate_request
      + benchmark/experiment policy
      + tep-sim capability/bounds/control checks as needed
 -> Executor
 -> lab/tep-sim/Tool Bridge adapter
 -> post-execution verify_result
 -> lab TaskStateStore.apply
```

Pre-execution request validation and post-execution result verification are different hooks.

## Work planning

v0 uses runtime dependency-aware WorkBatch only:

```text
WorkItem(kind=TOOL | SUBTASK, depends_on=[...])
```

There are no lab-specific ANALYSIS/MERGE graph nodes.

- deterministic analysis is a TOOL;
- open-ended merge/integration is the next Main Agent turn;
- simulation is a TOOL with side-effect class SIMULATE;
- full mutable Dynamic DAG replanning is later research.

## Information Plane

The program Information Plane is a logical ownership/ref layer, not multiple mandatory databases.

### Environment-owned

From `tep-sim`:

- ProcessGraph / DEXPI semantics;
- VariableRegistry;
- simulator capabilities/constraints;
- snapshots/rollouts/safety artifacts.

### Lab-owned/domain views

- RcaState;
- ObservationRecords;
- HypothesisEvidenceLinks;
- Hypotheses/Predictions/Experiments;
- lab Rule/policy metadata;
- benchmark fixtures/scorers;
- Engineering Records.

### v0 persistence

One append-only run log plus artifact files may back all logical views:

```text
runs/<run_id>/manifest.json
events.jsonl
artifacts/
investigation-report.json
```

Do not create separate Evidence/Experiment/Trace databases without a demonstrated need.

## Observation / evidence semantics

```text
ToolResult / simulator result
 -> ObservationRecord

ObservationRecord
 + explicit relation to Hypothesis
 -> HypothesisEvidenceLink
```

Observation is not automatically evidence.

This supports separate measurement of:

- irrelevant queries;
- unused observations;
- valid/invalid evidence links;
- evidence quality.

## Rule / knowledge semantics

Canonical metadata:

```text
origin × validation × authority
```

K0–K4 is shorthand only.

- simulator/runtime constraints may carry HARD_GATE authority within their scope;
- reviewed lab policies are explicit `origin=POLICY` rules;
- simulation-validated relationships are usually ADVISORY/PLANNING, not automatic HARD_GATE;
- literature/Agent claims cannot self-promote authority.

## Tool layers

### Environment/read tools

```text
get_current_observation
get_history
get_variable_metadata
get_process_node / neighbors / upstream / downstream
get_related_measurements
get_related_actuators
get_safety_margins
snapshot / fork
check_scenario_capability
compile_process_deviation
run_rollout
```

Canonical `get_related_disturbances`/IDV answer enumeration is not in the default blind RCA allowlist.

### Tool Bridge

First RCA bridge set:

```text
response-feature extraction
trajectory comparison
cross-correlation / lag
optional upstream TEP detector baseline
```

Later concrete studies may add PCA/PLS, sensitivity, optimizer, or other libraries.

Bridge implementations are allowlisted/pinned, but runtime gates/budget/authority remain upstream of the bridge.

A bridge that internally runs simulator trials is SIMULATE and consumes explicit nested rollout/horizon/trial budget.

### Recovery/MUTATE tools

Later only:

```text
propose_intervention
validate_intervention
apply_validated_intervention
```

`apply_validated_intervention` is MUTATE and requires expected reference-state revision binding. It is disabled in blind RCA/AutoResearch by default.

## RCA workflow

```text
incident
 -> RcaState
 -> observations
 -> competing Hypotheses + Predictions
 -> explicit EvidenceLinks
 -> discriminating analysis/counterfactual ExperimentProposal
 -> frozen ExperimentRunSpec
 -> deterministic ExperimentResult / PredictionEvaluation
 -> Main Agent interpretation/update
 -> structured CausalClaim
 -> InvestigationReport
```

The research target is investigation behavior relative to strong deterministic baselines, not fault-label recall.

## Mandatory C0 baseline

First-family RCA includes evaluator-side:

```text
enumerate candidate causes
 -> compile/rollout
 -> deterministic trajectory/feature match
 -> best candidate or NO_ABNORMAL_CAUSE
```

If C0 solves a case cheaply/reliably, that is evidence an Agent is unnecessary for that case.

## Later HAZOP / Recovery / AutoResearch

Existing proposal specs define later task-family direction but do not block first RCA implementation.

### HAZOP

Must preserve supported/unsupported capability honesty; not a claim of formal plant HAZOP completion.

### Recovery

Simulate candidate strategies first. SIMULATE never mutates reference state; any reference application is MUTATE.

### AutoProcessResearch

Separate later task family with frozen evaluator/search surface, deterministic scoring, explicit nested simulation budget, append-only experiment history, and hidden evaluation.

It is not another orchestration-ablation row.

## Engineering records

Every completed RCA produces a typed InvestigationReport tied to final state revision/evidence/experiment/trace refs.

DecisionRecord and ExperimentRecord preserve meaningful decisions/experiments.

LessonLearned/Runbook/manual promotion is deferred. v0 records are archive-only and are not automatically retrieved into later benchmark contexts.

## Evaluation architecture

```text
fixture/hidden truth --------------------> evaluator
       |
       v
Agent-visible ContextProjection/tool policy
       |
       v
runtime + lab + tep-sim
       |
       v
run log / state / observations / experiments / report
       |
       +---------------------------------> evaluator
```

`evaluation-v0.md` is the only canonical comparison matrix.

- Capability axis excludes subagents.
- Orchestration axis holds tool exposure fixed and includes WorkBatch/subagent conditions.
- AutoResearch is separate task-family evaluation.

## Key invariants

- evaluator truth/candidate set never enters blind Agent-visible refs/tools;
- runtime/lab state boundary is TaskStateStore, not imports;
- Observation != Evidence;
- deterministic ExperimentResult != Agent interpretation;
- Tool Bridge != authorization layer;
- SIMULATE != MUTATE;
- compound simulator tools expose nested budget usage;
- conversation history is not canonical state;
- Engineering Records do not automatically become future context/rules;
- unsupported physics stays unsupported;
- failures/negative experiments remain traceable;
- rules/tools/scorers/context projections are versioned for reported runs.
