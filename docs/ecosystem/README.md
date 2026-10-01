# Industrial Simulation + Agent Ecosystem

This program studies **AI agents operating inside a trustworthy industrial simulation world**. Generic P&ID digitization, arbitrary simulator generation, and 3D reconstruction are not current core goals.

## Three-repository program

```text
1. Environment / World Plane        -> tep-sim
2. Agent Runtime / Control Plane    -> industrial-agent-runtime
3. Domain / Information / Lab      -> tep-agent-lab
```

Existing knowledge projects remain optional services. The Playground Application Plane is a logical outer layer, not a fourth core repository in v0.

## Program architecture

```text
                    User / Researcher
                           |
                           v
               Playground Application Plane
       run lifecycle / manifest / canonical context
          read projections / events / artifacts
                           |
                           v
                industrial-agent-runtime
                    CONTROL PLANE
             Main Agent + deterministic
       gates / Executor / result verification
    explicit state-update + WorkBatch contracts
                           |
                           v
                    Information Plane
        refs / run log / state / records / rules
                           |
                           v
                    tep-agent-lab
             TEP-specific domain layer
                           |
                           v
                     tep-sim
                    WORLD PLANE
```

The Information Plane is a logical ownership/reference layer across existing repos, not a fourth repo and not multiple mandatory databases. The Application Plane is likewise a logical hosting/projection layer and initially lives in `tep-agent-lab`.

## Application / Playground principle

The Application Plane assembles one reproducible run and exposes read/query projections for people and future UI clients. It does not replace the generic Agent runtime or grant tool authority.

```text
Application/UI request
        !=
Agent ToolCallRequest
```

Agent execution still passes through:

```text
ToolSpec -> gates -> consumer validation -> Executor -> result verifier
```

Blind-playground views default to Agent-visible information. Evaluator/debug views are explicit trusted projections and must not silently contaminate Agent context.

## Canonical Context principle

Reviewed/versioned engineering and research truth lives in repository-controlled sources and is materialized locally at exact revisions for reproducible runs.

```text
Git canonical source
      |
      | exact revision / local checkout
      v
CanonicalContextRegistry
      |
 visibility + authority + provenance
      |
      v
bounded ContextProjection
      |
      v
Agent
```

Examples include ProcessGraph, variable metadata, reviewed bindings, safety limits, capability/scenario mappings, benchmark manifests, visibility/scoring policy, and evaluator ground truth.

Local availability is not permission: evaluator-only sources may be present on disk while remaining inaccessible to Agent projections/tools. The entire repository checkout is never automatically injected into model context.

Run-specific mutable investigation/runtime state stays in its existing owning stores and is not promoted to Git-backed canonical knowledge.

## 1. `tep-sim` — trusted process world

Owns:

- TEP simulator adapter;
- canonical XMEAS/XMV/IDV registry;
- reset/observe/step/rollout;
- snapshot/fork/replay;
- typed disturbances/interventions;
- capability/environment safety evaluation;
- ProcessGraph/DEXPI-derived semantics;
- entity-to-runtime binding registry;
- simulator/runtime truth;
- run provenance/artifacts.

For TEP, use machine-readable process semantics directly. Do not build P&ID OCR/generic simulator generation.

```text
DEXPI / ProcessGraph = static semantics/topology
TEP simulator        = dynamic behavior
binding registry     = semantic entity <-> runtime variable
```

`tep-sim` does not own LLMs, Agent orchestration, RCA/HAZOP reasoning, or recovery strategy selection.

## 2. `industrial-agent-runtime` — generic control plane

Owns:

- Main Agent provider/interface;
- generic InformationRef / ContextProjection / TaskStateStore;
- ModelTurn / ModelStateUpdateProposal / StateDelta;
- Task/Budget/ToolSpec/ToolResult;
- standard + extra-dimensional resource accounting;
- deterministic pre-execution gates;
- deterministic Executor/dispatcher;
- post-execution result verification;
- dependency-aware WorkBatch (`TOOL | SUBTASK` + `depends_on`);
- ephemeral Subtask/SubtaskResult;
- tracing/provenance;
- fake provider/test contracts.

