## 1. Control Placement Review

- [x] 1.1 Apply-agent plan review: before editing code, re-read the proposal's Control Placement and Node Agent reviews; confirm the implementation keeps worker output advisory, parser/validators non-bypassable, the existing one-shot repair bounded, and Journal facts projection-only. Correct the implementation plan if any task introduces a new admission, retry, route, or raw-diagnostic path. Done when the focused deterministic seams in sections 2-5 are mapped to those four boundaries.

## 2. Closed Worker Completion Contracts

- [x] 2.1 Add red deterministic Wave0/Wave1 prompt and capability-resource tests for initial and repair branches: exact model-visible closed key sets and minimum shapes, tool-then-final JSON completion for initial workers, zero-tool repair, final self-check, and explicit prohibition of prose, fences, unlisted fields, and placeholders without changing existing request bounds or adding a placeholder validator. Retain parser regressions proving non-standalone prose/fenced/embedded JSON still follows the existing rejection path.
- [x] 2.2 Implement node-local compact completion-contract renderers in Wave0 and Wave1 prompt builders; use each renderer for both initial and repair requests and align the two activated capability Markdown resources with the same bounded cognitive sequence and self-check.
- [x] 2.3 Run the new prompt/capability selectors and confirm valid scripted candidates still use the unchanged parser, local semantic validation, and deterministic admission path.

## 3. Versioned Bundle Journal Facts

- [x] 3.1 Add red domain and recorder tests for a v3 Event Journal: accepted closed response shapes, `post_candidate` stage, rejected impossible category/stage/shape/code combinations, v3 manifest/high-watermark/retention health, serialized-byte redaction, and v1/v2 read-only compatibility with no inferred fields, append, or silent upgrade.
- [x] 3.2 Extend the typed Journal contracts, event recorder protocol, persistence reader/writer, manifest sequence/high-watermark handling, retention/availability logic, and supported inspection projection for v3 events and the optional closed `response_shape`; newly established Journals write v3, v1/v2 Bundles remain readable but read-only, attempted old-Journal writes use existing observation-failure health, and summaries remain unchanged.
- [x] 3.3 Add `FinalResponseShape` and its pure shared structural classifier to `domain/run_observation.py`, using the standard JSON decoder rather than bracket slicing; test the specified precedence, multiple/nested object edges, enum-only return, unchanged parser input, and absence of retained response content or parser detail.
- [x] 3.4 Run the focused Journal domain/recorder and inspection tests, including a persisted reload proving profile, shape, and canonical-code facts remain Bundle-local and no lifecycle result changes.

## 4. Deterministic Producer Handoffs

- [x] 4.1 Add red scripted real-work-unit regressions for Wave0 and Wave1 that distinguish initial/repair response shapes from parser codes, preserve the current one-repair/controller bounds, and require a parser-accepted submit rejection to be recorded as exactly one `post_candidate` event.
- [x] 4.2 Update Wave0 and Wave1 worker subgraphs to classify every returned initial/repair summary before their existing parser/local-validator boundary and record the closed shape with the existing correlated validation facts; preserve invocation failure behavior with no fabricated shape.
- [x] 4.3 Update the shared work-unit submit boundary to emit `post_candidate` only when its existing typed `SubmissionValidationFailure` is caught, remove its misleading empty initial/repair success event, and leave terminal updates, retries, ledger commits, gates, routes, and lifecycle behavior unchanged.
- [x] 4.4 Run the Wave0/Wave1 integration suites and assert accepted candidates, malformed candidates, local semantic failures, and later submission failures each retain the correct Journal timeline with no raw response or validator text.

## 5. Bundle-Bound Live Calibration

- [x] 5.1 Add red zero-API tests for every existing evidence-intake live branch's setup: one explicit profile must supply both the sole configured model and matching safe revision, a fresh Bundle and Event Journal must be admitted before bridge dependency resolution, `SelectedBundleContext` must reach the production node context, and setup failure must prevent provider invocation and rubric creation. Prove pre-admission failure creates no Bundle, worker/repair cases retain only their applicable validation facts, and critic cases fabricate none.
- [x] 5.2 Implement the focused calibration admission path using the trusted explicit-profile composition boundary and existing Bundle lifecycle/Journal APIs; invoke only the named production branch request and its existing production parser/validator, record response shape and canonical codes only for Wave0/Wave1 worker or repair cases, then inspect the same Bundle through the supported reader.
- [x] 5.3 Update live calibration reports and test-owned evidence metadata so reports expose only safe profile identity/revision, correlation, branch-applicable closed shape, and canonical codes; retain `requires_llm`, profile-scoped resource bounds, the existing typed rubric contract, and the no-ledger/no-gate/no-full-pipeline boundary.
- [x] 5.4 Run the offline scenario/unit selectors to prove the runner is Bundle-bound and redacted without credentials, then run each changed initial worker branch once for every available explicit profile. Persist safe diagnostic facts only in that invocation's Bundle Journal; keep the required test-owned live report bounded to the fields in 5.3.

## 6. Evidence and Verification

- [x] 6.1 Preserve the pre-registered `WAN`, `WON`, `WOU`, and `EVH` IDs and the existing modified `REJ` IDs while updating their requirement-impact, scenario, and collected-claim assets; add detector smoke coverage for every new executable registry rule.
- [x] 6.2 Run the narrow deterministic regression set first: `cd deep_research_harness && UV_OFFLINE=1 uv run --locked --no-sync --extra operations python -m pytest tests/graph/test_wave0_worker.py tests/unit/test_wave1_critic_prompts.py tests/graph/test_node_agent_capability_cohort.py tests/unit/test_run_observation_store.py tests/graph/test_work_unit_component.py tests/unit/test_evidence_intake_calibration.py tests/integration/test_demo_sessions.py tests/integration/test_wave0_work_units.py tests/integration/test_wave1_work_units.py -q`.
- [x] 6.3 After the focused live branch loop is stable for an available explicit profile, run one fresh `DEERFLOW_DEMO_MODEL=<profile> make demo-real-scripted` Bundle for that profile and verify its Bundle Journal shows advancement through both Wave0 and Wave1. Do not treat later-phase success as part of this change's claim.
- [x] 6.4 Before archive, run `cd deep_research_harness && UV_OFFLINE=1 make verify`, `openspec validate stabilize-evidence-worker-output-envelopes --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm `backend/` and `frontend/` remain clean.

## 7. Archive Closeout Review

- [x] 7.1 Archive-agent control-placement closeout review: compare the final diff and deterministic results with the proposal's Control Placement and Workflow Outcome reviews; correct any drift that lets a prompt, Journal fact, or live runner affect admission/recovery/lifecycle. Done when the focused suites prove the bounded handoffs and each required live profile has either the required Bundle-local results or a test-evidence note that its preflight prerequisite was unavailable and no Bundle/provider call was created, after which archive validation may proceed.
