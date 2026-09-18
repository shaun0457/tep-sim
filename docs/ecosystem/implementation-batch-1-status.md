# Implementation batch 1 status — 2026-09-19

This record tracks the dependency-aware implementation plan. It records
implementation evidence and does not itself change frozen public contracts.

## Dependency state

```text
A1 environment API (complete) -> A2 snapshot/fork (complete)

B1 runtime contracts/reference loop (complete)
  -> C1 RCA state independent paths (implemented)
  -> C2 rule registry (complete)
  -> C3 hypothesis/experiment contracts (implemented)
          |
          +-> two narrow SPEC_CONFLICT paths stopped
          |
          v
     lab integration/batch-1
```

## Handoffs

| Task | Branch / commit | Verification | Status |
| --- | --- | --- | --- |
| A1 | `feat/environment-api-v0` / `d1374aa7485ad162f75dbc8e92025539b461909f` | 75 passed against pinned Python upstream | Complete |
| A2 | `feat/snapshot-fork-v0` / `313effa79c24328f0ec2f8687aa76737f08d2aa1` | 82 passed; wheel and compile checks | Complete; fidelity EXACT, cloned-state error 0.0 |
| B1 | `integration/batch-1` / `dc1845fa930683364abd04a8d0d4b910168eb3d8` | 52 passed; compile and wheel build | Complete for B1; B2/B3/B4 capabilities fail closed |
| C1 | `feat/investigation-state-v0-resume` / `59f82f8` | 63 lab tests with B1 pin; 13 C1 tests | Independent paths implemented; two dependent contract paths stopped |
| C2 | `feat/rule-registry-v0` / `7455fe8cc5095925345528220b0c054eb2055e13` | 12 focused tests plus integration regression | Complete for C2 v0 metadata registry |
| C3 | integrated source `17790ab5c4f35ffcb7a012985fb9da268735d2b9` | 21 focused experiment tests plus integration regression | Typed/data/dedup paths implemented; execution waits for C4/A2/B2 |
| Lab integration | `integration/batch-1` / `989336c` | exact runtime pin verified; 63 passed; compileall | Reviewable integrated batch |

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

## SPEC_CONFLICT — lifecycle persistence seam

Affected specs:

- runtime `docs/specs/runtime-v0.md` (`TaskStateStore` protocol);
- lab `docs/specs/investigation-state-v0.md` (`generic_status`,
  `SET_GENERIC_STATUS`).

Observed evidence: the lab spec requires Finish, hard-stop, failure,
cancellation, and exhaustion transitions to update the runtime-owned generic
status in `RcaState`. The generic protocol exposes only
`revision/status/project/apply_batch`; the Coordinator has no domain-independent
lifecycle transition call. Naming the lab-owned `SET_GENERIC_STATUS` operation
inside runtime would violate the repository boundary.

Smallest proposed change: add a runtime-owned typed lifecycle transition method
or delta to `TaskStateStore`, and have the Coordinator invoke it on terminal
paths. C1 currently validates trusted `RUNTIME` status deltas but does not invent
the missing invocation contract.

## SPEC_CONFLICT — interpretation/working-explanation shape

Affected specs:

- lab `docs/specs/hypothesis-experiment-v0.md` (Interpretation mapping);
- lab `docs/specs/investigation-state-v0.md` (`WorkingExplanation`).

Observed evidence: C3 maps `conclusion_summary` and `residual_uncertainty` to
`UPDATE_WORKING_EXPLANATION`, while C1 requires a canonical object containing a
leading hypothesis, rank/score summary, positive/counterevidence refs, remaining
uncertainties, and last revision. No owning spec defines a deterministic mapping
between those shapes.

Smallest proposed change: define one typed `UPDATE_WORKING_EXPLANATION` payload
and its deterministic materialization in the owning specs, then use that shared
shape in C3 mapping and C1 validation. The current integration fails closed on
the incompatible patch.

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
