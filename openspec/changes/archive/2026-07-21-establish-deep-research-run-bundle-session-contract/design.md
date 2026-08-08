## Context

The current local `DemoAdapter` creates its workspace in a `TemporaryDirectory` and
deletes it when the CLI or TUI closes. The graph correctly creates
`workspace/deep-research/<research_id>/`, but a developer cannot locate it after
the run. `ResearchRunExperience` has a safe `research_id` and verified trace in
memory, while presentation surfaces expose neither as a stable inspection handle.
The external diagnostic JSONL is intentionally failure-only and cannot describe a
normal run.

The canonical bundle, checkpoint, and submission ledger already have distinct
authority. This design makes the bundle discoverable without changing those
authorities or treating a filesystem record as graph control state.

## Goals / Non-Goals

**Goals**

- Retain local demo bundles under a bounded, developer-accessible root.
- Publish a safe run manifest and a redacted lifecycle trace for each retained run.
- Provide one opaque run reference and local inspect/list commands for developers.
- Present the same reference and retention truth through CLI/TUI shared run updates.
- Keep lifecycle trace, manifest, checkpoint, ledger, and artifact authority
  mechanically separate and testable.

**Non-Goals**

- Automatic cross-process resume, a new lifecycle action, or a checkpoint provider
  migration.
- Gateway, Web, production DeerFlow CLI, multi-user discovery, permissions, or a
  workbench.
- Raw provider requests, prompt/answer bodies, URLs, host paths, or exceptions in
  a manifest or trace.
- A generic event stream or node/model/web progress claims before a verified event
  exists.

## Decisions

### A run reference is opaque; one local command resolves it

The public handle is the existing `research_id`. Ordinary CLI/TUI output may show
that opaque reference and inspectability status, but never a host filesystem path.
Once a reference exists, both adapters show this exact developer command:

```text
make -C agent demo-sessions DEMO_ARGS="inspect <research_id>"
```

The `demo-sessions` command supports exactly `list`, `inspect <research_id>`, and
`cleanup`. `inspect` prints the run reference, an agent-relative bundle location,
the fixed manifest/diagnostic paths, bounded summaries, retention state, and
durability truth. It never prints artifact bodies, raw diagnostics, or a host path.

This preserves the existing opaque identity and avoids making a host path part of a
wire contract. Printing the temporary path directly was rejected because it is both
unstable and unsafe outside a local developer process.

### One retained local root, no registry, and a bounded cleanup protocol

The demo adapter always uses the project-local root
`agent/.deep-research-demo-runs/`, ignored only by the newly owned `agent/.gitignore`;
it is not configurable by an environment variable or product configuration. Its sandbox workspace is
`agent/.deep-research-demo-runs/workspace/`, so the retained bundle has exactly this
location:

```text
agent/.deep-research-demo-runs/workspace/deep-research/<research_id>/
```

Before every lifecycle dispatch, the adapter holds the retained root's shared cleanup
lock. Cleanup takes that same root lock exclusively and non-blocking, and skips its
work when the lock is unavailable. This protects the graph-owned bundle materialized
during a first dispatch before any result has safely bound a session. The session store
binds a bundle only after a record-bearing validated result supplies all of
`research_id`, `status`, `phase`, and `generation`; it never derives an id from
presentation state. Denials, preflight failures, malformed results, and status-less
errors create no session bundle and use only the global diagnostic journal. Once bound,
the publisher holds that bundle's owner-only live lock until adapter close. No index is
created: the validated id deterministically resolves to its contained bundle path.

`content_layout=graph_materialized` is earned only when the trusted contained workspace
already has an existing, regular, no-follow `request/marker.json` that validates as the
real bootstrap marker. Any absence, malformed marker, failed-before-bootstrap real
route, or full-fake route is `session_metadata_only`. For the metadata-only case, the
store may create only the contained root, `manifest.json`, and `diagnostics/`; it never
creates `request/marker.json`, `request/profile.json`, work, evidence, synthesis,
review, or final content on behalf of the graph. This preserves the one-way authority
of real bootstrap while still making lifecycle evidence inspectable.

