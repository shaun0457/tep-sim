# Tool Bridge v0

Status: accepted direction / v0 contract proposal  
Owner repo: `tep-agent-lab`

## Goal

Reuse mature open-source scientific/process-analysis libraries through narrow typed tools instead of reimplementing statistics, signal processing, dimensionality reduction, sensitivity analysis, optimization, and graph algorithms inside the agent runtime.

The Agent sees stable domain-oriented tool contracts. Library APIs remain behind adapters.

## Design principle

Correct:

```text
Main Agent
 -> typed tool request
 -> Tool Bridge adapter
 -> pinned open-source library/function
 -> normalized structured result + provenance
```

Incorrect:

```text
Main Agent
 -> arbitrary Python/shell/import
 -> install/call any package dynamically
```

The bridge is an allowlisted deterministic capability layer, not unrestricted code execution.

## Why bridge instead of rewrite

Many useful operations already exist in mature libraries and/or the upstream TEP simulator. Reusing them reduces implementation risk and lets the research focus on whether the Agent selects and interprets tools well.

External-library correctness is still bounded by our input assumptions; a mature statistical function does not automatically make an Agent conclusion correct.

## Candidate sources

### Existing TEP simulator capabilities

Prefer upstream-native implementations when they match the task and canonical data representation, including existing threshold/statistical/fault-detector plugins such as PCA/EWMA/CUSUM where available.

Bridge these through stable lab tools rather than copying detector implementations.

### Scientific Python

Candidate libraries behind adapters:

- NumPy / pandas — deterministic numeric/tabular transforms;
- SciPy — signal processing, cross-correlation/lag, filtering, statistical/optimization routines;
- statsmodels — time-series/statistical tests such as Granger non-causality tests;
- scikit-learn — PCA/PLS/ICA/scaling/clustering/model utilities where benchmark-appropriate;
- NetworkX or equivalent — graph algorithms over normalized ProcessGraph data;
- SALib — Sobol/Morris/FAST and other sensitivity-analysis workflows;
- Optuna — bounded numerical/hyperparameter optimization trials;
- additional libraries only after a concrete tool contract/evaluation need exists.

No library is a mandatory dependency merely because it appears in this candidate list. Versions and licenses must be reviewed/pinned when a bridge becomes active.

## Initial tool families

### Signal/statistical analysis

```text
analyze_summary_statistics(data_ref, variables, window)
analyze_cross_correlation(data_ref, x, y, lag_range)
analyze_change_point_or_cusum(...)
analyze_pca(...)
analyze_pls(...)
analyze_granger_noncausality(...)
```

`analyze_granger_noncausality` MUST describe its result as a statistical predictive-temporal test, not proof of physical causality.

### Trajectory comparison

```text
compare_trajectories(reference_ref, candidate_ref, variables, metrics)
compute_lag_alignment(...)
compute_response_features(...)
```

Candidate features may include direction, peak, settling time, integrated error, lag, correlation, and normalized trajectory distance.

### Sensitivity / design of experiments

```text
run_sensitivity_analysis(
    method,
    parameter_space,
    simulation_callable_ref,
    output_metric,
    budget
)
```

The adapter coordinates sampled inputs with isolated TEP rollouts and returns indices/results as artifacts.

### Numerical optimization

```text
optimize_parameters(
    search_space,
    objective_ref,
    constraints,
    method,
    trial_budget,
    seed
)
```

The Agent chooses the question/search variables/bounds/objective. The optimizer selects numeric candidates according to a pinned method.

### Graph analysis

```text
find_paths(source_node, target_node, constraints?)
get_upstream_subgraph(node, depth)
get_downstream_subgraph(node, depth)
find_control_paths(node)
```

These operate on the normalized TEP ProcessGraph, not directly on raw DEXPI objects.

## Tool Bridge adapter contract

```text
BridgeToolSpec
  tool_name
  semantic_version
  input_schema
  output_schema
  implementation_id
  library_name
  library_version
  allowed_functions
  deterministic_seed_policy?
  timeout/resource_limits
  side_effect_class
  provenance_fields
```

Each call returns:

```text
BridgeToolResult
  request_id
  status
  summary
  structured_result
  artifact_refs[]
  implementation/library versions
  input_refs
  seed/config
  warnings
  provenance
```

## Input/data policy

Adapters MUST:

- validate variable IDs/units/schema;
- materialize only required data windows;
- reject evaluator-only/hidden fields;
- normalize missing/NaN handling explicitly;
- record preprocessing/scaling;
- avoid silently changing sampling frequency/alignment;
- return dense arrays through artifacts rather than model context.

## Determinism / reproducibility

For deterministic algorithms, identical input refs/config/library version must reproduce the same result within documented tolerance.

For stochastic algorithms:

- seed is explicit;
- sampler/algorithm version is recorded;
- parallel nondeterminism is documented.

## Security and dependency boundary

The bridge MUST NOT expose:

- arbitrary `eval`/`exec`;
- arbitrary Python module import;
- package installation by model request;
- filesystem/network access beyond the specific adapter contract;
- raw function names supplied by the model unless allowlisted in the tool schema.

## Agent interpretation boundary

Tool outputs are evidence, not automatic conclusions.

Examples:

- high correlation does not prove causality;
- PCA components do not automatically identify root cause;
- Granger test does not establish physical causal mechanism;
- optimizer optimum is valid only under its objective/search space/scenario distribution.

Rule Registry / ProcessGraph evidence should be used to interpret results.

## Build-vs-bridge rule

Bridge when:

- a mature implementation exists;
- the semantic contract can be narrowed;
- version/provenance can be controlled;
- result can be deterministically validated/normalized.

Implement locally when:

- behavior is TEP-specific domain glue;
- external API is too broad/unstable;
- correctness depends on our own canonical semantics;
- the operation is trivial enough that a dependency adds more risk than value.

## Initial recommended bridge set

For the first RCA/AutoResearch milestones:

1. upstream TEP detector bridge;
2. SciPy cross-correlation/lag + response-feature bridge;
3. scikit-learn PCA/PLS bridge where useful for baselines;
4. SALib sensitivity bridge for parameter/mechanism exploration;
5. Optuna optimization bridge for bounded numeric search;
6. graph algorithms over ProcessGraph.

Add statsmodels time-series tests as an optional analysis tool after stationarity/preprocessing policies are explicit.

## Acceptance tests

1. Cross-correlation tool returns result + lag + pinned library provenance from a known fixture.
2. PCA bridge processes only agent-visible data and returns artifact-backed components/statistics.
3. Optimization bridge cannot alter objective/evaluator code during a study.
4. SALib-style sensitivity workflow generates samples, executes isolated rollouts, and returns reproducible indices with fixed seed/config.
5. Attempted arbitrary Python/import request has no bridge path.
6. Changing a bridge implementation/library version changes the recorded tool version in experiment provenance.
