# Roadmap — Industrial Agent Runtime

Runtime implementation begins only after focused Design Freeze re-review closes the current proposal contracts. Build the smallest testable domain-independent runtime first.

Canonical specs live in `docs/specs/`.

## Phase 0 — Core contracts / reference loop

Branch: `feat/contracts-runtime-v0`

Specs:

- `runtime-v0.md`
- `hybrid-orchestration-v0.md`

Implement:

- InformationRef;
- Task;
- Budget + `extra_dimensions`;
- ToolSpec/request/result + budget-draw metadata;
- TaskStatus / StateDelta / ContextProjection / TaskStateStore protocol;
- WorkBatch / WorkItem;
- RuntimeResult / TraceEvent;
- fake model provider;
- simple reference control loop/dispatcher;
- exact ContextProjection tracing per model turn.

Exit:

- fake-provider no-tool/read-tool task passes;
- fake consumer TaskStateStore works without runtime importing consumer class;
- valid dependency-aware TOOL WorkBatch runs deterministically;
- cyclic/over-budget work is denied;
- no LangGraph/MCP dependency is required.

## Phase 1 — Pre-execution deterministic gates

Branch: `feat/deterministic-gates-v0`  
Spec: `deterministic-gates-v0.md`

Implement:

- G0 schema/parse;
- G1 allowlist/authority;
- G2 standard + extra-dimensional reservation/recursion;
- G3 side-effect policy;
- consumer `validate_request` hook;
- frozen-request state revision binding for MUTATE;
- GateDecision tracing.

Exit: denied operations do not dispatch and compound resource requests cannot bypass budgets.

## Phase 2 — Post-execution verification

Implement as a small deterministic runtime module/hook, not another Agent/service.

Checks:

- output/ref/artifact existence;
- actual-vs-reserved budget reconciliation;
- required provenance/version metadata;
- WorkBatch dependency completion;
- consumer `verify_result` invariants;
- final structural readiness.

Exit: invalid/missing refs or resource/provenance inconsistencies are rejected/recorded after dispatch before state application.

## Phase 3 — Ephemeral subagents

Branch: `feat/subagents-v0`  
Spec: `subagents-v0.md`

Implement:

- scoped child task/context/tools;
- cumulative per-task child budget;
- `SubtaskResult`;
- parent/child trace;
- no child MUTATE;
- no nested SUBTASK bypass at depth limit;
- ready-child parallelism behind same WorkBatch semantics.

Exit: parent runs bounded children and receives compact SubtaskResults only.

## Phase 4 — First real model provider

Branch: `feat/provider-adapter-v0`

Choose one provider only after fake-provider/core contract tests pass. SDK objects stay internal.

Exit: same smoke task runs under fake and real provider with identical public contract shape/tracing requirements.

## Phase 5 — First domain integration

Consume runtime from `tep-agent-lab`; do not import TEP into runtime.

Proof:

- lab implements TaskStateStore with RcaState;
- TEP/Tool Bridge adapters register through ToolSpec;
- lab request/result validators plug into generic hooks;
- compound SIMULATE resource use is visible to runtime;
- subtask results remain domain-agnostic envelopes;
- core remains domain-free.

## Phase 6 — Correctness-first concurrency hardening

Only after semantic correctness:

- choose asyncio/thread/process/job execution strategy if needed;
- enforce `max_parallel_width`/backpressure;
- timeouts/cancellation of local dispatch;
- provider rate-limit handling;
- persistence backend optimizations.

Concurrency must not alter public WorkBatch/budget/state semantics.

## Deferred / not scheduled for runtime v0

### Full Dynamic DAG engine

No mutable graph-revision/cancellation/MERGE-node engine until an orchestration study justifies/specifies it.

### LangGraph adapter

Not scheduled until a concrete checkpoint/resume/interrupt/persistent-graph requirement exists.

### MCP

Not a runtime dependency. May later be one Tool Provider protocol behind registered adapters.

### Other non-goals

- global learned memory;
- autonomous organization/hiring;
- unlimited recursive agents;
- peer-to-peer chat network;
- domain safety/rules/RAG/KG;
- scientific Tool Bridge implementations;
- arbitrary shell/code execution as default tool.
