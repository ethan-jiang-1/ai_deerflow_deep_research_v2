## Why

The standalone real-research CLI exposed two reliability failures that full-fake lifecycle coverage alone did not exercise: a transient external read could be discarded after one attempt, and a HITL1 prompt could ask for a field its strict result schema forbids. Recent tactical fixes contain the immediate regressions, but an opaque `blocked@hitl1` real run remains and the system has no single, reviewable contract connecting external failure classification, bounded recovery, structured-output compatibility, and truthful CLI projection. Focused deterministic seams are now the regression evidence for those direct boundaries.

This change makes the real execution path diagnosable and bounded without promising that a model or web provider is always available. It is needed now because more node-local retries or CLI text would repeat the same ownership drift instead of preventing it.

## What Changes

- Define the standalone demo's configured read-only web tools as explicit external-I/O boundaries: each attempt has a deadline; only classified transient failures receive a cancellable, finite retry; non-retryable and unknown failures retain a bounded, redacted result.
- Require HITL1's model-visible `StructuredBrief` expected-output contract to be mechanically compatible with the strict parser it invokes. System-owned language constraints remain instructions/parser checks, rather than unsupported model-output fields.
- Repair the existing graph/terminal/CLI projection so an already typed provider or output-contract failure remains actionable at the terminal. The CLI remains a projection, not a recovery or classification owner.
- Add deterministic replay seams for retry eligibility, attempt limits, cancellation, prompt/schema compatibility, and terminal projection. Define one explicitly bounded live CLI canary as supplemental integration evidence before closing BUG-022 and BUG-023.

## Change Focus

- **Primary module / causal owner:** `deerflow_research/scripts/_demo_core.py` owns direct Tavily read attempts and retry eligibility; `deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/` owns the model-visible brief contract and strict admission compatibility.
- **Question:** How can the real standalone path keep direct Tavily reads and HITL1 brief candidates bounded and parser-compatible, without allowing one transient read error or an invalid prompt contract to collapse into an unexplained terminal result?
- **Necessary adjacent/external contracts:** `RuntimeNodeAgentBridge` remains the existing owner of admitted zero-tool model-service classification before graph recovery; `ResearchRunExperience` and `demo_real.py` answer how an already typed terminal outcome reaches the CLI without becoming a second classifier; the Tavily SDK/public `httpx` exception surface supplies only direct, sanitized retry facts.
- **Evidence seam:** deterministic `test_demo_core.py`, HITL1 prompt/node/lifecycle tests, and a returned `Terminal` projection fixture; one time- and attempt-bounded credentialed `run/real-research.sh` canary is supplemental evidence only.
- **Not in scope:** `backend/`, `frontend/`, DeerFlow public interfaces, provider switching, unbounded retries, changing Wave0/Wave1 aggregate budgets, cross-process resume, or a production availability/SLA claim.
- **Triggered review policies:** workflow-outcome-review, control-placement

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Admitted zero-tool model timeout or transient provider unavailability | `RuntimeNodeAgentBridge` emits the existing typed `NodeProblem` and safe observation | Existing HITL1 graph recovery, at most one automatic retry / two brief invocations | Existing typed blocked outcome only after recovery exhausts or is not eligible | Render the shared terminal category, diagnostic reference, and its existing safe fresh-start guidance | Bridge/HITL1 lifecycle replay with timeout then success, and exhaustion |
| Tavily read timeout, transport failure, HTTP 429, or HTTP 500-599 | The direct demo web-tool adapter classifies the direct public failure | That adapter only, at most three attempts with a per-attempt deadline and cancellable backoff | Bounded redacted unavailable tool result; it does not independently terminally end the graph | The existing worker may continue within its policy; an eventual terminal uses the shared lifecycle outcome | Adapter fake outcomes prove retry sequence, cap, backoff and payload |
| Tavily authentication, invalid input, non-429 4xx, unknown error, or cancellation | The direct demo web-tool adapter | None; cancellation propagates and all other categories return after the first attempt | No fabricated retry or success; cancellation has no terminal projection from the adapter | Existing worker/lifecycle behavior only | Adapter fake outcomes prove one attempt and `CancelledError` propagation |
| Invalid HITL1 brief JSON or a prompt/schema key mismatch | HITL1 prompt/parser plus the strict domain validator | Existing HITL1 structural repair, at most two brief candidates total | Existing typed output-validation blocked result after repair exhaustion | Render the shared category, diagnostic reference, and its existing legal next action; do not expose raw model output | Prompt/parser compatibility fixture plus HITL1 repair/exhaustion lifecycle test |
| Typed terminal is rendered by the standalone CLI | `ResearchRunExperience` / shared `Terminal` | None; CLI does not retry, reclassify, or inspect to discover a category | Safe terminal text retains category, phase, diagnostic reference, durability truth, and legal next action | Read-only inspection only when the shared terminal authorizes it; otherwise the supplied next action | Terminal projection fixture containing a provider/output-contract failure |

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Whether an external failure is retry-eligible | None; retry eligibility is a closed technical classification | The demo web-tool adapter classifies direct Tavily/public `httpx` facts for this change; `RuntimeNodeAgentBridge` remains the existing model boundary; classifier tests evaluate both owned seams | non-bypassable | Only the existing graph recovery or the idempotent adapter may retry within its declared cap; cancellation always escapes | Avoid a shared catch-all retry controller and CLI/provider-specific duplicate classifiers | Fake timeout/network/status/unknown/cancellation sequences |
| Whether the model may emit a JSON field | None; model output remains an untrusted candidate | HITL1 expected-output builder plus strict parser/domain schema; compatibility test evaluates accepted keys, values, and bounds | bounded-repair | Parser is the only admission owner; repair uses the existing bounded route | Avoid unsupported prompt-only fields and a second schema registry | Prompt builder output passed through parser-compatible fixtures |
| What an operator sees after terminal failure | None; presentation does not decide recovery | Shared typed `Terminal` / `RunFailure`; projection fixture evaluates visible safe fields | advisory | No raw exception, provider body, inferred retry, or cross-process resume claim | Avoid a second terminal-classification/recovery layer in the CLI | Returned terminal fixtures with distinct safe categories and diagnostic locations |

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `demo-pipeline`: Define bounded retry, deadline, cancellation, and safe result behavior for configured idempotent demo web reads.
- `hitl1-node`: Require parser-compatible model-visible structured-brief output guidance, and retain an actionable safe failure category on the blocked route.

## Impact

- Affected downstream code is limited to `deerflow_research/scripts/_demo_core.py`, the real HITL1 prompt/admission path, the existing standalone CLI terminal-projection seam, and their focused tests and run documentation.
- No upstream `backend/` or `frontend/` files change. No public API, credential format, configured provider, or CLI invocation syntax changes.
- The existing `node-agent-runtime`, `workflow-failure-outcomes`, and `research-cli-onboarding` contracts remain sources of typed provider/lifecycle semantics; this change consumes and verifies their ownership rather than adding a competing controller.
