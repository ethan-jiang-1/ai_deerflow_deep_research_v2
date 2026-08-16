## Context

See [proposal.md](proposal.md) for motivation. The verified current real CLI and real
TUI mode both bind `DemoLifecycleTransport` to a locally composed all-real graph.
Fixture CLI/TUI routes are separate and deterministic. Project-owned local profiles
already validate isolated configuration and launch the unchanged upstream stack, while
the public Deep Research skill and dedicated `deep-research` Agent already own the
normal Gateway entry workflow.

The archived predecessor owns the only approved runtime event type. At the unchanged
DeerFlow pin, the Harness captures the public injected `ToolRuntime.stream_writer`
once and reduces it to the predecessor-owned opaque sink; no custom-event convenience
helper is available or required. DeerFlow's public HTTP interface creates a thread and
streams a run through
`POST /api/threads/{thread_id}/runs/stream`; LangGraph custom stream records appear on
the SSE `custom` channel. Standard logs remain on process `stderr`, and trace logging
plus durable history are restart-scoped profile configuration.

## Goals / Non-Goals

**Goals:**

- Preserve the existing shared typed lifecycle/presentation contract while replacing
  the default real CLI/TUI transport with the configured public Gateway entry.
- Normalize the public SSE stream through one bounded runtime adapter and prove that
  presentation cannot create lifecycle or recovery authority.
- Add secure deployment-layer capture of the unchanged Gateway stack's `stderr` and
  retain DeerFlow's trace-correlated logging behavior.
- Make nested event forwarding a falsifiable admission condition after the predecessor
  archives.

**Non-Goals:**

- Do not change runtime event fields, fact owners, Bundle Journal, graph State, retry,
  route, terminal semantics, or Deep Research lifecycle controls.
- Do not support arbitrary remote/authenticated Gateway deployments in this Change;
  the first observer targets a selected project-owned local profile.
- Do not implement SSE history/replay, acknowledgement, deduplication authority, a
  polling observer, or any private Gateway adapter.
- Do not change DeerFlow source or its gitlink.

## Decisions

### Consume the archived predecessor without reopening it

Apply verified that `add-deerflow-native-live-event-projection` is archived and its
`deep_research.progress.v1` contract is in the main specs. This Change never
duplicates or conditionally redefines that payload. If the predecessor is not archived,
no Gateway forwarding or presentation work starts.

This one-way dependency replaces the former reciprocal plan among separate upgrade,
emission, and entrypoint records. No DeerFlow upgrade or helper admission remains in
this Change.

### Put the public HTTP/SSE boundary in one runtime adapter

Add `runtime/gateway_observer.py` as the single owner of public thread creation, run
stream request construction, structured SSE decoding, safe correlation retention, and
transport observations. Use `httpx` plus the explicitly declared `httpx-sse` package;
do not hand-parse lines or import Gateway implementation modules.

The adapter selects only a validated project profile and fixed configured
`assistant_id=deep-research`. Its only origin is the profile-launched direct local
Gateway `http://127.0.0.1:8001`; `:2026`, a proxy, and a caller-supplied origin are
outside this Change. A non-scripted `StartRun` asks that Gateway to create a fresh
thread, then starts one turn with the operator's explicit text. Only a later explicit
follow-up in that same observer process may use the returned thread id. A new start
never reuses a prior thread, and the observer never deletes a prior thread. The thread
id is process-local continuation context, not a Bundle locator or durable session
record. Caller-supplied thread/run/Bundle/checkpoint identity is rejected.

Using the Python in-process `DeerFlowClient` was rejected because it bypasses the
Gateway boundary whose StreamBridge, trace middleware, RunStore, and Console claims
this Change must prove. A raw `httpx` line parser was rejected because SSE framing,
multi-line data, heartbeat, and cursor behavior deserve a maintained structured parser.

### Preserve the shared experience through a Gateway lifecycle transport

The runtime adapter exposes a transport implementation compatible with the existing
`ResearchRunExperience` dispatch boundary. A non-scripted start, a typed answer, or a
selected current control value becomes one public turn to the configured Agent. The
adapter sends the exact entered text or the selected advertised value only; its local
`action`, `bundle_id`, and `context` parameters never become Gateway request fields or
tool arguments. During the stream, the adapter:

