## Why

Wave1's real top-level node currently passes an empty Wave0 URL baseline to its
worker, even though the worker correctly excludes a supplied baseline duplicate.
Its real gate contains only the shared work-completion rule, while the accepted
Wave1 contract requires per-topic source-floor, critic-review, and open-question
conditions. The critic artifacts have no Wave1 producer today, so a literal gate
check would make every real Wave1 execution repair and then exhaust. This is a
conformance defect, not evidence that the cognitive program is calibrated; it must
be repaired before Change 5 evaluates that program.

## Change Focus

- **Primary module / causal owner:** `graph/nodes/wave1/`; it owns Wave1's
  post-acceptance evidence-review lifecycle. `node.py::build_real` owns the
  authoritative baseline handoff and phase-local review construction, while the
  real Wave1 gate owns the resulting deterministic admission decision.
- **Product responsibility:** extract source-grounded evidence for one assigned
  research topic, then make its required independent reviews available to the
  bounded deterministic gate.
- **Participation mode / commitment state:** bounded cognitive program / current
  accepted. In addition to the existing retrieval worker and zero-tool structured
  repair, Wave1 has two bounded zero-tool critic branches: SourceDiagnostic and
  ClaimVerifier. Neither critic owns a route, checkpoint update, candidate
  admission, ledger write, or retry.
- **Question:** how can real Wave1 derive the current-generation Wave0 baseline,
  run its two required critics against accepted and provenance-bound observations,
  and give a pure gate only bounded review facts, so a duplicate, insufficient
  coverage, missing review, or disallowed open question cannot pass?
- **Necessary adjacent/external contracts:**
  - The work-unit store and `SubmissionRecord` contract answer which accepted
    Wave0 URLs and Wave1 result records belong to the current research generation;
    they remain the source and record fact authorities.
  - The existing attempt-scoped cache writer answers how an accepted Wave1 attempt
    can retain immutable review records. It does not make review records accepted
    evidence or grant them ledger authority.
  - The graph wrapper/gate adapter answer how a Wave1-only non-checkpointed review
    projection reaches the real gate. `WorkUnitGateView` remains unchanged.
  - The existing node-agent capability/runtime contracts answer how the new
    forbidden-tool requests are admitted before model-visible work; they do not
    grant the critic an action or lifecycle role.
  - Cognitive-program evidence, capability, prompt-catalog, and evaluation
    contracts answer the exact eighteen-branch review denominator and evidence
    closure.
- **Evidence seam:** scripted-real `NODE_SPEC.real_factory` execution backed by
  the real work-unit store, then the real Wave1 gate. It proves baseline handoff,
  critic request/materialization, and pass/repair/blocked behavior without a
  provider or live critic judgment.
- **Not in scope:** source-body capture or source-quality calibration; changing
  Wave0, Wave2, or targeted-evidence phase/route authority; generic work-unit gate
  view expansion; broad retry redesign; backend/ or frontend/ changes; any critic
  candidate, ledger, checkpoint, or route authority. Existing
  `untrusted_tool_results` are not persisted or used as critic input because they
  are ephemeral and lack a provenance-preserving source-id mapping.
- **Triggered charter policies:** node-agent-workflow-integrity, workflow-outcome-review

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave1 retrieval worker | node-agent | Find source-grounded evidence beyond the assigned Wave0 baseline for one topic. | Topic and ledger-derived baseline are trusted assignment; tool/model/source content is untrusted data. | One requested retrieval; the existing Wave1 capability, execution policy, and node-agent bridge enforce it. | `Wave1WorkerOutput` is parsed and submitted only through the existing validator/controller/ledger. | Existing invocation normalizer and work-unit controller retain the current bounded worker retry and terminal behavior. | Scripted-real Wave1 work-unit integration. |
| Wave1 structured repair | node-agent | Convert a malformed bounded draft and retained observations into the existing output schema. | Draft and retained tool observations are untrusted; no new source, claim, or question may be invented. | Forbidden tools, enforced by the local repair capability and bridge. | The same parser, validator, controller, and ledger remain the sole admission path. | Existing normalized invocation and parser failure path; no new recovery loop. | Malformed-draft integration test. |
| Wave1 SourceDiagnostic | node-agent | Classify the accepted new-source observations for trust/materiality and cross-verification signals. | Accepted Wave1 identity and source selection are trusted; the compact persisted source observation is untrusted data. Raw tool results, candidate paths, and source bodies not retained by Wave1 are absent. | Forbidden tools, enforced by `wave1-source-diagnostic` and the existing bridge capability admission. | `SourceDiagnosticResult` is admitted only by the Wave1 critic materializer after exact per-work binding checks. | A non-successful or invalid result writes no review artifact; the existing Wave1 gate's bounded repair/exhaustion behavior owns recovery. | Scripted critic dispatch plus bound-artifact materialization test. |
| Wave1 ClaimVerifier | node-agent | Assess each accepted Wave1 claim against its assigned new-source identities. | Accepted claim/source identities are trusted assignment; claim text is untrusted data. No tool result, artifact path, gate feedback, or route is an input. | Forbidden tools, enforced by `wave1-claim-verifier` and the existing bridge capability admission. | `ClaimVerifierResult` is admitted only by the Wave1 critic materializer after exact claim/source binding checks. | A non-successful or invalid result writes no review artifact; the existing Wave1 gate's bounded repair/exhaustion behavior owns recovery. | Scripted critic dispatch plus bound-artifact materialization test. |
| Baseline, review projection, and gate | no-agent | Derive accepted facts and evaluate them deterministically; a model would obscure provenance and route ownership. | Accepted records and validated review artifacts are authoritative for projection construction; artifact locations, candidate bodies, and critic prose are not gate inputs. | No tools or model invocation. | The gate returns a typed verdict; the existing gate kernel/wrapper maps it to the legal route. | Record/review identity mismatch fails before gate evaluation; repairable coverage/review failures use the existing phase budget and fatigue handling. | Real top-level node plus real Wave1 gate test. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Required same-generation Wave0 record is unavailable, malformed, or does not reconcile | Work-unit store plus validated `SubmissionRecord` contract | No new recovery is introduced; real Wave1 fails closed before worker dispatch. | No worker candidate or route is emitted from the failed handoff. | Existing outer lifecycle failure handling only. | Top-level factory test proves no empty-baseline substitution or agent call. |
| A parsed Wave1 draft has a foreign claim reference, duplicate canonical source URL, or insufficient new-source floor | Wave1 pre-persistence semantic validator, then the contract-specific submission validator | The bounded zero-tool repair receives a provenance, uniqueness, or floor violation before any source/result write; an inadequate repaired draft follows the existing worker failure/retry and gate-fatigue bound. The submit validator independently rejects any persisted divergence or newness-marker mismatch. | No source/result or candidate artifact is written for a pre-persistence rejection; no ledger record is appended for either rejection. | Existing structured repair, then the existing worker retry or `repair`/`exhausted` lifecycle mapping. | Scripted malformed-draft and persisted-document submit-validator tests. |
| A critic invocation fails or returns an invalid/unbound result | Wave1 critic materializer and accepted attempt identity | The next existing Wave1 repair visit may re-run only the missing critic; existing gate budget and fatigue bounds apply. | Existing blocked/exhausted projection once the bound is consumed. | Route only through the existing `repair` or `exhausted` mapping. | Scripted failed/invalid critic plus real-gate assertion. |
| A persisted critic artifact is malformed, conflicts with its accepted record, or cannot be reconciled | Wave1 review-artifact reader and projection validator | No repair conversion: integrity failure is rejected before business-gate evaluation. | No pass, repair, or route is emitted from malformed review input. | Existing closed validation/error boundary only. | Invalid review-artifact projection test. |
| New-source floor is unmet, one required critic artifact is absent, or an open question is in `targeted_search` | Frozen Wave1 review projection | Existing Wave1 gate and existing bounded repair budget after structural completion. | Existing blocked/exhausted projection after budget or fatigue exhaustion. | Route only through the existing `repair` or `exhausted` mapping. | Pure real-gate rule test plus scripted-real top-level integration. |

