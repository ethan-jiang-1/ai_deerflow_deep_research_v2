> req: NAC-001, NAC-002, NAC-003, NAC-004, NAC-005, NAC-006, NAC-007, NAC-008, NAC-009

## RENAMED Requirements

- FROM: `### Requirement: First cohort carries explicit capability admission without generic fallback`
- TO: `### Requirement: All current direct branches carry explicit capability admission without generic fallback`
- FROM: `### Requirement: Planning and initial-intake branches carry a closed capability cohort`
- TO: `### Requirement: Planning and initial-intake branches retain declared local capabilities`
- FROM: `### Requirement: Evidence-evaluation branches carry the final closed capability cohort`
- TO: `### Requirement: Evidence-evaluation branches retain declared local capabilities`

## MODIFIED Requirements

### Requirement: Migrated node-agent requests bind a validated local capability

Every direct LLM-Bearing Node request SHALL carry one frozen
`NodeAgentCapabilityRef` with a stable capability ID, a package identity rooted
under `deerflow_deep_research.graph.nodes`, and a simple relative Markdown name
rooted at that package's `capabilities/` directory. The ref SHALL reject an
absolute path, traversal, a non-Markdown name, or a package outside that node
namespace. A request without a ref SHALL be rejected at construction. The
agents-owned loader SHALL validate the ref, local resource, and first-line
metadata before it returns any final prompt text or permits runtime tool, model,
or agent construction. It SHALL reject a missing, escaping, unknown, malformed,
or package-mismatched resource and SHALL not infer a generic capability.

The metadata comment SHALL be at most 4 KiB UTF-8 and decode to exactly a
version-1 JSON object with only `schema_version`, `capability_id`, `role`,
`method`, `authority_limit`, `completion_condition`, `uncertainty_boundary`, and
`tool_posture`; unknown fields SHALL be rejected and the capability ID SHALL
match the ref. `tool_posture` SHALL be exactly `{"kind":"forbidden"}` or
`{"kind":"required","allowed_tool_names":[...]}`. The required list SHALL
be non-empty, unique, and lexicographically sorted; the forbidden posture SHALL
carry no tool names. The remaining Markdown body SHALL be static Node Cognitive
Control Program policy text only, at most 16 KiB UTF-8. No parsed ref or
metadata field SHALL carry graph route data, checkpoint authority,
parser/evaluator/materializer selection, repair control, evidence selector, or a
live tool object. (`NAC-001`)

#### Scenario: A request resolves its declared policy before execution work
- **WHEN** any production builder constructs a request with its declared capability
- **THEN** the loader returns the matching validated local policy before final prompt
  text, tool resolution, model construction, or agent construction, and rejects a
  missing, mismatched, escaping, unknown, or malformed ref/resource at that boundary

#### Scenario: A migrated request resolves its declared policy
- **WHEN** a current direct builder constructs a request for its declared capability
- **THEN** the loader returns that matching validated local policy before final prompt
  text, model construction, tool resolution, or agent construction

#### Scenario: Parsed capability metadata cannot create graph authority
- **WHEN** a local capability metadata comment contains an unknown route,
  checkpoint, parser, repair, evidence, or live-tool field
- **THEN** validation rejects the resource before prompt text is returned; the
  Markdown body remains static policy text and no graph route, state write, tool
  dispatch, or parser selection is created by the resource

### Requirement: Capability composition keeps static cognition separate from dynamic assignment

For every direct request, the agents-owned final renderer SHALL compose the exact
base safety policy, validated local Node Cognitive Control Program policy,
graph-provided trusted assignment and expected-output contract, and delimited
untrusted data in that order. The renderer SHALL expose the validated capability
projection needed by the node-agent runtime bridge but SHALL NOT resolve configured
tools, receive a runtime envelope, create a sandbox, invoke a model, or accept an
arbitrary full-system-prompt override. (`NAC-002`)

#### Scenario: Four prompt layers remain visible and ordered
- **WHEN** a deterministic catalog case renders a direct request with source or
  tool-result references
- **THEN** its review projection identifies the capability ID and local source path
  and contains the base policy, capability policy, assignment/output contract, and
  delimited untrusted data in the declared order

#### Scenario: Dynamic assignment cannot replace static capability policy
- **WHEN** a caller supplies a trusted assignment containing prompt-like text or a
  legacy full-system-prompt parameter
- **THEN** the renderer treats assignment as its bounded layer and rejects the
  override parameter without replacing the validated base or capability policy