- retains only public metadata correlation;
- forwards bounded transport/progress observations to a separate presentation
  callback;
- displays only safe assistant text chunks;
- ignores tool arguments and all non-Deep-Research tool results; and
- validates the returned `deep_research` ToolMessage payload through the existing
  typed lifecycle result parser before returning it to `ResearchRunExperience`.

The configured Agent and public skill may propose one lifecycle call, but existing
tool schema, trusted runtime, Bundle State, and lifecycle handlers remain the only
admission/effect authorities. The observer never calls a lifecycle endpoint directly.
An absent or invalid typed result yields a bounded unknown/fault presentation even if
the outer SSE stream emits `end` or assistant prose sounds conclusive.

The Gateway transport rejects `StartRun(scripted=True)`, any non-empty dispatch
context, and a local `CancelRun`, `StatusRun`, or `RefineRun` dispatch before a new
public turn request. These are not lost Gateway features: an operator may type an explicit
ordinary-language cancellation, status request, or direction as the next user turn,
and the configured Agent may then propose the appropriate public tool call. The real
TUI therefore hides its local cancel button; fixture and embedded-smoke routes retain
their graph-owned cancellation behavior.

### Keep transport observations separate from lifecycle state

The adapter recognizes only `metadata`, `messages-tuple`, `custom`, `error`, `end`,
heartbeat, and gap. Before the forwarding proof, a valid
`deep_research.progress.v1` on `custom` is a withheld validation candidate: focused
fixtures and the one bounded integration probe may observe it, but no real CLI/TUI
presentation callback receives it. Unknown event names, malformed data, unsafe fields,
duplicate/reordered progress, and non-Deep-Research tool messages are dropped or
projected as bounded transport conditions.

Heartbeat means connection liveness. Gap/disconnect means the live window is
incomplete. `end` means the Gateway turn ended. None means Deep Research completed,
failed, remains active, or should be retried. The existing typed lifecycle result is
the only source for those presentations. The adapter retains no replay database,
cursor authority, acknowledgement, or dedupe state.

### Cut over both real entrypoints and leave fixtures unchanged

`scripts/demo_real.py` and real mode of `scripts/demo_tui.py` select the Gateway
transport by default and require a valid explicit `--profile` label. They no longer
call local model/Tavily readiness or build the local all-real graph. `--question`,
shared typed prompts/results, and explicit follow-up input remain. A missing or invalid
profile label, or a Gateway-default `--scripted` invocation, reports the bounded
preflight problem and exits before a Gateway request; it does not reinterpret a fixed
question as consent to fabricate follow-up input. The embedded-smoke selection retains
the existing `--scripted` behavior and local provider preflight.

Fixture CLI/TUI paths retain their current graph composition and credential-free
behavior. The current local all-real composition may remain only behind an explicit
embedded-smoke selection, where its banner, help, tests, and docs deny Gateway
history/trace/SSE claims. Keeping an implicit fallback was rejected because a failed
Gateway preflight must not silently change execution architecture.

### Make profile readiness the Gateway claim boundary

Extend the existing structured profile validation rather than adding observer-local
configuration parsing. A profile advertised for observation must prove:

- `logging.enhance.enabled: true` and JSON format;
- a documented durable local history backend rather than memory;
- existing public skill and dedicated-Agent entry readiness; and
- a healthy `http://127.0.0.1:8001/health` Gateway endpoint.

The entry prerequisite uses the existing project-owned
`configure.execute_configuration(..., mode="check")` with the selected profile's
already validated launch environment. It is zero-mutation and must report both
`runtime_config_ready=True` and `entry_status="ready"`; `unknown` and `not_ready`
are observation-preflight failures, not permission to send credentials, query an
authenticated Agent API, or mutate configuration. Profile checks remain redacted. The
observer consumes a validated safe profile result and fixed local endpoint, not raw
YAML or credentials. Provider model/web credentials remain in the Gateway environment;
the observer does not require or inspect them.

### Use the current root configuration as the only preparation baseline

This repository is in active local development and has one supported configuration
shape: the current root `config.yaml`. Preparation reads its `config_version` as the
only baseline, keeps the selected profile as the AppConfig/config-upgrade target, and
requires their versions to be exactly equal before synchronizing the backend or
installing the Harness. This is an internal consistency check for the current local
setup, not a backward- or forward-compatibility policy. The static
`deerflow/config.example.yaml` is an upstream sample only and neither selects nor
overrides the local baseline. Missing, malformed, or unequal versions fail with a
redacted preparation error; no DeerFlow upgrade, runtime root-config fallback, or
manual editable-install bypass is admitted.

