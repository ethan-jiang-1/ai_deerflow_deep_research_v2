> req: RUS-001, RUS-003

## MODIFIED Requirements

### Requirement: A canonical local run bundle is a discoverable derived session

The retained run-session store SHALL preserve its owner-only contained bundle, manifest,
trace, live-lock, and shared dispatch-lock behavior. After a record-bearing result is
privately bound by an operation-enabled profile, it MAY atomically maintain an owner-only
private index of opaque binding references and recipe-compatibility metadata. That index
is not a public registry, is never rendered by inspection, and is the only discovery
source for the broker; bundle paths and `list_sessions()` SHALL NOT be used to authorize
an operation. Binding metadata SHALL be staged without an active index before bundle
publication and activated only after successful retained-bundle publication; an activation
failure leaves the bundle inspection-only. The owner/profile index SHALL be bounded by
the retained-session capacity; under the root lease only an undiscoverable staged record
with no validated manifest reference may be reaped.

Before cleanup deletes an eligible validated unlocked bundle carrying an opaque binding
reference, it SHALL revoke the matching private binding and owner-index entry. A failed
revocation SHALL skip deletion; a later deletion failure leaves the bundle
inspection-only and SHALL downgrade its manifest's operation-binding projection to
unavailable. Cleanup SHALL not delete generic checkpoint rows or infer/rebind legacy
content. (`RUS-001`)

#### Scenario: A denial carrying an id does not create a session
- **WHEN** a validated control outcome exposes a research id but no status, phase, or
  generation
- **THEN** it remains a no-record result, creates no retained bundle, and any warranted
  diagnostic stays in the global journal

#### Scenario: First dispatch is protected before its first returned record
- **WHEN** real graph bootstrap materializes its workspace while the adapter is waiting
  for its first returned result
- **THEN** cleanup cannot acquire the root cleanup lock and cannot remove that content

#### Scenario: Metadata does not impersonate bootstrap output
- **WHEN** no valid regular real bootstrap marker exists after a record-bearing bind
- **THEN** the manifest reports `session_metadata_only` and no graph-owned request or
  research-content path is fabricated

#### Scenario: Public inspection cannot reveal a private binding target
- **WHEN** a developer inspects a retained session with an available lifecycle binding
- **THEN** output may state bounded binding availability and durability but never emits
  a user id, outer thread id, namespace, provider connection, or host path

#### Scenario: Cleanup cannot leave an operable orphan
- **WHEN** cleanup selects a retained bound bundle for deletion
- **THEN** it revokes the matching private operation entry before deletion, or safely
  skips the bundle when revocation cannot be confirmed

### Requirement: Local developer inspection resolves a safe run reference

Broker discovery MAY expose only a bounded operation availability projection and fixed
contained artifact references after owner-index and broker authorization. Existing `list`,
`inspect`, and `cleanup` remain separate legacy commands with their existing read-only or
retention semantics; the broker SHALL NOT use `list`/`inspect` bundle traversal as a
discovery source. The same local command may additionally expose profile-mediated
`discover`, `open <session_ref>`, `status <session_ref>`, `cancel <session_ref>`, and
`resume <session_ref> --request-id <opaque_id>` operations. The command constructs its
fixed current-profile broker before accepting a session reference, and `resume` reads its
raw answer from stdin rather than an argument or retained record. Legacy bundles remain
inspection-only, no artifact body is added, and the session store SHALL not infer a
binding from legacy content. Mutating local operations SHALL acquire the shared
retained-root dispatch lease with a bounded wait of at most 30 seconds; list, inspect,
discover, open, and status remain lock-free reads. (`RUS-003`)

#### Scenario: Developer inspects a paused run without resuming it
- **WHEN** a local demo reaches HITL and exits
- **THEN** inspection shows only the last verified state, fixed safe references, and
  honest durability/no-live-lock facts; it executes no graph action and promises no
  resume

#### Scenario: Unknown inspection has zero writes
- **WHEN** a developer supplies an unknown, malformed, cross-root, or traversal-like
  reference
- **THEN** inspection returns a bounded not-found or invalid-reference result without
  creating any retained-root filesystem object or invoking a sandbox, provider, or graph

#### Scenario: Cleanup may temporarily exceed its policy
- **WHEN** locked or corrupt contained candidates prevent count, age, or byte pruning
- **THEN** cleanup skips them, reports bounded skipped facts, and does not falsely
  report policy compliance or follow/delete an untrusted target

#### Scenario: Legacy session cannot be upgraded by discovery
- **WHEN** a retained bundle has no valid private binding
- **THEN** legacy inspection may show its inspection facts, while broker discovery omits
  it and never guesses, backfills, or rebinds it

#### Scenario: Command-line answer is never an authority or a process argument
- **WHEN** a user resumes an authorized selected session through the local command
- **THEN** the command reads one raw answer from stdin only after receiving an opaque
  expected request id, never echoes or persists that answer, and dispatches only if the
  broker validates the latest checkpointed pending request
