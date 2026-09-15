# Industrial Simulation + Agent Ecosystem

This program studies **AI agents operating inside a trustworthy industrial simulation world**. Generic P&ID digitization, arbitrary simulator generation, and 3D reconstruction are not current core goals.

## Three-repository program

```text
1. Environment / World Plane        -> tep-sim
2. Agent Runtime / Control Plane    -> industrial-agent-runtime
3. Domain / Information / Lab      -> tep-agent-lab
```

Existing knowledge projects remain optional services.

## Program architecture

```text
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

The Information Plane is a logical ownership/reference layer across existing repos, not a fourth repo and not multiple mandatory databases.

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

Does not own TEP/domain state, Tool Bridge implementations, DEXPI parsing, rules/safety truth, RCA/HAZOP/recovery, or benchmark scoring.

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
- model Context is a bounded task-specific projection.

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
- public contracts have one owning repo.

## Design Freeze state — COMPLETE

The program completed:

1. independent full architecture/spec review;
2. formal adjudication;
3. focused independent re-review;
4. closure of the final MAJOR-R1 state-update contract gap.

Final record:

- [`design-freeze-record.md`](design-freeze-record.md)

Supporting review records:

- [`reviews/2026-09-15-independent-spec-review.md`](reviews/2026-09-15-independent-spec-review.md)
- [`reviews/2026-09-15-focused-re-review.md`](reviews/2026-09-15-focused-re-review.md)
- [`design-review-adjudication.md`](design-review-adjudication.md)

Implementation status:

```text
tep-sim A1-A4          GO
runtime B1-B5          GO in dependency order
lab C1-C5              GO in dependency order
D0 benchmark pilot     GO after upstream dependencies
```

Deferred/open-research items remain explicitly non-blocking.

## Research / implementation sequence

```text
tep-sim A1-A4
     |
runtime B1 -> B2/B3 -> B4 -> provider
     |
lab C1/C2/C3 -> C4/C5
     |
D0 benchmark identifiability + C0
     |
D1 blind RCA capability study
     |
D2 orchestration O0-O5
     |
later HAZOP / recovery / AutoProcessResearch
     |
optional knowledge / organizational-memory studies
```

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
- arbitrary Agent Python/shell/package installation as normal Tool Bridge behavior.
