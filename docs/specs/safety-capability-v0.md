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
