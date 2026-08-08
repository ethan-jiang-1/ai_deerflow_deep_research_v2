> req: RUS-002, RUS-003

## MODIFIED Requirements

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
success or mutate checkpoint control state.

An authorized runtime-owned workbench reader MAY transform only validated trace records
into a bounded timeline projection after the existing broker has returned an available
selected-session view. That broker authorization may use its established checkpoint
provider verification. The contained timeline reader SHALL omit trace deltas and all
raw/unknown fields, and SHALL not open an additional checkpoint provider, initialize a
sandbox, invoke a graph, or determine the current lifecycle state. (`RUS-002`)

#### Scenario: A partial multi-file publication stays honest
- **WHEN** diagnostic publication succeeds but trace or manifest publication fails
- **THEN** inspection reports only independently verified available/unavailable facts
  and the original validated lifecycle result remains authoritative

#### Scenario: Interrupted trace replacement has no plausible tail
- **WHEN** replacement fails before publishing the next trace snapshot
- **THEN** inspection sees the prior complete trace or a closed unavailable outcome,
  never a parsed partial final JSONL record

#### Scenario: Workbench timeline stays an observation
- **WHEN** an authorized workbench reads a validated retained lifecycle trace
- **THEN** it emits only bounded timeline facts and does not mutate, resume, cancel, or
  otherwise derive graph control from the trace

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
discover, open, and status remain lock-free reads.

An authorized runtime-owned workbench reader MAY map an existing fixed broker artifact
reference to a catalog key and then use the contained artifact-view contract. It SHALL
not use legacy inspection as authorization, accept an arbitrary relative path, enumerate
bundle contents, or add an artifact body to legacy inspection output. (`RUS-003`)

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

#### Scenario: Workbench catalog is not a bundle listing
- **WHEN** an authorized workbench opens a session with additional work or evidence
  files beneath its retained bundle
- **THEN** the catalog exposes only fixed broker-authorized references and does not
  enumerate or infer any additional filename or artifact body
