# Runtime v0

Status: proposal  
Version: v0  
Owner repo: `industrial-agent-runtime`

## Goal

Provide a small, domain-independent execution harness for one main reasoning agent that can use tools, create bounded ephemeral subtasks, return structured results, and produce complete traces without embedding application-specific safety truth.

## v0 execution model

```text
Task
 |
 v
Context Builder
 |
 v
Main Agent
 |\
 | +--> optional bounded Subtask(s)
 |             |
 |<-- EvidenceBundle(s)
 |
 v
Structured Result or Tool Proposal
 |
 v
Generic deterministic gates
 |
 v
Tool adapter / consuming application
 |
 v
ToolResult
 |
 +--> continue bounded loop / finish
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

`goal` is natural language. Authority is not encoded in prose; allowed tools and policy are explicit fields.

### `Budget`

At minimum:

```text
max_model_calls
max_tool_calls
max_subagents
max_subagent_depth
max_total_tokens?
max_steps
```

Time/cost budgets MAY be added when reliable provider accounting exists.

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

A model-produced typed request. It is never assumed valid merely because parsing succeeded.

### `ToolResult`

```text
request_id
status
structured_output
artifact_refs?
error?
provenance
```

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

Each meaningful transition MUST record:

```text
event_id
task_id
parent_task_id?
type
timestamp
model/provider metadata?
input summary
output summary
budget delta
latency/cost when known
status/error
```

## Provider abstraction

Core runtime MUST depend on an internal model interface rather than one provider SDK.

Conceptual interface:

```text
generate(messages/context, tool_specs, output_schema, limits) -> ModelTurn
```

v0 MUST support a deterministic fake provider for tests before a real provider integration is required.

Provider-specific message objects MUST NOT appear in public runtime contracts.

## Main-agent authority

The main agent may:

- request read/compute/simulate tools allowed by the task;
- create bounded subtasks under the subagent policy;
- consume child `EvidenceBundle`s;
- produce the task's final structured output;
- produce proposals for side-effecting operations.

The main agent MUST NOT bypass deterministic execution gates.

## Runtime loop

The executor SHOULD remain a small explicit Python state machine in v0:

```text
BUILD_CONTEXT
  -> MODEL_TURN
  -> PARSE
  -> {TOOL_GATE | SUBTASK_GATE | FINISH | FAIL}
  -> EXECUTE/WAIT
  -> MODEL_TURN ...
```

Every loop is bounded by `Budget`.

## Failure behavior

The runtime MUST fail closed for malformed structured outputs, unknown tools, exhausted budget, invalid subtask requests, or denied side effects.

A denial is a normal structured event and may be returned to the main agent for replanning if budget remains.

## Context discipline

The runtime SHOULD pass references/artifacts instead of automatically concatenating large histories. Tool adapters and consumer applications are responsible for compact domain projections.

Child transcripts are not automatically copied into the parent context; only child structured results are returned.

## Persistence

v0 does not require durable cross-run memory. It requires trace persistence for the current task/run.

## LangGraph boundary

LangGraph is not required for v0. Add an adapter only after a concrete consumer requires durable checkpoints, human interrupts, resumable execution, or persistent branching.

## Invariants

- No fixed domain roles are hard-coded into core runtime.
- No TEP/process-specific variable or safety rule exists in core runtime.
- Every tool call is gated before execution.
- Every subtask is bounded and trace-linked to its parent.
- Every task terminates by success, explicit failure, cancellation, or budget exhaustion.
- Tests can run without network/model access using a fake provider.

## Acceptance tests

1. Fake provider completes a typed no-tool task.
2. Fake provider requests an allowed read tool and consumes a typed result.
3. Unknown/denied tool is rejected without execution.
4. Budget exhaustion deterministically stops the loop.
5. Main agent spawns one valid child and receives only its `EvidenceBundle`.
6. Malformed child or model output becomes a traceable failure/denial, not an implicit retry loop.
7. Core package tests import no TEP/domain module.

## Non-goals

v0 does not implement global memory, autonomous agent hiring, permanent specialist identities, unrestricted peer-to-peer messaging, arbitrary recursive swarms, or application-specific safety rules.
