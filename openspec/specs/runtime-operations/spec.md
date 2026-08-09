# runtime-operations Specification

> req: RUO-001, RUO-002, RUO-003, RUO-004

## Purpose
Harden non-interactive execution and recovery without changing topology or full-fake behavior.

## Requirements
### Requirement: Non-interactive mode requires policy

A trusted runtime that marks an input-bearing lifecycle request non-interactive with
the canonical `non_interactive=true` marker, or the existing trusted
`disable_clarification=true` compatibility marker, SHALL provide one closed
`non_interactive_policy` value with exactly the `auto_profile` and `auto_proceed` keys,
both set to the boolean value `true`. Missing keys, extra keys, false values,
non-boolean values, or a non-mapping policy SHALL be denied with
`INTERACTIVE_REQUIRED` before Bundle publication or graph mutation. The policy is a
validated trusted input value, not a public tool argument, caller-selected graph
option, or presentation decision. Only a new `start` may turn it into the typed action
input carried to graph execution; a later marked `resume` or `refine` remains subject
to the same validation but cannot create or replace a graph-state input.
`ResearchRunExperience` SHALL emit only the canonical marker.

Only a new `start` executed through a trusted-composed `BundleGraphExecutor` SHALL
write the admitted policy into initial graph values. The selected Bundle's graph
checkpoint SHALL own that value for all later graph work. A `resume` or `refine`
against an existing Bundle SHALL read the checkpointed value and SHALL NOT insert,
replace, or clear policy from a later runtime context. Policy admission SHALL NOT
instantiate or select a graph executor; an uncomposed fallback/full-fake lifecycle
retains its existing behavior. When the runtime does not mark an action
non-interactive, ordinary interactive behavior SHALL remain unchanged regardless of
an incidental policy-shaped context value.

#### Scenario: Non-interactive with policy is allowed
- **WHEN** trusted runtime context marks a new `start` non-interactive and contains
  `non_interactive_policy={"auto_profile": true, "auto_proceed": true}`, and trusted
  runtime composition supplies a `BundleGraphExecutor`
- **THEN** the lifecycle admits one typed action input, writes its policy only through
  initial graph values, and the resulting selected Bundle checkpoint owns the policy

#### Scenario: Compatibility marker uses the same closed policy
- **WHEN** trusted runtime context marks a new `start` with
  `disable_clarification=true` and contains a complete closed policy
- **THEN** the lifecycle applies the same non-interactive admission and denial rules
  as for the canonical `non_interactive=true` marker

#### Scenario: Policy admission preserves uncomposed fallback
- **WHEN** trusted runtime context marks a new `start` non-interactive and contains a
  complete closed policy, but no trusted-composed `BundleGraphExecutor` is available
- **THEN** the lifecycle retains its existing uncomposed fallback/full-fake behavior
  and does not create graph state from the policy

#### Scenario: Non-interactive without policy is denied
- **WHEN** a trusted runtime marks an input-bearing action non-interactive but the
  policy is absent, has an unknown or missing key, or either required value is not the
  boolean value `true`
- **THEN** the action returns `INTERACTIVE_REQUIRED` without publishing a Bundle,
  writing graph state, or creating a profile artifact

#### Scenario: Resume cannot reinject a policy
- **WHEN** a later `resume` or `refine` carries a complete policy-shaped context for
  an available Bundle that already has a graph checkpoint
- **THEN** the context passes the same closed validation but the invocation consumes
  only the checkpointed policy value, and the later context cannot replace or add a
  policy field

#### Scenario: Interactive mode is unaffected
- **WHEN** the runtime does not mark a lifecycle invocation non-interactive
- **THEN** the invocation follows the existing interactive path and a policy-shaped
  context value does not create non-interactive graph behavior

### Requirement: HITL nodes auto-respond under non-interactive policy

HITL1 SHALL consume `auto_profile` only from the selected Bundle's checkpointed
non-interactive policy. When enabled, HITL1 SHALL skip `interrupt()` and write its
existing degraded default profile only after applying the same deterministic comparison
and language admission rules as the interactive path. A required comparison pair SHALL
be present only when the local intake seed found an explicit valid pair in the original
request, and the accepted output language SHALL be locally supported rather than
defaulted. The resulting degraded profile SHALL retain those typed facts and append a
bounded audit entry to the existing execution trace.

When that policy is enabled but a supported comparison lacks an explicit valid pair, or
the request language requires a human `zh`/`en` choice, HITL1 SHALL NOT issue an
interrupt, write a profile artifact, write final profile fields, or fabricate a pair or
language. It SHALL take the existing terminal `GATE_BLOCKED` path. HITL2 SHALL consume
`auto_proceed` only from that same checkpointed policy. When enabled, it SHALL choose
the existing `proceed` route instead of its ordinary autonomous route recommendation
and append a bounded audit entry to the existing execution trace. When policy is absent,
both nodes SHALL retain their ordinary behavior.

#### Scenario: HITL1 auto-profile generates default profile
- **WHEN** the checkpointed `non_interactive_policy.auto_profile` is `true`, the local
  intake seed has supported language evidence, and it either does not require comparison
  subjects or contains an explicit valid pair
- **THEN** HITL1 writes the permitted degraded default profile with the typed intake
  facts, records its bounded audit entry, and routes to `accepted`

#### Scenario: Non-interactive generic comparison cannot acquire a default pair
- **WHEN** the checkpointed `non_interactive_policy.auto_profile` is `true` and a
  supported comparison request lacks an explicit valid pair
- **THEN** HITL1 blocks with `GATE_BLOCKED`, writes neither `profile.json` nor final
  profile fields, and does not fabricate a comparison pair

#### Scenario: Non-interactive unsupported language cannot acquire a default
- **WHEN** the checkpointed `non_interactive_policy.auto_profile` is `true` and the
  request language would require the interactive supported-language choice
- **THEN** HITL1 blocks with `GATE_BLOCKED` and writes neither `profile.json` nor final
  profile fields

#### Scenario: HITL2 auto-proceed routes to proceed
- **WHEN** the checkpointed `non_interactive_policy.auto_proceed` is `true`
- **THEN** HITL2 selects `proceed` and records its bounded audit entry without creating
  a user decision or a second route authority

#### Scenario: HITL nodes invoke interrupt normally when policy absent
- **WHEN** `non_interactive_policy` is absent from checkpointed graph state
- **THEN** HITL1 retains its ordinary interrupt behavior and HITL2 retains its ordinary
  autonomous route selection

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
