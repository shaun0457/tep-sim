# AGENTS.md

Repository-wide rules for coding agents working on `industrial-agent-runtime`.

## Product boundary

This is a **domain-independent agent harness**. Do not encode TEP, chemical-process, manufacturing, finance, or other domain semantics in core runtime code.

## Canonical specs

Before implementing runtime behavior, read the owning spec:

- `docs/specs/runtime-v0.md`
- `docs/specs/subagents-v0.md`
- `docs/specs/deterministic-gates-v0.md`
- `docs/open-questions.md`
- `docs/decisions/ADR-001-minimal-explicit-executor.md`

If implementation evidence contradicts a proposal spec, update the spec/ADR rather than silently changing semantics.

## Hard rules

1. Prefer deterministic code to LLM calls for validation, permissions, budgeting, serialization, recursion/retry limits, and routing that can be expressed explicitly.
2. Model output is a request/proposal, never execution authority.
3. Subagents are ephemeral child tasks, not permanent role hierarchies.
4. Every child receives explicit goal, context refs, allowed tools, budget, and output schema.
5. v0 defaults: `max_subagent_depth=1`, at most 3 children per parent, child reference-world mutation disabled.
6. Child context is scoped; do not automatically copy the parent transcript/tool set.
7. Child returns compact structured evidence; do not automatically merge hidden child transcripts into parent context.
8. Cap model calls, tool calls, steps, retries, subagent count, and depth deterministically.
9. Invalid structured output and unknown policy fail closed.
10. Model-provider code stays behind interfaces; core tests must run with a deterministic fake provider.
11. LangGraph is optional/later; public contracts must not require LangGraph types.
12. Record model/tool/subagent/gate events with parent-child provenance and budget deltas.
13. No TEP/domain tool implementations in core; consumers register adapters/validators.

## Side-effect path

```text
model ToolCallRequest
 -> schema gate
 -> tool allowlist
 -> budget/recursion gate
 -> generic side-effect gate
 -> optional consumer/domain validator
 -> optional approval
 -> tool adapter
 -> structured ToolResult
```

Do not implement arbitrary agent-generated shell/Python execution as the normal runtime path. A consuming product may register a separately sandboxed code-execution tool under its own policy.

## Testing

At minimum test:

- fake-provider typed task;
- allowed read tool;
- malformed/unknown tool request;
- budget exhaustion;
- consumer-validator denial;
- subagent count/depth limit;
- child mutation denial;
- parent-child trace correctness;
- deterministic replay of fake-provider tests.

Keep this file short; detailed behavior belongs in `docs/specs`, unresolved assumptions in `docs/open-questions.md`, and rationale in ADRs.
