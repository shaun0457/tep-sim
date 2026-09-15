# Evaluation v0

Status: accepted direction / v0 contract proposal  
Owner repo: `tep-agent-lab`

## Goal

Make agent experiments reproducible, ablatable, resistant to ground-truth leakage, and capable of evaluating not only final correctness but **how the Agent investigated the problem**.

## Experiment fixture

Each benchmark case SHOULD be versioned with evaluator-only and agent-visible sections:

```text
case_id
case_version
seed(s)
environment_config
reference_run_setup
hidden_ground_truth
agent_visible_projection
tool_policy
subagent_policy
orchestration_policy
simulation_budget
recovery_policy?
scoring_config
```

The fixture is evaluator-owned. A deterministic projection function builds agent-visible input.

## Run identity

Every run MUST record:

```text
run_id
case_id/version
tep-sim revision
upstream simulator revision
industrial-agent-runtime revision
tep-agent-lab revision
model/provider/model version
prompt/template version
orchestration mode
rule/tool-bridge versions
seed
policy/spec versions
start/end timestamps
```

## Trace completeness

A run is invalid for quantitative comparison if required tracing is missing for model calls, plan/DAG revisions, tool calls, subagent spawns, gate decisions, experiment refs, rollout artifacts, or final evidence refs.

## Metric families

### E0 — Environment validity

- same-seed reproducibility;
- snapshot/fork isolation;
- hidden-truth fixture correctness;
- simulation/tool artifact completeness;
- supported/unsupported capability classification.

### E1 — Runtime / gate behavior

- invalid schema/tool requests blocked;
- permission/budget enforcement;
- Dynamic DAG validation failures;
- mutation attempts denied/approved correctly;
- stale-state/revision errors;
- verifier evidence/artifact checks;
- termination reason correctness.

### E2 — Task quality

Task-specific metrics:

- RCA top-1/top-k diagnosis correctness;
- hypothesis ranking/calibration;
- evidence validity/relevance;
- HAZOP simulability classification and consequence evidence;
- recovery success/safety/recovery-time/production metrics;
- AutoResearch best-candidate performance/generalization.

### E3 — Investigation / scientific behavior

Measure whether the Agent performs useful engineering investigation rather than simply consuming budget.

Candidate metrics:

```text
relevant evidence query rate
irrelevant query rate
hypotheses proposed
hypotheses supported/rejected
hypotheses eliminated per experiment
experiments linked to explicit hypothesis/question
experiment discrimination score
information gain proxy per rollout
redundant experiment rate
duplicate experiment rate
unsupported experiment request rate
useful evidence per model/tool call
belief/rank change after informative evidence
open-question resolution rate
stop efficiency after sufficient evidence
```

Not every metric must be used in every study. Each benchmark freezes the subset/formula before runs.

#### Information-value proxy

For RCA, a practical deterministic proxy MAY score an experiment by how much it separates predicted/observed outcomes across competing hypotheses or how much it changes correct-hypothesis rank, normalized by rollout cost.

Do not call this formal Shannon information gain unless the probability model supports that interpretation.

### E4 — Agent/runtime efficiency

- model calls;
- input/output tokens;
- tool calls by class;
- topology/history/analysis calls;
- subagents spawned and depth;
- Dynamic DAG node count/revisions/parallel width;
- number/total horizon of counterfactual rollouts;
- simulation/tool/model latency;
- provider cost when available;
- context size/ref materialization volume.

### E5 — Safety / authority behavior

- direct mutation attempts;
- gate rejection rate;
- policy violations attempted;
- unsupported physics claimed as fact;
- stale/invalid validation-token attempts;
- hidden-ground-truth access attempts;
- shutdown/safety metrics for recovery runs.

## Two orthogonal ablation matrices

### Capability ablation

This tests what information/tools create value while holding orchestration as fixed as practical.

```text
C0 deterministic/no-agent baseline
C1 static compact LLM context only
C2 + read telemetry tools
C3 + topology/DEXPI tools
C4 + Tool Bridge analysis tools
C5 + counterfactual simulation
C6 + bounded subagents
C7 + rule/knowledge evidence
C8 + AutoResearch/search tools where task-appropriate
```

### Orchestration architecture ablation

This tests how the same capabilities are orchestrated.

```text
O0 static one-shot LLM
O1 local ReAct-style Main Agent
O2 fixed deterministic DAG/workflow
O3 Hybrid: deterministic macro + local ReAct
O4 Hybrid + model-proposed Dynamic DAG
O5 O4 + bounded ephemeral subagents
O6 Hybrid AutoProcessResearch mode (task-specific)
```

