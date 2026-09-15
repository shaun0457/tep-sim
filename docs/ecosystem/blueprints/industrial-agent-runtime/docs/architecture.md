# Architecture

## Runtime model

The runtime separates reasoning from authority.

```text
Task
 |
 v
Context Builder
 |
 v
Main Agent
 |\
 | +--> Subtask Planner --> ephemeral Subagent(s)
 |                         |
 |<------ typed evidence --+
 |
 v
Typed Proposal / Answer
 |
 +--> if side effect --> deterministic gate --> tool
 |
 v
Result + trace
```

## Core contracts

### Task

```text
task_id
goal
context_refs
allowed_tools
budget
output_schema
parent_task_id?
```

### Budget

```text
max_model_calls
max_tool_calls
max_subagents
max_depth
max_output_tokens
optional deadline/step limit
```

### Subtask

A subtask is a narrow unit of independent work. It should have an expected output small enough for the parent agent to consume without inheriting the entire child transcript.

### ToolSpec

```text
name
description
input_schema
output_schema
side_effect_level
permission_policy
```

### ToolProposal

For mutating/high-impact tools, the model emits a proposal which can be validated before execution.

### TraceEvent

Every model/subagent/tool transition records:

```text
event_id
task_id
parent_task_id
type
timestamp/model metadata
input summary
output summary
cost/latency
status/error
```

## Subagent policy

The main agent may spawn subagents only when one of these is true:

- the work is independently parallelizable;
- a narrow specialist context materially reduces main-agent context;
- independent hypothesis testing is useful;
- a verifier/critic provides measurable benefit.

Do not spawn a subagent merely to mirror an organizational job title.

## Orchestration

### MVP

Use a small Python executor/state machine.

### Add LangGraph when needed

Introduce the adapter for:

- durable checkpoints;
- human interrupts;
- multi-step resumable tasks;
- bounded branching with persistent state;
- production tracing tied to graph state.

Do not put provider-specific messages or LangGraph state objects into public contracts.

## Tool permissions

Tools are classified by side-effect level, for example:

```text
READ      observe/query
COMPUTE   local deterministic computation
SIMULATE  isolated environment fork/rollout
PROPOSE   produce a candidate mutation
MUTATE    change external state
```

The consuming application supplies policy for which levels require deterministic validation or human approval.

## Memory

Do not build a global memory system in the MVP.

Support references to external memory/evidence providers through tools. Add persistence only after concrete tasks demonstrate a need for cross-run agent memory.

## Domain boundary

The runtime should be able to power TEP, manufacturing, software, or other agent labs without code changes to core orchestration. Domain semantics enter only through task context, tool adapters, schemas owned by the consumer, and optional external knowledge services.
