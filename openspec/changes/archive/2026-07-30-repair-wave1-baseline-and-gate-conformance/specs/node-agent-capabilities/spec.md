> req: NAC-006, NAC-007

## MODIFIED Requirements

### Requirement: Planning and initial-intake branches carry a closed capability cohort

The next capability cohort SHALL migrate exactly the following six cases from `legacy`
to `required` bindings. Each listed resource SHALL be package-local; a forbidden posture
SHALL retain a required capability binding while exposing no model-visible tool.

| Catalog case | Capability ID | Package identity | Resource | Tool posture |
| --- | --- | --- | --- | --- |
| `topic-planning/plan` | `topic-planning-profile-decomposition` | `deerflow_deep_research.graph.nodes.topic_planning` | `capabilities/topic-planning-profile-decomposition.md` | forbidden |
| `topic-planning/plan-repair` | `topic-planning-plan-repair` | `deerflow_deep_research.graph.nodes.topic_planning` | `capabilities/topic-planning-plan-repair.md` | forbidden |
| `wave1/worker` | `wave1-evidence-extraction` | `deerflow_deep_research.graph.nodes.wave1` | `capabilities/wave1-evidence-extraction.md` | required |
| `wave1/repair` | `wave1-evidence-extraction-repair` | `deerflow_deep_research.graph.nodes.wave1` | `capabilities/wave1-evidence-extraction-repair.md` | forbidden |
| `wave1/source-diagnostic` | `wave1-source-diagnostic` | `deerflow_deep_research.graph.nodes.wave1` | `capabilities/wave1-source-diagnostic.md` | forbidden |
| `wave1/claim-verifier` | `wave1-claim-verifier` | `deerflow_deep_research.graph.nodes.wave1` | `capabilities/wave1-claim-verifier.md` | forbidden |

Wave0 worker and repair SHALL retain their existing required local bindings; its repair
posture remains forbidden. No targeted-evidence or Wave2 branch SHALL be inferred or
migrated by this cohort. The global capability-evidence matrix SHALL preserve its
existing eight rows and add these six rows, for fourteen unique direct branches total.
Every matrix row SHALL retain separate collected normal and highest-risk
`REAL_NODE_FAKE_CAPABILITIES` claims. The required Wave1 worker resource SHALL declare
only `duckduckgo_search`, `firecrawl_scrape`, `jina_ai`, `tavily_extract`,
`tavily_search`, `web_fetch`, and `web_search`, in lexical order; the existing Wave1
runtime policy remains the authority that supplies a configured subset or reports no
eligible tool. (`NAC-006`)

#### Scenario: The cohort resolves only its eight declared local policies
- **WHEN** the prompt catalog and production builders construct the planning and initial-intake cohort requests
- **THEN** topic planning, Wave0, and all four Wave1 normal, repair, and critic cases resolve their exact local resources and postures, the matrix contains fourteen exact direct branches, and every targeted-evidence branch remains legacy with no capability reference

#### Scenario: A migrated intake request cannot bypass admission
- **WHEN** a topic-planning or Wave1 request has an invalid required binding or local resource
- **THEN** validation fails before model construction or tool dispatch and neither a topic registry, work-unit submission, nor Wave1 review artifact is admitted

#### Scenario: Wave1 policy cannot widen runtime retrieval authority
- **WHEN** the declared Wave1 worker capability posture is compared with its existing runtime execution policy
- **THEN** its ordered allowed-name list is a non-empty subset of that policy, and a broader or malformed list fails before model construction or tool dispatch

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
SHALL retain its fourteen existing rows and add these four rows, producing eighteen
unique branches with separate normal and highest-risk `REAL_NODE_FAKE_CAPABILITIES`
claims. No deferred, readiness, final-delivery, planner, or Wave0 branch SHALL be
migrated or inferred by this cohort. (`NAC-007`)

#### Scenario: The final cohort resolves only its declared local policies
- **WHEN** the prompt catalog and production builders construct Wave2 and targeted evidence-evaluation requests
- **THEN** the six cases resolve their exact local resources and postures, the matrix contains eighteen exact direct branches, and all deferred or already completed branches retain their declared status

#### Scenario: Invalid targeted binding cannot reach a model or ledger
- **WHEN** a targeted worker, repair, or critic has an invalid required binding or local resource
- **THEN** validation fails before model construction or tool dispatch and no work-unit candidate, critic artifact, ledger submission, route, or checkpoint authority is admitted

#### Scenario: Required targeted policy cannot widen retrieval authority
- **WHEN** the targeted worker capability posture is compared with its existing runtime execution policy
- **THEN** its ordered seven-name list exactly matches the existing Wave0 worker bridge policy, and a broader, narrower, empty, duplicate, or malformed list fails before model construction or dispatch
