# Industrial Simulation + Agent Ecosystem

This program is centered on **AI agents operating inside a trustworthy industrial sandbox**. Generic P&ID digitization, arbitrary simulator generation, and 3D reconstruction are not current core goals.

## Core program

Use three core repositories:

```text
1. Environment / World Plane        -> tep-sim
2. Agent Runtime / Control Plane    -> industrial-agent-runtime
3. Integration / Information / Lab -> tep-agent-lab
```

Existing knowledge projects remain optional services.

## Program architecture

```text
                     Hybrid Agent Runtime
                     CONTROL PLANE
          Main Agent + deterministic Coordinator
             Executor + Verifier + gates
                         |
                         v
                    Information Plane
        ProcessGraph / Variable Registry / Rules
       Evidence / Experiments / Investigation State
                         |
                         v
                       tep-sim
                     WORLD PLANE
```

The Information Plane is an architectural layer across existing repositories, not a fourth repo.

## 1. `tep-sim` — process world

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
- K0 simulator/runtime truth and reviewed K1 environment constraints;
- numeric run artifacts/provenance.

For TEP, start from machine-readable DEXPI/process data. Do **not** build OCR/P&ID-recognition or generic simulator generation.

```text
DEXPI / ProcessGraph = static structure + engineering semantics
TEP simulator        = dynamic process behavior
binding registry     = semantic entity <-> XMEAS/XMV/IDV
```

Does not own LLMs, Agent orchestration, Dynamic DAGs, RCA/HAZOP reasoning, or recovery strategy selection.

## 2. `industrial-agent-runtime` — Hybrid control plane

Purpose: domain-independent goal-driven Agent runtime with deterministic execution authority.

Owns:

- Main Agent lifecycle/model interface;
- deterministic Coordinator / Executor / Verifier;
- local ReAct-style reasoning loop;
- bounded model-proposed Dynamic DAG validation/scheduling;
- task/budget/tool/result contracts;
- ephemeral subtask/subagent execution;
- context/reference discipline;
- generic schema/permission/budget/side-effect/plan gates;
- tracing/token/latency accounting;
- framework-neutral checkpoint/approval interfaces;
- optional LangGraph adapter.

Does not own TEP equations/topology/safety truth, Rule Registry domain content, DEXPI parsing, RCA/HAZOP/recovery workflows, or benchmark ground truth.

## 3. `tep-agent-lab` — information/research/benchmark lab

Purpose: study what agents can do inside the TEP process world.

Owns:

- typed Investigation State;
- hypotheses/evidence/experiment contracts;
- Evidence Store / Experiment Ledger;
- K2 simulation-validated rules and K3 literature heuristics;
- TEP-specific environment tools;
- Tool Bridge adapters to allowlisted scientific/open-source libraries;
- domain experiment/recovery policies;
- RCA experiments;
- simulation-backed HAZOP;
- recovery/counterfactual experiments;
- AutoProcessResearch;
- benchmark scenario families/identifiability/leakage controls;
- capability + orchestration ablations;
- scientific-behavior evaluation and reports.

This is the only core repo that intentionally knows both generic Agent Runtime semantics and TEP domain semantics.

## Knowledge authority

```text
K0 simulator/runtime truth             -> tep-sim
K1 reviewed physical/safety invariant  -> tep-sim / reviewed policy
K2 validated engineering relationship  -> tep-agent-lab
K3 paper/document heuristic            -> tep-agent-lab
K4 Agent working hypothesis            -> Investigation State only
```

K3/K4 cannot directly create hard gates.

## Tool Bridge principle

Reuse mature libraries through narrow typed adapters rather than reimplementing standard analysis or giving the Agent arbitrary Python/shell access.

Candidate capabilities include:

- upstream TEP detectors;
- signal correlation/lag/response features;
- PCA/PLS baselines;
- graph algorithms;
- sensitivity analysis;
- bounded numerical optimization.

The Agent decides **which analysis/research question to ask**; deterministic tools perform the computation and return versioned evidence.

## AutoProcessResearch

A separate lab mode adapts the AutoResearch pattern:

```text
frozen evaluator + bounded mutable surface
 -> baseline
 -> Agent hypothesis/change
 -> deterministic experiment/search
 -> score
 -> append ledger
 -> keep/reject/neutral
 -> repeat until deterministic stop
 -> hidden evaluation
```

It does not let the Agent modify TEP physics, evaluator code, safety policy, or its own authority.

## Existing repositories to reuse

### `manufacturing-kg-agent`

Keep independent. It may later provide read-only process/document evidence after clean no-KG baselines exist. Extracted relationships enter as K3 candidates until validated.

### `personal-agent-os`

Keep independent. It solves personal orchestration/memory/email workflows rather than the narrow industrial control/research runtime.

## Parked research — generic P&ID -> simulator

Generic `pid2sim` is **not a current core project**. The research note [`pid-to-sim-automation.md`](pid-to-sim-automation.md) is retained only for future reference.

## Dependency direction

```text
                      manufacturing-kg-agent
                              ^
                              | optional evidence
                              |
industrial-agent-runtime ---> tep-agent-lab <--- tep-sim
```

Rules:

- `tep-sim` has no dependency on Agent repos.
- `industrial-agent-runtime` has no dependency on TEP/domain repos.
- `tep-agent-lab` pins versions/revisions of both.
- optional knowledge/tool libraries stay behind adapters and do not become hidden architecture dependencies.

## Phase 0 before implementation

Core implementation is frozen until the architecture/spec consistency review in [`implementation-plan.md`](implementation-plan.md) is complete.

Phase 0 covers:

- Hybrid orchestration;
- Information Plane;
- Investigation State;
- K0–K4 Rule Registry;
- Hypothesis/Experiment contracts;
- Tool Bridge;
- benchmark/evaluation design;
- AutoProcessResearch contract.

After freeze, independent implementation branches may run in parallel under [`development-agent-orchestration.md`](development-agent-orchestration.md).

## Research sequence after freeze

```text
trusted TEP world
 -> Hybrid runtime / gates
 -> Investigation State + information contracts
 -> environment + analysis Tool Bridge
 -> blind RCA baseline
 -> orchestration ablation
 -> HAZOP / recovery
 -> AutoProcessResearch
 -> optional KG evidence / broader scenarios
```

## Documentation map

Program-level:

- [`program-charter.md`](program-charter.md) — purpose, role, architecture invariants
- [`information-plane.md`](information-plane.md) — shared information/reference architecture
- [`documentation-standard.md`](documentation-standard.md) — README/spec/ADR/open-question rules
- [`development-workflow.md`](development-workflow.md) — branch/PR/spec-first workflow
- [`development-agent-orchestration.md`](development-agent-orchestration.md) — parallel coding-agent policy
- [`implementation-plan.md`](implementation-plan.md) — Design Freeze + cross-repo phases
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
- permanent role-based Supervisor/MachineExpert/DataEngineer/DataScientist Agent organizations;
- unrestricted recursive swarms;
- persistent global learned memory before simple baselines are measured;
- arbitrary Agent Python/shell/package installation as normal Tool Bridge behavior.
