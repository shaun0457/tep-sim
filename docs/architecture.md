# Architecture: TEP Process Sandbox

## Decision

`tep-sim` is an **agent-agnostic, forkable process-simulation environment**.

Its job is to make the Tennessee Eastman Process available through stable, typed, reproducible contracts that can later be consumed by:

- normal Python experiments;
- deterministic controllers;
- HAZOP/RCA integration workflows;
- RL policies;
- LLM agents;
- dashboards and 3D visualizers.

The environment must not depend on any of those consumers.

---

## Design goals

1. **Reproducible** — same seed/config/intervention schedule should reproduce the same run within documented numerical tolerance.
2. **Forkable** — a caller can snapshot a state, create isolated branches, and compare counterfactual rollouts.
3. **Typed** — interventions and results use explicit schemas rather than raw array mutation.
4. **Capability-aware** — callers can discover what the environment can and cannot simulate.
5. **Auditable** — every run records simulator version, inputs, interventions, termination state, and result artifacts.
6. **Agent-agnostic** — no prompts, model SDKs, orchestration graph, agent memory, or subagent logic.
7. **Extensible** — future process/safety physics may be added without breaking the external environment contract.

---

## Non-goals

This repository does not attempt to:

- perform autonomous diagnosis;
- decide HAZOP credibility;
- generate recovery plans with an LLM;
- digitize P&ID drawings;
- infer missing engineering parameters;
- generate arbitrary plant simulators from diagrams;
- model all process-safety consequences.

Those are upstream/downstream projects.

---

## High-level architecture

```text
                  External Consumers

 Python      HAZOP/RCA       Agent Lab       UI / Replay
 scripts      workflow        / RL
    |             |             |                |
    +-------------+-------------+----------------+
                          |
                          v
                 +------------------+
                 | Public Env API   |
                 +------------------+
                   |   |   |   |   |
             observe  fork |   | capabilities
                        scenario  safety
                   |       |       |
                   v       v       v
             +--------------------------------+
             |         tep-sim core           |
             |                                |
             | registry   contracts           |
             | snapshot   scenario compiler   |
             | telemetry  safety evaluator    |
             | persistence/replay             |
             +---------------+----------------+
                             |
                             v
                  +-----------------------+
                  | upstream TEPSimulator |
                  +-----------------------+
```

---

## Public contracts

### `EnvironmentConfig`

Contains only information needed to reproduce environment behavior, for example:

```text
seed
backend
control_mode
dt
record_interval
upstream_revision
```

### `Observation`

A point-in-time, immutable view of the environment:

```text
simulation_time
xmeas
xmv
active_disturbances
shutdown
safety_margins
```

Arrays may exist internally, but the public layer should also make canonical IDs and metadata accessible.

### `Snapshot`

A serializable or cloneable environment state sufficient for deterministic continuation.

Requirements:

- creating a snapshot must not mutate the live environment;
- multiple forks from one snapshot must be isolated;
- snapshot format/version must be explicit;
- if upstream prevents exact serialization, the limitation must be documented and tested rather than hidden.

### `Intervention`

A typed request to mutate a supported environment quantity.

Examples:

```text
DisturbanceIntervention(target="IDV(4)", value=1)
MVIntervention(target="XMV(10)", value=55.0)
MVConstraint(target="XMV(10)", max_value=60.0)
```

The environment validates syntax, identity, bounds, and capability before mutation.

### `ProcessDeviation`

A higher-level, HAZOP-friendly request:

```text
ProcessDeviation(
    node="reactor_cooling_loop",
    parameter="flow",
    guide_word="LESS",
    magnitude=0.20,
)
```

This is **not** automatically an intervention. It must pass through a deterministic `ScenarioCompiler` that either:

1. maps it to one or more supported interventions; or
2. returns `UnsupportedScenario` / `AmbiguousScenario`.

### `RolloutResult`

Contains:

```text
run_id
config
start_snapshot_id
intervention_schedule
time
measurements
manipulated_variables
disturbances
shutdown_state
events
provenance
```

Large arrays should be written to an artifact format rather than repeatedly embedded into JSON/log messages.

### `SafetyEvaluation`

Deterministic result derived from a rollout:

