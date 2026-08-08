## MODIFIED Requirements

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
