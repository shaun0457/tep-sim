# Architecture

## Pipeline

```text
Source
  |
  v
Input Adapter
  |
  v
Canonical Plant Graph
  |
  +--> Validation Findings
  |
  v
Enrichment Layer
  |
  +--> Missing/Assumption Ledger
  |
  v
Component Model Resolver
  |
  v
Simulation IR
  |
  +--> Compiler: Python
  +--> Compiler: Modelica
  |
  v
Executable Model
  |
  v
Validation Harness
```

## Canonical plant graph

The internal graph should represent at least:

```text
Equipment
Ports / Nozzles
Streams / Piping connections
Valves
Sensors
Actuators
Control relationships
Tags
Engineering attributes
Source provenance
```

Do not encode graphical coordinates as the core semantic identity. Drawing geometry is useful provenance/visualization metadata but distinct from process topology.

## Adapters

### DEXPI adapters

Provide version-specific import/export modules:

```text
dexpi_1x_adapter
DEXPI_2_adapter
```

Both produce the same internal graph contract.

### Drawing adapters — later

Raster/vector recognition produces candidate graph elements with confidence and source bounding geometry. Human corrections become provenance-preserving graph edits.

## Validation layers

### Schema validation

Are required fields/types valid?

### Topology validation

Examples:

- dangling stream endpoints;
- impossible port types;
- disconnected equipment;
- ambiguous line crossing/connection;
- duplicate/conflicting tags.

### Simulation-readiness validation

Does the selected fidelity have enough data?

Examples:

```text
low-fidelity tank:
  volume? initial level? inlet/outlet relation?

pump:
  qualitative on/off may need little data
  hydraulic dynamic model needs curve/parameters

reactor:
  high fidelity requires thermodynamics/kinetics not present in ordinary P&ID topology
```

## Enrichment ledger

Every missing value stays visible:

```text
field
required_for_fidelity
status
value?
source?
confidence?
assumption_id?
reviewer?
```

This is one of the project's most important artifacts.

## Component model library

A component resolver maps semantic equipment to one or more candidate simulation models.

```text
Plant Graph Pump P-101
      |
      v
ModelResolver
      |
      +-> QualitativePump
      +-> SimpleHydraulicPump
      +-> DetailedPumpCurveModel
```

The selected model depends on fidelity goal and available parameters.

## Simulation intermediate representation (IR)

Do not compile directly from DEXPI objects to backend code.

Use an intermediate representation containing:

```text
instances
ports
connections
parameters
initial_conditions
controllers
boundary_conditions
assumptions
source_provenance
```

This allows multiple compilers and makes backend differences testable.

## Compiler backends

### Simple Python backend

Use first for deterministic compiler unit/integration tests and qualitative dynamics.

### Modelica backend

Use for component-based equation modeling and reusable physical model libraries once the IR is stable.

Additional proprietary/open-source process simulators may be adapters later; avoid making MVP depend on licensing/tool installation.

## Validation harness

Generated models are tested at multiple levels:

```text
build/compile
steady-state plausibility
mass/energy invariant checks where available
response direction/order
trajectory comparison against reference
fault/deviation scenario comparison
```

For TEP benchmark cases, `tep-sim` is the reference environment, not a code dependency inside the compiler.

## Human review

Review interfaces should focus attention on:

- low-confidence extraction;
- unresolved topology;
- missing simulation-critical parameters;
- model-class ambiguity;
- explicit assumptions;
- validation failures.

The objective is to automate the easy/high-confidence majority and make the remaining human work explicit and efficient.
