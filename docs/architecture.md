# Architecture: Hybrid TEP Simulation + Agent Runtime

## Decision

Use a **hybrid runtime**:

- the Tennessee Eastman Process simulator, sampling, safety checks, detectors, action gates, and state transitions are deterministic Python;
- the LLM is invoked only on event-driven slow paths that require diagnosis, explanation, or recovery planning;
- LangGraph may orchestrate that slow path when persistence, retries, human approval, or multi-step reasoning become useful;
- CLI coding agents such as Codex CLI / Claude Code are development harnesses, not online controllers.

This design minimizes token use, latency, and agent failure surface while keeping the LLM focused on the part that actually benefits from reasoning.

---

## Why not use a CLI coding agent as the runtime?

A coding agent is optimized for repository work: inspect files, run commands, edit code, test, and iterate. It generally carries broader context and a much more capable tool surface than a plant controller needs.

Using it directly in the TEP loop would create several problems:

- excessive context and token use;
- unpredictable latency relative to the simulation clock;
- unnecessary filesystem/shell permissions;
- poor separation between reasoning and control authority;
- difficult reproducibility;
- hard-to-test hidden agent loops.

Use coding agents to **build and maintain** this repository. Keep the runtime narrow and explicit.

---

## Why not put the whole runtime in LangGraph?

LangGraph is useful for stateful, long-running workflows, but the TEP plant loop is fundamentally a deterministic numerical process. A graph node per simulation tick would add orchestration overhead without adding intelligence.

The recommended boundary is:

```text
FAST PATH (no LLM)

TEPSimulator.step()
      |
      v
ObservationSnapshot
      |
      v
rolling features / detector bank / safety rules
      |
      +---- healthy ----> record + next step
      |
      v
IncidentEvent

SLOW PATH (LLM optional)

IncidentEvent
      |
      v
context builder
      |
      v
[LangGraph or simple FSM]
 diagnose -> propose -> validate -> apply -> verify
                 |          |
                 |          +---- deterministic gate
                 |
                 +--------------- structured LLM output
```

A plain Python finite-state machine should be enough for the first milestone. Introduce LangGraph when at least one of these becomes necessary:

- durable checkpoint/resume;
- human approval interrupts;
- multi-step diagnosis/recovery with explicit retries;
- multiple reasoning branches that need stateful coordination;
- production tracing around agent state transitions.

Do not introduce it merely to have an "agent framework".

---

## Core runtime states

Keep the control runtime small and observable.

```text
NORMAL
  |
  | detector/alarm
  v
INCIDENT_OPEN
  |
  | context ready
  v
DIAGNOSING
  |
  | structured proposal
  v
VALIDATING
  |\
  | \ rejected
  |  v
  | SAFE_HOLD / HUMAN_REVIEW
  |
  | approved
  v
ACTING
  |
  v
VERIFYING
  |\
  | \ recovered -> NORMAL
  |
  +---- failed -> DIAGNOSING (bounded retry)
             \
              -> SAFE_HOLD when retry budget exhausted
```

The transition function should be deterministic. The model supplies information used by transitions; it does not decide arbitrary next nodes.

---

## Data contracts

### ObservationSnapshot

One simulator sample. Keep raw numerical state available to deterministic code, but do not automatically send it to the LLM.

Suggested fields:

```python
@dataclass(frozen=True)
class ObservationSnapshot:
    run_id: str
    step: int
    sim_time_s: float
    xmeas: tuple[float, ...]   # 41 values
    xmv: tuple[float, ...]     # 12 values
    shutdown: bool
```

### IncidentEvent

Produced by deterministic detectors.

```python
@dataclass(frozen=True)
class IncidentEvent:
    incident_id: str
    run_id: str
    opened_at_step: int
    severity: str
    detector_ids: tuple[str, ...]
    abnormal_variables: tuple[str, ...]
    evidence: dict
```

`evidence` should contain compact numeric facts such as z-score, slope, duration, safety margin, or residual; not generated prose.

### IncidentContext

The only object sent to the reasoning agent.

It should contain:

- the incident metadata;
- selected abnormal XMEAS values;
- only the XMV variables related to those measurements/subsystems;
- short-window features such as current, mean, slope, min/max, delta;
- deterministic detector outputs;
- safety margins;
- recent actions/outcomes;
- allowed control targets and constraints;
- retrieved domain facts for relevant variables/equipment.

