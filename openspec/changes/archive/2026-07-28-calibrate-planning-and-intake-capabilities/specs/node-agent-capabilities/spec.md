> req: NAC-006

## ADDED Requirements

### Requirement: Planning and initial-intake branches carry a closed capability cohort

The next capability cohort SHALL migrate exactly the following four cases from
`legacy` to `required` bindings. Each listed resource SHALL be package-local; a
forbidden posture SHALL retain a required capability reference while exposing no
model-visible tool.

| Catalog case | Capability ID | Package identity | Resource | Tool posture |
| --- | --- | --- | --- | --- |
| `topic-planning/plan` | `topic-planning-profile-decomposition` | `deerflow_deep_research.graph.nodes.topic_planning` | `capabilities/topic-planning-profile-decomposition.md` | forbidden |
| `topic-planning/plan-repair` | `topic-planning-plan-repair` | `deerflow_deep_research.graph.nodes.topic_planning` | `capabilities/topic-planning-plan-repair.md` | forbidden |
| `wave1/worker` | `wave1-evidence-extraction` | `deerflow_deep_research.graph.nodes.wave1` | `capabilities/wave1-evidence-extraction.md` | required |
| `wave1/repair` | `wave1-evidence-extraction-repair` | `deerflow_deep_research.graph.nodes.wave1` | `capabilities/wave1-evidence-extraction-repair.md` | forbidden |

Wave0 worker and repair SHALL retain their existing required local bindings; its repair
posture remains forbidden. No targeted-evidence or Wave2 branch SHALL be inferred or
migrated by this cohort. The global capability-evidence matrix SHALL preserve its
existing eight rows and add these four rows, for twelve unique direct branches total.
Every matrix row SHALL retain separate collected normal and highest-risk
`REAL_NODE_FAKE_CAPABILITIES` claims. The required Wave1 resource SHALL declare only
`duckduckgo_search`, `firecrawl_scrape`, `jina_ai`, `tavily_extract`,
`tavily_search`, `web_fetch`, and `web_search`, in lexical order; the existing
Wave1 runtime policy remains the authority that supplies a configured subset or
reports no eligible tool. (`NAC-006`)

#### Scenario: The cohort resolves only its six declared local policies
- **WHEN** the prompt catalog and production builders construct the planning and
  initial-intake cohort requests
- **THEN** topic planning, Wave0, and Wave1 normal/repair cases resolve their exact
  local resources and postures, the matrix contains twelve exact direct branches, and
  every targeted-evidence branch remains legacy with no capability reference

#### Scenario: A migrated intake request cannot bypass admission
- **WHEN** a topic-planning or Wave1 request has an invalid required binding or local
  resource
- **THEN** validation fails before model construction or tool dispatch and neither a
  topic registry nor a work-unit submission is admitted

#### Scenario: Wave1 policy cannot widen runtime retrieval authority
- **WHEN** the declared Wave1 capability posture is compared with its existing runtime
  execution policy
- **THEN** its ordered allowed-name list is a non-empty subset of that policy, and a
  broader or malformed list fails before model construction or tool dispatch
