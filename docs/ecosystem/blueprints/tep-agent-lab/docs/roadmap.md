# Roadmap — TEP Agent Lab

Implementation begins only after the program Phase 0 Design Freeze. The lab then builds the minimum information/tool/evaluation substrate needed to study Agent behavior before adding increasingly complex research modes.

Canonical specs live in `docs/specs/`.

## Phase 0 — Reproducible lab / benchmark shell

Specs: `evaluation-v0.md`, `benchmark-design-v0.md`

Deliver:

- pinned `tep-sim` and `industrial-agent-runtime` revisions;
- versioned case/scenario-family schema;
- development/research/hidden-eval partitions;
- evaluator-only vs Agent-visible projection;
- run/artifact manifest;
- leakage audit;
- deterministic re-scoring;
- first identifiability pilot utilities.

Exit: a minimal/fake run can be projected, traced, re-scored, and leakage-tested reproducibly.

## Phase 1 — Information Plane / Investigation State

Branch: `feat/investigation-state-v0`  
Spec: `investigation-state-v0.md`

Deliver:

- typed InvestigationState + revisions/deltas;
- EvidenceStore refs;
- ExperimentLedger refs;
- context projection;
- open-question/delegation/experiment summaries;
- semantic stop-readiness fields;
- evaluator visibility separation.

Exit: one investigation is reconstructable without relying on chat transcript as canonical state.

## Phase 2 — Rule / knowledge authority

Branch: `feat/rule-registry-v0`  
Spec: `knowledge-rule-registry-v0.md`

Deliver:

- K0–K4 metadata model;
- K2/K3 lab registry;
- enforcement classes;
- source/validation/version provenance;
- K3 candidate + validation-campaign records;
- conflict/deprecation representation;
- hard-authority restrictions.

Exit: one paper-derived K3 candidate and one simulator/runtime K0 rule coexist without authority confusion; a K3 rule cannot become a blocking gate directly.

## Phase 3 — Hypothesis / Experiment contracts

Branch: `feat/hypothesis-experiment-v0`  
Spec: `hypothesis-experiment-v0.md`

Deliver:

- Hypothesis + evidence links;
- ExperimentProposal;
- frozen ExperimentRunSpec;
- deterministic ExperimentResult;
- model ExperimentInterpretation;
- ledger duplicate checks;
- provenance to tools/rules/artifacts.

Exit: two competing hypotheses can be tested by one traceable discriminating experiment and updated from deterministic result evidence.

## Phase 4 — TEP environment tools + Tool Bridge

Branches:

```text
feat/tool-surface-v0
feat/tool-bridge-v0
```

Specs: `tool-surface-v0.md`, `tool-bridge-v0.md`

### Environment tools

- observations/history;
- ProcessGraph/topology/bindings;
- snapshot/fork/rollout;
- capability/safety;
- proposal/validation skeleton.

### Initial analysis bridge

Start minimal and benchmark-driven:

- upstream TEP detector/analysis capability adapters;
- SciPy response/correlation/lag features;
- graph utilities;
- selected PCA/PLS baseline tools as needed.

Sensitivity/optimization dependencies are introduced when AutoResearch requires them.

Exit: Hybrid runtime can inspect/analyze/simulate TEP only through typed, versioned, leakage-audited tools; arbitrary Agent Python/shell/import is unavailable.

## Phase 5 — Blind RCA baseline

Branch: `exp/rca-reactor-v0`  
Spec: `rca-v0.md`

Use the reactor/cooling-water scenario family selected by the identifiability pilot.

Capability progression:

```text
static context
 -> telemetry
 -> topology
 -> analysis Tool Bridge
 -> counterfactual simulation
```

Start with a single Main Agent and fixed budgets before Dynamic DAG/subagent complexity.

Exit: at least one blind incident is reproducibly investigated with evidence-backed hypotheses and counterfactual results.

## Phase 6 — Orchestration architecture ablation

Branch: `exp/orchestration-ablation-v0`  
Spec: `evaluation-v0.md` + runtime Hybrid spec

Hold capability set as constant as practical and compare:

```text
one-shot
ReAct
fixed workflow/DAG
Hybrid deterministic macro + local ReAct
Hybrid + Dynamic DAG
Hybrid + Dynamic DAG + bounded subagents
```

Measure final diagnosis, scientific behavior, DAG/subagent overhead, tool/rollout/tokens, and stopping efficiency.

Exit: Dynamic DAG/subagent policy is retained/adjusted from evidence rather than assumed better.

## Phase 7 — Simulation-backed HAZOP

Branch: `exp/hazop-reactor-v0`  
Spec: `hazop-v0.md`

Start with reactor/cooling subsystem and a small supported/unsupported deviation pack.

Use Rule/Capability registries and evidence-backed rollouts.

Exit: supported scenarios produce traceable process/safety evidence; unsupported physics is reported honestly.

## Phase 8 — Recovery planning

Branch: `exp/recovery-reactor-v0`  
Spec: `recovery-v0.md`

Deliver:

- allowed action/search space per fixture;
- candidate strategy generation;
- forked evaluation + no-action/deterministic baseline;
- deterministic metric vector/scorer;
- layered gates;
- verification contract.

Initially rank strategies only. Enable reference application only after gate/verification tests and explicit benchmark policy permit it.

Exit: recovery candidates are reproducibly ranked, with at least one validated application path available when enabled.

## Phase 9 — AutoProcessResearch

Branch: `exp/autoresearch-recovery-v0`  
Spec: `autoresearch-v0.md`

Prerequisites: stable recovery objective, scenario split, Tool Bridge optimizer path, Experiment Ledger, and hidden evaluation.

Deliver:

- frozen ResearchSpec/evaluator;
- bounded mutable surface;
- baseline/best-candidate state;
- Agent hypothesis/change loop;
- deterministic trial scoring;
- append-only accept/reject/neutral ledger;
- plateau/budget stop rules;
- hidden-eval final check;
- optional deterministic numeric optimizer bridge.

Exit: one campaign improves or fails to improve a declared recovery objective transparently, with all negative/failed trials preserved and hidden-eval generalization reported.

## Phase 10 — Knowledge augmentation / rule promotion research

Connect `manufacturing-kg-agent` only after no-KG baselines.

Study:

- retrieved evidence contribution;
- K3 candidate extraction quality;
- K3 -> K2 validation campaigns;
- rule conflicts/provenance;
- impact on hypothesis/tool/experiment selection.

## Phase 11 — Benchmark freeze / expansion

Freeze representative versioned packs across:

- healthy/negative cases;
- RCA difficulty tiers;
- orchestration conditions;
- HAZOP supported/unsupported cases;
- recovery;
- AutoResearch hidden evaluation;
- optional knowledge augmentation.

Publish machine-readable run manifests/report schemas so future models/runtime versions can be compared without changing the benchmark.

## Not on the critical path

- P&ID OCR/model generation;
- 3D visualization;
- plant-wide formal HAZOP automation;
- learned cross-run Agent memory;
- unrestricted recursive swarms;
- production deployment control authority.
