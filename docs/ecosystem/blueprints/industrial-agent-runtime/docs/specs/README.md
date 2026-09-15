# Industrial Agent Runtime Specifications

These are v0 proposal specs for the future `industrial-agent-runtime` repository.

- [`runtime-v0.md`](runtime-v0.md) — main execution model and core contracts.
- [`subagents-v0.md`](subagents-v0.md) — bounded ephemeral-subagent semantics.
- [`deterministic-gates-v0.md`](deterministic-gates-v0.md) — generic permission/budget/side-effect gate model.

The runtime is domain-independent. TEP-specific topology, safety truth, intervention limits, RCA logic, HAZOP logic, and recovery scoring must remain outside this repository.
