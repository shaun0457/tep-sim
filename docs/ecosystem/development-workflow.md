# Development Workflow — Spec First, Small Branches

## Goal

Make human + coding-agent development predictable. A branch has one bounded purpose, one owning contract, explicit dependencies, and measurable acceptance criteria.

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

## Design Freeze rule

Current program state after independent review:

- `tep-sim` A1–A4 may begin independently because their contracts are self-contained;
- `industrial-agent-runtime` and `tep-agent-lab` feature implementation remains held until the focused post-adjudication re-review closes BLOCKER/implementation-defining MAJOR contradictions.

Do not treat an existing roadmap/branch name as authorization to start held work.

## Spec-before-code rule

A new externally visible contract or major runtime behavior SHOULD have an owning proposal/accepted spec before implementation.

Typical flow:

```text
issue/question
 -> spec/<topic>
 -> review assumptions/open questions
 -> focused independent review when architecture-defining
 -> accept/proceed
 -> feat/<topic>
 -> tests against acceptance criteria
 -> merge
```

For exploratory research, an `exp/...` branch may precede a final contract, but experimental behavior must not silently become core API.

## Branch scope template

Every branch/PR should state:

```text
Problem
In scope
Explicitly out of scope
Canonical spec/ADR links
Dependencies / required upstream revisions
Owned files/modules
Acceptance tests / exit criteria
Known risks/open questions
```

## Coding-agent task prompt template

Give Codex/Claude Code a narrow instruction such as:

```text
Implement docs/specs/snapshot-fork-replay-v0.md.
Scope only Phase A2: snapshot + isolated fork + tests.
Do not add agent/LLM dependencies.
Do not redesign public contracts without first reporting SPEC_CONFLICT.
Run the acceptance tests named in the spec and report upstream limitations explicitly.
```

Do not paste the entire program architecture into every implementation session when a canonical spec already exists.

## `SPEC_CONFLICT` rule

If implementation evidence shows the canonical spec is wrong/ambiguous:

1. stop treating the conflicting requirement as authoritative;
2. report `SPEC_CONFLICT` with observed evidence and affected contract;
3. update/review the proposal spec or ADR;
4. only then align implementation/tests.

Do not silently invent replacement architecture in code.

## PR size policy

Prefer branches understandable from one primary spec and a small set of modules. Split work when it mixes independently testable concerns, for example:

- snapshot/fork and DEXPI parsing;
- generic runtime gates and TEP policy;
- RCA benchmark construction and HAZOP workflow;
- Tool Bridge adapter implementation and benchmark scorer changes.

## Tests by document/branch type

- Spec PR: links/status/manual consistency; no runtime implementation required.
- Feature PR: canonical spec acceptance tests + negative/error paths.
- Experiment PR: fixture reproducibility + leakage + trace/scorer tests.
- Refactor PR: behavior/tests unchanged.

## Cross-repository dependency rule

Downstream work pins known upstream revisions/contracts.

```text
tep-sim contract/feature
        ↓
industrial-agent-runtime contract/feature  (independent where possible)
        ↓
tep-agent-lab adapter/experiment pins both
```

Never make `tep-sim` depend on lab/runtime just to unblock an experiment.

## Current branch sequence

### `tep-sim` — may start now

```text
feat/environment-api-v0
feat/snapshot-fork-v0
feat/dexpi-binding-v0
feat/capability-safety-v0
```

### `industrial-agent-runtime` — after focused re-review

```text
feat/contracts-runtime-v0
feat/deterministic-gates-v0
feat/subagents-v0
feat/provider-adapter-v0
```

Post-execution verification is part of the runtime core/gate integration, not a separate Agent/service branch unless implementation size justifies a small module PR.

Not scheduled in v0:

```text
feat/langgraph-adapter-v0
full Dynamic DAG engine
MCP runtime dependency
```

### `tep-agent-lab` — after focused re-review

```text
feat/investigation-state-v0
feat/rule-registry-v0
feat/hypothesis-experiment-v0
feat/tool-surface-v0
feat/tool-bridge-v0
exp/rca-benchmark-pilot-v0
exp/rca-reactor-v0
exp/orchestration-ablation-v0
```

Later only after RCA contracts/evaluation stabilize:

```text
exp/hazop-reactor-v0
exp/recovery-reactor-v0
exp/autoresearch-recovery-v0
```

## Parallel coding-agent policy

After a held phase is released, independent branches MAY run in parallel when:

- dependencies are explicit;
- file/module ownership does not overlap materially;
- public contracts are already frozen for that work;
- each agent has its own branch/worktree;
- acceptance tests are explicit;
- handoff is compact/structured.

Follow `development-agent-orchestration.md` for coordination/integration.

## Definition of done for a feature branch

A feature is done when:

- canonical spec acceptance criteria pass;
- failure/unsupported/security paths are tested;
- required provenance/traces exist;
- no hidden domain dependency leaked across repo boundaries;
- README/architecture/roadmap links remain consistent;
- no stale/superseded contract remains in AGENTS/CLAUDE instructions;
- known empirical gaps are captured in `open-questions.md`/issue rather than chat history;
- any implementation-discovered contract change passed the `SPEC_CONFLICT` flow.
