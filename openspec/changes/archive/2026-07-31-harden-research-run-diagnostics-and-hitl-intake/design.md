## Context

See [proposal.md](proposal.md) for motivation. Current provider terminals already carry
a safe category, response observation, opaque reference, retry projection, and a
session-view projection. However, bridge wall-time and SDK timeout collapse into the
same no-response category, and retained publication only writes `records.jsonl` when
it first derives a reference. A provider terminal normally supplies its reference, so
the later trace and summary can refer to a record that was never published. CLI/TUI
also embed the pre-rename `agent/` directory in their inspection string.

BUG-013 is no longer a current defect: the human-interaction contract and HITL1
semantic-intake path now classify a natural confirmation as a bounded candidate and
the node deterministically admits only the current proposal. This change preserves
that implementation through explicit evidence; it does not add another interpreter.

## Goals / Non-Goals

**Goals:**

- Carry the smallest closed safe timeout-origin fact for each final or retry-trigger
  observation through terminal incident, retained diagnostic, shared terminal, and
  presentation.
- Make a `session_bundle` location a claim backed by an exact retained diagnostic file.
- Give CLI/TUI one module-local, executable, read-only inspection command.
- Preserve and document the verified BUG-013 natural-confirmation regression path.

**Non-Goals:**

- No changes to provider timeouts, retry counts, provider SDK policy, graph routing,
  live-provider reliability, or `same_process` durability.
- No raw failure-content retention and no inspection-based resume.
- No changes under `backend/` or `frontend/`, and no new semantic-intake model role.

## Decisions

### 1. Carry a typed origin, not a second failure category

`ProviderObservation` gains an optional closed `timeout_origin` with only
`bridge_wall_time_budget` and `provider_sdk_timeout` for new bridge-produced timeout
results. `RuntimeNodeAgentBridge` emits the former only
after its admitted deadline has expired and the latter only for the supported
`openai.APITimeoutError` branch. Its separately handled `httpx.TimeoutException`, a
bare inner `TimeoutError`, and legacy/generic no-response results retain the existing
`provider.timeout` or generic category with origin absent, because the bridge cannot
prove either closed cause. Absence means legacy/not observed, not a third meaning.
The terminal failure category remains `provider.timeout`; HITL1 retains its current
recovery decision from that category, not from origin.

The origin remains attached to its `ProviderObservation` through `NodeProblem`, terminal
incident, recovery observation, `RunFailure`, and presentation-safe provider details.
A terminal can contain both `provider_recovery.trigger_observation` and a final
`provider_observation`. Therefore `RecordBearingLifecycleFact` and the frozen retained
diagnostic record carry distinct optional `recovery_trigger_timeout_origin` and
`final_timeout_origin` fields, and inspection presents those same roles rather than
collapsing them into one terminal-level value.

`workflow_outcomes.derive_provider_diagnostic_reference()` is the shared canonical
identity owner for every existing caller, including HITL1, topic planning, Wave2, and
controller-derived worker incidents. It includes each origin only when present and in
its owning trigger/final role, so distinct observed branches cannot silently share one
diagnostic identity. With no origin on either observation it retains the exact existing
version-one identity payload, rather than adding null fields or changing the version;
current origin-absent references remain stable. HITL1 supplies its two observed roles to
that helper. Legacy incident/reference data remains unchanged and no projection infers
an origin from timestamps or endpoint metadata.

Alternative rejected: adding an origin only to text output would make retention and
machine consumers parse prose, and would still be vulnerable to presentation drift.

### 2. Treat diagnostic publication as a precondition for bundle location

`RunSessionStore` resolves the reference from the lifecycle fact: it uses the supplied
provider-terminal reference as-is or derives one only under the existing non-supplied
path. Both existing runtime fact builders, `ResearchRunExperience` and
`ResearchSessionOperationBroker`, copy role-bound origins from a provider terminal
incident into the fact, leaving them absent for every other terminal. For every
record-bearing terminal with a reference and a non-null category that satisfies the
existing safe `failure_category` field validation, it constructs one frozen, bounded
redacted record and atomically writes `diagnostics/records.jsonl` first. A later
identical republish revalidates that same one record rather than appending a duplicate;
a conflicting or malformed retained record makes the diagnostic proof unavailable. The
fact validator rejects a terminal reference without that category; it does not create a
storage-local failure enum or synthesize a category. Old malformed data remains an
unavailable observation. Only after the exact record succeeds and revalidates may it
publish the terminal event, lifecycle trace, summary, manifest, and a view that exposes
the reference. The record is not a lifecycle controller; it is proof for a projection
of the checkpointed terminal fact.

