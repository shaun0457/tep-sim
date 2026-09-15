# Open Questions — `tep-agent-lab`

Only unresolved empirical/later-phase choices belong here. Current v0 contracts use RcaState, Observation/Evidence separation, `origin × validation × authority`, typed Prediction/Experiment, minimal Tool Bridge, strong C0 baseline, and archival Engineering Records.

## OQ-1 — First RCA scenario set

Use reactor/cooling-water-related family first, but exact candidate causes, magnitudes, timings, seeds, nuisance/operating variants are selected after `benchmark-design-v0.md` identifiability + C0 pilot.

Need at least:

- healthy/no-abnormal case;
- multiple plausible alternatives;
- one non-local/nontrivial case before MEDIUM/HARD claims.

## OQ-2 — Incident trigger source

First benchmark default: fixture-provided investigation start point + compact abnormal-signal summary so detector quality does not confound investigation quality.

Later compare deterministic detector-triggered starts.

## OQ-3 — WorkBatch value / richer Dynamic DAG

v0 WorkBatch supports `TOOL | SUBTASK` + `depends_on` only.

Open research:

- when does dependency-aware TOOL batching improve O3 Hybrid?
- when do bounded subtasks improve O4?
- is a richer mutable DAG with cancellation/replanning ever measurably better?

Do not implement full DAG semantics before evidence/specification.

## OQ-4 — Subagent trigger/default limits

Default proposal: Main Agent chooses delegation within runtime depth=1/cumulative max=3.

Measure:

- incremental diagnosis/experiment quality;
- context reduction;
- token/tool/simulation overhead;
- duplicate work;
- cases where parent-only path suffices.

## OQ-5 — Formal semantic stopping

v0 = Agent finish proposal + deterministic structural readiness checks.

Open research:

- probability/belief semantics;
- hypothesis update rule;
- information-value estimator;
- marginal-value stop threshold.

Do not hard-code formal information-gain stopping until those definitions exist.

## OQ-6 — Rule validation / knowledge promotion

Canonical Rule schema is fixed as origin/validation/authority, but full promotion workflow is deferred.

When studied, freeze:

- deterministic scenario-family sampling;
- operating/held-out envelope;
- seed diversity;
- effect/tolerance policy;
- contradictory evidence handling;
- authority mapping policy.

The proposing Agent must not choose only favorable validation trials or self-promote authority.

## OQ-7 — Initial Tool Bridge dependencies

First RCA recommendation:

1. response-feature/trajectory comparison;
2. SciPy-style lag/cross-correlation;
3. optional upstream TEP detector baseline.

Open later dependencies:

- PCA/PLS;
- graph utility package if needed beyond local traversal;
- SALib;
- Optuna/search backend;
- statsmodels/Granger;
- remote/MCP provider.

Add only from a concrete research contract, license/version review, and reproducibility need.

## OQ-8 — Simulation experiment granularity

Default: semantic scenario/deviation contracts where deterministic mappings exist, with bounded low-level controls only through typed tools.

Pilot RCA will show whether semantic compilation is too restrictive.

## OQ-9 — Recovery authority

First recovery study ranks forked strategies only.

Open later:

- first benchmark enabling reference MUTATE;
- exact policy limits/action schema;
- whether research UI/SME authority escalation is useful.

Any enabled MUTATE is expected-state-revision bound.

## OQ-10 — AutoProcessResearch first campaign

Candidate direction: robust reactor cooling/recovery strategy after recovery scoring exists.

Need to freeze:

- mutable strategy representation;
- primary objective/weights;
- hard constraints;
- RESEARCH/HIDDEN_EVAL split;
- optimizer/trial budget;
- plateau/minimum-improvement policy.

AutoResearch remains separate task-family evaluation.

## OQ-11 — HAZOP scope

Preserve node/parameter/guide-word/deviation/cause/consequence/safeguard semantics while labeling results simulation-backed research support, not formal plant HAZOP completion.

Open: how much worksheet/report structure adds research value.

## OQ-12 — External knowledge timing

Add `manufacturing-kg-agent` only after no-KG baseline.

Open:

- which task benefits;
- retrieval/evidence scoring;
- literature candidate validation;
- interaction with hidden benchmark data.

## OQ-13 — Cross-incident Engineering Record retrieval

v0 writes records but does not retrieve them into future context.

Later study may compare:

```text
no history
raw trace retrieval
structured Engineering Record retrieval
approved rule/runbook retrieval
```

Need strict partition/leakage controls.

## OQ-14 — Model/provider study design

Architecture is provider-independent.

Open: whether model comparison becomes a primary experimental axis or only robustness validation after tool/orchestration design stabilizes.

## OQ-15 — Visualization

2D topology + telemetry + experiment/work/branch timeline is sufficient initially.

3D remains deferred until a spatial-reasoning question exists.
