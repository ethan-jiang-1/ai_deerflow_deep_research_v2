> req: NAC-007

## ADDED Requirements

### Requirement: Evidence-evaluation branches carry the final closed capability cohort

The final direct-branch capability cohort SHALL migrate exactly these four
`targeted-evidence` catalog cases from `legacy` to required package-local bindings:

| Catalog case | Capability ID | Resource | Tool posture |
| --- | --- | --- | --- |
| `targeted-evidence/worker` | `targeted-gap-evidence-retrieval` | `capabilities/targeted-gap-evidence-retrieval.md` | required |
| `targeted-evidence/repair` | `targeted-gap-evidence-repair` | `capabilities/targeted-gap-evidence-repair.md` | forbidden |
| `targeted-evidence/source-diagnostic` | `targeted-source-diagnostic` | `capabilities/targeted-source-diagnostic.md` | forbidden |
| `targeted-evidence/claim-verifier` | `targeted-claim-verifier` | `capabilities/targeted-claim-verifier.md` | forbidden |

Every listed resource SHALL be local to
`deerflow_deep_research.graph.nodes.targeted_evidence`. The required worker resource
SHALL declare exactly `duckduckgo_search`, `firecrawl_scrape`, `jina_ai`,
`tavily_extract`, `tavily_search`, `web_fetch`, and `web_search`, in lexical order.
The existing Wave0 worker bridge policy remains the authority that supplies a
configured subset or reports no eligible tool. Wave2 synthesis and repair SHALL retain
their existing distinct required forbidden-tool bindings. The direct capability matrix
SHALL retain its twelve existing rows and add these four rows, producing sixteen unique
branches with separate normal and highest-risk `REAL_NODE_FAKE_CAPABILITIES` claims.
No deferred, readiness, final-delivery, planner, Wave0, or Wave1 branch SHALL be
migrated or inferred by this cohort. (`NAC-007`)

#### Scenario: The final cohort resolves only its declared local policies
- **WHEN** the prompt catalog and production builders construct Wave2 and targeted
  evidence-evaluation requests
- **THEN** the six cases resolve their exact local resources and postures, the matrix
  contains sixteen exact direct branches, and all deferred or already completed
  branches retain their declared status

#### Scenario: Invalid targeted binding cannot reach a model or ledger
- **WHEN** a targeted worker, repair, or critic has an invalid required binding or
  local resource
- **THEN** validation fails before model construction or tool dispatch and no work-unit
  candidate, critic artifact, ledger submission, route, or checkpoint authority is
  admitted

#### Scenario: Required targeted policy cannot widen retrieval authority
- **WHEN** the targeted worker capability posture is compared with its existing runtime
  execution policy
- **THEN** its ordered seven-name list exactly matches the existing Wave0 worker bridge
  policy, and a broader, narrower, empty, duplicate, or malformed list fails before
  model construction or dispatch
