# Phase 0 Design Freeze Record — 2026-09-15

Status: **COMPLETE / READY FOR IMPLEMENTATION**

This record closes the architecture/spec review cycle for the v0 TEP Agent Playground control/investigation contracts.

It is a release/governance record, not a replacement for owning specs.

## Review chain

1. Independent full review:
   - `reviews/2026-09-15-independent-spec-review.md`
   - verdict: **NOT READY FOR DESIGN FREEZE**
   - identified three architecture BLOCKERs plus implementation-defining MAJOR findings.

2. Program adjudication:
   - `design-review-adjudication.md`
   - accepted/simplified the findings and updated canonical specs.

3. Independent focused re-review:
   - `reviews/2026-09-15-focused-re-review.md`
   - verdict: **READY WITH CONDITIONS**
   - confirmed all original BLOCKERs closed and nine of ten original MAJORs closed;
   - found one remaining implementation-defining MAJOR, `MAJOR-R1`, concerning how Main Agent state proposals become `StateDelta`s.
   - explicitly stated that closing R1 is sufficient for **READY FOR DESIGN FREEZE**.

4. R1 closure:
   - runtime `ModelTurn` now contains an explicit optional `ModelStateUpdateProposal` plus one routed action;
   - model-proposed state changes are bound to the exact `ContextProjection.base_revision` seen by the model;
   - state-update batches are atomically validated/applied through consumer `TaskStateStore.apply_batch`;
   - model state updates consume `max_steps` but not `max_tool_calls`;
   - rejected/stale state updates prevent the same turn's execution action from dispatching;
   - every successful agent-visible ToolResult is deterministically registered as an ObservationRecord by the lab ingestion path;
   - evidence creation remains an explicit `ADD_EVIDENCE_LINK` model state update;
   - result-ingestion deltas from parallel WorkBatch items bind the current revision at deterministic ingestion time, avoiding false stale conflicts;
   - `ExperimentInterpretation` is explicitly mapped to typed StateDelta operations.

Owning contracts:

- `blueprints/industrial-agent-runtime/docs/specs/runtime-v0.md`
- `blueprints/industrial-agent-runtime/docs/specs/hybrid-orchestration-v0.md`
- `blueprints/industrial-agent-runtime/docs/specs/deterministic-gates-v0.md`
- `blueprints/tep-agent-lab/docs/specs/investigation-state-v0.md`
- `blueprints/tep-agent-lab/docs/specs/hypothesis-experiment-v0.md`

Decision Register: D-032 / D-033.

## Frozen v0 architecture boundary

```text
ContextProjection
      |
      v
Main Agent / ModelTurn
      |
      +-- ModelStateUpdateProposal? --> TaskStateStore.apply_batch
      |
      +-- action --------------------> NONE | TOOL_REQUEST | WORK_BATCH | FINISH
                                          |
                                          v
                                  pre-execution gates
                                          |
                                          v
                                       Executor
                                          |
                                          v
                                  post-exec verify_result
                                          |
                                          v
                               deterministic result ingestion
                                          |
                                          v
                                  TaskStateStore.apply_batch
```

The v0 contract intentionally does **not** require:

- a full mutable Dynamic DAG engine;
- LangGraph;
- MCP;
- learned cross-run Agent memory;
- five physical Information Plane databases/services;
- automated Lesson Learned/Runbook promotion;
- unrestricted code/shell execution.

Those remain deferred research/extensions.

## Implementation release

### GO — `tep-sim`

- A1 environment API
- A2 snapshot/fork/replay
- A3 DEXPI/ProcessGraph binding
- A4 capability/safety

These were already independently cleared by the first review.

### GO — `industrial-agent-runtime`

- B1 core contracts/reference loop
- B2 deterministic gates
- B3 post-execution verification
- B4 bounded ephemeral subagents
- B5 provider adapter after fake-provider contract tests

Implementation must conform to the frozen v0 specs. A coding agent may not silently restore full-DAG/LangGraph/EvidenceBundle-era semantics.

### GO — `tep-agent-lab`

- C1 RcaState/run log/projection/engineering records
- C2 rule/policy metadata
- C3 hypothesis/prediction/experiment contracts
- C4 TEP tool surface
- C5 minimal Tool Bridge
- D0 benchmark/C0/identifiability pilot once dependencies are available

Later HAZOP/Recovery/AutoResearch work remains ordered by `implementation-plan.md` and their own proposal specs.

## What Design Freeze means

Design Freeze means implementation agents should no longer need to invent **product architecture** for B1/C1 and their immediate dependencies.

It does not mean:

- every empirical parameter is fixed;
- Hybrid is proven superior;
- subagent limits are scientifically optimal;
- first RCA causes/magnitudes are already selected;
- later HAZOP/Recovery/AutoResearch contracts can never evolve.

Those remain experiment/pilot questions.

## Spec-conflict rule

If implementation reveals an architecture contradiction or missing public contract:

```text
SPEC_CONFLICT
 -> stop local invention
 -> capture evidence
 -> update owning spec/ADR/Decision Register
 -> then continue implementation
```

Do not silently resolve architecture gaps only in code.

## Final Phase 0 verdict

**READY FOR DESIGN FREEZE / IMPLEMENTATION RELEASED** for the runtime/lab v0 control-state boundary.

Remaining DEFER / OPEN_RESEARCH items are explicitly non-blocking and should be answered by pilots/ablations rather than additional architecture speculation.
