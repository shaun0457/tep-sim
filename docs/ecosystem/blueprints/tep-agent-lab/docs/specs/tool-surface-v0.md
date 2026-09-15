# TEP Agent Tool Surface v0

Status: proposal  
Version: v0  
Owner repo: `tep-agent-lab`  
Depends on: `tep-sim`, `industrial-agent-runtime`

## Goal

Expose a narrow, typed tool surface that lets agents investigate and experiment with the TEP environment without giving them raw simulator internals or unrestricted mutation authority.

## Tool groups

### Read tools

```text
get_current_observation()
get_history(window, variables)
get_variable_metadata(ids)
get_process_node(node_id)
get_neighbors(node_id, direction?)
get_related_measurements(node_id)
get_related_actuators(node_id)
get_related_disturbances(node_id)
get_safety_margins()
```

All read tools MUST return compact structured results. Large time series SHOULD be artifact-backed or summarized numerically unless raw data is explicitly requested within budget.

### Simulation tools

```text
snapshot_environment()
fork_environment(snapshot_id)
check_scenario_capability(scenario)
compile_process_deviation(deviation)
run_rollout(branch_id, horizon, interventions?)
compare_rollouts(rollout_refs, metrics?)
```

Simulation tools operate on isolated branches. They MUST NOT mutate the reference branch unless the operation is explicitly a recovery application step.

### Proposal/recovery tools

```text
propose_intervention(proposal)
validate_intervention(proposal, reference_state_ref)
apply_validated_intervention(validation_token)
```

`apply_validated_intervention` is the only initial path allowed to change the reference branch and MUST require prior deterministic validation.

## Tool authority classes

Map tool specs to generic runtime classes:

```text
READ       -> observation/topology/history queries
SIMULATE   -> snapshot/fork/rollout/compare
PROPOSE    -> candidate intervention generation
MUTATE     -> apply validated intervention to reference branch
```

## Domain gate layering

For a reference-world intervention:

```text
agent ToolCallRequest
   -> runtime schema/allowlist/budget gate
   -> lab experiment-policy gate
   -> tep-sim capability/bounds/control-mode validation
   -> optional human approval
   -> apply exact validated intervention
```

The lab policy gate may enforce experiment-specific rules such as allowed actuators, max intervention magnitude, cooldown, maximum number of reference-world actions, or "simulate before apply" requirements.

## Data minimization

The agent SHOULD query topology/history on demand rather than receiving all 41 XMEAS, all 12 XMV, full DEXPI graph, and long raw history at task start.

Initial incident context should contain only:

- task/incident identity;
- current timestamp/state summary;
- top abnormal signals or trigger evidence;
- minimal local topology seeds;
- available tool names and budgets;
- safety state;
- prior action summary if any.

## Ground-truth isolation

Tools available to the agent MUST NOT expose hidden scenario truth such as injected fault ID unless an experiment explicitly studies non-blind diagnosis.

Evaluator-only APIs/fixtures must remain separate from agent tool registration.

## Artifact refs

Tool results that produce dense trajectories SHOULD return:

```text
summary
schema
shape
artifact_ref
preview/selected features
```

not full embedded arrays.

## Failure behavior

Tool results MUST distinguish:

```text
INVALID_REQUEST
UNSUPPORTED_CAPABILITY
POLICY_DENIED
SIMULATION_FAILED
ARTIFACT_ERROR
OK
```

An unsupported request is evidence for replanning; it is not a reason to fabricate a simulated outcome.

## Acceptance tests

1. Query reactor topology and retrieve bound measurements/actuators without exposing full graph.
2. Run one isolated fork/rollout and prove reference state is unchanged.
3. Attempt hidden-fault lookup through registered agent tools and verify it is unavailable.
4. Attempt direct reference mutation without validation and verify deterministic denial.
5. Validate/apply one permitted intervention through the complete layered gate path.
6. Return large rollout data through artifact refs rather than model-context embedding.
