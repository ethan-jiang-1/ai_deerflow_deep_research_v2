## ADDED Requirements

### Requirement: Suspended credentialed selectors remain retained but inactive

A credentialed `FULL_REAL_PIPELINE` selector that is presently unsuitable for an
ordinary automation loop SHALL remain tracked under
`deep_research_harness/tests/scenarios_suspended/` rather than be deleted or
represented as passing evidence. Its non-test filename SHALL exclude it from ordinary
pytest discovery, and its retained `release_e2e` marker SHALL remain excluded from
every active test lane. Active Make targets, GitHub workflows, focused lane selection,
and active evidence registries SHALL not invoke, select, or claim the suspended
selector as current release evidence.

The local suspended-scenarios record SHALL link to the single diagnostic issue that
owns its repair and state the reactivation precondition. Reactivation SHALL require a
new approved OpenSpec change and a deterministic diagnostic loop that completes in
less than ten seconds before another credentialed execution is authorized. (`EVH-024`)

While the selector is suspended, the active requirement-evidence policy SHALL not
require a current full-real release claim. The retained source and any versioned
redacted attestation are historical diagnostic material; neither SHALL be treated as a
collected replacement claim or as evidence of a current successful release.

#### Scenario: Ordinary automation excludes a retained selector
- **WHEN** a contributor runs ordinary pytest collection or an active Make or GitHub
  workflow test lane
- **THEN** the retained suspended selector is neither collected nor selected, while its
  active deterministic control-plane evidence remains collected

#### Scenario: A later release reactivation is proposed
- **WHEN** a contributor wants to run the retained credentialed selector again
- **THEN** a new approved OpenSpec change first supplies the linked issue's
  less-than-ten-second deterministic diagnostic loop and then defines any authorized
  credentialed execution

## MODIFIED Requirements

### Requirement: Evidence consolidation preserves named risks without a count target

Any proposed deletion or replacement of a collected test-evidence selector SHALL be
represented by a typed consolidation decision before deletion. The decision SHALL
identify the displaced claim and selector, every affected requirement and named risk,
and the collected retained claim or claims that continue to prove each risk at the
lowest responsible seam. A retained claim at a different seam, authenticity level, or
evidence class SHALL include a bounded rationale for why the original risk remains
proved without overclaiming model judgment or workflow authenticity. A retention-only
suspension that keeps the original source but removes it from active collection and
evidence is not a consolidation replacement: it SHALL be governed by an owning
requirement, SHALL not map its full-real risk to a lower-authenticity claim, and SHALL
not represent the suspended selector as current coverage. (`EVH-023`)

Validation SHALL reject an unknown or uncollected displaced/replacement claim, an
unmapped requirement or risk, self-replacement, a replacement that does not own the
mapped requirement, any seam/evidence-class/authenticity difference without
justification, and any proposal justified only by aggregate test count, directory
placement, marker, or line coverage. An evidence board or consolidation decision SHALL
not itself delete a test or authorize deletion. This change's accepted retirement set
SHALL be empty.

#### Scenario: Unmapped deletion or replacement is rejected
- **WHEN** a consolidation candidate deletes or replaces a selector without mapping
  every affected requirement and named risk to collected retained proof
- **THEN** deterministic evidence governance rejects the decision before any test is
  deleted or any requirement is presented as covered

#### Scenario: Retained suspension cannot impersonate a replacement
- **WHEN** a tracked selector is suspended from every active execution and evidence
  surface without being deleted or replaced
- **THEN** the owning suspension requirement retains the source and its diagnostic
  boundary without asserting that lower-authenticity or historical material proves the
  suspended selector's current full-real risk

#### Scenario: Aggregate count cannot justify consolidation
- **WHEN** a consolidation candidate cites only a desired pytest total, marker balance,
  directory placement, line coverage, or an aggregate passing selector
- **THEN** validation rejects it because no displaced risk has been preserved at its
  responsible seam

#### Scenario: Different evidence metadata remains bounded
- **WHEN** retained proof uses a different seam, authenticity level, or evidence class
- **THEN** the decision explains that exact difference and gives a bounded reason the
  replacement preserves the original named risk without claiming a universal strength
  ordering or model quality from deterministic evidence

#### Scenario: Governance rollout deletes no tests
- **WHEN** this evidence-board change is applied
- **THEN** the retirement decision set is empty and every currently collected test
  remains present, regardless of the resulting aggregate count

### Requirement: The singular release acceptance proves a model-led first-party smoke path

The retained `release-full-real-acceptance` scenario SHALL remain the sole
`FULL_REAL_PIPELINE` release-acceptance definition. It SHALL begin with the fixed
Chinese request to prepare a Python 3.12 upgrade checklist using Python official
documentation, wait for the model-led HITL1 proposal, and submit a natural-language
confirmation before using the existing remaining lifecycle path. It SHALL not inject a
hand-authored profile payload or create another release runner.

For this scenario only, the test-owned live web adapter and release assertion SHALL
admit only the declared canonical Python 3.12 source set. A successful release outcome
SHALL retain the confirmation handoff and verify a non-empty Chinese final report with
at least three cited claim bindings from at least two distinct URLs in that source set.
The selector is retained in the suspended-scenarios surface and has no active
credentialed release lane, Make target, GitHub workflow, focused release-evidence
category, or `FULL_REAL_PIPELINE` evidence claim. It SHALL not be presented as a
current successful release acceptance. The network-free tests cover the fixed
interaction and source-set admission seams without claiming that a live run proves
general research quality. The current Harness structural/lifecycle change closes its
deterministic Bundle-authority migration with those tests; a successful credentialed
execution remains a separately tracked diagnostic issue and is not this change's
archive prerequisite.

The runner SHALL call the same trusted public Deep Research entry as a user-facing
execution and obtain lifecycle, report, citation, containment, and terminal facts only
from the selected available Run Bundle and its Bundle-local State. It SHALL not pass or
derive a `research_id`, compile or inspect a Deep Research GraphHost snapshot, select
an external checkpoint, or infer an outcome from a workspace-derived report path. A
missing or unreadable selected Bundle SHALL fail a future authorized release attempt
rather than cause legacy recovery or result inference. (`EVH-024`)

#### Scenario: A reactivated release proof remains Bundle-authoritative
- **WHEN** a later approved change explicitly reactivates the credentialed full-real
  release selector
- **THEN** its one public-entry execution carries only the selected opaque `bundle_id`
  through trusted control context, and its report/citation assertions observe the
  selected Bundle without a session, checkpoint, GraphHost, or workspace fallback
