# Cross-Repository Implementation Plan

This plan is **not authorization to implement immediately**. Core architecture/spec decisions must pass Phase 0 Design Freeze first. After freeze, work may be parallelized across coding agents/subagents using small spec-scoped branches.

## Phase 0 — Architecture / Spec Freeze

**Goal:** remove architectural ambiguity before implementation branches diverge.

Required accepted/reviewed contracts:

### Program level

- three-repository boundary;
- Autonomous Investigator v0 role / long-term Process Engineer direction;
- Information Plane ownership/reference model;
- deterministic knowledge authority and provenance policy;
- development/parallel-agent workflow.

### `industrial-agent-runtime`

- `runtime-v0.md`;
- `hybrid-orchestration-v0.md`;
- `deterministic-gates-v0.md`;
- `subagents-v0.md`;
- Coordinator/Executor/Verifier responsibility boundary;
- framework-neutral contract / LangGraph adapter boundary.

### `tep-agent-lab`

- `investigation-state-v0.md`;
- `knowledge-rule-registry-v0.md`;
- `hypothesis-experiment-v0.md`;
- `tool-surface-v0.md`;
- `tool-bridge-v0.md`;
- `evaluation-v0.md`;
- RCA/HAZOP/recovery contracts;
- `autoresearch-v0.md`.

### Freeze exit criteria

- no canonical document contradicts the Decision Register;
- every accepted decision has an owner/spec/ADR or explicit minimal contract;
- remaining unknowns are empirical/implementation questions, not unresolved core architecture;
- branch dependency graph is explicit;
- implementation agents can work from specs without inventing product architecture.

Until these criteria are met, do not start broad feature implementation merely because an older roadmap says to.

---

## Phase A — `tep-sim`: trusted world

### A1 — Environment adapter

Branch: `feat/environment-api-v0`  
Spec: `docs/specs/environment-api-v0.md`

Deliver `TEPEnvironment`, canonical config/observation/intervention/result contracts, run provenance, and baseline tests.

### A2 — Snapshot / fork / replay

Branch: `feat/snapshot-fork-v0`  
Spec: `docs/specs/snapshot-fork-replay-v0.md`

Deliver fidelity investigation, isolated branches, replay/provenance, explicit `EXACT`/`RECONSTRUCTED`/`UNSUPPORTED` state.

### A3 — DEXPI / ProcessGraph binding

Branch: `feat/dexpi-binding-v0`  
Spec: `docs/specs/dexpi-binding-v0.md`

Deliver pinned TEP semantic fixture, normalized graph, topology queries, variable binding registry, and validation tests.

### A4 — Capability / hard safety truth

Branch: `feat/capability-safety-v0`  
Spec: `docs/specs/safety-capability-v0.md`

Deliver capability registry, minimal deterministic scenario compilation, hard safety/capability evaluation, explicit unsupported-physics behavior.

---

## Phase B — `industrial-agent-runtime`: hybrid control plane

### B1 — Contracts / state-independent executor primitives

Branch: `feat/contracts-runtime-v0`

Implement Task/Budget/ToolSpec/ToolResult/TraceEvent/RuntimeResult, fake provider, trace recorder, and framework-neutral interfaces.

### B2 — Hybrid Coordinator / Executor / Verifier

Branch: `feat/hybrid-orchestration-v0`  
Spec: `docs/specs/hybrid-orchestration-v0.md`

Deliver deterministic Coordinator/Executor/Verifier, local Main-Agent loop, plan routing, stop/termination handling, and Dynamic DAG proposal/validation primitives.

Exit:

- simple task runs without DAG;
- valid bounded DAG executes;
- cyclic/over-authority DAG fails before execution;
- deterministic verifier catches invalid refs/contracts.

### B3 — Deterministic gates

Branch: `feat/deterministic-gates-v0`

Implement schema, allowlist, budget, authority/side-effect gates and consumer-validator hook.

### B4 — Ephemeral subagents

Branch: `feat/subagents-v0`

Implement bounded child tasks, isolated context, EvidenceBundle, parent-child trace, configurable depth/count limits.

### B5 — LangGraph adapter

Branch: `feat/langgraph-adapter-v0`

Only after B1–B4 contracts stabilize. Map generic state/coordinator semantics to LangGraph without exposing LangGraph types in public contracts.

Use it first from `tep-agent-lab` for macro workflow/checkpointing. The generic runtime remains usable without it.

### B6 — Real provider adapter

Branch: `feat/provider-adapter-v0`

Add one reliable provider behind the generic model interface. Freeze provider/model version per benchmark run.

---

## Phase C — `tep-agent-lab`: information + investigation plane

