# Deterministic Gates v0

Status: proposal  
Version: v0  
Owner repo: `industrial-agent-runtime`

## Goal

Separate model reasoning from execution authority through deterministic, auditable gates. Core runtime gates remain generic; domain-specific safety truth is delegated to consumer-owned validators.

## Gate pipeline

For any requested tool operation:

```text
Model ToolCallRequest
        |
        v
G0 Parse / schema gate
        |
        v
G1 Tool allowlist gate
        |
        v
G2 Budget / recursion gate
        |
        v
G3 Side-effect policy gate
        |
        v
optional consumer/domain validator
        |
        v
optional human approval
        |
        v
execute tool adapter
```

A rejection at any stage prevents execution and produces a structured `GateDecision` trace event.

## Tool side-effect classes

v0 proposes:

```text
READ       - inspect external state, no mutation
COMPUTE    - deterministic/local transformation, no external mutation
SIMULATE   - isolated/sandboxed mutation with no reference-world side effect
PROPOSE    - create a candidate change but do not apply it
MUTATE     - change reference/external state
ADMIN      - change policy/runtime configuration or high-authority external state
```

Consumers may refine classes but MUST preserve monotonic authority: child/task permissions cannot silently upgrade themselves.

## `GateDecision`

Required fields:

```text
request_id
decision: ALLOW | DENY | REQUIRE_APPROVAL
stage
reason_code
reason
policy_version
validator_refs?
```

A model-authored rationale is not a gate decision.

## G0 — schema gate

Checks tool name, input schema, output expectations, required identifiers, and parse validity. No side effect occurs before G0 passes.

## G1 — allowlist gate

Checks that the task and current agent/subagent were explicitly granted the tool. Absence means deny.

## G2 — budget/recursion gate

Checks model/tool/subagent/step budgets, recursion depth, and other deterministic task quotas.

## G3 — side-effect policy gate

Default proposal:

- READ/COMPUTE: auto-allow after prior gates unless consumer policy says otherwise;
- SIMULATE: allow only when adapter declares isolation and task policy grants it;
- PROPOSE: allow creation of proposal data but not reference mutation;
- MUTATE: require consumer validator; MAY also require human approval;
- ADMIN: deny by default in v0 unless explicitly enabled by host application.

## Consumer/domain validator contract

Core runtime MAY call a registered deterministic validator owned by the consuming application:

```text
validate(request, task_policy, application_context) -> GateDecision
```

The validator returns only a decision/reason/normalized constraints. It must not depend on model hidden reasoning.

For TEP, this allows `tep-agent-lab`/`tep-sim` to enforce process-specific intervention rules without importing TEP logic into core runtime.

## Human approval

Human approval is optional in v0 and should be represented as a separate gate state rather than a special model turn.

A pending approval MUST freeze the proposed operation and its exact validated parameters; resuming approval must not regenerate them silently.

## Replanning after denial

A denied request MAY be returned to the main agent as structured feedback if budget remains. The runtime MUST cap such loops through existing task budgets; there is no special infinite retry behavior.

## TOCTOU / stale validation

For state-sensitive mutations, consumer validators MAY attach an expected-state/version token. The executor SHOULD reject application if the reference state changed between validation and execution.

This is optional for initial TEP sandbox work but part of the contract to avoid later unsafe assumptions.

## Invariants

- Model text cannot override a gate.
- Unknown policy means deny for side-effecting operations.
- Gate logic is deterministic for identical request/policy/application state.
- Denied operations produce no reference-world side effect.
- Child authority never exceeds explicitly delegated parent/task authority.
- Domain rules remain outside core generic runtime.

## Acceptance tests

1. Invalid schema fails at G0 with no tool call.
2. Valid but unlisted tool fails at G1.
3. Exhausted tool budget fails at G2.
4. READ tool succeeds under allowlist/budget.
5. MUTATE request is held for consumer validation rather than executed directly.
6. Consumer denial is traceable and cannot be overridden by another model message.
7. Child requesting parent-only authority is denied.
8. Optional approval resumes the exact frozen request or is rejected if stale-state validation fails.

## Open questions

- Which approval/policy interface is simplest without tying core runtime to one UI?
- Should `SIMULATE` be a first-class side-effect class or a capability tag on COMPUTE? v0 keeps it explicit because sandbox experimentation is central to intended consumers.
