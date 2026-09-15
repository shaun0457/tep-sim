# Hybrid Orchestration v0

Status: accepted direction / v0 contract proposal  
Owner repo: `industrial-agent-runtime`  
Primary consumer: `tep-agent-lab`

## Goal

Define a hybrid agent runtime that combines:

- a goal-driven Main Agent for open-ended investigation;
- deterministic coordination, execution, verification, budgets, and authority;
- local ReAct-style iteration for simple cases;
- bounded dynamically generated DAGs for complex investigations;
- framework-neutral public contracts, with LangGraph allowed as an orchestration adapter.

The design must preserve agent autonomy where reasoning is useful without turning deterministic engineering constraints into repeated LLM decisions.

## Core components

```text
Engineering Goal / Incident
          |
          v
+-------------------------+
| Deterministic Coordinator|
+------------+------------+
             |
             v
+-------------------------+
| Main Agent              |
| goal-driven reasoning   |
| local ReAct-style loop  |
+-----+---------------+---+
      |               |
 simple work       complex work
      |               |
      |               v
      |        Dynamic Investigation DAG
      |         /       |        \
      |      subtask  analysis  simulation
      |         \       |        /
      |          evidence merge
      |               |
      +---------------+
             |
             v
+-------------------------+
| Deterministic Verifier  |
+------------+------------+
             |
             v
+-------------------------+
| Deterministic Executor  |
+------------+------------+
             |
             v
        tools / world
```

Only the Main Agent is assumed to require an LLM. Coordinator, Executor, and Verifier are runtime components, not permanent agent personas.

## Responsibilities

### Main Agent

May:

- interpret the goal/current investigation state;
- choose the next useful action;
- query tools;
- form/update hypotheses;
- propose experiments;
- propose a dynamic DAG for independent/dependent work;
- spawn bounded ephemeral reasoning workers through the DAG/subtask interface;
- integrate evidence;
- decide whether evidence is sufficient to finish;
- produce structured conclusions/proposals.

It cannot directly execute unvalidated side effects or alter runtime policies.

### Coordinator

Deterministic control-plane component responsible for:

- owning canonical task/investigation execution state;
- maintaining budgets and step counters;
- routing Main Agent decisions;
- validating dynamic DAG structure;
- scheduling ready DAG nodes;
- tracking node dependencies/status;
- exposing only currently allowed tools/capabilities;
- freezing requests before approval/execution;
- deciding whether runtime termination conditions have been reached.

The Coordinator does not invent domain conclusions.

### Executor

Deterministic dispatcher responsible for:

- executing the exact validated tool/subtask/simulation request;
- enforcing timeout/resource limits;
- binding request/result IDs;
- recording provenance and artifacts;
- never broadening authority beyond the validated request.

The Executor does not re-plan or reinterpret the request.

### Verifier

Deterministic verifier responsible for checks that can be mechanically evaluated, including:

- output/schema validity;
- evidence/artifact reference existence;
- rule/policy compliance;
- DAG dependency completion;
- simulator/tool result provenance;
- ground-truth isolation policy;
- budget/accounting consistency;
- stop-condition inputs;
- exact constraint checks supplied by the consumer.

Semantic criticism that requires open-ended judgment MAY be requested as an ordinary bounded subtask, but it is evidence only and cannot override deterministic verification.

## Macro orchestration

The reference semantic flow is:

```text
INIT
 -> LOAD_CONTEXT_REFS
 -> MAIN_AGENT_TURN
 -> ROUTE_DECISION
      -> DIRECT_TOOL_REQUEST
      -> SUBTASK_REQUEST
      -> DYNAMIC_DAG_PROPOSAL
      -> FINISH_PROPOSAL
 -> GATE / VALIDATE
 -> EXECUTE_READY_WORK
 -> INGEST_RESULTS
 -> VERIFY
 -> UPDATE_STATE
 -> STOP_CHECK
      -> MAIN_AGENT_TURN
      -> FINISH
      -> FAIL / BUDGET_EXHAUSTED
```

This is the stable semantic contract. A framework implementation may represent stages as LangGraph nodes, an explicit state machine, or another executor without changing the public contracts.

## Local ReAct mode

For simple investigation steps, the Main Agent may iterate:

```text
reason over current structured state
 -> request one tool/action
 -> receive verified observation
 -> update state
 -> continue/finish
```

The transcript is not the source of truth. Important state is externalized into typed runtime/application state.

## Dynamic Investigation DAG

A complex investigation MAY be represented by a model-proposed `InvestigationPlan`.

Conceptual contract:

```text
plan_id
objective
nodes[]
edges[]
plan_budget
completion_policy
rationale_summary
```

### `PlanNode`

```text
node_id
type: TOOL | ANALYSIS | SIMULATION | SUBTASK | MERGE
goal
depends_on[]
input_refs[]
allowed_tools[]
budget
output_schema
status
```

### Deterministic DAG validation

Before scheduling, the Coordinator MUST check:

- unique node IDs;
- graph acyclicity;
- all dependency references exist;
- node count/depth/parallelism budgets;
- child tool authority does not exceed parent/task policy;
- node output/input schemas are compatible where declared;
- mutation nodes are rejected or routed through the side-effect gate;
- no evaluator-only/hidden-ground-truth ref enters agent-visible nodes.

Invalid plans are returned as structured denial/replan evidence.

## Dynamic replanning

A completed/failed node MAY cause the Main Agent to propose a revised plan. Replanning creates a new plan revision and preserves prior nodes/results in the trace; it does not silently rewrite history.

The Coordinator enforces a bounded number of plan revisions.

## Tool exposure

The Main Agent SHOULD NOT receive every installed tool on every turn.

The Coordinator/consumer may dynamically expose a subset based on:

- task policy;
- current macro stage;
- current investigation state;
- authority class;
- remaining budget;
- environment capabilities.

Tool discovery itself should be structured and traceable.

## LangGraph boundary

Recommended architecture:

- `industrial-agent-runtime` owns framework-neutral Coordinator/Executor/Verifier/state contracts;
- it MAY provide a `langgraph_adapter` that maps those contracts to graph state/nodes;
- `tep-agent-lab` may use LangGraph for its deterministic macro workflow and durable investigation state;
- no public contract exposes LangGraph-native message/state types.

This allows the TEP playground to benefit from graph orchestration without making every future domain depend on one framework.

## Invariants

- Main Agent reasons; deterministic runtime components hold execution authority.
- Coordinator/Executor/Verifier are not fixed LLM roles.
- A model-proposed DAG is data until deterministically validated.
- A child/subtask never gains more authority than the parent/task grants.
- Important investigation state exists outside conversation transcripts.
- Every plan revision, node execution, denial, verification, and merge is traceable.
- Simple tasks do not require building a dynamic DAG.

## Acceptance tests

1. Simple task completes through local Main Agent tool loop without a dynamic DAG.
2. Main Agent proposes a three-node parallel DAG; Coordinator validates and schedules it.
3. Cyclic DAG is rejected before execution.
4. Node requesting forbidden mutation authority is denied.
5. Failed node produces structured evidence and bounded replan rather than silent retry.
6. Verifier rejects a conclusion citing a nonexistent artifact/evidence ref.
7. Same validated DAG and deterministic tool results produce identical scheduling/verification trace.
8. Runtime contracts remain importable without LangGraph installed.
