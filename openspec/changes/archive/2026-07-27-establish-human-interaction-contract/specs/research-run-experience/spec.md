> req: RER-010, RER-011

## ADDED Requirements

### Requirement: Shared prompt view projects typed interaction facts and visible controls

ResearchRunExperience SHALL construct HITL1 proposal subject, material constraints,
feedback, and visible controls from the pending request's typed controller-owned
interaction projection, not by parsing `HumanInputRequest.context`. It SHALL retain a
safe legacy-context fallback for checkpoints that lack that projection. PromptView
shall expose only adapter-safe visible controls and SHALL not expose action ids; action
ids remain internal `HumanInputRequest` and verifier transport facts. (`RER-010`)

#### Scenario: Follow-up feedback retains its control in every adapter
- **WHEN** HITL1 returns semantic failure or clarification feedback
- **THEN** CLI and TUI receive the same subject, feedback, and current-proposal control
  through PromptView without decoding context or action ids

### Requirement: Runtime resolves generic visible-control selection under current state

ResearchRunExperience SHALL accept `SelectControlRun(control_id)` and, only against its
current pending request and displayed PromptView, bind it to the corresponding
advertised typed response. It SHALL reject a missing, stale, or unadvertised control
without constructing a response message. Existing direct typed `AnswerRun` remains
compatible for trusted transport callers. (`RER-011`)

#### Scenario: CLI control number does not become a magic phrase
- **WHEN** a CLI adapter submits the current numbered control selection
- **THEN** ResearchRunExperience performs the current trusted binding and no adapter
  converts a phrase such as `adopt suggestion` into an action id
