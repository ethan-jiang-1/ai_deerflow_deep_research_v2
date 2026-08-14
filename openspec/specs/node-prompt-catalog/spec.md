# node-prompt-catalog Specification

> req: NPC-001, NPC-002, NPC-003, NPC-004, NPC-005, NPC-006, NPC-007

## Purpose
The deterministic, reviewable catalog of final prompts used by graph-owned node-agent
requests.
## Requirements

### Requirement: Node Cognitive Control Program rendering has one source-faithful pure seam

The agents layer SHALL expose one pure renderer for the Node Cognitive Control
Program that accepts one validated request and virtual attempt workspace and
returns exact trusted system-policy text plus the exact final human message for an
LLM-Bearing Node invocation. It SHALL load the base policy and mandatory validated
capability policy from package resources, compose them with the graph-provided
assignment/output contract and delimited untrusted references, and expose the
validated capability projection for review. The node-agent bridge SHALL use this
renderer when it constructs its child messages, so no catalog or adapter duplicates
the final message template. The renderer SHALL reject a missing or invalid request
or capability ref before returning prompt text and SHALL not resolve tools, model,
runtime configuration, or lifecycle authority. (`NPC-001`)

#### Scenario: Direct prompt rendering is deterministic
- **WHEN** a test renders one direct request with a virtual attempt workspace and
  declared capability ref
- **THEN** it receives the same ordered trusted policy, assignment, and delimited
  untrusted-data layers that the runtime bridge will use, without model or tool work

#### Scenario: Capability admission fails before prompt projection
- **WHEN** a request is missing a ref or names an invalid, unknown, or package-
  mismatched local capability
- **THEN** the renderer raises its deterministic admission error and returns no final
  prompt projection, model binding, or tool inventory

#### Scenario: Catalog and bridge receive the same final prompt text
- **WHEN** one canonical node request has an objective, expected output, attempt
  workspace, source artifact references, and declared capability ref
- **THEN** the catalog renderer and node-agent bridge use the same system policy and
  final human message, including the bounded untrusted-artifact delimiter

#### Scenario: Rendering needs no runtime execution authority
- **WHEN** a prompt-catalog test renders a canonical case
- **THEN** no model, tool resolver, sandbox, provider, lifecycle graph,
  configuration, credential, user input, or external source body is accessed

### Requirement: Node prompts have a complete deterministic review catalog

The graph-owned prompt catalog SHALL define a stable, synthetic case for every top-level
node prompt-builder function in `graph/nodes/**/prompts.py` whose body directly
constructs a `NodeExecutionRequest`. A builder with a `repair_error` parameter SHALL
have both initial and repair cases; a dedicated repair builder SHALL have its repair
case. The catalog generator SHALL render only those cases through the shared rendering
interface. When an explicit reviewer runs `make prompt-dump`, it SHALL emit an ignored
local Markdown index and one stable case file below
`deep_research_harness/.node-prompt-review/`. The project SHALL not commit that tree or
register it as a required structural path. Each case file SHALL show the stable case
identity, exact system policy, exact final human message, and clearly labelled requested
tool state, minimum calls, and call limit. It SHALL not contain real-user text, runtime
configuration, provider data, credentials, sandbox identity, timestamps, or a locally
resolved tool inventory. (`NPC-002`)

`make prompt-dump-check` SHALL remain a read-only convenience wrapper over the same
generator check adapter. It SHALL validate an already generated local review tree and
report a missing, stale, unsafe, or unexpected tree without writing. It SHALL not be
selected by `UV_OFFLINE=1 make verify` as a committed-tree freshness baseline. Instead,
the focused fast deterministic selection SHALL retain source-level catalog-inventory,
shared-renderer, and temporary-tree generation checks; it SHALL neither require nor
create the ignored local review workspace.

#### Scenario: A reviewer creates an ignored prompt projection on demand
- **WHEN** a node prompt builder or shared policy changes and a reviewer runs `make prompt-dump`
- **THEN** the generator creates a deterministic projection only below `deep_research_harness/.node-prompt-review/`, Git ignores that workspace, and no runtime path reads it as prompt or execution authority

