# Decision Register

This register summarizes current program decisions. Detailed rationale belongs in ADRs/specs; this file answers "what is currently assumed?"

| ID | Decision | Status | Revisit trigger |
|---|---|---|---|
| D-001 | Use three core repos: `tep-sim`, `industrial-agent-runtime`, `tep-agent-lab`. | accepted | Two repos become inseparable in practice or a fourth stable responsibility gains multiple consumers. |
| D-002 | `tep-sim` is agent-agnostic and owns environment truth only. | accepted | Breaking this requires explicit architecture change. |
| D-003 | Use machine-readable DEXPI/process semantics for TEP; do not build P&ID OCR/model generation now. | accepted | Agent research is stable and a separately funded P&ID project is started. |
| D-004 | No 3D/Omniverse/Blender milestone for v0; use topology + telemetry first. | accepted | A concrete spatial-reasoning research question requires it. |
| D-005 | v0 product/research role is **Autonomous Industrial Process Investigator**; long-term direction may expand toward Autonomous Process Engineer. | accepted | Investigation tasks fail to represent target use cases or recovery/control becomes the primary research goal. |
| D-006 | One Main Agent by default; subagents are ephemeral bounded tasks, not permanent organizational roles. | accepted scope decision | An explicit ablation later justifies another organization. |
| D-007 | Use a **Hybrid contract**: goal-driven Main Agent + deterministic runtime authority shell. The architecture contract is accepted as the v0 implementation shape; whether it outperforms simpler orchestration is an empirical question. | accepted | Orchestration ablations show simpler architecture should replace it. |
| D-008 | Coordinator/gates/Executor/post-execution Verifier are deterministic runtime components by default, not permanent LLM agents. | accepted | A bounded semantic critic demonstrates value as an optional subtask. |
| D-009 | v0 does not require a full Dynamic DAG engine. Complex work uses dependency-aware `WorkBatch` (`TOOL`/`SUBTASK` + `depends_on`). Rich Dynamic DAG replanning/cancellation is deferred research. | accepted | O4/O5 evidence demonstrates richer graph semantics are necessary/useful. |
| D-010 | LangGraph is not a v0 core dependency or scheduled critical-path deliverable. Public contracts stay framework-neutral/serializable. | accepted | Concrete checkpoint/resume/interrupt requirements justify an adapter. |
| D-011 | v0 subagent defaults: depth 1, cumulative max 3 per task, child reference mutation disabled. | proposal | Subagent experiments quantify better limits. |
| D-012 | Deterministic pre-execution gates separate model reasoning from execution authority. Post-execution result verification is a separate stage. | accepted | Exact hook signatures may evolve; authority separation is invariant. |
| D-013 | Counterfactual simulation is a first-class investigation capability; SIMULATE never mutates reference state. Recovery reference mutation is a distinct MUTATE path. | accepted | None for class separation; recovery policy may evolve. |
| D-014 | Hidden scenario ground truth/candidate answer sets are evaluator-only in blind diagnosis. | accepted | Only explicit non-blind study condition. |
| D-015 | First research benchmark starts with reactor/cooling-water-related scenarios; exact causes/timing/magnitude/difficulty are fixture decisions based on identifiability and strong deterministic C0 performance. | accepted direction | Pilot data shows poor coverage/diagnosability. |
| D-016 | Build strong deterministic/single-Agent baselines before claiming value from WorkBatch/subagents. | accepted | None; required for attribution. |
| D-017 | No persistent cross-run learned Agent memory/retrieval in v0 benchmark. Engineering records are archival first. | proposal | A separate memory study explicitly enables retrieval. |
| D-018 | `manufacturing-kg-agent` is optional evidence augmentation after clean no-KG baselines. | accepted | Knowledge becomes necessary for a target task. |
| D-019 | P&ID-to-simulator (`pid2sim`) is parked research, not a current repo/milestone. | accepted | Explicit future project restart. |
| D-020 | Use an **Information Plane** as a logical contract/ownership boundary, not a fourth repo or five mandatory storage services. v0 may use one append-only run log + artifacts + typed views. | accepted | Multiple independent domains/scale justify extracting shared persistence services. |
| D-021 | Generic `InformationRef`, `ContextProjection`, `TaskStateStore`, budgets/tool contracts belong to `industrial-agent-runtime`; domain state/projection semantics belong to consuming lab. | accepted | A second domain proves a different generic boundary is needed. |
| D-022 | Observation and Evidence are distinct: tool/simulator output creates immutable observation/result records; an explicit evidence link relates observations to claims/hypotheses. | accepted | None expected; exact schemas may evolve. |
| D-023 | Domain Rules use independent `origin × validation × authority` metadata. K0–K4 is documentation shorthand only. Agent/paper/simulation evidence cannot self-promote authority. | accepted | A better evidence/authority model is demonstrated. |
| D-024 | Hypotheses, Predictions, experiments, deterministic results, and model interpretations are first-class distinct objects. | accepted | None expected; feature vocabulary may evolve. |
| D-025 | Reuse mature scientific/open-source functionality through allowlisted **Tool Bridge adapters** outside generic runtime. Runtime owns ToolSpec/gates/budget/execution authority. | accepted | A bridged dependency is less reliable than a small local implementation. |
| D-026 | Compound tools that internally run simulation are `SIMULATE` and must declare/reserve nested rollout/horizon/trial budgets. | accepted | None expected; resource dimensions may evolve. |
| D-027 | Numeric parameter search normally uses deterministic/seeded search/optimizer tools; the Agent chooses mechanism, variables, bounds/objectives, and interprets results. | accepted | A study explicitly investigates LLM numeric search. |
| D-028 | `AutoProcessResearch` remains a separate later lab task/mode with frozen evaluator, bounded mutable surface, explicit budgets, append-only experiment history, and hidden evaluation. It is not an orchestration-ablation row. | accepted direction | Initial campaigns show poor research value or benchmark gaming. |
| D-029 | `evaluation-v0.md` is the sole canonical comparison matrix. Capability and orchestration axes are separated; tool exposure is held fixed across orchestration comparisons unless exposure itself is studied. | accepted | Metrics/study design prove unreliable. |
| D-030 | Every first RCA benchmark version includes a strong deterministic C0 enumerate/simulate/match baseline. A case C0 solves cheaply/reliably cannot be used to claim Agent necessity. | accepted | A different deterministic baseline is demonstrably stronger/more appropriate. |
| D-031 | v0 writes structured `InvestigationReport`, `DecisionRecord`, and `ExperimentRecord`. Lesson Learned/Runbook/manual promotion is deferred and does not happen automatically. | accepted | Cross-incident organizational-memory study begins. |

