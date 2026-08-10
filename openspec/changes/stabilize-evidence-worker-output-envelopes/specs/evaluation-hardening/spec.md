> req: EVH-030

## ADDED Requirements

### Requirement: Evidence-intake live calibration binds an explicit profile to an admitted Bundle

Each selected case in the existing Wave0/Wave1 evidence-intake live calibration corpus
SHALL resolve exactly one registered explicit demo profile before it constructs the
focused production bridge. It SHALL create a fresh test-owned Run Bundle through the
existing Bundle admission path, establish that Bundle's Event Journal, and bind the
resulting `SelectedBundleContext` through the existing production node dependency seam
before the branch invocation. A missing selected context, unavailable Bundle,
absent/unknown/non-unique profile, or missing branch prerequisite SHALL fail before
provider invocation and produce no rubric result.

The selected calibration SHALL invoke only its named generated branch request through
the real production model/tool bridge, then evaluate its existing production parser and
applicable local semantic validation without submitting a candidate to a ledger, gate,
route, critic, or full-pipeline lifecycle. A selected Wave0/Wave1 worker or repair case
that reaches its candidate parser SHALL classify the final response at that same
boundary and record the correlated closed response shape and canonical validation codes
in the selected Bundle Journal. A selected SourceDiagnostic or ClaimVerifier case SHALL
retain its existing typed parser/rubric boundary and SHALL NOT fabricate a worker-local
response-shape or validation fact. Supported read-only Journal inspection SHALL verify
the profile provenance and any branch-applicable validation facts. A failed hard
invariant or candidate validation SHALL be a live-run failure without a rubric
disposition. The calibration SHALL not retain a raw prompt, model response, tool result,
exception text, provider body, URL, or artifact path in its report or Bundle Journal,
and it SHALL not claim full-pipeline, source-quality, evidence-acceptance, or
profile-quality success.
(`EVH-030`)

#### Scenario: A selected worker calibration reaches the production bridge with Bundle authority
- **WHEN** an operator selects one named Wave0 or Wave1 worker calibration with one
  explicit profile and all required live credentials
- **THEN** it creates and binds a fresh selected Bundle before invocation, executes only
  the named branch through the real bridge, and inspects that Bundle's safe Journal
  facts without constructing a work-unit submission or full research run

#### Scenario: Missing Bundle selection fails before a live model call
- **WHEN** a selected evidence-intake calibration cannot establish its selected Bundle
  context before dependency resolution
- **THEN** it fails its hard invariant before provider invocation and records no rubric
  result or inferred candidate outcome

#### Scenario: A real prose result is an attributable live failure
- **WHEN** a selected worker returns final prose or another non-admissible response
  shape after its permitted live tool turn
- **THEN** the calibration fails without a rubric disposition and the selected Bundle
  exposes only the correlated profile, closed response shape, and canonical validation
  facts needed to diagnose it

#### Scenario: Selected critic calibration does not invent a worker boundary
- **WHEN** a selected SourceDiagnostic or ClaimVerifier case reaches its existing typed
  parser and rubric boundary
- **THEN** it remains Bundle- and profile-bound but emits no worker-local response-shape
  or validation fact that the critic branch did not reach
