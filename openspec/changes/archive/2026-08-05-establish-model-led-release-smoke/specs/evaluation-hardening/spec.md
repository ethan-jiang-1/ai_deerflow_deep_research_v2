> req: EVH-024

## ADDED Requirements

### Requirement: The singular release acceptance proves a model-led first-party smoke path

The existing `release-full-real-acceptance` scenario SHALL remain the sole
`FULL_REAL_PIPELINE` release proof. It SHALL begin with the fixed Chinese request to
prepare a Python 3.12 upgrade checklist using Python official documentation, wait
for the model-led HITL1 proposal, and submit a natural-language confirmation before
using the existing remaining lifecycle path. It SHALL not inject a hand-authored
profile payload or create another release runner.

For this scenario only, the test-owned live web adapter and release assertion SHALL
admit only the declared canonical Python 3.12 source set:

- `https://docs.python.org/3.12/whatsnew/3.12.html`
- `https://docs.python.org/3.12/library/venv.html`
- `https://docs.python.org/3.12/library/removed.html`

The release proof SHALL fail rather than fall back to another source, while
production web-search and source-policy behavior remain unchanged. A successful
release outcome SHALL record that the confirmation handoff occurred, retain the
existing isolated identity and hard lifecycle invariants, and verify a non-empty
Chinese final report with at least three cited claim bindings from at least two
distinct URLs in that source set. The credentialed release lane remains manually
selected with strict preflight; network-free tests SHALL cover the fixed interaction
and source-set admission seams without claiming that a live run proves general
research quality. (`EVH-024`)

The committed 2026-07-17 version-1 release attestation SHALL remain a frozen
historical record with its existing exact eight-invariant schema and SHALL NOT be
used to attest this changed smoke path. If a version-2 attestation is created, it
SHALL be generated only from one separately selected successful run of this scenario,
be paired to that run by its source-report hash, retain the eight legacy invariant
results, and add only the closed smoke evidence for confirmation handoff, non-empty
Chinese report, minimum cited-claim count, declared-source-set-only verdict, and
minimum distinct-source count. The version-2 payload SHALL use a fixed source-set
identifier and counts rather than source URLs, report/model/source body, credentials,
or host paths. Validators SHALL dispatch by version, preserve v1's exact validation,
and fail closed for a mixed schema, mismatched report, or sensitive payload. Matching
the report proves bounded payload integrity only; the separately selected real-run
provenance and evidence approval remain an operator responsibility.

#### Scenario: Release acceptance follows the user-facing confirmation handoff
- **WHEN** an operator explicitly selects the full-real release lane with its
  required credentials
- **THEN** the one release scenario sends the fixed Chinese request, receives a
  model-led proposal, submits natural confirmation, and does not use a profile JSON
  fixture before research continues

#### Scenario: Release-only source containment fails closed
- **WHEN** the test-owned live web adapter receives a search result or final citation
  URL outside the declared canonical Python 3.12 source set
- **THEN** the release scenario rejects that evidence and does not broaden the test
  to another source or alter production source policy

#### Scenario: A passing smoke outcome remains bounded and inspectable
- **WHEN** the selected release scenario reaches its existing completed lifecycle
  outcome
- **THEN** its report includes the existing hard invariants plus confirmation,
  Chinese-report, three-claim, and first-party-citation evidence without retaining
  credentials, raw model text, or a second full-pipeline claim

#### Scenario: Historical release evidence cannot be upgraded by a code change
- **WHEN** deterministic tests validate the committed 2026-07-17 attestation while
  this smoke-path change has not run the credentialed release lane
- **THEN** they preserve and validate its version-1 schema and eight invariant names,
  but do not compare it to a new release report or claim the new confirmation/source
  evidence was historically observed

#### Scenario: A future smoke attestation is versioned and redacted
- **WHEN** a separately selected successful release run is explicitly prepared for
  durable evidence
- **THEN** a matching version-2 attestation may record the bounded extended invariant
  and count evidence, rejects cross-version or mismatched-source pairing, and stores
  neither source URLs nor raw report/model/source content or credentials