#### Scenario: Clean deterministic verification has no local-review prerequisite
- **WHEN** a clean checkout without `deep_research_harness/.node-prompt-review/` runs `UV_OFFLINE=1 make verify`
- **THEN** source-level catalog completeness and rendering evidence runs deterministically without creating or requiring the ignored workspace

#### Scenario: Explicit local review detects stale output without writing
- **WHEN** a reviewer has generated the local workspace and a file is stale, omitted, unsafe, or unexpected
- **THEN** `make prompt-dump-check` fails read-only; rerunning `make prompt-dump` is the bounded recovery and does not create a tracked change

### Requirement: Profile-brief catalog cases project local capability composition

The deterministic prompt catalog SHALL project `hitl1/brief` and
`hitl1/brief-repair` with their stable capability ID, package-local resource path,
ordered base/capability/assignment/untrusted-data layers, and forbidden requested-
versus-runtime tool posture. The committed catalog SHALL remain a generated review
projection and SHALL not become request or runtime authority. (`NPC-003`)

#### Scenario: Reviewers can distinguish proposal from repair policy
- **WHEN** the catalog renders both HITL1 brief cases
- **THEN** the projection identifies different local capability IDs and resources while
  retaining the same zero-tool runtime posture

### Requirement: Planning and initial-intake catalog cases project their local policies

The deterministic prompt catalog SHALL project the eight topic-planning, Wave0, and
Wave1 normal, repair, SourceDiagnostic, and ClaimVerifier cases with their exact
capability ID, local resource, ordered composition layers, requested tool posture, and
runtime tool-policy distinction. The catalog remains a generated review projection and
SHALL not grant a policy, prompt, or catalog case parser, controller, route, ledger, or
tool authority. (`NPC-004`)

#### Scenario: Reviewers can distinguish research-start roles
- **WHEN** the catalog renders the planning and initial-intake cases
- **THEN** it distinguishes zero-tool plan, repair, and critic policies from required-retrieval worker policies and identifies each local resource without resolving a live tool inventory or invoking a model

### Requirement: Evidence-evaluation catalog cases project local policy boundaries

The deterministic prompt catalog SHALL project Wave2 synthesis and repair plus the
four targeted-evidence worker, repair, SourceDiagnostic, and ClaimVerifier cases with
their exact capability ID, package-local resource, ordered composition layers,
requested tool posture, and runtime tool-policy distinction. The catalog SHALL remain
a generated review projection and SHALL not create a parser, validator, controller,
ledger, route, gate, or tool authority. (`NPC-005`)

#### Scenario: Reviewers can distinguish retrieval, repair, and critic roles
- **WHEN** the catalog renders evidence-evaluation cases
- **THEN** it identifies the one required-retrieval worker and the five zero-tool
  synthesis, repair, and critic policies without resolving a live tool inventory or
  invoking a model

### Requirement: Prompt catalog exposes branch-review facts without becoming prompt authority

The catalog SHALL continue to expose each current direct branch's stable synthetic
composition, local capability, and requested tool posture. The test-owned cognitive
program ledger SHALL join the catalog case ID to bridge-enforced posture and bounded
feedback facts; neither projection becomes the owner of runtime prompt selection,
tool availability, feedback, candidate admission, or model authority.

#### Scenario: Branch composition is inspected
- **WHEN** a maintainer opens a direct branch projection
- **THEN** they can review its exact composition facts and follow its ledger join
  without treating the catalog as runtime configuration or an admission authority

### Requirement: Final report composition has a deterministic catalog projection

The prompt catalog SHALL project the final-delivery composer with its stable case ID,
local capability, ordered base/capability/assignment/untrusted-data layers, and
forbidden requested tool posture. The projection SHALL remain a generated review
artifact and SHALL not select a prompt, evidence, parser, publisher, route, or
lifecycle result. (`NPC-007`)

#### Scenario: Composer projection is reviewable without runtime authority
- **WHEN** the catalog renders the final-delivery composer case
- **THEN** reviewers can inspect its bounded composition inputs and zero-tool posture
  without invoking a model, resolving runtime dependencies, or accessing evidence
