# ADR-002 — Hybrid orchestration for agent investigations

Status: accepted  
Date: 2026-09-15

## Context

The target industrial Agent must choose evidence, hypotheses, experiments, and delegation while budgets, permissions, execution, and machine-checkable invariants remain deterministic.

A prior design coupled this Hybrid idea to a full model-proposed Dynamic DAG and suggested a LangGraph adapter early. Independent review found those details under-specified and premature.

## Decision

Adopt a **Hybrid contract** for v0:

```text
consumer TaskStateStore.project
        |
        v
Main Agent
  local goal-driven/ReAct reasoning
        |
 ToolCall / WorkBatch / FinishProposal
        |
        v
pre-execution G0-G3 + consumer.validate_request
        |
        v
Deterministic Executor
        |
        v
post-execution verify_result
        |
        v
consumer TaskStateStore.apply
```

Coordinator/gates/Executor/post-execution Verifier are deterministic runtime responsibilities, not permanent LLM personas.

This ADR accepts the implementation boundary, **not** a claim that Hybrid is empirically better than ReAct or a fixed workflow. That is measured by `evaluation-v0.md`.

## Dependency-aware work decision

v0 does not require a general mutable Dynamic DAG engine.

For bounded dependent/parallel work, Main Agent may propose:

```text
WorkBatch
  items:
    - TOOL or SUBTASK
    - depends_on[]
```

Coordinator deterministically validates acyclicity, cumulative budgets, authority, visibility, and dependency readiness.

There are no v0 `ANALYSIS` or `MERGE` graph node types:

- deterministic analysis is a TOOL;
- open-ended analysis/merge is the next Main Agent turn;
- simulation is a TOOL with `side_effect_class=SIMULATE`.

Richer dynamic replanning/cancellation/graph semantics require a later spec and are an empirical orchestration extension.

## Pre/post validation decision

The term Verifier refers only to post-execution result/state verification.

Pre-execution authorization is:

```text
G0 schema
G1 allowlist/authority
G2 budget/resource reservation
G3 side-effect policy
consumer.validate_request
```

Post-execution verification checks result refs/provenance/accounting/state invariants that cannot exist before dispatch.

## State boundary decision

Runtime owns generic `TaskStateStore`, `TaskStatus`, `StateDelta`, `ContextProjection`, and `InformationRef` contracts.

Consumers own domain state schemas and projection relevance.

The runtime must never import TEP/RCA state types.

## Framework decision

Public contracts remain framework-neutral/serializable.

LangGraph is **not** a v0 core dependency or scheduled delivery. It may be added only when a concrete checkpoint/resume/interrupt/persistent-graph requirement demonstrates value beyond the reference loop.

MCP is similarly not an orchestration dependency; it may later appear only behind a Tool Provider adapter.

## Consequences

Positive:

- preserves Agent autonomy for open-ended investigation;
- keeps authorization/accounting mechanically testable;
- removes undefined graph node semantics from the critical path;
- keeps state/repo boundaries explicit;
- allows dependency-aware parallel work without graph-framework lock-in;
- enables clean ReAct/fixed-workflow/Hybrid/WorkBatch/subagent ablations.

Costs:

- runtime still needs explicit state/budget/ref contracts;
- consumer must implement TaskStateStore/projection logic;
- richer dynamic graph behavior is deferred rather than available by default.

## Alternatives considered

1. Pure ReAct as sole architecture — retained as experimental baseline, rejected as the v0 authority/state contract because deterministic policy/state handling is still required.
2. Fixed workflow only — retained as orchestration baseline.
3. Full Dynamic DAG from day one — deferred after review because execution/failure/merge/replanning semantics were not justified for v0.
4. Permanent Coordinator/Executor/Verifier LLM agents — rejected.
5. LangGraph-first runtime — deferred until concrete durable-graph requirements exist.

## Revisit triggers

- WorkBatch cannot express a measured useful investigation/planning behavior;
- mutable DAG replanning/cancellation shows measurable value;
- durable checkpoint/resume/interrupt becomes a concrete requirement;
- simpler O1/O2 orchestration consistently matches/exceeds the Hybrid implementation at lower cost.
