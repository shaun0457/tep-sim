# Architecture — Industrial Agent Runtime

## Purpose

Provide a domain-independent **control plane** for goal-driven agent work while separating model reasoning from execution authority.

The runtime must support simple local ReAct-style work and complex bounded Dynamic DAGs without hard-coding TEP or any other domain.

## Hybrid runtime model

```text
Task / Goal
   |
   v
Context / Information Refs
   |
   v
+--------------------------+
| Deterministic Coordinator|
+------------+-------------+
             |
             v
+--------------------------+
| Main Agent               |
| goal-driven reasoning    |
| local ReAct-style loop   |
+-----+----------------+---+
      |                |
 direct tool       Dynamic DAG proposal
      |            /    |     \
      |         tool  subtask  simulation
      |            \    |     /
      |              merge
      +----------------+
             |
             v
+--------------------------+
| Deterministic Verifier   |
+------------+-------------+
             |
             v
+--------------------------+
| Deterministic Executor   |
+------------+-------------+
             |
             v
 external tools / consumers / worlds
```

Coordinator, Executor, and Verifier are runtime components, not permanent LLM personas.

## Main responsibilities

### Main Agent

Open-ended reasoning:

- understand the goal/current structured state;
- choose tools/evidence;
- decide whether simple direct work is sufficient;
- propose Dynamic DAGs/subtasks when useful;
- integrate evidence;
- produce structured results/proposals;
- recommend semantic stopping.

### Coordinator

Deterministic orchestration:

- maintain task execution state;
- budget accounting;
- route model decisions;
- validate/schedule Dynamic DAG nodes;
- track dependencies/status;
- expose allowed tools;
- apply hard termination rules;
- coordinate checkpoint/resume through adapters.

### Executor

Deterministic dispatch:

- execute exact validated requests;
- enforce timeout/resource limits;
- bind request/result/artifact refs;
- never reinterpret intent or expand permissions.

### Verifier

Machine-checkable verification:

- schema/output validity;
- evidence/artifact ref existence;
- dependency completion;
- policy/rule-validator verdicts;
- provenance/budget consistency;
- stop-readiness structural requirements.

An optional LLM critic may be used as a normal bounded subtask, but its opinion is not execution authority.

## Core public contracts

### `Task`

```text
task_id
goal
context_refs
allowed_tools
budget
output_schema
parent_task_id?
metadata?
```

### `Budget`

```text
max_model_calls
max_tool_calls
max_subagents
max_subagent_depth
max_steps
max_plan_nodes?
max_plan_revisions?
max_parallel_width?
max_tokens/cost/time?
```

### `ToolSpec`

```text
name
description
input_schema
output_schema
side_effect_class
required_policy_tags
```

### `InvestigationPlan` / generic dynamic plan

Framework-neutral plan data:

```text
plan_id
objective
nodes[]
edges[]
plan_budget
completion_policy
revision
```

A plan is never executable solely because the model produced valid JSON; Coordinator validation is required.

### `Subtask`

Temporary child task with explicit goal, context refs, tools, budget, schema, and reason for delegation.

### `EvidenceBundle`

Compact child result/evidence refs returned to parent; child full transcript is not inherited by default.

### `TraceEvent`

Every significant transition records task/plan/node lineage, input/output summaries, budget delta, model/tool metadata, status/error, and artifact refs.

## Orchestration semantics

Reference flow:

```text
INIT
 -> LOAD_CONTEXT
 -> MAIN_AGENT_TURN
 -> PARSE/ROUTE
 -> {TOOL | SUBTASK | DYNAMIC_DAG | FINISH}
 -> GATES / PLAN VALIDATION
 -> EXECUTE READY WORK
 -> VERIFY
 -> UPDATE STATE/TRACE
 -> STOP CHECK
 -> repeat / finish / fail
```

Simple tasks should not pay the cost of Dynamic DAG construction.

## Dynamic DAG semantics

Coordinator validates:

- unique node IDs;
- acyclicity;
- valid dependencies;
- node/depth/parallel/revision budgets;
- authority monotonicity;
- schema/tool compatibility;
- hidden/evaluator ref isolation as supplied by consumer policy.

Independent nodes may run in parallel behind the same contract.

Plan revisions are append-only trace events; prior plans/results remain auditable.

## Deterministic gates

Generic runtime gate pipeline:

```text
schema
 -> tool allowlist
 -> budget/recursion/plan limits
 -> side-effect policy
 -> optional consumer/domain validator
 -> optional human approval
 -> Executor
```

Domain safety truth stays outside this repo.

## Information / context boundary

The runtime operates on refs and projections supplied by consumers.

It may provide a generic `ContextBroker` interface for:

- ref visibility;
- budget limits;
- projection hooks;
- caching/materialization;

but it does not decide domain relevance or encode process knowledge.

Conversation history is trace/context material, not guaranteed canonical application state.

## LangGraph boundary

Hybrid semantics are framework-neutral.

Recommended:

- core contracts/Coordinator/Executor/Verifier do not require LangGraph;
- `orchestration/langgraph_adapter.py` may map runtime/application state to LangGraph nodes/checkpoints;
- consumers such as `tep-agent-lab` may use the adapter for deterministic macro workflows, durable checkpointing, interrupts, and visualization;
- LangGraph message/state objects do not appear in public runtime contracts.

## Tool permissions

Side-effect classes:

```text
READ
COMPUTE
SIMULATE
PROPOSE
MUTATE
ADMIN
```

Authority can only narrow through delegation unless host policy explicitly grants otherwise.

## Memory

v0 does not implement global learned cross-run memory.

It supports Information Plane/evidence/artifact references supplied by consumers and durable per-task traces/checkpoints.

## Domain boundary

Core runtime contains no TEP variables/equations, HAZOP mappings, process rules, benchmark fixtures, or domain safety thresholds.

The same runtime should be able to support process simulation, manufacturing, software, or other labs through consumer-owned tools/state/schemas.

## Canonical specs

- `specs/runtime-v0.md`
- `specs/hybrid-orchestration-v0.md`
- `specs/deterministic-gates-v0.md`
- `specs/subagents-v0.md`
