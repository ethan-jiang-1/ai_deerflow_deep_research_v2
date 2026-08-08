> req: RER-007

## ADDED Requirements

### Requirement: Shared run updates project bounded intake feedback and observed run state

`ResearchRunExperience` SHALL project only validated versioned HITL1 intake facts into the shared `PromptView`: advisory-proposal availability, explicitly advertised action ids, recognized fields, missing fields including `must_answer`, bounded rejection feedback, accepted-answer rounds remaining, and rejection retries remaining. It SHALL not expose raw interrupt context, model output, or user answer text.

Every `Working` and terminal shared update SHALL expose only observed lifecycle facts: opaque run reference when available, durability, last committed phase, elapsed local time, and returned-only delivery mode. It SHALL distinguish local waiting from graph execution and SHALL make a terminal outcome's phase, category/reference, and inspection availability available to presentation adapters. (`RER-007`)

#### Scenario: Adapters share the same intake feedback
- **WHEN** HITL1 rejects a zero-recognition response
- **THEN** CLI and TUI receive the same bounded feedback/missing-field projection and neither adapter decodes raw lifecycle or interrupt data

#### Scenario: Waiting does not pretend to stream graph activity
- **WHEN** a real dispatch remains unresolved without a runtime stream event
- **THEN** consecutive working updates may advance elapsed local time but retain the same last committed phase and returned-only label

#### Scenario: Terminal update is operationally complete
- **WHEN** a record-bearing run returns `blocked`
- **THEN** its shared terminal update contains the known terminal phase, safe failure category/reference, durability, and safe retained-inspection availability without raw diagnostic data