The root retains at most 20 validated and unlocked candidates, candidates no older
than 14 days by manifest creation time, and at most 1 GiB measured as recursive,
contained bundle bytes. Tests inject smaller policy values. Cleanup validates paths
without following links, skips locked or corrupt candidates, and prunes eligible
candidates oldest first. Locked/corrupt candidates may temporarily exceed a policy;
the bounded cleanup report states the skipped facts rather than claiming that bounds
were achieved. A bundle is closed only when its live lock is no longer held; the
manifest's retention state is descriptive and never a liveness authority. A crashed
process releases its OS lock and may become eligible because the demo has no
cross-process execution authority. `list` returns at most 20 entries and at most 20
skipped-entry summaries.

The retained root, workspace, bundle, and diagnostics directories are owner-only
`0700`. Manifest, trace, diagnostic, lock, and staging files are regular owner-only
`0600`. No-follow validation rejects symlink, nonregular, or broader-mode components.
Every retained-root filesystem operation runs in `asyncio.to_thread`.

Retention is inspectable-content retention, not a claim that every retained run can
resume. The old temporary-root approach was rejected because it makes real artifacts
disappear; unbounded retention was rejected because it turns local demos into an
uncontrolled cache.

### Manifest and trace are derived views

The runtime owns frozen domain contracts and contained atomic stores for:

```text
<bundle>/manifest.json
<bundle>/diagnostics/lifecycle.jsonl
```

`manifest.json` is version 1 and records only schema version, research id,
creation/update time, local retention state, the lifecycle-provided durability
classification, and the fixed relative references to `diagnostics/lifecycle.jsonl`
and optional `diagnostics/records.jsonl`. It does not contain a checkpoint-provider
reference: provider names, DSNs, namespaces, and file locations are unnecessary for
inspection and may be sensitive.

Each version-1 `lifecycle.jsonl` record has a sequence in `1..2^31-1`, timestamp,
action, verified trace delta, committed phase, bounded pending-input phase/mode/id
summary, terminal outcome, closed failure category, and diagnostic reference. A record
is at most 8 KiB; a snapshot is at most 2 MiB and retains at most 256 records. Under
the per-bundle lock the store atomically replaces a complete bounded JSONL snapshot
after semantically appending a validated result-derived delta, preserving repeated
phase visits without a torn trailing record. It never claims node/model/web streaming
progress.

There is no cross-file transaction. For a post-bind classified failure, the store
atomically publishes the diagnostic record first, then the trace snapshot referring
to it, then the manifest. Inspection validates each file independently: a missing,
stale, malformed, or unavailable file is a bounded unavailable observation, never a
lifecycle inference or claim of a globally consistent snapshot. Failures before a
record-bearing bind retain the existing project-relative support journal because no
bundle can be trusted or discovered. A diagnostic fingerprint is computed only from
closed safe fields (action, phase, category, certainty, and mode), never raw
exceptions, messages, prompts, answers, provider data, or their hashes.

Both records are projections. Graph nodes and lifecycle routing never read them to
choose a phase, validate a human response, or restore a run. The authoritative
checkpoint stays the only control source, and the submission ledger stays evidence
authority. A manifest is preferred over a `state.json` because it makes discovery
explicit and limits the contents to references rather than copied control state.

### Publication is best-effort observation, never a competing result

A runtime-owned session module validates references, creates only a safe
session-metadata root when graph content is absent, writes the manifest/trace, applies
retention, and returns a safe `RunSessionView`. `ResearchRunExperience` projects that
view into `RunSnapshot`; CLI/TUI render it without filesystem or lifecycle-wire
parsing. The demo adapter only supplies the retained workspace and keeps the advisory
lock.

`DemoAdapter` constructs a runtime-owned `RunSessionPublisher` from its trusted
envelope and selected retained root, then passes only that protocol into
`ResearchRunExperience`; scripts never construct paths or parse persisted records.
`handle()` awaits all required publication and final cleanup before returning its run
update. All session filesystem work, including atomic write, journal read/trim,
retention scan, and diagnostic publication, runs through `asyncio.to_thread`. CLI
`finally` may await the close protocol without masking the primary lifecycle outcome.
Textual `on_unmount()` only synchronously releases locks already finalized by the
handle/close protocol; it is never relied on for async I/O or final publication.

