# Snapshot / Fork / Replay v0

Status: proposal  
Version: v0  
Owner repo: `tep-sim`

## Goal

Make counterfactual experiments first-class and reproducible. A caller must be able to preserve a process state, create isolated branches, apply different interventions, and compare outcomes without contaminating the reference state.

## Contracts

### `Snapshot`

Required metadata:

```text
snapshot_id
parent_run_id
simulation_time
environment_version
upstream_revision
seed/random-state metadata
state_format_version
state payload or reconstruction reference
checksum
```

### `Branch`

Required metadata:

```text
branch_id
parent_snapshot_id
branch_seed/random-state policy
created_at
intervention schedule
```

### `ReplaySpec`

Identifies the exact run/snapshot/config/intervention schedule needed to reproduce a trajectory.

## Semantics

### Snapshot

Creating a snapshot MUST NOT mutate or advance the source environment.

### Fork

Forks MUST NOT share mutable process state. Mutation in branch A MUST NOT change branch B or the parent environment.

### Randomness

The fork policy MUST be explicit. v0 default proposal:

- branches cloned from the same snapshot inherit equivalent random state so differences after the fork are attributable to interventions when possible;
- if the upstream simulator cannot support exact RNG cloning, the limitation must be documented and branch comparisons must record the fallback policy.

### Reference branch

The lab may designate one branch as reference/observed, but `tep-sim` itself does not attach special agent semantics to it.

## Counterfactual experiment pattern

```text
snapshot S
  |
  +--> A: hypothesis/action A -> rollout
  +--> B: hypothesis/action B -> rollout
  +--> C: no intervention      -> rollout
```

Comparison is performed by callers or evaluation utilities; the environment only guarantees branch provenance and isolation.

## Persistence

A persisted branch MUST retain enough metadata to answer:

- what state was forked;
- what intervention(s) were applied;
- which simulator versions were used;
- how randomness was handled;
- where dense result artifacts are stored.

## Failure behavior

If the upstream simulator cannot be cloned exactly, `snapshot()` MUST NOT pretend exact cloning is supported. The implementation should return a declared fidelity/capability status such as:

```text
EXACT
RECONSTRUCTED
UNSUPPORTED
```

A reconstructed snapshot is acceptable for v0 only if its error is measured and documented.

## Invariants

- Parent remains unchanged after fork execution.
- Branches are independently disposable.
- Branch provenance is never lost.
- Replay does not depend on hidden agent state.
- A failed branch rollout does not corrupt sibling branches.

## Acceptance tests

1. Snapshot a healthy state and show the source state is unchanged.
2. Fork A/B from the same snapshot and apply distinct interventions.
3. Verify A does not change B or parent state.
4. Repeat the same branch experiment and quantify reproducibility.
5. Persist and replay a branch from recorded metadata.
6. Verify explicit behavior if exact snapshotting is not possible with upstream internals.

## Open implementation choice

Whether v0 stores complete simulator state directly or reconstructs it by deterministic replay from a checkpoint remains implementation-dependent until the upstream state surface has been inspected. This choice requires an ADR once tested.
