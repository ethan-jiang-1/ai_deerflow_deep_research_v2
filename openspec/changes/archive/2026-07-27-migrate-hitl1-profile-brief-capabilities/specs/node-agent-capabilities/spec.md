> req: NAC-005

## ADDED Requirements

### Requirement: HITL1 profile-brief branches carry distinct local capabilities

The second node-agent capability cohort SHALL migrate exactly the following catalog
cases. Each ref SHALL use package identity
`deerflow_deep_research.graph.nodes.hitl1`, the exact listed resource, and the
closed forbidden-tool posture:

| Catalog case | Capability ID | Resource |
| --- | --- | --- |
| `hitl1/brief` | `hitl1-profile-brief` | `capabilities/hitl1-profile-brief.md` |
| `hitl1/brief-repair` | `hitl1-profile-brief-repair` | `capabilities/hitl1-profile-brief-repair.md` |

Both requests SHALL use `required` bindings, `tools_enabled=false`, zero minimum tool
calls, and no tool-call limit. The remaining closed legacy set SHALL be exactly
`targeted-evidence/claim-verifier`, `targeted-evidence/repair`,
`targeted-evidence/source-diagnostic`, `targeted-evidence/worker`,
`topic-planning/plan`, `topic-planning/plan-repair`, `wave1/worker`, and
`wave1/repair`; none SHALL carry or infer a ref. (`NAC-005`)

#### Scenario: Brief requests resolve their exact local policies
- **WHEN** the two HITL1 brief catalog cases construct their production requests
- **THEN** each resolves only its declared local policy with no model-visible tool,
  and no remaining legacy request is counted as migrated

#### Scenario: Brief policy cannot accept research
- **WHEN** brief or repair metadata contains an unknown lifecycle, parser, or live-tool
  field
- **THEN** the capability loader rejects it before rendering; its Markdown body remains
  static policy text, and only the existing HITL1 typed parser can admit a model result
  as an advisory proposal
