# ADR-001: Exact snapshot state for the pinned Python backend

Status: accepted  
Date: 2026-09-17  
Owning spec: `docs/specs/snapshot-fork-replay-v0.md`

## Context

The v0 specification leaves snapshot fidelity open until the actual upstream
state surface is inspected. A valid decision must preserve process, controller,
randomness, and adapter state without advancing the source environment.

The pinned upstream Python `TEPSimulator` keeps all continuation state on the
object graph:

- process state and derivatives (`yy`, `yp`), measurements, MVs, and IDVs;
- LCG random state (`_g`) and disturbance-walk coefficients/times;
- thermodynamic/process common-block values and shutdown state;
- simulator time and step count;
- PI controller errors, cascade setpoints, timing, and purge override state.

The A1 adapter additionally owns active MV constraints. Run identity, events,
telemetry artifacts, and prior schedules are provenance rather than physical
continuation state.

## Decision

Snapshots of upstream revision
`9a6c8e5fcef4a2850778704e7793c87b0a187005` on the Python backend are declared
`EXACT`. The state payload serializes the complete `TEPSimulator` object graph
and the adapter's constraints and termination state. Each fork deserializes its
own object graph. The v0 branch randomness policy is `CLONED_STATE`.

`EXACT` means an exact continuation with the same environment version, upstream
revision, state format, and Python backend. It does not claim compatibility
across code revisions, state-format changes, or other backends. Unsupported
fidelity, version, and format values fail with `SnapshotFailure`.

Snapshot creation writes separate state and metadata artifacts but does not
change source simulator state, events, intervention schedule, or provenance.
The snapshot metadata is the audit record for that operation.

Replay records the exact parent snapshot, config, post-fork typed intervention
schedule, target time/step, random policy, source identities, and expected final
observation checksum. Replay permits only `DisturbanceIntervention`,
`MVIntervention`, and `MVConstraint`, and validates schedule order and time/step
agreement before loading state.

## Evidence

An exploratory round trip after 17 closed-loop steps produced a 15,976-byte
payload, preserved LCG state `2636408377`, and yielded `array_equal` process
states and measurements after the next step.

The acceptance test activates IDV(1), snapshots after 25 steps, forks twice,
and advances both branches for 300 real upstream steps. Across every XMEAS and
XMV value, maximum absolute branch error is `0.0`. Further tests show that
distinct interventions do not change a sibling or parent, persisted replay
reaches the exact recorded observation, and a failed branch does not affect
other worlds.

## Trust boundary

The payload format uses `pickle`; therefore hashes provide corruption detection,
not producer authentication. Loading requires an explicit trusted artifact root.
The loader derives the only allowed state and metadata paths from validated
run, branch, and snapshot identifiers, requires exact paths below that root,
verifies both checksums, and requires the supplied snapshot object to equal its
persisted metadata before deserialization. A forged external path is rejected
before `pickle.loads`.

Artifact trees received from another trust domain must not be loaded as trusted.
A future interchange feature would need an authenticated producer and a
non-executable state format; that is outside v0.

## Consequences

Forks are fast and retain exact random/control continuation state, while each
branch pays one deserialization and its own mutable memory. Persisted artifacts
are intentionally revision-bound. Reconstruction from initial seed and schedule
is unnecessary for v0, and no approximate fidelity is advertised.

No public specification conflict was found.
