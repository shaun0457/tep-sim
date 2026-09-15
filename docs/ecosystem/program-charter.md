# Program Charter — Industrial Agent Playground

## Purpose

Build a research-grade environment for studying how AI agents investigate, experiment, reason, and propose actions inside an executable industrial process world.

The program is intentionally **agent-first**. It does not attempt to solve generic P&ID digitization, arbitrary simulator generation, or 3D plant reconstruction.

## Core research question

> Given a process world with explicit topology, dynamic behavior, measurable state, forkable simulation, and bounded tools, how effectively can an AI agent behave like an engineering investigator rather than a static question-answering system?

## Three core repositories

### `tep-sim`
Owns environment truth: TEP dynamics, process semantics, DEXPI/process graph, bindings, interventions, snapshot/fork/replay, deterministic safety/capability evaluation, and run provenance.

### `industrial-agent-runtime`
Owns domain-independent agent mechanics: main-agent lifecycle, ephemeral subagents, task/tool/budget contracts, model-provider abstraction, context discipline, tracing, and generic deterministic permission/budget gates.

### `tep-agent-lab`
Owns TEP-specific integration and experiments: topology/telemetry tools, scenario adapters, RCA, simulation-backed HAZOP, recovery experiments, domain-policy gates, benchmarks, ablations, and reports.

## Optional existing service

`manufacturing-kg-agent` may provide read-only process/document evidence. It is not required for the first milestones.

## Non-goals

The active program does not include:

- OCR/symbol/line extraction from P&ID drawings;
- automatic arbitrary-plant simulator generation;
- production-grade process control deployment;
- general fire/explosion/toxic-dispersion consequence modeling;
- 3D digital-twin reconstruction;
- fixed role-based multi-agent organizations;
- a global cross-project memory platform.

## Research tasks

The first three task families are:

1. **RCA** — diagnose an incident using observations, topology, history, and discriminating counterfactual experiments.
2. **Simulation-backed HAZOP** — formulate process deviations, test only simulator-supported scenarios, observe consequences, and produce evidence-backed findings.
3. **Recovery planning** — generate candidate strategies, evaluate them in forks, and propose a bounded intervention through deterministic policy/safety gates.

## Agent abilities under study

- observation selection;
- topology reasoning;
- hypothesis generation;
- experiment design;
- dynamic subagent allocation;
- evidence integration;
- recovery strategy generation;
- tool-budget efficiency;
- uncertainty calibration;
- graceful handling of unsupported environment capabilities.

## Program invariants

1. Environment truth is deterministic code/data, not prompt memory.
2. Ground truth used by scorers is separated from agent-visible context.
3. An LLM never receives unrestricted direct mutation authority.
4. Subagents are ephemeral task workers, not permanent organizational roles.
5. Every model call, subagent spawn, tool call, gate decision, and experiment is traceable.
6. Healthy/no-incident execution can run without an LLM.
7. Unsupported physics must be surfaced explicitly rather than hallucinated.

## Success criteria for v1

A v1 program exists when one reproducible TEP incident can be:

```text
created -> detected/observed -> investigated by an agent
-> branched into counterfactual experiments -> diagnosed
-> recovery candidates simulated -> proposal gated
-> result scored against hidden ground truth -> complete trace/report saved
```

The same experiment must be runnable with at least:

- deterministic/no-agent baseline;
- single-agent baseline;
- main agent + counterfactual tools;
- main agent + bounded subagents.

## Parked research

Generic `pid2sim`, P&ID computer vision, arbitrary plant model generation, and 3D reconstruction are retained only as future ideas. They must not appear on the critical path of the current agent research program.
