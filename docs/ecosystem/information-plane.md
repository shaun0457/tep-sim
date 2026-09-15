# Information Plane Architecture

Status: proposal

## Purpose

Define the typed information boundary between Agent reasoning and the TEP world without creating a fourth repository or prematurely building multiple storage services.

The Information Plane is a **logical architecture layer**: stable refs, schemas, provenance, visibility, append-only records, and projections. v0 may implement it with one run log plus artifacts.

```text
                  Agent Runtime
                  CONTROL PLANE
                       |
                       v
              Information Plane
      +--------------------------------+
      | ProcessGraph / VariableRegistry|
      | Rule metadata                  |
      | RunLog typed records/views     |
      | Artifact refs                  |
      | Consumer TaskStateStore        |
      | Engineering records            |
      +----------------+---------------+
                       |
                       v
                    tep-sim
                  WORLD PLANE
```

## Core principle

```text
Memory != Context
Trace != Observation
Observation != Evidence
Evidence != Engineering Record
Engineering Record != Knowledge/Rule
```

Conversation text is not authoritative system state.

Future context is a bounded projection over approved/visible information, not an ever-growing transcript/history dump.

## v0 physical persistence

Do not implement five independent stores before a scale/multi-consumer requirement exists.

A valid v0 layout may be:

```text
runs/<run_id>/
  manifest.json
  events.jsonl
  artifacts/
  investigation-report.json
```

The append-only event/run log can expose typed views/indexes for:

- observations/results;
- evidence links;
- hypotheses/state deltas;
- experiments;
- decisions;
- tool/subtask/gate/verification trace.

`EvidenceStore`, `ExperimentLedger`, and similar names describe logical views/contracts, not mandatory separate databases/services.

## Generic reference ownership

`industrial-agent-runtime` owns the generic `InformationRef` envelope defined in `runtime-v0.md`:

```text
ref_id
kind
owner
version
checksum?
visibility: AGENT | EVALUATOR | INTERNAL
created_at
```

The producing repository owns the referenced content/schema.

## Information objects and ownership

### `ProcessGraph`

Owner: `tep-sim`

Contains normalized process topology/semantics and source/version provenance.

### `VariableRegistry`

Owner: `tep-sim`

Contains canonical XMEAS/XMV/IDV identities, units, simulator bindings, and authoritative environment metadata.

### `Rule`

Ownership follows rule scope:

- simulator/runtime constraints: `tep-sim`;
- lab policy/advisory/experimental rules: `tep-agent-lab`.

Canonical rule metadata is `origin × validation × authority`, defined in `knowledge-rule-registry-v0.md`.

### `ObservationRecord`

Owner: producing lab/tool/runtime adapter through the run log.

An immutable record that a query/tool/simulator/analysis returned something.

```text
observation_id
producer_request_ref
summary
artifact_refs[]
information_refs[]
provenance
visibility
created_at
```

Observation is not automatically evidence.

### `HypothesisEvidenceLink`

Owner: `tep-agent-lab`.

An explicit relation between a visible observation and a hypothesis/claim:

```text
hypothesis_ref
observation_ref
relation
reason_summary
producer
```

This allows the evaluator to distinguish queries from actually cited/used evidence.

### Experiment Ledger view

Owner: `tep-agent-lab`.

Logical append-only view of proposed/frozen/executed experiments and outcomes. Canonical experiment contracts are in `hypothesis-experiment-v0.md`.

### `TaskStateStore`

Generic protocol owner: `industrial-agent-runtime`.

Consumer implementation owner: `tep-agent-lab` for RCA.

The runtime calls `revision/status/project/apply`; it never imports RcaState fields.

### Artifact files

Ownership follows producer.

Dense telemetry, rollouts, plots, arrays, context projections, and other large blobs remain outside model context and are referenced by checksum/versioned refs.

## Engineering records

`tep-agent-lab` owns structured archival engineering records defined in `engineering-records-v0.md`.

v0 minimum:

- `InvestigationReport`;
- `DecisionRecord`;
- `ExperimentRecord`.

Future types may include:

- `RecoveryRecord` / `MaintenanceRecord`;
- `LessonLearned`;
- `RunbookCandidate`;
- `ManualChangeProposal`.

These future records do not automatically gain rule/authority status.

## Engineering records versus future memory

v0 records are **archive/audit outputs**.

They are not automatically retrieved into later benchmark ContextProjections. This preserves clean no-memory baselines and prevents previous Agent conclusions from contaminating hidden evaluation.

A later cross-incident-memory experiment may explicitly compare:

```text
no history
vs raw trace retrieval
vs structured engineering-record retrieval
vs approved lesson/rule retrieval
```

Such retrieval must be versioned/configured as a capability ablation.

## Context projection

There is no generic domain-relevance `ContextBroker` service in v0.

Instead, the consumer provides a domain function such as:

```text
project_rca_state(state, policy) -> ContextProjection
```

Consumer responsibilities:

- resolve domain refs;
- choose relevant state/evidence/topology slices;
- reject evaluator-only refs;
- preserve provenance;
- keep within configured content policy.

Runtime responsibilities:

- validate generic ref integrity/visibility metadata;
- enforce model-context/token/size limits;
- persist the exact immutable ContextProjection used for each model turn.

Only introduce a generic ContextBroker after a second domain demonstrates genuinely reusable projection behavior.

## Read/write authority

```text
Object / view              Agent reads?       Write authority
ProcessGraph                policy-scoped      tep-sim build/update path
VariableRegistry            policy-scoped      tep-sim
Simulator rules             policy-scoped      tep-sim
Lab rules/policies          policy-scoped      lab controlled path
ObservationRecord           yes by visible ref deterministic producer/run log
EvidenceLink                yes               validated lab state update
Experiment records          yes               lab experiment path
RcaState                    projected          lab TaskStateStore.apply
Evaluator Ground Truth      no                evaluator only
Artifacts                   visible by ref     deterministic producer
Engineering records         archive/read later report builder + verifier
```

The model never directly edits persistent records/stores. It proposes typed operations/links/results through registered contracts.

## Provenance

Every derived object must point to inputs/transformation/version.

Examples:

```text
rollout R17 + feature extractor v2 -> Observation O42
Observation O42 -> EvidenceLink supporting H3
Experiment E7 + predictions -> deterministic result ER7
final RcaState revision 31 + refs -> InvestigationReport IR1
```

## Ground-truth isolation

Two controls are required:

1. consumer projection/tool policy must not resolve evaluator-only refs;
2. generic runtime must fail closed if a ContextProjection includes an `EVALUATOR` ref.

Leakage audit must inspect artifact names/metadata as well as structured fields.

## Why this is not a new repository

The plane describes ownership/contracts/views, not an independently deployable product.

Revisit a shared information service only if multiple independent domain labs require the same persistent evidence/experiment/record infrastructure.

## Invariants

- Conversation transcript is not canonical state.
- v0 does not require multiple physical databases/stores.
- `InformationRef` generic envelope belongs to runtime.
- Domain relevance/projection belongs to the consumer.
- Observation becomes evidence only through an explicit link.
- Engineering records do not automatically become Rules or future Context.
- Hidden evaluator truth never becomes agent-visible information.
- Mutable state is versioned; run evidence/history is append-only.
