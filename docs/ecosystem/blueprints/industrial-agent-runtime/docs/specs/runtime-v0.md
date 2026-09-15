# Runtime v0

Status: accepted base contracts / implemented later under Design Freeze  
Version: v0  
Owner repo: `industrial-agent-runtime`

## Goal

Define the domain-independent base contracts used by the Hybrid runtime: one goal-driven Main Agent, deterministic Coordinator/Executor/Verifier, typed tools, bounded Dynamic DAGs/subtasks, structured results, and complete traces without embedding application-specific safety truth.

The detailed orchestration contract is in `hybrid-orchestration-v0.md`.

## Runtime layers

```text
Task + information refs
        |
        v
Coordinator
        |
        v
Main Agent
  direct/local ReAct
  or Dynamic DAG proposal
        |
        v
Verifier / deterministic gates
        |
        v
Executor
        |
        v
Tool adapter / consuming application
```

## Core contracts

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

`goal` is natural language. Authority is encoded in explicit tool/policy/budget fields, not prose.

### `Budget`

At minimum:

```text
max_model_calls
max_tool_calls
max_subagents
max_subagent_depth
max_steps
max_plan_nodes?
max_plan_revisions?
max_parallel_width?
max_total_tokens?
```

Consumer/application budgets may additionally include simulation rollouts/horizon, cost, and time.

### `ToolSpec`

```text
name
description
input_schema
output_schema
side_effect_class
required_policy_tags
```

### `ToolCallRequest`

Model-produced typed request. Parsing success never implies execution authority.

### `ToolResult`

```text
request_id
status
structured_output
artifact_refs?
error?
provenance
```

### `Plan` / `PlanNode`

Dynamic-plan data structures are framework-neutral and defined in `hybrid-orchestration-v0.md`.

### `RuntimeResult`

```text
task_id
status
structured_output
trace_ref
budget_usage
warnings/errors
```

### `TraceEvent`

Every meaningful transition records:

```text
event_id
task_id
parent_task_id?
plan/node refs?
type
timestamp
model/provider/tool metadata?
input summary
output summary
budget delta
latency/cost when known
status/error
artifact refs?
```

## Provider abstraction

Core runtime depends on an internal model interface rather than one provider SDK.

Conceptually:

```text
generate(context_projection, tool_specs, output_schema, limits) -> ModelTurn
```

A deterministic fake provider is mandatory for tests before a real provider is required.

Provider-specific message objects must not appear in public runtime contracts.

## Main Agent authority

May:

- request allowed READ/COMPUTE/SIMULATE tools;
- propose Dynamic DAGs;
- create bounded subtasks;
- consume EvidenceBundles;
- produce final structured output;
- produce side-effect proposals.

Cannot:

- bypass Coordinator/Verifier/gates;
- execute tools directly;
- change task/tool/budget policy;
- grant children extra authority;
- directly mutate consumer reference state.

## Coordinator / Executor / Verifier

Detailed responsibilities are defined in `hybrid-orchestration-v0.md`.

Base invariant:

> model reasoning proposes; deterministic runtime validates, schedules, executes, verifies, accounts, and traces.

## Simple reference loop

A minimal explicit loop remains supported as the simplest/reference path:

```text
LOAD_CONTEXT
 -> MAIN_AGENT_TURN
 -> PARSE/ROUTE
 -> GATE
 -> EXECUTE
 -> VERIFY
 -> UPDATE
 -> STOP_CHECK
 -> repeat/finish
```

It is not the complete architecture for complex investigations; Dynamic DAG semantics sit alongside it.

## Failure behavior

Fail closed for malformed output, unknown tools, invalid/cyclic plan, exhausted budget, invalid subtask request, denied authority, missing evidence refs, or consumer validator denial.

A denial/failure becomes a structured trace event and may be returned for bounded replanning if policy/budget allow.

## Context / Information Plane discipline

Runtime passes references/projections instead of concatenating full histories. Consumer applications resolve domain Information Plane refs and produce compact projections.

Child transcripts are not copied automatically into parent context; only structured results/evidence refs are returned.

Conversation transcript is not assumed to be canonical application state.

## Persistence

v0 requires complete per-task/run trace and optional checkpoint serialization. It does not require learned cross-run Agent memory.

## LangGraph boundary

Hybrid semantics/public contracts are framework-neutral.

An accepted LangGraph adapter may provide macro-graph execution, checkpoints, interrupts, and graph observability for consumers such as `tep-agent-lab`.

The package must remain testable/usable without requiring LangGraph-native public types and should retain a simple reference executor for unit tests/baselines.

## Invariants

- No fixed domain roles in core runtime.
- No TEP/process-specific variable/rule/safety truth in core runtime.
- Coordinator/Executor/Verifier are deterministic components by default.
- Every tool/plan/subtask is validated before execution.
- Dynamic DAGs are data proposals until accepted by Coordinator policy.
- Every subtask is bounded/trace-linked.
- Every task terminates by success, explicit failure, cancellation, hard stop, or budget exhaustion.
- Tests run without network/model access via fake provider.

## Acceptance tests

1. Fake provider completes a typed no-tool task.
2. Fake provider requests an allowed read tool and consumes a typed result.
3. Unknown/denied tool is rejected without execution.
4. Budget exhaustion deterministically stops the loop.
5. Valid simple path completes without Dynamic DAG.
6. Valid bounded plan/DAG can be represented/routed; cyclic/over-budget plan is rejected.
7. Main Agent spawns one valid child and receives only its EvidenceBundle.
8. Verifier rejects a final result referencing nonexistent evidence/artifact.
9. Core package tests import no TEP/domain module and require no LangGraph-native public contract.

## Non-goals

v0 does not implement global learned memory, autonomous hiring/retiring organizations, permanent specialist identities, unrestricted peer-to-peer chat, arbitrary recursive swarms, application-specific safety truth, or arbitrary agent shell/code execution as the normal tool model.