Do not include the complete process history by default.

### ActionProposal

The model may propose, but cannot execute.

```python
@dataclass(frozen=True)
class ActionProposal:
    target: str          # canonical id, e.g. "XMV(10)"
    mode: str            # "delta" or "absolute"
    value: float
    rationale: str
    expected_effect: str
    verify_after_s: int
    confidence: float
```

### GateDecision

Pure deterministic output.

```python
@dataclass(frozen=True)
class GateDecision:
    approved: bool
    normalized_target: str | None
    normalized_value: float | None
    reasons: tuple[str, ...]
```

---

## Deterministic gates

The LLM must never bypass these.

### 1. Variable identity gate

Resolve IDs from a canonical registry sourced from the vendored simulator. Do not trust prompt text to define what XMV(10) means.

### 2. Range gate

Reject non-finite values and values outside the actuator range.

For direct valve positions, start with the simulator-valid 0-100% envelope, then tighten per actuator if domain limits are added.

### 3. Delta/rate gate

Limit how much an actuator can move per intervention. This is essential even if the final physical limit is 0-100%.

Example policy shape:

```text
max_abs_delta_per_action[XMV] = configurable value
minimum_seconds_between_actions[XMV] = configurable cooldown
```

Do not encode these values in the prompt; store them in configuration.

### 4. Safety gate

The model must not intentionally cross configured shutdown/safety margins. If the process is already near shutdown, switch to a separately tested safe policy or human review instead of asking the LLM to improvise.

### 5. Permission gate

Each experiment declares which XMV variables are controllable. All others are read-only.

### 6. Duplicate/cooldown gate

Reject repeated proposals that merely oscillate the same variable before the previous action has been evaluated.

### 7. Output/schema gate

Malformed or incomplete model output means `approved=False`. Never infer a missing target or value.

---

## Detector hierarchy

Prefer a cascade so the expensive reasoning layer sees very few events.

### Layer A: hard process/safety rules

Examples:

- simulator shutdown flag;
- pressure/temperature/level safety margins;
- NaN/Inf and sensor validity checks.

### Layer B: cheap temporal rules

Examples:

- sustained deviation from baseline;
- derivative/rate-of-change threshold;
- actuator saturation;
- measurement-actuator inconsistency;
- no-response after an action.

### Layer C: statistical/ML detector

Optional PCA/residual/anomaly detector or the upstream detector plugin interface.

### Layer D: LLM diagnosis

Only run when Layers A-C produce an incident that cannot be handled by a known deterministic policy.

This makes "zero model calls during healthy operation" a testable requirement.

---

## Agent design

Start with **one reasoning agent**, not role-based multi-agent orchestration.

The agent has two responsibilities:

1. diagnose the likely process/control cause using the compact incident context;
2. return one or a small number of ranked `ActionProposal`s.

Avoid permanent roles such as Supervisor, Data Engineer, Data Scientist, and Machine Expert inside this runtime. Those roles are useful for research on agent collaboration, but here they create handoffs, duplicated context, and token overhead.

If later needed, spawn temporary subagents only for clearly independent tasks, for example:

- one agent checks process-document evidence;
- one agent evaluates alternative recovery hypotheses;
- a final node compares already-structured outputs.

Do not let subagents converse freely. Parent passes bounded inputs and receives bounded outputs.

---

## Context minimization

The context builder is more important than the prompt.

### Bad

```text
Send all 41 XMEAS + 12 XMV for the last 60 minutes + papers + previous chat history.
```

### Better

```text
Incident: reactor temperature rising for 90 s
XMEAS(9): current / baseline / slope / z-score
XMEAS(7): pressure current / slope
XMEAS(21): reactor CW outlet current / slope
XMV(10): current position / last action
IDV metadata: hidden during blind diagnosis
Relevant process relation: XMV(10) is reactor cooling-water flow
Safety margins: reactor temperature / pressure
Allowed action: XMV(10), max delta configured by gate
```

The reduction from raw history to features should be deterministic.

---

## Canonical variable registry

A registry should be constructed from the vendored simulator's metadata/constants and exposed to the rest of the application.

It should provide at least:

```text
canonical ID
index
name
kind (XMEAS/XMV/IDV)
unit
process area / equipment tag
control relationship(s), when curated
```

