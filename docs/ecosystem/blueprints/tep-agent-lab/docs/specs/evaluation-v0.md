# Evaluation v0

Status: proposal  
Version: v0  
Owner repo: `tep-agent-lab`

## Goal

Make agent experiments reproducible, ablatable, and resistant to accidental ground-truth leakage or cherry-picked success cases.

## Experiment fixture

Each benchmark case SHOULD be represented by a versioned fixture with evaluator-only and agent-visible sections.

Conceptually:

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
simulation_budget
recovery_policy?
scoring_config
```

The fixture itself is evaluator-owned. A function builds the agent-visible task projection.

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
seed
policy/spec versions
start/end timestamps
```

## Trace completeness

A run is invalid for quantitative comparison if required tracing is missing for model calls, tool calls, subagent spawns, gate decisions, or rollout artifact refs.

## Metric families

### Task quality

Depends on task family:

- RCA correctness/top-k/evidence validity;
- HAZOP support classification/evidence-backed consequence quality;
- recovery success/safety/recovery-time metrics.

### Agent behavior

- model calls;
- tool calls by class;
- topology/history query count;
- subagents spawned;
- delegation depth;
- duplicate/redundant calls;
- denied/invalid requests;
- unsupported capability requests;
- retries/replans.

### Resource efficiency

- input/output tokens;
- model latency;
- tool/simulation latency;
- number and total horizon of counterfactual rollouts;
- cost when provider accounting is available.

### Safety/authority behavior

- direct mutation attempts;
- gate rejection rate;
- policy violations attempted;
- unsupported physics claimed as fact;
- stale/invalid validation-token attempts;
- shutdown/safety metrics for applied recovery runs.

## Baseline matrix

Do not compare only "agent" vs "nothing". Recommended ablation ladder:

```text
B0 deterministic/no-agent baseline
B1 LLM with static compact context only
B2 main agent + read telemetry tools
B3 B2 + topology/DEXPI tools
B4 B3 + counterfactual simulation
B5 B4 + bounded dynamic subagents
B6 optional B5 + external knowledge evidence
```

For recovery tasks, add deterministic recovery-controller baseline and no-action branch.

## Randomization / robustness

Where possible, benchmark over multiple seeds, fault magnitudes/times, and equivalent scenario variants so the model cannot succeed only by memorizing one canonical TEP prompt.

Scenario generation MUST remain deterministic given fixture/seed.

## Ground-truth leakage checks

Automated tests SHOULD inspect agent-visible fixtures/tools for prohibited fields such as hidden disturbance ID or evaluator-only labels.

Prompt/context snapshots MAY be retained privately for audit, subject to provider/data policies.

## Evidence reference validation

Any agent claim scored as evidence-backed must reference a tool result or artifact that exists in the trace. The scorer should distinguish valid ref, irrelevant ref, unsupported narrative claim, and missing ref.

## Statistical reporting

Early MVP reports may be descriptive. Once enough cases/seeds exist, report confidence intervals or appropriate uncertainty rather than only point estimates.

Do not claim broad agent superiority from one hand-picked scenario.

## Reproducibility bundle

A report SHOULD make it possible to reconstruct:

- exact case fixture;
- code revisions;
- model configuration;
- runtime policy/budgets;
- environment seeds;
- tool traces/artifacts;
- scorer version;
- final metrics.

## v0 first benchmark suite

Start small:

1. one healthy/reference case;
2. 2–3 reactor/cooling-water RCA variants;
3. a small supported/unsupported HAZOP deviation set;
4. one recovery case with multiple candidate actions.

Expand coverage only after tracing/scoring are reliable.

## Invariants

- Evaluator has access to truth; agent does not unless explicitly configured.
- Same trace is scored deterministically by the same scorer version.
- Ablations change one meaningful capability at a time where practical.
- Failure runs remain in datasets/reports rather than being silently discarded.
- Model output does not define its own score.

## Acceptance criteria

1. Execute one case under at least three ablations with identical environment seed/fixture.
2. Verify hidden-truth leakage test passes.
3. Produce a machine-readable run summary with task, behavior, cost, and safety metrics.
4. Validate every evidence ref in final agent output.
5. Re-score an existing trace and obtain identical metrics.
6. Generate a concise human-readable comparison report from saved run artifacts.
