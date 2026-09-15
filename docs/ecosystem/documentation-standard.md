# Documentation Standard

This program uses a small set of document types so architecture decisions do not drift between README files, coding-agent instructions, and implementation notes.

## Document types

### `README.md`
Purpose, audience, scope, quick architecture, repository map, and links. It should stay readable by a new contributor and must not become a detailed implementation specification.

### `docs/architecture.md`
Stable component boundaries, ownership, dependency direction, and major runtime flows. Architecture documents describe *where responsibilities live*, not every field or method.

### `docs/specs/*.md`
Testable contracts. A spec should define inputs, outputs, invariants, error behavior, acceptance criteria, and explicit non-goals. Specifications may begin as `v0 proposal` and graduate to `accepted`.

### `docs/decisions/ADR-*.md`
Architecture Decision Records. ADRs explain why a choice was made, alternatives considered, consequences, and whether the decision is reversible.

### `docs/open-questions.md`
Questions that materially affect architecture or experiments but are not yet resolved. An unresolved item must not silently become a dependency assumption.

### `docs/roadmap.md`
Implementation order and exit criteria. Roadmaps point to specs; they do not redefine contracts.

### `AGENTS.md` / `CLAUDE.md`
Minimal repository-local instructions for coding agents. These files may summarize architecture invariants but must link to canonical docs rather than duplicate long specifications.

## Spec status

Every spec starts with metadata:

```text
Status: proposal | accepted | deprecated
Version: v0, v1, ...
Owner repo: ...
Depends on: ...
```

`proposal` means implementation may explore the contract but callers must not rely on long-term stability.

`accepted` means tests and implementation should conform to it; incompatible changes require a version change or ADR.

## Requirement language

Use:

- **MUST / MUST NOT** for invariants;
- **SHOULD / SHOULD NOT** for strong defaults;
- **MAY** for optional behavior.

## Definition of done for a spec

A spec is ready for implementation when it has:

1. scope and non-goals;
2. named contracts/schemas;
3. happy-path behavior;
4. failure/error behavior;
5. deterministic invariants;
6. observability/provenance requirements where relevant;
7. acceptance tests or measurable exit criteria;
8. open questions isolated at the end rather than embedded as hidden assumptions.

## Cross-repository rule

Public contracts must be owned by exactly one repository.

Examples:

- `Snapshot` semantics are owned by `tep-sim`.
- generic `Task`/`Budget` semantics are owned by `industrial-agent-runtime`.
- TEP-specific `IncidentCase`/`HazopFinding` experiment semantics are owned by `tep-agent-lab`.

A downstream repo may adapt an upstream contract but must not redefine its meaning.

## Duplication rule

When the same statement exists in more than one document, one location must be declared canonical and the others should link/summarize. This is especially important for `AGENTS.md`, `CLAUDE.md`, and README files because duplicated constraints create coding-agent context drift.
