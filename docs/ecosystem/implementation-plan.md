# Cross-Repository Implementation Plan

This plan converts the program charter and v0 specs into small implementation branches. It is intentionally ordered to prove environment correctness before agent complexity.

## Phase A — `tep-sim`: trusted environment

### A1 — Environment adapter

Branch: `feat/environment-api-v0`  
Canonical spec: `docs/specs/environment-api-v0.md`

Deliver:

- `TEPEnvironment` adapter;
- canonical config/observation/intervention/result contracts;
- control-mode validation;
- run provenance;
- deterministic baseline tests.

Exit: environment API acceptance tests pass without any agent dependency.

### A2 — Snapshot / fork / replay

Branch: `feat/snapshot-fork-v0`  
Canonical spec: `docs/specs/snapshot-fork-replay-v0.md`

Deliver:

- snapshot fidelity investigation;
- branch identity/provenance;
- isolated fork semantics;
- replay test;
- explicit `EXACT`/`RECONSTRUCTED`/`UNSUPPORTED` fidelity status.

Exit: two branches can diverge without cross-contamination and reproducibility is quantified.

### A3 — DEXPI/process semantics

Branch: `feat/dexpi-binding-v0`  
Canonical spec: `docs/specs/dexpi-binding-v0.md`

Deliver:

- pinned machine-readable TEP semantic fixture;
- normalized `ProcessGraph`;
- canonical topology queries;
- variable binding registry;
- validation tests including reactor cooling path.

Exit: code can query reactor topology and resolve known XMEAS/XMV relations deterministically.

### A4 — Capability / safety

Branch: `feat/capability-safety-v0`  
Canonical spec: `docs/specs/safety-capability-v0.md`

Deliver:

- capability registry;
- deterministic scenario compiler for a minimal supported set;
- deterministic safety evaluation;
- explicit unsupported physics tests.

Exit: supported and unsupported scenarios are machine-distinguishable before mutation.

## Phase B — `industrial-agent-runtime`: minimal agent mechanics

### B1 — Contracts + executor

Branch: `feat/contracts-executor-v0`  
Canonical spec: `docs/specs/runtime-v0.md`

Deliver:

- Task/Budget/ToolSpec/ToolResult/TraceEvent/RuntimeResult contracts;
- fake provider;
- explicit bounded executor;
- read-only tool loop;
- trace recorder.

Exit: fake-provider tests complete typed tasks deterministically.

### B2 — Deterministic gates

Branch: `feat/deterministic-gates-v0`  
Canonical spec: `docs/specs/deterministic-gates-v0.md`

Deliver schema, allowlist, budget, side-effect-class gates and consumer-validator hook.

Exit: denied tool requests provably do not execute and all decisions are traced.

### B3 — Ephemeral subagents

Branch: `feat/subagents-v0`  
Canonical spec: `docs/specs/subagents-v0.md`

Deliver bounded child tasks, context isolation, `EvidenceBundle`, parent-child tracing, and depth/count enforcement.

Exit: two child analyses complete and parent receives only structured evidence.

### B4 — First real provider

Branch: `feat/provider-adapter-v0`

Decision remains open until B1 contracts are stable. Add one provider adapter without leaking provider objects into public contracts.

Exit: the same integration smoke task can run under fake and real provider.

## Phase C — `tep-agent-lab`: first agent world

### C1 — Tool surface

Branch: `feat/tool-surface-v0`  
Canonical spec: `docs/specs/tool-surface-v0.md`

Deliver adapters from generic runtime ToolSpec to `tep-sim` observation, topology, snapshot/fork/rollout, capability, and proposal-validation operations.

Exit: agent tools expose compact domain evidence and hidden truth remains unreachable.

### C2 — RCA benchmark

Branch: `exp/rca-reactor-v0`  
Canonical spec: `docs/specs/rca-v0.md`

Deliver versioned reactor/cooling-water fixtures, agent-visible projection, scorer, baselines B1–B5 where supported, and run reports.

Exit: at least one blind incident is reproducibly investigated with counterfactual evidence.

### C3 — Simulation-backed HAZOP

Branch: `exp/hazop-reactor-v0`  
Canonical spec: `docs/specs/hazop-v0.md`

Deliver bounded reactor/cooling deviation set, supported/unsupported cases, structured finding schema, and evidence validation.

Exit: at least one supported and one unsupported deviation are handled correctly.

### C4 — Recovery planning

Branch: `exp/recovery-reactor-v0`  
Canonical spec: `docs/specs/recovery-v0.md`

Deliver candidate strategy generation, forked evaluation, deterministic metric vector, domain gate policy, and post-action verification. Reference mutation may remain disabled until gates pass.

Exit: candidate strategies can be ranked against no-action/deterministic baselines; one gated application path is testable when enabled.

### C5 — Evaluation suite

Evaluation is introduced from C2 onward and consolidated under `docs/specs/evaluation-v0.md`.

Exit: identical saved traces re-score deterministically and ablation reports separate task quality from resource/agent behavior.

## Phase D — optional extensions after v0

Only after A–C are stable:

- external knowledge/KG evidence ablation;
- detector-triggered incident start instead of fixture start;
- persistent LangGraph adapter/human interrupt;
- longer subagent depth if evidence supports it;
- cross-incident memory experiment;
- 2D interactive process/branch visualization;
- additional TEP subsystems/fault families.

Generic P&ID OCR/model generation and 3D digital-twin reconstruction are not on this plan.

## Critical path

The shortest path to the first meaningful result is:

```text
A1 environment API
 -> A2 fork
 -> A3 minimal topology/bindings
 + B1 executor
 + B2 gates
 -> C1 tool surface
 -> C2 RCA benchmark
```

HAZOP and recovery should not delay the first RCA end-to-end experiment.
