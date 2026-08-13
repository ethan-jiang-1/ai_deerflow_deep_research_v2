## Why

Approved Cognitive Evaluation Suite (CES) requirements forbid a case-linked Rubric as
an execution input, while approved evaluation-hardening (EVH) requirements and current
admission require scenario `review_criteria` to match the declared Rubric. This leaves
two incompatible required-behavior answers for the same admission boundary.

The already selected product decision is narrow: a Rubric identity and its criterion
IDs are case-control-integrity metadata for deterministic admission. Rubric criterion
content, model-facing input, and cognitive quality judgment remain review-only.

## What Changes

- Modify CES to distinguish five concepts: Rubric identity, criterion IDs, criterion
  content, model-facing execution input, and cognitive quality verdict.
- Permit deterministic admission to read the declared Rubric only to validate the
  selected Case identity/version and the set/uniqueness of declared criterion IDs before
  subject construction.
- Prohibit criterion prose, weights, thresholds, evaluator guidance, and cognitive
  judgment from entering a subject fixture, model-facing context, execution output, or
  Runner completion status.
- Modify HITL1, Wave0, Wave1, and Wave2 cognitive-program requirements so their
  existing `review_criteria` fields are explicitly criterion-ID control metadata, not
  an execution-quality rubric.
- Retain the existing Runner's exactly-once behavior, execution statuses, review
  separation, and post-execution review authority. No code, typed contract, fixture,
  test, CONTEXT, ADR, or A-004 diagnostic-retention behavior is changed by this
  planning-authorized change.

## Change Focus

- **Primary module / causal owner:** `openspec/specs/cognitive-evaluation-suite/spec.md`; it owns the current incompatible definition of what may enter a Cognitive Evaluation execution.
- **Seam classification:** deterministic-guardrail - the decision constrains the deterministic Case-admission boundary rather than a model role or human decision.
- **Question:** Which exact Rubric facts may cross from source-controlled review control into deterministic execution admission without making Rubric content or cognitive judgment an execution input?
- **Necessary adjacent/external contracts:** `openspec/specs/evaluation-hardening/spec.md` answers how Wave0/Wave1/Wave2 cognitive-program scenario fixtures declare criterion IDs; `openspec/specs/hitl1-node/spec.md` answers the equivalent HITL1 cognitive-program contract; `runtime/evaluation/controls.py` answers whether current admission already stays within the selected narrow boundary; `tests/eval/test_cognitive_evaluation_suite.py` answers the lowest responsible deterministic evidence seam. No DeerFlow interface is required.
- **Evidence seam:** source review of `runtime/evaluation/controls.py` establishes the existing registry-admission mechanism; the existing suite proves normal registry loading and the two-status/independent-review boundary, but has no source-controlled invalid-Rubric registry fixture. Apply records that evidence gap and separately inspects the real subject-to-model handoff for Rubric content or quality interpretation.
- **Not in scope:** application code, typed domain contracts, case fixtures, registries, tests, model prompts/context, Runner behavior, review records, CONTEXT/ADR synchronization, external diagnostics or Bundle-loss retention (A-004), policy-cardinality residual N-002, governance executables, `openspec/config.yaml`, archived changes, and the `deerflow/` gitlink or source.
- **Triggered review policies:** local-context,change-admission,control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Case-control integrity metadata permitted at admission | No cognitive candidate or human judgment decides admission; the Case and source-controlled Rubric declare the facts. | The Evaluation Case's declared Rubric identity/version and scenario criterion IDs are evaluated by deterministic `runtime/evaluation/controls.py` during registry admission. | non-bypassable | Registry admission rejects malformed, stale/mismatched, missing, or duplicate controls before a Runner can construct a subject. | Reuses the existing Case registry and one admission evaluator; avoids a second Runner-side quality controller. | Source review proves the local verifier; existing tests prove normal registry loading but no source-controlled invalid-Rubric fixture presently exercises this exact rejection. |
| Rubric content and quality judgment remain review-only | A later reviewer may assess the retained Bundle; no execution candidate may supply a quality verdict. | The separate review workflow owns criterion content interpretation and the four-state Cognitive Evaluation Result; the Runner owns only `completed` or `failed`. | non-bypassable | Criterion prose, weights, thresholds, evaluator guidance, and verdicts cannot enter model-facing input, execution output, or Runner status. | Reuses existing execution/review separation rather than adding a model-visible rubric channel or execution grade. | Existing Runner completion and review-record separation tests; no new live-evaluation claim is created. |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cognitive-evaluation-suite`: reconcile the Case/Rubric execution-input boundary with the selected control-integrity metadata contract.
- `evaluation-hardening`: define Wave0/Wave1/Wave2 cognitive-program scenario `review_criteria` as criterion-ID admission metadata while retaining the existing non-quality execution boundary.
- `hitl1-node`: define HITL1 cognitive-program scenario `review_criteria` as criterion-ID admission metadata while retaining its bounded model-method contract.

## Impact

- Main-spec requirements will change in the three listed capability deltas and must be
  synced only after a separate apply authorization.
- Current `runtime/evaluation/controls.py`, typed scenario fixtures, and focused tests
  are reviewed as conformance evidence only. The source-controlled invalid-Rubric
  admission test is a disclosed evidence gap; apply must stop and record a
  `DEFERRED-CODE-CHANGE` if a code path consumes prohibited Rubric content, treats a
  criterion ID as model-facing quality guidance or scoring, or produces a quality
  verdict.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink;
  this change neither needs nor authorizes that boundary.
