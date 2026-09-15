# Knowledge and Rule Registry v0

Status: accepted direction / v0 contract proposal  
Owner repo: `tep-agent-lab` with hard environment truth owned by `tep-sim`

## Goal

Convert engineering knowledge into explicit, provenance-preserving machine-usable artifacts without promoting paper text or LLM claims directly into hard execution authority.

The registry separates simulator truth, physical invariants, validated engineering relationships, literature heuristics, and agent hypotheses.

## Knowledge levels

```text
K0 — Simulator/runtime ground truth
K1 — Formal physical/safety invariant with reviewed implementation
K2 — Empirically/simulation-validated engineering relationship
K3 — Literature/document-derived heuristic or candidate relationship
K4 — Agent-generated hypothesis / unvalidated working claim
```

### K0 — simulator truth

Examples:

- canonical XMEAS/XMV/IDV identity;
- simulator-supported bounds/capabilities;
- control-mode behavior;
- shutdown state defined by the vendored implementation.

Owner: `tep-sim`.

Eligible for deterministic BLOCK/ALLOW behavior when the underlying contract is authoritative.

### K1 — formal invariant

Examples:

- explicit unit/range constraints;
- mathematically defined conservation/physical constraints where the model exposes sufficient quantities;
- reviewed safety limits with authoritative source/implementation.

Owner depends on scope; environment invariants belong in `tep-sim`.

Hard enforcement requires explicit source, scope, test coverage, and review.

### K2 — validated relationship

A relationship supported by controlled simulation/experimental evidence over an explicit scope.

Examples:

- response-direction relation validated across selected operating conditions;
- signal lag range validated in a scenario family;
- an actuator-to-measurement sensitivity relation within a tested region.

K2 is not automatically a hard gate. Default enforcement is advisory/scoring unless a separate review promotes it to a formal constraint.

### K3 — literature/document heuristic

Extracted from papers, manuals, SOPs, or expert documents.

K3 may guide retrieval, hypothesis priors, experiment selection, and warnings. It MUST NOT become a hard safety/execution constraint solely because an LLM extracted it.

### K4 — agent hypothesis

Created during an investigation/research session.

K4 is working state only. It can be tested, supported, rejected, or eventually contribute to a K2 promotion campaign.

## Rule contract

```text
Rule
  rule_id
  version
  title
  knowledge_level
  scope
  predicate_or_relation
  inputs[]
  expected_effect_or_constraint?
  enforcement
  source_refs[]
  validation_refs[]
  operating_envelope?
  units?
  confidence_or_support?
  status
  created_by
  reviewed_by?
  created_at
  updated_at
```

## Enforcement classes

```text
BLOCK     reject an operation
ALLOW     explicitly permit under stated scope
WARN      deterministic warning, does not block
SCORE     contribute to ranking/scoring
ANNOTATE  add contextual information/evidence
PRIOR     influence hypothesis prior/attention only
```

Hard execution authority (`BLOCK`/high-authority `ALLOW`) is limited to K0/K1 unless an explicit ADR/review says otherwise.

K2 defaults to WARN/SCORE/ANNOTATE. K3 defaults to ANNOTATE/PRIOR. K4 is not a registry enforcement rule.

## Promotion pipeline

Paper/document text is never directly promoted to a hard rule.

```text
source document
  -> candidate extraction
  -> K3 candidate with provenance
  -> semantic/unit/scope review
  -> design validation campaign
  -> run controlled TEP experiments
  -> collect evidence + failures
  -> validation result
      -> remain K3
      -> reject/deprecate
      -> promote to K2 within explicit operating envelope
```

Promotion to K1 requires stronger formal justification/review than simulation support alone.

## Extraction workflow

LLMs may assist with extracting candidate rules from literature, but extraction output must include:

```text
source_ref
source_location
claim
variables/entities
conditions/assumptions
units
relationship type
uncertainties
candidate knowledge level = K3
```

The extractor has no authority to assign K0/K1/K2.

## Validation campaign

A K3 candidate may define:

```text
ValidationCampaign
  campaign_id
  candidate_rule_ref
  scenarios[]
  operating_points[]
  seeds[]
  expected_relation
  metrics
  pass/fail/tolerance policy
  result_refs[]
```

The campaign evaluator is deterministic where possible.

## Conflict handling

Conflicting rules are preserved, not silently merged.

Conflict records SHOULD identify:

- overlapping scope;
- conflicting expected relation/constraint;
- source/validation strength;
- operating-envelope differences;
- resolution status.

Precedence for execution truth:

```text
K0 simulator contract
> applicable K1 formal invariant
> reviewed policy
> K2 advisory evidence
> K3 heuristic
> K4 hypothesis
```

A higher level does not imply general scientific truth outside its declared scope.

## Versioning and demotion

Rules are versioned. New simulator versions or contradictory validation may:

- narrow operating envelope;
- supersede a rule;
- deprecate it;
- demote K2 back to K3 pending revalidation.

Past experiments keep the exact rule-version refs used.

## Agent access

Suggested typed tools:

```text
query_rules(scope, variables?, level?, enforcement?)
get_rule(rule_id, version?)
get_rule_provenance(rule_ref)
get_rule_validation(rule_ref)
find_rule_conflicts(rule_ref)
```

Agents cannot directly edit rule level/enforcement. They may submit `RuleCandidate` or `ValidationProposal` objects.

## Relationship to deterministic gates

The domain validator may consume K0/K1 hard rules. K2/K3 rules may inform scoring/warnings/context but must not silently become blocking gates.

## Invariants

- LLM extraction never directly creates a hard gate.
- Every K2/K3 rule has source provenance.
- Every K2 promotion has validation evidence and operating scope.
- Rule behavior is versioned and reproducible per experiment.
- Simulator/document disagreements remain visible and simulator runtime truth governs current TEP execution behavior.
- K4 agent hypotheses live in investigation state, not as persistent rules by default.

## Acceptance tests

1. Import a paper-derived relation as K3 with exact source/provenance metadata.
2. Reject an attempt to mark the K3 relation as BLOCK without promotion/review.
3. Run a deterministic validation campaign and promote a passing scoped relation to K2.
4. Record a conflicting candidate without overwriting existing rule history.
5. Domain gate consumes a K0 hard constraint and ignores a K3 heuristic for blocking authority.
6. Re-score an old run using its pinned rule versions.
