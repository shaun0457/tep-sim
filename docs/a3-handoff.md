# A3 DEXPI / ProcessGraph binding handoff

Task: A3. Branch: `feat/dexpi-binding-v0`. Base: `main` `fcf9929`.
Owning specification: `docs/specs/dexpi-binding-v0.md`.

## Delivered

- `tep_sim.process`: immutable `ProcessGraph` (17 nodes, 18 edges including TEP
  streams 1-11 and cooling-water/steam utilities), fail-closed normalization, and
  deterministic topology queries plus `TopologyProjection`;
- `tep_sim.bindings`: `VariableBinding` contracts with required provenance; the
  runtime identity is always resolved from the vendored `REGISTRY`;
- `tep_sim.evaluator_bindings`: a separate `EVALUATOR_ONLY` entity <-> IDV registry
  that accounts for every IDV (15 bound, IDV(16)-(20) explicitly unbound), pinned
  to the exact graph content hash;
- packaged, pinned fixtures under `src/tep_sim/fixtures/`.

## Blind-RCA leakage boundary

The Agent-visible graph and projection hold only XMEAS/XMV bindings. They have no
disturbance query, reject `DISTURBS` bindings and `IDV(n)` strings in visible
fixtures, and the projection constructor rejects non-visible runtime kinds. Tests
check that no local projection contains an IDV id or upstream IDV name.

## Validation detected

Duplicate IDs and stream numbers, dangling edges and attachments, unknown runtime
variables, relation/kind mismatches, conflicting one-to-one bindings,
unnormalizable entities and unknown fields, expected variables absent from the
simulator or left unbound, undeclared unbound entities (declared ones become
`INTENTIONALLY_UNBOUND` warnings), unknown source references, missing
provenance, upstream-revision mismatch, schema mismatch, pinned-content drift,
and evaluator/graph version mismatch. All issues are reported together.

## Verification

```text
PYTHONPATH=src;<upstream>/src python -m pytest -p no:cacheprovider -q tests \
  <upstream>/tests/test_constants.py <upstream>/tests/test_controllers.py \
  <upstream>/tests/test_simulator.py
```

124 passed locally on Python 3.13.0 and 3.12.4 (42 A3, 20 A1/A2, 62 pinned
upstream). CI runs 3.11 and 3.13.

## Unresolved

- The fixture is a curated equivalent, not the official DEXPI XML; the bindings
  still need human review (`PENDING_HUMAN_REVIEW`).
- XMEAS(22) is named "Separator Cooling Water Outlet Temp" upstream; it is bound
  to the condenser cooling-water outlet per the Downs & Vogel flowsheet.
- Which evaluator bindings a disclosed non-blind condition may expose is a
  `tep-agent-lab` C4/D0 policy decision; `tep-sim` does not decide it.

No `SPEC_CONFLICT`.