Not every combination must be run. Use a fractional study design that isolates the research question without combinatorial explosion.

## Dynamic DAG metrics

When enabled, record:

- proposed plans;
- rejected plans and reasons;
- plan revisions;
- node types/count/dependencies;
- parallelism actually used;
- failed/skipped nodes;
- merge quality/evidence coverage;
- plan overhead relative to direct ReAct.

## Subagent metrics

Record:

- reason for delegation;
- unique vs duplicate work;
- context size per child;
- evidence accepted/ignored by parent;
- incremental quality gain;
- token/tool/latency overhead;
- whether a simpler parent-only path would have sufficed.

The objective is not to maximize subagent usage; a good Main Agent should learn when **not** to delegate.

## AutoResearch evaluation

For each campaign report:

- baseline score;
- best dev/research score;
- hidden-eval score;
- trials to first/best improvement;
- accept/reject/neutral/failure counts;
- plateau length;
- duplicate/repeated idea rate;
- optimizer trials versus Agent research turns;
- total simulation/model/tool budget;
- constraint/safety violations attempted;
- robustness across scenarios/seeds;
- accepted-strategy complexity.

## Randomization / robustness

Benchmark over multiple seeds, disturbance magnitudes/times, and scenario variants when feasible. Scenario generation is deterministic given fixture/seed.

The first benchmark suite SHOULD include difficulty tiers based on measured distinguishability, not subjective labels alone.

## Ground-truth leakage checks

Automated tests SHOULD inspect:

- agent-visible fixture projection;
- registered tools;
- Information Plane refs/visibility;
- Rule Registry entries;
- prompts/context snapshots;

for prohibited hidden disturbance IDs/evaluator labels.

## Evidence reference validation

Any claim scored as evidence-backed must reference an existing visible evidence/tool/artifact result in the trace. The scorer distinguishes:

```text
VALID_RELEVANT_REF
VALID_BUT_IRRELEVANT_REF
MISSING_REF
HIDDEN_REF_VIOLATION
UNSUPPORTED_NARRATIVE_CLAIM
```

## Semantic stopping evaluation

Beyond hard budget exhaustion, measure whether the Agent stops appropriately when evidence becomes sufficient.

Record:

- extra low-value calls after correct stable diagnosis;
- premature conclusion before required evidence;
- unresolved critical question count at finish;
- marginal value of final N actions.

## Statistical reporting

Early MVP reports may be descriptive. Once enough cases/seeds/repeats exist, report uncertainty/confidence intervals or paired comparisons rather than only point estimates.

Repeated stochastic model runs SHOULD be used when evaluating architecture differences large enough to be affected by model sampling.

## Benchmark-overfitting protection

Separate:

```text
DEVELOPMENT fixtures — used while building/debugging
RESEARCH fixtures — allowed feedback for experiments
HIDDEN EVALUATION fixtures — final evaluator-only comparison
```

Do not claim general improvement from repeated optimization on the visible benchmark alone.

## Reproducibility bundle

A report SHOULD reconstruct:

- exact case fixture;
- code revisions;
- model configuration;
- orchestration/tool/rule policies;
- environment seeds;
- Investigation State revisions;
- Dynamic DAG revisions;
- tool/subagent/rollout artifacts;
- scorer versions;
- final metrics.

## v0 first benchmark suite

Start small:

1. one healthy/reference case;
2. 2–3 reactor/cooling-water RCA variants with measured distinguishability;
3. a small supported/unsupported HAZOP deviation set;
4. one recovery case with multiple candidate strategies;
5. one bounded AutoProcessResearch campaign after recovery scoring is stable.

## Invariants

- Evaluator has truth; Agent does not unless explicitly configured.
- Same saved trace is scored deterministically by the same scorer version.
- Capability and orchestration ablations are not conflated in the same comparison unless intentionally designed.
- Failure runs remain in datasets/reports.
- Model output does not define its own score.
- Scientific-behavior metrics are frozen per benchmark version before comparison.

## Acceptance criteria

1. Execute one case under at least three capability ablations with identical fixture/seed.
2. Execute at least two orchestration modes over the same capability set.
3. Verify hidden-truth leakage tests.
4. Produce machine-readable task, scientific-behavior, efficiency, and safety metrics.
5. Validate every final evidence ref.
6. Re-score a saved trace identically.
7. Generate a human-readable comparison report that separates final correctness from investigation efficiency/quality.
