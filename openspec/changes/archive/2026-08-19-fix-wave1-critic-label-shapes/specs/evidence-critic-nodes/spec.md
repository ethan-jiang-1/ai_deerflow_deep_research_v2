# evidence-critic-nodes Delta

> req: EVC-001

## MODIFIED Requirements

### Requirement: SourceDiagnostic agent produces a typed trust and materiality assessment

The SourceDiagnostic critic SHALL accept a set of accepted `SourceRef`s (with
sandbox content read by the critic via its `read_roots`) and SHALL produce a
versioned `SourceDiagnosticResult` carrying per-source assessments: a `trust_tier`
(enumerated: `high`/`medium`/`low`/`untrusted`), a `materiality`
(enumerated: `primary`/`secondary`/`peripheral`), a `marketing_risk`
flag, and a `cross_verification_need` flag. The critic SHALL only reference source ids present
in the assigned evidence set; references to unassigned or fabricated sources SHALL
fail validation.

The critic's expected-output contract SHALL declare the two flag fields as
booleans (with their allowed enum fields bounded the same way), matching the
targeted-critic precedent. At the deterministic parse boundary, the two flag
fields SHALL additionally accept a closed, casefolded label set mapped to
booleans — `high`, `yes`, `true`, `elevated`, `needed`, `required` to `true`;
`low`, `none`, `no`, `false`, `minimal`, `minor`, `unlikely`, `not_needed` to
`false` — because real provider output expresses these flags as severity labels
(observed: `marketing_risk: "low"` blocking a real run). Any other value for
those fields — including the ambiguous `medium` — SHALL fail validation
fail-closed. (`EVC-001`)

#### Scenario: Valid source assessment is produced
- **WHEN** SourceDiagnostic runs with assigned accepted source refs and their content
- **THEN** a typed `SourceDiagnosticResult` is written with per-source trust tier, materiality, marketing risk, and cross-verification need, referencing only assigned source ids

#### Scenario: Severity-label flags normalize at the parse boundary
- **WHEN** SourceDiagnostic output carries `"marketing_risk": "low"` or `"cross_verification_need": "high"` instead of booleans
- **THEN** the deterministic parse boundary maps the closed label set to `false`/`true` respectively and the typed result materializes; the model output itself gains no authority beyond the mapped boolean

#### Scenario: Out-of-map label values fail closed
- **WHEN** SourceDiagnostic output carries a flag value outside the closed label set (for example `"medium"` or a novel token)
- **THEN** validation fails with the typed critic-boundary code, no review artifact is written, and the bounded repair path is entered rather than the value being guessed or truncated

#### Scenario: Expected output declares boolean flags
- **WHEN** the wave1 SourceDiagnostic request is built
- **THEN** its expected-output contract declares `marketing_risk` and `cross_verification_need` as booleans with the trust and materiality enums bounded, matching the targeted-critic precedent

#### Scenario: Fabricated source reference fails validation
- **WHEN** SourceDiagnostic output references a source id not in the assigned evidence set
- **THEN** the deterministic materializer rejects the output before writing any artifact

#### Scenario: Prompt-injected source yields honest assessment
- **WHEN** a source contains directives to claim high trust or suppress risk flags
- **THEN** the critic produces a limitation entry rather than elevating trust, and the deny-by-default tool policy blocks any attempted tool call
