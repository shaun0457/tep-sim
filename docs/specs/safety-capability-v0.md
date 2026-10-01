# Safety and Capability v0

Status: proposal  
Version: v0  
Owner repo: `tep-sim`

## Goal

Make the sandbox honest about what it can simulate and expose deterministic process-safety information without implying unsupported consequence physics.

## Capability registry

`tep-sim` MUST expose machine-readable capabilities grouped by domain. Conceptually:

```text
runtime_variables
supported_disturbances
supported_mv_interventions
supported_constraints
supported_semantic_scenarios
snapshot_fidelity
consequence_domains
unsupported_domains
```

A capability entry SHOULD identify required control mode or other preconditions.

## Scenario compilation

Higher-level semantic requests MAY be compiled into TEP interventions when a deterministic, tested mapping exists.

Compilation result MUST be one of:

```text
SupportedScenario(interventions, provenance)
UnsupportedScenario(reason, missing_capability)
AmbiguousScenario(candidates, reason)
InvalidScenario(reason)
```

The environment MUST NOT ask an LLM to resolve an ambiguous scenario internally.

## Safety evaluation

For a rollout, `SafetyEvaluation` SHOULD report:

```text
shutdown_occurred
shutdown_time
termination_reason
limit_crossings
minimum_safety_margins
unsafe_intervals
relevant_process_events
unsupported_consequence_domains
```

Safety limits and derived margins MUST be deterministic and versioned.

## Supported vs unsupported statements

Examples of acceptable environment claims:

- reactor temperature exceeded a defined threshold;
- pressure approached a simulator shutdown boundary;
- a process shutdown occurred at simulation time T;
- one branch maintained a larger numeric safety margin than another.

Examples the current TEP model MUST NOT produce as simulated facts without an added validated model:

- pipe rupture occurred;
- toxic cloud radius was N meters;
- ignition probability was X;
- blast overpressure was Y;
- personnel fatality probability was Z.

## Layered validation boundary

This spec covers **environment capability and environment-native limits** only.

It does not decide whether an agent is authorized to request an otherwise valid intervention. Agent authorization and experiment-policy rules belong upstream in `industrial-agent-runtime` / `tep-agent-lab`.

## Invariants

- Unsupported physics produce explicit unsupported results.
- Environment safety evaluation is independent of LLM output.
- Agent explanation cannot alter numeric safety results.
- Capability checks occur before simulator mutation.
- Capability/version information is included in experiment provenance.

## Acceptance tests

1. Query supported IDVs/XMVs and verify against vendored runtime metadata.
2. Compile at least one known supported reactor-cooling scenario.
3. Reject a pipe-rupture/fire/dispersion request as unsupported.
4. Run a scenario that crosses a known process threshold and record deterministic safety events.
5. Confirm that two identical rollouts return equivalent safety evaluation.
6. Confirm capability rejection occurs before state mutation.

## A4 implementation notes (v0)

Implemented in `tep_sim.capability`, `tep_sim.scenario`, `tep_sim.safety`, and the
`TEPEnvironment` methods `capabilities()`, `compile_scenario()`, `apply_scenario()`,
and `evaluate_safety()`. No LLM, agent-authorization, RCA, or recovery logic is added.

- **Capability registry** (`tep-sim.capabilities/v0`). `capabilities()` returns an
  immutable `CapabilityRegistry` (replacing the A1/A2 flat mapping) with every spec
  domain. Entries are derived from the vendored `REGISTRY` and pinned upstream:
  73 runtime variables, IDV(1)-IDV(20) (IDV(16)-IDV(20) flagged
  `semantics_documented: false`), 12 MV interventions and 12 MV constraints
  (precondition `control_mode: manual`), the 8 shutdown limits, the tested scenario
  catalog with parameter bounds and mode preconditions, snapshot fidelity
  (`exact`/`cloned_state` for python), supported consequence domains
  (`process_trajectory`, `process_shutdown`, `process_limit_margin`), and unsupported
  domains (`pipe_rupture`, `fire`, `toxic_dispersion`, `blast_overpressure`,
  `personnel_casualty`). `to_json()` is the machine-readable form.
