# pid2sim

Research toolkit for converting process-engineering representations into validated executable simulation models, with explicit human review where engineering information is missing or ambiguous.

## Long-term vision

```text
P&ID / engineering data
      -> semantic plant model
      -> enriched simulation graph
      -> executable model
      -> validation report
```

The project does **not** assume that a P&ID contains enough information for a trustworthy high-fidelity simulation.

## MVP scope

Start from machine-readable input:

- DEXPI/process-model data;
- curated graph fixtures;
- TEP-derived reference topology.

Do not start with OCR. First prove that a clean semantic plant graph can be validated, enriched, compiled, executed, and compared against a ground-truth process.

## Fidelity ladder

```text
L0 topology graph
L1 qualitative/logical model
L2 low-fidelity dynamic model
L3 calibrated process model
L4 consequence/safety-physics models
```

The MVP targets L1/L2.

## Core pipeline

```text
Input Adapter
   |
   v
Canonical Plant Graph
   |
   v
Schema + Topology Validator
   |
   v
Enrichment / Missing-Data Report
   |
   v
Component Model Resolver
   |
   v
Simulation Compiler
   |
   +-> Modelica backend (initial candidate)
   +-> simple Python backend for tests
   |
   v
Executable Model
   |
   v
Validation / Comparison Report
```

## Human-in-the-loop principle

Missing engineering facts remain explicit unresolved facts.

The system may:

- retrieve evidence;
- propose candidates;
- estimate confidence;
- allow an explicitly labelled assumption.

It must not silently invent:

- thermodynamic packages;
- equipment curves;
- reaction kinetics;
- controller tuning;
- design parameters.

## DEXPI strategy

Support a versioned canonical adapter rather than coupling the whole codebase to one serializer/library version.

Conceptually:

```text
DEXPI 1.x / Proteus ----\
                         -> canonical graph
DEXPI 2.0 XML ----------/
```

The canonical graph should preserve source provenance for every extracted/converted object.

## Why use TEP first?

TEP supplies a known process and executable simulator, which makes model-generation validation possible.

Initial benchmark:

```text
known TEP topology/semantics
-> canonical graph
-> generated low-fidelity model
-> execute standard scenarios
-> compare with tep-sim reference behavior
```

This creates measurable progress before introducing noisy industrial drawings.

## Later drawing digitization track

After the graph-to-simulation compiler works:

```text
scan/vector P&ID
-> OCR + symbol detection + line extraction
-> connectivity reconstruction
-> tag/equipment resolution
-> DEXPI/canonical graph
-> human correction
-> existing compiler pipeline
```

## Suggested layout

```text
src/pid2sim/
  ingestion/
  dexpi/
  graph/
  validation/
  enrichment/
  models/
  compiler/
    modelica/
    python/
  benchmark/

fixtures/
  dexpi/
  tep/
  pid_images/

tests/
docs/
AGENTS.md
```

## Success metric

The goal is not "generated code runs". The goal is:

- traceable source semantics;
- correct topology;
- explicit missing data;
- compilable model;
- behavior agreement appropriate to the chosen fidelity;
- low human correction effort;
- no hidden hallucinated engineering parameters.
