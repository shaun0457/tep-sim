# AGENTS.md

Rules for coding agents working on `tep-agent-lab`.

## Product boundary

This repository owns TEP-specific Agent tools, domain state/projection, lab policy, experiments, Engineering Records, and evaluation. It does not own TEP physics or generic runtime internals.

## Canonical specs

Before implementation, read the relevant owning spec:

- `docs/specs/investigation-state-v0.md`
- `docs/specs/knowledge-rule-registry-v0.md`
- `docs/specs/hypothesis-experiment-v0.md`
- `docs/specs/tool-surface-v0.md`
- `docs/specs/tool-bridge-v0.md`
- `docs/specs/engineering-records-v0.md`
- `docs/specs/benchmark-design-v0.md`
- `docs/specs/evaluation-v0.md`
- `docs/specs/rca-v0.md`
- `docs/specs/hazop-v0.md`
- `docs/specs/recovery-v0.md`
- `docs/specs/autoresearch-v0.md`
- `docs/open-questions.md`
- `docs/decisions/ADR-001-simulate-before-reference-mutation.md`

`evaluation-v0.md` is the sole canonical capability/orchestration comparison matrix.

## Dependency rules

- pin/import `tep-sim`; do not copy its physics, variable registry, snapshot semantics, or capability truth;
- pin/import `industrial-agent-runtime`; do not fork its ToolSpec/gates/TaskStateStore/WorkBatch/subtask semantics locally;
- lab implements `TaskStateStore` for RcaState but runtime never imports RcaState;
- optional knowledge services remain behind typed read-only evidence adapters until an explicit later capability study;
- evaluator-only truth/candidate sets never become registered Agent tools.

## Hard rules

1. Preserve hidden truth/candidate-answer isolation in blind experiments.
2. `ObservationRecord != Evidence`: tool/simulator output becomes evidence only via explicit evidence link to a hypothesis/claim.
3. Exact model-visible ContextProjection is persisted for every model turn.
4. Blind RCA does not expose canonical node-to-IDV answer bindings or full candidate list by default.
5. Counterfactual experiments use isolated branches; SIMULATE never mutates reference state.
6. MUTATE is a separate high-authority path and is disabled in blind RCA/AutoResearch by default.
7. Compound Tool Bridge operations that run simulator trials are SIMULATE and must reserve/report nested rollout/horizon/trial budget.
8. Tool Bridge is not an authorization layer; all calls pass runtime gates + lab `validate_request`.
9. Domain Rule metadata is `origin × validation × authority`; K0–K4 is shorthand only.
10. LLM/paper/simulation evidence cannot self-promote execution authority.
11. Typed Prediction/ExperimentResult data is preferred over free-text judging for experiment discrimination.
12. Required first RCA baseline C0 is strong deterministic enumerate/simulate/match, not a strawman.
13. Tool exposure stays fixed across orchestration ablations unless exposure itself is the independent variable.
14. Subagents appear on the orchestration axis, not the capability axis.
15. Failed/negative runs/experiments remain in the append-only run history.
16. Engineering Records are archival in v0 and are not automatically retrieved into later benchmark context.
17. Unsupported physics are reported as unsupported, never fabricated as simulator evidence.
18. No arbitrary Agent Python/shell/import as the normal analysis path.

## v0 implementation/research order

```text
RcaState / run-log / ContextProjection
 -> Rule/policy metadata
 -> Hypothesis + Prediction + Experiment
 -> blind TEP Tool Surface
 -> minimal Tool Bridge
 -> benchmark identifiability + C0
 -> RCA capability ladder
 -> orchestration O0-O5
 -> later HAZOP / Recovery
 -> later AutoProcessResearch
 -> optional knowledge/memory studies
```

Do not implement HAZOP/Recovery/AutoResearch infrastructure just because their proposal specs exist; first RCA contracts/tracing/evaluation must stabilize.

## Subagents

Inherit runtime policy:

- depth 1 default;
- cumulative max 3 children per task default;
- child MUTATE disabled;
- child cannot create nested SUBTASK at depth limit;
- child receives scoped ContextProjection/tools;
- parent receives `SubtaskResult`, not complete child transcript.

The parent/lab decides which child observation refs become EvidenceLinks.

## Tool Bridge v0 scope

Initial bridge implementation should remain small:

- response features / trajectory comparison;
- cross-correlation / lag;
- optional upstream TEP detector baseline if benchmark requires it.

SALib/Optuna/PCA/PLS/Granger/MCP are later, concrete-need additions.

## Benchmark/reporting

Every first-family report should include:

- C0 performance/cost;
- task quality;
- evidence/Prediction validity;
- observation/query waste;
- model/tool/rollout/subtask resources;
- gate/authority violations;
- benchmark/tool/scorer versions;
- final InvestigationReport ref.

Keep this file concise. Detailed workflow semantics belong in `docs/specs`; unresolved empirical questions belong in `docs/open-questions.md`.
