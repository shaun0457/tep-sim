# tep-sim

Tennessee Eastman Process (TEP) dynamic simulation with an event-driven agent layer for diagnosis, recovery planning, and controlled intervention.

## Goal

Build a reproducible TEP testbed where:

1. the physical/process simulation runs deterministically;
2. alarms, safety checks, feature extraction, and action validation are code, not LLM prompts;
3. an LLM is called only when an event needs diagnosis or recovery reasoning;
4. every proposed control action is typed, validated, logged, and reversible;
5. the process state and agent decisions can later be visualized as a pipeline/dashboard.

## Simulator

The process model is vendored as a git submodule at `vendor/tep-sim-upstream` and currently points to `jkitchin/tennessee-eastman-profbraatz`.

Important runtime facts:

- `TEPSimulator.step()` advances the process one simulation step.
- `ControlMode.CLOSED_LOOP` uses the built-in PI controllers and can overwrite manual MV changes.
- Agent-driven control therefore uses `ControlMode.MANUAL` or a custom controller/plugin.
- Upstream already exposes measurements, manipulated variables, disturbances, streaming history, detector hooks, and custom controller interfaces.

## Architecture decision

Use **CLI coding agents for development**, not as the online plant-control runtime.

The online runtime is a hybrid:

```text
TEP simulator
    |
    v
state sampler / rolling window
    |
    v
deterministic detectors + safety gates
    |
    +---------------- no event ----------------> continue simulation
    |
    v
compact incident context
    |
    v
LLM diagnosis / recovery proposal
    |
    v
deterministic action validator
    |
    +------------ reject / safe fallback ------> monitor
    |
    v
apply bounded XMV action
    |
    v
post-action verification
```

LangGraph is useful around the **slow reasoning path** (diagnose -> propose -> verify/escalate), where persistence, retries, interrupts, or human approval are valuable. It should not own the 1-second simulation loop.

See [`docs/architecture.md`](docs/architecture.md) for the design and [`docs/roadmap.md`](docs/roadmap.md) for implementation order.

## Agent principle

The agent never receives the full simulation history and never directly calls `set_mv()`.

Instead it receives a compact typed incident snapshot and returns a typed proposal. A deterministic gate validates variable identity, bounds, rate-of-change, safety rules, cooldowns, and action permissions before anything reaches the simulator.

## Variable mapping

Do not hard-code XMEAS/XMV meanings in prompts. Use the simulator's canonical metadata as the source of truth. In particular, the vendored simulator maps:

- XMV(6): Purge Valve
- XMV(7): Separator Pot Liquid Flow
- XMV(8): Stripper Liquid Product Flow
- XMV(9): Stripper Steam Valve
- XMV(10): Reactor Cooling Water Flow
- XMV(11): Condenser Cooling Water Flow

This mapping is critical for experiments involving XMEAS(9) reactor temperature.

## Development agents

Repository-level instructions for Codex/Claude-style coding agents live in [`AGENTS.md`](AGENTS.md). Claude-specific setup remains in [`CLAUDE.md`](CLAUDE.md).

## Near-term milestone

The first useful milestone is **not** a 3D plant visualization. It is a headless, reproducible closed experiment:

```text
normal run -> inject one TEP disturbance -> deterministic detection
-> agent diagnosis -> bounded proposed action -> gate -> apply/reject
-> verify recovery -> save run trace
```

Only after that loop is stable should the dashboard/pipeline visualization become the next layer.
