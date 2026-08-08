# node-agent-capabilities Specification

> req: NAC-001, NAC-002, NAC-003, NAC-004, NAC-005, NAC-006, NAC-007, NAC-008, NAC-009

## Purpose
Define validated node-local cognitive capabilities, their four-layer prompt
composition, closed admission posture, and per-branch deterministic evidence without
granting graph or lifecycle authority to policy resources.
## Requirements
### Requirement: Migrated node-agent requests bind a validated local capability

A migrated direct phase-agent branch SHALL construct a frozen
`NodeAgentCapabilityRef` with a stable capability ID, a package identity rooted under
`deerflow_deep_research.graph.nodes`, and a simple relative Markdown name rooted at
that package's `capabilities/` directory. The ref SHALL reject an absolute path,
traversal, a non-Markdown name, or a package outside that node namespace. The
request SHALL carry one explicit capability binding with an exclusive ref invariant:
`legacy` SHALL carry no ref and retain the existing renderer path, while `required`
SHALL carry exactly one syntactically valid ref. Every other binding/ref combination
SHALL be rejected before node invocation. A migrated branch SHALL use `required`; an
unmigrated branch SHALL use `legacy` with no ref and SHALL receive no inferred
capability. The agents-owned loader SHALL validate a
first-line `<!-- node-agent-capability: <JSON object> -->` metadata comment of at
most 4 KiB UTF-8, strip it before rendering, and reject a remaining Markdown body over
16 KiB UTF-8. The comment SHALL decode to exactly a version-1 JSON object with only
`schema_version`, `capability_id`, `role`, `method`, `authority_limit`,
`completion_condition`, `uncertainty_boundary`, and `tool_posture`; unknown fields
SHALL be rejected and the capability ID SHALL match the ref. `tool_posture` SHALL be
exactly `{"kind":"forbidden"}` or
`{"kind":"required","allowed_tool_names":[...]}`. The required list SHALL be
non-empty, unique, and lexicographically sorted; the forbidden posture SHALL carry no
tool names. The remaining Markdown body is static policy text only. No parsed ref or
metadata field SHALL carry graph route data, checkpoint authority,
parser/evaluator/materializer selection, repair control, evidence selector, or a live
tool object. (`NAC-001`)

#### Scenario: A migrated request resolves its declared policy
- **WHEN** a first-cohort builder constructs a request for its declared capability
- **THEN** the loader returns the matching validated local policy before rendering and
  rejects a mismatched, escaping, missing, unknown, or malformed resource before
  model construction

#### Scenario: Parsed capability metadata cannot create graph authority
- **WHEN** a local capability metadata comment contains an unknown route,
  checkpoint, parser, repair, evidence, or live-tool field
- **THEN** validation rejects the resource before rendering; the Markdown body remains
  static policy text and no graph route, state write, tool dispatch, or parser
  selection is created by the resource

### Requirement: Capability composition keeps static cognition separate from dynamic assignment

For a migrated request, the agents-owned final renderer SHALL compose the exact base
safety policy, validated local capability policy, graph-provided trusted assignment
and expected-output contract, and delimited untrusted data in that order. The renderer
SHALL expose the validated capability projection needed by the runtime bridge but
SHALL NOT resolve configured tools, receive a runtime envelope, create a sandbox,
invoke a model, or accept an arbitrary full-system-prompt override. (`NAC-002`)

#### Scenario: Four prompt layers remain visible and ordered
- **WHEN** a deterministic catalog case renders a migrated request with source or
  tool-result references
- **THEN** its review projection identifies the capability ID and local source path
  and contains the base policy, capability policy, assignment/output contract, and
  delimited untrusted data in the declared order

#### Scenario: Dynamic assignment cannot replace static capability policy
- **WHEN** a caller supplies a trusted assignment containing prompt-like text or a
  legacy full-system-prompt parameter
- **THEN** the renderer treats assignment as its bounded layer and rejects the
  override parameter without replacing the validated base or capability policy

### Requirement: First cohort carries explicit capability admission without generic fallback

The first migration cohort SHALL contain exactly these direct catalog cases and
capability IDs:

