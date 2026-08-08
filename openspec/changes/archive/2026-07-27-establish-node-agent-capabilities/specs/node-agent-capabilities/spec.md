> req: NAC-001, NAC-002, NAC-003, NAC-004

## ADDED Requirements

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
