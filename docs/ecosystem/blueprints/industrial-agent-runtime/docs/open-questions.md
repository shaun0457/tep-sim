# Open Questions — `industrial-agent-runtime`

Only unresolved empirical/implementation choices belong here. The Hybrid architecture, deterministic Coordinator/Executor/Verifier boundary, and framework-neutral LangGraph adapter direction are no longer open questions.

## OQ-1 — First real model provider

Core remains provider-agnostic and fake-provider-testable.

Choose the first real adapter based on:

- structured tool/schema reliability;
- model quality on investigation/planning;
- tracing/token/cost visibility;
- deterministic configuration controls;
- ease of local/CI testing.

Provider choice is an experiment/runtime adapter decision, not architecture.

## OQ-2 — Dynamic DAG limits

Need empirical defaults for:

```text
max_plan_nodes
max_plan_depth
max_parallel_width
max_plan_revisions
per-node budget
```

Start conservative; tune using orchestration-ablation results rather than aesthetics.

## OQ-3 — Subagent depth/limit

Initial proposal remains depth 1 and max 3 children per parent. Change only from measured quality/context/cost results.

## OQ-4 — Parallel executor implementation

The semantic contract allows independent nodes/subtasks to run in parallel. The first implementation may be sequential for correctness.

Open implementation choice: asyncio, threads, processes, or a job-executor abstraction depending on provider/tool blocking behavior.

Public contracts must not depend on the choice.

## OQ-5 — Context Broker sophistication

How much automatic retrieval/compression should generic runtime provide versus consumer adapters?

Default:

- runtime manages refs, budgets, visibility, and projection hooks;
- consumer owns domain selection/compaction;
- model-generated summarization is not used where deterministic structured compaction is sufficient.

Revisit after real context-pressure measurements.

## OQ-6 — Persistent checkpoint backend

LangGraph adapter/checkpointing direction is accepted, but storage backend is not.

Candidates may include in-memory/reference implementation first, then SQLite/Postgres/object storage depending on actual resume/audit needs.

Do not select infrastructure before state-size/concurrency requirements exist.

## OQ-7 — Human approval interface

Need a provider/UI-neutral contract for freezing an exact validated request and later approving/rejecting it without regeneration.

The approval surface may live in CLI/UI/API; core only defines state/transition contracts.

## OQ-8 — Optional semantic critic/verifier subtask

Deterministic Verifier is authoritative for machine-checkable constraints.

Open research question: does an optional LLM critic subtask improve semantic completeness enough to justify cost? If tested, it returns evidence/advice only and cannot override deterministic verification.

## OQ-9 — Cross-run learned memory

No persistent learned agent memory in v0. Revisit only after repeated-task studies show measurable value beyond Information Plane evidence, rules, and Experiment Ledger.

## OQ-10 — Stop-policy thresholds

Hybrid runtime supports semantic stop readiness plus hard budgets. Exact thresholds/policies for "evidence sufficient" remain consumer/task-specific and should be evaluated in the lab, not hard-coded globally.