| Catalog case | Capability ID | Package identity | Resource file | Tool posture |
| --- | --- | --- | --- | --- |
| `hitl1/semantic-intake` | `hitl1-semantic-intake` | `deerflow_deep_research.graph.nodes.hitl1` | `capabilities/hitl1-semantic-intake.md` | forbidden |
| `hitl1/semantic-intake-repair` | `hitl1-semantic-intake-repair` | `deerflow_deep_research.graph.nodes.hitl1` | `capabilities/hitl1-semantic-intake-repair.md` | forbidden |
| `wave0/worker` | `wave0-authoritative-source-intake` | `deerflow_deep_research.graph.nodes.wave0` | `capabilities/wave0-authoritative-source-intake.md` | required |
| `wave0/repair` | `wave0-source-intake-repair` | `deerflow_deep_research.graph.nodes.wave0` | `capabilities/wave0-source-intake-repair.md` | forbidden |
| `wave2-synthesis/synthesis` | `wave2-evidence-synthesis` | `deerflow_deep_research.graph.nodes.wave2_synthesis` | `capabilities/wave2-evidence-synthesis.md` | forbidden |
| `wave2-synthesis/repair` | `wave2-evidence-synthesis-repair` | `deerflow_deep_research.graph.nodes.wave2_synthesis` | `capabilities/wave2-evidence-synthesis-repair.md` | forbidden |

Each listed branch SHALL carry the declared capability reference and exact local
resource shown in the table. A missing, unknown, malformed, package-mismatched, or
resource-mismatched resource SHALL reach no model construction or tool dispatch; an
invalid binding, including a `required` binding without a reference, SHALL be rejected
before node invocation. Neither failure SHALL select a default or generic capability.
The closed temporary legacy set SHALL be exactly
`hitl1/brief`, `hitl1/brief-repair`, `targeted-evidence/claim-verifier`,
`targeted-evidence/repair`, `targeted-evidence/source-diagnostic`,
`targeted-evidence/worker`, `topic-planning/plan`, `topic-planning/plan-repair`,
`wave1/worker`, and `wave1/repair`; each SHALL use `legacy` with no ref and none
receives an inferred capability until its own cohort migrates it. The Wave2 normal
builder SHALL set `tools_enabled=false`, and `wave2_synthesis` SHALL bind a dedicated
zero-tool runtime policy rather than the HITL1 bridge policy. (`NAC-003`)

#### Scenario: Every first-cohort branch is independently admitted
- **WHEN** the prompt catalog and source-backed inventory inspect the first cohort
- **THEN** exactly the six listed cases have one explicit stable reference and local
  resource with the listed posture, exactly the named ten legacy cases have no ref,
  and no other branch is counted as migrated by owner-level aggregation

#### Scenario: Invalid capability binding is rejected before node invocation
- **WHEN** a first-cohort builder constructs `required` without a ref or `legacy`
  with a ref
- **THEN** request validation rejects the request without invoking a node, model,
  tool resolver, or tool dispatch

#### Scenario: Missing capability resource fails before agent-visible work
- **WHEN** a first-cohort request has a syntactically valid ref that names a missing
  or mismatched local resource
- **THEN** the deterministic admission boundary returns its typed non-success path
  without constructing a model, resolving a tool, or dispatching a tool call

### Requirement: Capability evidence is measured per branch, behavior, and authenticity

Test-owned capability evidence SHALL contain one matrix row per migrated direct
branch. Each row SHALL name its stable capability, source/catalog case, declaration
source, production entrypoint, and two distinct collected `TestEvidenceClaim` IDs:
one for success and one for the highest-risk behavior. The two claims SHALL resolve to
different selectors and retain their own deterministic authenticity. Static
declaration/resource and catalog checks SHALL remain distinct from recording-bridge
and scripted real-node evidence. A generic owner test, another branch's test, or an
aggregate pytest count SHALL NOT satisfy a row. (`NAC-004`)

#### Scenario: A required-tool branch proves actual binding and failure
- **WHEN** the `wave0/worker` row is evaluated
- **THEN** it includes a recording bridge or tool seam proving one permitted retrieval
  alternative binds and a separate scripted real-node journey proving no-permitted-
  tool failure or bounded repair without granting the model ledger or route authority

