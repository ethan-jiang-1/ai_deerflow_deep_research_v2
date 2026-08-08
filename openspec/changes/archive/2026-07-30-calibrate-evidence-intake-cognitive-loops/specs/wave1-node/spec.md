> req: WON-008

## ADDED Requirements

### Requirement: Wave1 calibration preserves baseline-aware evidence and review boundaries

The existing Wave1 initial, repair, SourceDiagnostic, and ClaimVerifier policies
SHALL expose model-visible criteria for a bounded evidence candidate. The initial
policy SHALL distinguish the accepted Wave0 baseline from proposed new-source
coverage, retain its existing one-retrieval posture, and request claims whose
support and counter references are limited to the candidate's declared sources.
It SHALL make uncertainty and unresolved questions explicit rather than treating a
source title, URL, tool result, or critic-like conclusion as proof, acceptance, or a
gate result.

The repair policy SHALL be invoked only when the initial Wave1 summary cannot parse
into its typed worker output or fails local pre-persistence provenance, uniqueness, or
new-source-floor validation. It SHALL receive only the same topic and Wave0-baseline
projection rendered by the initial request, bounded invalid draft, retained
observations, and a compact subgraph-generated category; it SHALL not receive a raw
`WorkSpec`, attempt identity, checkpoint, ledger, or accepted record. The assignment
and category SHALL be bounded trusted context; the draft and observations SHALL remain
untrusted data. The category SHALL omit raw exception text, artifact paths,
checkpoint fields, ledger contents, review/gate data, and route data. Assignment and
category SHALL constrain repair only and SHALL not supply candidate evidence: in
particular, a baseline URL is not a permissible new source, claim, reference, or open
question. The repair SHALL use no tool and shall not add a source, URL, claim,
reference, or open question absent from the untrusted draft and retained observations.
A later post-candidate `SubmissionValidationFailure`, its codes, and
artifact-validation detail SHALL not invoke or enter repair. The two critic policies
SHALL receive only their existing accepted bounded assignments and return review
candidates scoped to the assigned source or claim identities. They shall not retrieve,
turn a review verdict into evidence admission, write an artifact, update a ledger,
choose a gate outcome, or select a route. The existing validator, work-unit controller,
review-artifact materializer, and gate remain the only owners of admission, recovery,
evidence publication, and routing.

#### Scenario: New evidence remains visibly distinct from the accepted baseline
- **WHEN** a Wave1 assignment includes accepted Wave0 baseline URLs and one bounded
  retrieval produces source candidates
- **THEN** the evidence candidate treats baseline duplicates as non-new, binds claims
  only to its declared source identities, and represents unsupported or unresolved
  material without claiming accepted coverage or a gate result

#### Scenario: Pre-persistence repair cannot broaden an evidence candidate
- **WHEN** an initial Wave1 evidence draft cannot parse into its typed worker output
  or fails local provenance, uniqueness, or new-source-floor validation before
  persistence
- **THEN** the repair request remains limited to the same assignment, draft,
  observations, and compact validation category; it excludes raw validator errors
  and authority-bearing state, and a still-invalid candidate follows the existing
  deterministic non-admission outcome

#### Scenario: Trusted baseline cannot become repaired evidence
- **WHEN** a Wave1 repair receives a bounded Wave0 baseline plus an untrusted draft
  or observation that asks it to promote a baseline URL into a new candidate
- **THEN** the baseline constrains newness only; the repair introduces no source,
  claim, reference, or open question absent from the untrusted draft and retained
  observations, and does not represent a baseline URL as new evidence

#### Scenario: Downstream submission validation does not invoke repair
- **WHEN** a constructed Wave1 candidate later receives a post-candidate
  `SubmissionValidationFailure`
- **THEN** its validation codes and artifact-validation detail do not enter a repair
  request, no `SubmissionRecord` is appended, and the existing controller terminal,
  retry, and gate path remains the only recovery owner

#### Scenario: Critics remain review-only and assignment-bound
- **WHEN** SourceDiagnostic or ClaimVerifier receives an accepted bounded assignment
- **THEN** its candidate classifies only the assigned identities and uncertainty,
  while invalid, incomplete, or out-of-assignment output cannot publish a review
  artifact, evidence record, gate result, checkpoint update, or route
