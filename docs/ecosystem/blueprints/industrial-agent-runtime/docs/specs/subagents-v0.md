# Ephemeral Subagents v0

Status: proposal  
Version: v0  
Owner repo: `industrial-agent-runtime`

## Goal

Allow the main agent to delegate narrow independent reasoning tasks without reintroducing a fixed Supervisor/MachineExpert/DataScientist organization or unbounded multi-agent chatter.

## Core rule

A subagent is a **temporary child task**, not a persistent persona or organizational role.

It exists only for one bounded `Subtask` and returns one compact structured `EvidenceBundle` to its parent.

## `Subtask`

Required fields:

```text
subtask_id
parent_task_id
goal
context_refs
allowed_tools
budget
output_schema
reason_for_delegation
```

## v0 defaults

Proposed conservative defaults:

```text
max_subagent_depth = 1
max_subagents_per_parent = 3
child_mutating_tools = disabled
child_can_spawn_subagents = false
```

All values are configurable policy defaults, not hard-coded universal constants.

## When spawning is justified

The runtime should allow a subtask when at least one condition is true:

- independent hypotheses can be evaluated in parallel;
- a narrow context materially reduces the parent's context load;
- an independent verification/critique has a defined output contract;
- separate simulation experiments can be performed safely in isolated forks.

The agent should not spawn merely because a job title can be invented.

## `EvidenceBundle`

A child returns compact structured evidence, conceptually:

```text
evidence_id
subtask_id
claim_or_result
supporting_refs
uncertainty/confidence?
artifacts?
warnings
status
```

The parent does not inherit the child's full hidden transcript by default.

## Authority model

v0 proposal:

- child may use READ/COMPUTE/SIMULATE tools granted by the parent/task policy;
- child may not execute MUTATE operations;
- child may return a suggested action only as evidence/proposal data;
- only the parent may produce an application-level side-effect proposal;
- the parent still cannot bypass deterministic gates.

This keeps delegation useful while retaining one clear authority boundary.

## Context isolation

A subagent receives only explicitly selected `context_refs` plus tool schemas it is permitted to use. It MUST NOT automatically inherit the complete parent transcript or all parent tools.

## Parallelism

Independent read/compute/simulation subtasks MAY run in parallel. Parallel children must not share mutable application state. Consumer tool adapters are responsible for isolated simulation branches when needed.

## Duplicate-work control

The runtime SHOULD detect obvious duplicate subtask goals/IDs and expose active/completed child summaries to the parent to reduce repeated delegation.

## Failure behavior

A child failure is returned as a structured failed `EvidenceBundle`/subtask result. It does not silently restart or recursively delegate unless the parent explicitly replans within remaining budget.

## Trace requirements

Every spawn records:

```text
parent_task_id
subtask_id
reason_for_delegation
context refs
allowed tools
allocated budget
start/end status
budget used
result reference
```

## Invariants

- Child has narrower or equal authority than parent.
- Child cannot escape task/tool/budget policy.
- No child-to-child free-form chat in v0.
- No child persistence after subtask completion.
- Parent consumes structured result, not hidden full transcript.
- Spawn count/depth are deterministically enforced.

## Acceptance tests

1. Parent spawns two independent read-only hypothesis subtasks.
2. Children receive different scoped context refs.
3. Child attempting a forbidden mutating tool is denied before execution.
4. Fourth child is rejected when policy limit is three.
5. Child cannot recursively spawn at depth limit.
6. Parent receives compact evidence and combines it into final output.
7. Child failure is visible and does not trigger unbounded retries.

## Open questions

- Should verifier/critic subtasks have a dedicated semantic type, or remain ordinary subtasks with different schemas?
- Should a consumer be allowed to grant a child a proposal-only mutation tool for recovery candidate generation?
- What measurable threshold should justify enabling deeper delegation in future versions?
