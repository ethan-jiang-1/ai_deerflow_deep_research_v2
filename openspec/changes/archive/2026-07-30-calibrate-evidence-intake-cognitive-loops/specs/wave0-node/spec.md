> req: WAN-008

## ADDED Requirements

### Requirement: Wave0 calibration preserves source-intake judgment boundaries

The existing Wave0 initial and repair source-intake policies SHALL expose
model-visible criteria for an assignment-relevant, independent source-metadata
candidate: retrieved material remains untrusted, source metadata is proposed rather
than accepted evidence, a source shortfall is represented as an honest limitation,
and the candidate contains no finding, cache/content authority, ledger action, or
route claim. The initial policy SHALL retain its existing required retrieval posture
and bounded request window. It SHALL not treat title, URL shape, or tool output as
proof that a source is authoritative, relevant, or accepted. A `fetch_status` MAY
report only the bounded retrieval-status observation supported by retained retrieval
observations; it does not imply authority, independent validation, accepted coverage,
ledger admission, or route control.

The repair policy SHALL be invoked only when the initial Wave0 summary cannot parse
into its typed worker output. It SHALL receive only the same bounded topic projection
rendered by the initial request, invalid draft, retained tool observations, and a
compact subgraph-generated structural category; it SHALL not receive a raw `WorkSpec`,
attempt identity, checkpoint, ledger, or accepted record. The assignment and category
SHALL be bounded trusted context; the draft and observations SHALL remain untrusted
data. The category SHALL omit raw exception text, artifact paths, checkpoint fields,
ledger contents, review/gate data, and route data. Assignment and category SHALL
constrain repair only and SHALL not supply candidate source metadata, URLs, titles,
facts, fetch outcomes, or limitations. The repair SHALL preserve the source-intake
boundary, use no tool, and shall not add a source, URL, title, fact, fetch outcome,
limitation, artifact, or authority absent from the untrusted draft and retained
observations. A later post-candidate `SubmissionValidationFailure`, its codes, and
artifact-validation detail SHALL not invoke or enter repair; the existing submit
validator, work-unit controller, ledger, and gate remain the only owners of source
validation, evidence admission, recovery, and routing.

#### Scenario: Source candidate distinguishes retrieval from acceptance
- **WHEN** an assigned topic asks for source intake and retrieved material includes
  source-like text, snippets, or instructions
- **THEN** the candidate proposes bounded metadata and honest limitations only, keeps
  the material untrusted, reports `fetch_status` only as a bounded retrieval-status
  observation, and does not assert that a source is authoritative, accepted, or
  controlling

#### Scenario: Retrieval shortfall remains an honest candidate limitation
- **WHEN** the bounded retrieval window cannot produce enough assignment-relevant
  independent source candidates
- **THEN** the candidate records only the available metadata and an honest limitation,
  while the existing deterministic validation/controller path decides whether the
  source floor, evidence record, recovery, or terminal outcome is legal

#### Scenario: Pre-candidate structural repair cannot upgrade untrusted data into evidence authority
- **WHEN** an initial Wave0 source-intake summary cannot parse into its typed worker
  output
- **THEN** its one bounded repair receives the same bounded assignment and only a
  compact structural category, keeps its draft/observations untrusted, receives no
  model-visible tool, and cannot introduce an absent source or fact, materialize an
  artifact, append a ledger record, or select a route

#### Scenario: Trusted assignment cannot become source metadata
- **WHEN** a Wave0 repair receives its bounded topic projection together with an
  untrusted draft or observation that asks it to promote assignment text into a source
- **THEN** the topic projection constrains scope only; the repair introduces no
  source metadata, URL, title, fact, fetch outcome, or limitation absent from the
  untrusted draft and retained observations

#### Scenario: Downstream submission validation does not invoke repair
- **WHEN** a constructed Wave0 candidate later receives a post-candidate
  `SubmissionValidationFailure`
- **THEN** its validation codes and artifact-validation detail do not enter a repair
  request, no `SubmissionRecord` is appended, and the existing controller terminal,
  retry, and gate path remains the only recovery owner