## Canonical supporting documents

Program-level:

- `program-charter.md`
- `information-plane.md`
- `design-review-adjudication.md`
- `documentation-standard.md`
- `development-workflow.md`
- `implementation-plan.md`

Runtime:

- `blueprints/industrial-agent-runtime/docs/specs/runtime-v0.md`
- `blueprints/industrial-agent-runtime/docs/specs/hybrid-orchestration-v0.md`
- `blueprints/industrial-agent-runtime/docs/specs/deterministic-gates-v0.md`
- `blueprints/industrial-agent-runtime/docs/specs/subagents-v0.md`

Lab:

- `blueprints/tep-agent-lab/docs/specs/investigation-state-v0.md`
- `blueprints/tep-agent-lab/docs/specs/knowledge-rule-registry-v0.md`
- `blueprints/tep-agent-lab/docs/specs/hypothesis-experiment-v0.md`
- `blueprints/tep-agent-lab/docs/specs/tool-surface-v0.md`
- `blueprints/tep-agent-lab/docs/specs/tool-bridge-v0.md`
- `blueprints/tep-agent-lab/docs/specs/engineering-records-v0.md`
- `blueprints/tep-agent-lab/docs/specs/benchmark-design-v0.md`
- `blueprints/tep-agent-lab/docs/specs/evaluation-v0.md`
- task-specific RCA/HAZOP/recovery/AutoResearch specs.

## Status rule

- Architecture/ADR decisions use accepted/proposed/superseded states in their own records.
- Specs use only `proposal | accepted | deprecated` per `documentation-standard.md`.
- An accepted architecture contract is not evidence that the architecture empirically outperforms alternatives.

## Rule

An accepted decision must not change only inside code/chat; update this register plus the owning ADR/spec. Empirical superiority claims require benchmark evidence rather than decision-register status.
