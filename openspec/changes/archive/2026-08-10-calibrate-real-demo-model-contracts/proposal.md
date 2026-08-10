## Why

`make demo-real-scripted` can currently resolve more than one configured model and
silently use registry order, while the Bundle-local Event Journal does not retain the
selected model profile or the safe reason beneath a broad `budget.exhausted` outcome.
The retained BUG-024 evidence therefore proves cross-node real-demo failures but cannot
tell an operator whether a particular profile, budget bound, or structured-output rule
caused them. Wave1's eager parallel-tool failure is already fixed; this change makes
the remaining failures diagnosable before anyone changes a model default or relaxes a
contract.

## What Changes

- Require an all-real demo invocation to resolve exactly one explicit configured model
  profile before Bundle admission. Missing, unknown, or non-unique selection fails the
  existing safe prerequisite path and creates no Bundle or Journal.
- Carry a trusted, redacted execution-profile identity and revision from the real-demo
  composition root into the admitted Bundle's Journal admission/summary facts. The
  profile is observational only and excludes credentials, endpoint URLs, prompts, and
  provider payloads.
- Extend Journal evidence for known node-agent budget stops with a closed safe
  subreason, without changing the existing failure category, retry policy, terminal
  route, or legal lifecycle action.
- Publish canonical initial/repair validation facts for Wave0 and topic-planning
  parser/materialization boundaries, matching the existing Journal treatment of Wave1
  and keeping raw drafts, exceptions, and model output out of retained evidence.
- Add deterministic evidence and an operator-facing bounded calibration procedure that
  runs an explicitly selected profile through existing real-demo evidence paths. It
  records facts for later comparison; it does not declare a model qualified from one
  run or change the selected default.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `demo-pipeline`: all-real demo admission resolves one explicit model profile rather
  than using incidental configured-model order, and exposes a bounded profile-specific
  calibration entry procedure.
- `run-event-journal`: admitted Bundles retain trusted execution-profile provenance,
  closed budget-stop subreasons, and canonical validation facts without becoming
  lifecycle authority.
- `node-agent-runtime`: the bridge exposes only a closed budget-stop reason to
  the Journal producer while preserving its current normalized result and recovery
  contracts.
- `topic-planning-node`: planner parser/materialization failures retain canonical
  initial/repair validation evidence through the existing Journal boundary.
- `wave0-node`: Wave0 parser and its one structural repair retain canonical
  initial/repair validation evidence through the existing Journal boundary.

## Impact

- Primary module: `deep_research_harness/scripts/_demo_core.py` for explicit
  real-demo model-profile resolution; adjacent downstream runtime modules own trusted
  Journal publication and normalized failure facts.
- Affected contracts and tests include `RunEvent`/`RunSummary`,
  `RunObservationStore`, `RuntimeNodeAgentBridge`, the Wave0/topic-planning nodes,
  their focused deterministic tests, and real-demo operator documentation.
- No modification is proposed under `deerflow/`, `backend/`, or `frontend/`; the
  change uses existing public DeerFlow runtime composition only.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/_demo_core.py` owns selection of the all-real demo's configured model profile before it creates the graph-backed execution environment.
- **Seam classification:** deterministic-guardrail — Journal evidence and attribution for existing profile, budget, and parser/materialization boundaries; no node capability Markdown, prompt builder, or feedback change, and the owning deterministic owners keep admission, recovery, route, and lifecycle authority.
- **Question:** How can an operator compare real-demo model profiles using Bundle-local, redacted, deterministic-at-the-boundary evidence without treating a diagnostic as lifecycle authority or inferring a model choice from configuration order?
- **Necessary adjacent/external contracts:** `run-event-journal` answers which execution and failure facts persist in a Bundle; `node-agent-runtime` answers which budget boundary produced a normalized stop; `topic-planning-node` and `wave0-node` answer which parser/materialization boundary owns validation facts; existing real-demo operator entry documents answer how an explicit profile is invoked.
- **Evidence seam:** focused zero-API tests for model-profile selection, Journal serialization/redaction, budget-reason propagation, and Wave0/topic-planning validation events; `UV_OFFLINE=1 make verify` remains the aggregate deterministic gate. A credentialed calibration run is bounded supplemental evidence, not proof of a distributional model-quality claim.
- **Not in scope:** selecting a new default model, changing model/provider credentials, altering budgets, prompts, tool windows, repair counts, retry/terminal/lifecycle behavior, or modifying the DeerFlow submodule, backend, or frontend.
- **Triggered review policies:** authority-and-projections, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| All-real demo model selection before Bundle admission | An operator supplies one deployment selector; no model, CLI/TUI caller, or registry ordering may choose a replacement | The trusted demo composition resolver validates a non-blank selector against credential-backed registered profiles and supplies exactly one config to the fixed real recipe | non-bypassable | A missing, unknown, or non-unique selection takes the existing prerequisite path before graph/Bundle/Journal creation; it cannot enter checkpoint state or a route | Reuse the existing credential preflight and fixed composition root; avoid a bridge-level selector, per-node model chooser, and order-dependent fallback | `tests/unit/test_demo_core.py` plus real-command preflight contracts prove both rejection-before-admission and one-config composition |
| Bundle-local profile provenance | An operator may inspect the retained safe selected-profile fact, but no participant may infer provenance when it is absent or treat an observed outcome as a qualification decision | The trusted composition envelope supplies safe identity/revision; the admitted Bundle's existing Journal recorder validates and retains matching admission/summary facts | advisory | The retained fact cannot select a Bundle/model, alter graph/checkpoint/lifecycle state, authorize retry/route, or create a cross-Bundle history | Reuse the existing trusted-envelope and optional recorder seam; avoid process-global logging and a new profile/lifecycle control surface | Journal serialization/reload/redaction tests plus a `BundleGraphExecutor` admitted/rejected-start test |
| Budget and parser/materialization attribution | No model candidate, raw exception, or diagnostic consumer decides recovery or terminal handling | Existing middleware/bridge normalization and Wave0/topic-planning parser/materializer boundaries produce closed observational facts; existing node/controller/lifecycle owners retain recovery and outcomes | advisory | Closed codes preserve the existing one-repair, provider-recovery, route, checkpoint, and terminal contracts; observation write failures remain isolated | Reuse the existing model-tool/validation Journal events and Wave1 local pattern; avoid raw-error logs, a generic controller, or a diagnostic retry layer | Focused middleware/bridge, Wave0, topic-planning, and Journal-event tests prove the real producer-to-recorder handoff |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Explicit profile is missing, unknown, or resolves non-uniquely | Real-demo prerequisite/model-profile resolver | None; admission rejects before graph or Bundle creation | Existing safe configuration prerequisite result | Configure one supported profile and start a new run | `tests/unit/test_demo_core.py` |
| A node-agent exhausts a known budget boundary | `BudgetMiddleware` and bridge normalization | Existing owning node/controller recovery only; this change adds no retry | Existing normalized failure and terminal route | Existing typed run outcome supplies the legal action | `tests/unit/test_budget_middleware.py`, `tests/unit/test_node_agent_bridge.py`, Journal store tests |
| Wave0 or topic-planning candidate cannot pass a parser/materialization boundary | Existing Wave0/topic-planning deterministic parser and node boundary | Existing one repair or node/controller recovery bound only | Existing structured-output or node failure outcome | Existing typed run outcome supplies the legal action | Focused Wave0/topic-planning graph tests and Journal event tests |
