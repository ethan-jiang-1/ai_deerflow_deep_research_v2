> req: RUS-001, RUS-002, RUS-003

## ADDED Requirements

### Requirement: A canonical local run bundle is a discoverable derived session

The agent project SHALL provide a runtime-owned local run-session store below the
project-relative `agent/.deep-research-demo-runs/` root. It SHALL bind a bundle at
`workspace/deep-research/<research_id>/` only after a record-bearing validated returned
lifecycle result supplies non-null research id, status, phase, and generation.
Preflight, denial/no-record, malformed, and status-less results SHALL create no bundle
or session metadata. The store SHALL atomically publish version-1 `manifest.json`
containing only schema version, research id, creation/update times, local retention
state, lifecycle-provided durability classification, content-layout classification,
and fixed bundle-relative diagnostic references. It SHALL not contain checkpoint
provider details, state cursor, pending-input/answer body, credentials, provider body,
host path, URL, raw exception, or arbitrary state.

`content_layout=graph_materialized` SHALL require an existing regular no-follow
`request/marker.json` which validates as the real bootstrap marker. Every other case,
including a full-fake or failed-before-bootstrap real route, SHALL be
`session_metadata_only`; that store-created root may contain only `manifest.json` and
`diagnostics/`, and SHALL not fabricate request marker/profile, work, evidence,
synthesis, review, or final artifacts.

Before every lifecycle dispatch the adapter SHALL hold a shared retained-root cleanup
lock. Cleanup SHALL require the corresponding exclusive non-blocking root lock and
shall skip safely if unavailable. After bind, the publisher SHALL hold an advisory
per-bundle live lock until adapter close. No registry/index is created: validated ids
resolve only to their deterministic contained location. Manifest and lock data are
discovery/liveness observations only: graph nodes, lifecycle routing, resume
validation, and evidence acceptance SHALL never read them as control authority.

The retained root, workspace, bundle, and diagnostics directories SHALL be owner-only
`0700`. Manifest, trace, diagnostic, lock, and staging files SHALL be regular
owner-only `0600`; no-follow contained primitives SHALL reject symlink, nonregular, or
broader-mode components. All retained-root filesystem work SHALL run through
`asyncio.to_thread`. (`RUS-001`)

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

### Requirement: A bounded lifecycle trace records verified session facts

The runtime-owned session store SHALL append a redacted version-1
`diagnostics/lifecycle.jsonl` record only from a record-bearing validated returned
lifecycle fact. Each record has sequence `1..2^31-1`, timestamp, action, verified
trace delta, committed phase, bounded pending-input phase/mode/request-id summary,
terminal outcome, closed failure category, and diagnostic reference. A record SHALL be
at most 8 KiB; a complete snapshot SHALL be at most 2 MiB and retain at most 256
records. The trace SHALL not claim node/model/web streaming progress or retain raw
messages, prompt context, responses, provider payloads, URLs, host paths, credentials,
exceptions, or source-derived hashes. Under the session lock, each snapshot replacement
is individually atomic and preserves repeated verified phase visits.

There is no cross-file transaction among `manifest.json`, lifecycle trace, and optional
`diagnostics/records.jsonl`. For a post-bind classified failure, the store SHALL
individually publish the diagnostic record first, trace snapshot referring to it second,
and manifest last. Inspect SHALL validate each independently; a missing, stale,
malformed, or unavailable file is a bounded unavailable observation and SHALL NOT infer
a lifecycle result or a globally consistent snapshot. Trace failure SHALL not fabricate
success or mutate checkpoint control state. (`RUS-002`)

#### Scenario: A partial multi-file publication stays honest
- **WHEN** diagnostic publication succeeds but trace or manifest publication fails
- **THEN** inspection reports only independently verified available/unavailable facts
  and the original validated lifecycle result remains authoritative

#### Scenario: Interrupted trace replacement has no plausible tail
- **WHEN** replacement fails before publishing the next trace snapshot
- **THEN** inspection sees the prior complete trace or a closed unavailable outcome,
  never a parsed partial final JSONL record

### Requirement: Local developer inspection resolves a safe run reference

The project SHALL provide `make -C agent demo-sessions` with exactly `list`,
`inspect <research_id>`, and `cleanup`. `list` returns at most 20 entries and at most
20 skipped-entry summaries. Inspection resolves an opaque id only through its
deterministic contained local-root location and returns only an agent-relative bundle
location, `manifest.json`, `diagnostics/lifecycle.jsonl`, optional
`diagnostics/records.jsonl`, and verified existing `request/marker.json` and
`request/profile.json`, plus bounded summaries, retention state, and durability truth.
It SHALL never enumerate `work/`, evidence, caches, dynamic artifact paths, filenames,
or bodies, and ordinary output SHALL never reveal a raw host path.

Retention applies only to validated unlocked candidates: retain at most 20, no older
than 14 days from manifest creation time, and at most 1 GiB of recursive contained
bundle bytes. Cleanup prunes eligible candidates oldest first, skips locked/corrupt
candidates, and reports bounded skipped facts when they temporarily prevent the bounds
from being met. `list` and `inspect`, including unknown or malformed ids, are strictly
read-only: they create no directory, lock, staging file, repair, sandbox, provider, or
graph action. Discovery, inspection, and cleanup SHALL use no-follow contained opens
for all root, manifest, trace, diagnostics, locks, and candidates. (`RUS-003`)

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
