# Cross-Repository Implementation Plan

This plan follows the independent design review, `design-review-adjudication.md`, focused re-review, `design-freeze-record.md`, and the implementation-driven Program Re-baseline v1.

**Phase 0 Design Freeze is complete.** The Playground/Application additions below are additive hosting/context contracts and do not reopen accepted World Plane, Control Plane, Information Plane, or investigation-state boundaries.

Implementation evidence may still reopen a contract through `SPEC_CONFLICT`; coding agents must not silently invent product architecture.

## Current implementation baseline

As of Program Re-baseline v1:

- `tep-sim` A1–A4 are implemented; A3's ProcessGraph/bindings are human verified: `tep-process-graph` 0.2.0 (`HUMAN_VERIFIED`) is the canonical graph for D0, and the curated 0.1.0 baseline stays immutable;
- `industrial-agent-runtime` B1–B3 are implemented;
- `tep-agent-lab` C1–C4 are implemented;
- C4 exposed the need for focused B2.1 request-bound reservation before D0;
- C5, P0 Playground Backend, B5 provider, D0, D1, and B4/D2 remain.

---

# Phase 0 — Design Review Closure — COMPLETE

Closed contracts include pre/post execution separation, generic refs/state contracts, explicit ModelTurn/state-update routing, atomic revision-bound updates, Observation versus Evidence, WorkBatch, extensible budgets, typed experiment objects, blind-RCA leakage restrictions, strong C0 baselines, Engineering Records, canonical evaluation matrices, and removal of LangGraph/MCP from the v0 critical path.

Review evidence:

- `reviews/2026-09-15-independent-spec-review.md`;
- `design-review-adjudication.md`;
- `reviews/2026-09-15-focused-re-review.md`;
- `design-freeze-record.md`.

---

# R0 — Program / Playground Re-baseline — DOCUMENTATION

Purpose: add one reproducible Application / Playground hosting layer before benchmark work creates a separate run/persistence/context stack.

Deliver:

- logical Application / Playground Plane while preserving three core repos;
- repository-backed canonical-context architecture with exact revision, governance metadata where applicable, visibility, and provenance;
- P0 backend contract in `tep-agent-lab`;
- B2.1 request-bound reservation milestone;
- B5 provider decoupled from B4 subagents;
- corrected dependency graph.

P0 is local-first/single-process. No mandatory FastAPI, Postgres, Redis, Kafka, vector database, RAG framework, distributed workers, or Kubernetes.

---

# Phase A — `tep-sim`: trusted world — IMPLEMENTED

## A1 — Environment adapter — COMPLETE

Spec: `docs/specs/environment-api-v0.md`

## A2 — Snapshot / fork / replay — COMPLETE

Spec: `docs/specs/snapshot-fork-replay-v0.md`

## A3 — DEXPI / ProcessGraph binding — COMPLETE, HUMAN VERIFIED

Spec: `docs/specs/dexpi-binding-v0.md`

Done before D0 benchmark freeze (handoff: `docs/a3-promotion-handoff.md`):

- human review of the curated topology/bindings: signed record `a3-process-graph-human-verification` 0.2.0, 88/88 ACCEPT;
- the XMEAS(22) nomenclature/source discrepancy is resolved and recorded (Q1, Option A; runtime name not renamed);
- the approved mapping is published as the new pinned fixture version `tep-process-graph` 0.2.0 plus evaluator fixture 0.2.0; the pinned 0.1.0 fixtures are unchanged.

Remaining non-blocking item: the F-11 paper-file rename (separate provenance-hygiene change).

## A4 — Capability / hard environment truth — COMPLETE

Spec: `docs/specs/safety-capability-v0.md`

---

# Phase B — `industrial-agent-runtime`: generic control plane

## B1 — Core contracts / reference loop — COMPLETE

Specs:

- `docs/specs/runtime-v0.md`
- `docs/specs/hybrid-orchestration-v0.md`

## B2 — Deterministic pre-execution gates — COMPLETE

Spec: `docs/specs/deterministic-gates-v0.md`

## B2.1 — Request-bound reservation — NEXT / REQUIRED BEFORE D0

Purpose: resolve C4 SC-5 while preserving D-037: **no budget-draw expression language**.

Direction:

- a trusted deterministic consumer/runtime contract may compute a request-specific exact reservation;
- runtime validates that reservation against ToolSpec-declared dimensions and `max_budget_draw`;
- final remaining-quota check/reservation/accounting remains generic runtime authority;
- no `eval`, expression parser, or Lab-side bypass;
- actual resource use is still reconciled after execution.

