# industrial-agent-runtime

Domain-independent Hybrid runtime for one goal-driven Main Agent, deterministic Coordinator/Executor/Verifier components, bounded Dynamic DAGs, typed tools, ephemeral subagents, and deterministic execution gates.

## Purpose

Industrial agent experiments should not embed generic orchestration inside every simulator/domain repository. This runtime provides reusable agent mechanics while remaining ignorant of TEP, XMEAS/XMV/IDV, HAZOP mappings, process-safety truth, and benchmark-specific scoring.

## Core principles

- one Main Agent provides open-ended reasoning;
- Coordinator, Executor, and Verifier are deterministic runtime components by default, not permanent LLM roles;
- simple tasks use a local ReAct-style loop without forcing a plan graph;
- complex tasks may use a model-proposed, deterministically validated Dynamic DAG;
- subagents are temporary bounded tasks, not job titles;
- model outputs are requests/proposals, not execution authority;
- deterministic code handles schemas, DAG validity, permissions, budgets, recursion/plan limits, execution, provenance, and machine-checkable verification;
- context is reference-based and assembled per task rather than accumulated indefinitely;
- every model turn, plan revision, node, tool, subagent, gate, and result is traceable;
- tests use a deterministic fake provider;
- public contracts are framework-neutral; LangGraph is supported through an adapter rather than defining the API.

## Conceptual runtime

```text
Task / Goal
   |
   v
Information refs / Context projection
   |
   v
Deterministic Coordinator
   |
   v
Main Agent
   |\
   | +-- simple --> tool/subtask
   |
   +---- complex --> Dynamic DAG proposal
                       /   |   \
                    tool subtask sim
                       \   |   /
                         merge
   |
   v
Deterministic Verifier
   |
   v
schema / permission / budget / side-effect gates
   |
   v
Deterministic Executor
   |
   v
consumer tools / environments
```

## Repository owns

- model-provider abstraction;
- Main Agent invocation contract;
- deterministic Coordinator/Executor/Verifier;
- dynamic-plan/DAG validation and scheduling semantics;
- task/tool/budget/result contracts;
- ephemeral-subagent execution;
- context/reference broker interfaces;
- generic tool registry/permissions;
- deterministic generic gates;
- traces/observability;
- LangGraph/checkpoint/approval adapters.

## Repository does not own

- TEP variables/equations/topology;
- application-specific Investigation State fields;
- process Rule Registry content;
- application-specific safety limits;
- HAZOP/RCA/recovery workflows;
- P&ID/DEXPI parsing;
- domain knowledge bases;
- experiment ground truth/scorers.

## Suggested package layout

```text
src/industrial_agent_runtime/
  contracts/
    task.py
    result.py
    tool.py
    budget.py
    plan.py
    trace.py
  runtime/
    coordinator.py
    executor.py
    verifier.py
    main_agent.py
    context.py
    subtask.py
  gates/
    schema.py
    permission.py
    budget.py
    side_effect.py
    plan.py
  tools/
    registry.py
  models/
    base.py
    fake.py
    providers/
  tracing/
    recorder.py
  orchestration/
    langgraph_adapter.py
  persistence/
    checkpoint.py

tests/
docs/
AGENTS.md
```

## Minimal API direction

```python
runtime = AgentRuntime(
    model=model,
    tools=tools,
    policy=policy,
    coordinator=coordinator,
    verifier=verifier,
)

result = runtime.run(
    Task(
        goal="Investigate the incident and return evidence-backed hypotheses",
        context_refs=[...],
        allowed_tools=[...],
        budget=Budget(
            max_model_calls=8,
            max_tool_calls=20,
            max_subagents=3,
            max_subagent_depth=1,
            max_steps=30,
            max_plan_nodes=8,
            max_plan_revisions=2,
        ),
        output_schema=InvestigationResult,
    )
)
```

The runtime must not know what a reactor, pump, CNC machine, or TEP fault is.

## First consumer

`tep-agent-lab` is the first serious consumer. It supplies TEP-specific Investigation State, Information Plane refs, Tool Bridge adapters, policies, and output/evaluation schemas.

## Documentation

- `AGENTS.md` — minimal coding-agent constraints
- `docs/architecture.md` — Hybrid runtime boundary
- `docs/roadmap.md` — implementation order
- `docs/specs/runtime-v0.md` — core execution contracts
- `docs/specs/hybrid-orchestration-v0.md` — Coordinator/Executor/Verifier + ReAct/Dynamic DAG semantics
- `docs/specs/subagents-v0.md` — ephemeral-subagent contract
- `docs/specs/deterministic-gates-v0.md` — generic gate model
- `docs/open-questions.md` — remaining empirical/implementation choices
- `docs/decisions/` — ADRs