## What Changes

- Derive the real Wave1 worker's immutable Wave0 baseline from same-generation
  accepted Wave0 submission records through the authoritative store/record contract,
  preserving canonical URL semantics and failing closed rather than substituting an
  empty set.
- Add two Wave1-local, bounded, zero-tool critic branches after a Wave1 submission
  is accepted. SourceDiagnostic receives only the accepted new-source observations;
  ClaimVerifier receives only the accepted claims and assigned new-source identities.
  Each produces an immutable, identity-bound review artifact for that Wave1
  work/attempt. The critics do not reuse `targeted_evidence` phase or route authority.
- Add one Wave1-local pre-persistence semantic check for claim provenance, duplicate
  canonical URLs, baseline-derived newness, and the two-distinct-new-URL floor before
  any source/result write; then have contract-specific submit validation independently
  recompute those facts from the persisted result and accepted Wave0 records before a
  record is appended. The frozen review projection rechecks the floor at gate time.
  A pre-persistence violation enters structured repair before any artifact/candidate
  admission.
- Construct a Wave1-only frozen, non-checkpointed review projection after work-unit
  reconciliation. Keep `WorkUnitGateView` unchanged; neither the projection nor the
  gate contains artifact paths, candidate bodies, source bodies, critic reasons, or
  route authority.
- Extend the real Wave1 gate, after structural completion, with the two-distinct-
  canonical-new-source floor, both bound critic artifacts, and allowed open-question
  states. Preserve the gate kernel, repair budget, fatigue behavior, and
  `{PASS: pass, REPAIR: repair, BLOCKED: exhausted}` route map.
- Extend the direct-branch governance denominator from sixteen to eighteen:
  `wave1/source-diagnostic` and `wave1/claim-verifier` receive local capabilities,
  prompt-catalog cases, individual evidence-ledger rows, and independent normal/risk
  deterministic claims. Regenerate the committed prompt catalog.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave1-node`: enforce the real Wave0 baseline handoff and post-acceptance
  Wave1-local critic review, then consume bounded review facts in the real gate.
- `cognitive-program-evidence`: raise the exact active direct-branch coverage from
  sixteen to eighteen.
- `node-agent-capabilities`: add the two forbidden-tool Wave1 critic capabilities
  to the planning/initial-intake capability cohort and update the final denominator.
- `node-prompt-catalog`: add Wave1 SourceDiagnostic and ClaimVerifier generated
  catalog cases.
- `evaluation-hardening`: require separate normal and highest-risk deterministic
  evidence claims for each Wave1 critic branch.

## Impact

- Likely code: `agent/src/deerflow_deep_research/graph/nodes/wave1/`, the
  Wave1 result-contract/contract-specific submission-validation seam in
  `domain/wave1.py` and `engine/work_units/validation.py`, the Wave1-specific
  graph-wrapper/gate-preview seam, and `engine/gate_fixtures.py`. The existing
  attempt-cache writer is consumed through its constrained interface; its generic
  ledger, routing, and `WorkUnitGateView` contracts do not expand.
- Likely evidence: focused Wave1 integration and gate tests; prompt/capability
  catalog tests and generated `agent/node_prompts/`; the test-owned capability,
  cognitive-program, and requirement-evidence inventories.
- No public API, backend, frontend, provider credential, live-evaluation, or generic
  `WorkUnitGateView` contract change is proposed.