```text
limit_crossings
minimum_margins
shutdown
shutdown_time
unsafe_intervals
unsupported_consequence_domains
```

`unsupported_consequence_domains` is important: process excursions are not equivalent to fire/explosion/toxic consequence modeling.

---

## Capability model

The environment should expose a machine-readable capability registry.

Conceptually:

```text
capabilities():
  disturbances:
    - IDV(1)..IDV(20)
  manipulated_variables:
    - XMV(1)..XMV(12)
  scenario_semantics:
    - feed_flow_change
    - feed_temperature_change
    - cooling_water_temperature_change
    - selected_valve_sticking
    - reaction_kinetics_variation
  consequence_models:
    - process_state
    - shutdown_state
  unsupported:
    - pipe_rupture_release
    - atmospheric_dispersion
    - fire_radiation
    - explosion_overpressure
```

This boundary prevents an external agent from confusing semantic plausibility with actual simulator support.

---

## Scenario compiler

The `ScenarioCompiler` is deterministic domain glue between higher-level experiment descriptions and TEP-specific actuators/disturbances.

```text
ProcessDeviation
      |
      v
canonical node/parameter lookup
      |
      v
supported mapping?
   /       \
 yes       no/ambiguous
  |           |
  v           v
Intervention  explicit failure
```

Example:

```text
reactor_cooling_loop + flow + LESS
```

may be representable by an XMV(10) constraint, while:

```text
reactor_pipe + containment + RUPTURE
```

is not supported by the current TEP physics.

Mappings must be stored as testable code/data, not as prompt instructions.

---

## Snapshot / fork / counterfactual semantics

Counterfactual branching is the key feature that turns a simulator into an agent playground.

```text
                      snapshot S
                    /     |      \
                   /      |       \
             branch A  branch B  branch C
                |          |         |
              action A   action B  no action
                |          |         |
             rollout     rollout   rollout
                \          |        /
                 \         |       /
                    compare
```

Rules:

- branches cannot share mutable simulator state;
- all branches retain parent snapshot provenance;
- comparison is performed outside the simulator core;
- simulation clocks and random generators must be handled so results are meaningful.

---

## Safety boundary

The upstream TEP model includes process shutdown/safety limits. `tep-sim` should expose those cleanly and may derive additional deterministic margins.

Do not equate these with a full process-safety consequence model.

For example, a rollout can truthfully report:

```text
reactor temperature exceeded threshold
reactor pressure approached shutdown
process shut down at t = ...
```

It cannot truthfully report, without additional models:

```text
pipe ruptured
flammable cloud radius = ...
blast overpressure = ...
personnel fatality probability = ...
```

---

## Persistence and reproducibility

Every run should record at least:

```text
run_id
created_at
tep-sim version/commit
upstream submodule commit
Python/backend versions
seed
EnvironmentConfig
initial snapshot/config
intervention schedule
termination reason
artifact paths/checksums
```

Prefer Parquet/NPZ for dense numeric traces plus JSON/JSONL for metadata/events. SQLite may be added if run querying becomes important.

---

## Integration boundary with agent systems

Agent systems integrate through the public environment API only.

Correct:

```text
agent runtime -> tool adapter -> TEPEnvironment
```

Incorrect:

```text
TEPEnvironment imports LangGraph/provider SDK/prompt files
```

The agent runtime may decide what experiment to request. The environment decides whether the requested experiment is valid and simulable.

---

## Visualization

Visualization consumes `Observation` and `RolloutResult`.

Initial target:

- process topology view;
- key XMEAS/XMV trends;
- active disturbance/intervention markers;
- safety-margin overlays;
- branch/experiment comparison.

Blender/Omniverse/DEXPI-derived visuals can be added later, but rendering remains downstream from environment state.

---

## Repository boundary

See [`ecosystem/README.md`](ecosystem/README.md).

The short version:

```text
tep-sim                  = environment
industrial-agent-runtime = generic agent harness
tep-agent-lab            = TEP + agents + HAZOP/RCA experiments
pid2sim                  = P&ID/engineering-data -> executable model research
```

Existing `manufacturing-kg-agent` may later provide optional domain evidence, but it is not a dependency of the simulator.
