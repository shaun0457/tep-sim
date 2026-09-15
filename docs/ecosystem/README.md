# Industrial Simulation + Agent Ecosystem

This program is intentionally centered on **AI agents operating inside a trustworthy industrial sandbox**. Generic P&ID digitization and automatic simulator generation are not core goals.

## Core program

Use three core repositories:

```text
1. Environment       -> tep-sim
2. Agent runtime     -> industrial-agent-runtime
3. Integration/eval  -> tep-agent-lab
```

Existing knowledge projects may be connected as optional services.

---

## 1. `tep-sim` — process playground

**Purpose:** trustworthy, reproducible Tennessee Eastman Process environment.

Owns:

- TEP simulator adapter;
- canonical XMEAS/XMV/IDV registry;
- reset / observe / step / rollout;
- snapshot / fork / replay;
- typed disturbances and interventions;
- deterministic safety evaluation;
- capability discovery;
- a machine-readable TEP process/topology representation;
- DEXPI Process import/adapter for TEP;
- numeric run artifacts;
- read-only visualization adapters.

For TEP, do **not** build an OCR/P&ID-recognition pipeline. Use an existing machine-readable DEXPI representation (or a curated DEXPI 2.0 TEP representation) as the static engineering-semantic layer, while the existing TEP simulator remains the dynamic/physics layer.

Conceptually:

```text
DEXPI / process graph   = what the plant is and how it is connected
TEP simulator           = how the plant evolves dynamically
tep-sim adapter         = binds graph entities to XMEAS/XMV/IDV/state
```

Does not own:

- LLM providers;
- LangGraph;
- prompts or agent memory;
- dynamic subagents;
- HAZOP/RCA reasoning;
- P&ID OCR;
- generic P&ID-to-simulation generation.

---

## 2. `industrial-agent-runtime` — generic reasoning harness

**Purpose:** domain-independent main-agent runtime that may create bounded, ephemeral subagents and use external environments through tools.

Owns:

- main-agent lifecycle;
- dynamic subagent spawning;
- task/budget/tool contracts;
- model-provider abstraction;
- context construction/compression;
- structured outputs;
- tool permissions;
- deterministic gates around side effects;
- tracing and token/latency accounting;
- optional LangGraph orchestration for stateful slow paths.

Does not own TEP equations, XMEAS/XMV mappings, DEXPI semantics, HAZOP mappings, or environment-specific safety truth.

---

## 3. `tep-agent-lab` — integration and benchmark lab

**Purpose:** combine `tep-sim` and `industrial-agent-runtime` to study what agents can do inside a process-engineering playground.

Owns:

- TEP-specific agent tools/adapters;
- RCA experiments;
- simulation-backed HAZOP experiments;
- recovery/mitigation experiments;
- counterfactual simulation policies;
- experiment configs and benchmark packs;
- evaluation metrics;
- deterministic-vs-agent comparisons;
- agent/subagent behavior traces;
- visualization of agent investigations and experiment branches.

This is the only core repo that intentionally knows both agent-runtime semantics and TEP process semantics.

---

## Existing repositories to reuse

### `manufacturing-kg-agent`

Keep independent. It may later provide read-only process/document evidence to `tep-agent-lab`.

### `personal-agent-os`

Keep independent. It solves a different problem: personal orchestration, memory, email workflows, and persistent knowledge management.

---

## Parked research: generic P&ID -> simulator (`pid2sim`)

This is **not a current core project**.

The problem is valuable but large enough to become a standalone product/research program: drawing recognition, symbol/text/line extraction, connectivity reconstruction, DEXPI normalization, component-model mapping, missing engineering parameter resolution, validation, and model generation.

For the present TEP program, avoid that scope completely. Start from machine-readable DEXPI/process data.

The existing `docs/ecosystem/pid-to-sim-automation.md` and `blueprints/pid2sim/` are retained only as parking-lot research notes and should not drive near-term implementation.

---

## Dependency direction

```text
                      manufacturing-kg-agent
                              ^
                              | optional evidence
                              |
industrial-agent-runtime ---> tep-agent-lab <--- tep-sim
```

Rules:

- `tep-sim` has no dependency on agent repos.
- `industrial-agent-runtime` has no dependency on TEP/domain repos.
- `tep-agent-lab` pins versions/revisions of both.
- knowledge services remain optional.

---

## Near-term research sequence

### Track A — build the trusted world

1. TEP environment adapter;
2. reproducible snapshot/fork/replay;
3. capability registry;
4. DEXPI/process-graph adapter for TEP;
5. entity-to-XMEAS/XMV/IDV mapping;
6. deterministic safety evaluation;
7. lightweight 2D topology/process visualization.

### Track B — build the agent runtime

1. main-agent contract;
2. bounded ephemeral subagents;
3. tool/budget/context contracts;
4. structured outputs;
5. tracing/eval hooks;
6. optional LangGraph only when durable state, interrupts, or explicit retries justify it.

### Track C — study agent behavior in the playground

1. observation/query tools;
2. process-topology query tool;
3. counterfactual simulation tool;
4. RCA benchmark;
5. simulation-backed HAZOP benchmark;
6. recovery-strategy benchmark;
7. compare autonomous investigation policies, subagent usage, token cost, latency, safety, and task success.

---

## What not to build now

Do not spend core-project effort on:

- raster P&ID OCR;
- YOLO/U-Net symbol pipelines;
- generic CAD/P&ID digitization;
- automatic arbitrary-plant simulator generation;
- photorealistic 3D plant reconstruction;
- a new HAZOP ontology repo;
- a separate visualization repo.

Use DEXPI/process topology as a ready engineering representation and spend the research budget on agent behavior.
