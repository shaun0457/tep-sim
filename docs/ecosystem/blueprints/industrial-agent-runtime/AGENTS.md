# AGENTS.md

Repository-wide rules for coding agents working on `industrial-agent-runtime`.

## Product boundary

This repository is a **domain-independent agent runtime**. Do not encode TEP, chemical-process, manufacturing, finance, or other domain semantics in core runtime code.

## Canonical specs

Before implementation, read:

- `docs/specs/runtime-v0.md`
- `docs/specs/hybrid-orchestration-v0.md`
- `docs/specs/deterministic-gates-v0.md`
- `docs/specs/subagents-v0.md`
- `docs/open-questions.md`
- `docs/decisions/ADR-002-hybrid-orchestration.md`

`ADR-001-minimal-explicit-executor.md` is historical/superseded context, not current architecture authority.

If implementation evidence contradicts a proposal spec, report/update the spec/ADR rather than silently inventing semantics.

## Hard rules

1. Prefer deterministic code for validation, permissions, budgeting, serialization, state revisions, routing, dependency scheduling, and machine-checkable verification.
2. Model output is a request/proposal, never execution authority.
3. Pre-execution request validation and post-execution result verification are distinct stages.
4. Runtime must not import application/domain state classes; use `TaskStateStore`.
5. Every model turn has an immutable `ContextProjection` ref with prompt/model/tool metadata.
6. Budgets include standard counters plus configured `extra_dimensions`; compound tools cannot hide nested simulator/optimizer use.
7. `SIMULATE` may mutate only isolated/sandbox state and never reference state.
8. `MUTATE` requires deterministic consumer validation and expected-state revision binding when enabled.
9. Subagents are ephemeral child tasks, not persistent roles.
10. Child authority is a strict subset of task/parent authority; no escalation exceptions.
11. Subagent count is cumulative per task, including `SUBTASK` WorkBatch items.
12. Child at depth limit cannot create another SUBTASK through WorkBatch or another equivalent path.
13. Child returns `SubtaskResult`, not `EvidenceBundle`/full transcript.
14. v0 dependency planning is `WorkBatch` with `TOOL | SUBTASK` + `depends_on`; do not invent `ANALYSIS`/`MERGE` node types or a full Dynamic DAG engine.
15. LangGraph and MCP are not v0 core dependencies.
16. Core tests run with a deterministic fake model provider and no domain import.
17. No arbitrary agent shell/Python/import execution as the normal tool model.

## Request path

```text
model request / WorkItem
 -> G0 schema
 -> G1 allowlist/authority
 -> G2 budget/resource reservation
 -> G3 side-effect policy
 -> consumer.validate_request
 -> optional authority escalation/approval
 -> frozen request
 -> Executor
 -> post-execution verify_result
 -> TaskStateStore.apply
```

## WorkBatch semantics

```text
WorkItem.kind = TOOL | SUBTASK
```

- ready items may run in parallel within policy;
- failed required dependency => dependent `SKIPPED_DEPENDENCY`;
- no silent retries;
- merge/open-ended integration happens on the next Main Agent turn.

## Testing minimum

- fake-provider typed task;
- allowed read tool;
- malformed/unknown request;
- standard/extra-dimensional budget denial;
- compound SIMULATE reservation/accounting;
- consumer request-validator denial;
- post-result missing-ref rejection;
- TaskStateStore stale revision rejection;
- WorkBatch cycle/dependency/failure behavior;
- subagent cumulative count/depth limit;
- child MUTATE denial;
- exact ContextProjection trace refs;
- deterministic fake-provider replay.

Keep this file concise; detailed semantics belong in `docs/specs`, unresolved empirical questions in `docs/open-questions.md`, and rationale in ADRs.
