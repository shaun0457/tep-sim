# Open Questions — `industrial-agent-runtime`

Only unresolved empirical/implementation choices belong here. Current architecture contracts are owned by specs/ADR-002.

## OQ-1 — First real model provider

Core stays provider-agnostic and fake-provider-testable.

Choose the first real adapter based on:

- structured output/tool reliability;
- investigation/planning quality;
- tracing/token/cost visibility;
- deterministic/configuration controls;
- CI/local integration cost.

Provider choice is not architecture.

## OQ-2 — WorkBatch parallel-width default

Semantic contract supports ready-item parallel execution, but v0 may implement sequential scheduling first for correctness.

Open implementation/default choices:

- default `max_parallel_width`;
- asyncio/thread/process/job backend;
- backpressure/timeout behavior.

These must not alter public WorkBatch semantics.

## OQ-3 — Subagent depth/limit

Initial proposal:

```text
max_subagent_depth = 1
max_subagents = 3 cumulative per task
```

Change only from measured quality/context/cost results.

## OQ-4 — Model-based critic subtask

Post-execution Verifier remains deterministic/authoritative for machine-checkable checks.

Open research question: does an optional bounded LLM critic improve semantic completeness enough to justify cost?

If studied:

- it is an ordinary Subtask;
- output is advice/evidence only;
- it cannot override gates/Verifier.

## OQ-5 — Formal semantic stopping / information value

v0 stopping is Agent finish proposal + deterministic structural readiness checks.

Open research:

- explicit probability/belief semantics;
- rank/probability update rule;
- information-value estimator;
- marginal-value stopping threshold.

Do not implement formal information-gain stopping until these semantics exist.

## OQ-6 — Full Dynamic DAG value

v0 uses dependency-aware WorkBatch only.

A richer graph engine is justified only if experiments demonstrate value from features such as:

- in-place plan revisions;
- cancellation of running branches;
- richer graph-specific scheduling;
- durable graph persistence.

If pursued, specify failure/retry/revision semantics before implementation.

## OQ-7 — LangGraph adapter threshold

LangGraph is deferred, not scheduled.

Introduce only after a concrete need for one or more of:

- durable checkpoint/resume;
- human interrupt;
- long-running graph persistence;
- graph-level tooling whose value exceeds adapter cost.

Do not select checkpoint/storage infrastructure before that requirement exists.

## OQ-8 — Authority-escalation UI

Runtime defines only the frozen request/revision-bound approval state contract for enabled high-authority MUTATE paths.

The actual human/SME/UI mechanism may live in CLI/web/API and is not required for first blind RCA.

## OQ-9 — Cross-run learned memory

No automatic cross-run learned memory/retrieval in v0.

Future memory is a consumer capability experiment over Engineering Records/rules, not generic runtime default behavior.
