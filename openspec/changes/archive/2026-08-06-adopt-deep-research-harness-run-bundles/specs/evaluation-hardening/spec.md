> req: EVH-005, EVH-010, EVH-025, EVH-026

## ADDED Requirements

### Requirement: Deterministic evidence proves Run Bundle lifecycle authority and loss boundaries

The deterministic evidence corpus SHALL retain collected zero-API cases at the lowest
responsible lifecycle/store/adapter seams for fresh opaque Bundle publication,
one-active admission, Current Bundle Handle continuation, absent-handle scoped
discovery, safe refinement ordering, ended-Bundle reactivation, Bundle loss,
no-external-recovery, cross-conversation isolation, and Cognitive Evaluation separation.
Each case SHALL invoke a real focused production interface with typed inputs and assert
the Bundle-local State/content or typed lifecycle outcome it owns. Static path scans,
mocked presentation dictionaries, test counts, and live-provider success SHALL not
substitute for this evidence. (`EVH-025`)

#### Scenario: Deleted Bundle case proves no external recovery
- **WHEN** a deterministic lifecycle case deletes a selected Bundle while a legacy checkpoint/session/binding observation remains available
- **THEN** it observes a typed unavailable result, no replacement State/directory, and no use of the external observation as lifecycle authority

### Requirement: Verification and evidence paths use the canonical Harness root

The complete deterministic verification command, requirement/evidence registries,
source ownership scans, architecture checks, Docker/profile contract tests, and release
path protections SHALL use `deep_research_harness/` as the sole downstream physical
root. They SHALL preserve the existing distinct fast, integration, workflow, live, and
release evidence classes and SHALL reject stale protected-path or source-root references
that could omit the moved downstream surface. (`EVH-026`)

#### Scenario: Root-sensitive governance cannot pass from the former path
- **WHEN** a test/evidence/architecture rule is pointed at `deerflow_research/` after the move
- **THEN** its focused detector test fails rather than silently collecting an empty or mis-scoped surface

## MODIFIED Requirements

### Requirement: The singular release acceptance proves a model-led first-party smoke path

The existing `release-full-real-acceptance` scenario SHALL remain the sole
`FULL_REAL_PIPELINE` release proof. It SHALL begin with the fixed Chinese request to
prepare a Python 3.12 upgrade checklist using Python official documentation, wait for
the model-led HITL1 proposal, and submit a natural-language confirmation before using
the existing remaining lifecycle path. It SHALL not inject a hand-authored profile
payload or create another release runner.

For this scenario only, the test-owned live web adapter and release assertion SHALL
admit only the declared canonical Python 3.12 source set. A successful release outcome
SHALL retain the confirmation handoff and verify a non-empty Chinese final report with
at least three cited claim bindings from at least two distinct URLs in that source set.
The credentialed release lane remains manually selected with strict preflight; the
network-free tests cover the fixed interaction and source-set admission seams without
claiming that a live run proves general research quality. The current Harness
structural/lifecycle change closes its deterministic Bundle-authority migration with
those tests; a successful credentialed execution is a separately tracked diagnostic
issue and is not this change's archive prerequisite.

The runner SHALL call the same trusted public Deep Research entry as a user-facing
execution and obtain lifecycle, report, citation, containment, and terminal facts only
from the selected available Run Bundle and its Bundle-local State. It SHALL not pass or
derive a `research_id`, compile or inspect a Deep Research GraphHost snapshot, select
an external checkpoint, or infer an outcome from a workspace-derived report path. A
missing or unreadable selected Bundle SHALL fail the release attempt rather than cause
legacy recovery or result inference. (`EVH-024`)

#### Scenario: Release proof remains Bundle-authoritative
- **WHEN** the operator explicitly selects the credentialed full-real release lane
- **THEN** its one public-entry execution carries only the selected opaque `bundle_id`
  through trusted control context, and its report/citation assertions observe the
  selected Bundle without a session, checkpoint, GraphHost, or workspace fallback

### Requirement: Release gate combines deterministic CI with optional LLM canary

The existing five pairwise-disjoint evidence selections, offline/no-implicit-sync
deterministic gate, strict selected live/release lanes, and stable workflow/status
identity guarantees remain unchanged. Their canonical complete deterministic command is
`cd deep_research_harness && UV_OFFLINE=1 make verify`. CI path filters, working
directories, artifacts, release-attestation scopes, and protected-path checks SHALL use
`deep_research_harness/`, while `backend/`, `frontend/`, and `openspec/` boundary
checks remain repository-root checks. A filesystem-root change SHALL not rename a
workflow display name, job/status identity, test lane, or evidence semantic. (`EVH-005`)

#### Scenario: Canonical verification starts from the Harness root
- **WHEN** a developer runs the complete deterministic verification gate
- **THEN** `cd deep_research_harness && UV_OFFLINE=1 make verify` performs the existing
  local aggregate without resolving a former downstream root

### Requirement: Test selection and requirement traceability are mechanical

The existing collected-test coverage, invalid-fixture, detector-smoke, registry, and
cross-lane evidence requirements remain unchanged. The production-source ownership scan
SHALL inspect `deep_research_harness/src/**/*.py` as its canonical downstream source
root and shall fail closed for a stale, empty, relocated, or mis-scoped scan. (`EVH-010`)

#### Scenario: Production ownership scan uses the moved source tree
- **WHEN** a detector-smoke fixture places a known invalid `@impl` annotation beneath
  the canonical production source root
- **THEN** the scan discovers and rejects it under `deep_research_harness/src/` rather
  than succeeding against `deerflow_research/src/`
