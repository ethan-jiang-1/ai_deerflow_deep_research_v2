## Why

The two archived observability changes established safe standard logs and the
approved current-pin `deep_research.progress.v1` event attempt.
However, both current real entrypoints still construct a local graph through
`DemoLifecycleTransport`. They therefore cannot truthfully claim Gateway run history,
trace correlation, StreamBridge liveness, or nested custom-event delivery. The final
operator-facing delivery must be one separate Change whose scope matches the backlog
exactly.

## What Changes

- Add one bounded Gateway observer over DeerFlow's public thread-create and
  `POST /api/threads/{thread_id}/runs/stream` interfaces at the profile-launched
  local loopback Gateway `http://127.0.0.1:8001`. It targets the configured
  `deep-research` Agent, uses a structured SSE client, and normalizes only approved
  `metadata`, `messages-tuple`, `custom`, `error`, `end`, heartbeat, and gap facts.
- First add only a validated, withheld candidate path for
  `deep_research.progress.v1`; then prove that one predecessor-owned event from the
  reflected Deep Research tool reaches DeerFlow's public SSE `custom` channel before
  routing later candidates that pass the same validation to an observer progress
  presentation. Missing forwarding
  blocks or explicitly re-scopes this Change; it never creates a raw-writer,
  private-store, or file-transport fallback.
- Move the default real paths in `scripts/demo_real.py` and real mode of
  `scripts/demo_tui.py` to the configured Gateway observer. Preserve `--question`,
  require one explicit `--profile` label, preserve shared typed lifecycle
  presentation, and explicit user follow-up turns. The
  Gateway path rejects `--scripted` before creating a thread because its automatic
  policy is trusted runtime context, not a public Gateway input; that flag and
  explicit graph cancellation remain on the fixture/embedded-smoke paths. Keep
  fixture CLI/TUI behavior unchanged, and retain local graph composition only behind
  an explicitly labelled embedded-smoke mode.
- Replace local model/Tavily readiness on the Gateway-backed paths with selected
  profile, Gateway health, public-entry, trace-correlated logging, and durable history
  readiness. Preparation uses the current root `config.yaml` as the sole local
  `config_version` baseline and requires the selected profile to match it exactly;
  the static upstream example is not a compatibility or version authority. The
  embedded-smoke mode alone retains the local
  `DEERFLOW_DEMO_MODEL`/`TAVILY_API_KEY` preflight.
- Extend the project-owned local profile launcher to tee the unchanged Gateway
  process `stderr` into a secure, bounded process log below
  `.deep-research-demo-runs/logs/`, while preserving normal `stderr` and DeerFlow's
  logging configuration.
- Register the new bounded runtime observer and deterministic evidence paths in the
  project-structure contract. Use the already locked `httpx-sse` package as an
  explicit Harness dependency rather than hand-parsing SSE records.

## Capabilities

### New Capabilities

- `gateway-operator-observer`: A configured Gateway request/stream adapter and safe,
  non-controlling projection of current-run transport facts.

### Modified Capabilities

- `demo-pipeline`: The real CLI uses the selected Gateway profile by default; direct
  graph composition remains only an explicitly labelled embedded smoke path.
- `research-demo-tui`: Real TUI mode uses the same Gateway observer while fixture mode
  remains the existing credential-free fixed graph.
- `local-configuration-profiles`: Profile readiness covers the Gateway observation
  prerequisites and the launcher owns bounded physical `stderr` capture.
- `project-structure`: The Gateway observer, its focused evidence, and the structured
  SSE dependency remain in canonical downstream ownership paths.

## Impact

- Expected implementation owners are
  `deep_research_harness/src/deerflow_deep_research/runtime/gateway_observer.py`,
  `scripts/demo_real.py`, `scripts/demo_tui.py`, `scripts/local_profiles.py`, existing
  shared run-experience contracts, profile/Makefile wiring, focused tests, and local
  operator documentation.
- This Change consumes the archived
  `add-deerflow-native-live-event-projection` contract. It does not
  redefine that Change's event schema, safe fields, or runtime fact owners.
