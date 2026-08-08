## Why

Wave0 and Wave1 already enforce bounded retrieval, typed candidates, provenance,
and deterministic admission, but their current evidence primarily proves structural
conformance. The next roadmap step must make their model-visible source/evidence
judgment criteria and bounded feedback explicit, without treating a fluent source,
claim, or critic verdict as accepted evidence, a gate decision, or a route.

## What Changes

- Calibrate Wave0's existing source-intake worker and its zero-tool repair at the
  existing initial parser/typed-structural-output seam so a candidate distinguishes
  assignment-relevant, independent source metadata from untrusted retrieved content,
  preserves honest degradation, and cannot broaden an invalid draft into evidence or
  authority. The repair invocation will receive the same trusted assignment and a
  compact closed structural-failure category, while its invalid draft and retained
  retrieval observations remain untrusted data. The trusted assignment constrains
  scope but cannot seed source metadata or facts. Later submission validation is not
  a repair trigger or repair input.
- Calibrate Wave1's baseline-aware evidence worker, its existing pre-persistence
  structured repair (initial parser or local semantic-validation failure),
  SourceDiagnostic, and ClaimVerifier policies so candidates distinguish accepted
  Wave0 baseline coverage, new-source evidence, claim provenance/counterevidence,
  bounded uncertainty, and review-only verdicts. Its repair invocation will use the
  same bounded feedback boundary as Wave0 without exposing raw validator errors or
  authority-bearing state; its baseline projection cannot seed repaired evidence; and
  later submission validation remains controller-owned.
- Add a separate, labeled test-only evidence-intake calibration corpus with one
  normal and one highest-risk case for each of the six existing branches. It will
  reuse the typed live-rubric reporting contract while remaining separate from the
  prior intake/planning corpus, `LIVE_CANARIES`, and the lane-neutral
  `ScenarioCase` registry.
- Retain deterministic request, tool-posture, repair-feedback wiring, validation,
  review-artifact, and non-admission proof at the existing node/work-unit seams.
  Credentialed live evaluation will be explicitly selected and supplemental:
  tool-bearing cases use a real model-and-web branch runner and fail strict
  model-and-web preflight when the required credentials are absent; zero-tool cases
  use a real model-only branch runner.

## Change Focus

- **Primary module / causal owner:** `agent/src/deerflow_deep_research/graph/nodes/wave0/`
  owns the first model-visible source-intake candidate for a planner-assigned topic.
- **Question:** Can the existing Wave0 source-intake branches and the necessary
  baseline-consuming Wave1 branches produce conservative, assignment-faithful
  evidence candidates for a bounded labeled corpus while preserving the current
  deterministic evidence, review, and route owners?
- **Necessary adjacent/external contracts:**
  `graph/nodes/wave1/` consumes the accepted Wave0 baseline and owns the four
  evidence-extraction/review candidate boundaries; its question is whether those
  policies keep baseline-newness, provenance, uncertainty, and critic scope visible
  without treating a critic as a gate owner. `evaluation-hardening` and the
  test-only live calibration/report contract own the question of how the separate
  corpus, strict web/model preflight, deterministic conformance, and selected live
  judgment evidence remain distinguishable.
- **Evidence seam:** production prompt builders and Wave0/Wave1 subgraph repair
  invocations plus real nodes with fake capabilities for deterministic
  request/admission assertions; a separate selected `requires_llm` calibration case
  with a typed rubric for each judgment claim.
- **Not in scope:** `backend/`, `frontend/`, HITL1/topic planning, Wave2/targeted
  evidence, HITL2/readiness/final delivery, provider selection, runtime bridge
  policy, tool inventory, graph topology, retry/fallback budgets, evidence schemas,
  ledger/checkpoint mutation, gate/route authority, canonical live-canary count or
  deadline budget, and any claim that a source or research conclusion is true.