Publication happens after lifecycle decoding and cannot replace an authoritative
`AwaitingInput`, `Terminal`, or source `Fault`. If persistence or later inspection
fails, that update still carries the validated lifecycle result plus a bounded
`RunSessionView` with `inspectability=unavailable` and a closed observation category.
No response is retried, no checkpoint state changes, and no prompt is hidden merely
because observability failed.

This avoids both presentation-owned filesystem logic and a second session state
machine. A CLI-only implementation was rejected because it would leave the TUI and
future entry points inconsistent.

### Redaction is schema-level, not best-effort formatting

Manifest, trace, diagnostic, and session-view contracts are frozen, extra-forbid
models with bounded strings and closed enum values. Writers accept typed
lifecycle/control projections rather than raw `Command`, messages, errors, provider
responses, or contexts. Tests inject sentinel secrets, paths, URLs, questions, and
raw exceptions; they assert neither literal content nor a source-dependent fingerprint
reaches retained records or inspect output.

All discovery, inspection, locking, and cleanup open the retained root and child
directories with no-follow contained-path primitives. `list` and `inspect`, including
unknown or malformed ids, are strictly read-only: they create no root, bundle, lock,
staging file, repair, sandbox, provider, or graph action. Inspect output is a fixed
whitelist: agent-relative bundle location, `manifest.json`,
`diagnostics/lifecycle.jsonl`, optional `diagnostics/records.jsonl`, and only verified
existing `request/marker.json` / `request/profile.json`; it never enumerates `work/`,
evidence, dynamic paths, filenames, or bodies. Symlinks, malformed JSONL tails, and
unexpected entries are closed safe inspection/cleanup outcomes; they are neither
followed nor interpreted as run content.

EOF or `KeyboardInterrupt` at a CLI-owned paused prompt is a local presentation event,
not a graph lifecycle record. The last verified returned record remains authoritative;
the CLI may render a local interruption message and the exact inspect command before
closing, while later inspection may report last verified state and no-live-lock facts
without claiming a graph transition or resume capability.

## Risks / Trade-offs

- [A retained manifest becomes a state authority] -> bind only after a record-bearing
  lifecycle result; graph/lifecycle readers never consult it; add denial and
  status-less-result tests.
- [Local root and trusted sandbox diverge] -> bind the root through the existing
  trusted adapter/workspace mapping and run mount/containment checks before writes.
- [Retention deletes an active or first-dispatch run] -> hold the shared root lock
  through each dispatch, require and skip per-bundle live locks, and make cleanup
  non-blocking, explicit, and bounded.
- [Observability hides a usable HITL prompt] -> preserve the already validated
  lifecycle update and attach an unavailable-inspection state instead of converting it
  to an unrelated persistence fault.
- [An opaque hash becomes a secret oracle] -> construct diagnostic fingerprints from
  only closed safe values; prove source changes do not change the fingerprint.
- [A crash leaves a plausible but torn trace] -> atomically replace a complete bounded
  JSONL snapshot, document no cross-file transaction, and refuse malformed tails
  during inspection.
- [A local symlink escapes the retained root] -> use no-follow contained opens and
  reject symlinked manifests, traces, diagnostic paths, and cleanup candidates.
- [Useful trace leaks sensitive data] -> typed allowlist, fixed byte/count bounds,
  and sentinel-redaction tests at store, CLI, TUI, and inspect seams.
- [Inspection is mistaken for resume] -> manifest/CLI/TUI always expose a separate
  inspectability and durability classification; no resume command ships here.

## Migration Plan

1. Add contracts and deterministic stores/inspection/cleanup tests, including
   permissions, no-follow handling, marker classification, and cross-file partial
   availability.
2. Add the shared `ResearchRunExperience` publisher protocol before changing the
   adapter, then migrate diagnostics according to record-bearing bind state.
3. Switch fake and real demo roots to the retained root with root-dispatch and
   per-bundle locks; establish only metadata content where no valid bootstrap marker
   exists.
4. Add thin inspect/list/cleanup and shared CLI/TUI rendering; migrate deterministic
   tests to injected temporary retained roots.
5. Verify deterministic fake/replayed-real evidence. Run credentialed start-to-HITL
   acceptance only when preflight and credentials are available; otherwise record its
   safe preflight skip. Retained artifacts stay inert and are never used for routing or
   resume.
