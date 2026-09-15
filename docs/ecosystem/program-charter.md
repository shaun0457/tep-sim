# Program Charter — Industrial Agent Playground

## Purpose

Build a research-grade environment for studying how AI agents investigate, experiment, reason, delegate, validate evidence, and propose engineering actions inside an executable industrial process world.

The program is intentionally **agent-first**. It does not attempt to solve generic P&ID digitization, arbitrary simulator generation, or 3D plant reconstruction.

## Core research question

> Given a process world with explicit topology, dynamic behavior, measurable state, forkable simulation, deterministic engineering constraints, and bounded tools, how effectively can an AI agent behave like an autonomous engineering investigator rather than a static question-answering system?

## Agent role

v0 role:

> **Autonomous Industrial Process Investigator**

The Main Agent may observe, query, form hypotheses, design experiments, use analysis tools, create bounded Dynamic DAGs/subtasks, integrate evidence, and produce recommendations.

Long-term direction:

> **Autonomous Process Engineer**

This may add richer recovery/design/optimization authority only after investigation quality and deterministic governance are proven.

## Three core repositories

### `tep-sim`

Owns environment truth:

- TEP dynamics;
- process semantics / DEXPI-derived ProcessGraph;
- canonical variable registry;
- interventions;
- snapshot/fork/replay;
- capabilities;
- K0 runtime truth and reviewed K1 environment constraints;
- deterministic safety evaluation;
- run provenance.

### `industrial-agent-runtime`

Owns domain-independent agent mechanics:

- Main Agent lifecycle/model interface;
- deterministic Coordinator / Executor / Verifier;
- Hybrid orchestration contracts;
- local ReAct-style loop;
- bounded model-proposed Dynamic DAG validation/execution primitives;
- ephemeral subagents;
- task/tool/budget contracts;
- context/reference handling;
- tracing;
- generic permission/budget/authority gates;
- optional LangGraph adapter without framework leakage into public contracts.

### `tep-agent-lab`

Owns TEP-specific agent research:

- Investigation State;
- hypotheses/evidence/experiments;
- Information Plane adapters;
- K2/K3 Rule Registry;
- Tool Bridge;
- RCA;
- simulation-backed HAZOP;
- recovery planning;
- AutoProcessResearch;
- domain-policy gates;
- benchmark design/identifiability;
- capability/orchestration ablations;
- reports/evaluation.

## Information Plane

The program uses an Information Plane rather than chat history as canonical state.

```text
Agent Runtime / Control Plane
          |
          v
Information Plane
  ProcessGraph
  Variable Registry
  Rule Registry
  Evidence Store
  Experiment Ledger
  Artifact refs
  Investigation State
          |
          v
TEP Simulation / World Plane
```

This is an architectural layer, not a fourth repository.

## Optional existing service

`manufacturing-kg-agent` may provide read-only process/document evidence after no-KG baselines exist.

## Non-goals

The active program does not include:

- OCR/symbol/line extraction from P&ID drawings;
- automatic arbitrary-plant simulator generation;
- production-grade autonomous plant control deployment;
- general fire/explosion/toxic-dispersion consequence modeling;
- 3D digital-twin reconstruction;
- fixed role-based multi-agent organizations;
- unrestricted recursive swarms;
- arbitrary agent Python/shell/package installation as the normal analysis interface;
- a global cross-project learned-memory platform.

## Research task families

1. **RCA** — diagnose incidents using observations, topology, analysis, hypotheses, and discriminating counterfactual experiments.
2. **Simulation-backed HAZOP** — formulate deviations, test simulator-supported scenarios, observe consequences, and produce evidence-backed findings.
3. **Recovery planning** — generate candidate strategies, evaluate them in forks, and propose bounded interventions through deterministic gates.
4. **AutoProcessResearch** — autonomously iterate bounded engineering hypotheses/experiments against a frozen evaluator and mutable search surface.

## Hybrid orchestration principle

```text
Deterministic Macro Control
        |
Main Investigator
  local ReAct for simple work
        |
  Dynamic DAG when useful
        |
deterministic Coordinator / Executor / Verifier
        |
typed tools / Tool Bridge / TEP world
```

The model decides strategy and what evidence/experiment is useful. Deterministic components own validation, budgets, authority, execution semantics, provenance, and machine-checkable verification.

## Knowledge authority

```text
K0 simulator/runtime truth
K1 reviewed formal physical/safety invariant
K2 simulation/experiment-validated engineering relationship
K3 literature/document heuristic
K4 Agent working hypothesis
```

K3/K4 cannot directly become hard gates. Knowledge is promoted only through explicit provenance/review/validation workflows.

## Agent abilities under study

- observation/evidence selection;
- topology reasoning;
- hypothesis generation/ranking;
- experiment design/discrimination;
- Dynamic DAG planning/replanning;
- dynamic subagent allocation;
- analysis-tool selection;
- evidence integration/belief update;
- semantic stopping;
- recovery strategy generation;
- research-loop idea generation;
- numeric-search delegation to optimizers;
- tool/budget/context efficiency;
- uncertainty calibration;
- graceful handling of unsupported capabilities.

## Program invariants

1. Environment truth is deterministic code/data, not prompt memory.
2. Ground truth used by scorers is separated from Agent-visible context/refs.
3. An LLM never receives unrestricted direct reference-world mutation authority.
4. Coordinator/Executor/Verifier are deterministic runtime components by default, not fixed LLM roles.
5. Subagents are ephemeral task workers, not permanent organizational identities.
6. Dynamic DAGs are model proposals until deterministic validation.
7. Conversation transcripts are not canonical Investigation State.
8. Paper/LLM-extracted knowledge cannot directly create a hard gate.
9. Every model call, plan revision, subagent, tool call, gate, experiment, and artifact is traceable.
10. Healthy/no-incident environment execution can run without an LLM.
11. Unsupported physics must be explicit rather than hallucinated.
12. Numeric optimization should use deterministic search/optimizer tools when appropriate rather than repeated LLM value guessing.

## Success criteria for v1

A v1 program exists when a reproducible TEP incident can be:

```text
created -> observed
-> represented in typed Investigation State
-> investigated through Hybrid orchestration
-> analyzed with ProcessGraph/rules/tools
-> branched into discriminating counterfactual experiments
-> diagnosed with evidence
-> recovery candidates simulated/ranked
-> proposals gated
-> result scored against hidden truth
-> complete trace/state/artifacts/report saved
```

The same core benchmark must support at least:

- deterministic/no-agent baseline;
- static/one-shot LLM baseline;
- ReAct-style Main Agent;
- Hybrid Main Agent + deterministic macro runtime;
- Hybrid + counterfactual simulation;
- Hybrid + Dynamic DAG;
- bounded-subagent ablation.

AutoProcessResearch becomes a v1.x research mode after recovery scoring/tooling is stable.

## Development policy

Implementation is frozen until the Phase 0 architecture/spec consistency review in `implementation-plan.md` is complete.

After freeze, multiple coding agents may work in parallel only through spec-scoped branches/worktrees and explicit dependency DAGs described in `development-agent-orchestration.md`.

## Parked research

Generic `pid2sim`, P&ID computer vision, arbitrary plant model generation, and 3D reconstruction remain future ideas and are not on the critical path.