Before coding, update the owning runtime spec with the exact hook/stage ordering and fail-closed behavior. This plan deliberately does not invent that public API.

## B3 — Post-execution verification / deterministic ingestion — COMPLETE

## B4 — Ephemeral subagents — DEFERRED UNTIL D2/O5

Branch: `feat/subagents-v0`  
Spec: `docs/specs/subagents-v0.md`

B4 does **not** block D0 or the first single-Agent D1 run. Implement it before the O5 bounded-SUBTASK orchestration condition.

## B5 — First real provider — REQUIRED BEFORE D1, NOT D0

Branch: `feat/provider-adapter-v0`

B5 may proceed after B1–B3 independently of B4 and independently of D0 benchmark construction.

Add one provider only after fake-provider contracts pass. Provider SDK types stay behind the internal model interface.

B5 is a D1 blocker because the first Blind RCA capability study requires a real model; it is **not** a D0 benchmark/C0 prerequisite.

## Explicitly not scheduled in B v0

- LangGraph adapter;
- MCP runtime dependency;
- general mutable Dynamic DAG engine.

---

# Phase C — `tep-agent-lab`: first RCA information/investigation plane

## C1 — RCA state / run log / projection — COMPLETE

Specs:

- `docs/specs/investigation-state-v0.md`
- `docs/specs/engineering-records-v0.md`
- program `information-plane.md`

## C2 — Rule/policy metadata — COMPLETE

Spec: `docs/specs/knowledge-rule-registry-v0.md`

## C3 — Hypothesis / Prediction / Experiment — COMPLETE

Spec: `docs/specs/hypothesis-experiment-v0.md`

## C4 — TEP tool surface — COMPLETE

Spec: `docs/specs/tool-surface-v0.md`

Blind-RCA surface provides bounded READ/SIMULATE tools, hidden-truth isolation, artifact-backed dense telemetry, baseline-lineage counterfactual scenarios, and no MUTATE/default cause enumeration.

## C5 — Minimal Tool Bridge — NEXT

Branch: `feat/tool-bridge-v0`  
Spec: `docs/specs/tool-bridge-v0.md`

First implementation only:

1. response-feature extraction;
2. deterministic trajectory comparison;
3. cross-correlation/lag;
4. optional existing TEP detector baseline only if D0 requires it.

Defer SALib/Optuna/PCA/PLS/Granger until a concrete experiment requires them.

C5 remains an adapter/provider layer; runtime retains authorization/budget/execution authority.

---

# Phase P — Playground application/backend

## P0 — Minimal Playground Backend — REQUIRED BEFORE D0 FREEZE

Owner repo: `tep-agent-lab`  
Owning spec: `shaun0457/tep-agent-lab:docs/specs/playground-backend-v0.md`

Deliver one local reproducible run path:

- immutable `RunManifest` published at READY plus separate terminal `RunOutcome`;
- minimal application `RunStatus` lifecycle and `RunManager` distinct from runtime `TaskStatus`;
- `CanonicalContextRegistry` / `ContextSourceRef` resolver over exact repository revisions;
- context-source inventory frozen at READY and not model-authored;
- transport-neutral read/query projections;
- ProcessGraph/P&ID-like process view;
- telemetry / investigation / branch-tree / budget / event views;
- exact-ref/checksum artifact access;
- AGENT vs EVALUATOR projection boundaries.

P0 does not create a second TaskStateStore, ProcessWorld, trace/evidence ontology, scheduler, or tool authority path. Existing runtime/lab/world stores remain canonical; application views are derived projections.

P0 is intentionally local-first/single-process. HTTP/streaming adapters and polished UI are later consumers, not required P0 infrastructure.

## P1 — Investigation UI — AFTER D0, CAN RUN ALONGSIDE D1

Initial UI slice may visualize:

- P&ID-like ProcessGraph / flow topology;
- current telemetry/safety;
- investigation hypotheses/evidence;
- simulation branch tree;
- run/tool/budget event timeline.

P1 is not a D0 blocker and must consume P0 projections rather than reaching directly into simulator/runtime internals.

---

# Phase D — first RCA research

## D0 — Benchmark/identifiability/C0 pilot

Branch: `exp/rca-benchmark-pilot-v0`

Specs:

