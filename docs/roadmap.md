# Roadmap: TEP Process Sandbox

This roadmap stops at the environment boundary. The fastest path to useful agent research is to make TEP trustworthy, forkable, semantically queryable, and capability-aware — then move upward into `tep-agent-lab`.

Canonical specs live in `docs/specs/`.

## Phase 0 — Verify upstream contract

**Goal:** remove uncertainty about the vendored simulator before wrapping it.

Deliver:

- record/pin upstream revision;
- verify target Python/Windows setup;
- verify reset/step, XMEAS/XMV access, IDV injection, control modes, shutdown behavior;
- generate/validate canonical runtime variable registry;
- deprecate local tables that conflict with runtime truth.

Exit:

```text
initialize -> baseline -> supported disturbance -> reproduce with same seed/config
```

No new abstraction should hide an unverified upstream behavior.

## Phase 1 — Environment API v0

Branch: `feat/environment-api-v0`  
Spec: `docs/specs/environment-api-v0.md`

Deliver:

- `TEPEnvironment` facade;
- config/observation/intervention/result contracts;
- explicit control-mode validation;
- run provenance and artifact policy;
- typed failure behavior.

Exit: all Environment API v0 acceptance tests pass without agent dependencies.

## Phase 2 — Snapshot / fork / replay v0

Branch: `feat/snapshot-fork-v0`  
Spec: `docs/specs/snapshot-fork-replay-v0.md`

Deliver:

- snapshot fidelity investigation;
- isolated branches;
- RNG/state policy;
- parent/branch provenance;
- replay/reproduction tests;
- explicit fidelity status (`EXACT`, `RECONSTRUCTED`, or unsupported).

Exit:

```text
state S -> fork A/B -> different interventions -> isolated reproducible rollouts
```

This is the highest-value environment feature for agent research.

## Phase 3 — DEXPI / process semantics v0

Branch: `feat/dexpi-binding-v0`  
Spec: `docs/specs/dexpi-binding-v0.md`

Deliver:

- choose/pin machine-readable TEP semantic fixture;
- normalize into compact `ProcessGraph`;
- topology queries;
- validated entity <-> XMEAS/XMV/IDV binding registry;
- provenance/validation tests.

Exit: callers can navigate reactor/cooling topology and resolve known runtime bindings without raw XML or prompt memory.

No P&ID OCR, symbol detection, generic model generation, or 3D reconstruction.

## Phase 4 — Capability / safety v0

Branch: `feat/capability-safety-v0`  
Spec: `docs/specs/safety-capability-v0.md`

Deliver:

- machine-readable capability registry;
- minimal deterministic semantic scenario compiler;
- explicit unsupported/ambiguous scenario results;
- deterministic process/shutdown safety evaluation;
- tests proving unsupported consequence physics are not fabricated.

Exit: an external agent/tool adapter can determine whether an experiment is supported before any environment mutation and obtain deterministic outcome/safety evidence afterward.

## Environment v0 complete

`tep-sim` v0 is sufficient for the agent program when this path works reliably:

```text
reset
 -> observe topology + state
 -> snapshot
 -> fork
 -> compile/apply supported scenario
 -> rollout
 -> safety/capability evidence
 -> replay/provenance
```

At this point the critical path moves to `industrial-agent-runtime` and `tep-agent-lab` rather than adding more simulator features.

## Optional extensions after first agent benchmark

Only implement when a concrete consumer needs them:

- batch rollout convenience API;
- richer process/control-loop semantics;
- performance/storage optimization;
- additional scenario mappings;
- simple serialization adapters for a 2D topology/telemetry UI.

Do not make these block the first RCA benchmark.

## Explicitly out of roadmap

- LLM/provider integration;
- dynamic subagents;
- HAZOP/RCA reasoning and scoring;
- recovery strategy selection;
- generic P&ID digitization/model generation;
- Blender/Omniverse/3D work.

See `docs/ecosystem/program-charter.md` and `docs/ecosystem/implementation-plan.md` for the cross-repository plan.
