> req: CPE-001

## MODIFIED Requirements

### Requirement: Every active direct branch has an individual evidence ledger row

The six active logical nodes SHALL maintain one test-owned cognitive-program evidence
row for each current direct model branch. The row IDs SHALL equal both the canonical
prompt-catalog case IDs and `COHORT_EVIDENCE` case IDs exactly. Each row SHALL record
product responsibility, bounded question, trusted/untrusted input boundary, capability
binding, catalog and final-render seam, requested tool window, bridge-enforcement seam,
feedback disposition and recipient when one exists, candidate/admission owner, guardrail
evidence, classified evidence links, and evaluation disposition. A node aggregate,
grouped row, or catalog count SHALL not close a missing branch row; the ledger SHALL
remain a review projection and SHALL not select a prompt, tool, route, model, candidate,
or lifecycle result.

#### Scenario: Branch inventory is reviewed
- **WHEN** maintainers review active cognitive evidence
- **THEN** they can establish exact eighteen-branch coverage, including `wave1/source-diagnostic` and `wave1/claim-verifier`, and identify the composition, feedback, guardrail, and evaluation-disposition proof for each branch
