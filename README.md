# tep-sim

Agent-agnostic Tennessee Eastman Process (TEP) sandbox for reproducible process, fault, safety, and counterfactual experiments.

## Scope

`tep-sim` owns the **environment**, not the agent.

It provides a stable programmatic world for scripts, deterministic controllers, RL policies, agent-tool adapters, benchmark labs, and read-only visualizers without knowing which reasoning system consumes it.

Core responsibilities:

- deterministic TEP dynamics and reproducible seeds;
- canonical XMEAS/XMV/IDV metadata;
- typed observation/intervention APIs;
- snapshot/fork/replay;
- machine-readable capability and deterministic safety evaluation;
- machine-readable TEP process topology/semantics;
- DEXPI/process-data normalization and semantic-to-runtime bindings;
- traceable run provenance/artifacts.

Out of scope:

- LLM/provider integration;
- LangGraph/agent orchestration;
- prompts, memory, subagents;
- RCA/HAZOP reasoning;
- generic P&ID OCR/model generation;
- 3D plant reconstruction.

See [`docs/ecosystem/README.md`](docs/ecosystem/README.md) for the three-repository program boundary.

## Simulator

The process model is vendored as `vendor/tep-sim-upstream` from `jkitchin/tennessee-eastman-profbraatz`.

Important facts:

- `TEPSimulator.step()` advances one simulation step.
- `ControlMode.CLOSED_LOOP` uses built-in PI controllers and can overwrite manual MV changes.
- Direct MV intervention therefore requires `ControlMode.MANUAL` or a suitable custom controller/plugin.
- Runtime variable identity comes from the vendored simulator/registry, not duplicated literature tables or prompts.

## Static semantics + dynamic simulation

For TEP, do not build a P&ID computer-vision pipeline. Use machine-readable DEXPI/process data as the **static engineering-semantic layer** and the existing TEP simulator as the **dynamic layer**.

```text
DEXPI / ProcessGraph
  topology / process steps / streams / semantics
                 |
                 v
          binding registry
       entity <-> XMEAS/XMV/IDV
                 |
                 v
           TEP simulator
  dynamics / disturbances / control / shutdown
```

See [`docs/dexpi-tep-integration.md`](docs/dexpi-tep-integration.md) and [`docs/specs/dexpi-binding-v0.md`](docs/specs/dexpi-binding-v0.md).

## Target environment behavior

Conceptually:

```python
env = TEPEnvironment(config)
obs = env.reset()

snapshot = env.snapshot()
branch = env.fork(snapshot)
branch.apply(intervention)
result = branch.rollout(horizon=...)
safety = branch.evaluate_safety(result)
```

Non-negotiable properties:

1. reproducibility;
2. typed interventions;
3. explicit capability/unsupported behavior;
4. branch isolation/provenance;
5. no hidden LLM behavior.

## Capability boundary

TEP can represent selected feed/cooling-water/process disturbances, valve/control behavior, manipulated-variable changes, process-variable propagation, and shutdown behavior.

It must not pretend to simulate absent consequence physics such as pipe rupture release, atmospheric dispersion, ignition/fire radiation, blast overpressure, or personnel consequence. Unsupported scenarios return explicit capability results.

## Near-term critical path

```text
Environment API
 -> Snapshot/Fork/Replay
 -> DEXPI/ProcessGraph bindings
 -> Capability/Safety
```

Once this path is reliable, implementation priority moves to the agent runtime and `tep-agent-lab` rather than adding more simulator features.

## Documentation

Environment:

- [`docs/architecture.md`](docs/architecture.md) — sandbox boundaries
- [`docs/roadmap.md`](docs/roadmap.md) — four-phase environment critical path
- [`docs/specs/`](docs/specs/README.md) — testable v0 contracts
- [`docs/open-questions.md`](docs/open-questions.md) — unresolved environment decisions
- [`docs/runtime-variable-map.md`](docs/runtime-variable-map.md) — temporary runtime mapping reference
- [`docs/dexpi-tep-integration.md`](docs/dexpi-tep-integration.md) — semantic integration design

Program:

- [`docs/ecosystem/program-charter.md`](docs/ecosystem/program-charter.md)
- [`docs/ecosystem/implementation-plan.md`](docs/ecosystem/implementation-plan.md)
- [`docs/ecosystem/development-workflow.md`](docs/ecosystem/development-workflow.md)
- [`docs/ecosystem/decision-register.md`](docs/ecosystem/decision-register.md)
- [`docs/ecosystem/documentation-standard.md`](docs/ecosystem/documentation-standard.md)
- [`docs/ecosystem/README.md`](docs/ecosystem/README.md)

Future-repo scaffolds:

- `docs/ecosystem/blueprints/industrial-agent-runtime/`
- `docs/ecosystem/blueprints/tep-agent-lab/`

Parked P&ID-to-simulation notes remain documentation only and are not part of the active roadmap.

Development-agent instructions live in [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md); those files intentionally stay concise and defer to canonical specs.
