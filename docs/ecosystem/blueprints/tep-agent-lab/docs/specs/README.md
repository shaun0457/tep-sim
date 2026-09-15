# TEP Agent Lab Specifications

These v0 specs define TEP-specific integration, investigation, research, and evaluation on top of `tep-sim` and `industrial-agent-runtime`.

## State / knowledge / experiment contracts

- [`investigation-state-v0.md`](investigation-state-v0.md) — canonical typed investigation state, revisions, open questions, budgets, and stopping readiness.
- [`knowledge-rule-registry-v0.md`](knowledge-rule-registry-v0.md) — K0–K4 knowledge levels, provenance, enforcement classes, and promotion workflow.
- [`hypothesis-experiment-v0.md`](hypothesis-experiment-v0.md) — first-class hypotheses, evidence links, experiment proposals/run specs/results.

## Tools

- [`tool-surface-v0.md`](tool-surface-v0.md) — agent-visible TEP environment tools and authority classes.
- [`tool-bridge-v0.md`](tool-bridge-v0.md) — allowlisted adapters to mature open-source analysis/optimization/graph tools.

## Research workflows

- [`rca-v0.md`](rca-v0.md) — blind root-cause investigation contract.
- [`hazop-v0.md`](hazop-v0.md) — simulation-backed HAZOP contract.
- [`recovery-v0.md`](recovery-v0.md) — counterfactual recovery-planning contract.
- [`autoresearch-v0.md`](autoresearch-v0.md) — frozen-evaluator autonomous engineering experiment loop.

## Benchmark / evaluation

- [`benchmark-design-v0.md`](benchmark-design-v0.md) — scenario-family design, identifiability pilot, difficulty, partitioning, and leakage controls.
- [`evaluation-v0.md`](evaluation-v0.md) — environment/runtime/task/scientific-behavior metrics plus capability and orchestration ablations.

The lab owns TEP/domain-policy adapters and evaluation logic. It does not reimplement TEP physics or generic runtime mechanics.
