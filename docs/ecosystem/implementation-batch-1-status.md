# Implementation batch 1 status — 2026-09-19

This record tracks the dependency-aware implementation plan. It records
implementation evidence and does not itself change frozen public contracts.

## Dependency state

```text
A1 environment API (complete) -> A2 snapshot/fork (complete)

B1 runtime contracts/reference loop (complete)
  -> C1 RCA state (implemented)
  -> C2 rule registry (complete)
  -> C3 hypothesis/experiment contracts (implemented)
          |
          v
     lab integration/batch-1
```

## Handoffs

| Task | Branch / commit | Verification | Status |
| --- | --- | --- | --- |
| A1 | `feat/environment-api-v0` / `d1374aa7485ad162f75dbc8e92025539b461909f` | 75 passed against pinned Python upstream | Complete |
| A2 | `feat/snapshot-fork-v0` / `313effa79c24328f0ec2f8687aa76737f08d2aa1` | 82 passed; wheel and compile checks | Complete; fidelity EXACT, cloned-state error 0.0 |
| B1 | `integration/batch-1` / `6c8a8d222a7dbf2bd6ed4b9162e3c6b7424d8ec7` | 62 passed; compile and wheel build | Complete for B1; terminal lifecycle persistence included; B2/B3/B4 capabilities fail closed |
| C1 | `feat/investigation-state-v0-resume` / `ae3cc40` | 66 lab tests with B1 pin; 16 C1 tests | Complete for scheduled C1 v0 scope |
| C2 | `feat/rule-registry-v0` / `7455fe8cc5095925345528220b0c054eb2055e13` | 12 focused tests plus integration regression | Complete for C2 v0 metadata registry |
| C3 | integrated source `17790ab5c4f35ffcb7a012985fb9da268735d2b9` | 21 focused experiment tests plus integration regression | Typed/data/dedup paths implemented; execution waits for C4/A2/B2 |
| Lab integration | `integration/batch-1` / `e583495` | exact runtime pin verified; 66 passed; compileall | Reviewable integrated batch; no unresolved contract conflict |

Boundary checks found no responsibility movement: `tep-sim` imports no runtime
or lab package; runtime imports no TEP/domain/provider-framework package; lab
imports generic contracts from the exact runtime pin and does not copy simulator
physics or runtime scheduling.

## Resolved contract conflict — D-034

The previously reported B1 public wire gaps were explicitly approved and are
now closed in both owning specs and blueprint copies:

```text
ToolCallRequest = request_id + tool_name + arguments
FinishProposal = structured_output + information_refs[] + artifact_refs[]
WorkBatch completion_policy v0 = ALL_SETTLED
```

Decision Register entry D-034 records the adjudication. Runtime spec commit is
`83b8645d1e80fdfb426f137b39be02498ea8a4ad`; program/blueprint commit is
`13ed126683a8d0a1a152055e5fdb3ff94bf21dd5`.

## Resolved contract conflicts — D-035

The approved minimum corrections close both implementation seams in owning specs,
blueprint copies, and code:

1. Runtime `TaskStateStore.transition_status(status, expected_revision)` now
   persists Coordinator-owned terminal status without naming a lab operation.
   DONE, FAILED, EXHAUSTED, and CANCELLED are revision-bound; same-terminal calls
   are idempotent and different terminal overwrites reject.
2. Lab `WorkingExplanationUpdate` is a shared revision-free C1/C3 payload.
   Interpretation maps conclusion/uncertainty into it, and C1 materializes
   `last_updated_revision` from the accepted resulting state revision.

Runtime implementation/spec commit is `6c8a8d2`; lab contract implementation is
`74d3d60`, integrated as `2c2d99c`. The cross-repo test proves two lexical
WorkBatch ingestions at `0->1` and `1->2`, followed by verified Finish persisting
DONE at `2->3`.

No B1/C1/C3 `SPEC_CONFLICT` remains.

## Verification limitations and deferred work

The A1 upstream SciPy-only test file remains uncollected because SciPy is not
installed; the 62 available upstream regressions and all A1/A2 acceptance tests
pass. A2 reused the initialized pinned upstream copy because network access is
restricted. Snapshot deserialization remains limited to an explicit trusted
artifact root.

B2 full deterministic gates/resource reservation, B3 full verifier policy, B4
subtask execution, and C4 experiment/scenario execution remain downstream work.
No HAZOP, Recovery, AutoProcessResearch, learned memory, or knowledge-promotion
implementation was added.
