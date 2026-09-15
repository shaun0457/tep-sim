# Development Workflow — Spec First, Small Branches

## Goal

Make human + coding-agent development predictable. A branch should have one bounded architectural purpose and an explicit acceptance target.

## Branch types

Use these prefixes across the three core repositories:

```text
spec/<topic>        documentation/specification only
adr/<topic>         architecture decision only
feat/<topic>        product/runtime implementation
exp/<task>-<case>   benchmark/experiment implementation
fix/<topic>         bug/correctness fix
refactor/<topic>    behavior-preserving structural change
```

Avoid broad branches such as `agent-improvements`, `new-architecture`, or `everything-v2`.

## Spec-before-code rule

A new externally visible contract or major runtime behavior SHOULD have an accepted/proposed spec before implementation.

Typical flow:

```text
issue/question
 -> spec/<topic>
 -> review assumptions/open questions
 -> merge/accept spec
 -> feat/<topic>
 -> tests against acceptance criteria
 -> merge
```

For exploratory research, an `exp/...` branch may precede a final spec, but experimental code must not silently become core API without a later contract/ADR.

## Branch scope template

Every branch/PR description should answer:

```text
Problem
What is in scope?
What is explicitly out of scope?
Canonical spec/ADR links
Files/modules expected to change
Acceptance tests / exit criteria
Known risks/open questions
```

## Coding-agent task prompt template

Give Codex/Claude Code a narrow instruction such as:

```text
Implement docs/specs/snapshot-fork-replay-v0.md.
Scope only Phase A2: snapshot + isolated fork + tests.
Do not add agent/LLM dependencies.
Do not redesign public contracts without updating the spec first.
Run the acceptance tests named in the spec and report any upstream limitation explicitly.
```

This is preferable to pasting the entire program architecture into each session.

## Spec change during implementation

If implementation reveals the spec is wrong:

1. stop treating the old requirement as authoritative;
2. document the observed constraint/evidence;
3. update the proposal spec or create an ADR;
4. then align code/tests.

Do not quietly code around the spec while leaving documentation false.

## PR size policy

Prefer branches that can be understood from one core spec and a small number of modules. Split when a PR mixes two independently testable concerns, for example:

- snapshot/fork and DEXPI parsing;
- generic runtime gates and TEP safety policy;
- RCA workflow and HAZOP campaign logic.

## Tests by document type

- Spec PR: lint/links/manual consistency; no runtime implementation required.
- Feature PR: acceptance tests from its canonical spec.
- Experiment PR: fixture reproducibility + trace/scorer tests.
- Refactor PR: existing behavior/tests unchanged.

## Merge order across repos

Downstream work pins released/merged upstream revisions.

```text
tep-sim contract/feature
        ↓
industrial-agent-runtime contract/feature  (independent where possible)
        ↓
tep-agent-lab adapter/experiment pins both
```

Do not make `tep-sim` depend on a lab branch just to unblock an experiment.

## Suggested initial branch sequence

### `tep-sim`

```text
feat/environment-api-v0
feat/snapshot-fork-v0
feat/dexpi-binding-v0
feat/capability-safety-v0
```

### `industrial-agent-runtime`

```text
feat/contracts-executor-v0
feat/deterministic-gates-v0
feat/subagents-v0
feat/provider-adapter-v0
```

### `tep-agent-lab`

```text
feat/tool-surface-v0
exp/rca-reactor-v0
exp/hazop-reactor-v0
exp/recovery-reactor-v0
```

The exact order inside independent repos can overlap, but `tep-agent-lab` should not outrun the contracts it consumes.

## Definition of done for a feature branch

A feature is done when:

- canonical spec acceptance criteria pass;
- errors/unsupported paths are tested;
- provenance/traces required by the spec exist;
- README/roadmap links remain correct;
- no out-of-scope dependency leaked into the repo;
- known gaps are captured in `open-questions.md` or an issue rather than left in chat history.
