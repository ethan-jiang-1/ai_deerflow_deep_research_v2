## Why

`EvaluationBundleManifest` currently gives a missing `evidence_layer` the same value as a
current deterministic writer, while `runtime.evaluation.contracts` duplicates domain contracts
as an unbounded import route. User/Evaluation Owner has authorized a clean cutover: an absent or
unknown layer is unsupported evidence, not a conservative current fact, and the documented
facade is the only supported Python route.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/domain/evaluation.py::EvaluationBundleManifest`; it owns the persisted evidence-layer fact and its validation.
- **Seam classification:** deterministic-guardrail - the change tightens deterministic manifest admission and removes duplicate compatibility projections without changing an evaluation subject, reviewer judgment, or live-provider behavior.
- **Question:** How can the Evaluation Bundle reader require an explicit evidence layer, preserve the existing facade as the only supported import surface, and fail closed before Review or quality provenance is written?
- **Necessary adjacent/external contracts:** `runtime/evaluation/{__init__,runner,review,operations}` asks how domain-owned validation reaches the documented facade and the existing bounded review diagnostic; `project-structure` / `PRS-015` asks how removal of `runtime/evaluation/contracts.py` updates the exact required-path inventory without merging evaluation data into Deep Research Run discovery; `tests/eval/metrics.py` asks whether the zero-caller shim has any behavior to preserve. No DeerFlow interface is needed because this change neither imports from nor modifies the upstream gitlink.
- **Evidence seam:** direct manifest validation plus `verify_bundle()` through `EvaluationReviewService` and `EvaluationOperations.review`; focused import/removed-surface checks, current live-boundary checks, requirement-to-test coverage, and architecture governance prove the facade, no-write rejection, and structural retirement.
- **Not in scope:** Evaluation Case/subject or Review-result semantics; selected-live/provider behavior; a new review interface, retry, retention service, data backfill, or automatic migration; any external/private record support; profile/proposal/checkpoint input compatibility (05); host/config compatibility (06); Run Bundle/Journal/checkpoint retained-data migration (07); and all DeerFlow source or gitlink changes.
- **Triggered review policies:** participant-outcomes, control-and-recovery, workflow-outcome-review, control-placement, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Retained Evaluation Bundle evidence-layer admission | None; an operator may submit a Bundle but cannot supply or infer its layer | `EvaluationBundleManifest` owns the declared layer; `verify_bundle()` validates it before `EvaluationReviewService` can write a Review Record | non-bypassable | Missing or unknown layer rejects before Review/quality claim and performs no write, backfill, or provenance upgrade; emergency rollback restores the previous reader before a fresh retry | Reuses the existing manifest validator and BundleIntegrityError route; removes the silent default | Manifest-minus-layer fixture through `verify_bundle()`, Review service, and `EvaluationOperations.review` |
| Supported evaluation contract import | None | Domain contracts remain fact authority; `runtime.evaluation` is the supported package projection | non-bypassable | A removed `.contracts` import cannot create a duplicate contract authority; the legal migration target is the facade | Removes the intermediate re-export and its required-path entry without adding an alias | Facade import/contract identity and removed-module tests plus architecture governance |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Bundle manifest has a missing or unknown `evidence_layer` | `EvaluationBundleManifest` validation | No automatic migration, default, retry, write, or quality classification; a source rollback may restore the former reader only before an explicit retry | `BundleIntegrityError("bundle_manifest_invalid")`; no Review Record, live-quality claim, or payload mutation | Submit a Bundle whose manifest has an explicit valid layer, or restore the previous reader under the authorized rollback | Direct manifest, `verify_bundle()`, Review service, and operations tests with a planted missing/unknown layer |
| Consumer imports retired `runtime.evaluation.contracts` | Domain contracts and the supported facade boundary | No runtime fallback or alias; consumer must change to `runtime.evaluation` | Import fails without creating a second contract path | Import the documented facade | Facade identity and removed-module tests, import governance, and project-structure check |

## What Changes

- **BREAKING** Require every Evaluation Bundle manifest and Review Record to carry an explicit
  valid `evidence_layer`. Missing or unknown layer input becomes an unsupported-record rejection
  before review; it cannot be defaulted, written back, classified as live quality, or used to
  create a Review Record.
- Preserve `deerflow_deep_research.runtime.evaluation` as the one documented, supported Python
  facade while keeping `domain.evaluation` as fact authority. Migrate internal runtime imports
  directly to domain contracts and delete the unsupported `runtime.evaluation.contracts` re-export.
- Remove the zero-caller, always-empty `compute_metrics()` test shim and its export without
  changing typed metric functions or `ValidatedEvaluationOutcome`.
- Update the evaluation operator documentation, requirement registry and implementation/test
  annotations, and the
  `PRS-015` structural inventory so the current supported route, rejection behavior, and removed
  path agree. Keep live-report classification and archive admission guards intact.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cognitive-evaluation-suite`: require explicit evidence-layer provenance at Bundle/Review
  admission and declare the supported facade boundary without changing execution or review authority.
- `project-structure`: preserve PRS-015's separated evaluation ownership while retiring the
  obsolete runtime contract re-export from the exact structure inventory.

## Impact

- Affected downstream paths: `domain/evaluation.py`, `runtime/evaluation/`, focused evaluation
  tests, evaluation documentation, `tests/eval/metrics.py`, `project-structure.toml`, and their
  requirement/evidence governance surfaces.
- Supported imports remain on `deerflow_deep_research.runtime.evaluation`; direct imports of the
  removed `.contracts` module break by design. Unenumerated retained records without an explicit
  layer become unsupported and reject rather than being silently interpreted.
- No dependency, external service, live-run, DeerFlow source, or gitlink change is introduced.
