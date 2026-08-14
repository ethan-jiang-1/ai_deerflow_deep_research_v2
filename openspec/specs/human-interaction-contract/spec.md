# human-interaction-contract Specification

> req: HIC-001, HIC-002, HIC-003, HIC-004

## Purpose

Defines the bounded semantic interpretation, visible-control projection, and safe
human recovery contract for a complete current HITL proposal.
## Requirements
### Requirement: HITL proposal interaction has one bounded semantic contract

The domain layer SHALL define frozen, extra-forbid contracts for a current proposal
subject, closed human candidate intent, semantic candidate, resolution, feedback,
visible control, and interaction projection. The contract SHALL validate bounded
human-safe proposal values, full revision shape, feedback text, and unique control ids.
It SHALL not contain a graph route, request id, checkpoint writer, raw response text,
provider observation, action id, or runtime handle. (`HIC-001`)

#### Scenario: A complete revision remains a candidate
- **WHEN** semantic intake proposes a complete changed profile
- **THEN** the domain resolution identifies it as a revision requiring fresh
  confirmation rather than a final profile or graph action

#### Scenario: Unsafe candidate data is rejected
- **WHEN** a semantic result includes an unknown intent, partial revision, action id,
  or oversized text
- **THEN** contract validation fails before graph state or presentation projection is
  changed

### Requirement: Proposal interaction preserves legal user recovery

For a current complete proposal, the domain projection SHALL expose a human-safe
subject, any closed bounded feedback, and a visible current-proposal control. A question,
clarification, ambiguity, malformed semantic output, or semantic-provider failure SHALL
preserve the current proposal and its visible control. The projection SHALL not teach a
hidden action token or require JSON for ordinary confirmation. (`HIC-002`)

#### Scenario: Semantic failure retains a visible fallback
- **WHEN** semantic intake exhausts its permitted calls for a reply
- **THEN** the next projection retains the same proposal and exposes a numbered
  current-proposal control with closed failure feedback

### Requirement: Proposal questions have bounded recommendation explanations

An `ask_about_proposal` semantic candidate SHALL return only a bounded explanation of
why a proposed setting fits the supplied question and current proposal. It SHALL not
claim research findings, cite external sources, create a new requirement, or alter the
proposal. (`HIC-003`)

#### Scenario: A cost question does not turn into research output
- **WHEN** a user asks why the proposal selected a moderate cost tolerance
- **THEN** the interaction feedback explains that recommendation within its bounded
  proposal context and keeps every proposal field unchanged

### Requirement: HITL1 deterministic proposal presentation remains action-oriented

For a complete current-proposal interaction, the deterministic presentation context
and node-generated semantic-invalid or semantic-unavailable feedback SHALL retain the
current proposal and its visible control. They SHALL be bounded and state only an
ordinary confirmation/revision/question choice or a legal recovery. They SHALL NOT
teach a hidden action token, expose raw candidate JSON, or require schema or JSON
syntax. Validated model-produced proposal explanation and clarification text remain
bounded candidates governed by `HIC-003`; this requirement does not claim a scripted
fake candidate proves live language quality. Complete-proposal context SHALL NOT
duplicate the trusted action id; the corresponding `HumanInputRequest.action_ids` and
`InteractionProjection.controls` remain the action-binding and visible-control owners.
(`HIC-004`)

#### Scenario: Complete proposal context supports ordinary confirmation
- **WHEN** HITL1 presents a complete current proposal before a person replies
- **THEN** its deterministic context and visible control allow ordinary confirmation,
  revision, or a proposal question without schema/JSON instruction or a duplicated
  action token, while its trusted request action binding and visible control remain
  available

#### Scenario: Closed semantic fallback avoids schema instruction
- **WHEN** semantic intake returns a node-generated invalid or unavailable fallback
- **THEN** the next projection keeps the same proposal/control and gives bounded
  recovery feedback without raw candidate JSON, action-token instruction, or
  schema/JSON teaching

#### Scenario: Revision constraints remain in the proposal rather than feedback
- **WHEN** a person revises the proposal to require first-party sources and citations
- **THEN** the new visible advisory proposal contains those profile constraints and the
  lifecycle presentation keeps the revision pending later confirmation

### Requirement: Incomplete comparison and language intake has no premature acceptance control

For a HITL1 proposal that lacks a required typed comparison pair or accepted supported
output/interaction language, the human-interaction contract SHALL project the bounded
missing fact and its human-safe follow-up. It SHALL not project
`accept_current_proposal`, a hidden action token, an advisory default pair, or a
model-selected language. A complete proposal SHALL render its typed comparison and
language facts as material subject values so that a later visible acceptance control
means acceptance of those facts.

An unsupported or ambiguous request-language result SHALL be projected as the existing
correlated human-input choice surface with only the supported language options. That
option projection remains a presentation/selection contract: it SHALL not own a graph
route, request correlation, profile write, or output-language default. HITL1 remains
the admission owner after it receives the correlated typed option response.

#### Scenario: Missing pair has a focused recovery without a generic start action
- **WHEN** the current HITL1 profile requires comparison subjects but has none
- **THEN** the next projection identifies that missing fact and exposes no
  current-proposal acceptance control

#### Scenario: Complete proposal displays accepted language and pair
- **WHEN** a current HITL1 proposal contains a valid comparison pair and language
  preference
- **THEN** its human-safe subject renders both facts before the visible
  current-proposal acceptance control is available

### Requirement: Canonical profile parsing proposes candidates without compatibility inference

The canonical profile parser SHALL return the bounded parse result consumed by current
HITL1 semantic admission. It SHALL not retain a duplicate convenience projection or
use absent/legacy persisted schema conventions to manufacture a current profile,
proposal, visible control, route, or lifecycle fact. Invalid or extra raw input remains
subject to the existing bounded candidate rejection and visible-recovery contract.
(`HIC-001`, `HIC-002`, `HIC-004`)

#### Scenario: Canonical result does not become a lifecycle fact directly
- **WHEN** raw profile text is parsed successfully
- **THEN** the result remains a bounded candidate until the existing HITL1 admission
  path accepts it, and no parser convenience surface creates a checkpoint or control

#### Scenario: Rejected old input preserves current visible recovery
- **WHEN** an unsupported persisted profile/proposal shape is encountered before a
  current semantic interaction can be admitted
- **THEN** it creates no replacement proposal/control or inferred profile fact, while
  the existing legal recovery behavior remains available only from valid current State
