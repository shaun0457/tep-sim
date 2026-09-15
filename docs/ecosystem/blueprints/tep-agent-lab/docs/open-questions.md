# Open Questions — `tep-agent-lab`

Only unresolved empirical/benchmark choices remain here. Hybrid orchestration, Information Plane, K0–K4 knowledge levels, Tool Bridge, first-class Hypothesis/Experiment objects, and AutoProcessResearch are accepted directions with v0 specs.

## OQ-1 — First RCA scenario set

Use reactor/cooling-water family first, but exact candidate causes, IDVs, magnitudes, timings, seeds, and operating variants must be selected after the identifiability pilot in `benchmark-design-v0.md`.

Avoid both trivial one-signal cases and practically indistinguishable cases unless intentionally labeled as difficulty/uncertainty tests.

## OQ-2 — Incident trigger source

First benchmark default: fixture-provided investigation start point plus compact abnormal-signal evidence, so detector quality does not confound investigation quality.

Later compare with deterministic detector-triggered starts.

## OQ-3 — Dynamic DAG policy defaults

Hybrid/Dynamic DAG direction is accepted, but lab defaults for when complexity justifies a DAG remain empirical.

Questions:

- should the Main Agent explicitly classify simple/complex work or simply propose a plan when useful?
- what node/parallel/revision budgets minimize overhead?
- when does direct ReAct outperform plan construction?

Answer through orchestration ablation, not hard-coded intuition.

## OQ-4 — Subagent trigger policy

Default: Main Agent chooses when to delegate within deterministic limits.

Compare with:

- no subagents;
- fixed parallel hypothesis workers;
- dynamic delegation.

Evaluate incremental quality versus context/token/tool cost.

## OQ-5 — Semantic stop thresholds

The state/verifier support semantic stopping, but mode-specific thresholds remain open.

Examples:

- minimum evidence support;
- hypothesis-rank margin;
- unresolved critical-question count;
- marginal experiment value threshold;
- plateau criteria.

These should be frozen per benchmark version.

## OQ-6 — Rule promotion thresholds

K0–K4 architecture is fixed, but K3 -> K2 validation criteria are relationship-specific.

Need pilot policies for:

- number/diversity of scenarios;
- operating-envelope coverage;
- seed variation;
- tolerance/effect consistency;
- contradictory evidence handling;
- when K2 remains advisory versus warrants stronger reviewed enforcement.

## OQ-7 — Initial Tool Bridge dependency set

Candidate set is documented, but actual v0 dependencies should stay minimal.

Choose based on first benchmark needs, maintenance/license review, reproducibility, and whether upstream TEP already supplies equivalent functionality.

Likely order:

1. upstream TEP detector/analysis capabilities;
2. SciPy signal/lag features;
3. graph utilities;
4. selected PCA/PLS baseline tools;
5. sensitivity/optimization tools when AutoResearch begins.

## OQ-8 — Simulation experiment granularity

Default: prefer semantic scenario/deviation contracts when deterministic mappings exist; allow bounded low-level XMV/IDV experiment controls through explicit typed tools.

Pilot experience will determine how often semantic compilation is too restrictive for useful research.

## OQ-9 — Recovery authority

First recovery benchmark ranks forked strategies. Reference mutation remains disabled until gates/verification are proven.

Open: which benchmark version first enables one real reference-branch action and whether human approval is required in research mode.

## OQ-10 — AutoProcessResearch first campaign

Default candidate: robust reactor cooling-water recovery strategy.

Still to freeze after recovery benchmark exists:

- exact mutable surface;
- primary scalar objective/weights;
- hard safety constraints;
- research versus hidden-eval scenario split;
- optimizer method/trial budget;
- plateau/minimum-improvement thresholds.

## OQ-11 — HAZOP scope

Default: preserve node/parameter/guide-word/deviation/cause/consequence/safeguard semantics while clearly labeling results as simulation-backed research support, not formal HAZOP completion.

Open: how much worksheet/report structure is useful versus overhead for the agent-research question.

## OQ-12 — External knowledge timing

Add `manufacturing-kg-agent` only after clean no-KG baselines.

Open: which task family benefits enough to justify retrieval and how K3 extracted rules/evidence are scored.

## OQ-13 — Model/provider study design

Architecture remains provider-independent. First real model should be frozen per benchmark run.

Open: whether model comparison is a primary study axis or only robustness validation after orchestration/tool architecture stabilizes.

## OQ-14 — Cross-incident learned memory

No learned cross-run memory initially. Revisit only after Information Plane/Rule Registry/Experiment Ledger baselines show a remaining repeated-task gap.

## OQ-15 — Visualization

2D topology + telemetry + investigation/DAG/branch timeline is sufficient for v0.

Only add 3D if a concrete spatial-reasoning question appears.
