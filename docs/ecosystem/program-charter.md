# Program Charter — Industrial Agent Playground

## Purpose

Build a research-grade environment for studying how AI agents investigate, experiment, reason, delegate bounded work, validate evidence, and propose engineering actions inside an executable industrial process world.

The program is intentionally **agent-first**. It does not attempt to solve generic P&ID digitization, arbitrary simulator generation, or 3D plant reconstruction.

## Core research question

> Given a process world with explicit topology, dynamic behavior, measurable state, forkable simulation, deterministic engineering constraints, and bounded tools, how effectively can an AI agent behave like an autonomous engineering investigator rather than a static question-answering system?

## Agent role

v0 role:

> **Autonomous Industrial Process Investigator**

The Main Agent may observe, query, form hypotheses, make typed predictions, design experiments, use analysis tools, propose dependency-aware work, delegate bounded subtasks, integrate evidence, and produce structured conclusions/recommendations.

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
- environment capabilities;
- authoritative simulator/runtime constraints;
- deterministic safety/capability evaluation;
- run provenance.

### `industrial-agent-runtime`

Owns domain-independent control-plane contracts:

- Main Agent model/provider interface;
- deterministic Coordinator/control loop;
- explicit ModelTurn/ModelStateUpdateProposal routing;
- pre-execution gates;
- deterministic Executor/dispatcher;
- post-execution result verifier;
- Task/Budget/ToolSpec/ToolResult;
- InformationRef/ContextProjection/TaskStateStore;
- dependency-aware WorkBatch;
- ephemeral subagents/SubtaskResult;
- tracing/resource accounting;
- generic permission/side-effect/authority policy.

It does **not** require LangGraph, MCP, TEP, or a full Dynamic DAG engine in v0.

### `tep-agent-lab`

Owns TEP-specific agent research:

- RcaState + domain ContextProjection;
- ObservationRecord / EvidenceLink;
- hypotheses / typed Predictions / experiments;
- lab Rule/policy metadata;
- Tool Bridge adapters;
- structured Engineering Records;
- RCA;
- later simulation-backed HAZOP;
- later recovery planning;
- later AutoProcessResearch;
- benchmark design/identifiability;
- capability/orchestration ablations;
- reports/evaluation.

## Application / Playground Plane

The program also has a logical **Application / Playground Plane** outside the three core ownership layers:

```text
User / Researcher
       |
       v
Playground Application Plane
run lifecycle / manifest / canonical context / read projections / artifacts
       |
       v
industrial-agent-runtime
       |
       v
tep-agent-lab
       |
       v
tep-sim
```

This plane is **not a fourth core repository in v0**. Its first implementation belongs in `tep-agent-lab` because it assembles runtime + lab + world components for a TEP playground run.

The Application/UI API and the Agent Tool Surface are distinct authority surfaces. UI/backend calls do not grant the Agent execution authority and must not bypass:

```text
ToolSpec -> deterministic gates -> consumer validation -> Executor -> post-execution verification
```

Application `RunStatus` describes hosting lifecycle and is distinct from runtime/consumer `TaskStatus`.

Blind-playground read projections expose only Agent-visible information by default. Evaluator/debug projections are explicit trusted views and must never silently enter Agent context or tool results.

## Information Plane

The program uses a logical Information Plane rather than chat history as canonical state.

```text
Agent Runtime / Control Plane
          |
          v
Information Plane
  ProcessGraph / Variable Registry
  Rule metadata
  append-only RunLog + typed views
  Artifact refs
  consumer TaskStateStore
  Engineering Records
          |
          v
TEP Simulation / World Plane
```

This is an ownership/reference/provenance architecture layer, not a fourth repository and not five mandatory database services.

## Canonical long-term context

Durable engineering/research truth is version-controlled in repository-owned sources and materialized locally at exact revisions for reproducible runs.

Examples include:

- ProcessGraph and variable metadata;
- reviewed entity/runtime bindings;
- safety limits and capability/scenario mappings;
- reviewed engineering rules/provenance;
- benchmark manifests and visibility/scoring policy;
- evaluator ground-truth records.

The local checkout is a **persistent context substrate**, not the model context itself:

```text
Repository-controlled canonical source
        |
        | exact revision / local checkout
        v
CanonicalContextRegistry
        |
 visibility + governance + provenance
        |
        v
bounded ContextProjection
        |
        v
Agent
```

