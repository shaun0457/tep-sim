# Open Questions — `tep-agent-lab`

## OQ-1 — First RCA ground-truth disturbance

Use reactor cooling-water family for the first benchmark, but exact IDV/magnitude/timing should be chosen only after baseline trajectories and distinguishability are measured.

Avoid a case that is either trivially identifiable from one signal or impossible to discriminate under available TEP physics.

## OQ-2 — Incident trigger source

Should RCA begin from a deterministic detector-generated incident, or from a fixture-provided investigation start time?

Default for first benchmark: fixture-provided start point plus compact abnormal-signal summary, so detector quality does not confound agent investigation quality. Add detector-trigger experiments later.

## OQ-3 — Main-agent planning style

Do we require an explicit plan before tool use or allow free ReAct-style iteration?

Default: do not require verbose plans. Tool calls and subtask reasons already provide traceable intent. Test an explicit short-plan condition later as an ablation.

## OQ-4 — Subagent trigger policy

Should main agent freely decide when to spawn within budget, or should the host expose recommended triggers?

Default: agent chooses within deterministic limits. Compare against no-subagent and fixed-parallel-hypothesis baselines.

## OQ-5 — Simulation experiment API granularity

Should an agent specify raw TEP interventions or higher-level semantic scenarios?

Default: prefer semantic deviation/scenario contracts when deterministic mappings exist; allow bounded low-level XMV/IDV controls only through explicit experiment tools.

## OQ-6 — Recovery authority

Should the first recovery benchmark actually apply an agent-selected action to the reference branch, or only rank forked strategies?

Default: first prove candidate-generation/evaluation in forks; enable reference application only after domain gates and verification tests pass.

## OQ-7 — Deterministic domain-policy limits

Exact values for max XMV delta, cooldowns, allowed actuators, and verification windows must be derived per experiment from simulator behavior, not invented globally.

## OQ-8 — HAZOP scope and terminology

How closely should v0 mimic formal IEC HAZOP worksheets versus focus on simulation-backed deviation experiments?

Default: preserve node/parameter/guide-word/deviation/cause/consequence/safeguard structure, but clearly label the system as research support rather than formal HAZOP completion.

## OQ-9 — Knowledge service timing

When should `manufacturing-kg-agent` enter the benchmark?

Default: after a clean no-KG baseline exists, so the contribution of document/knowledge retrieval can be measured as an ablation.

## OQ-10 — Model choice

Model/provider is an experiment dimension, not an architecture dependency. First implementation should support one reliable model through the generic runtime, then freeze model/version per benchmark run.

## OQ-11 — Long-term agent memory

No cross-incident learned memory in initial benchmarks. Add only as a separately evaluated capability after single-run behavior is understood.

## OQ-12 — Visualization

A 2D process graph + telemetry + branch timeline is sufficient for v0. Do not introduce Blender/Omniverse/3D until it supports a concrete research question such as spatial reasoning.
