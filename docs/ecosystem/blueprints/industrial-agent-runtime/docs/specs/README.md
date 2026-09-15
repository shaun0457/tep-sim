# Industrial Agent Runtime Specifications

These proposal specs define the future `industrial-agent-runtime` repository.

- [`runtime-v0.md`](runtime-v0.md) — generic refs/state interfaces, Task/Budget/ToolSpec, ContextProjection, WorkBatch, trace/provider/result contracts.
- [`hybrid-orchestration-v0.md`](hybrid-orchestration-v0.md) — Main Agent + deterministic request gates/Executor/post-result verifier and dependency-aware WorkBatch semantics.
- [`deterministic-gates-v0.md`](deterministic-gates-v0.md) — pre-execution schema/authority/budget/side-effect/resource-reservation and consumer `validate_request` contract.
- [`subagents-v0.md`](subagents-v0.md) — bounded ephemeral subtasks and `SubtaskResult` contract.

The runtime is domain-independent. TEP topology, domain state, Tool Bridge implementations, Rule content, process safety truth, RCA/HAZOP/recovery logic, benchmark fixtures, and evaluation remain in consumer/domain repositories.

v0 does not require a general Dynamic DAG engine, LangGraph, or MCP. Public contracts remain serializable/framework-neutral so later adapters can be added without changing domain/runtime ownership.
