# A4 capability / safety handoff

Branch `feat/capability-safety-v0`. Owning spec: `docs/specs/safety-capability-v0.md`
(see "A4 implementation notes").

## Delivered

- `tep_sim.capability`: versioned `CapabilityRegistry` covering every spec domain.
- `tep_sim.scenario`: `ScenarioRequest` and `compile_scenario` returning
  `SupportedScenario | UnsupportedScenario | AmbiguousScenario | InvalidScenario`.
- `tep_sim.safety`: versioned shutdown limits, `Observation.safety_margins`, and the
  pure `evaluate_safety(rollout) -> SafetyEvaluation`.
- `TEPEnvironment.capabilities()/compile_scenario()/apply_scenario()/evaluate_safety()`.

## Acceptance mapping (`tests/test_safety_capability.py`)

1. IDV/XMV capabilities vs vendored metadata: `test_capabilities_match_vendored_runtime_metadata`.
2. Supported reactor-cooling scenario: `test_compile_supported_reactor_cooling_scenarios`,
   `test_apply_supported_scenario_records_provenance`.
3. Pipe rupture / fire / dispersion / blast / casualty unsupported:
   `test_consequence_physics_requests_are_unsupported`.
4. Threshold crossing with deterministic safety events (MANUAL, XMV(10) = 0 ->
   reactor pressure ISD after ~196 s): `test_cooling_loss_crosses_shutdown_limit_and_records_events`.
5. Identical rollouts give equal evaluations: `test_identical_rollouts_give_identical_evaluations`.
6. Rejection before mutation: `test_rejected_scenarios_never_mutate_state`,
   `test_multi_intervention_scenario_validates_all_before_mutating`,
   `test_terminated_environment_rejects_scenario_before_mutation`.

Negative paths also cover malformed scenarios, ambiguity, mode preconditions,
tampered telemetry, immutability, upstream level-limit equivalence, and an AST
boundary check (no agent/runtime/model imports).

## Not in scope

Agent authorization, GatePolicy, RCA/recovery policy, LLM logic, HAZOP findings.
Which scenarios an Agent may request is a runtime/lab decision.

## Unresolved

- `capabilities()` now returns a `CapabilityRegistry` instead of the A1/A2 flat
  mapping; the two existing assertions were updated. No external consumer exists yet.
- Margins inherit measurement noise and telemetry resolution (documented in spec).
- A3 `ProcessGraph` remains `PENDING_HUMAN_REVIEW`; this blocks D0 freeze, not A4.

No `SPEC_CONFLICT`.

## Batch-3 review closure

- Deep immutability for capability and scenario data (see spec notes).
- Replay decision recorded as D-043. The register also records the B3
  adjudications D-039–D-042 (owning spec:
  `industrial-agent-runtime/docs/specs/hybrid-orchestration-v0.md`).
