# P&ID -> Simulation Automation: Current Boundary and Research Plan

## Executive conclusion

A useful part of the pipeline is automatable today, but **arbitrary legacy P&ID -> trustworthy high-fidelity dynamic simulation is not a solved one-click workflow**.

The problem should be decomposed into two different transformations:

```text
A. Drawing / engineering data
        -> machine-readable plant model

B. Machine-readable plant model
        -> executable simulation model
```

Both have existing research and commercial tooling. The reliability and missing-information problems are different.

---

## A. Drawing -> machine-readable plant model

Input may be:

- scanned paper/PDF;
- vector PDF;
- CAD/P&ID authoring export;
- object-oriented engineering database;
- DEXPI/Proteus/DEXPI XML.

Possible automation stages:

```text
image/vector input
    |
    +-> text/tag OCR
    +-> symbol detection/classification
    +-> line/connector extraction
    +-> nozzle/port association
    +-> instrumentation-loop extraction
    +-> topology reconstruction
    +-> engineering-attribute extraction
            |
            v
       semantic plant graph
            |
            v
        DEXPI-like model
```

This is increasingly practical, especially when the source is already structured engineering data rather than a raster scan.

However, legacy drawings remain difficult because of:

- inconsistent symbol libraries;
- drawing quality;
- crossing vs connected lines;
- off-page connectors;
- handwritten/old annotations;
- vendor-specific conventions;
- duplicated or missing tags;
- incomplete attributes;
- differences between drawing intent and actual as-built plant.

Human validation remains important.

---

## DEXPI role

DEXPI should be treated primarily as a **semantic/interoperability representation**, not as a physics simulator.

A machine-readable P&ID model can provide:

- equipment identity;
- piping/connectivity;
- instrumentation;
- engineering attributes;
- topology needed to build a process graph.

It does not automatically provide all equations, thermodynamics, dynamics, controller tuning, or consequence models required for a simulation.

DEXPI 2.0 unifies the plant/P&ID and process/PFD/BFD exchange direction and introduces DEXPI XML. Tool support will transition over time, so version adapters and validation should be explicit.

---

## B. Plant model -> executable simulation

This is a separate model-generation problem.

Conceptually:

```text
semantic plant graph
      |
      v
model enrichment
      |
      +-> equipment model class
      +-> physical properties / property package
      +-> design/operating parameters
      +-> boundary conditions
      +-> initial conditions
      +-> controller logic/tuning
      +-> reaction kinetics
      +-> fidelity choice
      |
      v
simulation model compiler
      |
      +-> Modelica
      +-> custom Python
      +-> DWSIM / CAPE-OPEN adapter
      +-> other process-simulation backend
      |
      v
executable model
      |
      v
validation / calibration
```

Topology alone is insufficient.

---

## What can be generated reliably first?

Do not start with high-fidelity chemical simulation.

Use a fidelity ladder:

### Level 0 — topology only

- equipment nodes;
- streams/pipes;
- sensors/actuators;
- control-loop relationships.

Useful for graph reasoning, path tracing, document retrieval, and HAZOP node enumeration.

### Level 1 — qualitative / logical simulation

- flow possible/not possible;
- valve open/closed/stuck;
- pump running/stopped;
- simple propagation rules;
- control interlocks/state machines.

Useful for control testing and virtual commissioning.

### Level 2 — low-fidelity dynamic simulation

- lumped balances;
- simple pressure/flow/level/temperature dynamics;
- reusable component libraries;
- simplified controller models.

Useful for scenario exploration and many HAZOP-style process deviations.

### Level 3 — calibrated process simulation

- validated thermodynamics;
- equipment sizing/characteristics;
- reaction kinetics;
- operating data calibration;
- detailed controller behavior.

Requires much more engineering information and validation.

### Level 4 — consequence/safety physics

- release/leak;
- dispersion;
- fire;
- explosion;
- relief-system dynamics;
- personnel consequences.