### Requirement: All current direct branches carry explicit capability admission without generic fallback

The current direct-node catalog SHALL contain exactly twenty active branch cases.
Each case SHALL construct one request with its declared stable capability ref,
package-local resource, and required or forbidden tool posture. The source-backed
catalog and capability inventory SHALL agree on the exact twenty-case set and the
one-to-one case/ref/resource mapping. A missing, invalid, unknown,
package-mismatched, or resource-mismatched ref SHALL reach no final prompt text,
model construction, tool resolution, or tool dispatch. Neither failure SHALL select
a default or generic capability. (`NAC-003`)

#### Scenario: Every current branch is independently admitted
- **WHEN** the prompt catalog and source-backed inventory inspect current direct
  branches
- **THEN** exactly twenty cases each have one explicit stable ref and matching local
  resource with the declared posture, and no branch is counted through an owner
  aggregate or an inferred capability

#### Scenario: Every first-cohort branch is independently admitted
- **WHEN** the deterministic catalog and source-backed inventory inspect current
  direct branches
- **THEN** every current branch has its own declared ref/resource/posture mapping and
  none is admitted through a legacy, default, or aggregate path

#### Scenario: Invalid capability ref is rejected before node invocation
- **WHEN** a request is missing a ref or presents an invalid, unknown, or
  package-mismatched ref
- **THEN** request construction or prompt admission rejects it without invoking a
  node, model resolver, tool resolver, model, or tool dispatch

#### Scenario: Invalid capability binding is rejected before node invocation
- **WHEN** a request has no ref or supplies an invalid, unknown, or package-mismatched ref
- **THEN** construction or prompt admission rejects it without node invocation, model
  construction, tool resolution, or tool dispatch

#### Scenario: Missing capability resource fails before agent-visible work
- **WHEN** a request has a syntactically valid ref that names a missing or mismatched
  package-local resource
- **THEN** deterministic admission returns its typed non-success path without final
  prompt text, agent construction, model construction, tool resolution, or tool dispatch

### Requirement: Capability evidence is measured per branch, behavior, and authenticity

Test-owned capability evidence SHALL contain one matrix row per current direct
branch. Each row SHALL name its stable capability, source/catalog case, declaration
source, production entrypoint, and two distinct collected `TestEvidenceClaim` IDs:
one for success and one for the highest-risk behavior. The two claims SHALL resolve
to different selectors and retain their own deterministic authenticity. Static
declaration/resource and catalog checks SHALL remain distinct from recording-bridge
and scripted real-node evidence. A generic owner test, another branch's test, or an
aggregate pytest count SHALL NOT satisfy a row. (`NAC-004`)

#### Scenario: A required-tool branch proves actual binding and failure
- **WHEN** the `wave0/worker` row is evaluated
- **THEN** it includes a recording bridge or tool seam proving one permitted retrieval
  alternative binds and a separate scripted real-node journey proving no-permitted-
  tool failure or bounded repair without granting the model ledger or route authority

#### Scenario: Zero-tool branches do not inherit retrieval authority
- **WHEN** a forbidden-posture direct branch is rendered and bound
- **THEN** its evidence rows prove that no model-visible tool is available and that
  malformed output follows its existing deterministic repair or failure owner

### Requirement: HITL1 profile-brief branches carry distinct local capabilities

The `hitl1/brief` and `hitl1/brief-repair` catalog cases SHALL each use their
distinct package-local `NodeAgentCapabilityRef` and forbidden tool posture. Their
requests SHALL expose no tools, require zero minimum tool calls, and carry no
tool-call limit. (`NAC-005`)

#### Scenario: Brief requests resolve their exact local policies
- **WHEN** the two HITL1 brief catalog cases construct their production requests
- **THEN** each resolves only its declared capability resource and preserves the
  forbidden tool posture without a fallback capability

#### Scenario: Brief policy cannot accept research
- **WHEN** a brief or brief-repair capability metadata resource contains an unknown
  lifecycle, parser, or live-tool field
- **THEN** the loader rejects it before prompt text is returned, and only the existing
  HITL1 deterministic parser may admit a candidate as an advisory proposal

### Requirement: Planning and initial-intake branches retain declared local capabilities

The topic-planning, Wave0, and Wave1 planning and initial-intake catalog cases SHALL
each use their declared package-local capability ref and exact tool posture. The
current evidence matrix SHALL retain one independent row for every listed branch;
the case set SHALL be determined by the current catalog rather than a migration
cohort label. (`NAC-006`)

