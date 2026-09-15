# Roadmap

This roadmap prioritizes a reproducible control/agent loop before visualization or multi-agent complexity.

## Phase 0 — Lock the simulator contract

**Goal:** know exactly what the vendored simulator does.

Deliverables:

- pin/record upstream submodule commit in run metadata;
- verify pure-Python backend on the target Windows environment;
- confirm `step()`, measurement access, XMV access, disturbance injection, and shutdown behavior;
- add an automated variable-registry consistency test;
- correct local documentation so XMV IDs match the vendored simulator.

Exit criteria:

```text
initialize -> step N times -> read XMEAS/XMV -> inject a disturbance -> reproduce run with same seed
```

No LLM is involved.

## Phase 1 — Deterministic runtime shell

**Goal:** create the plant loop and logging without an agent.

Implement:

- simulator adapter;
- `ObservationSnapshot`;
- run ID + experiment config;
- rolling telemetry window;
- event log;
- deterministic runtime state machine;
- JSONL/SQLite/Parquet persistence (choose one simple path first).

Exit criteria:

- 1-hour simulated run is replayable;
- run metadata and events are persisted;
- no-event path is fast and deterministic.

## Phase 2 — Detector cascade

**Goal:** only escalate meaningful incidents.

Implement in order:

1. hard safety/shutdown detector;
2. sustained deviation/rate-of-change detector;
3. action-no-response detector;
4. optional PCA/statistical/upstream detector plugin.

Exit criteria:

- selected IDV disturbance produces a deterministic `IncidentEvent`;
- healthy baseline does not constantly open incidents;
- detector evidence is numeric and compact.

## Phase 3 — Action gate and deterministic controller

**Goal:** make the intervention path safe before adding an LLM.

Implement:

- canonical variable registry;
- action proposal schema;
- bounds gate;
- max-delta/rate gate;
- actuator cooldown;
- experiment-specific allowlist;
- safe rejection behavior;
- action executor;
- deterministic nominal/recovery policy for at least one fault scenario.

Exit criteria:

- invalid actions never reach `set_mv()`;
- a deterministic recovery policy can use the same gate/executor path;
- `CLOSED_LOOP` and `MANUAL/custom-controller` behavior is covered by tests.

## Phase 4 — Single reasoning agent

**Goal:** add reasoning only where deterministic logic stops.

Implement:

- `Agent` interface independent of model provider;
- compact `IncidentContext` builder;
- structured diagnosis/action output;
- fake agent for tests;
- one real model adapter;
- model call/token/latency metrics.

Default agent flow:

```text
incident -> diagnose -> propose -> deterministic gate -> apply/reject -> verify
```

Exit criteria:

- healthy runs make zero model calls;
- agent receives only incident-relevant context;
- malformed model output causes no action;
- all proposals and gate decisions are traceable.

## Phase 5 — Closed recovery loop

**Goal:** evaluate whether an intervention actually helped.

Implement:

- verification horizon;
- expected direction/recovery criterion;
- action outcome classification;
- bounded retry/re-diagnosis;
- safe-hold transition when retry budget is exhausted.

Suggested first scenario:

```text
IDV(4) reactor cooling-water inlet temperature disturbance
-> reactor temperature/related signals deviate
-> incident opens
-> agent identifies cooling-water path
-> proposes bounded XMV(10) intervention
-> gate validates
-> runtime applies action
-> verification checks temperature/safety trend
```

Do not expose the ground-truth disturbance ID to the agent when measuring diagnosis quality.

Exit criteria:

- full incident trace can be inspected end-to-end;
- outcome is judged by deterministic metrics, not by model self-evaluation.

## Phase 6 — Introduce LangGraph only if needed

**Goal:** add orchestration features, not complexity for its own sake.

Adopt LangGraph when one or more of these are required:

- durable checkpoint/resume;
- human approval before high-risk action;
- explicit multi-step retry graph;
- parallel bounded reasoning branches;
- persistent incident workflow across UI/API requests.

Keep the simulation loop outside the graph.

Suggested graph boundary:

```text
IncidentContext
   -> diagnosis
   -> proposal
   -> [deterministic gate outside/at boundary]
   -> verification decision
   -> retry / close / human review
```

## Phase 7 — Dashboard and process visualization

**Goal:** make the experiment understandable to a human.

Start with a 2D dashboard before Blender/DEXPI.

Views:

- process overview;
- selected XMEAS time series;
- XMV positions;
- active disturbance for experiment/debug mode;
- detector events;
- agent diagnosis/proposal;
- gate decision;
- recovery status;
- token/latency counters.

Then add a process-flow topology where abnormal equipment/streams are highlighted.

Only after the state/event model is stable should DEXPI/Blender be considered.

## Phase 8 — Evaluation matrix

Compare at least:

```text
A. built-in closed-loop control
B. manual mode + deterministic recovery policy
C. manual/custom control + event-driven LLM agent
D. optional LangGraph version of C
```

Metrics:

- recovery success rate;
- time to detect;
- time to recover;
- safety-limit violations / shutdown rate;
- number and magnitude of control actions;
- false incident rate;
- LLM calls per simulated hour;
- input/output tokens per incident;
- model latency per incident;
- malformed/rejected proposal rate;
- reproducibility across seeds.

## What not to build yet

Defer these until Phase 5 works:

- continuous multi-agent chatter;
- Supervisor/DataEngineer/DataScientist role hierarchy;
- full knowledge graph;
- DEXPI authoring pipeline;
- Blender/Omniverse digital twin rendering;
- agent-generated controller code during a live run;
- broad shell/filesystem access from the online agent.

The first success criterion is a small, explainable, replayable closed experiment—not a large agent platform.
