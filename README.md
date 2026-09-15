# tep-sim

Agent-agnostic Tennessee Eastman Process (TEP) simulation sandbox for reproducible process-control, fault, safety, and counterfactual experiments.

## Scope

`tep-sim` owns the **environment**, not the agent.

It should provide a stable programmatic world that can be used by humans, scripts, RL policies, LLM agents, HAZOP tooling, and integration labs without knowing which reasoning system is driving it.

Core responsibilities:

- deterministic TEP dynamics and reproducible seeds;
- canonical XMEAS / XMV / IDV metadata;
- disturbance and intervention APIs;
- observation and telemetry APIs;
- snapshot / fork / replay for counterfactual experiments;
- explicit capability discovery;
- deterministic safety-limit evaluation and run termination;
- traceable run metadata and results;
- machine-readable process topology/semantics for TEP;
- later, read-only visualization consumers.

Out of scope:

- LLM provider integration;
- LangGraph or other agent orchestration;
- prompts, agent memory, dynamic subagent spawning;
- HAZOP/RCA reasoning logic;
- P&ID image digitization/OCR;
- generic P&ID-to-simulation generation;
- photorealistic 3D plant reconstruction.

Those boundaries are described in [`docs/ecosystem/README.md`](docs/ecosystem/README.md).

## Simulator

The process model is vendored as a git submodule at `vendor/tep-sim-upstream` and points to `jkitchin/tennessee-eastman-profbraatz`.

Important facts:

- `TEPSimulator.step()` advances the process one simulation step.
- `ControlMode.CLOSED_LOOP` uses built-in PI controllers and can overwrite manual MV changes.
- Direct intervention experiments therefore use `ControlMode.MANUAL` or a suitable custom controller/plugin.
- Upstream exposes measurements, manipulated variables, disturbances, streaming history, detector hooks, and custom-controller interfaces.

## Static semantics + dynamic simulation

For the Tennessee Eastman benchmark, do not build a P&ID OCR pipeline. Use DEXPI Process / a curated machine-readable TEP process representation as the **static engineering-semantic layer**, and bind it to the existing TEP simulator as the **dynamic layer**.

```text
DEXPI / process graph
  equipment / process steps / streams / variables / connectivity
                    |
                    v
             TEP binding layer
                    |
          entity <-> XMEAS/XMV/IDV
                    |
                    v
              TEP simulator
        dynamics / disturbances / control
```

This gives agents a queryable process world without making drawing digitization part of the research problem.

See [`docs/dexpi-tep-integration.md`](docs/dexpi-tep-integration.md).

## Target environment API

```python
env = TEPEnvironment(seed=42)
obs = env.reset()

snapshot = env.snapshot()
branch = env.fork(snapshot)

branch.inject(
    Intervention(
        kind="disturbance",
        target="IDV(4)",
        value=1,
    )
)

result = branch.rollout(horizon_seconds=1800)
report = branch.evaluate_safety(result)
```

Non-negotiable properties:

1. reproducibility;
2. typed interventions;
3. no hidden LLM behavior inside the environment.

## Capability boundary

A caller must be able to ask what the sandbox supports before requesting an experiment.

TEP can model feed changes, cooling-water disturbances, valve sticking, reaction-kinetics variation, manipulated-variable changes, and resulting process/shutdown behavior.

It must **not pretend** to model hazards absent from its physics, such as pipe rupture, toxic-cloud dispersion, ignition, fire radiation, or blast overpressure. Unsupported scenarios return an explicit capability error.

## Variable mapping

Runtime code must derive variable metadata from the vendored simulator, not from an LLM prompt or duplicated literature table. A temporary human-readable mapping is kept in [`docs/runtime-variable-map.md`](docs/runtime-variable-map.md).

In particular:

- XMV(6): Purge Valve
- XMV(7): Separator Pot Liquid Flow
- XMV(8): Stripper Liquid Product Flow
- XMV(9): Stripper Steam Valve
- XMV(10): Reactor Cooling Water Flow
- XMV(11): Condenser Cooling Water Flow

## Near-term milestone

```text
reset
-> run baseline
-> snapshot
-> fork
-> inject supported disturbance
-> rollout
-> capture telemetry and safety state
-> replay with same seed/config
-> obtain identical result within numerical tolerance
```

Then add the DEXPI/topology binding and expose it as read-only/queryable environment context for the agent lab.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — sandbox architecture and contracts
- [`docs/roadmap.md`](docs/roadmap.md) — implementation sequence
- [`docs/runtime-variable-map.md`](docs/runtime-variable-map.md) — runtime mapping reference
- [`docs/dexpi-tep-integration.md`](docs/dexpi-tep-integration.md) — DEXPI/process-graph integration for TEP
- [`docs/ecosystem/README.md`](docs/ecosystem/README.md) — focused three-repository ecosystem
- [`docs/ecosystem/pid-to-sim-automation.md`](docs/ecosystem/pid-to-sim-automation.md) — parked research note, not current scope
- [`AGENTS.md`](AGENTS.md) — repository rules for coding agents
- [`CLAUDE.md`](CLAUDE.md) — concise Claude Code context
