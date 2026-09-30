# Development-Agent Orchestration

Status: accepted working policy

## Purpose

Define how multiple coding agents/subagents may build the three-repository program in parallel **after Phase 0 Design Freeze**.

This document is about software-development agents (Codex/Claude Code/etc.), not the product runtime's Main Agent/subagents.

## Core rule

Parallelize implementation only across already-decided contracts with non-overlapping ownership. Do not use more coding agents to compensate for unresolved architecture.

```text
Human / architecture decision
        |
        v
accepted spec / ADR
        |
        v
Development Coordinator
        |
   dependency DAG
   /     |      \
agent A agent B agent C
   \     |      /
     review/integration
```

## Development Coordinator

The coordinator may be a human, a coding-agent harness, or a primary coding agent. Its responsibilities are deterministic/project-management oriented:

- read the canonical spec/ADR;
- decompose work into independent bounded tasks;
- define branch/worktree ownership;
- define dependencies/merge order;
- prevent overlapping file ownership where practical;
- collect test/result summaries;
- request review/integration;
- never silently change architecture to resolve implementation conflicts.

## Task contract

Every parallel coding task gets:

```text
DevelopmentTask
  task_id
  repo
  branch/worktree
  goal
  canonical_spec_refs[]
  in_scope_files/modules
  forbidden/out_of_scope areas
  dependencies[]
  expected_outputs
  required_tests
  acceptance criteria
  handoff format
```

## Branch/worktree model

Prefer one branch/worktree per independently reviewable task.

Example after design freeze:

```text
tep-sim
  feat/environment-api-v0
  feat/dexpi-binding-v0       # only when dependency contract permits

industrial-agent-runtime
  feat/contracts-runtime-v0
  feat/deterministic-gates-v0 # may begin after required contracts stabilize
```

Do not let two agents edit the same canonical spec or central contract simultaneously unless the task is explicitly a coordinated review.

## Dependency DAG

Parallel work follows an explicit DAG rather than "start everything".

Example:

```text
runtime contracts
  |\
  | \-> trace recorder
  |----> gate primitives
  \----> fake provider
          |
          v
hybrid coordinator/executor/verifier integration
```

A downstream task may inspect an upstream branch, but should not assume unmerged behavior without pinning the exact ref.

## Recommended development roles

These are task labels, not permanent multi-agent personas:

### Implementer

Implements one bounded spec/task and tests.

### Test/Verifier worker

Writes/runs independent acceptance tests or reviews evidence against the spec. It does not redefine expected behavior.

### Integration worker

Combines already-reviewed branches, resolves mechanical conflicts, runs cross-module tests, and reports architecture conflicts back to the coordinator.

### Research worker

Investigates an unresolved implementation fact (e.g. upstream simulator snapshot capability) and returns evidence without writing production architecture by default.

## Handoff format

Each worker returns a compact handoff:

```text
Task ID
Branch/commit
What changed
Tests run + results
Spec acceptance criteria status
Known limitations
Unexpected evidence / spec conflicts
Files touched
Follow-up dependencies
```

Do not hand off only "done" or a full transcript.

## Spec conflict policy

If a coding worker discovers that the spec is impossible/incorrect:

1. stop expanding implementation around the mismatch;
2. preserve the failing evidence/test;
3. report a `SPEC_CONFLICT` handoff;
4. coordinator opens/updates spec or ADR discussion;
5. resume only after the contract is revised or an explicit exception is accepted.

No worker may silently redefine public behavior to make tests pass.

## Parallelism limits

More agents are not automatically better.

Use parallel workers when:

- tasks have low file/contract overlap;
- dependency inputs are stable;
- tests can verify outputs independently;
- integration cost is lower than saved development time.

Prefer sequential work when:

- architecture is still changing;
- tasks touch the same schemas/core state;
- one discovery can invalidate all downstream work;
- shared fixtures/interfaces are not frozen.

## Review policy

Important core changes should receive at least one review pass independent of the implementer when practical.

Review focuses on:

- spec compliance;
- hidden scope expansion;
- deterministic/reproducibility guarantees;
- boundary violations between repos;
- tests/negative paths;
- context/dependency bloat.

## Integration order

Completion time does not determine merge order. Merge follows dependency/version order.

Downstream integration pins exact upstream revisions during development; after upstream merge/release, update pins intentionally.

## Product-runtime separation

Development-agent orchestration may use broader repo/shell/test permissions than the product Agent Runtime. Never copy development-agent permissions/behaviors into `industrial-agent-runtime` by convenience.

## Definition of done for parallel batch

A parallel development batch is done when:

- all task handoffs are collected;
- spec conflicts are resolved or explicitly deferred;
- branch tests pass;
- integration tests pass in dependency order;
- canonical docs/ADRs remain consistent;
- no temporary worktree/branch assumptions are mistaken for released interfaces.
