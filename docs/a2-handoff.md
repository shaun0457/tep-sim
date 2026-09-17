# A2 snapshot / fork / replay handoff

Task: A2. Branch: `feat/snapshot-fork-v0`.
Base: A1 commit `d1374aa`.
Owning specification: `docs/specs/snapshot-fork-replay-v0.md`.

## Delivered

- immutable `Snapshot`, `Branch`, and `ReplaySpec` contracts with explicit
  `EXACT` fidelity and `CLONED_STATE` randomness policy;
- exact pinned-Python state artifacts covering simulator, process, RNG,
  controller, constraints, time, and termination state;
- isolated fork lifecycle and branch provenance under the parent run;
- persisted, checksummed replay specifications with typed intervention
  allowlisting and target time/step validation;
- trusted-root/path, metadata, state, format, revision, and checksum gates before
  deserialization;
- acceptance tests using the actual upstream process, including 300-step
  same-snapshot stochastic reproduction with maximum XMEAS/XMV error `0.0`;
- `ADR-001` documenting the tested fidelity and trust boundary.

## Verification

The A2 worktree reused the already initialized A1 submodule checkout at the exact
required revision because outbound network was unavailable for a second worktree
clone. The source hashes are also checked by the adapter before construction.

```powershell
$env:PYTHONPATH='src;../a1/vendor/tep-sim-upstream/src'
python -m pytest -p no:cacheprovider --basetemp <workspace-temp> `
  -c pyproject.toml -q tests `
  ../a1/vendor/tep-sim-upstream/tests/test_constants.py `
  ../a1/vendor/tep-sim-upstream/tests/test_controllers.py `
  ../a1/vendor/tep-sim-upstream/tests/test_simulator.py
```

Result: `82 passed in 4.78s` (7 A2, 13 A1 adapter, 62 pinned upstream
regressions). `compileall`, wheel build, and `git diff --check` also pass.

The upstream `test_python_backend.py` remains outside the run because SciPy is
not installed; all A1/A2 tests execute the real pinned Python backend.

## Boundaries and unresolved items

Only `tep-sim` snapshot/fork/replay and the minimal A1 provenance/schedule hooks
were changed. No DEXPI, safety, runtime, lab, agent, or research behavior was
added. Exact fidelity is limited to the pinned Python backend and state format.
Imported artifact trees are not authenticated and must not be designated as a
trusted artifact root.

No `SPEC_CONFLICT` was identified.
