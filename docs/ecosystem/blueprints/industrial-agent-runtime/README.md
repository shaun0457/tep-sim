# industrial-agent-runtime

Domain-independent runtime for one main reasoning agent that can use typed tools and dynamically create bounded ephemeral subagents while deterministic gates retain execution authority.

## Purpose

Industrial agent experiments should not embed orchestration inside each simulator/domain repository. This runtime provides reusable agent mechanics while remaining ignorant of TEP, XMEAS/XMV/IDV, HAZOP mappings, or process-safety truth.

## Core principles

- one main agent by default;
- subagents are temporary tasks, not permanent job titles;
- child context/tool/budget/output contracts are explicit;
- v0 defaults to depth 1, max 3 children, no child mutation authority;
- deterministic code handles schema validation, permissions, budgets, recursion limits, and side-effect gates;
- model outputs are requests/proposals, not execution authority;
- context is assembled per task and large artifacts are referenced rather than copied blindly;
- every model/tool/subagent/gate transition is traceable;
- tests use a deterministic fake model provider;
- LangGraph is optional and added only when durable state/interrupt requirements justify it.

## Conceptual runtime

```text
Task
 |
 v
Context Builder
 |
 v
Main Agent
 |\
 | +--> bounded Subtask(s)
 |             |
 |<-- EvidenceBundle(s)
 |
 v
Tool request / structured result
 |
 v
schema -> allowlist -> budget -> side-effect gate
 |
 v
consumer validator / external tool
```

## Repository owns

- model-provider abstraction;
- main-agent executor;
- ephemeral-subagent executor;
- task/tool/budget/result contracts;
- context references and context budgets;
- tool registry/permissions;
- deterministic generic gates;
- traces/observability;
- optional approval/checkpoint adapters.

## Repository does not own

- TEP variables/equations/topology;
- application-specific safety limits;
- HAZOP/RCA/recovery workflows;
- P&ID/DEXPI parsing;
- domain knowledge bases;
- experiment ground truth/evaluators.

## Suggested package layout

```text
src/industrial_agent_runtime/
  contracts/
    task.py
    result.py
    tool.py
    budget.py
    trace.py
  runtime/
    executor.py
    context.py
    subtask.py
  gates/
    schema.py
    permission.py
    budget.py
    side_effect.py
  tools/
    registry.py
  models/
    base.py
    fake.py
    providers/
  tracing/
    recorder.py
  orchestration/
    langgraph_adapter.py   # optional/later

tests/
docs/
AGENTS.md
```

## Minimal API direction

```python
runtime = AgentRuntime(model=model, tools=tools, policy=policy)

result = runtime.run(
    Task(
        goal="Investigate the incident and return ranked hypotheses",
        context_refs=[...],
        allowed_tools=[...],
        budget=Budget(
            max_model_calls=8,
            max_tool_calls=20,
            max_subagents=3,
            max_subagent_depth=1,
            max_steps=30,
        ),
        output_schema=DiagnosisResult,
    )
)
```

The runtime must not know what a reactor, pump, CNC machine, or TEP fault is.

## First consumer

`tep-agent-lab` is the first serious consumer and supplies TEP-specific tool adapters, policies, and output schemas.

## Documentation

- `AGENTS.md` — minimal coding-agent constraints
- `docs/architecture.md` — runtime boundary
- `docs/roadmap.md` — implementation order
- `docs/specs/runtime-v0.md` — execution contract
- `docs/specs/subagents-v0.md` — ephemeral-subagent contract
- `docs/specs/deterministic-gates-v0.md` — generic gate model
- `docs/open-questions.md` — unresolved design choices
- `docs/decisions/` — ADRs
