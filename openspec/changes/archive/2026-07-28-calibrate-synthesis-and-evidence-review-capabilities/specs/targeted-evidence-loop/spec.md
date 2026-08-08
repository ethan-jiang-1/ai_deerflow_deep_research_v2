> req: TEL-005

## ADDED Requirements

### Requirement: Targeted evidence capabilities remain gap-scoped and read-only by role

The real targeted worker initial request SHALL bind its required local retrieval
capability and make exactly one permitted retrieval call for one gate-projected gap.
Its structured repair SHALL bind a distinct forbidden capability and SHALL receive
only the assigned gap, bounded draft, and validation facts; it SHALL not retrieve or
add a source, URL, title, fact, or gap identity absent from those observations.
SourceDiagnostic and ClaimVerifier SHALL each bind a distinct forbidden local
capability, receive only their assigned references and delimited untrusted material,
and return candidates that reference only that assignment. Existing work-unit
validation, controller, ledger, critic materializer, and gate owners SHALL remain the
only authorities that admit evidence, artifacts, outcomes, or routes. (`TEL-005`)

#### Scenario: One gate-projected gap permits one bounded retrieval
- **WHEN** a scripted real targeted worker receives one valid gate-projected gap
- **THEN** exactly one permitted retrieval occurs, the model cannot change the gap,
  findings, gate, or ledger, and only validator-approved same-gap source candidates
  reach the existing submission path

#### Scenario: Repair cannot invent targeted evidence
- **WHEN** the targeted worker's initial draft is malformed or names a different gap
- **THEN** its zero-tool repair either returns a contract-valid result constrained to
  the assigned gap and retained observations or follows the existing non-admission
  outcome without a source artifact or ledger record

#### Scenario: Critics cannot escape assigned references or read-only posture
- **WHEN** a scripted SourceDiagnostic or ClaimVerifier candidate names an unassigned
  source reference or attempts a tool call
- **THEN** the zero-tool runtime posture prevents dispatch and the existing validator
  or materializer rejects the out-of-scope candidate without writing critic, ledger,
  gate, or route authority
