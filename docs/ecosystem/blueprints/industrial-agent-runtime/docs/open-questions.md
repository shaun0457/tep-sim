# Open Questions — `industrial-agent-runtime`

## OQ-1 — Real model provider order

v0 core must be provider-agnostic and testable with a fake provider. The first real provider integration is intentionally not locked yet.

Decision criterion: structured tool use, schema reliability, tracing/cost visibility, and ease of local testing.

## OQ-2 — LangGraph introduction threshold

Default: no LangGraph in core MVP.

Introduce only if a concrete consumer requires durable checkpoints, human interrupts, resumable long-running state, or graph-level persistence that the explicit executor cannot reasonably provide.

## OQ-3 — Subagent depth/limit

Proposal default is depth 1 and max 3 children per parent. These values should be changed only based on measured task quality/context/cost, not aesthetics.

## OQ-4 — Verifier semantics

Should verifier/critic be a dedicated runtime primitive or simply another bounded subtask with a verification schema? Default: ordinary subtask until a distinct primitive demonstrates value.

## OQ-5 — Context manager sophistication

How much automatic compression/retrieval belongs in generic runtime versus consumer adapters?

Default: runtime manages references and budgets; domain consumers decide what evidence to retrieve/compact.

## OQ-6 — Memory

No persistent cross-run agent memory in v0. Revisit only after experiments show repeated knowledge/reasoning that cannot be handled by external evidence services or run artifacts.

## OQ-7 — Approval mechanism

Need a provider/UI-neutral interface for pausing a frozen request and later approving/rejecting it without regenerating parameters.

## OQ-8 — Parallel execution

Which executor model should v0 use for parallel read/simulation subtasks: asyncio, thread pool, or sequential reference implementation first?

Default: correctness-first sequential implementation, then add parallelism behind the same contract.
