# Industrial Simulation + Agent Ecosystem

This document defines repository boundaries for the broader research/program around process simulation, autonomous agents, HAZOP/RCA experiments, and automated model generation.

## Core principle

Do not organize repositories by today's demo. Organize them by **stable responsibility**.

The program has four core responsibilities:

```text
1. Environment       -> tep-sim
2. Agent runtime     -> industrial-agent-runtime
3. Integration/eval  -> tep-agent-lab
4. Model generation  -> pid2sim
```

Existing knowledge projects may be connected as optional services rather than merged into these cores.

---

## Repository map

### 1. `tep-sim` — process playground

**Purpose:** trustworthy, reproducible Tennessee Eastman Process environment.

Owns:

- TEP simulator adapter;
- canonical variable registry;
- reset/observe/step/rollout;
- snapshot/fork/replay;
- interventions/disturbances;
- capability discovery;
- deterministic safety evaluation;
- scenario compilation for supported TEP semantics;
- numeric run artifacts;
- read-only visualization adapters.

Does not own:

- LLMs;
- LangGraph;
- prompts or memory;
- HAZOP/RCA reasoning;
- P&ID digitization;
- generic simulator generation.

### 2. `industrial-agent-runtime` — generic reasoning harness

**Purpose:** domain-independent main-agent runtime that may create bounded ephemeral subagents and use external environments through tools.

Owns:

- main-agent lifecycle;
- dynamic subagent spawning;
- task/budget/tool contracts;
- model-provider abstraction;
- context construction and compression;
- structured outputs;
- tool permissions;
- deterministic gates around agent side effects;
- tracing and token/latency accounting;
- optional LangGraph orchestration for stateful slow paths.

Does not own:

- TEP variable knowledge;
- TEP equations;
- P&ID parsing;
- HAZOP scenario mappings;
- environment-specific safety truth.

### 3. `tep-agent-lab` — integration and benchmark lab

**Purpose:** combine `tep-sim` and `industrial-agent-runtime` to evaluate agent behavior on realistic process-engineering tasks.

Owns:

- TEP-specific agent tools/adapters;
- HAZOP workflows;
- RCA workflows;
- recovery/mitigation experiments;
- counterfactual experiment policies;
- experiment configs;
- benchmark scenario packs;
- evaluation metrics;
- run reports comparing deterministic and agent-assisted methods.

This is the only core repo that knows both:

```text
agent runtime semantics
AND
TEP process semantics
```

### 4. `pid2sim` — engineering model generation

**Purpose:** research and prototype the pipeline from P&ID/engineering data to a machine-readable process graph and ultimately an executable simulation model.

Owns:

- P&ID ingestion;
- raster/vector/CAD extraction adapters;
- symbol/text/line/tag recognition;
- connectivity reconstruction;
- DEXPI normalization/version adapters;
- graph validation;
- model enrichment requirements;
- simulation-component mapping;
- simulation code/model generation;
- human-in-the-loop review;
- generated-model validation.

Does not own agent runtime or TEP-specific experiments.

---

## Existing repositories to reuse

### `manufacturing-kg-agent`

Keep this independent. It can later expose **read-only process/document evidence** to `tep-agent-lab` or the generic agent runtime.

Potential role:

```text
manuals / SOP / papers / specs
          |
          v
manufacturing-kg-agent
          |
     evidence API
          |
          v
tep-agent-lab
```

Do not move TEP simulator physics into the KG repo and do not move generic KG ingestion into `tep-sim`.

### `personal-agent-os`

Keep this independent. It solves a different problem: personal orchestration, dynamic hiring/retiring, memory, email interface, and persistent knowledge workflows.

Patterns may be reused conceptually, but the industrial runtime should have a much narrower tool and safety surface.

---

## Dependency direction

```text
                      manufacturing-kg-agent
                              ^
                              | optional evidence
                              |
industrial-agent-runtime ---> tep-agent-lab <--- tep-sim
                                  ^
                                  |
                                  | optional generated environments/models
                                  |
                                pid2sim
```

Hard dependency rules:

- `tep-sim` depends on none of the other project repos.
- `industrial-agent-runtime` depends on none of the domain repos.
- `tep-agent-lab` depends on released/pinned versions of `tep-sim` and `industrial-agent-runtime`.
- `pid2sim` may use `tep-sim` only as a benchmark/ground-truth target, not as its internal architecture.
- knowledge services are optional integrations.

---

## Why four repos instead of one monorepo?

The separation reduces:

- `AGENTS.md` / `CLAUDE.md` context pollution;
- dependency conflicts;
- accidental LLM code inside deterministic simulation;
- domain leakage into generic agent infrastructure;
- testing scope;
- cognitive load for coding agents and humans.

It also enables independent versioning:

```text
tep-sim v0.2
industrial-agent-runtime v0.1
tep-agent-lab experiment config pins both
```

---

## What not to split yet

Do **not** create extra repositories yet for:

- shared contracts;
- dashboards;
- model-provider wrappers;
- HAZOP ontology;
- TEP topology;
- evaluation utilities.

Keep those inside their owning core repo until at least two independent consumers prove a shared package is necessary.

---

## Recommended research sequence

### Track A — Trusted playground first

1. finish `tep-sim` environment adapter;
2. snapshot/fork/replay;
3. capability registry;
4. TEP scenario compiler;
5. deterministic safety evaluation.

### Track B — Agent runtime second

1. main-agent contract;
2. bounded ephemeral subagents;
3. tool and budget contracts;
4. structured outputs;
5. tracing/eval hooks;
6. optional LangGraph only when durable state/interrupts/retries justify it.

### Track C — Integration lab third

1. observation/query tools;
2. counterfactual simulation tool;
3. RCA benchmark;
4. simulation-backed HAZOP benchmark;
5. recovery/mitigation benchmark;
6. deterministic-vs-agent comparison.

### Track D — P&ID-to-simulation as independent long-horizon project

1. start from machine-readable DEXPI reference data;
2. normalize to internal graph;
3. compile graph to a low-fidelity executable model;
4. validate topology and qualitative behavior;
5. only then add raster/vector P&ID digitization;
6. use TEP as a round-trip benchmark where known process knowledge and simulation behavior provide ground truth.

---

## Repository scaffolds

Drafts for the future repositories live under `docs/ecosystem/blueprints/` on this architecture branch. They are temporary migration material and should be moved to the new repositories once those repositories are created.