Local availability does not imply Agent visibility. Evaluator-only records may be materialized on the same machine while remaining inaccessible to Agent projections/tools.

The canonical-context source inventory used by a run is trusted application/harness state, frozen when the run becomes READY, and is not model-authored mutable investigation state.

Run-specific mutable state is not promoted to Git-backed canonical knowledge. Current hypotheses, observations, evidence links, simulation branches, budgets, traces, and temporary telemetry remain owned by their existing runtime/lab/world stores.

The whole repository is never automatically injected into model context; `ContextProjection` remains bounded, task-specific, revision-aware, and visibility-aware.

## Optional existing service

`manufacturing-kg-agent` may provide read-only process/document evidence after clean no-KG/no-memory baselines exist.

## Non-goals

The active program does not include:

- raster P&ID OCR/symbol/line extraction;
- automatic arbitrary-plant simulator generation;
- production-grade autonomous real-plant control deployment;
- general fire/explosion/toxic-dispersion consequence modeling;
- 3D digital-twin reconstruction;
- fixed role-based multi-agent organizations;
- unrestricted recursive swarms;
- arbitrary Agent Python/shell/package installation as the normal analysis interface;
- a global cross-project learned-memory platform;
- LangGraph/MCP as required v0 infrastructure;
- mandatory microservice/Kafka/Redis/Kubernetes infrastructure for the first Playground backend;
- automatic vector/RAG indexing as the definition of canonical context.

## Research task families

1. **RCA** — diagnose incidents using observations, topology, typed hypotheses/predictions, analysis, and discriminating counterfactual experiments.
2. **Simulation-backed HAZOP** — later formulate deviations, test simulator-supported scenarios, observe consequences, and produce evidence-backed findings.
3. **Recovery planning** — later generate candidate strategies, evaluate them in forks, and propose bounded interventions through deterministic gates.
4. **AutoProcessResearch** — later autonomously iterate bounded engineering hypotheses/experiments against a frozen evaluator and mutable search surface.

## Hybrid orchestration contract

```text
consumer state projection
        |
Main Agent / ModelTurn
        |
        +-- optional ModelStateUpdateProposal
        |      -> atomic TaskStateStore.apply_batch
        |
        +-- one action: NONE | ToolCall | WorkBatch | FinishProposal
                  |
            pre-execution deterministic gates
                  |
               Executor
                  |
         post-execution deterministic verifier
                  |
         deterministic result ingestion
                  |
         consumer TaskStateStore.apply_batch
```

A WorkBatch contains only `TOOL | SUBTASK` items with explicit `depends_on` in v0.

A richer mutable Dynamic DAG is not a v0 dependency; its value/replanning semantics are an open orchestration research question.

The architecture contract is accepted as the implementation boundary, not as proof that Hybrid outperforms ReAct/fixed workflows.

## Knowledge / rule authority

The canonical Rule model is:

```text
origin × validation × authority
```

Examples:

```text
origin: SIMULATOR | FORMAL_DERIVATION | POLICY | LITERATURE | EXPERIMENT | AGENT
validation: NONE | CORROBORATED | SIMULATION_VALIDATED | ROBUST_VALIDATED | REVIEWED
authority: REFERENCE | ADVISORY | PLANNING | OPERATIONAL_PROPOSAL | HARD_GATE
```

K0–K4 may be used only as human-facing shorthand/presets.

Paper/Agent/simulation evidence cannot self-promote execution authority. Authority is assigned independently by explicit policy.

These Rule authority categories are reused by Canonical Context only when the owning source contract actually defines them; non-rule sources are not forced into Rule Registry authority semantics.

## Information semantics

```text
Trace != Observation != Evidence != EngineeringRecord != Knowledge != Context
```

- Every successful agent-visible ToolResult is registered as an immutable observation/result.
- Evidence is an explicit link from an observation to a hypothesis/claim.
- Engineering Records summarize/audit completed work.
- Rules/knowledge have separate governance/authority.
- Context is a bounded task-specific projection.

Historical Engineering Records are archive-only in the first benchmark and are not automatically injected into future contexts.

## Tool architecture

```text
Main Agent
 -> runtime ToolSpec/allowlist/budget/side-effect gates
 -> consumer validate_request
 -> Executor
 -> lab Tool Bridge adapter
 -> pinned local/remote implementation
 -> ToolResult + provenance/resource usage
```

