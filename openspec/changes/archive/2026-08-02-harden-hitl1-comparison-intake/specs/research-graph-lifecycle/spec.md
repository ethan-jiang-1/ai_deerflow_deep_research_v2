## ADDED Requirements

### Requirement: HITL1 language selection is a correlated bounded option response

The lifecycle wire contract SHALL support a HITL1 `CHOICE` request only for an explicit
supported-language selection whose option identifiers and values are a closed language
set. A matching `OPTION` response SHALL include the current request id and one
advertised option id; trusted lifecycle validation SHALL reject stale, forged, missing,
or non-language options before HITL1 executes. Existing HITL2 choice identifiers and
responses SHALL remain wire-compatible and distinct from HITL1 language options.

The HITL1 language option SHALL not be a generic action id, visible-control alias, or
free-text phrase-to-action mapping. The selected option is an input candidate only;
HITL1 retains validation, profile mutation, and route authority. Existing text HITL1
requests and retained version-1 interrupts SHALL remain readable.

#### Scenario: Current language option is accepted as input rather than an action
- **WHEN** a current HITL1 language-choice request receives its advertised Chinese
  option with the matching request id
- **THEN** lifecycle delivers one correlated option response to HITL1 and does not
  fabricate an action id or graph route

#### Scenario: Stale language option fails before node execution
- **WHEN** a language option from an earlier HITL1 request is submitted after a new
  correlated request is pending
- **THEN** lifecycle rejects the response and leaves the checkpoint unchanged
