# ADR-002 — Hybrid orchestration for agent investigations

Status: accepted direction  
Date: 2026-09-15

## Context

The target industrial Agent must be autonomous enough to choose evidence, hypotheses, experiments, and delegation, while TEP/process invariants, budgets, authority, and execution semantics should not consume repeated LLM reasoning.

Pure ReAct is flexible but can create long/unstructured trajectories. A fully fixed DAG is reproducible but cannot adapt investigation structure to unknown incidents. A fully model-controlled Dynamic DAG gives flexibility but needs deterministic validation/authority boundaries.

## Decision

Use a Hybrid runtime:

```text
Deterministic Coordinator
        |
        v
Main Agent
  local ReAct for simple work
        |
        +-- complex --> model-proposed Dynamic DAG
        |
        v
Deterministic Verifier / Gates
        |
        v
Deterministic Executor
```

### Authority

- Main Agent decides strategy and proposes work.
- Coordinator owns runtime state, budgets, routing, DAG validation/scheduling, and hard termination.
- Executor performs the exact validated request.
- Verifier checks machine-checkable validity/evidence/policy/provenance.
- Domain validators remain consumer-owned.

Coordinator/Executor/Verifier are not permanent LLM agents.

## Framework decision

Public runtime contracts remain framework-neutral.

A LangGraph adapter is allowed/recommended for `tep-agent-lab` macro workflow, structured state/checkpointing, interrupts, and graph observability, but LangGraph-native message/state types do not define the core API.

A simple explicit executor remains a reference implementation and baseline.

## Dynamic DAG decision

Dynamic DAGs are model-proposed **data**, not direct control authority. Coordinator validates acyclicity, dependencies, budgets, tool authority, schemas, and consumer visibility policy before scheduling.

Simple work must not require a DAG.

## Consequences

Positive:

- preserves autonomy for investigation/planning;
- reduces unnecessary Agent exploration for deterministic constraints;
- supports adaptive parallel experiments/subtasks;
- keeps authority auditable;
- supports direct comparison of ReAct/fixed DAG/Hybrid/Dynamic DAG architectures;
- avoids generic-runtime coupling to TEP or one framework.

Costs:

- more state/contracts than a plain ReAct loop;
- Dynamic DAG validation/scheduling requires careful testing;
- two orchestration paths (simple/direct and DAG) require trace consistency;
- LangGraph adapter adds an additional integration layer.

## Alternatives

1. Pure ReAct — retained as an ablation/simple local reasoning pattern, rejected as the sole architecture.
2. Fixed DAG only — retained as an ablation/deterministic macro component, rejected for all investigation planning.
3. Fully model-controlled dynamic graph — rejected because graph validity/authority/budgets must remain deterministic.
4. Permanent Coordinator/Executor/Verifier agents — rejected; these responsibilities are deterministic runtime components unless a bounded semantic critic is explicitly studied.

## Revisit trigger

Revisit if benchmark evidence shows a simpler architecture achieves equal/better investigation quality and efficiency, or if Dynamic DAG overhead dominates its value across intended tasks.