Tool Bridge is not the authorization layer.

Compound tools that internally run simulator trials are `SIMULATE` and consume declared rollout/horizon/trial budget.

MCP may later be one external provider protocol, not a core safety/runtime dependency.

## Agent abilities under study

- observation selection;
- topology/process reasoning;
- hypothesis generation/ranking;
- typed prediction quality;
- experiment design/discrimination;
- dependency-aware work planning;
- bounded subagent allocation;
- analysis-tool selection;
- evidence integration/rank update;
- semantic stopping;
- recovery strategy generation later;
- research-loop idea generation later;
- numeric-search delegation to optimizers later;
- tool/budget/context efficiency;
- uncertainty handling;
- graceful handling of unsupported capabilities.

## Program invariants

1. Environment truth is deterministic code/data, not prompt memory.
2. Ground truth/candidate answer sets used by scorers are separated from Agent-visible context/refs.
3. Model output proposes; deterministic code authorizes/executes/applies validated state updates.
4. Model-proposed internal state changes are explicit and revision-bound; rejected changes do not silently affect execution.
5. Pre-execution validation and post-execution verification are distinct.
6. SIMULATE never mutates reference state.
7. Subagents are ephemeral bounded tasks, not permanent organizational identities.
8. Conversation transcripts are not canonical task/investigation state.
9. Observation becomes evidence only through an explicit evidence link.
10. Rule origin/validation/authority are independent; model/paper evidence cannot self-grant HARD_GATE authority.
11. Compound tools cannot hide nested simulator/search resource usage.
12. Every model turn uses/persists an exact ContextProjection ref.
13. Unsupported physics must be explicit rather than hallucinated.
14. Strong deterministic baselines are not weakened to make Agent results look better.
15. Numeric optimization should use deterministic/seeded search tools where appropriate rather than repeated LLM floating-point guessing.
16. Application/UI projections are derived views and do not replace runtime/lab/world canonical state.
17. Version-controlled canonical context is materialized by exact source revision; local materialization never overrides visibility policy.
18. Canonical context source inventory is frozen for a READY run and cannot be mutated by model output.

## Success criteria for first meaningful v1 research slice

The first v1 slice is RCA-centric. A reproducible TEP incident can be:

```text
created -> observed
-> represented in RcaState
-> investigated by the Main Agent
-> externalized through explicit typed state updates
-> analyzed with bounded read/analysis/simulation tools
-> tested by typed discriminating counterfactuals when useful
-> concluded as a structured CausalClaim with evidence links
-> scored against hidden truth and strong C0 baseline
-> complete trace/state/context projections/artifacts/InvestigationReport saved
```

The same frozen cases support at least:

- C0 deterministic enumerate/simulate/match;
- static/one-shot LLM;
- ReAct;
- fixed workflow;
- Hybrid reference loop;
- Hybrid + dependency-aware TOOL WorkBatch;
- bounded-subagent orchestration condition.

HAZOP, Recovery, and AutoProcessResearch are later research slices and do not block the first RCA result.

## Development policy

**Phase 0 Design Freeze is complete.** See `design-freeze-record.md`.

Implementation proceeds according to `implementation-plan.md`. Implementation evidence has added an Application/Playground layer and sequencing refinements without reopening the accepted World/Control/Information/Investigation contracts.

Current direction:

- `tep-sim` A1–A4: implemented; A3 semantic fixture still requires human verification before D0 benchmark freeze;
- runtime B1–B3: implemented; focused B2.1 request-bound reservation is required before D0; B5 real provider may proceed independently of B4 and is required before D1, not D0;
- lab C1–C4: implemented; C5 minimal Tool Bridge remains;
- P0 Playground Backend is required before D0 benchmark freeze;
- B4 bounded subagents are required for the later O5/D2 orchestration condition, not for the first single-Agent D1 run.

Coding agents may work in parallel only through spec-scoped branches/worktrees and explicit dependency contracts in `development-agent-orchestration.md`.

If implementation finds a missing/contradictory public contract, emit `SPEC_CONFLICT` and reopen the owning spec rather than inventing architecture locally.

## Parked research

Generic `pid2sim`, P&ID computer vision, arbitrary plant model generation, 3D reconstruction, cross-incident learned memory, full Dynamic DAG infrastructure, LangGraph integration, and MCP integration are not on the first critical path.
