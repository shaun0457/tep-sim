# Implementation batch 1 status — 2026-09-17

This status record applies the dependency-aware plan in
`implementation-batch-1.md`. It does not change frozen public contracts.

## Dependency state

```text
A1 environment API (complete) -> A2 snapshot/fork (complete)

B1 explicit contracts/tracing (partial)
    -> SPEC_CONFLICT: request/finish/completion wire fields
    -> dispatcher/fake provider/reference loop stopped

B1 pinned contract tranche -> C1 storage/records partial
                           \-> C2 rule registry complete
                           \-> C3 prediction/dedup partial
                                      |
                                      v
                         lab integration/batch-1
```

## Handoffs

| Task | Branch / commit | Verification | Status |
| --- | --- | --- | --- |
| A1 | `feat/environment-api-v0` / `d1374aa7485ad162f75dbc8e92025539b461909f` | 75 passed against actual pinned Python upstream | Complete; A2/A3/A4 excluded |
| B1 contracts tranche | `feat/contracts-runtime-v0` / `98413477f5294e60f67035de8d4342cd90e8fbd7` | 15 passed, compileall | Partial; no execution loop |
| C1 independent | `feat/investigation-state-v0` / `2076e22` | 14 passed with exact runtime pin | Partial; storage and Engineering Records only |
| C2 | `feat/rule-registry-v0` / `7455fe8cc5095925345528220b0c054eb2055e13` | 12 passed | Complete for C2 v0 metadata registry; real gate adapter deferred |
| C3 independent | `feat/hypothesis-experiment-v0` / `e70440e` | 19 branch tests (11 C3 + 8 inherited regression) | Partial; prediction comparison/dedup only |
| Lab integration | `integration/batch-1` / `5aad2e2` | runtime pin verified; 37 passed; compileall; wheels installed/imported | Reviewable integrated partial batch |
| A2 | `feat/snapshot-fork-v0` / `313effa79c24328f0ec2f8687aa76737f08d2aa1` | 82 passed; compileall; wheel built | Complete; pinned Python fidelity EXACT, cloned-state error 0.0 |

All completed worktrees were checked for boundary violations: `tep-sim` imports no
runtime/lab/agent package; runtime imports no domain/provider/LangGraph/MCP package;
lab imports generic refs only from the exact pinned runtime commit and does not copy
simulator physics.

## SPEC_CONFLICT — B1

Affected owning specs:

- runtime `docs/specs/runtime-v0.md` (`ToolCallRequest`, `FinishProposal`);
- runtime `docs/specs/hybrid-orchestration-v0.md` (`completion_policy`).

Observed evidence and conflicting assumptions:

- `ToolCallRequest` is named but has no field contract, so G0/dispatch cannot know
  the tool identity and arguments without inventing a public wire format;
- `FinishProposal` is routed and verified but has no defined payload;
- `WorkBatch.completion_policy` is required but has no allowed values or behavior.

Smallest proposed contract change, not yet applied:

```text
ToolCallRequest
  request_id
  tool_name
  arguments

FinishProposal
  structured_output
  information_refs[]
  artifact_refs[]

WorkBatch completion_policy v0
  ALL_SETTLED only; unknown values fail closed
```

Dependent implementation remains stopped until explicit adjudication updates the
owning specs/decision register. Existing failure and dependency semantics are not
otherwise changed.

## Verification limitations

The A1 upstream `test_python_backend.py` file was not collected because SciPy is not
installed; all A1 acceptance cases execute the actual upstream Python backend, and
the 62 available upstream constants/controllers/simulator regressions pass.
The first sandbox rerun could not create pytest files in the user temp directory;
rerunning with a workspace-owned `--basetemp` produced the recorded 75/75 pass.

A2 reused the already initialized A1 copy of the same pinned upstream submodule
because the isolated worktree could not clone through the restricted network. Its
combined A1/A2/upstream run produced 82/82 passes. Snapshot state deserialization
requires an explicit trusted artifact root; checksums detect corruption but do not
authenticate an imported artifact producer.