This normally requires additional specialized models. It should not be inferred from a P&ID alone.

---

## Proposed `pid2sim` architecture

```text
                Inputs
  raster PDF / vector / CAD / DEXPI
                  |
                  v
          Ingestion adapters
                  |
                  v
       Drawing/data extraction
                  |
                  v
       Canonical plant graph
                  |
          +-------+-------+
          |               |
          v               v
    graph validator    human review
          |               |
          +-------+-------+
                  |
                  v
          model enrichment
                  |
                  v
        component resolver
                  |
                  v
        simulation compiler
                  |
        +---------+----------+
        |                    |
      Modelica           other backend
        |                    |
        +---------+----------+
                  |
                  v
           executable model
                  |
                  v
        validation benchmark
```

---

## Where agents can help

Agents are useful for **uncertain semantic work**, not for silently inventing missing physics.

Possible agent tasks:

- resolve ambiguous symbol/tag matches;
- propose candidate equipment classes;
- retrieve manuals/datasheets for missing parameters;
- identify inconsistent topology;
- suggest model fidelity based on task;
- propose candidate component models from a library;
- generate a list of unresolved engineering assumptions;
- create validation plans;
- compare generated model behavior against reference data.

All inferred values must carry provenance/confidence and remain reviewable.

Bad pattern:

```text
missing pump curve
-> LLM invents plausible curve
-> simulation silently runs
```

Better pattern:

```text
missing pump curve
-> unresolved parameter
-> retrieve candidate evidence / ask human / use explicitly labelled assumption
-> record provenance
```

---

## Why TEP is the right first benchmark

TEP is valuable because it provides a known reference process with known variables, disturbances, and executable dynamics.

Use it as a **round-trip benchmark**:

```text
known TEP process/simulator
        |
        v
create/obtain canonical process representation
        |
        v
DEXPI/process graph
        |
        v
pid2sim compiler
        |
        v
generated low-fidelity model
        |
        v
compare against known TEP behavior
```

This is much more scientific than starting with an arbitrary industrial drawing where ground truth is unavailable.

Metrics can include:

- topology precision/recall;
- equipment/tag extraction accuracy;
- connectivity accuracy;
- model-compilation success;
- steady-state consistency;
- qualitative response agreement;
- key-variable trajectory error;
- fault/deviation response ordering;
- human corrections required per model.

---

## Recommended project scope

### `pid2sim` MVP

Start from **machine-readable input**, not OCR.

1. DEXPI/process graph input;
2. canonical internal graph;
3. schema/topology validation;
4. component-model library;
5. low-fidelity Modelica or Python generation;
6. generated-model execution;
7. comparison with TEP reference behavior;
8. explicit unresolved-parameter report.

### Second milestone

Add vector/raster P&ID digitization:

1. text/symbol/line extraction;
2. graph reconstruction;
3. DEXPI normalization;
4. human correction UI;
5. feed corrected graph into the already-tested model compiler.

This order prevents computer-vision errors from being confused with simulation-model-generation errors.

---

## Human-in-the-loop checkpoints

A realistic workflow should have explicit review gates:

```text
P&ID extraction
    -> topology review

semantic graph
    -> tag/equipment review

model enrichment
    -> assumptions/parameter review

generated simulation
    -> steady-state/behavior validation

safety use
    -> domain-expert acceptance
```

The long-term goal is to **reduce human engineering effort and focus review on unresolved/low-confidence items**, not to hide humans from the workflow.

---

## Relationship to the other repos

- `pid2sim` creates/validates simulation-ready models or process graphs.
- `tep-sim` is the first trusted benchmark environment and remains hand-curated around TEP.
- `tep-agent-lab` evaluates agents inside trusted environments.
- `industrial-agent-runtime` supplies generic reasoning/subagent machinery.

Do not block the agent-playground work on `pid2sim`; it is a parallel, longer-horizon research line.
