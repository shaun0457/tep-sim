# Roadmap

## Phase 0 — Contracts before models

Implement Pydantic/dataclass contracts for:

- `Task`;
- `Budget`;
- `ToolSpec`;
- `ToolResult`;
- `Subtask`;
- `RuntimeResult`;
- `TraceEvent`.

Use fake models only.

## Phase 1 — Single main agent

Implement:

- provider abstraction;
- one main-agent executor;
- structured output parsing;
- read-only tool registry;
- trace recording;
- budget enforcement.

Exit criterion: one deterministic fake-model test and one real-provider smoke test complete the same typed task.

## Phase 2 — Side-effect gates

Add:

- tool side-effect classes;
- proposal/execute separation;
- schema/permission gate;
- rejection events;
- fail-closed behavior.

## Phase 3 — Ephemeral subagents

Add:

- subtask creation;
- bounded spawn count/depth;
- isolated context slices;
- structured child result;
- parallel independent subtasks where safe;
- parent-child trace links.

Exit criterion: parent can request two independent analyses and combine only their compact results.

## Phase 4 — Context discipline

Add:

- context-reference abstraction;
- result compaction;
- configurable context budgets;
- caching of static tool/schema metadata;
- token/cost/latency metrics.

## Phase 5 — Optional LangGraph adapter

Only after a consuming workflow needs persistence/interrupt/recovery, implement:

- state mapping;
- checkpoint adapter;
- human interrupt hook;
- resumable bounded retry;
- graph trace correlation.

Core runtime remains usable without LangGraph.

## Phase 6 — First domain integration

Integrate from `tep-agent-lab`, not in this repository.

Required proof:

- runtime can use environment tools without importing TEP code;
- environment mutation still passes external deterministic gates;
- subagent context contains only task-relevant process evidence;
- traces report model calls, subagents, tool calls, cost, latency, and outcome.
