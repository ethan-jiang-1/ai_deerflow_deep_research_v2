> req: WOU-012

## ADDED Requirements

### Requirement: Shared submit validation records a distinct post-candidate Journal fact

When the shared work-unit component receives a candidate that reached its deterministic
submit-validation boundary, it SHALL record the boundary as a correlated
`post_candidate` Event Journal validation fact. A rejected candidate SHALL retain only
the existing canonical submission-validation code collection; a successful submission
SHALL retain no post-candidate rejection fact. The component SHALL not label this
boundary as `initial` or `repair`, because those stages remain reserved for the
worker-local candidate validation observations.

This fact is a Bundle-local diagnostic projection only. It SHALL not change candidate
validation, attempt status, failure category, retry eligibility, ledger commit, gate
evaluation, checkpoint state, route, terminal disposition, or lifecycle action. The
component SHALL continue to propagate only its existing frozen typed validation
rejection through the existing controller path. (`WOU-012`)

#### Scenario: Rejected submitted candidate retains its own validation stage
- **WHEN** a Wave0 or Wave1 candidate reaches the shared submit validator and receives
  canonical validation codes
- **THEN** the correlated Journal records one `post_candidate` validation fact with
  those codes while the existing attempt remains a `submission_validation` failure

#### Scenario: Accepted candidate does not fabricate a later failure
- **WHEN** a candidate passes shared submit validation and is committed through the
  existing ledger path
- **THEN** no `post_candidate` rejection fact is recorded and the existing submit and
  terminal projections remain unchanged

