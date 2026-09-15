# Decision Register

This register summarizes current program decisions. Detailed rationale belongs in ADRs/specs; this file answers "what is currently assumed?"

| ID | Decision | Status | Revisit trigger |
|---|---|---|---|
| D-001 | Use three core repos: `tep-sim`, `industrial-agent-runtime`, `tep-agent-lab`. | accepted | Two repos become inseparable in practice or a fourth stable responsibility gains multiple consumers. |
| D-002 | `tep-sim` is agent-agnostic and owns environment truth only. | accepted | Breaking this requires explicit architecture change. |
| D-003 | Use machine-readable DEXPI/process semantics for TEP; do not build P&ID OCR/model generation now. | accepted | Agent research is stable and a separately funded P&ID project is started. |
| D-004 | No 3D/Omniverse/Blender milestone for v0; use topology + telemetry first. | accepted | A concrete spatial-reasoning research question requires it. |
| D-005 | v0 product role is **Autonomous Industrial Process Investigator**; long-term direction may expand toward Autonomous Process Engineer. | accepted | Investigation tasks fail to represent the target use cases or recovery/control becomes the primary research goal. |
| D-006 | One Main Agent by default; subagents are ephemeral bounded tasks, not permanent organizational roles. | accepted | Ablations show another organization materially improves results. |
| D-007 | Use **Hybrid orchestration**: goal-driven Main Agent + deterministic Coordinator/Executor/Verifier; local ReAct for simple work; bounded Dynamic DAG for complex work. Public contracts remain framework-neutral. | accepted | Benchmark results show a simpler/fixed architecture dominates without losing target capability. |
| D-008 | Coordinator/Executor/Verifier are deterministic runtime components by default, not additional permanent LLM agents. | accepted | A specific semantic-verification task demonstrates measurable benefit from an optional critic subtask. |
| D-009 | LangGraph may implement the TEP/lab macro workflow and checkpointing through an adapter, but LangGraph-native types do not define public runtime contracts. | accepted direction | Another framework/runtime becomes clearly preferable or adapter overhead is unjustified. |
| D-010 | v0 subagent defaults: depth 1, max 3 children, child no reference mutation. | proposal | Subagent experiments quantify need for different limits. |
| D-011 | Deterministic gates separate model reasoning from execution authority. Generic gates handle schema/allowlist/budget/side-effect class; TEP domain safety stays downstream. | accepted | Exact layers may evolve; authority separation is invariant. |
| D-012 | Counterfactual simulation is a first-class agent tool; recovery defaults to simulate-before-reference-mutation. | accepted direction | Simulation cost/latency invalidates the policy for a target task. |
| D-013 | Hidden scenario ground truth is evaluator-only in blind diagnosis. | accepted | Only explicit non-blind study condition. |
| D-014 | First research benchmark targets reactor/cooling-water scenarios; exact disturbance/timing/magnitude are fixture decisions based on identifiability. | accepted direction | Pilot trajectories show poor diagnosability/coverage. |
| D-015 | Build single-agent/counterfactual baselines before measuring Dynamic DAG/subagent value. | accepted | None; required for attribution. |
| D-016 | No persistent cross-run learned agent memory in v0. | proposal | Repeated-task studies show measurable need beyond evidence/run artifacts. |
| D-017 | `manufacturing-kg-agent` is optional evidence augmentation, added after no-KG baselines. | accepted | Knowledge becomes necessary for a target task. |
| D-018 | P&ID-to-simulator (`pid2sim`) is parked research, not a current repo/milestone. | accepted | Explicit future project restart. |
| D-019 | Use an **Information Plane** (not a new repo) for ProcessGraph, registries, evidence refs, Experiment Ledger, artifacts, and Investigation State. Conversation transcripts are not canonical state. | accepted | Multiple independent domains justify extracting a shared information service. |
| D-020 | Domain knowledge uses K0–K4 levels: simulator truth, formal invariants, validated relationships, literature heuristics, and agent hypotheses. LLM/paper extraction cannot directly create hard gates. | accepted | A better provenance/knowledge-control model is demonstrated. |
| D-021 | Hypotheses and experiments are first-class typed objects; deterministic experiment results are separated from model interpretation. | accepted | None expected; schemas may evolve. |
| D-022 | Reuse mature scientific/open-source functionality through an allowlisted **Tool Bridge** rather than arbitrary agent Python/shell execution or local reimplementation. | accepted | A dependency is less reliable than a small local implementation or cannot satisfy provenance/security requirements. |
| D-023 | Numeric parameter search should normally use deterministic optimizers/search tools; the Agent chooses mechanism, variables, bounds, objectives, and interprets results. | accepted | A research task explicitly studies LLM numeric search behavior. |
| D-024 | Add `AutoProcessResearch` as a separate lab mode with frozen evaluator, bounded mutable surface, fixed experiment budgets, append-only ledger, and keep/reject/neutral decisions. | accepted direction | Initial campaigns show insufficient research value or excessive benchmark gaming. |
| D-025 | Evaluation uses two orthogonal ablation axes: **capability ablation** and **orchestration architecture ablation**, plus scientific-behavior metrics such as experiment information value/redundancy. | accepted | Metrics prove unreliable and require revision. |

## Canonical supporting documents

Program-level:

- `program-charter.md`
- `information-plane.md`
- `documentation-standard.md`
- `development-workflow.md`
- `implementation-plan.md`

Runtime/lab contracts:

- `blueprints/industrial-agent-runtime/docs/specs/hybrid-orchestration-v0.md`
- `blueprints/industrial-agent-runtime/docs/specs/deterministic-gates-v0.md`
- `blueprints/tep-agent-lab/docs/specs/investigation-state-v0.md`
- `blueprints/tep-agent-lab/docs/specs/knowledge-rule-registry-v0.md`
- `blueprints/tep-agent-lab/docs/specs/hypothesis-experiment-v0.md`
- `blueprints/tep-agent-lab/docs/specs/tool-bridge-v0.md`
- `blueprints/tep-agent-lab/docs/specs/autoresearch-v0.md`
- per-repo architecture/spec/open-question/ADR documents.

## Rule

A proposed decision may be used to build a minimal experiment, but results should validate or revise it. An accepted decision must not change only inside code or chat; update this register plus the relevant ADR/spec.