- No `deerflow/` source browsing or modification, gitlink update, private
  RunJournal/store access, Bundle Journal schema change, State mutation, or Deep
  Research lifecycle/retry/route control path is in scope.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/gateway_observer.py`; it owns the public Gateway request/SSE boundary and validated transport projection, while existing shared run-experience and CLI/TUI adapters retain their current typed/presentation responsibilities.
- **Seam classification:** wiring because the Change connects existing typed Deep Research results and predecessor-owned live events to DeerFlow's public Gateway stream and local operator entrypoints without adding execution or recovery semantics.
- **Question:** With the current DeerFlow pin fixed and both observability predecessors archived, can the supported local real CLI and TUI run through the configured `deep-research` Gateway Agent and expose safe live transport/log facts without making SSE, assistant text, a local file, or presentation code a second lifecycle or history authority?
- **Necessary adjacent/external contracts:** `gateway-operator-observer` owns public stream normalization; `demo-pipeline` and `research-demo-tui` own real-entry selection and presentation; `runtime-observability` owns safe logs/events; `local-configuration-profiles` owns selected profile readiness and process capture; `project-structure` owns canonical paths/imports; `deployment-configuration` `DEC-003`/`DEC-004` owns the configured public skill and `deep-research` Agent; predecessor `add-deerflow-native-live-event-projection` owns event emission; DeerFlow's public thread, run-stream, trace-logging, and durable run-history interfaces are the only admitted framework surfaces.
- **Evidence seam:** deterministic structured-SSE fixtures covering request shape, fresh-thread/explicit-follow-up ownership, pre-request rejection of non-interactive context and non-text UI controls, typed tool-result extraction, withheld progress candidates, assistant text filtering, heartbeat/gap/error/end, duplicate/malformed records, and no lifecycle side effects; profile capture/readiness tests including a zero-mutation `configure.py` entry assessment that accepts only `entry_status=ready`; then one bounded configured-Gateway forwarding proof before a later candidate that passes the same validation reaches an entrypoint presentation callback.
- **Not in scope:** runtime event taxonomy/payload changes, DeerFlow source or gitlink changes, generic remote/authenticated Gateway support, proxy/Nginx `:2026` or caller-selected Gateway origins, raw stream writers, private Gateway store/`__run_journal` access, Bundle Journal/history changes, graph State or lifecycle/retry/route control, SSE replay implementation, event acknowledgement, file/tailer/heartbeat fallbacks, or translating scripted policy/context and non-text local controls into invented Gateway user messages.
- **Triggered review policies:** authority-and-projections, participant-outcomes, control-and-recovery, workflow-outcome-review, control-placement, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Gateway turn and typed Deep Research result | The configured `deep-research` Agent may propose one lifecycle tool call from a user-entered turn or a selected advertised control value | Existing public skill/tool schema and Deep Research runtime admit the action/result; the observer only validates the returned public envelope and creates no turn for scripted context or a non-text local control | non-bypassable | No observer, SSE record, or renderer may invent a lifecycle action, result, or user message | Reuses the configured public entry instead of a second local lifecycle controller | Fixture stream proves fresh-thread and exact-follow-up input handling, rejected scripted/cancel paths, accepted/missing/malformed reflected-tool results, and no direct lifecycle client call |
| Live progress display | None; the event is already a predecessor-owned runtime projection | `gateway_observer.py` first validates and withholds exact `deep_research.progress.v1` candidates received on DeerFlow's `custom` channel; a bounded configured-Gateway proof admits only later candidates that pass the same validation to presentation | advisory | Missing, duplicate, reordered, or malformed delivery never changes the Run, and an unproven delivery path cannot reach presentation | Avoids polling, acknowledgements, dedupe state, a second progress emitter, and a guessed feature flag | Withheld-candidate fixtures, configured-Gateway forwarding proof, then post-admission projection tests |
| Terminal and liveness presentation | None; heartbeat, gap, `error`, `end`, and typed lifecycle results are distinct facts | Gateway transport owns heartbeat/gap/error/end; existing typed Deep Research result owns lifecycle disposition | non-bypassable | `end` means Gateway turn end only; gap/disconnect never becomes completed/failed/still-running research | Avoids local terminal inference and implicit retry/resume/cancel | Clock-controlled fixture proves each projection and absence of lifecycle side effects |
| Physical local log file | None; bytes are already admitted to the launched Gateway's normal `stderr` | Profile launcher owns byte-for-byte tee, permissions, rotation, and retention; DeerFlow keeps logger/trace ownership | advisory | Capture failure leaves `stderr`, Gateway execution, and every Run outcome unchanged | Avoids root-handler mutation, Bundle-local files, tailers, and a second log schema | Process-capture permissions, concurrency, rotation, and injected-write-failure tests |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Selected profile lacks entry, logging, history, or health readiness | Profile validator and public Gateway health response | Operator corrects the named profile/configuration and restarts the Gateway; observer never patches it | No Gateway turn or Deep Research Run is claimed | Run the reported profile setup/check action, then start a fresh observer | Profile fixtures with each missing prerequisite and unreachable health endpoint |
| Public thread or stream request cannot be opened | Gateway HTTP transport | Operator may start a new observer connection; no Deep Research retry or local lifecycle dispatch occurs automatically | Bounded connection failure, not a Deep Research terminal result | Inspect/restart the selected Gateway, then explicitly start a new turn | HTTP fixture fails before metadata and after connection establishment |
| Reflected lifecycle result is absent or malformed | Existing Deep Research result schema owns valid output; observer owns validation only | Drop the invalid candidate and end the presentation as unknown/fault without inventing a result | Gateway turn may end; Deep Research outcome remains unknown to the observer | Inspect supported Gateway history or start a new explicit user turn | `messages-tuple` fixtures with missing, wrong-tool, unsafe, and invalid result payloads |
| Gateway entry receives `--scripted` context or a non-text local control | CLI/TUI entrypoint owns admission of only a user-entered turn or selected visible value | Entry-point/transport validator rejects before a new Gateway turn request; the configured Agent receives no invented control message | No new Gateway turn or Deep Research lifecycle result is claimed | Use an explicit interactive turn, or choose fixture/embedded smoke for the existing automatic policy or graph cancellation | Entry-point and transport fixtures prove no new thread/stream request and no local lifecycle call |
| Heartbeat, gap, disconnect, duplicate, or reordered stream data occurs | Gateway transport | No Deep Research recovery; renderer exposes only the bounded transport condition | Existing Run outcome is unchanged and may remain unknown | Continue the current connection when possible or inspect supported history | Clock/cursor-controlled structured-SSE fixtures |
| Nested progress event does not reach the public `custom` channel | This Change owns forwarding admission; the archived predecessor retains emission ownership | Keep the validated candidate withheld from presentation and either repair or explicitly re-scope this active Change before archive | Coarse Gateway observation remains possible; no event-delivery claim is accepted | Repair the public forwarding path or approve a reduced Change | Bounded configured-Gateway integration test against the archived predecessor contract |
| Local file capture fails or reaches its bound | Profile launcher | Disable/close only capture and retain normal `stderr`; no rerun or lifecycle action | Existing Gateway process and Run continue unchanged | Read normal Gateway/deployment logs or launch a later process | Injected capture failure and active-file retention tests |
