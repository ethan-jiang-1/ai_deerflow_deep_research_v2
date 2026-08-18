## MODIFIED Requirements

### Requirement: HITL1 adapts model-led confirmation without granting model authority

The pre-existing non-interactive auto-profile path remains outside the interactive
admission boundary. It SHALL construct the profile from the declared non-interactive
intent: when `profile_intent=minimal`, the written profile carries research depth
`quick_overview`, cost tolerance `minimal`, and time budget `very_quick` (still
marked degraded, no model call); when the intent is absent, the current degraded
profile behavior is unchanged. In both cases the profile SHALL seed
`must_answer=(request_text,)` — an automatic run that omits it currently produces
an empty final report (observed). The existing `single_topic` planner derivation
then forces exactly one topic under the minimal intent, so wave0/wave1 each run
one work unit and cross-topic synthesis stays trivial. The auto branch keeps its
existing blocked behavior when typed comparison scope or language facts are
missing. Interactive HITL1 journeys and the 002 scripted-template path are
unchanged. (`HIN-014`)

#### Scenario: Model-led natural confirmation starts research through the existing path
- **WHEN** HITL1 has shown a complete model-led proposal and receives a correlated
  natural-language confirmation of that proposal
- **THEN** it writes only the admitted current profile through its existing profile
  publication path and follows its existing accepted route without requiring a JSON
  profile response or an adapter action alias

#### Scenario: A semantic revision remains advisory
- **WHEN** semantic intake returns a valid complete revision for a correlated reply
- **THEN** HITL1 persists and renders the revised proposal as one outstanding User
  Decision, requires a later confirmation, and writes no profile artifact

#### Scenario: Semantic fallback keeps lifecycle ownership unchanged
- **WHEN** the existing semantic-intake bridge reaches its bounded unavailable or
  invalid-output fallback
- **THEN** HITL1 preserves the current outstanding User Decision and its typed
  feedback without delegating retry, terminal disposition, or checkpoint authority
  to Research Confirmation

#### Scenario: Declared minimal intent produces the single-topic profile
- **WHEN** a non-interactive start with `auto_profile` declares `profile_intent=minimal`
- **THEN** the written profile carries depth `quick_overview`, cost tolerance
  `minimal`, and time budget `very_quick`, is marked degraded, and the topic
  planner is required to emit exactly one topic

#### Scenario: Absent intent keeps the current degraded profile
- **WHEN** a non-interactive start with `auto_profile` declares no intent
- **THEN** the current degraded profile behavior is unchanged

#### Scenario: Auto profile always carries the must-answer question
- **WHEN** a non-interactive start with `auto_profile` writes a profile
- **THEN** the profile's `must_answer` contains the request text, so the readiness
  critic produces per-question verdicts and the final report plan is non-empty

#### Scenario: Over-long auto request fails closed
- **WHEN** a non-interactive start with `auto_profile` submits a request longer
  than the must-answer question bound (256 characters)
- **THEN** HITL1 blocks without writing a profile artifact, matching the existing
  typed-fact blocked path, and never truncates the request

#### Scenario: Auto profile missing typed facts still blocks
- **WHEN** a non-interactive start with `auto_profile` lacks required comparison
  subjects or output language
- **THEN** HITL1 blocks without writing a profile artifact, unchanged from current behavior
