# runtime-operations Specification

> req: RUO-001, RUO-002, RUO-003, RUO-004

## Purpose
Harden non-interactive execution and recovery without changing topology or full-fake behavior.

## Requirements
### Requirement: Non-interactive mode requires policy

Non-interactive start/resume SHALL be denied unless a `non_interactive_policy` dict with `auto_profile` and `auto_proceed` boolean keys is provided in the runtime context. When the policy is present, it SHALL flow through `ResearchActionInput` into the initial graph state. Without policy, non-interactive SHALL be denied with `INTERACTIVE_REQUIRED` as before.

#### Scenario: Non-interactive with policy is allowed
- **WHEN** runtime context has `non_interactive=True` and `non_interactive_policy={"auto_profile": true, "auto_proceed": true}`
- **THEN** start/resume proceeds and the policy is written to checkpoint state via initial graph values

#### Scenario: Non-interactive without policy is denied
- **WHEN** runtime context has `non_interactive=True` but no `non_interactive_policy`
- **THEN** start/resume is denied with `INTERACTIVE_REQUIRED`

#### Scenario: Interactive mode is unaffected
- **WHEN** `non_interactive` is not set (default interactive)
- **THEN** start/resume proceeds normally regardless of policy presence

### Requirement: HITL nodes auto-respond under non-interactive policy

HITL1 SHALL check `state.get("non_interactive_policy", {}).get("auto_profile")`. When
True, HITL1 SHALL skip `interrupt()` and write its existing degraded default profile
only after applying the same deterministic comparison and language admission rules as
the interactive path. A required comparison pair SHALL be present only when the local
intake seed found an explicit valid pair in the original request, and the accepted
output language SHALL be locally supported rather than defaulted. The resulting
degraded profile SHALL retain those typed facts and record an audit note.

When that policy is enabled but a supported comparison lacks an explicit valid pair, or
the request language requires a human `zh`/`en` choice, HITL1 SHALL NOT issue an
interrupt, write a profile artifact, write final profile fields, or fabricate a pair or
language. It SHALL take the existing terminal `GATE_BLOCKED` path. HITL2 SHALL check
`auto_proceed` similarly. When True, HITL2 SHALL skip `interrupt()`, route to
`proceed`, and record an audit note.

#### Scenario: HITL1 auto-profile generates default profile
- **WHEN** `non_interactive_policy.auto_profile` is True, the local intake seed has
  supported language evidence, and it either does not require comparison subjects or
  contains an explicit valid pair
- **THEN** HITL1 writes the permitted degraded default profile with the typed intake
  facts and routes to `accepted`

#### Scenario: Non-interactive generic comparison cannot acquire a default pair
- **WHEN** `non_interactive_policy.auto_profile` is True and a supported comparison
  request lacks an explicit valid pair
- **THEN** HITL1 blocks with `GATE_BLOCKED` and writes neither `profile.json` nor final
  profile fields

#### Scenario: Non-interactive unsupported language cannot acquire a default
- **WHEN** `non_interactive_policy.auto_profile` is True and the request language would
  require the interactive supported-language choice
- **THEN** HITL1 blocks with `GATE_BLOCKED` and writes neither `profile.json` nor final
  profile fields

#### Scenario: HITL2 auto-proceed routes to proceed
- **WHEN** `non_interactive_policy.auto_proceed` is True
- **THEN** HITL2 routes to `proceed` with an audit note

#### Scenario: HITL nodes invoke interrupt normally when policy absent
- **WHEN** `non_interactive_policy` is None or absent from state
- **THEN** HITL1 and HITL2 invoke `interrupt()` as normal

### Requirement: Orphan attempts detected on recovery

On crash recovery, work attempts in `running` status whose owning work_spec generation is lower than the current graph generation SHALL be detected as orphaned and transitioned to `failed` with orphan reason.

#### Scenario: Orphan attempt from prior generation is cleaned up
- **WHEN** recovery detects a running attempt with generation 0 while the current graph generation is 1
- **THEN** the attempt is transitioned to `failed` with orphan reason

### Requirement: Cross-cutting changes do not alter topology or full-fake

Non-interactive policy SHALL NOT alter graph topology or full-fake behavior. Full-fake graph SHALL produce identical outputs.

#### Scenario: Full-fake graph unchanged
- **WHEN** the full-fake graph runs with runtime hardening changes
- **THEN** all nodes produce the same outputs as before
