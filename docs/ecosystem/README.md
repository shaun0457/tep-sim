# Industrial Simulation + Agent Ecosystem

This program is centered on **AI agents operating inside a trustworthy industrial sandbox**. Generic P&ID digitization and automatic simulator generation are not current core goals.

## Core program

Use three core repositories:

```text
1. Environment       -> tep-sim
2. Agent runtime     -> industrial-agent-runtime
3. Integration/eval  -> tep-agent-lab
```

Existing knowledge projects may be connected as optional services.

## 1. `tep-sim` — process playground

Purpose: trustworthy, reproducible Tennessee Eastman Process environment.

Owns:

- TEP simulator adapter;
- canonical XMEAS/XMV/IDV registry;
- reset/observe/step/rollout;
- snapshot/fork/replay;
- typed disturbances/interventions;
- machine-readable capability and deterministic safety evaluation;
- machine-readable TEP topology/process semantics;
- DEXPI/process-data adapter and entity-to-runtime binding registry;
- numeric run artifacts/provenance.

For TEP, start from machine-readable DEXPI/process data. Do **not** build OCR/P&ID-recognition or generic simulator generation.

```text
DEXPI / ProcessGraph = static structure + engineering semantics
TEP simulator        = dynamic process behavior
binding registry     = semantic entity <-> XMEAS/XMV/IDV
```

Does not own LLMs, prompts, LangGraph, subagents, RCA/HAZOP reasoning, or recovery strategy selection.

## 2. `industrial-agent-runtime` — generic reasoning harness

Purpose: domain-independent main-agent runtime with bounded ephemeral subagents and deterministic authority gates.

Owns:

- main-agent lifecycle;
- task/budget/tool/result contracts;
- model-provider abstraction;
- bounded subtask/subagent execution;
- context-reference discipline;
- generic schema/permission/budget/side-effect gates;
- consumer validator hook;
- tracing/token/latency accounting;
- optional later checkpoint/approval adapter.

Does not own TEP equations/topology/safety truth, DEXPI parsing, HAZOP mappings, RCA workflows, or benchmark ground truth.

## 3. `tep-agent-lab` — integration and benchmark lab

Purpose: study what agents can do inside the TEP process world.

Owns:

- TEP-specific agent tool adapters;
- domain experiment/recovery policies;
- RCA experiments;
- simulation-backed HAZOP experiments;
- recovery/counterfactual experiments;
- scenario fixtures and hidden truth;
- evaluation/ablation/scoring;
- agent/subagent behavior traces and reports.

This is the only core repo that intentionally knows both generic agent-runtime semantics and TEP domain semantics.

## Existing repositories to reuse

### `manufacturing-kg-agent`

Keep independent. It may later provide read-only process/document evidence after clean no-KG baselines exist.

### `personal-agent-os`

Keep independent. It solves a different problem: personal orchestration, memory, email workflows, and persistent knowledge management.

## Parked research — generic P&ID -> simulator

Generic `pid2sim` is **not a current core project**. The single research note [`pid-to-sim-automation.md`](pid-to-sim-automation.md) is retained for future reference, but no `pid2sim` repository scaffold or implementation milestone is maintained in the active branch.

For the present TEP program, avoid raster P&ID OCR, YOLO/U-Net symbol pipelines, generic CAD/P&ID digitization, automatic arbitrary-plant simulator generation, and 3D reconstruction.

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
- optional knowledge services do not become hidden core dependencies.

## Critical path to first meaningful result

```text
tep-sim:
  Environment API -> Snapshot/Fork -> DEXPI bindings

industrial-agent-runtime (parallel):
  Contracts/Executor -> Deterministic Gates

then:
  tep-agent-lab Tool Surface -> blind RCA benchmark
```

Subagents are added as an ablation **after** a single-agent + counterfactual baseline exists. HAZOP and recovery follow RCA; they should not delay the first end-to-end agent investigation.

## Documentation map

Program-level:

- [`program-charter.md`](program-charter.md) — purpose, research scope, invariants
- [`documentation-standard.md`](documentation-standard.md) — README/spec/ADR/open-question rules
- [`development-workflow.md`](development-workflow.md) — branch/PR/spec-first workflow
- [`implementation-plan.md`](implementation-plan.md) — cross-repo phases and initial branches
- [`decision-register.md`](decision-register.md) — current accepted/proposed decisions

Environment:

- [`../architecture.md`](../architecture.md)
- [`../roadmap.md`](../roadmap.md)
- [`../specs/`](../specs/README.md)
- [`../dexpi-tep-integration.md`](../dexpi-tep-integration.md)
- [`../open-questions.md`](../open-questions.md)

Future-repo scaffolds:

- `blueprints/industrial-agent-runtime/`
- `blueprints/tep-agent-lab/`

## What not to build now

Do not spend core-project effort on:

- raster P&ID OCR;
- generic simulator generation;
- photorealistic 3D plant reconstruction;
- a separate HAZOP ontology repo;
- a separate visualization repo;
- permanent role-based Supervisor/MachineExpert/DataEngineer/DataScientist agents;
- persistent recursive swarms or global agent memory before simple baselines are measured.
