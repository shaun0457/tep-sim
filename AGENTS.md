# AGENTS.md

Repository-wide instructions for coding agents.

## Product intent

`tep-sim` is an **agent-agnostic Tennessee Eastman Process sandbox**.

This repository models the environment. It does not implement an LLM agent runtime or TEP-specific agent workflow.

## Hard boundaries

1. **Do not add LLM or agent-framework dependencies here.** No LangGraph, provider SDK, prompt framework, agent memory, or subagent orchestration belongs in this repo.
2. **Do not implement RCA/HAZOP/recovery reasoning here.** The environment exposes data and deterministic experiment primitives only.
3. **Do not implement P&ID OCR, generic P&ID-to-simulation generation, or 3D reconstruction here.** Those are outside the active program scope.
4. **Preserve deterministic reproducibility.** Runs must be attributable to seed, simulator version, config, intervention schedule, and run/branch identity.
5. **Use typed environment APIs.** Callers request observations, snapshots, forks, interventions, rollouts, topology, or evaluations through explicit contracts rather than mutating internals.
6. **Fail explicitly for unsupported physics.** Never invent a substitute behavior for an unsupported scenario.
7. **Keep runtime metadata canonical.** XMEAS/XMV/IDV identity comes from vendored runtime metadata/registry, not duplicated prose or prompts.
8. **Keep DEXPI/process semantics deterministic.** Structured process data may be normalized/bound by code; no LLM is needed inside the environment to infer runtime bindings.
9. **Make side effects auditable.** Record reset, intervention, fork, rollout, termination, and safety events/provenance.
10. **Prefer small stable public interfaces.** Upstream internals may change; consumers depend on `tep-sim` contracts.

## Canonical specs

Before implementing a feature, read its owning spec:

- `docs/specs/environment-api-v0.md`
- `docs/specs/snapshot-fork-replay-v0.md`
- `docs/specs/dexpi-binding-v0.md`
- `docs/specs/safety-capability-v0.md`

If implementation evidence contradicts a spec, update the proposal/ADR rather than silently coding different semantics.

Cross-repo scope and branch workflow:

- `docs/ecosystem/program-charter.md`
- `docs/ecosystem/development-workflow.md`
- `docs/ecosystem/implementation-plan.md`
- `docs/ecosystem/decision-register.md`

## Target modules

Keep responsibilities separated:

- `simulation`: adapter around upstream `TEPSimulator`
- `registry`: canonical XMEAS/XMV/IDV metadata and units
- `contracts`: environment schemas
- `telemetry`: trace/history representation
- `snapshot`: snapshot/fork/replay semantics
- `process`: DEXPI/ProcessGraph normalization and topology queries
- `bindings`: semantic entity <-> runtime variable mapping
- `scenario`: deterministic supported scenario compilation
- `safety`: capability, shutdown/limit state, deterministic margins
- `persistence`: run/branch metadata and artifacts

Do not create a `agents/` package in this repository.

## Testing expectations

For each feature:

1. inspect upstream behavior before wrapping it;
2. implement acceptance tests from the canonical spec;
3. test failure/unsupported paths, not only happy path;
4. preserve branch/run provenance;
5. verify no state mutation on validation failure;
6. keep tests runnable without network/model access.

Specific high-value tests include same-seed reproduction, snapshot/fork isolation, registry consistency, DEXPI-binding validation, and unsupported-scenario rejection.

## Development-agent usage

Codex CLI, Claude Code, or similar coding agents may inspect/edit/test this repository as development assistants. They are not part of the runtime architecture.

Keep this file concise. Detailed contracts belong in `docs/specs`; unresolved decisions belong in `docs/open-questions.md`; reasons for architecture choices belong in ADRs.

## Known simulator constraint

For direct MV intervention, use `ControlMode.MANUAL` or an appropriate custom controller. In `CLOSED_LOOP`, the upstream PI controller can overwrite manual MV changes on the next step.
