# Architecture — TEP Agent Lab

## Purpose

`tep-agent-lab` is the integration/research layer where the generic Agent Runtime operates against the trusted TEP world. It owns TEP-specific investigation state, tools, rules, experiments, benchmarks, and evaluation.

## System boundary

```text
                 optional knowledge service
                          |
                          v
industrial-agent-runtime |  generic control plane
  Coordinator / Executor / Verifier / Main Agent
                          |
                          v
+------------------------------------------------+
|                 tep-agent-lab                  |
|                                                |
|  Investigation State                          |
|  Hypotheses / Experiments                      |
|  Rule Registry (K2/K3)                         |
|  Evidence Store / Experiment Ledger            |
|  Tool Bridge / domain policy                   |
|  RCA / HAZOP / Recovery / AutoResearch         |
|  evaluation / benchmark fixtures               |
+----------------------+-------------------------+
                       |
                       v
                  `tep-sim`
        ProcessGraph / K0-K1 truth / dynamics
        snapshot / fork / rollout / capability
```

`manufacturing-kg-agent` may later provide read-only evidence. It is optional.

## Hybrid orchestration

The lab consumes `hybrid-orchestration-v0.md`.

```text
Incident / Engineering Goal
        |
        v
Deterministic Macro Workflow
        |
        v
Main Investigator (local ReAct-style reasoning)
        |
        +-- simple request --> typed tool/subtask
        |
        +-- complex request --> Dynamic Investigation DAG
                                  /      |      \
                              analysis  sim   subtask
                                  \      |      /
                                   evidence merge
        |
        v
Deterministic verification / state update / stop check
```

Main Agent is the reasoning authority. Coordinator, Executor, and Verifier are deterministic runtime components by default.

The macro workflow may be implemented through a LangGraph adapter for state/checkpointing, but the domain/public contracts remain framework-neutral.

## Information Plane

The lab participates in the program Information Plane.

### Environment-owned information

From `tep-sim`:

- ProcessGraph / DEXPI semantics;
- VariableRegistry;
- capabilities;
- K0 simulator truth;
- K1 hard/formal environment constraints;
- snapshots/rollouts/safety artifacts.

### Lab-owned information

- InvestigationState;
- hypotheses/evidence links;
- Experiment Ledger;
- K2 validated engineering relationships;
- K3 document/literature heuristics;
- tool-analysis artifacts;
- benchmark fixtures/scoring configs;
- AutoResearch state.

K4 Agent hypotheses remain investigation state, not persistent rules.

## Tool layers

### Environment tools

```text
get_current_observation
get_history
get_variable_metadata
get_process_node / neighbors / upstream / downstream
get_safety_margins
snapshot / fork
check_scenario_capability
compile_process_deviation
run_rollout
compare_rollouts
```

### Tool Bridge analysis/research tools

Examples:

```text
summary statistics
cross-correlation / lag
response features
PCA / PLS baseline analysis
sensitivity analysis
bounded parameter optimization
graph algorithms
```

Bridge implementations are allowlisted/pinned. No arbitrary model-requested Python/import execution is part of the normal path.

### Recovery tools

```text
propose_intervention
validate_intervention
simulate_intervention
apply_validated_intervention   # only when benchmark/policy enables it
```

## Rule / knowledge authority

```text
K0 simulator/runtime truth             -> environment hard authority
K1 formal physical/safety invariant    -> reviewed hard authority
K2 simulation-validated relationship   -> advisory/score/warn by default
K3 paper/document heuristic            -> prior/annotation
K4 Agent hypothesis                    -> investigation only
```

Paper/LLM extraction cannot directly create hard gates.

## RCA workflow

```text
incident
 -> InvestigationState
 -> initial evidence/topology
 -> hypotheses
 -> analysis/query tools
 -> discriminating ExperimentProposal(s)
 -> isolated fork/rollout or Tool Bridge analysis
 -> deterministic ExperimentResult
 -> Main Agent interpretation
 -> hypothesis update
 -> semantic stop check
 -> evidence-backed diagnosis
```

The research target is investigation quality, not fault-label recall.

## HAZOP workflow

```text
node + parameter + guide word
 -> candidate deviation/cause hypotheses
 -> Rule/Capability lookup
 -> deterministic scenario compilation
 -> isolated rollout(s)
 -> safety/process result
 -> evidence-backed finding
 -> unsupported domains explicitly retained
```

The lab supports HAZOP research/decision support; it does not claim to replace formal plant HAZOP review.

## Recovery workflow

```text
abnormal state
 -> candidate strategies
 -> isolated fork comparisons
 -> deterministic metric vector
 -> Main Agent recommendation
 -> domain/generic gates
 -> optional reference application
 -> verification
```

Default is simulate-before-reference-mutation.

## AutoProcessResearch mode

AutoResearch is a separate lab mode, not the normal incident loop.

```text
frozen ResearchSpec/evaluator
 -> baseline
 -> Agent hypothesis/change
 -> bounded experiment/search
 -> deterministic score
 -> append Experiment Ledger
 -> keep/reject/neutral
 -> repeat until deterministic stop
 -> hidden evaluation
```

Numeric optimization should use deterministic search/optimizer tools where appropriate; the Agent chooses mechanism/search space/objective and interprets outcomes.

## Evaluation architecture

```text
scenario fixture -----------------> evaluator/scorer
     |
     v
agent-visible projection
     |
Hybrid runtime + lab tools
     |
Investigation trace / result ------> evaluator/scorer
```

Evaluation separates:

- environment validity;
- runtime/gate behavior;
- final task quality;
- scientific/investigation behavior;
- cost/efficiency;
- safety/authority behavior.

Two independent ablation axes are used:

1. capabilities/tools available;
2. orchestration architecture (one-shot/ReAct/fixed DAG/Hybrid/Dynamic DAG/subagents).

## Key invariants

- evaluator truth never enters Agent-visible Information Plane refs;
- Agent text never directly mutates TEP reference state;
- conversation history is not canonical investigation state;
- deterministic results are separated from model interpretation;
- Dynamic DAG is model-proposed data until Coordinator validation;
- unsupported physics remains unsupported;
- failures/negative experiments remain traceable;
- rules/tools/scorers are version-pinned per reported run.
