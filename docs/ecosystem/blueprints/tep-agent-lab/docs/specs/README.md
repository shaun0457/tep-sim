# TEP Agent Lab Specifications

These v0 proposal specs define the TEP-specific integration and research workflows built on top of `tep-sim` and `industrial-agent-runtime`.

- [`tool-surface-v0.md`](tool-surface-v0.md) — agent-visible TEP tools and authority classes.
- [`rca-v0.md`](rca-v0.md) — root-cause-analysis experiment contract.
- [`hazop-v0.md`](hazop-v0.md) — simulation-backed HAZOP contract.
- [`recovery-v0.md`](recovery-v0.md) — counterfactual recovery-planning contract.
- [`evaluation-v0.md`](evaluation-v0.md) — benchmark, ground-truth separation, metrics, and ablations.

The lab owns domain-policy adapters and evaluation logic. It does not reimplement TEP physics or generic agent orchestration.
