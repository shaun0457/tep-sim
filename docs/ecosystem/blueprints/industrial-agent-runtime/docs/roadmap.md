# Roadmap — Industrial Agent Runtime

Implementation begins only after the program Phase 0 Design Freeze. The runtime roadmap then builds framework-neutral Hybrid mechanics in the smallest testable order.

Canonical specs live in `docs/specs/`.

## Phase 0 — Base contracts

Branch: `feat/contracts-runtime-v0`  
Specs: `runtime-v0.md`, `hybrid-orchestration-v0.md`

Implement:

- `Task`;
- `Budget`;
- `ToolSpec` / request/result;
- plan/plan-node contracts;
- `RuntimeResult`;
- `TraceEvent`;
- model-provider interface;
- deterministic fake provider;
- simple reference execution path.

Exit: fake-provider tests complete typed no-tool/read-tool tasks and represent valid/invalid plan data deterministically.

## Phase 1 — Hybrid Coordinator / Executor / Verifier

Branch: `feat/hybrid-orchestration-v0`  
Spec: `hybrid-orchestration-v0.md`

Implement:

- deterministic Coordinator;
- deterministic Executor;
- deterministic Verifier;
- direct/local Main-Agent routing;
- Dynamic DAG validation/scheduling primitives;
- plan revision tracking;
- hard stop/termination states;
- tool-exposure hook.

Exit:

- simple task avoids DAG overhead;
- valid bounded DAG executes;
- cycle/authority/budget violations fail before execution;
- missing evidence/artifact refs fail verification.

## Phase 2 — Generic deterministic gates

Branch: `feat/deterministic-gates-v0`  
Spec: `deterministic-gates-v0.md`

Implement schema/parse, tool allowlist, budget/recursion/plan-limit, side-effect, consumer-validator, and approval-state contracts.

Exit: denied operations provably do not execute and all gate decisions are traceable.

## Phase 3 — Ephemeral subagents

Branch: `feat/subagents-v0`  
Spec: `subagents-v0.md`

Implement:

- scoped child task/context/tools;
- EvidenceBundle;
- parent/child trace;
- configurable depth/count limits;
- no implicit child mutation authority;
- optional independent-node parallel scheduling behind same contract.

Exit: parent runs two bounded child analyses and consumes only structured evidence.

## Phase 4 — Context/reference discipline + observability

Implement:

- generic InformationRef/ContextBroker interfaces;
- visibility/budget hooks;
- artifact references;
- context projection/cache hooks;
- model/tool/subagent/plan accounting;
- deterministic trace export;
- duplicate/redundant work diagnostics.

Exit: a run can explain every model/plan/node/tool/subagent/gate transition without provider-specific objects or full transcript dependence.

## Phase 5 — LangGraph adapter

Branch: `feat/langgraph-adapter-v0`

Map framework-neutral Coordinator/state contracts to LangGraph for consumers that need:

- macro workflow graph;
- checkpoint/resume;
- human interrupts;
- durable structured state;
- graph observability.

This is an accepted adapter path, not a replacement for public runtime contracts.

Exit:

- same simple contract test runs with reference executor and adapter;
- adapter checkpoint/resume preserves task/plan/trace identity;
- core imports/public types remain usable without LangGraph-native state types.

## Phase 6 — First real model provider

Branch: `feat/provider-adapter-v0`

Choose one provider after core contracts are stable. Keep SDK objects behind the model interface.

Exit: the same smoke task runs under fake and real provider with identical public contract shape/tracing semantics.

## Phase 7 — First domain integration

Consume runtime from `tep-agent-lab`; never import TEP into core.

Required proof:

- domain Investigation State is supplied through consumer refs/projections;
- TEP tools register through generic ToolSpec;
- lab validators plug into consumer hooks;
- Tool Bridge results look like ordinary typed tools to runtime;
- Dynamic DAG can schedule isolated simulation/analysis/subtask nodes;
- core remains domain-free.

## Phase 8 — Performance/concurrency hardening

Only after correctness:

- choose asyncio/thread/process/job execution strategy where needed;
- parallel ready-node scheduling;
- backpressure/timeout handling;
- trace/checkpoint storage backend;
- provider rate-limit handling;
- benchmark runtime overhead.

Do not let concurrency implementation alter public semantic contracts.

## Not in v0 runtime roadmap

- global persistent learned memory;
- autonomous hiring/retiring organizations;
- unlimited recursive agents;
- peer-to-peer chat network;
- TEP/process safety rules;
- domain RAG/KG logic;
- arbitrary shell/code execution as default Tool Bridge.