- **Triggered charter policies:** change-admission, node-agent-workflow-integrity, workflow-outcome-review

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave0 source intake | node-agent | Which assignment-relevant, independent source metadata can be proposed after bounded retrieval, including an honest limitation? | WorkSpec/topic assignment is trusted; tool/model material remains untrusted. | Required retrieval; the request's 1--3 `tool_call_limit` window is enforced by bridge middleware, while the capability/runtime policy enforces the allow-list, containment, and wider budgets. | `Wave0WorkerOutput` / `CandidateResult`; existing submit validator, work-unit controller, and ledger alone admit evidence. | Existing parser/typed-structural zero-tool repair and work-unit recovery bounds. | `build_wave0_worker_prompt` plus real Wave0 fake-capability workflow tests. |
| Wave0 source-intake repair | node-agent | Can one parser/typed-structural-invalid source draft be repaired from the same assignment, draft, and retained observations without retrieval or invention? | Only the initial request's topic projection and a compact structural category are trusted scope context; they cannot seed source metadata or facts. Draft/tool observations remain untrusted. A later submission-validation code is never an input. | Forbidden; existing Wave0 bridge and request binding. | `Wave0WorkerOutput` / `CandidateResult`; existing validator/controller/ledger admit or reject it. | The existing one repair applies only at the initial parser/typed-structural seam; later submission validation follows the existing failed-attempt/controller path. | Repair prompt, subgraph-feedback, and no-artifact-admission tests. |
| Wave1 evidence extraction | node-agent | Which new, provenance-bound evidence candidates can extend the accepted Wave0 baseline for the assigned topic? | WorkSpec/topic/baseline are trusted; tool/model material is untrusted. | One required retrieval; the request's exact-one `tool_call_limit` is enforced by bridge middleware, while the capability/runtime policy enforces tool scope, containment, and wider budgets. | `Wave1WorkerOutput` / `CandidateResult`; existing validator/controller/ledger admit evidence. | Existing parser/local-semantic zero-tool repair and work-unit outcome bounds. | `build_wave1_worker_prompt` plus real Wave1 fake-capability workflow tests. |
| Wave1 evidence repair | node-agent | Can one parser- or local-semantic-invalid evidence draft be repaired using the same assignment and retained observations without adding source, claim, or open-question authority? | Only the initial topic/Wave0-baseline projection and compact category are trusted scope context; baseline URLs cannot seed evidence. Invalid draft/retained observations remain untrusted. A later submission-validation code is never an input. | Forbidden; existing Wave1 request binding. | `Wave1WorkerOutput` / `CandidateResult`; existing validator/controller/ledger admit or reject it. | The existing one repair applies only at the parser or local pre-persistence semantic seam; later submission validation follows the existing failed-attempt/controller path. | Repair prompt, subgraph-feedback, and malformed-repair tests. |
| Wave1 SourceDiagnostic | node-agent | How should only the accepted assigned new-source observations be classified for bounded review? | Accepted record identity/source selection is trusted; observations and model summary are untrusted. | Forbidden; existing Wave1 runtime bridge. | `SourceDiagnosticResult`; existing review-artifact materializer validates binding and admits the artifact. | Existing missing-review dispatch during review construction; a failed or malformed newly dispatched result is suppressed and the existing gate outcome remains owner-controlled. | Source-diagnostic prompt and bound-artifact tests. |
| Wave1 ClaimVerifier | node-agent | How should only the accepted assigned claims and new-source identities be assessed for bounded support uncertainty? | Accepted record identity/claims/source ids are trusted; claim text and model summary are untrusted. | Forbidden; existing Wave1 runtime bridge. | `ClaimVerifierResult`; existing review-artifact materializer validates binding and admits the artifact. | Existing missing-review dispatch during review construction; a failed or malformed newly dispatched result is suppressed and the existing gate outcome remains owner-controlled. | Claim-verifier prompt and bound-artifact tests. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| A selected tool-bearing calibration lacks required model or web credentials | `preflight_live_environment` | Operator configuration; no invocation or automatic retry | Selected test fails before execution and produces no quality evidence | Configure supported credentials or do not select that case | Live preflight and calibration-selection tests |
| A Wave0 initial summary cannot parse into its typed worker output | Existing Wave0 parser/subgraph | Existing one zero-tool repair only at that parser/typed-structural seam; subsequent failure follows the existing work-unit failed-attempt path | No `CandidateResult` from that attempt; controller owns its legal retry or terminal outcome | Correct the policy or parser-compatible candidate and rerun deterministic evidence | Wave0 repair prompt, subgraph, and real-node fake-capability tests |
| A Wave1 initial summary cannot parse or fails local pre-persistence provenance, uniqueness, or new-source-floor validation | Existing Wave1 parser/local semantic validator/subgraph | Existing one zero-tool repair only at that pre-persistence seam; subsequent failure follows the existing work-unit failed-attempt path | No `CandidateResult` from that attempt; controller owns its legal retry or terminal outcome | Correct the policy or locally valid candidate and rerun deterministic evidence | Wave1 repair prompt, subgraph, and real-node fake-capability tests |
| A constructed Wave0 or Wave1 candidate fails post-candidate submission validation | Shared `submit_candidate_if_active()` / work-unit controller | Existing `VALIDATION_FAILED` terminal update, retry allocation, and gate bound; it never invokes a zero-tool repair or supplies validation codes to one | No `SubmissionRecord`; existing controller retry/gate or terminal disposition | Correct the deterministic candidate/validation path and rerun its narrow controller evidence | Shared submission/controller tests plus Wave0/Wave1 real-node fake-capability tests |
| A newly dispatched SourceDiagnostic or ClaimVerifier output is malformed, out of assignment, or incomplete | Existing review dispatcher/materializer | `build_wave1_gate_review()` dispatches missing critics during review construction; a failed or malformed new result is suppressed, not guaranteed a retry | No valid review artifact; existing gate repair or blocked outcome remains owner-controlled | Correct the critic policy or deterministic binding violation | Critic prompt, review-materializer, and gate-projection tests |
| A selected live branch violates tool/bound, bridge, parser, or Wave1 local-semantic hard invariants | Test-only selected-live runner plus existing bridge/parser | No automatic recovery or production retry; one declared outer attempt only | Selected test fails and records no rubric disposition or quality evidence | Correct the branch runner, fixture, or candidate policy and rerun the selected case | Live-runner contract, preflight, and branch request-composition tests |
| A selected live candidate is structurally valid but misses a declared judgment criterion | Test-only calibration rubric evaluator | No automatic recovery or production retry | Typed `limited` or `inconclusive` supplemental result | Review the branch-local policy/corpus; do not alter evidence acceptance, gate, or route | Typed rubric/report tests plus branch request-composition tests |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave0-node`: define calibrated source-intake and repair candidate behavior without changing
  retrieval, evidence admission, controller, ledger, or route authority.
- `wave1-node`: define calibrated baseline-aware extraction, repair, source-diagnostic, and
  claim-verifier behavior without changing provenance validation, review-artifact admission,
  gate, or route authority.
- `evaluation-hardening`: define branch-specific deterministic and optional live calibration
  evidence for the six Wave0/Wave1 evidence-intake judgment claims.

## Impact

- Affected implementation scope is limited to the package-local Wave0/Wave1 capability Markdown,
  prompt composition, and existing pre-persistence Wave0/Wave1 repair-invocation wiring, generated prompt-catalog
  projection, and focused `agent/tests/` evidence/evaluation assets. The existing test-only
  live-rubric/report contract may receive a compatible extension only if the separate corpus
  cannot reuse it as-is.
- The implementation is expected to register `WAN-008`, `WON-008`, and `EVH-019` in
  `openspec/governance/req-registry.yaml`; registry metadata does not grant runtime authority.
- No public API, DeerFlow host interface, database schema, provider configuration, tool inventory,
  `backend/`, or `frontend/` change is introduced.
- Default deterministic verification remains network-free; selected tool-bearing live calibration
  requires both model and web credentials and selected zero-tool cases require model credentials.
