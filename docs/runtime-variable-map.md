# Runtime Variable Map

This file documents the **vendored simulator runtime mapping**, not a literature appendix.

Source of truth for code must remain the vendored simulator metadata/constants at the pinned submodule commit. Tests should fail if this document/registry diverges from the simulator.

## Manipulated variables (XMV)

Current vendored mapping:

| ID | Runtime name | Initial value in vendored simulator |
|---|---|---:|
| XMV(1) | D Feed Flow (stream 2) | 63.05263039 |
| XMV(2) | E Feed Flow (stream 3) | 53.97970677 |
| XMV(3) | A Feed Flow (stream 1) | 24.64355755 |
| XMV(4) | A and C Feed Flow (stream 4) | 61.30192144 |
| XMV(5) | Compressor Recycle Valve | 22.21000000 |
| XMV(6) | Purge Valve (stream 9) | 40.06374673 |
| XMV(7) | Separator Pot Liquid Flow | 38.10034370 |
| XMV(8) | Stripper Liquid Product Flow | 46.53415582 |
| XMV(9) | Stripper Steam Valve | 47.44573456 |
| XMV(10) | Reactor Cooling Water Flow | 41.10581288 |
| XMV(11) | Condenser Cooling Water Flow | 18.11349055 |
| XMV(12) | Agitator Speed | 50.00000000 |

These values are simulator state initialization values, not a promise that every external TEP dataset uses identical operating conditions.

## Critical relationship for first recovery experiment

For reactor temperature experiments:

- `XMEAS(9)` = Reactor Temperature
- `XMEAS(21)` = Reactor Cooling Water Outlet Temperature
- `XMV(10)` = Reactor Cooling Water Flow
- `IDV(4)` = Reactor Cooling Water Inlet Temperature step disturbance
- `IDV(11)` = Reactor Cooling Water Inlet Temperature random variation
- `IDV(14)` = Reactor Cooling Water Valve sticking

This relationship should come from a registry/tool at runtime rather than being copied into an LLM system prompt.

## Measurement units

The vendored simulator defines, among others:

- `XMEAS(4)` A and C Feed: `kscmh`
- `XMEAS(5)` Recycle Flow: `kscmh`
- `XMEAS(7)` Reactor Pressure: `kPa`
- `XMEAS(8)` Reactor Level: `%`
- `XMEAS(9)` Reactor Temperature: `deg C`
- `XMEAS(21)` Reactor Cooling Water Outlet Temperature: `deg C`

Some literature-derived local notes use different labels/units/orderings. Those notes are useful as references but must not define runtime IDs.

## Implementation rule

Create a runtime `VariableRegistry` from the simulator's exported metadata (or its pinned constants if necessary) and expose lookups such as:

```text
registry.get("XMV(10)")
registry.by_kind("XMV")
registry.resolve_index(kind="XMEAS", index=9)
registry.related("XMEAS(9)")
```

The registry should be the only component that translates numeric array indexes to semantic variable identities.

## Test requirement

Add a test that asserts at least all 12 XMV IDs/names against the vendored simulator. A mapping mismatch is a hard test failure because it can cause an otherwise plausible agent to manipulate the wrong actuator.
