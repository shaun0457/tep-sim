# industrial-agent-runtime

Domain-independent control plane for one goal-driven Main Agent using typed tools, deterministic authority gates, consumer-owned state adapters, dependency-aware work, and bounded ephemeral subagents.

## Purpose

Provide reusable Agent runtime mechanics without embedding TEP, process safety, RCA/HAZOP semantics, or scientific-library implementations.

## Core shape

```text
consumer TaskStateStore.project
        |
        v
Main Agent
        |
 ToolCall / WorkBatch / FinishProposal
        |
        v
G0-G3 + consumer.validate_request
        |
        v
Executor
        |
        v
post-execution verify_result
        |
        v
TaskStateStore.apply
```

Only the Main Agent is assumed to require an LLM.

## Runtime owns

- `InformationRef`;
- `Task` / `Budget` including extra resource dimensions;
- `ToolSpec` / request/result contracts;
- generic `TaskStatus` / `StateDelta` / `ContextProjection` / `TaskStateStore` protocol;
- dependency-aware `WorkBatch` (`TOOL | SUBTASK` + `depends_on`);
- deterministic pre-execution gates;
- deterministic Executor/dispatcher;
- deterministic post-execution result verification;
- ephemeral `Subtask` / `SubtaskResult`;
- provider abstraction + fake provider;
- exact model-turn tracing/resource accounting.

## Runtime does not own

- TEP variables/equations/topology;
- application-specific Investigation/RCA state fields;
- HAZOP/recovery policies;
- domain safety/actuator limits;
- DEXPI parsing;
- scientific Tool Bridge implementations;
- benchmark ground truth/scorers;
- knowledge/promotion workflows.

## Critical invariants

- model proposes; deterministic code authorizes and executes;
- pre-execution validation != post-execution verification;
- runtime never imports domain state types;
- child authority never exceeds task/parent authority;
- SIMULATE never mutates reference state;
- compound tools cannot hide nested budget consumption;
- model turns reference exact immutable ContextProjection artifacts;
- conversation history is not canonical application state;
- no arbitrary Agent Python/shell as the normal tool model.

## Dependency-aware work

v0 deliberately does not implement a general mutable Dynamic DAG engine.

```text
WorkBatch
  items:
    TOOL | SUBTASK
    depends_on[]
```

Coordinator validates acyclicity/budget/authority and schedules ready items. Failed required dependency causes dependents to be skipped. Merge/open-ended integration is the next Main Agent turn.

Full graph replanning/cancellation is later research.

## Framework boundary

Public contracts are serializable/framework-neutral.

- LangGraph: not a v0 dependency; consider only after a concrete checkpoint/resume/interrupt need.
- MCP: not a runtime dependency; may later be one external Tool Provider protocol behind ordinary ToolSpec/gates.

## Suggested package direction

```text
src/industrial_agent_runtime/
  contracts/
    refs.py
    task.py
    state.py
    tool.py
    budget.py
    work.py
    trace.py
  runtime/
    coordinator.py
    executor.py
    verifier.py
  gates/
    schema.py
    permission.py
    budget.py
    side_effect.py
  models/
    base.py
    fake.py
    providers/
  tracing/
    recorder.py

tests/
docs/
AGENTS.md
```

Component names are implementation organization, not separate services/agents.

## First consumer

`tep-agent-lab` implements TaskStateStore for RcaState, registers TEP/Tool Bridge adapters, and supplies consumer `validate_request` / `verify_result` domain logic.

## Documentation

Canonical contracts:

- `docs/specs/runtime-v0.md`
- `docs/specs/hybrid-orchestration-v0.md`
- `docs/specs/deterministic-gates-v0.md`
- `docs/specs/subagents-v0.md`

Rationale/history:

- `docs/decisions/ADR-002-hybrid-orchestration.md` — current accepted architecture decision
- `docs/decisions/ADR-001-minimal-explicit-executor.md` — superseded historical context

Research/implementation unknowns belong in `docs/open-questions.md`.
