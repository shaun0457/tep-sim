# DEXPI Integration for the Tennessee Eastman Sandbox

## Decision

Use DEXPI Process / a curated DEXPI 2.0-compatible TEP process representation as the **static engineering-semantic layer** for the Tennessee Eastman sandbox.

Do not build P&ID OCR, symbol detection, line detection, or generic P&ID-to-simulation generation as part of the core TEP/agent project.

The TEP simulator already provides the executable dynamics. DEXPI is used to give humans and agents a structured description of process topology and semantics.

## Why this is practical

The DEXPI Process 1.0 supporting material includes a `TennesseeEastman.xml` example process. More recent 2026 work on `bpmn2dexpi` also uses the Tennessee Eastman process as a reference case and can generate schema-valid DEXPI 2.0 XML.

This means TEP does not need a drawing-recognition pipeline merely to obtain a process graph.

## Separation of concerns

```text
DEXPI / process graph
    |
    | static semantics
    | - process steps
    | - streams
    | - connectivity
    | - materials / parameters where available
    | - measurement/control concepts where represented
    v
TEP semantic binding
    |
    | canonical mappings
    | - graph entity -> simulator variable(s)
    | - simulator variable -> graph entity
    | - XMEAS / XMV / IDV metadata
    v
TEP simulator
    |
    | executable dynamics
    | - disturbances
    | - controller behavior
    | - trajectories
    | - shutdown
    v
telemetry / snapshots / forks / rollouts
```

DEXPI does **not** replace the simulator and is not treated as the source of process dynamics.

## Initial deliverables

### 1. Acquire a machine-readable TEP representation

Preferred order:

1. official/example Tennessee Eastman DEXPI Process material;
2. DEXPI 2.0 TEP example produced by the open-source `bpmn2dexpi` reference implementation;
3. only if necessary, curate a small internal TEP DEXPI/process-graph fixture manually.

No OCR.

### 2. Normalize into a small internal topology model

The runtime should not force every consumer to understand the full DEXPI schema.

Expose a compact read-only model such as:

```python
ProcessGraph
  nodes: list[ProcessNode]
  streams: list[ProcessStream]
  sensors: list[VariableBinding]
  actuators: list[VariableBinding]
```

DEXPI remains the interchange/source representation; the compact graph is the environment-facing query model.

### 3. Build the TEP binding registry

Example conceptual mappings:

```text
Reactor
  measurements:
    XMEAS(7)  reactor pressure
    XMEAS(8)  reactor level
    XMEAS(9)  reactor temperature
    XMEAS(21) reactor cooling-water outlet temperature
  actuator:
    XMV(10)   reactor cooling-water flow
  related disturbances:
    IDV(4)    reactor cooling-water inlet temperature
    IDV(11)   random reactor cooling-water inlet temperature
    IDV(14)   reactor cooling-water valve sticking
```

The simulator registry remains the runtime source of truth for IDs and units. The DEXPI binding references those canonical entries rather than duplicating them in prompts.

### 4. Expose topology queries

Useful read-only APIs for agents and UI:

```text
get_process_nodes()
get_neighbors(node)
get_upstream(node)
get_downstream(node)
get_measurements(node)
get_actuators(node)
get_related_disturbances(node)
trace_stream(source, sink)
```

These are environment/tool APIs, not LLM reasoning.

### 5. Start with 2D visualization

Generate a simple process graph/PFD-like view from the semantic model:

- process units;
- streams;
- selected XMEAS/XMV overlays;
- alarms/incidents;
- optional agent experiment branches.

Do not make 3D reconstruction a dependency for agent research.

## Role in the agent lab

The agent should be able to combine two kinds of evidence:

```text
STRUCTURE
"What is connected to the reactor?"
"Which actuator influences this subsystem?"

DYNAMICS
"What changed during the last five minutes?"
"What happens if I fork this state and inject IDV(4)?"
```

This produces a much more useful industrial playground than raw time-series alone, without requiring P&ID computer vision.

## Example agent investigation

```text
incident: reactor temperature rising
        |
        v
query topology
  reactor -> cooling-water loop -> XMV(10)
        |
        v
query recent telemetry
  XMEAS(9), XMEAS(21), XMV(10)
        |
        v
form hypotheses
  cooling-water disturbance vs kinetics drift
        |
        v
fork simulator
  rollout hypothesis A
  rollout hypothesis B
        |
        v
compare trajectories
        |
        v
report diagnosis / propose bounded recovery experiment
```

The key research object is the **agent's investigation policy**, not diagram extraction.

## Non-goals

- raster P&ID OCR;
- YOLO/U-Net symbol recognition;
- generic arbitrary-plant DEXPI extraction;
- automatic high-fidelity model generation from DEXPI;
- photorealistic 3D reconstruction;
- replacement of engineering validation.

## References

- DEXPI Process Specification 1.0 manual and Tennessee Eastman example process.
- DEXPI Specification 2.0.
- Khella et al. (2026), *Representing DEXPI Process in BPMN 2.0 for graphical modeling and exchange of block flow and process flow diagrams*.
- `skhella/bpmn2dexpi` open-source reference implementation.
