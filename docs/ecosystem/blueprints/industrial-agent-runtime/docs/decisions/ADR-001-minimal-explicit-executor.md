# ADR-001 — Start with a minimal explicit executor

Status: proposed  
Date: 2026-09-15

## Context

The runtime needs bounded model/tool/subagent orchestration. Frameworks such as LangGraph can provide durable state and interrupts, but the initial requirements are small enough to represent directly.

## Decision

Implement v0 as an explicit Python executor/state machine with typed contracts and deterministic gates. Keep orchestration-framework types out of public contracts.

LangGraph remains an optional adapter introduced only when a consuming workflow demonstrates a concrete need for durable checkpoint/resume, human interrupts, or persistent multi-step branching.

## Consequences

Positive:

- smaller dependency/context surface;
- clearer unit tests and failure semantics;
- easier comparison of agent behavior versus orchestration behavior;
- no framework lock-in in task/tool contracts.

Negative:

- some checkpoint/interrupt features may need later adapter work;
- executor code must still be disciplined about state transitions and traces.

## Alternatives considered

1. LangGraph from day one — rejected for v0 because it adds concepts before requirements justify them.
2. CLI coding agent as runtime — rejected because repository/shell capabilities and broad context are inappropriate for controlled domain execution.
3. Fully autonomous recursive agent swarm — rejected because it is difficult to bound, evaluate, and attribute gains to specific mechanisms.

## Revisit trigger

Revisit after at least one `tep-agent-lab` workflow requires durable resume/human interrupt or after explicit-executor complexity becomes measurably worse than a graph adapter.
