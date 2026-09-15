# AGENTS.md

Repository-wide instructions for coding agents.

## Product intent

`tep-sim` is an **agent-agnostic Tennessee Eastman Process simulation sandbox**.

This repository models the environment. It does not implement an LLM agent runtime.

## Hard boundaries

1. **Do not add LLM or agent-framework dependencies here.** No LangGraph, provider SDK, prompt framework, agent memory, or dynamic subagent orchestration belongs in this repo.
2. **Do not implement HAZOP/RCA reasoning here.** The environment may expose the data and experiment primitives those workflows need, but the reasoning workflow lives elsewhere.
3. **Do not implement P&ID image digitization or generic P&ID-to-simulation generation here.** That is a separate side project.
4. **Preserve deterministic reproducibility.** Every run must be attributable to seed, simulator version, configuration, intervention schedule, and run ID.
5. **Use typed environment APIs.** Callers should request observations, snapshots, forks, interventions, rollouts, or evaluations through explicit schemas rather than mutate simulator internals.
6. **Fail explicitly for unsupported physics.** Never approximate an unsupported hazard by inventing behavior. Return a capability/unsupported-scenario error.
7. **Keep runtime metadata canonical.** XMEAS/XMV/IDV identities come from the vendored simulator or generated registry, not duplicated prompt/document memory.
8. **Make side effects auditable.** Record reset, intervention, fork, rollout, termination, and safety events.
9. **Prefer small stable public interfaces.** Internal upstream details may change; callers should depend on `tep-sim` contracts.
10. **Visualization is downstream.** UI/3D/dashboard consumers may read state and replay traces; they must not become a hidden mutation path.

## Target modules

Keep responsibilities separated:

- `simulation`: adapter around upstream `TEPSimulator`
- `registry`: canonical XMEAS/XMV/IDV metadata and units
- `contracts`: typed observation/intervention/scenario/result schemas
- `telemetry`: rolling history, downsampling, feature-ready traces
- `snapshot`: snapshot/fork/replay semantics
- `scenario`: compile environment-neutral scenario requests to TEP-supported interventions
- `safety`: deterministic safety limits, shutdown state, margins
- `persistence`: run metadata, traces, scenario/result artifacts
- `ui`: read-only dashboard/visualization adapters

## Required public capabilities

The environment should eventually support:

```text
reset(seed, config)
observe()
capabilities()
snapshot()
fork(snapshot)
inject(intervention)
step(n)
rollout(horizon)
evaluate_safety(result)
replay(run_id)
```

Do not expose an API merely because the upstream simulator has a method; expose it when the semantic contract is clear and testable.

## HAZOP-facing contract

The sandbox may accept typed process deviations, for example:

```text
Deviation(
  node="reactor_cooling_loop",
  parameter="flow",
  guide_word="LESS",
  magnitude=0.20
)
```

A deterministic scenario compiler may map a supported deviation to one or more TEP interventions. The environment does **not** decide whether the deviation is a credible HAZOP finding; it only reports whether and how it can be simulated.

## Capability discipline

Examples of currently plausible TEP capabilities:

- feed-flow/composition/temperature disturbances;
- cooling-water disturbances;
- valve sticking represented by available IDVs;
- reaction-kinetics variation represented by available IDVs;
- bounded XMV interventions;
- process-variable propagation and shutdown behavior.

Examples that require extra physics and must not be fabricated:

- pipe rupture/leak mass release;
- atmospheric dispersion;
- ignition/fire;
- explosion/blast;
- detailed relief-device sizing;
- personnel consequence modeling.

## Testing expectations

When implementing a feature:

1. inspect upstream behavior before duplicating it;
2. add deterministic tests first where practical;
3. test same-seed replay;
4. test snapshot/fork isolation;
5. test registry consistency against upstream;
6. test unsupported-scenario failure behavior;
7. test that result artifacts include enough metadata to reproduce the run.

## Development-agent usage

Codex CLI, Claude Code, or similar tools may inspect/edit/test this repository as development assistants. They are not part of the runtime architecture.

Keep this file concise. Domain reasoning, agent prompts, model-provider rules, and experiment-specific instructions belong in their own repositories so coding-agent context does not accumulate unrelated concerns.

## Known simulator constraint

For direct MV intervention, use `ControlMode.MANUAL` or an appropriate custom controller. In `CLOSED_LOOP`, the upstream PI controller can overwrite manual MV changes on the next step.