### C1 — Investigation State / Information refs

Branch: `feat/investigation-state-v0`

Implement typed InvestigationState, EvidenceStore refs, ExperimentLedger refs, revisions/deltas, context projection, and evaluator visibility separation.

### C2 — Knowledge / Rule Registry

Branch: `feat/rule-registry-v0`

Implement K0–K4 metadata model, rule provenance/versioning, enforcement classes, candidate extraction/promotion records, and hard-authority restrictions.

Initial implementation may contain only a few representative rules; architecture/provenance correctness matters more than rule count.

### C3 — Hypothesis / Experiment contracts

Branch: `feat/hypothesis-experiment-v0`

Implement first-class hypotheses, evidence links, experiment proposals/run specs/results, deterministic compilation, duplicate ledger checks.

### C4 — Environment + analysis Tool Surface

Branch: `feat/tool-surface-v0`

Expose TEP observation/topology/fork/rollout/capability tools plus stable bridge interfaces.

### C5 — Tool Bridge

Branch: `feat/tool-bridge-v0`

Bridge mature allowlisted scientific libraries and upstream TEP analysis capabilities. Initial candidates:

- upstream TEP detectors;
- SciPy signal/lag features;
- selected scikit-learn PCA/PLS baselines;
- graph algorithms;
- SALib sensitivity analysis;
- Optuna-style bounded numeric optimization.

No arbitrary agent Python/shell/import tool is introduced as the normal analysis path.

---

## Phase D — first agent research benchmarks

### D1 — Blind RCA baseline

Branch: `exp/rca-reactor-v0`

Start with Main Agent under fixed capability budget. Add counterfactual simulation after read/topology baseline.

### D2 — Orchestration ablation

Branch: `exp/orchestration-ablation-v0`

Compare, over the same capability set where practical:

```text
one-shot
ReAct
fixed DAG
Hybrid macro + ReAct
Hybrid + Dynamic DAG
Hybrid + Dynamic DAG + bounded subagents
```

Dynamic DAG/subagent value must be measured rather than assumed.

### D3 — Simulation-backed HAZOP

Branch: `exp/hazop-reactor-v0`

Use curated supported/unsupported deviations and Rule/Capability registries.

### D4 — Recovery planning

Branch: `exp/recovery-reactor-v0`

Rank forked strategies against no-action/deterministic baselines. Reference mutation remains gated and may stay disabled in early runs.

---

## Phase E — AutoProcessResearch

Only after deterministic recovery/scoring/tool infrastructure is reliable.

### E1 — Research loop / Experiment Ledger

Branch: `exp/autoresearch-recovery-v0`  
Spec: `docs/specs/autoresearch-v0.md`

Deliver frozen ResearchSpec/evaluator, baseline, candidate/ledger loop, accept/reject/neutral policy, deterministic stop conditions, hidden evaluation.

### E2 — Deterministic optimizer bridge

Compare Agent-only candidate selection with Agent mechanism selection + bounded numeric optimizer.

### E3 — Dynamic DAG research trials

Optionally parallelize independent scenario/seed evaluations inside one fixed trial budget.

---

## Phase F — knowledge augmentation / expansion

After clean no-KG baselines:

- integrate `manufacturing-kg-agent` through read-only evidence tools;
- evaluate paper/document K3 candidate extraction;
- run K3 -> K2 validation campaigns;
- add more TEP subsystem/fault families;
- test detector-triggered incident start;
- evaluate cross-incident memory separately if justified;
- build 2D process/branch investigation UI if useful.

Still out of scope: generic P&ID OCR/model generation and 3D digital-twin reconstruction.

## Evaluation is continuous

`evaluation-v0.md` applies from the first benchmark onward. Every architecture/capability extension must preserve comparable traces and score:

- task outcome;
- scientific/investigation behavior;
- cost/efficiency;
- safety/authority compliance;
- reproducibility.

## Post-freeze parallel development

After Phase 0, independent branches MAY be executed by multiple coding agents in parallel when file/module ownership and dependencies do not overlap. Parallelism follows `development-workflow.md`; integration order follows this dependency chain, not completion race.

## Critical dependency graph

```text
tep-sim A1 -> A2 -> A3/A4

runtime B1 -> B2 -> B3
                 -> B4
                 -> B5 adapter

lab C1 + C2 + C3
        |    |
        +----+----> C4/C5 tools
                     |
                     v
                  D1 RCA
                     |
                  D2 orchestration ablation
                     |
               D3 HAZOP / D4 Recovery
                     |
                  E AutoResearch
```

The exact branches may overlap after contracts are frozen, but downstream labs must pin known upstream contract versions.