Does not own TEP/domain state, Tool Bridge implementations, DEXPI parsing, rules/safety truth, RCA/HAZOP/recovery, benchmark scoring, or Playground persistence/projection semantics.

v0 does not require:

- full mutable Dynamic DAG infrastructure;
- LangGraph;
- MCP.

Those may be studied/adapted later only after concrete requirements/evidence.

## 3. `tep-agent-lab` — TEP domain/research layer

Owns:

- RcaState implementation of TaskStateStore;
- ObservationRecord / EvidenceLink;
- Hypothesis / typed Prediction / Experiment;
- structured CausalClaim;
- Rule/policy metadata;
- TEP-specific Agent tools;
- Tool Bridge adapters;
- append-only run views/artifacts;
- Engineering Records;
- benchmark design/identifiability/C0;
- RCA/evaluation;
- initial Playground application/backend assembly;
- later HAZOP/recovery/AutoProcessResearch.

It is the only core repo that intentionally knows both generic runtime contracts and TEP domain semantics.

## State-update semantics

Model reasoning state is explicit; it is not hidden in chat history.

```text
ContextProjection
 -> ModelTurn
      -> optional ModelStateUpdateProposal
           -> atomic TaskStateStore.apply_batch
      -> one action: NONE | TOOL_REQUEST | WORK_BATCH | FINISH_PROPOSAL
```

Model-proposed state deltas are bound to the exact projection revision the model saw. A stale/invalid update prevents the same turn's action from dispatching.

Successful executable results are ingested deterministically. In the TEP lab every successful agent-visible ToolResult becomes an ObservationRecord automatically; evidence remains a separate explicit link.

Parallel WorkBatch result-ingestion deltas bind the then-current state revision in a stable deterministic order, rather than all reusing the originating model revision.

## Information semantics

```text
Trace != Observation != Evidence != EngineeringRecord != Rule/Knowledge != Context
```

- successful tool/simulator output creates an ObservationRecord;
- an explicit link makes an observation evidence for a claim/hypothesis;
- Engineering Records archive completed work;
- reusable rules/knowledge have separate provenance/validation/authority;
- model Context is a bounded task-specific projection;
- Playground views are derived projections, not new canonical truth.

v0 may implement logical information views using one append-only run log plus artifacts.

## Rule / knowledge authority

Canonical machine metadata:

```text
origin × validation × authority
```

Example axes:

```text
origin: SIMULATOR | FORMAL_DERIVATION | POLICY | LITERATURE | EXPERIMENT | AGENT
validation: NONE | CORROBORATED | SIMULATION_VALIDATED | ROBUST_VALIDATED | REVIEWED
authority: REFERENCE | ADVISORY | PLANNING | OPERATIONAL_PROPOSAL | HARD_GATE
```

K0–K4 is documentation shorthand only.

Agent/paper/simulation evidence cannot directly self-promote hard execution authority.

## Tool Bridge principle

Tool Bridge lives in the lab/provider layer, while runtime owns authorization/budget/dispatch.

```text
Agent
 -> runtime ToolSpec/gates/resource reservation
 -> lab validate_request
 -> Executor
 -> Tool Bridge adapter
 -> pinned implementation
 -> result + provenance + actual resource draw
```

If a bridge internally executes simulator trials, it is `SIMULATE` and must expose nested rollout/horizon/trial usage.

First RCA bridge scope stays small:

- response features / trajectory comparison;
- cross-correlation / lag;
- optional upstream TEP detector baseline.

PCA/PLS/SALib/Optuna/Granger/MCP are later concrete-need additions.

## Engineering Records

v0 writes structured:

- InvestigationReport;
- DecisionRecord;
- ExperimentRecord.

They are archive/audit outputs first. They are not automatically retrieved into future benchmark context and do not automatically become Rules/Lessons/Runbooks.

Later organizational-memory research may explicitly study record retrieval and knowledge promotion.

## AutoProcessResearch

Later separate task family:

```text
frozen evaluator + bounded mutable surface
 -> baseline
 -> Agent conceptual hypothesis/change
 -> isolated simulation/search
 -> deterministic score
 -> append trial record
 -> ACCEPT/REJECT/NEUTRAL
 -> repeat
 -> held-out evaluation
```

Reference MUTATE is disabled by default; numeric search tools expose full nested SIMULATE budget.

