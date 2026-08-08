## Why

One real provider-timeout terminal currently leaves operators unable to distinguish a
bridge deadline, an observed SDK timeout, or an unclassified no-response result, directs
them to an inspection command for a deleted module root, and may claim a session-bundle
diagnostic that was never written.
Those defects make the next action non-actionable. Separately, the active BUG-013 card
describes an old HITL1 failure that the current human-interaction contract has already
replaced; it must be aligned and retained as a regression guarantee rather than drive a
second, conflicting intake design.

## Change Focus

- **Primary module / causal owner:** `deerflow_research/runtime/run_session.py` owns
  retained terminal-diagnostic publication and the truth of `session_bundle`
  availability.
- **Question:** How can a provider-diagnostic terminal retain one safe, inspectable
  diagnostic record with the exact existing reference, expose each role-bound closed
  timeout origin through the terminal and read-only inspection projection, and give
  every participant an executable read-only inspection action?
- **Necessary adjacent/external contracts:** `node-agent-runtime` answers which bridge
  branch owns the safe timeout-origin fact; `workflow-failure-outcomes` answers how the
  shared provider-diagnostic reference distinguishes each observed role without changing
  origin-absent reference identity; `research-run-experience` answers how verified
  publication becomes the terminal location; `research-cli-onboarding` answers how
  CLI/TUI render one executable read-only command; `human-interaction-contract` and
  `hitl1-node` answer what existing semantic-confirmation behavior BUG-013 must preserve
  and prove.
- **Evidence seam:** deterministic bridge and shared diagnostic-reference identity
  fixtures, real `RunSessionStore` publication/inspection plus the existing
  session-operation publisher, shared `ResearchRunExperience` terminal projection, a
  rendered-command subprocess test rooted at `deerflow_research/`, and the existing
  HITL1 node fixture for a natural Chinese confirmation.
- **Not in scope:** `backend/`, `frontend/`, provider configuration changes, a new
  provider retry policy, cross-process resume for `same_process` demos, raw
  exception/prompt/provider-body retention, or a new LLM role for semantic intake.
- **Triggered charter policies:** authority-and-projections, participant-outcomes, control-and-recovery, workflow-outcome-review, change-admission

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Bridge wall-time expiry versus SDK timeout versus unclassified no-response | `RuntimeNodeAgentBridge` classifies only the observed bridge-deadline and SDK-exception branches before any lifecycle projection; `workflow-failure-outcomes` owns the shared safe reference identity. | Existing HITL1 provider retry remains unchanged: at most one retry-eligible retry; origin is diagnostic-only. | Existing typed provider terminal retains final and retry-trigger origins separately when observed; category stays unchanged. | Inspect the retained diagnostic, then use the existing fresh-start action; no resume is implied. | Inject a bridge deadline followed by an SDK timeout, and a transport timeout; assert role-preserving distinct origins, reference identity only when an origin is present, and an absent origin with no raw exception data. |
| Existing terminal diagnostic reference cannot be published to the bundle | `RunSessionStore` owns contained diagnostic-file publication. | No graph retry is introduced. `ResearchRunExperience` alone keeps the existing exact-reference support-journal fallback for its shared provider terminal; the session-operation broker retains its existing unavailable result. | `session_bundle` only after exact record publication; otherwise the shared provider terminal is `support_journal` or `unavailable`. | Read the displayed source if available; otherwise use the existing fresh-start action. | Publish provider and non-provider terminals with supplied references and inject bundle-write failure through each existing publisher boundary. |
| Printed inspection command cannot run | Shared CLI/TUI presentation contract owns its static command shape; it projects an already verified terminal/session fact. | No execution recovery; inspection remains read-only. | Existing terminal category and durability are unchanged. | Run the displayed module-local `make demo-sessions ...` command. | Render then execute the command against the actual checkout layout. |
| Natural confirmation of a complete HITL1 proposal | HITL1 plus `human-interaction` candidate/resolution contracts own interpretation and graph admission. | Existing bounded semantic-intake behavior remains unchanged; ambiguity or semantic failure preserves the proposal/control. | Existing accepted route for an admitted confirmation, otherwise existing follow-up with recovery feedback. | Select the visible proposal control or provide ordinary confirmation/revision/question text. | Existing real-node scripted candidate test with `确认，按这个方案开始吧。`; add it to this change's regression inventory. |

## What Changes

- Add closed, redacted timeout-origin facts to provider diagnostics so a bridge wall-time
  expiry is distinguishable from a provider SDK timeout without exposing raw exceptions,
  payloads, prompts, credentials, full URLs, or provider content. Retry-trigger and
  final observations retain their roles independently; the shared provider-diagnostic
  reference incorporates each present role without changing the existing origin-absent
  identity. The existing failure category and retry eligibility remain authoritative and
  unchanged.
- Require every record-bearing terminal carrying an existing opaque diagnostic reference
  to write the exact reference into the retained bundle before publishing event, trace,
  summary, or session view; for provider terminals projected by `ResearchRunExperience`,
  make the existing fallback location truthful when that publication is unavailable.
- Let `demo-sessions inspect` render only a strictly parsed, exact-reference-correlated
  diagnostic projection (reference, category, phase, and role-bound optional closed
  timeout origins), so a retained record is operationally useful without exposing an
  artifact body or changing inspection into control.
- Make CLI and TUI emit the one documented module-local read-only inspection command,
  verify that it is runnable after the `agent/` to `deerflow_research/` rename, and
  retain the distinction between inspection and resume.
- Preserve and explicitly regression-test the already implemented HITL1 semantic path:
  an ordinary unambiguous confirmation of a complete proposal is admitted only through
  the existing bounded candidate/resolution contract, while ambiguity and failures keep
  the visible proposal/control. Align BUG-013 with that verified current behavior.
- Close or update BUG-013 through BUG-016 only after the corresponding deterministic
  evidence passes; no bug card is treated as resolved merely because this proposal exists.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `node-agent-runtime`: expose a closed safe origin for provider timeout diagnostics at
  the bridge classification boundary.
- `workflow-failure-outcomes`: retain each observed role-bound origin in the shared
  provider-diagnostic correlation identity while preserving the current origin-absent
  identity.
- `hitl1-node`: retain the bridge-supplied safe timeout origin through the existing
  terminal incident and shared correlation path while preserving the established
  natural-confirmation flow.
- `research-run-session`: atomically publish an exact supplied terminal diagnostic
  reference before any retained projection claims that the bundle contains it, then
  project only its verified closed diagnostic facts to read-only inspection.
- `research-run-experience`: derive terminal diagnostic location and record-created
  truth from verified retained publication or the existing fallback, while preserving
  lifecycle authority and retry semantics.
- `research-cli-onboarding`: render an executable, read-only inspection command from
  the documented module context for CLI and TUI provider terminals.

## Impact

- Affected implementation is limited to `deerflow_research/` runtime, domain
  contracts, the existing session-operation publisher, demo adapters, and their focused
  tests; `backend/` and `frontend/` are not modified.
- Retained bundle diagnostic schema and safe terminal/provider projections gain a
  closed compatibility-reviewed field. Existing records without an origin remain
  readable as legacy observations and must not be reconstructed.
- The implementation needs focused contract, runtime-storage, adapter-command, and
  HITL1 regression tests plus the existing governance/evidence metadata updates.
