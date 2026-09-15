# AGENTS.md

Rules for coding agents working on `tep-agent-lab`.

## Product boundary

This repository owns TEP-specific agent tools, policies, experiments, and evaluation. It does not own TEP physics or generic agent-runtime internals.

## Canonical specs

Read the owning spec before implementation:

- `docs/specs/tool-surface-v0.md`
- `docs/specs/rca-v0.md`
- `docs/specs/hazop-v0.md`
- `docs/specs/recovery-v0.md`
- `docs/specs/evaluation-v0.md`
- `docs/open-questions.md`
- `docs/decisions/ADR-001-simulate-before-reference-mutation.md`

## Dependency rules

- pin/import `tep-sim`; do not copy its physics, variable registry, snapshot semantics, or capability truth;
- pin/import `industrial-agent-runtime`; do not fork its executor/subagent mechanics into local variants unless the experiment explicitly studies a runtime variant;
- optional knowledge services stay behind read-only evidence adapters;
- evaluator-only ground truth never becomes a registered agent tool.

## Hard experimental rules

1. Preserve hidden truth in blind experiments.
2. Record environment/runtime/lab revision, model config, fixture version, seed, tool/subagent policy, budgets, and run ID.
3. Large telemetry/rollouts use artifact refs and compact summaries; do not dump full traces into model context.
4. Counterfactual experiments use isolated forks; diagnosis does not mutate the reference branch.
5. Recovery defaults to simulate-before-reference-mutation.
6. Reference mutation requires generic runtime gates + lab policy + `tep-sim` capability/control-mode validation + optional approval if configured.
7. Unsupported physics are reported as unsupported, never hallucinated as simulator evidence.
8. HAZOP findings distinguish simulated evidence from engineering inference.
9. Model/tool/subagent/simulation/retry budgets are deterministic and enforced outside prompts.
10. Evaluate baselines/ablations before claiming agent or subagent benefit.
11. Evaluation/scoring code does not trust agent self-reported correctness/confidence.
12. Failed runs remain visible in reports/datasets.

## v0 experiment order

```text
Tool Surface
 -> RCA single-agent baseline
 -> + topology
 -> + counterfactual simulation
 -> bounded subagent ablation
 -> HAZOP
 -> Recovery
 -> optional KG evidence
```

Do not enable dynamic subagents in the first RCA baseline; their value must be measured on the same cases.

## Dynamic subagents

Inherit runtime v0 defaults unless an experiment explicitly overrides them:

- depth 1;
- at most 3 children per parent;
- child reference-world mutation disabled;
- children receive scoped context/tool subsets;
- parent receives structured `EvidenceBundle`, not complete child transcript.

## HAZOP boundary

Simulation-backed HAZOP is research/decision support, not a claim of completing formal plant HAZOP review. A structured finding must preserve scenario support status and evidence provenance.

## Reporting

Every benchmark report should include task quality, behavior/resource metrics, simulation use, gate denials/policy violations, safety/environment outcomes where relevant, and deterministic baseline comparison.

Keep this file concise. Detailed workflow semantics belong in `docs/specs`; unresolved research choices belong in `docs/open-questions.md`.
