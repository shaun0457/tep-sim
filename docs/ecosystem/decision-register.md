# Decision Register

This register summarizes current program decisions. Detailed rationale belongs in ADRs/specs; this file answers "what is currently assumed?"

| ID | Decision | Status | Revisit trigger |
|---|---|---|---|
| D-001 | Use three core repos: `tep-sim`, `industrial-agent-runtime`, `tep-agent-lab`. | accepted | Two repos become inseparable in practice or a fourth stable responsibility gains multiple consumers. |
| D-002 | `tep-sim` is agent-agnostic and owns environment truth only. | accepted | None expected; breaking this would require explicit architecture change. |
| D-003 | Use machine-readable DEXPI/process semantics for TEP; do not build P&ID OCR/model generation now. | accepted | Agent research is stable and a separate product/research goal explicitly funds P&ID automation. |
| D-004 | No 3D/Omniverse/Blender milestone for v0; use topology + telemetry first. | accepted | A research question requires spatial reasoning or 3D materially improves evaluation. |
| D-005 | One main agent by default; subagents are ephemeral bounded tasks, not permanent roles. | accepted direction / v0 policy proposed | Ablations show another organization materially improves results. |
| D-006 | v0 subagent defaults: depth 1, max 3 children, child no reference mutation. | proposal | RCA/subagent experiments quantify need for different limits. |
| D-007 | Generic runtime starts with explicit Python executor, not mandatory LangGraph. | proposal (ADR in runtime blueprint) | Durable resume/human interrupt/persistent graph becomes a concrete requirement. |
| D-008 | Deterministic gates separate model reasoning from execution authority. | accepted | None expected; exact gate layers may evolve. |
| D-009 | Generic runtime gates handle schema/allowlist/budget/side-effect class; TEP domain safety/policy stays downstream. | proposal | Integration proves boundary is impractical or duplicated. |
| D-010 | Counterfactual simulation is a first-class agent tool; recovery defaults to simulate-before-reference-mutation. | proposal (ADR in lab blueprint) | Measured simulation cost/time makes policy unsuitable for a target task. |
| D-011 | Hidden scenario ground truth is evaluator-only in blind diagnosis. | accepted | Only explicit non-blind study condition. |
| D-012 | First research benchmark targets reactor/cooling-water scenario family, but exact disturbance/timing/magnitude are fixture decisions. | accepted direction | Pilot trajectories show poor diagnosability or insufficient variation. |
| D-013 | Build single-agent/counterfactual baselines before enabling subagent ablation. | accepted | None; needed for attribution. |
| D-014 | No persistent cross-run agent memory in v0. | proposal | Repeated-task studies demonstrate measurable need beyond evidence services/run artifacts. |
| D-015 | `manufacturing-kg-agent` is optional evidence augmentation, added after no-KG baselines. | accepted | Knowledge becomes required to make target task meaningful. |
| D-016 | P&ID-to-simulator (`pid2sim`) is parked research, not a current repo/milestone. | accepted | Explicit future project restart. |

## Canonical supporting documents

- `program-charter.md`
- `documentation-standard.md`
- `development-workflow.md`
- `implementation-plan.md`
- `../architecture.md`
- per-repo `docs/specs/`, `docs/open-questions.md`, and `docs/decisions/`

## Rule

A proposed decision may be used to build a minimal experiment, but results should be used to validate or revise it. An accepted decision should not be changed only inside code or chat; update this register plus the relevant ADR/spec.
