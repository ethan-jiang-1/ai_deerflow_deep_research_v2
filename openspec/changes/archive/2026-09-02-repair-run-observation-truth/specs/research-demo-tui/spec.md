> req: RED-012

## ADDED Requirements

### Requirement: Journal-derived live narration binds the session's exact Bundle

During a dispatched run, the demo TUI's journal-derived live narration (progress
lines, rolling event feed, and last model-call state) SHALL read only the exact
Bundle that the session's shared updates identify by Bundle id. It SHALL NOT
select a narration source by scanning the workspace for the most recently updated
active or suspended Bundle. Until the session's updates identify a Bundle, live
narration SHALL degrade to the static working presentation and SHALL NOT read any
other Bundle's journal. A suspended node visit SHALL be narrated as awaiting
recovery, never as completed or failed. The startup attach candidate listing
keeps its bounded recency ordering; selecting a candidate is an exact bind.
(`RED-012`)

#### Scenario: Narration never shows another Bundle's facts
- **WHEN** two active or suspended Bundles coexist in the workspace and the
  session's updates identify one of them
- **THEN** live narration exposes only the identified Bundle's sequence, phase,
  and facts, and never the other Bundle's events

#### Scenario: Unbound narration stays static
- **WHEN** a dispatch is running and the session's updates have not yet
  identified a Bundle id
- **THEN** the TUI shows the static working presentation and reads no Bundle
  journal through a latest-activity scan

#### Scenario: A suspended visit is narrated as awaiting recovery
- **WHEN** the bound journal contains a node attempt whose outcome is `suspended`
- **THEN** live narration names that phase as suspended/awaiting recovery and
  does not count it as completed or failed