- `docs/specs/benchmark-design-v0.md`
- `docs/specs/evaluation-v0.md`
- `docs/specs/rca-v0.md`

Prerequisites for benchmark freeze:

- B2.1 request-bound reservation;
- C5 minimal Tool Bridge;
- A3 human-reviewed ProcessGraph/bindings (done: `tep-process-graph` 0.2.0);
- P0 reproducible run/context/projection path.

**B5 is not a D0 prerequisite.** D0/C0 can remain deterministic/fake-provider where appropriate.

Deliver before Agent superiority claims:

- scenario variants;
- strong C0 enumerate/simulate/match baseline;
- healthy/no-abnormal case;
- candidate/topology/context leakage audit;
- data-informed difficulty labels;
- at least one non-local/nontrivial case for medium/hard investigation claims;
- explicit counterfactual-origin timing/seed visibility policy so exact baseline replay does not accidentally create a hidden-timing oracle;
- versioned canonical context source refs and evaluator-only ground-truth refs.

## D1 — Blind RCA capability ladder

Branch: `exp/rca-reactor-v0`

Prerequisites:

- D0 frozen benchmark;
- B5 real provider;
- C1–C5/P0 required Agent-visible infrastructure.

Use the canonical capability axis in `evaluation-v0.md`.

Start single-Agent. Do not add subagents as a capability row.

## D2 — Orchestration ablation

Branch: `exp/orchestration-ablation-v0`

Canonical conditions:

```text
O0 one-shot
O1 ReAct
O2 fixed workflow
O3 Hybrid reference loop
O4 O3 + dependency-aware TOOL WorkBatch
O5 O4 + bounded SUBTASK work
```

B4 is required before O5 only.

Use identical Agent-visible capability/tool/context policy across O1–O5 unless exposure itself is explicitly being studied.

The value of WorkBatch/subagents is measured rather than assumed.

---

# Phase E — later task families

Only after RCA environment/tracing/evaluation contracts are stable.

## E1 — Simulation-backed HAZOP

Branch: `exp/hazop-reactor-v0`

## E2 — Recovery planning

Branch: `exp/recovery-reactor-v0`

Rank forked strategies first. Reference MUTATE remains disabled until state-revision-bound validation/gates are proven.

## E3 — AutoProcessResearch

Branch: `exp/autoresearch-recovery-v0`

Only after deterministic recovery/scoring/search-space contracts exist.

AutoProcessResearch remains a separate research task family, not an orchestration-ablation condition.

---

# Phase F — optional knowledge / organizational memory

After clean no-KG/no-memory baselines:

- connect `manufacturing-kg-agent` through read-only evidence adapters;
- validate literature/document candidates;
- implement KnowledgePromotionProposal/ValidationPlan/ValidationResult/PromotionDecision if needed;
- study structured Engineering Record retrieval across incidents;
- compare no-history vs record retrieval vs approved rule/runbook retrieval;
- add subsystem/fault families;
- detector-triggered start.

Canonical context does not imply automatic retrieval or learned memory: repository-backed reviewed truth and cross-run memory are separate concerns.

Lesson Learned/Runbook/manual promotion must be evaluated/authority-governed rather than automatically generated from one incident.

Still out of scope: generic P&ID OCR/model generation and 3D reconstruction.

---

# Parallel development after re-baseline

Use `development-agent-orchestration.md` and `development-workflow.md`.

A coding agent receives:

```text
repo/branch
canonical spec
owned files/modules
dependencies
acceptance tests
handoff contract
```

On spec conflict it reports `SPEC_CONFLICT`; it does not silently redesign architecture.

## Dependency graph

```text
A1-A4 complete          B1-B3 complete          C1-C4 complete
      \                       |                       /
       +-------------- Program R0 ------------------+
                              |
             +----------------+----------------+
             |                |                |
           B2.1              C5     A3 human review (done)
             |                |                |
             +----------------+----------------+
                              |
                              v
                             P0
                              |
                              v
                        D0 benchmark/C0
                         /           \
                        v             v
                     P1 UI          D1 RCA <------ B5 provider
                                      |
                                      v
                                 B4 + D2/O5
                                      |
                               E1/E2/E3 later
                                      |
                           F knowledge/memory studies
```

B5 is independent of D0 and may be implemented in parallel any time after R0/B1–B3; it joins the dependency graph only at D1.

Independent branches may run in parallel when their upstream frozen contracts are available and file/module ownership does not overlap. Completion race does not change integration order.
