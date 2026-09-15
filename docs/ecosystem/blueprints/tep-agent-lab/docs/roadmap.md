# Roadmap

## Phase 0 — Pin dependencies and experiment schema

Create reproducible experiment metadata:

```text
scenario_id
seed
tep_sim_revision
agent_runtime_revision
model_config
tool_policy
budget
ground_truth (hidden from agent)
```

Implement report/artifact layout before running many experiments.

## Phase 1 — Read-only diagnosis baseline

Expose observation/history/metadata tools.

Run selected IDV scenarios with:

- deterministic baseline;
- single agent;
- no subagents;
- no counterfactual forks.

Measure diagnosis quality and token/latency cost.

## Phase 2 — Counterfactual RCA

Add snapshot/fork/rollout tools.

Evaluate whether the agent can select useful experiments rather than brute-force all faults.

Metrics:

- final diagnosis rank/accuracy;
- number of forks;
- simulated horizon;
- model/tool calls;
- tokens;
- time.

## Phase 3 — Dynamic subagents

Allow bounded workers for independent hypothesis/signal/evidence tasks.

Run ablation against the same tasks with subagents disabled.

Do not assume multi-agent is better; require measurable gain.

## Phase 4 — Simulation-backed HAZOP MVP

Start with a small curated set of TEP nodes and parameters.

Implement:

- guide-word candidate generation;
- environment capability check;
- deterministic deviation compilation;
- branch rollout;
- safety/process consequence report;
- structured HAZOP table output.

Score:

- valid deviation coverage;
- unsupported-case honesty;
- observed consequence correctness;
- duplicated/low-value scenarios;
- environment rollouts and token cost.

## Phase 5 — Recovery/mitigation sandbox

Generate bounded candidate strategies and test them in forks.

Compare:

- no action;
- deterministic recovery baseline;
- agent recommendation without simulation;
- agent recommendation with counterfactual simulation.

## Phase 6 — Knowledge augmentation

Connect `manufacturing-kg-agent` through a read-only evidence adapter.

Ablate with/without retrieval and evaluate citation/evidence correctness, not just answer quality.

## Phase 7 — Benchmark suite

Freeze representative scenario packs and produce repeatable reports for:

- RCA;
- HAZOP;
- recovery;
- subagent value;
- token/context efficiency;
- safety-policy compliance.

Publish result schemas and run manifests so later models/runtimes can be compared without changing the environment benchmark.