### Tee process stderr at the profile launcher

`scripts/local_profiles.py` remains the owner of local profile launch. Replace its
direct exec only for profile launch with a project-owned child-process supervisor that
starts the unchanged upstream `serve.sh --dev --skip-install`, preserves terminal
signals and exit status, and tees child `stderr` bytes to both the inherited `stderr`
and one owner-only rotating process log family.

The launcher creates `.deep-research-demo-runs/logs/` with `0700`, opens files with
`0600` and no symlink following, prints the absolute base path before starting the
child, uses collision-resistant process naming, and performs bounded inactive-log
retention without deleting files held by live launch locks. Capture errors close only
the file side and continue inherited `stderr`; they never restart or terminate the
Gateway solely because capture failed.

A Python logging handler inside the application was rejected because DeerFlow owns
root logging/trace formatting and the intended boundary is deployment capture of the
already formatted `stderr` stream. A Bundle-local file was rejected because it would
be sandbox-visible and a second persistence contract.

### Require an actual nested forwarding proof before enabling progress

After deterministic decoder/entrypoint/profile evidence passes, run one bounded local
Gateway integration through the withheld-candidate path: configure the public entry,
start a fresh thread/run, cause one known predecessor-owned progress fact, and assert
one matching payload appears on the public SSE `custom` channel alongside public
thread/run metadata and the public response-header trace id. Record thread/run/Bundle/
trace correlation only in redacted test evidence. That proof changes no Run and renders
  nothing; only after it passes may the implementation route later candidates that
  satisfy the same validation to the real entrypoint presentation callback and run its
  deterministic missing/disorder tests. The proof record itself is not retained or
  replayed into an entrypoint.

If this proof fails, progress candidates remain withheld. The Change remains active
for repair or is explicitly re-scoped in proposal/spec/tasks before archive to a coarse
Gateway observer. It does not use raw writers, private stores, file tailing, or
application heartbeats to force the original claim through.

## Risks / Trade-offs

- [Dedicated Agent returns no valid lifecycle ToolMessage] -> Fail the turn as unknown
  to the presentation, retain Gateway history for diagnosis, and never trust assistant
  prose as lifecycle truth.
- [Public SSE record names drift] -> The focused structured-stream contract fails;
  update the active Change against documented public behavior before implementation.
- [Nested events are not forwarded] -> Keep progress disabled and repair or explicitly
  re-scope before archive; coarse Gateway facts do not silently satisfy the claim.
- [A profile is healthy but history/log settings are stale] -> Restart-scoped profile
  preflight blocks the observer before creating a thread.
- [File capture blocks or fails] -> Use a dedicated bounded tee path, preserve signal/
  exit semantics, and disable only the file side on failure.
- [Real and embedded modes become confused] -> Require explicit mode labels and source
  guards proving the default real entry imports no local graph composition path.
- [A local automatic policy or cancel button is sent as a public turn] -> Reject it
  before a public request and require entered text or the explicitly selected
  embedded-smoke mode; never synthesize a user message or direct lifecycle call.

## Migration Plan

1. Verify and record the archived predecessor and current two-entrypoint embedded
   baseline.
2. Add red structured-SSE, typed-result, profile-readiness, and stderr-capture tests;
   register the new path/import contract.
3. Implement the public Gateway observer/transport and deterministic stream fixtures,
   retaining every custom progress payload as a withheld validation candidate and
   rejecting non-text/control-context dispatches before a new public turn request.
4. Cut over default real CLI and TUI modes; keep fixture modes unchanged and move
   local all-real composition behind explicit embedded-smoke selection.
5. Add profile readiness and process `stderr` tee with failure/retention evidence.
6. Run the bounded configured-Gateway custom-event forwarding proof. On success,
   connect the already-validated candidate to presentation and prove disorder remains
   non-controlling; on failure, repair or explicitly re-scope and add no fallback
   transport.
7. Run full verification and archive only when proposal, specs, tasks, diff, and
   evidence describe the same final observer scope.
