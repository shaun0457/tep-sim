# Industrial Agent Runtime Specifications

These v0 specs define the future `industrial-agent-runtime` repository.

- [`runtime-v0.md`](runtime-v0.md) — core task/tool/budget/provider/result contracts.
- [`hybrid-orchestration-v0.md`](hybrid-orchestration-v0.md) — Main Agent + deterministic Coordinator/Executor/Verifier, local ReAct, and bounded Dynamic DAG semantics.
- [`deterministic-gates-v0.md`](deterministic-gates-v0.md) — generic schema/permission/budget/side-effect gate model.
- [`subagents-v0.md`](subagents-v0.md) — bounded ephemeral-subagent semantics and EvidenceBundle contract.

The runtime is domain-independent. TEP topology, Rule Registry content, process safety truth, intervention limits, RCA/HAZOP/recovery logic, benchmark fixtures, and AutoResearch scoring remain in consumer/domain repositories.

The public contracts are framework-neutral. LangGraph may be used through an adapter but must not leak native state/message types into these contracts.
