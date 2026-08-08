> req: TEL-006

## ADDED Requirements

### Requirement: Targeted-evidence calibration preserves gap-scoped judgment boundaries

The targeted worker, its existing zero-tool repair, SourceDiagnostic, and ClaimVerifier SHALL
make model-visible the criteria for gap-scoped source/evidence candidates, provenance,
counterevidence, uncertainty, and honest non-resolution. The worker SHALL preserve its existing
single gate-projected gap and exactly-one retrieval posture. Its repair SHALL receive only the
same assigned gap, bounded draft, retained observations, and closed validation facts, and SHALL
not retrieve, add a source, fact, or gap identity, or receive ledger, artifact, gate, retry, or
route authority. Each critic SHALL receive only its assigned references and delimited untrusted
material. The existing validator, work-unit controller, materializer, ledger, convergence gate,
and graph route owners SHALL remain the only owners that admit candidates or decide outcomes.

#### Scenario: Calibrated targeted worker remains one-gap and provenance-bounded
- **WHEN** a targeted worker receives one gap projected by the current Wave2 gate
- **THEN** it makes only its existing one permitted retrieval and returns a candidate limited to
  that gap, observed source metadata, stated uncertainty, and resolution status, without changing
  findings, gap identity, ledger, convergence state, or route

#### Scenario: Repair and critics cannot broaden targeted evidence authority
- **WHEN** a targeted worker repair, SourceDiagnostic, or ClaimVerifier receives malformed,
  incomplete, or out-of-scope untrusted material
- **THEN** its zero-tool candidate remains constrained to its assigned gap or references, and an
  invalid or out-of-scope result produces no source/result/review artifact, ledger update, gate
  decision, or route authority

