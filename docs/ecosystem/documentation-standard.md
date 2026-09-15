# Documentation Standard

This program uses a small set of document types so architecture decisions do not drift between README files, coding-agent instructions, implementation notes, and experiments.

## Document types

### `README.md`
Purpose, audience, scope, quick architecture, repository map, and links. It summarizes; it does not redefine detailed contracts.

### `docs/architecture.md`
Stable component boundaries, ownership, dependency direction, and major runtime flows. Architecture documents describe where responsibilities live; field-level semantics belong in specs.

### `docs/specs/*.md`
Testable contracts: inputs, outputs, invariants, error behavior, observability/provenance, acceptance tests, and explicit non-goals/open research.

### `docs/decisions/ADR-*.md`
Architecture Decision Records explain why a choice was made, alternatives, consequences, current status, and revisit trigger.

### `docs/open-questions.md`
Only genuinely unresolved empirical/implementation questions. A settled architecture decision must not remain "open" in another document.

### `docs/roadmap.md`
Implementation/research order and exit criteria. Roadmaps point to canonical specs; they do not invent/redefine contracts.

### `AGENTS.md` / `CLAUDE.md`
Minimal repository-local instructions for coding agents. They summarize hard boundaries and link to canonical docs rather than duplicating long semantics.

### Review/adjudication records
Files such as `design-review-adjudication.md` record external findings and disposition. They are evidence/history, not replacement specs.

## Spec status vocabulary

Every spec uses exactly one:

```text
Status: proposal | accepted | deprecated
Version: v0, v1, ...
Owner repo: ...
Depends on: ...   # when useful
```

Definitions:

- `proposal` — sufficiently explicit for review/prototyping; public callers must not assume long-term stability;
- `accepted` — implementation/tests should conform; incompatible semantic changes require a version change and/or ADR;
- `deprecated` — retained for history/migration but no longer authoritative.

Do not use hybrid phrases such as:

```text
accepted direction / proposal
accepted working policy
implemented later under Design Freeze
```

Put architecture-decision status in the ADR/Decision Register and contract maturity in the spec status.

## ADR status vocabulary

Use exactly one:

```text
Status: proposed | accepted | superseded | deprecated
```

- `proposed` — decision under active review;
- `accepted` — current architecture decision;
- `superseded` — replaced by a newer named ADR/decision; retained for history;
- `deprecated` — intentionally retired without a direct replacement.

A superseded ADR must identify its replacement where applicable.

## Decision Register status

The program Decision Register may additionally distinguish:

- accepted scope/architecture decisions;
- proposals/defaults awaiting empirical tuning;
- accepted directions for later research.

Decision status is not empirical evidence of superiority. For example, an accepted Hybrid implementation contract does not imply Hybrid outperforms ReAct.

## Requirement language

Use:

- **MUST / MUST NOT** for invariants;
- **SHOULD / SHOULD NOT** for strong defaults;
- **MAY** for optional behavior.

## Definition of done for a spec

A spec is implementation-ready when it has:

1. scope/non-goals;
2. named owned contracts/schemas;
3. happy-path behavior;
4. failure/error behavior;
5. deterministic invariants;
6. observability/provenance/resource-accounting requirements where relevant;
7. acceptance tests/measurable exit criteria;
8. cross-repo interface ownership where relevant;
9. unresolved empirical questions isolated from required contract semantics.

## Cross-repository ownership rule

A public contract is owned by exactly one repository.

Examples:

- `Snapshot` semantics — `tep-sim`;
- generic `InformationRef`, `Task`, `Budget`, `ToolSpec`, `TaskStateStore`, `WorkBatch` — `industrial-agent-runtime`;
- `RcaState`, `CausalClaim`, `Prediction`, TEP lab policy/scoring — `tep-agent-lab`.

A downstream repo may implement/adapt an upstream interface but must not redefine its generic meaning.

## Duplication rule

When the same statement appears in multiple documents, one location is canonical and the others summarize/link.

Priority for semantic conflicts:

```text
owning accepted/proposal spec
 -> accepted ADR/Decision Register for architecture rationale/scope
 -> architecture.md summary
 -> roadmap
 -> README / AGENTS / CLAUDE summary
```

If two owning specs contradict each other at a cross-repo boundary, that is a `SPEC_CONFLICT`, not something an implementation agent resolves by preference.

## Review rule

For architecture-defining changes:

1. author/update proposal specs;
2. independent reviewer inspects repo/contracts without relying on author chat history;
3. findings are adjudicated;
4. canonical docs are changed;
5. focused re-review verifies BLOCKER/implementation-defining MAJOR closure;
6. only then mark/freeze implementation-ready contracts.

Empirical questions remain open and should be answered by pilots/ablations rather than documentation consensus.
