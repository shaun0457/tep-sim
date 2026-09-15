# Architecture

## Integration boundary

```text
                    optional knowledge service
                             |
                             v
                    evidence tool adapter
                             |
                             v
industrial-agent-runtime -> tep-agent-lab -> tep-sim
          |                    |              |
      agent mechanics      domain logic    environment truth
```

The lab owns adapters and workflows that translate process-engineering goals into environment/tool operations.

## Tool surface

Initial read-only tools:

```text
get_current_observation
get_history(window, variables)
get_variable_metadata
get_process_topology
get_safety_margins
```

Experiment tools:

```text
snapshot_environment
fork_environment
check_scenario_capability
compile_deviation
run_rollout
compare_rollouts
```

Mutation/recovery tools remain proposal-gated:

```text
propose_intervention
validate_intervention
apply_intervention   # only after deterministic approval
```

## HAZOP workflow

```text
select node
   |
select parameter
   |
apply guide word
   |
main agent forms candidate deviation
   |
capability/compile check ---------- unsupported --> record gap
   |
   v
fork + rollout
   |
process/safety evaluation
   |
agent interprets evidence
   |
structured HAZOP finding
   |
independent deterministic/report validator
```

The agent may spawn workers to explore independent node/deviation combinations, but experiment-budget gates cap combinatorial expansion.

## RCA workflow

```text
incident
   |
compact telemetry + topology
   |
rank hypotheses
   |
choose discriminating counterfactual(s)
   |
fork/rollout
   |
compare predicted vs observed behavior
   |
update diagnosis
   |
final ranked result
```

The key research value is not whether an LLM can name a fault from memory, but whether it can **design and use experiments** efficiently.

## Recovery workflow

Candidate recovery strategies are evaluated in cloned branches before touching the reference branch when the task allows.

```text
state S
 |\
 | +-> strategy A -> rollout -> score
 +---> strategy B -> rollout -> score
 +---> no action  -> rollout -> score
             |
             v
       recommendation
             |
       deterministic gate
```

## Evaluation architecture

Evaluation code receives ground truth directly from scenario fixtures, not from agent output.

```text
scenario fixture
  |             \
  |              -> scorer
  v
agent-visible projection -> runtime -> result -> scorer
```

This prevents accidental ground-truth leakage.

## Baselines

At minimum compare:

1. deterministic detector/controller only;
2. single main agent without subagents;
3. main agent + dynamic subagents;
4. main agent + counterfactual simulation tools;
5. optional knowledge-service augmentation.

Ablations should isolate which capability creates the gain.