#### Scenario: Zero-tool branches do not inherit retrieval authority
- **WHEN** a HITL1 semantic or Wave2 synthesis/repair case is rendered and bound
- **THEN** its evidence rows prove that no model-visible tool is available and that
  malformed output follows its existing deterministic repair or failure owner

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

### Requirement: Planning and initial-intake branches carry a closed capability cohort

The next capability cohort SHALL migrate exactly the following six cases from
`legacy` to `required` bindings. Each listed resource SHALL be package-local; a
forbidden posture SHALL retain a required capability binding while exposing no
model-visible tool.

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
`REAL_NODE_FAKE_CAPABILITIES` claims. The required Wave1 worker resource SHALL declare only
`duckduckgo_search`, `firecrawl_scrape`, `jina_ai`, `tavily_extract`,
`tavily_search`, `web_fetch`, and `web_search`, in lexical order; the existing
Wave1 runtime policy remains the authority that supplies a configured subset or
reports no eligible tool. (`NAC-006`)

#### Scenario: The cohort resolves only its eight declared local policies
- **WHEN** the prompt catalog and production builders construct the planning and
  initial-intake cohort requests
- **THEN** topic planning, Wave0, and all four Wave1 normal, repair, and critic cases resolve their exact local resources and postures, the matrix contains fourteen exact direct branches, and every targeted-evidence branch remains legacy with no capability reference

#### Scenario: A migrated intake request cannot bypass admission
- **WHEN** a topic-planning or Wave1 request has an invalid required binding or local
  resource
- **THEN** validation fails before model construction or tool dispatch and neither a topic registry, work-unit submission, nor Wave1 review artifact is admitted

#### Scenario: Wave1 policy cannot widen runtime retrieval authority
- **WHEN** the declared Wave1 capability posture is compared with its existing runtime
  execution policy
- **THEN** its ordered allowed-name list is a non-empty subset of that policy, and a
  broader or malformed list fails before model construction or tool dispatch

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
SHALL retain its fourteen existing rows and add these four rows, producing eighteen unique
branches with separate normal and highest-risk `REAL_NODE_FAKE_CAPABILITIES` claims.
No deferred, readiness, final-delivery, planner, or Wave0 branch SHALL be
migrated or inferred by this cohort. (`NAC-007`)

#### Scenario: The final cohort resolves only its declared local policies
- **WHEN** the prompt catalog and production builders construct Wave2 and targeted
  evidence-evaluation requests
- **THEN** the six cases resolve their exact local resources and postures, the matrix contains eighteen exact direct branches, and all deferred or already completed branches retain their declared status

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

### Requirement: Capability evidence records the cognitive-program handoff per branch

Each current direct branch's test-owned ledger evidence SHALL join its canonical
catalog case to the existing local capability reference and distinguish local
capability policy from trusted inputs, untrusted observations, candidate shape,
deterministic admission, and route authority. It SHALL validate the case-ID and
capability binding against the existing closed cohort, and SHALL not infer a new
capability, tool, admission, recovery, or route behavior.

#### Scenario: Capability handoff is reviewed
- **WHEN** a branch capability is inspected with its prompt and bridge evidence
- **THEN** the reviewer can identify the existing deterministic admission owner and
  runtime enforcer without treating the ledger as either owner

### Requirement: Final report composition has an explicit local capability and evidence row

The `final-delivery/composer` direct branch SHALL bind one required package-local
capability with forbidden tool posture. Its test-owned capability evidence row SHALL
name the stable capability, source/catalog case, production entrypoint, and distinct
collected normal and highest-risk deterministic claims. The capability resource SHALL
not grant evidence selection, candidate admission, publication, recovery, route, or
lifecycle authority. (`NAC-009`)

#### Scenario: Composer policy is independently admitted
- **WHEN** a final-delivery composer request is rendered and inspected
- **THEN** it resolves only its declared local zero-tool capability and an invalid or
  missing binding reaches no model construction or artifact publication
