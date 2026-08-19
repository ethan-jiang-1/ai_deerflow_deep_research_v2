# Fix Wave1 Critic Boolean Label Shapes (BUG-058)

## Why

The first real mode-004 run (bundle `b_8bfIc_sJr53K0o5MJfK8fOPP0MOVvL5A3XxJvHNvW4A`,
default intent, comparison question) blocked at wave1 with six failed attempts:
every time the wave1 worker produced a validated candidate (3/3), the
SourceDiagnostic critic's output failed parsing as
`wave1_review_output_invalid`, exhausting the gate budget to
`research.blocked`. Root cause (reproduced against the real model,
2026-08-19): the contract `CriticSourceAssessment` requires
`marketing_risk: bool` / `cross_verification_need: bool`, but the wave1
prompt never declares the boolean type (its objective says only
"marketing-risk flag"), and the real model returns label strings —
`"marketing_risk": "low"` — which pydantic rejects and the critic error
boundary masks into one opaque code. This is the same real-model-shape
defect class 003 fixed for wave2 (`priority: "high"`) and targeted sources
(`url`→`canonical_url`); the targeted SourceDiagnostic prompt already
declares `"marketing_risk": "boolean"` — wave1 simply lacks the same
declaration. Bug record: `_backlog/bugs/BUG-058-wave1-critic-bool-fields-string-labels.md`.

## What Changes

- **Contract-boundary label normalization.** `CriticSourceAssessment`'s two
  boolean fields accept, at the deterministic parse boundary, a closed
  label set in addition to JSON booleans: casefolded
  `high|yes|true|elevated|needed|required` → `true` and
  `low|none|no|false|minimal|minor|unlikely|not_needed` → `false`. Labels
  outside the closed map (notably the ambiguous `medium`) still fail
  validation fail-closed. Both consumers (wave1 review and the targeted
  evidence critic) share `SourceDiagnosticResult`, so the normalization
  lives once in `domain/critics.py`.
- **Prompt parity with the targeted precedent.** The wave1
  SourceDiagnostic prompt's expected-output gains the same `bounds` block
  the targeted critic already declares (`"marketing_risk": "boolean"`,
  `"cross_verification_need": "boolean"`, plus the trust/materiality
  enums), and the objective wording makes the boolean explicit. The model
  is asked for booleans first; normalization is the deterministic safety
  net.
- **Critic failure-code transparency.** The wave1 review error boundary
  distinguishes a pydantic shape failure (`wave1_review_output_shape_invalid`)
  from JSON decode / non-object failures, instead of masking every
  non-prefixed ValueError into one opaque code. The code set stays closed;
  no exception detail crosses the boundary.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `evidence-critic-nodes`: EVC-001's SourceDiagnostic assessment gains the
  closed label normalization at the typed boundary and the explicit
  boolean declaration in the critic's expected output contract.

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/critics.py`
  (label normalization validators on `CriticSourceAssessment`)
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/prompts.py`
  (bounds block + objective wording)
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/review.py`
  (shape-invalid code split in `_canonical_critic_code`)
- Tests: critic contract tests (label map red-first), wave1 prompt parity
  test, review code-mapping test
- Bug record: `_backlog/bugs/BUG-058-...` (fix关联 updated on completion)
- No gate, route, ledger, or state-writer changes; no `deerflow/` gitlink
  changes. The 004 rerun acceptance stays in change `hard-real-auto`
  (task 4.3).

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/domain/critics.py` — the typed assessment contract is where the provider-shape-to-contract decision belongs; both critic consumers import it.
- **Seam classification:** deterministic-guardrail — a pure data-contract normalization with a closed map and fail-closed rejection; the critic's cognitive responsibility (assess assigned sources) is unchanged.
- **Question:** How does a real SourceDiagnostic output that expresses the two assessment flags as severity labels get admitted into the typed contract deterministically, without weakening the fail-closed boundary or moving any decision into the model's hands?
- **Scope honesty:** fixes the observed blocker for both consumers of `SourceDiagnosticResult`; does not claim coverage of other critic shapes (ClaimVerifier has no boolean fields — verified; readiness critic is a different module with no observed failure).
- **Necessary adjacent/external contracts:** `wave1-node` (WON requirements own the wave1 critic invocation/review flow — read-only confirmation that the parse boundary placement and the new closed code compose with the existing review error handling).
- **Evidence seam:** `tests/unit/test_critic_contracts.py` (or the file owning critic domain tests) for the closed label map and fail-closed rejection; `tests/graph/test_wave1_review*.py` for the prompt bounds parity and the code split; the real 004 rerun in `hard-real-auto` task 4.3 is the end-to-end evidence.
- **Not in scope:** mapping the ambiguous `medium` label (no observed occurrence; forcing an explicit semantic choice by failing closed is the evidence-driven posture); ClaimVerifier/readiness shape changes (no boolean fields / no observed failure); prompt-engineering beyond the targeted-parity bounds block; bridge hang hardening.
- **Triggered review policies:** change-admission

## deerflow boundary

Ordinary downstream work neither modifies nor source-browses the `deerflow/`
gitlink; this change does not own or approve any `deerflow/` boundary work.
