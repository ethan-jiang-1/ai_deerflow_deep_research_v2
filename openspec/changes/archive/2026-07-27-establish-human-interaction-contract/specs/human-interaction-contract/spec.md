> req: HIC-001, HIC-002, HIC-003

## ADDED Requirements

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
