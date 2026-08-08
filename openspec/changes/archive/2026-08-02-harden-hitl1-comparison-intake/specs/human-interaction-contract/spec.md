## ADDED Requirements

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
