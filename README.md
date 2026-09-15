# tep-sim

Agent-agnostic Tennessee Eastman Process (TEP) simulation sandbox for reproducible process-control, fault, safety, and counterfactual experiments.

## Scope

`tep-sim` owns the **environment**, not the agent.

It should provide a stable programmatic world that can be used by humans, scripts, RL policies, LLM agents, HAZOP tooling, and future integration labs without knowing which reasoning system is driving it.

Core responsibilities:

- deterministic TEP dynamics and reproducible seeds;
- canonical XMEAS / XMV / IDV metadata;
- disturbance and intervention APIs;
- observation and telemetry APIs;
- snapshot / fork / replay for counterfactual experiments;
- explicit capability discovery so callers know what the environment can actually simulate;
- deterministic safety-limit evaluation and run termination;
- traceable run metadata and results;
- later, read-only visualization consumers.

Out of scope:

- LLM provider integration;
- LangGraph or other agent orchestration;
- prompts, agent memory, dynamic subagent spawning;
- HAZOP reasoning logic;
- RCA reasoning logic;
- P&ID image digitization;
- generic P&ID-to-simulation model generation.

Those live in separate repositories described in [`docs/ecosystem/README.md`](docs/ecosystem/README.md).

## Simulator

The process model is vendored as a git submodule at `vendor/tep-sim-upstream` and points to `jkitchin/tennessee-eastman-profbraatz`.

Important facts:

- `TEPSimulator.step()` advances the process one simulation step.
- `ControlMode.CLOSED_LOOP` uses the built-in PI controllers and can overwrite manual MV changes.
- Direct intervention experiments therefore use `ControlMode.MANUAL` or a suitable custom controller/plugin.
- Upstream already exposes measurements, manipulated variables, disturbances, streaming history, detector hooks, and custom-controller interfaces.

## Target environment API

The long-term public API should feel like this:

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

The exact API can evolve, but three properties are non-negotiable:

1. reproducibility;
2. typed interventions;
3. no hidden LLM behavior inside the environment.

## Capability boundary

A caller must be able to ask what the sandbox supports before requesting an experiment.

For example, TEP can model process disturbances such as feed changes, cooling-water disturbances, valve sticking, reaction-kinetics variation, manipulated-variable changes, and resulting process/shutdown behavior.

It must **not pretend** to model hazards that are absent from its physics, such as a pipe rupture, toxic-cloud dispersion, ignition, fire radiation, or blast overpressure. Unsupported scenarios should return an explicit capability error rather than a fabricated result.

## Variable mapping

Runtime code must derive variable metadata from the vendored simulator, not from an LLM prompt or duplicated literature table. A temporary human-readable mapping is kept in [`docs/runtime-variable-map.md`](docs/runtime-variable-map.md).

In particular, the vendored simulator maps:

- XMV(6): Purge Valve
- XMV(7): Separator Pot Liquid Flow
- XMV(8): Stripper Liquid Product Flow
- XMV(9): Stripper Steam Valve
- XMV(10): Reactor Cooling Water Flow
- XMV(11): Condenser Cooling Water Flow

## Near-term milestone

The first environment milestone is a headless reproducible experiment:

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

After that, add scenario compilation, HAZOP-friendly deviation contracts, and visualization adapters.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — sandbox architecture and contracts
- [`docs/roadmap.md`](docs/roadmap.md) — implementation sequence
- [`docs/runtime-variable-map.md`](docs/runtime-variable-map.md) — current runtime mapping reference
- [`docs/ecosystem/README.md`](docs/ecosystem/README.md) — multi-repository ecosystem
- [`docs/ecosystem/pid-to-sim-automation.md`](docs/ecosystem/pid-to-sim-automation.md) — boundary between P&ID digitization and executable simulation
- [`AGENTS.md`](AGENTS.md) — repository rules for coding agents
- [`CLAUDE.md`](CLAUDE.md) — concise Claude Code context
