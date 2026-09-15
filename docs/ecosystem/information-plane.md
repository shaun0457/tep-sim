# Information Plane Architecture

Status: accepted direction / v0 ownership proposal

## Purpose

The program needs a durable information layer between agent reasoning and the simulation world. This layer is not a new repository. It is a set of typed, versioned information services and references owned by the existing three-repository architecture.

```text
                  Agent Runtime
                  CONTROL PLANE
                       |
                       v
              Information Plane
      +--------------------------------+
      | ProcessGraph / DEXPI           |
      | Variable Registry              |
      | Rule Registry                  |
      | Evidence Store                 |
      | Experiment Ledger              |
      | Artifact / Run Store           |
      | Investigation State refs       |
      +----------------+---------------+
                       |
                       v
                    tep-sim
                  WORLD PLANE
```

## Design principle

Conversation text is not the authoritative system state. The runtime passes stable references to typed information objects and materializes only the task-relevant subset into model context.

## Information objects

### `ProcessGraph`

Owner: `tep-sim`

Contains machine-readable process structure derived from DEXPI/curated TEP semantics:

- nodes/equipment/process sections;
- streams/connectivity;
- control/sensor relationships where represented;
- canonical IDs;
- source/version provenance.

### `VariableRegistry`

Owner: `tep-sim`

Contains canonical XMEAS/XMV/IDV identities, units, ranges when authoritative, semantic bindings, and source provenance.

### `RuleRegistry`

Split ownership:

- hard simulator/environment rules owned by `tep-sim`;
- validated/heuristic investigation rules owned by `tep-agent-lab`.

Each rule records knowledge level, source, scope, validation status, enforcement behavior, and version.

### `EvidenceStore`

Owner: `tep-agent-lab`

Stores compact, addressable evidence produced or retrieved during investigations:

```text
evidence_id
type
claim/summary
source_ref
artifact_ref?
producer
created_at
scope
quality/uncertainty metadata
```

Evidence may point to telemetry windows, topology query results, paper/document excerpts, analysis outputs, or simulation rollouts.

### `ExperimentLedger`

Owner: `tep-agent-lab`

Append-only logical history of proposed and executed experiments:

```text
experiment_id
research/investigation_id
hypothesis_refs
purpose
configuration/intervention refs
seed/horizon/budget
result refs
score/metrics
status
keep/reject/neutral decision?
provenance
```

It supports RCA counterfactuals and AutoResearch without forcing the Main Agent to remember prior attempts in conversation history.

### `ArtifactStore`

Owner: physical artifact ownership follows producing repo; references are consumer-visible.

Stores dense traces/plots/tables/model outputs outside LLM context. Agent-visible tools return compact summaries plus artifact refs.

### `InvestigationState`

Owner: `tep-agent-lab`, coordinated through `industrial-agent-runtime`.

Contains current goal, hypotheses, evidence refs, experiment refs, open questions, delegated tasks, budget state, and conclusion status.

## Reference contract

Cross-component state SHOULD use opaque stable references rather than direct Python objects or full blobs.

Conceptually:

```text
InformationRef:
  ref_id
  kind
  owner
  version
  checksum?
  visibility: AGENT | EVALUATOR | INTERNAL
  created_at
```

The `visibility` field is critical for ground-truth isolation.

## Read/write authority

```text
Object                 Read by Agent?   Write authority
ProcessGraph            yes              tep-sim build/update path
VariableRegistry        yes              tep-sim
Hard Rule Registry      yes              tep-sim / reviewed code-data
Lab Rule Registry       yes              tep-agent-lab promotion workflow
EvidenceStore           yes              tool/runtime adapters
ExperimentLedger        yes              lab experiment service
Evaluator Ground Truth  no               evaluator only
InvestigationState      scoped           Coordinator + validated updates
ArtifactStore           by ref           producing deterministic tool/service
```

The model never directly edits persistent stores. It requests typed updates through tools/contracts.

## Context Broker

The generic runtime SHOULD provide a reference-aware `ContextBroker` interface but must not decide TEP semantics.

Consumer responsibilities:

- resolve information refs;
- select task-relevant slices;
- apply visibility policy;
- enforce size/token budgets;
- summarize deterministically where possible;
- preserve provenance.

Example:

```text
Main Agent requests reactor cooling context
 -> ContextBroker receives process/evidence refs
 -> lab adapter selects local topology + recent signals + relevant rules
 -> compact structured context enters model turn
```

## Provenance rule

Every derived information object must be traceable to its inputs and transformation.

Examples:

```text
paper excerpt -> extracted K3 candidate rule
rollout R17 + analyzer v2 -> lag-analysis evidence E42
K3 rule + validation campaign V4 -> K2 rule revision
```

## Why this is not a new repository

The information plane describes contracts and ownership, not a standalone product. Creating another repo now would add coordination/context overhead without an independent consumer boundary.

Revisit only if multiple independent domain labs require the same persistent evidence/experiment services.

## Invariants

- Hidden evaluator truth cannot be materialized through agent-visible refs.
- Large raw artifacts are not automatically copied into model context.
- Every mutable information object is versioned or append-only.
- Domain truth remains owned by domain/environment repositories, not generic runtime.
- Conversation transcripts are supplementary trace data, not canonical investigation state.
