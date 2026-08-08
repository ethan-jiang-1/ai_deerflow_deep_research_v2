> req: EVH-011

## ADDED Requirements

### Requirement: Evidence layers are smallest-sufficient and distinct-risk

For each requirement changed by a test-evidence change, typed test-owned impact
metadata SHALL identify the owning contract, lowest responsible production seam,
normal edit-loop selector, and the risk each selected layer proves; its selector SHALL
resolve through the claim catalog and collected selection. A requirement normally uses
no more than one pure contract/unit layer, one runtime integration layer, and one
user-path/workflow layer; an additional layer, persisted replay, live dependency, or
full-real proof SHALL name a distinct risk that cannot be proven by the lower selected
seam. The active change `tasks.md` SHALL separately record the next smallest selector
and measured progress without treating prose status as task completion.

#### Scenario: Duplicate proof is rejected without a distinct risk
- **WHEN** a change proposes two evidence layers that assert the same behavior at the
  same responsible seam
- **THEN** the impact map requires one to be removed or records the distinct risk that
  justifies retaining it

#### Scenario: Escalated evidence is honest about its need
- **WHEN** a requirement uses trace replay, live dependencies, or full-real execution
- **THEN** its evidence record identifies the lower-seam gap and the bounded distinct
  risk the escalation proves

#### Scenario: Impact metadata cannot point at stale proof
- **WHEN** a typed requirement-impact entry names a selector not present in the claim
  catalog or its collected selection
- **THEN** deterministic evidence governance rejects the entry before it can claim
  coverage
