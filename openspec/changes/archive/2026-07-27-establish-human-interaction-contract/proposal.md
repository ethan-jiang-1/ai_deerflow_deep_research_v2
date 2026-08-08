## Why

The real Deep Research CLI currently makes a user infer a transport protocol at the
first research decision: a natural confirmation is parsed as profile text, can exhaust
the rejection budget, and can remove the only visible recovery affordance. Recent
HITL, projection, recovery, and fixture defects show that this is a repeated
human-interaction contract gap, not a missing Chinese alias.

This change establishes one bounded interaction model for the live HITL1 proposal so
new users can confirm, revise, ask about, or clarify a proposal naturally while graph
authority, typed actions, correlation, and checkpoint ownership remain strict.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/domain/` human-interaction contract.
- **Question:** How can a current, complete research proposal turn a human reply into a closed candidate intent and a safe graph-owned resolution without making adapters, raw text, or model output action authority?
- **Necessary adjacent/external contracts:** `node-agent-runtime` answers how a zero-tool, bounded semantic invocation runs; `hitl1-node` answers admission and checkpoint transition; `research-graph-lifecycle` answers correlated typed-action preservation; `research-run-experience` answers controller-fact projection; CLI/TUI/workbench specs answer generic rendering and control submission; `research-session-discovery-and-operations` answers brokered control revalidation; `deep-research-agent-charter` answers the recurring review rule; `project-structure` answers registration and import boundaries for the new domain contract.
- **Evidence seam:** scripted semantic-intake results through the real HITL1 lifecycle, plus shared-projection and adapter conformance tests; credentialed demo runs are supplemental only.
- **Not in scope:** `backend/`, `frontend/`, generic chat, initial-question interpretation, agent-led HITL2 routing, cross-process continuation, provider-global configuration, or research/report quality.
- **Triggered charter policies:** local-context, authority-and-projections, participant-outcomes, human-interaction-integrity, control-and-recovery, workflow-outcome-review, change-admission

## What Changes

- Add a domain-owned human-interaction contract with closed proposal intents, material-visibility rules, revision-confirmation behavior, bounded feedback, and visible controls.
- Add a zero-tool structured semantic-intake invocation for raw HITL1 text. It may only return a candidate intent, full candidate revision, bounded explanation, or focused clarification; it cannot route, accept, write state, or construct actions.
- Make HITL1 retain the current proposal across questions, ambiguity, and semantic failure; revisions create a fully visible new proposal and require fresh confirmation. Natural confirmation, revision, questions, and ambiguity no longer consume the old profile rejection budget.
- Add a shared interaction projection and generic control-selection intent. CLI, TUI, and workbench render the same subject, feedback, and visible controls; adapters no longer translate magic phrases or machine action IDs.
- Keep advertised typed actions and stale/forged-action denial at the graph boundary. A visible control is bound by trusted runtime state only when it is current and advertised.
- Define bounded semantic-invocation recovery: at most three calls per human reply, including at most two transient provider retries and one structured-output repair. Exhaustion preserves the proposal and offers an explicit fallback control rather than terminally rejecting the user.
- Add a charter policy for human-interaction integrity and operator-facing documentation that describes natural confirmation, revision, and questions without teaching hidden protocol tokens.

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Semantic provider timeout/unavailable | HITL1 semantic invocation result | HITL1; at most two transient retries, three total calls | Non-terminal interaction feedback; preserve proposal | Select visible current-proposal control or submit another reply | Scripted lifecycle provider-failure transcript |
| Semantic structured output invalid | HITL1 semantic invocation result | HITL1; one repair within the same three-call cap | Non-terminal interaction feedback; preserve proposal | Select visible current-proposal control or submit another reply | Scripted malformed-output transcript |
| Semantic ambiguity | Domain interaction resolution | No automatic retry; one bounded clarification | Pending same proposal version | Answer the focused clarification | Domain and lifecycle transcript |
| Stale, forged, or unadvertised control | Generic human-input verifier and current pending request | No recovery controller; re-project current legal interaction when safe | Fail closed without graph mutation | Use a current visible control or answer | Runtime/broker stale-control tests |

## Capabilities

### New Capabilities

- `human-interaction-contract`: Defines the bounded proposal subject, candidate human intents, resolutions, feedback, material visibility, and visible-control contract.

### Modified Capabilities

- `hitl1-node`: Admit semantic candidates through graph-owned proposal state and preserve proposal/revision/feedback semantics.
- `node-agent-runtime`: Support the bounded zero-tool semantic-intake execution policy and structured result evidence seam.
- `research-graph-lifecycle`: Preserve correlated typed actions while allowing trusted runtime control selection to bind only current advertised controls.
- `research-run-experience`: Project controller-owned interaction facts into one safe shared interaction view.
- `research-cli-onboarding`: Make natural proposal interaction primary and render explicit numbered fallback controls.
- `research-demo-tui`: Render and submit shared visible controls without action-token aliases.
- `research-local-session-workbench`: Render and submit shared visible controls through the workbench.
- `research-session-discovery-and-operations`: Revalidate brokered visible-control selection under the existing lock and request correlation.
- `deep-research-agent-charter`: Add the focused human-interaction-integrity policy and routing entry.
- `project-structure`: Register the new domain contract module and its deterministic test seam.

## Impact

- Affects `agent/` domain contracts, HITL1 node state, node-agent invocation policy, lifecycle projection, standalone CLI/TUI/workbench adapters, and their deterministic tests.
- Adds `SelectControlRun` and safe visible-control projection alongside existing raw-text and typed-action paths; existing typed action transport remains valid for compatibility.
- Adds checkpoint-safe proposal-version and interaction-feedback facts with defaults for existing checkpoints; raw replies, model prompts, and provider bodies remain excluded from checkpoint, bundle, diagnostics, and presentation.