The existing `RunSessionView.terminal_diagnostic_ref` is a publication-proof projection:
it is set only after the exact record succeeds and revalidates, and is absent when that
proof is unavailable. It does not copy diagnostic origins. `ResearchRunExperience` then
sets `session_bundle` only from that positive verification. If publication cannot be
verified, its provider terminal attempts the existing support journal with the same
reference and optional role-bound safe origins; no branch generates a new reference.
`ResearchSessionOperationBroker` has no such fallback authority: its existing publication
failure result remains unavailable. The checkpointed terminal remains blocked/complete
according to the existing result in either path.

Alternative rejected: checking for a file from CLI/TUI would duplicate storage
authority and create races. Adapter code consumes only the shared typed terminal.

### 3. Project a verified diagnostic fact, then make inspection executable

The legacy inspection contract continues to prohibit artifact bodies and arbitrary
paths. It may, however, show last verified state and fixed safe references. The session
store therefore parses only the bounded known diagnostic-record schema after validating
the contained file, and exposes a typed `SessionInspection` diagnostic projection only
when exactly one record's opaque reference matches the terminal summary/view correlation.
That projection contains only reference, category, phase, and the role-bound optional
closed timeout origins. A missing, malformed, duplicate, stale, or differently referenced
record yields no projection and no origin; it never changes inspectability, lifecycle
outcome, or any recovery authority.
`demo-sessions inspect` renders that typed projection, not the JSONL body, so the same
retained evidence that supports `session_bundle` is useful to an operator after the
original terminal receipt is gone.

The shared presentation helper emits `make demo-sessions DEMO_ARGS="inspect <id>"` and
labels it read-only. The documented context is the module directory, matching the
fresh-start command and avoiding a hard-coded repository-relative directory name.
CLI and TUI call that same helper. The test renders a known retained terminal, executes
the emitted command with module-root working directory, and asserts it reports an
inspection, including verified role-bound closed timeout origins when present, without
graph/provider invocation.

Alternative rejected: retaining `make -C agent` or changing it only to
`make -C deerflow_research` leaves duplicated root knowledge in adapters and does not
prove the command works from its stated context.

### 4. Keep BUG-013 as a regression, not a new intake branch

The existing `HIN-009` through `HIN-011` and `HIC-001` through `HIC-004` already own
ordinary confirmation: raw reply is untrusted input to a zero-tool candidate request;
HITL1 deterministically resolves it, writes only the checkpointed proposal, and keeps
ambiguity/failure non-terminal. This change adds no parser alias or adapter magic
phrase. Its implementation task reruns and registers the natural Chinese confirmation
node test, then moves BUG-013 out of active backlog with the fixing change/reference.

## Risks / Trade-offs

- [A new persisted enum breaks legacy readers] -> Make each role-bound origin optional
  and preserve absent legacy data exactly; validate all new values closed/extra-forbid.
- [Diagnostic-write failure hides a valid terminal] -> Preserve the checkpointed
  terminal and use the existing same-reference journal fallback; only the location
  claim changes.
- [A diagnostic record loses one retry observation or leaks sensitive data] -> Use a
  frozen bounded record in both bundle and support-journal paths; allow only category,
  phase, certainty, opaque reference, fingerprint, and role-bound closed timeout origins.
- [Inspect turns a diagnostic file into a raw-output channel] -> Parse only the known
  bounded schema, require exactly one exact terminal-reference correlation, and render
  the typed projection rather than a diagnostic-record body or arbitrary file path.
- [Command tests become environment-dependent] -> Execute only `demo-sessions inspect`
  on a contained fixture bundle with no provider, graph dispatch, or credential access.
- [Semantic regression is mistaken for live language-quality proof] -> Keep its
  deterministic scripted candidate claim scoped to control/admission; live model
  quality remains supplemental.

## Migration Plan

1. Existing bundles and terminal incidents with no origin remain readable and are never
   rewritten by inspection.
2. Newly published terminals use compatible optional role-bound fields and
   exact-reference record ordering.
3. The static old inspection command is replaced in all standalone adapters and docs
   owned by the capability; no shell alias or compatibility directory is introduced.
4. After focused tests and full verification pass, update BUG-013 through BUG-016 with
   their change reference and archive only the cards whose acceptance criteria pass.
