## Why

The accepted `REJ-011` requirement says a human-interrupt suspension is journaled as
suspension, "not unexpected failure", and its scenario says "the recorded outcome
identifies the attempt as suspended". The runtime wrapper already emits
`outcome="suspended"` on `GraphInterrupt`, but the persisted `RunEvent` model still
restricts `outcome` to `started | completed | failed`, so the durable recorder drops
every suspension inside `RunObservationStore` (a silently swallowed `ValueError`)
and the live observation projection relabels the same attempt as `failed`. Current
journal truth for suspensions therefore does not satisfy the accepted spec, and the
fake-recorder test that guarded REJ-011 never exercised the real persisted model.
Independently, the demo TUI's journal-derived live narration selects the most
recently updated active/suspended bundle in the whole workspace, so a concurrent
run, a historical suspended bundle, or a foreign run can be narrated as the current
run — exact correlation currently fails open at the presentation layer.

## What Changes

- Extend the persisted `RunEvent` outcome closed set with `suspended` on the existing
  schema version 3 event, reusing existing fields and version exactly as REJ-011
  requires; no new event category, no migration, and old events stay readable.
- Preserve `suspended` through every observation path: the live observation
  projection stops relabeling a suspended node attempt as `failed` (the live
  `ObservationOutcome` vocabulary gains the closed `suspended` value), while
  unexpected exceptions continue to persist `failed` + `internal.unexpected` and
  still propagate.
- Bind the demo TUI's journal-derived live narration (progress lines, event feed,
  last model-call state) to the exact Bundle identified by the session's shared
  updates. Before a session's updates identify a Bundle, narration degrades to the
  static working presentation and reads no other bundle. The RED-011 attach
  candidate listing keeps its bounded recency ordering; selecting a candidate is an
  exact bind.
- Add wrapper -> real Bundle recorder/store -> serialized `events.jsonl` -> reader
  integration evidence for `started -> suspended`; the fake-recorder test remains
  only as a local behavior test and is no longer REJ-011's proof.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `run-event-journal`: REJ-011 is tightened to name the persisted closed value
  `suspended` on the existing schema-version-3 outcome enumeration, to forbid the
  observation projection from relabeling suspension as failure, and to require the
  serialized round trip (`started -> suspended` readable from `events.jsonl`).
- `research-demo-tui`: new RED-012 requires journal-derived live narration to bind
  the session's exact Bundle and to fail closed to static working without an exact
  id; narration shows a suspended visit as suspension, not failure.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/domain/run_observation.py` owns the persisted `RunEvent` typed contract; `runtime/run_observation.py` and `runtime/events.py` own persistence and the live outcome vocabulary; `graph/builder.py` owns the wrapper's emitted facts; `scripts/demo_tui.py` owns presentation narration.
- **Seam classification:** wiring plus deterministic-guardrail fact truth: no node thinks differently, no route/topology changes; the change makes persisted and projected facts match what the wrapper already observed.
- **Question:** how can the journal and its live projection carry suspension truth (and only exact-correlated live narration) without changing graph authority, schema version, or the persisted reader compatibility rules REJ-002 already fixed?
- **Necessary adjacent/external contracts:** `run-event-journal` REJ-002 (schema version 3 remains the only reader-accepted version; unknown-outcome honesty) and REJ-011 (suspension distinction); `research-demo-tui` RED-003 (no local lifecycle inference — narration remains presentation color, never lifecycle state) and RED-011 (attach listing unchanged).
- **Evidence seam:** real-store integration test driving a fixture graph node through `GraphInterrupt` into `RunObservationStore.record_event` and reading back the serialized `events.jsonl`; builder unit seams for projection relabeling; TUI adapter tests with two coexisting bundles proving narration isolation and unbound static working.
- **Not in scope:** TraceFrame/projector design (C3), debug driving/lease (C4a), attach listing behavior change, retention priority changes, schema version bump, new event categories, and any `deerflow/` change.
- **Triggered review policies:** authority-and-projections, change-admission, participant-outcomes, local-context

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| What outcome a suspended node attempt carries | none; the wrapper already observed the interrupt | `RunEvent` typed contract + `ObservationOutcome` vocabulary | non-bypassable | observation never changes graph/route/terminal authority (existing swallow paths stay fail-safe) | removes the relabel-to-failed fiction; no second event category | real-store integration + builder projection unit tests |
| Which bundle live narration reads | none; the session's shared updates already carry the exact id | demo TUI narration binding from `snapshot.bundle_id` | non-bypassable | unbound narration degrades to static; no cross-bundle facts | removes workspace-wide latest-scan guesswork | TUI adapter isolation tests with two bundles |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Node suspends on human interrupt | wrapper emits `suspended`; store persists on v3 | lifecycle recovery owners unchanged | suspension is a pause awaiting recovery, never failure | resume/attach through existing lifecycle | integration round trip + no `internal.unexpected` |
| Observation persistence fails | store notes persistence failure | manifest health counters (existing) | graph/lifecycle outcome unchanged | diagnostics disclose degraded availability | persistence-failure injection test |
| Narration has no exact bundle id | shared updates own the id | presentation degrades to static | no narration is fabricated | operator sees static working until binding | TUI unbound test (no latest-scan read) |
| Old reader meets new suspended event | not applicable in-repo | declared coordinated cutover | pre-change readers reject the new value | revert commit restores old behavior; no data migration | reader-compatibility statement in design D1 |

## Impact

- Apply/sync will modify `openspec/specs/run-event-journal/spec.md` (REJ-011),
  `openspec/specs/research-demo-tui/spec.md` (new RED-012 + header), the
  requirement registry (RED-012 entry), `domain/run_observation.py`,
  `runtime/events.py`, `runtime/run_observation.py`, `graph/builder.py`,
  `scripts/demo_tui.py`, and focused tests.
- No new requirement ID beyond RED-012; no runtime route/topology/public API/
  checkpoint schema change; `deerflow/` untouched.
