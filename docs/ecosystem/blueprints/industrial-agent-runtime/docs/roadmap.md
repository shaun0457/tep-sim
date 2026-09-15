# Roadmap — Industrial Agent Runtime

The runtime roadmap builds generic mechanics in the smallest testable order. It does not wait for TEP integration to validate core behavior.

Canonical specs live in `docs/specs/`.

## Phase 0 — Contracts first

Branch: `feat/contracts-executor-v0`  
Spec: `docs/specs/runtime-v0.md`

Implement:

- `Task`;
- `Budget`;
- `ToolSpec`;
- `ToolCallRequest`;
- `ToolResult`;
- `RuntimeResult`;
- `TraceEvent`;
- deterministic fake model provider;
- minimal explicit executor/state machine.

Exit: fake-provider tests complete typed no-tool and read-tool tasks deterministically.

## Phase 1 — Generic deterministic gates

Branch: `feat/deterministic-gates-v0`  
Spec: `docs/specs/deterministic-gates-v0.md`

Implement:

- schema/parse gate;
- tool allowlist gate;
- budget/recursion gate;
- side-effect class gate;
- consumer/domain-validator hook;
- structured denial/approval decisions;
- fail-closed behavior.

Exit: denied operations provably do not execute and all gate decisions are traceable.

## Phase 2 — Ephemeral subagents

Branch: `feat/subagents-v0`  
Spec: `docs/specs/subagents-v0.md`

Implement proposed v0 policy:

- depth 1 by default;
- max 3 children per parent by default;
- no child reference-world mutation authority;
- scoped context/tool subset;
- `EvidenceBundle` result;
- parent-child trace links;
- deterministic depth/count enforcement.

Exit: parent runs two independent child analyses and consumes only compact structured evidence.

## Phase 3 — Context discipline and observability

Harden:

- context-reference abstraction;
- artifact references instead of transcript/data dumping;
- token/model/tool/subagent accounting;
- static tool-schema caching where useful;
- deterministic trace export;
- duplicate/redundant subtask diagnostics.

Exit: one run can explain every model/tool/subagent/gate step and its resource usage without requiring provider-specific internal objects.

## Phase 4 — First real model provider

Branch: `feat/provider-adapter-v0`

Choose one provider only after core contracts are stable. Keep provider SDK objects behind the model interface.

Exit: one integration smoke task can run under both fake and real provider with the same public `Task`/result contracts.

## Phase 5 — First domain integration

Consume the runtime from `tep-agent-lab`; do not import TEP into this repository.

Required proof:

- TEP tools register through generic `ToolSpec`;
- lab domain validators plug into the consumer-validator hook;
- simulation tools remain isolated;
- subagent context is TEP-specific only because the lab supplies it;
- core runtime remains domain-free.

## Phase 6 — Optional LangGraph / approval adapter

Only implement after a real consumer requires at least one of:

- durable checkpoint/resume;
- human approval interrupts;
- long-running resumable tasks;
- persistent graph state across process restarts.

The explicit executor remains the semantic reference implementation. Public contracts must not become LangGraph-specific.

## Not in v0 roadmap

- global persistent memory;
- autonomous hiring/retiring organization;
- unlimited recursive agents;
- peer-to-peer agent chat network;
- TEP/process safety rules;
- domain-specific RAG/KG logic.