## Existing projects

### `manufacturing-kg-agent`

Independent optional evidence service after clean no-KG/no-memory baselines.

### `personal-agent-os`

Independent personal orchestration/memory project; not part of the industrial runtime.

## Dependency direction

```text
                      manufacturing-kg-agent
                              ^
                              | optional later evidence
                              |
industrial-agent-runtime ---> tep-agent-lab <--- tep-sim
```

Rules:

- `tep-sim` depends on no Agent repo;
- `industrial-agent-runtime` depends on no TEP/domain repo;
- `tep-agent-lab` pins both;
- scientific/remote tools remain behind adapters;
- public contracts have one owning repo;
- Application Plane code initially stays in `tep-agent-lab`, not a fourth repo.

## Design Freeze state — COMPLETE

The program completed:

1. independent full architecture/spec review;
2. formal adjudication;
3. focused independent re-review;
4. closure of the final MAJOR-R1 state-update contract gap.

The Application/Playground re-baseline is an additive implementation-driven extension and does not reopen the accepted World/Control/Information/Investigation contracts.

Final record:

- [`design-freeze-record.md`](design-freeze-record.md)

Supporting review records:

- [`reviews/2026-09-15-independent-spec-review.md`](reviews/2026-09-15-independent-spec-review.md)
- [`reviews/2026-09-15-focused-re-review.md`](reviews/2026-09-15-focused-re-review.md)
- [`design-review-adjudication.md`](design-review-adjudication.md)

Implementation status:

```text
tep-sim A1-A4          implemented; A3 human verification remains before D0 freeze
runtime B1-B3          implemented
lab C1-C4              implemented
B2.1 + C5              next focused implementation milestones
P0 Playground Backend  required before D0 benchmark freeze
B5 provider            required before first D1 real-model run
B4 subagents            required only before O5/D2 bounded-subagent study
```

Deferred/open-research items remain explicitly non-blocking.

## Research / implementation sequence

```text
A1-A4 / B1-B3 / C1-C4 complete
                |
                v
        Program re-baseline
                |
      +---------+---------+
      |         |         |
     B2.1      C5     A3 human review
      |         |         |
      +---------+---------+
                |
        +-------+-------+
        |               |
       P0              B5 provider
        |               |
        +-------+-------+
                |
        D0 benchmark / C0
                |
          +-----+-----+
          |           |
        P1 UI      D1 blind RCA
                      |
                      v
                  B4 + D2/O5
                      |
             later HAZOP / recovery /
              AutoProcessResearch
```

P1 UI is not a D0 blocker. B4 is deliberately delayed until the orchestration study that needs SUBTASK capability.

Independent branches may run in parallel where frozen upstream contracts and file/module ownership permit.

## Documentation map

Program:

- [`program-charter.md`](program-charter.md)
- [`information-plane.md`](information-plane.md)
- [`design-review-adjudication.md`](design-review-adjudication.md)
- [`design-freeze-record.md`](design-freeze-record.md)
- [`decision-register.md`](decision-register.md)
- [`implementation-plan.md`](implementation-plan.md)
- [`documentation-standard.md`](documentation-standard.md)
- [`development-workflow.md`](development-workflow.md)
- [`development-agent-orchestration.md`](development-agent-orchestration.md)

Blueprints:

- `blueprints/industrial-agent-runtime/`
- `blueprints/tep-agent-lab/`

Application/backend contract:

- `tep-agent-lab/docs/specs/playground-backend-v0.md`

Environment:

- [`../architecture.md`](../architecture.md)
- [`../specs/`](../specs/README.md)
- [`../dexpi-tep-integration.md`](../dexpi-tep-integration.md)

## What not to build now

- raster P&ID OCR/generic simulator generation;
- photorealistic 3D plant reconstruction;
- permanent Supervisor/MachineExpert/DataEngineer/DataScientist role hierarchies;
- unrestricted recursive swarms;
- full Dynamic DAG engine before measured need;
- LangGraph/MCP integration before concrete need;
- automatic cross-run memory before clean baselines;
- arbitrary Agent Python/shell/package installation as normal Tool Bridge behavior;
- a mandatory vector database/RAG layer for canonical context;
- production microservice/distributed infrastructure for P0.
