# project-structure Delta

> req: PRS-020

## ADDED Requirements

### Requirement: Dev-harness doc-layer hygiene occupies a canonical governance path with a deterministic checker

The canonical structure SHALL register `openspec/governance/check_doc_hygiene.py` as
the dev-harness doc-layer hygiene checker. The checker SHALL exit non-zero when a
registered doc-layer rule is violated — an ADR index that lists a missing file or
omits a present ADR, a relative link in an entry-chain document that does not resolve
to an existing file, or an entry-chain document that is not UTF-8 or lacks a trailing
newline — and SHALL exit zero on a clean tree. The checker SHALL provide a
`--self-test` negative-control mode that proves each rule fails on a planted
violation. The checker SHALL NOT be aggregated into the OpenSpec root governance gate
(the `project-structure` gate requirement owns the six-component closeout and forbids
a separate consistency checker) and SHALL NOT be wired into the Harness `make verify`
gate, which remains application-independent. (`PRS-020`)

#### Scenario: Clean tree exits zero

- **WHEN** the doc layer is clean — every ADR is listed in the index, every relative
  entry-chain link resolves, and the entry-chain documents are UTF-8 with a trailing
  newline
- **THEN** the checker exits zero

#### Scenario: ADR index drift is rejected

- **WHEN** the ADR index lists a file that is absent from `docs/adr/`, or a present ADR
  file is missing from the index
- **THEN** the checker exits non-zero and names the drifted file and the violated rule

#### Scenario: Broken entry-chain link is rejected

- **WHEN** an entry-chain document contains a relative markdown link that does not
  resolve to an existing file
- **THEN** the checker exits non-zero and names the document and the broken target

#### Scenario: Encoding or newline drift is rejected

- **WHEN** an entry-chain document is not UTF-8 decodable or lacks a single trailing
  newline
- **THEN** the checker exits non-zero and names the document and the violation

#### Scenario: Negative control proves each rule

- **WHEN** the `--self-test` mode runs
- **THEN** a clean fixture exits zero, and each rule's planted violation exits non-zero

#### Scenario: Gate and Harness composition stay unchanged

- **WHEN** the OpenSpec root governance gate and the Harness `make verify` gate run
- **THEN** neither gate invokes `check_doc_hygiene.py`, and their six-component and
  application-independent composition is unchanged
