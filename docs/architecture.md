# Architecture: TEP Process Sandbox

## Decision

`tep-sim` is an **agent-agnostic, forkable Tennessee Eastman Process environment**.

It owns the executable process world and its machine-readable process semantics. It does not own agent reasoning.

The environment can be consumed by Python experiments, deterministic controllers, `tep-agent-lab`, RL policies, dashboards, or future visualizers without importing any of those consumers.

## Design goals

1. **Reproducible** — same seed/config/intervention schedule reproduces the same run within documented numerical tolerance.
2. **Forkable** — callers can snapshot state, create isolated branches, and compare counterfactual rollouts.
3. **Typed** — public interventions/results use explicit schemas rather than raw array mutation.
4. **Capability-aware** — callers can discover what the environment can and cannot simulate.
5. **Semantically queryable** — callers can query process topology and bind process entities to XMEAS/XMV/IDV through an explicit registry.
6. **Auditable** — runs record simulator version, inputs, interventions, termination state, and artifact provenance.
7. **Agent-agnostic** — no prompts, model SDKs, LangGraph state, memory, or subagent logic.

## Non-goals

This repository does not perform autonomous diagnosis, HAZOP reasoning, recovery planning, P&ID OCR, generic P&ID-to-simulation generation, LLM orchestration, or 3D reconstruction.

## High-level architecture

```text
                 External Consumers
 Python scripts   Agent Lab   UI / Replay   RL
       \             |            |          /
        +------------+------------+---------+
                     |
                     v
              Public Environment API
                     |
      +--------------+----------------+
      |              |                |
      v              v                v
  Simulation      Process         Experiment
   runtime        semantics        services
      |              |                |
      |        DEXPI / compact         |
      |        ProcessGraph            |
      |              |                |
      +------ binding registry --------+
                     |
                     v
              upstream TEPSimulator
```

## Core public contracts

### `EnvironmentConfig`

At minimum: `seed`, `backend`, `control_mode`, `dt`, `record_interval`, and `upstream_revision`.

### `Observation`

Immutable point-in-time state containing simulation time, XMEAS, XMV, active disturbances, shutdown state, and deterministic safety margins.

### `Snapshot`

A cloneable/serializable state sufficient for deterministic continuation. Forks from one snapshot must be isolated and retain parent provenance.

### `Intervention`

Typed environment mutation such as disturbance activation, MV change, or MV constraint. The environment validates identity, bounds, and simulator capability before applying it.

### `ProcessGraph`

A compact runtime representation derived from DEXPI/process data. It exposes units, process steps/equipment, streams, topology, measurements, actuators, and explicit binding metadata.

DEXPI is the **static engineering-semantic layer**; `TEPSimulator` remains the dynamic source of truth.

### `ProcessDeviation`

A higher-level HAZOP-friendly description such as `reactor_cooling_loop + flow + LESS`. It is not directly executable. A deterministic scenario compiler maps it to supported TEP interventions or returns an explicit unsupported/ambiguous result.

### `RolloutResult`

Contains run ID, config, start snapshot, intervention schedule, telemetry artifact references, shutdown state, events, and provenance.

### `SafetyEvaluation`

Deterministic evaluation of TEP-supported process limits. It may report threshold crossing and shutdown behavior but must not fabricate unsupported fire/explosion/dispersion consequences.

## DEXPI / TEP semantic binding

For TEP we do **not** build an OCR/P&ID digitization pipeline. We ingest or curate a machine-readable Tennessee Eastman DEXPI/process representation and normalize it into `ProcessGraph`.

The binding layer explicitly maps semantic entities to runtime variables, for example:

```text
Reactor
  temperature measurement -> XMEAS(9)
  cooling-water outlet temp -> XMEAS(21)
  cooling-water flow actuator -> XMV(10)
  cooling-water disturbances -> selected IDV entries
```

Bindings are data/code with validation tests, not prompt knowledge.

See `docs/dexpi-tep-integration.md` and `docs/specs/dexpi-binding-v0.md`.

## Capability model

The environment exposes a machine-readable capability registry covering supported disturbances, manipulated variables, scenario semantics, consequence domains, and unsupported domains.

Unsupported requests return an explicit result. Semantic plausibility is never treated as proof that the simulator can model the requested event.

## Snapshot / fork / counterfactual semantics

```text
                   snapshot S
                 /     |      \
             branch A branch B branch C
                |        |       |
             action A action B  no action
                |        |       |
             rollout  rollout  rollout
                 \       |      /
                      compare
```

Branches must not share mutable simulator state. Random-number handling and snapshot provenance must be explicit so comparisons remain meaningful.

## Safety boundary

`tep-sim` exposes simulator shutdown logic and deterministic process-safety margins that can be computed from available state. It is not a general consequence-analysis package.

## Persistence

Every run records at least: run ID, `tep-sim` revision, upstream simulator revision, runtime versions, seed, environment config, initial snapshot/config, intervention schedule, termination reason, and artifact checksums/paths.

Prefer Parquet/NPZ for dense traces and JSON/JSONL for metadata/events. Add SQLite only when cross-run querying becomes valuable.

## Integration boundary

Correct:

```text
industrial-agent-runtime
        |
        v
tep-agent-lab tool/policy adapters
        |
        v
tep-sim public API
```

Incorrect:

```text
tep-sim imports LangGraph / provider SDK / prompts
```

The agent side decides what experiment to request. `tep-sim` decides whether that experiment is syntactically valid and physically/simulator-supported.

## Visualization

Initial visualization is a read-only process topology + telemetry view. 3D is optional and explicitly not a milestone for the agent research program.

## Repository boundary

The active program uses three core repositories:

```text
tep-sim                  = environment + process semantics
industrial-agent-runtime = generic agent mechanics
tep-agent-lab            = TEP-specific agent tools, workflows, experiments, evals
```

`manufacturing-kg-agent` may later provide optional evidence. Generic P&ID digitization/model generation is parked research, not a core dependency or milestone.