Important: the current vendored simulator defines the manipulated-variable sequence as:

```text
XMV(1)  D Feed Flow
XMV(2)  E Feed Flow
XMV(3)  A Feed Flow
XMV(4)  A and C Feed Flow
XMV(5)  Compressor Recycle Valve
XMV(6)  Purge Valve
XMV(7)  Separator Pot Liquid Flow
XMV(8)  Stripper Liquid Product Flow
XMV(9)  Stripper Steam Valve
XMV(10) Reactor Cooling Water Flow
XMV(11) Condenser Cooling Water Flow
XMV(12) Agitator Speed
```

Do not allow duplicated handwritten mappings to diverge from this source.

---

## Control strategy for experiments

### Baseline A: built-in closed loop

Run `ControlMode.CLOSED_LOOP` with no agent. This is the conventional baseline.

### Baseline B: manual mode + deterministic controller

Use `ControlMode.MANUAL` and reproduce selected control behavior through explicit controller code. This validates the wrapper and action-gate path without any LLM.

### Agent experiment

Use manual/custom control with:

```text
deterministic nominal controller
       +
agent intervention channel for incident recovery
```

This is preferable to asking an LLM to continuously replace every PI loop. The agent should initially supervise or intervene, not become a millisecond/second-level process controller.

---

## Verification before/after action

An action is not successful merely because the LLM produced a plausible explanation.

For each approved action, record a verification contract:

```text
target variable(s)
expected direction
verification horizon
tolerance / recovery criterion
```

After the horizon:

- if the expected trend occurs and safety margins improve, close or continue monitoring;
- if not, mark the proposal ineffective;
- only then allow a bounded retry/re-diagnosis;
- after the retry budget, enter safe hold/human review.

This gives the agent a feedback loop without free-form self-reflection.

---

## Run trace

Every experiment should save enough information to replay what happened:

```text
run_id
seed
upstream simulator commit
control mode
fault/disturbance schedule
sampling configuration
detector configuration
agent model + prompt/config version
incident contexts (or hashes + persisted artifacts)
raw model structured outputs
gate decisions
applied actions
verification outcomes
shutdown/final status
token usage and model latency
```

Token count and model latency are first-class experiment metrics.

---

## Visualization boundary

Visualization consumes the same state/event stream as logging.

Suggested stages:

1. simple process dashboard with time-series plots, alarms, active incidents, and actuator positions;
2. 2D pipeline/process topology with equipment nodes and stream edges;
3. optional DEXPI/Blender/3D presentation layer.

The dashboard must not talk directly to the simulator's mutation methods. UI control, if later added, should go through the same action gate.

---

## Suggested package layout

```text
src/tep_sim/
  simulation/
    adapter.py
  registry/
    variables.py
  telemetry/
    snapshots.py
    features.py
  detectors/
    safety.py
    temporal.py
  runtime/
    state.py
    engine.py
  agents/
    interface.py
    context_builder.py
    schemas.py
    langgraph_runtime.py      # optional, add when justified
  gates/
    action_gate.py
  control/
    executor.py
    nominal_controller.py
  persistence/
    run_log.py
  ui/
    ...
```

Keep framework-specific code inside `agents/`; the rest of the project should not depend on LangGraph or a particular model provider.

---

## Key tests

At minimum:

1. **healthy-run test:** N simulation steps -> zero LLM calls;
2. **registry test:** XMV IDs/names exactly match upstream metadata;
3. **gate test:** malformed/out-of-range/excess-delta proposal cannot reach `set_mv()`;
4. **closed-loop overwrite test:** document/test that direct MV intervention is not used in `CLOSED_LOOP`;
5. **incident-context test:** only allowlisted/relevant variables enter agent context;
6. **recovery-loop test:** failed action has bounded retries then safe hold;
7. **reproducibility test:** same seed/config produces the same pre-agent simulation trace;
8. **trace completeness test:** every applied action has source incident, proposal, gate decision, and outcome.

---

## Rule of thumb

If a decision can be written as a stable `if`, formula, schema, finite-state transition, lookup, threshold, or bounded optimizer, keep it out of the LLM.

Use the LLM for ambiguous diagnosis, hypothesis ranking, explanation, and choosing among constrained recovery options.