#### Scenario: Planning and intake requests resolve only declared local policies
- **WHEN** the planning and initial-intake cases construct their production requests
- **THEN** each resolves its exact local resource and posture, and a malformed or
  package-mismatched ref reaches no model construction or tool dispatch

#### Scenario: The cohort resolves only its eight declared local policies
- **WHEN** production builders construct planning, Wave0, and Wave1 current requests
- **THEN** each resolves only its declared local resource and posture, and the current
  evidence matrix retains its independent branch rows without a legacy fallback

#### Scenario: A migrated intake request cannot bypass admission
- **WHEN** a topic-planning or Wave1 request has a missing, invalid, or package-
  mismatched capability ref/resource
- **THEN** validation fails before model construction or tool dispatch and no topic,
  work-unit, Wave1 review artifact, route, or checkpoint authority is admitted

#### Scenario: Wave1 policy cannot widen runtime retrieval authority
- **WHEN** the declared Wave1 capability posture is compared with its node-agent
  execution policy
- **THEN** its allowed-name list is a non-empty subset of that policy, and a broader
  or malformed list fails before model construction or tool dispatch

### Requirement: Evidence-evaluation branches retain declared local capabilities

The targeted-evidence worker, repair, source-diagnostic, and claim-verifier catalog
cases SHALL each use their declared package-local capability ref and exact tool
posture. The current evidence matrix SHALL retain one independent row for every
case; no request may rely on a migration cohort label or a legacy fallback. (`NAC-007`)

#### Scenario: Evidence-evaluation requests resolve only declared local policies
- **WHEN** a targeted-evidence case constructs its production request
- **THEN** its exact local resource and posture resolve, and a missing, malformed,
  or package-mismatched ref is denied before runtime work begins

#### Scenario: The final cohort resolves only its declared local policies
- **WHEN** production builders construct Wave2 and targeted-evidence current requests
- **THEN** each resolves only its declared package-local resource and posture, and
  independent current evidence rows retain the exact branch set

#### Scenario: Invalid targeted binding cannot reach a model or ledger
- **WHEN** a targeted worker, repair, or critic has a missing, invalid, or package-
  mismatched capability ref/resource
- **THEN** validation fails before model construction or tool dispatch and no work-unit
  candidate, critic artifact, ledger submission, route, or checkpoint authority is admitted

#### Scenario: Required targeted policy cannot widen retrieval authority
- **WHEN** the targeted worker capability posture is compared with its existing
  node-agent execution policy
- **THEN** a broader, narrower, empty, duplicate, or malformed allowed-name list
  fails before model construction or dispatch

### Requirement: Capability evidence records the cognitive-program handoff per branch

For every current direct branch, the evidence ledger SHALL record its local Node
Cognitive Control Program capability, bounded question, trusted assignment facts,
untrusted data boundary, requested tool posture, bridge enforcement seam,
deterministic candidate/admission owner, and classified evidence links. A row SHALL
not give the capability graph routing, state-writing, repair, or lifecycle authority.
(`NAC-008`)

#### Scenario: Capability evidence preserves the deterministic handoff
- **WHEN** a reviewer inspects any direct branch row
- **THEN** the row identifies the validated capability and the existing deterministic
  owner that may admit its candidate without treating the capability as control flow

#### Scenario: Capability handoff is reviewed
- **WHEN** a branch capability is inspected with its prompt and bridge evidence
- **THEN** the reviewer can identify its deterministic admission owner and runtime
  enforcer without treating the ledger as either owner

### Requirement: Final report composition has an explicit local capability and evidence row

The `final-delivery/composer` catalog case SHALL construct one request with the
`final-delivery-composer` package-local capability ref and a forbidden tool posture.
It SHALL retain one independent current evidence row with its own deterministic
rendering, parsing, publication, and gate boundaries. (`NAC-009`)

#### Scenario: Final composition remains separately bounded
- **WHEN** the final-delivery composer request is built and rendered
- **THEN** it resolves only its declared local policy, exposes no model-visible tool,
  and is represented by its own evidence row rather than inheriting another branch's
  capability or proof

#### Scenario: Composer policy is independently admitted
- **WHEN** the final-delivery composer request is constructed and rendered
- **THEN** its declared capability is validated before prompt text, model construction,
  tool resolution, or agent construction, and its evidence remains independently joined
