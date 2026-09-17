# Implementation batch 1 — 2026-09-17

Canonical release: design-freeze-record.md at tep-sim 3d0de4172bb7cb142d5564584365617c0db76459.
The historical hold text in development-workflow.md is superseded by that release.
No public architecture contracts are changed by this plan.

## Repository baseline

- tep-sim: clean architecture/hybrid-agent-runtime, 3d0de4172bb7cb142d5564584365617c0db76459.
- industrial-agent-runtime: initially empty repository; frozen blueprint copied verbatim, a2e8ea6.
- tep-agent-lab: initially empty repository; frozen blueprint copied verbatim, a0a761a.

## Work allocation and dependency order

| Task | Branch / isolated location | Owned modules | Inputs / blocking dependencies |
| --- | --- | --- | --- |
| A1 | feat/environment-api-v0 / ../.worktrees/a1 | environment contracts, simulation, metadata adapter, telemetry/provenance, A1 tests and packaging | environment-api-v0.md; vendored simulator revision; inspect actual upstream first |
| B1 | feat/contracts-runtime-v0 / ../.worktrees/b1 | generic contracts/protocols, fake provider, reference dispatcher, trace, B1 tests and packaging | runtime-v0.md + hybrid-orchestration-v0.md; gates/subagents specs constrain seams |
| C1 independent | feat/investigation-state-v0 / ../tep-agent-lab | persistence.py, records.py, corresponding tests and lab packaging | investigation-state-v0.md + engineering-records-v0.md + information-plane.md; append-only storage can start immediately; runtime InformationRef integration pins B1 |
| C2 independent | feat/rule-registry-v0 / ../.worktrees/c2 | rules.py, test_rules.py, c2-handoff.md only | knowledge-rule-registry-v0.md; no simulator truth duplicated; real tool/gate adapter waits for A1/B1 |
| C3 independent | feat/hypothesis-experiment-v0 / separate lab worktree after packaging baseline | experiments.py, test_experiments.py, c3-handoff.md | hypothesis-experiment-v0.md; typed predictions and normalized content key independent; StateDelta mapping waits for B1 + C1 typed state validation |

A1 and B1 execute independently; C2 shares no mutable modules with C1/C3.
Each worker must commit and supply files, exact test command/output, acceptance coverage,
regression results, boundary audit, limitations, SPEC_CONFLICTs, and commit SHA.
The coordinator collects every worker before final handoff. Integration uses exact commits,
not worktree-relative implicit imports or completion order.

## Acceptance and regression gates

- A1: all six environment acceptance cases; real upstream same-seed baseline and IDV replay;
  immutable observations; unknown/unsupported/mode/bounds rejection before mutation;
  complete persisted provenance and external dense telemetry; offline/domain-independent tests.
- B1: all four ModelTurn actions with fake provider; atomic multi-delta store example;
  rejected/stale update blocks same-turn dispatch; exact projection tracing; state-step accounting;
  dependency/cycle/failure TOOL WorkBatch and stable current-revision ingestion; no domain imports.
  B2/B3 hooks must fail closed where downstream implementations are unavailable.
- C1 independent: append-only event/artifact immutability; restart/readback and tamper detection;
  negative/failed records preserved; engineering record refs/provenance verified; new versions
  preserve old records; archive creation has no rule/projection side effect.
- C2: all seven rule acceptance cases via deterministic policy selection with test consumer;
  provenance/version preservation; no Agent authority escalation or automatic promotion.
- C3 independent: typed expected values/tolerances; deterministic supported feature matching;
  explicit unsupported/unscored behavior; identical parent content with different snapshot IDs
  yields identical key; version/seed/horizon/preprocessing changes affect identity; duplicate rejection.
- Run each repo suite plus compile/import checks and inspect imports for boundary violations.
  Integration-only acceptance cases must be explicitly reported pending, never counted as passed.

## Next dependent increments

1. Pin B1 contracts; implement/integrate C1 RcaState.apply_batch/projection/automatic ingestion.
2. C3 hypothesis/interpretation StateDelta mapping consumes that C1 operation validation.
3. B2/B3 gates and verified ingestion; A2 snapshot/fork needed for actual C3 isolated execution.
4. C4/C5 real adapters depend on these contracts; benchmark D0 follows. No provider required here.

## Explicit exclusions

No A2-A4 expansion, real provider credentials, product subagent implementation, unrestricted code
execution, DAG engine, LangGraph/MCP, learned memory, knowledge promotion, benchmark claims,
HAZOP, Recovery or AutoResearch implementation in this batch.

## Conflict handling

SPEC_CONFLICT reports name the owning spec, implementation evidence, contradictory assumptions,
and smallest proposed contract change. Stop only dependent work; never change frozen contracts
silently. Missing packaging/file names are implementation details, not grounds for architecture redesign.