- **Scenario compilation** (`tep-sim.scenarios/v0`). `compile_scenario` is total and
  deterministic. Order: request type/id -> unsupported consequence domain ->
  ambiguous term -> unknown id (`UnsupportedScenario`, `scenario:<id>`) -> parameter
  schema/bounds (`InvalidScenario`) -> control-mode precondition
  (`UnsupportedScenario`, `control_mode:<modes>`) -> `SupportedScenario`.
  Tested mappings: reactor cooling-water inlet temperature step (IDV(4)) and random
  variation (IDV(11)), reactor cooling-water flow reduction (XMV(10), MANUAL only),
  condenser cooling-water inlet temperature step (IDV(5)). `loss_of_cooling` and
  `reactor_cooling_degradation` return `AmbiguousScenario` with candidate ids; the
  caller chooses.
- **Validation before mutation.** `apply_scenario` compiles, then validates every
  compiled intervention (A1 order, including lifecycle state) before committing any.
  Rejections raise `UnsupportedScenarioError` (an `UnsupportedCapability`),
  `AmbiguousScenarioError` or `InvalidScenarioError` (both `InvalidIntervention`),
  each carrying the compilation `result`. Applied scenarios are recorded in run
  provenance (`scenarios`) beside the individual interventions used for replay.
- **Safety limits** (`tep-sim.safety-limits/v0`). The 8 limits mirror the pinned
  upstream ISD check: reactor pressure > 3000 kPa (XMEAS(7)), reactor temperature
  > 175 deg C (XMEAS(9)), and reactor/separator/stripper liquid-volume limits
  converted to XMEAS(8)/XMEAS(12)/XMEAS(15) percent with upstream's own linear
  formulas. Strict comparisons match upstream. `Observation.safety_margins` is now
  populated (positive = inside the limit).
- **Safety evaluation** (`tep-sim.safety-evaluation/v0`). `evaluate_safety(rollout)`
  is a pure function of the checksum-verified telemetry artifact and the rollout
  termination reason. It reports `shutdown_occurred`, `shutdown_time`,
  `termination_reason`, `shutdown_limit_ids`, `limit_crossings`,
  `minimum_safety_margins`, `unsafe_intervals`, ordered `relevant_process_events`
  (disturbance activation/deactivation, limit crossed/recovered, shutdown), and
  `unsupported_consequence_domains`. A tampered telemetry checksum or a termination
  reason that disagrees with the recorded shutdown state is rejected.
- **Known resolution limits.** Margins and crossings use recorded measurements, so
  they include upstream measurement noise and are only as fine as
  `record_interval` (the shutdown record is always written). Shutdown occurrence is
  the simulator's own state, not inferred from margins.
- Provenance now records `capability_version`, `scenario_mapping_version`, and
  `safety_limits_version`. The A3 `ProcessGraph` fixture and its
  `PENDING_HUMAN_REVIEW` status are unchanged.
- **Review hardening.** Thresholds are read from the vendored
  `tep.constants.SAFETY_LIMITS`; only the XMEAS unit conversions are local.
  Multi-intervention scenarios are validated against the planned effects of earlier
  interventions in the same scenario before anything commits. Scenario mappings may
  carry a state precondition (the flow reduction must close XMV(10) below its
  current position); `compile_scenario` without an observation records it as
  unchecked, and `apply_scenario` always checks it. Disturbances already active at
  rollout start are reported as `disturbance_active`. `ENVIRONMENT_VERSION` is now
  `0.2.0` because observations hash `safety_margins`, so pre-A4 snapshots/replay
  specs fail the version check instead of a misleading replay mismatch.
- Replay reproduces the individual interventions; scenario provenance stays in the
  source branch's provenance (`scenarios`), reachable via `replay_of_branch_id`.
  The A2 replay format is unchanged.
- **Batch-3 closure (D-043).** ReplaySpec v0 reproduces the physical intervention
  trajectory; semantic scenario identity/mapping provenance remains in the source
  run/experiment provenance (`scenarios`). The A2 ReplaySpec format is unchanged.
  D0 benchmark records must retain a source provenance ref/checksum whenever
  semantic-scenario provenance matters.
- **Deep immutability.** `CapabilityRegistry` rejects attribute assignment;
  `CapabilityEntry.preconditions/details` (including nested scenario parameter
  metadata) and `SupportedScenario.provenance` (including `parameters` and
  `state_precondition`) are recursively frozen (`tep_sim.frozen.deep_freeze`).
  `to_json()` and persisted run provenance use thawed, JSON-safe copies, so caller
  mutation can neither alter later results nor persisted provenance.
