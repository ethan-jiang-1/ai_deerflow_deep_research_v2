## Context

The Evaluation Bundle manifest and the in-memory Review Record currently use a default
`deterministic_handoff` evidence layer. `verify_bundle()` converts model-validation failures to
the existing bounded `bundle_manifest_invalid` diagnostic before the review writer is reached,
but a missing field currently succeeds because of those defaults. The runtime package also
contains a module-private re-export of the domain contracts even though the package facade is the
documented supported route. See [proposal.md](proposal.md) for the authorized cutover.

## Goals / Non-Goals

**Goals:**

- Make evidence-layer provenance explicit at all Evaluation Bundle and Review Record validation
  boundaries while preserving the existing deterministic and selected-live writer behavior.
- Preserve `runtime.evaluation` as the sole supported runtime import facade and remove its
  unsupported duplicate re-export.
- Retire the isolated zero-behavior metrics shim without changing typed metric semantics.
- Keep failure observable through the existing bounded review diagnostic and retain deterministic
  proof at the manifest and review-service seams.

**Non-Goals:**

- This change does not migrate, rewrite, retain, or inventory any private or external records.
- It does not alter Evaluation Case admission, review result semantics, provider selection,
  selected-live preflight, retry behavior, or Deep Research Run Bundle authority.
- It does not create a new persistence schema, compatibility alias, reader, or recovery service.

## Decisions

### Make the provenance fields required at their fact models

Remove the default from the Evaluation Bundle manifest and Review Record evidence-layer fields.
The closed evidence-layer enum remains the validator: current writers already always select and
write either deterministic handoff or credentialed live quality, while missing and unknown input
now fail normal model validation. Keeping a default and adding a later review check was rejected
because any other reader could still silently manufacture provenance. Introducing a new versioned
record format was rejected because the authorized scope is an explicit clean break, not retained
data support.

### Preserve the existing admission and no-write order

The review service continues to call `verify_bundle()` before resolving controls, calculating the
Bundle digest, or creating the Review Record path. The manifest validation error therefore becomes
the existing `BundleIntegrityError("bundle_manifest_invalid")`, which `EvaluationOperations.review`
projects as its bounded diagnostic. The writer is not entered, and the retained manifest is never
rewritten. No additional catch-all, defaulting path, retry, or provenance upgrade is introduced.

Review Record model validation independently rejects missing or unknown provenance for callers
that validate such a record. Completed reviews remain safe because the Review Record derives its
layer solely from the integrity-verified manifest.

### Retire the duplicate runtime contract route directly

The supported facade will import its contract projection directly from the evaluation domain, and
runtime implementation modules will import their domain contracts from that fact owner. Delete
the `runtime.evaluation.contracts` re-export instead of leaving an alias or deprecation reader.
This preserves a single supported consumer route while avoiding a second projection layer. The
facade's exported contract identities must remain those of the domain models.

### Synchronize structural, documentation, and evidence records

The exact project-structure registry will stop enumerating the deleted file, then its generated
`deep_research_harness/AGENTS.md` locator will be regenerated as required by architecture policy.
The operator document will remove the obsolete statement that missing-layer manifests are readable.
The requirement registry and affected production/test annotations will gain the new facade
requirement, giving the existing requirement-to-test coverage check a deterministic proof. The
separate `evaluation-hardening` test-evidence assets do not own this runtime behavior and remain
unchanged.

### Delete only the proven dead metrics shim

Remove `compute_metrics()` and its export after a repository-wide consumer check confirms it has
no callers. Retain all typed metric models and functions unchanged. This is a deletion of test
helper residue, not an evaluation-metrics behavior change.

## Risks / Trade-offs

- [Historical private or external records without provenance become unreadable] -> This is the
  explicit unsupported-record outcome authorized by the Evaluation Owner. The rejection occurs
  before Review or quality claims and leaves source bytes unchanged.
- [A consumer relied on the module-private import route] -> The authorized clean break causes a
  deterministic import failure; the supported facade is the sole migration target.
- [A regression could move validation after the writer] -> Focused tests plant missing and unknown
  layers through direct validation, review submission, and operations while asserting no Review
  Record path exists and the bounded diagnostic is returned.
- [Registry and generated locator drift] -> Update the delta, registry, rendered locator, and
  architecture fixtures together, then run the architecture checker before archive.

## Migration Plan

1. Add focused negative tests for missing and unknown manifest/record evidence layers, review
   no-write behavior, facade contract identity, and retired-module absence.
2. Remove the two provenance defaults; preserve the current writers and `verify_bundle()` error
   translation, then migrate runtime imports and remove the compatibility module.
3. Retire the metrics shim, synchronize documentation and governance inventories, and regenerate
   the architecture locator.
4. Run focused tests and the project requirement, requirement-evidence, architecture, charter,
   strict OpenSpec, whitespace, and standard offline verification gates.
5. An emergency rollback restores the former source reader only; it does not modify rejected
   record bytes. After rollback, an operator explicitly retries the review. Re-supporting retained
   records requires a separate inventory-led change with hash-preserving migration and retention
   decisions.

## Open Questions

None. The supported surface, unsupported record class, recovery action, and retention boundary
are all explicitly authorized by the Evaluation Owner.
