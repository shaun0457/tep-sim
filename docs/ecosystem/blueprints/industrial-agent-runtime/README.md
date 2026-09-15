# industrial-agent-runtime

Domain-independent runtime for a main reasoning agent that can dynamically spawn bounded ephemeral subagents, use typed tools, and interact with external environments through deterministic side-effect gates.

## Why this repository exists

Industrial agent experiments should not embed orchestration into each simulator/domain project. This runtime provides reusable agent mechanics while remaining ignorant of TEP, P&IDs, manufacturing equipment, or any specific plant.

## Core principles

- one main agent by default;
- subagents are created for tasks, not permanent job titles;
- subagents have explicit task, context, tools, budget, deadline/step limit, and output schema;
- deterministic code handles validation, budgets, permissions, retries, and side-effect gates;
- model outputs are structured proposals, not direct environment mutations;
- context is assembled per task rather than accumulated indefinitely;
- every model/tool call is traceable and measurable;
- LangGraph is optional orchestration, not a requirement for every workflow.

## Conceptual runtime

```text
User / Lab Task
      |
      v
Main Agent
      |
      +-- needs independent work? --> spawn Subtask(s)
      |                                |
      |                         ephemeral subagents
      |                                |
      +<---------- structured results--+
      |
      v
Tool / Environment Proposal
      |
      v
Deterministic permission + schema + budget gate
      |
      v
External tool/environment
```

## Repository owns

- model-provider interface;
- main-agent executor;
- dynamic subagent executor;
- tool registry and permissions;
- task contracts;
- context builder;
- structured result contracts;
- budgets (tokens, calls, wall/step limits where applicable);
- tracing and observability;
- deterministic side-effect gates;
- optional graph/checkpoint adapter.

## Repository does not own

- TEP variables/equations;
- HAZOP guide-word mappings for a specific plant;
- P&ID extraction;
- process-safety truth;
- domain knowledge bases;
- experiment-specific evaluation datasets.

## Suggested package layout

```text
src/industrial_agent_runtime/
  contracts/
    task.py
    result.py
    tool.py
    budget.py
  runtime/
    main_agent.py
    subagent.py
    executor.py
    context.py
  tools/
    registry.py
    permissions.py
  gates/
    side_effect.py
    schema.py
    budget.py
  models/
    base.py
    fake.py
    providers/
  orchestration/
    simple.py
    langgraph_adapter.py
  tracing/
    events.py
    recorder.py

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
        context=context,
        allowed_tools=[...],
        budget=Budget(max_model_calls=8, max_subagents=3),
        output_schema=DiagnosisResult,
    )
)
```

The runtime must not know what a reactor, XMEAS, CNC machine, or pump is.

## First consumer

`tep-agent-lab` should be the first serious consumer. That lab will provide TEP-specific tools such as `observe`, `fork_environment`, and `run_rollout`.

## Documents

- `AGENTS.md` — coding-agent constraints
- `docs/architecture.md` — runtime contracts and boundaries
- `docs/roadmap.md` — implementation order
