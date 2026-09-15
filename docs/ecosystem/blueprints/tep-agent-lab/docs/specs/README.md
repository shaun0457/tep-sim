# TEP Agent Lab Specifications

These proposal specs define TEP-specific investigation, tooling, records, benchmark design, and later research workflows on top of `tep-sim` and `industrial-agent-runtime`.

## First-RCA contracts

- [`investigation-state-v0.md`](investigation-state-v0.md) — RcaState implementation of generic TaskStateStore, Observation/Evidence separation, ContextProjection, stopping.
- [`hypothesis-experiment-v0.md`](hypothesis-experiment-v0.md) — Hypothesis, typed Prediction, evidence links, ExperimentProposal/RunSpec/Result/Interpretation, dedup identity.
- [`tool-surface-v0.md`](tool-surface-v0.md) — blind Agent-visible TEP tools, SIMULATE/MUTATE boundary, consumer request/result validation.
- [`tool-bridge-v0.md`](tool-bridge-v0.md) — allowlisted scientific-library adapters with runtime gating and nested resource accounting.
- [`engineering-records-v0.md`](engineering-records-v0.md) — InvestigationReport, DecisionRecord, ExperimentRecord archive contracts.
- [`rca-v0.md`](rca-v0.md) — structured CausalClaim, evidence-backed blind RCA, mandatory strong C0 baseline.
- [`benchmark-design-v0.md`](benchmark-design-v0.md) — scenario-family identifiability, C0-relative difficulty, leakage/memorization controls.
- [`evaluation-v0.md`](evaluation-v0.md) — sole canonical capability/orchestration matrices and outcome/process/resource/safety metrics.

## Rule / policy metadata

- [`knowledge-rule-registry-v0.md`](knowledge-rule-registry-v0.md) — canonical `origin × validation × authority` Rule model. K0–K4 is shorthand only; full promotion workflow is later research.

## Later task-family proposals

- [`hazop-v0.md`](hazop-v0.md) — simulation-backed HAZOP direction.
- [`recovery-v0.md`](recovery-v0.md) — counterfactual recovery-planning direction.
- [`autoresearch-v0.md`](autoresearch-v0.md) — later frozen-evaluator autonomous engineering research loop.

Later specs do not authorize implementing those task families before the RCA substrate/evaluation is stable.

The lab owns domain state/projection/policy/tool adapters/scoring. It does not reimplement TEP physics or generic runtime contracts.
