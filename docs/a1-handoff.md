# A1 environment API handoff

Task: A1. Branch: `feat/environment-api-v0`.
Owning specification: `docs/specs/environment-api-v0.md`.

## Delivered

- `src/tep_sim/contracts.py`: typed config, immutable observations, interventions,
  step results, and checksum artifact references.
- `src/tep_sim/environment.py`: explicit lifecycle, ordered validation, deterministic
  Python upstream adapter, manual MV admissibility constraints, streamed rollout,
  append-only in-memory schedule/events persisted as run provenance, failure artifacts.
- `src/tep_sim/registry.py`, `upstream_hashes.json`: upstream-derived metadata and
  source verification against submodule revision `9a6c8e5fcef4a2850778704e7793c87b0a187005`.
- `src/tep_sim/errors.py`, `__init__.py`: explicit typed failures and public exports.
- `pyproject.toml`, `.gitignore`, README: install/test setup and explicit units/limits.
- `tests/test_environment.py`: 13 acceptance/negative-path tests using actual upstream.

## Verification

Command:

```powershell
py -3.13 -m pytest -c pyproject.toml -q tests vendor/tep-sim-upstream/tests/test_constants.py vendor/tep-sim-upstream/tests/test_controllers.py vendor/tep-sim-upstream/tests/test_simulator.py
```

Output: `75 passed in 3.71s` (13 adapter + 62 upstream regression tests).

`py -3.13 -m pip wheel --no-build-isolation --no-deps --wheel-dir dist .`:
`Successfully built tep-sim`.

`git diff --check`: passed (only Windows line-ending conversion notices).

Acceptance 1–6 pass: identical baseline/reset and IDV trajectories; unknown target
and other validation failures preserve simulator/provenance and subsequent evolution;
closed-loop manual MV rejected; fixed rollout persists full attributable provenance;
no agent/runtime imports. Immutable observations and artifact checksum stability
after later rollouts/close are checked. Coordinator review finding about partial
telemetry on failure is fixed and regression-tested.

Initial upstream regression collection without `-c pyproject.toml` selected the
upstream pytest config and lacked the local source path. Corrected command above
uses the owning repo config. `test_python_backend.py` also needs unavailable SciPy;
that extra upstream suite was not run. All adapter acceptance tests use the real
Python backend, not a substitute process model.

## Boundaries / follow-up

No LLM, provider, runtime, RCA, topology, snapshot/fork, or research semantics added.
No canonical spec changes and no SPEC_CONFLICT identified.

A1 intentionally supports Python only. Fortran requires later validation before
enabling. Safety margins remain empty with capability explicitly false pending A4;
shutdown is actual upstream truth. `record_interval` is a positive integer step
count; horizon/time units are hours with integral one-second horizons. Seed range
is positive integers exactly representable by upstream float64 RNG state. Current
setpoint must satisfy a new manual MV constraint; no silent clipping occurs.

Upstream dependency installation is from the pinned submodule; importing any
different package source is rejected even if its package version matches.
Source-tree tests need NumPy and pytest only. A2 may now build snapshot/fork/replay
against these explicit environment primitives; no A2 fidelity claim is made here.

Commit identifier is provided by the coordinator handoff / branch HEAD, avoiding
a self-referential commit hash inside the commit itself.
