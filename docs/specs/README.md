# `tep-sim` Specifications

These specs define the stable contracts of the Tennessee Eastman Process sandbox.

## Active v0 specs

- [`environment-api-v0.md`](environment-api-v0.md) — public environment lifecycle and typed operations.
- [`snapshot-fork-replay-v0.md`](snapshot-fork-replay-v0.md) — counterfactual branching and reproducibility semantics.
- [`dexpi-binding-v0.md`](dexpi-binding-v0.md) — DEXPI/process graph normalization and TEP runtime binding.
- [`safety-capability-v0.md`](safety-capability-v0.md) — explicit simulator capability and deterministic safety reporting.

All v0 specs are proposals until their acceptance tests exist and pass against the vendored upstream simulator.

## Ownership

`tep-sim` owns environment truth only. It does not define agent tasks, subagent policies, prompt behavior, HAZOP interpretation, RCA scoring, or recovery reasoning.
