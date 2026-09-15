# Roadmap — TEP Agent Lab

The lab roadmap is experiment-first. It should produce a meaningful RCA result as early as possible, then add HAZOP/recovery and more agent capabilities as controlled ablations.

Canonical specs live in `docs/specs/`.

## Phase 0 — Reproducible lab shell

Deliver:

- pinned `tep-sim` and `industrial-agent-runtime` revisions;
- versioned experiment fixture schema;
- run/artifact directory policy;
- evaluator-only vs agent-visible fixture projection;
- run manifest and trace completeness checks.

Spec: `docs/specs/evaluation-v0.md`

Exit: one fake/minimal experiment can be created, projected, traced, and deterministically re-scored without exposing hidden truth.

## Phase 1 — Tool surface v0

Branch: `feat/tool-surface-v0`  
Spec: `docs/specs/tool-surface-v0.md`

Deliver:

- observation/history tools;
- process-topology/binding tools;
- snapshot/fork/rollout tools;
- capability/safety query tools;
- proposal/validation adapter skeleton;
- domain experiment-budget policy;
- hidden-truth isolation tests.

Exit: a generic runtime agent can inspect and simulate TEP only through typed lab tools.

## Phase 2 — RCA v0: single agent first

Branch: `exp/rca-reactor-v0`  
Spec: `docs/specs/rca-v0.md`

Start with reactor/cooling-water scenario family. Exact hidden disturbance/timing/magnitude remain fixture choices selected for useful diagnosability.

Run ablations progressively:

```text
B1 static compact context only
B2 + read telemetry
B3 + topology
B4 + counterfactual simulation
```

Do not enable subagents yet in the first pass.

Exit: at least one blind incident can be investigated end-to-end; scorer validates root-cause output, evidence refs, tool/simulation usage, cost, and unsupported claims.

## Phase 3 — Dynamic subagent ablation

Enable the v0 runtime subagent policy on the **same RCA cases**.

Compare B5 (counterfactual + bounded subagents) against B4.

Measure:

- diagnosis quality;
- rollout efficiency;
- tokens/model calls;
- latency;
- redundant queries;
- quality of delegated evidence;
- whether subagents actually reduce parent context pressure.

Exit: keep/adjust subagent policy only with measured evidence. Multi-agent complexity is not assumed beneficial.

## Phase 4 — Simulation-backed HAZOP v0

Branch: `exp/hazop-reactor-v0`  
Spec: `docs/specs/hazop-v0.md`

Scope only reactor + cooling subsystem initially.

Deliver:

- bounded node/parameter/guide-word cases;
- deterministic capability/scenario compilation path;
- supported and deliberately unsupported cases;
- rollout/safety evidence references;
- structured HAZOP findings;
- campaign budget enforcement.

Exit: at least one supported and one unsupported deviation are handled honestly and reproducibly.

## Phase 5 — Recovery v0

Branch: `exp/recovery-reactor-v0`  
Spec: `docs/specs/recovery-v0.md`

Deliver:

- allowed action space per fixture;
- candidate strategy generation;
- forked evaluation + no-action baseline;
- deterministic candidate metric vector;
- layered policy/capability gate;
- post-action verification contract.

Initially it is acceptable to rank strategies without applying them to the reference branch. Enable reference application only after gate tests pass.

Exit: recovery candidates can be compared reproducibly against deterministic/no-action baselines, and one gated application path is testable when enabled.

## Phase 6 — Optional knowledge augmentation

Connect `manufacturing-kg-agent` only after clean baselines exist.

Run with/without evidence retrieval on identical cases. Score evidence correctness, task quality, context/tokens, and whether retrieval changes tool/experiment choices.

## Phase 7 — Freeze benchmark suite

Once fixtures/tracing/scoring are stable, freeze representative packs across RCA, HAZOP, recovery, subagent/no-subagent, and optional knowledge conditions.

Publish machine-readable run manifests and report schemas so future models/runtime versions can be compared without changing the underlying benchmark.

## Not on the critical path

- P&ID OCR/model generation;
- 3D visualization;
- long-term agent memory;
- recursive agent swarms;
- plant-wide HAZOP coverage;
- formal deployment control authority.
