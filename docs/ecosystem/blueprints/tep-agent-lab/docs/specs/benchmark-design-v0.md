# Benchmark Design and Identifiability v0

Status: v0 contract proposal  
Owner repo: `tep-agent-lab`

## Goal

Create benchmark cases that test investigation capability rather than memorization, trivial signal lookup, or impossible discrimination.

## Core principle

A case is useful only if its hidden cause/task is:

- reproducible;
- supported by TEP physics;
- not directly leaked;
- meaningfully distinguishable from plausible alternatives under the allowed evidence/tools;
- not trivially solved by one hard-coded variable/fault label unless the benchmark explicitly targets that baseline.

## Benchmark partitions

```text
DEVELOPMENT
  visible cases used for engineering/debugging

RESEARCH
  cases used for architecture/tool/policy experiments and AutoResearch feedback

HIDDEN_EVAL
  evaluator-only cases/variants used for final generalization comparison
```

Case IDs/configs from hidden evaluation must not enter Agent/AutoResearch context.

## Scenario family contract

```text
ScenarioFamily
  family_id
  subsystem
  candidate_causes[]
  observable_variables[]
  controllable_variables[]
  supported_interventions[]
  nuisance_variation
  seed_space
  timing_range
  magnitude_range
  operating_conditions
  exclusions
```

A family generates versioned deterministic fixtures from a seed/config.

## First family

Start with reactor/cooling-water behavior because topology and simulator relationships are known enough to build a controlled benchmark.

Candidate causes should include at least two plausible alternatives where the simulator supports meaningful comparison, rather than a single isolated fault label.

Exact candidates/magnitudes/timing are selected after pilot trajectory analysis.

## Identifiability pilot

Before an Agent benchmark is frozen, run a deterministic pilot campaign.

For each candidate cause/variant:

1. generate reference trajectories over multiple seeds/operating variants;
2. compute task-relevant response features;
3. compare pairwise trajectory/feature separability;
4. identify confounded/near-identical cases;
5. verify allowed tools contain enough evidence to distinguish at least a useful subset;
6. verify no single hidden metadata field leaks truth.

Candidate deterministic features may include:

- direction/magnitude of selected responses;
- onset/lag relationships;
- transient/steady-state features;
- cross-correlation/lag;
- PCA/PLS baseline features;
- safety/shutdown behavior;
- topology distance/affected subsystem patterns.

These are diagnostic tools for benchmark design, not necessarily Agent inputs.

## Difficulty tiers

Difficulty labels should be data-informed.

Possible factors:

```text
signal-to-noise / random variation
number of plausible alternatives
trajectory separability
amount of initial visible context
tool budget
simulation budget
onset timing/magnitude
single vs interacting deviations
```

Suggested initial tiers:

- EASY: distinguishable with targeted read/topology evidence;
- MEDIUM: requires at least one useful analysis/counterfactual experiment;
- HARD: multiple plausible causes/variants, tighter budget, or weakly separated trajectories.

Do not freeze thresholds until pilot data exists.

## Memorization resistance

TEP is a public benchmark and model pretraining may include common fault descriptions.

Mitigations:

- do not score fault-name recall alone;
- vary seed/timing/magnitude/operating context;
- require evidence refs and experiment traces;
- include plausible alternative hypotheses;
- include simulator-supported scenario variants not identical to textbook prompts;
- score scientific behavior and efficiency;
- maintain hidden fixture variants;
- optionally use semantic case IDs rather than exposing canonical IDV labels to the Agent.

Known prior knowledge is not itself cheating; the benchmark asks whether the Agent can validate/use it against current evidence.

## Healthy / negative cases

Include healthy/no-fault or benign variation cases to measure false investigation/overdiagnosis behavior.

Agent should be allowed to conclude insufficient evidence/no abnormal root cause when justified.

## Unsupported cases

For HAZOP/capability evaluation, include requests outside TEP physics. Correct behavior is explicit unsupported classification, not invented simulation.

## Repeats and stochasticity

Environment seeds are deterministic. LLM runs may remain stochastic.

For architecture comparisons:

- pair cases/seeds across conditions;
- freeze model/version/settings;
- repeat stochastic Agent conditions enough to estimate variance when material;
- retain all failures;
- avoid cherry-picking successful traces.

## Benchmark evolution

Benchmark versions are immutable once used for reported comparisons.

New cases/bug fixes create a new version and preserve historical results.

## Leakage audit

Before freezing a benchmark version, automated/manual audit checks:

- fixture projection;
- registered tools;
- ProcessGraph/RuleRegistry visibility;
- artifact metadata;
- filenames/IDs;
- prompts/system context;
- experiment ledger;

for hidden answer leakage.

## Acceptance criteria

1. Generate at least three variants in the first scenario family reproducibly.
2. Pilot pairwise distinguishability with deterministic analysis.
3. Identify and exclude/relabel at least one trivial/confounded case if found.
4. Build one healthy negative fixture.
5. Prove hidden ground truth is absent from Agent-visible projection/tools.
6. Run the same frozen fixture under two Agent architectures and one deterministic baseline.
7. Preserve a hidden-eval variant unavailable to AutoResearch/Agent feedback.
