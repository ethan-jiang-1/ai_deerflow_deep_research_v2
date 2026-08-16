# Apply Record

## Admission Baseline

- Apply authorization: the user explicitly instructed execution of
  `wire-harness-observability-entrypoints` after the prior Change was archived and
  committed.
- Archived predecessor:
  `openspec/changes/archive/2026-08-16-add-deerflow-native-live-event-projection/`.
  It is included in commit `3edba72` and owns the current-pin
  `deep_research.progress.v1` emission contract through the public injected
  `ToolRuntime.stream_writer` surface.
- DeerFlow boundary: nested `HEAD`, root gitlink, and registry lock remain
  `66b9e7f21212490cf92fafac137542b9deb06615`; the submodule worktree is clean.
  This Change admits no DeerFlow source inspection, source edit, dependency upgrade,
  gitlink change, or missing convenience-helper assumption.
- Working tree baseline: before target edits, this active Change's planning artifacts
  were untracked and there were no pending implementation edits. Completed task `0.2`
  then made the approved planning-only synchronization to
  `_backlog/plans/runtime-operator-logs-and-live-trace.md`; it is the sole tracked
  modification outside this Change and is not an implementation target of the Change.

## Selected Profile And Public Interfaces

- Selection contract: both real entrypoints require an explicit project-owned
  `--profile` label. `demo` is the bounded local integration witness, not an implicit
  fallback and not currently ready.
- Current `demo` facts: profile isolation validation and observer readiness
  (`validate_observer_profile`) pass against the launched Gateway: isolated SQLite
  state, `logging.enhance.enabled: true` with JSON format, a verified public
  Deep Research entry (`runtime_config_ready=True`, `entry_status=ready`), and a
  healthy direct local Gateway on `127.0.0.1:8001`. The observer does not create a
  thread until that structured readiness check passes; this Change does not use
  the optional Nginx `127.0.0.1:2026` endpoint.
- Public thread creation: `POST /api/threads` with an empty JSON object; retain only
  the returned opaque `thread_id` for explicit turns in the current process.
- Public turn stream: `POST /api/threads/{thread_id}/runs/stream` with fixed
  `assistant_id=deep-research`, one explicit user message, and only the stream modes
  required for safe assistant text and custom progress observation.
- Gateway input admission: current `--scripted` automatic policy is trusted runtime
  context, and the TUI cancel button is a non-text local control. Neither is a public
  Gateway input, so the default Gateway entry must reject/hide it before a thread or
  stream request rather than inventing a user message or direct lifecycle call.
- Public correlation and stream facts: response header `X-Trace-Id`; SSE
  `metadata`, `messages-tuple`, `custom`, `error`, `end`, heartbeat, and gap. The
  adapter retains only safe Gateway-created thread/run correlation and approved
  Bundle/diagnostic references from validated Deep Research results or events.
- Authority boundary: only a returned `deep_research` ToolMessage payload that
  validates through the existing typed lifecycle contract may produce lifecycle
  presentation. Assistant prose, heartbeat, gap, disconnect, duplicate/reordered
  data, missing progress, and `end` remain transport observations only.

## Control Placement Review Result

The proposal's Control Placement Review and all six triggered policies were re-read:
`authority-and-projections`, `participant-outcomes`, `control-and-recovery`,
`workflow-outcome-review`, `control-placement`, and `change-admission`. The approved
postures remain valid: typed result admission and terminal interpretation are
non-bypassable; progress and physical log capture are advisory projections.

The working-tree comparison found one actionable planning drift and added ordinary
task `0.2`: the active Change and delivery plan still described the predecessor as
future/active and claimed a public custom-event helper or dependency-upgrade path.
The correction must record the actual archived current-pin `ToolRuntime.stream_writer`
boundary and exactly one active Change before implementation begins. Existing tasks
`1.1` and `1.2` already own deterministic public request/SSE characterization, so no
duplicate interface-discovery task was added.

The archived predecessor commit already registered the pending `GOO` prefix and
`GOO-001` through `GOO-003`, and updated `RED-001` for the Gateway-backed real TUI.
Task `0.3` therefore preserves those records and corrects only the still-ambiguous
`DPL-004` scripted-mode wording. Task `4.0` adds requirement-evidence impacts after
the focused test selectors exist. Neither task allocates duplicate IDs nor rewrites
archived requirement history.

## Forwarding Proof And Closeout (Tasks 4.2 Through 5.3)

The bounded configured-Gateway forwarding proof passed against the profile-launched
`demo` Gateway. A real `deep_research` tool reflection returned the typed lifecycle
result dict with `implementation_mode=all_real` and a Bundle id; three
`deep_research.progress.v1` candidates (bootstrap node started/completed, hitl1 node
started) reached the public SSE `custom` channel through the withheld-candidate path.
Each candidate carried the same `outer_run_id` as the SSE `metadata` `run_id` and the
same `bundle_id` as the typed result. The marked real-Gateway integration test
`tests/live/test_gateway_forwarding_proof.py` records only redacted evidence and
invokes no real entrypoint presentation callback.

Two real-Gateway contract facts were corrected during the proof:

- The public SSE record name for LangGraph message tuples is `messages` (the
  `messages-tuple` stream mode's SSE event name), so the observer accepts both names.
- LangGraph serializes assistant messages as `AIMessageChunk`, which the observer
  normalizes to the `ai` presentation kind.

After the proof, both real entrypoints route validated `deep_research.progress.v1`
candidates to a bounded progress presentation that renders only the
predecessor-approved `phase`/`operation`/`outcome` fields plus a bounded Bundle
reference. Deterministic unit tests prove a missing, duplicate, reordered, malformed,
or gap-separated custom event leaves the typed lifecycle result, Bundle Journal,
State, retry/route, and legal next action unchanged and creates no acknowledgement,
dedupe authority, or execution retry. Local operations documentation now names the
profile startup/observer sequence, the process log root, `tail -f` usage, the
trace/run/Bundle correlation route, and the distinct roles of `stderr`, SSE `custom`,
Gateway history, and Bundle inspection.

Verification (task 5.1): requirement, spec, architecture, and change-guidance
governance pass; `uv lock --check`, `ruff check`, and `ruff format --check` pass;
test-asset and requirement-coverage checks pass; the full fast lane (2794 tests) and
workflow lane (35 tests) pass. Three pre-existing integration failures are unrelated
to this Change: two require networked `make install` in a copied tree (denied by the
offline sandbox) and one is a baseline Wave1 review-gate assertion that fails on
`HEAD` without this Change's edits. Task 5.2 passes: `openspec validate --strict`
and `git diff HEAD --check` are clean, the DeerFlow gitlink remains
`66b9e7f21212490cf92fafac137542b9deb06615`, and the submodule worktree is clean.
Task 5.3 closeout facts hold: both real entrypoints use the public Gateway path,
fixture modes remain unchanged, physical logs remain deployment artifacts, and no
partial or fallback event-delivery claim is archived.
