## Why

The project has repeatedly repaired individual confirmation, profile, prompt, and
release-test failures without establishing one owner for the semantic handoff between
a user's free-text decision and research authority. The only full-real release
acceptance currently skips that handoff by injecting a JSON profile, so a green
lifecycle cannot demonstrate the product's intended path: a person confirms a
model-led proposal and receives a readable, cited report.

## What Changes

- Add a `research-confirmation` capability: a deep, deterministic domain boundary
  that turns a current proposal plus an explicit human decision or a bounded model
  candidate into either Accepted Research Facts or one outstanding User Decision.
  The original request stays authoritative as user-provided text; a model proposal
  or semantic interpretation remains advisory until this boundary admits it.
- Make HITL1 an adapter to that boundary for complete-proposal conversation. It
  continues to own the existing graph interrupt, checkpoint writes, profile artifact
  publication, routes, and provider/recovery behavior. The model continues to lead
  free-text explanation and interpretation, with the existing exact clear-confirmation
  fast path retained only as an invisible reliability optimization.
- Upgrade the singular `release-full-real-acceptance` scenario to begin with the
  fixed Chinese Python 3.12 request, wait for a model-led proposal, submit natural
  text confirmation, and then use the existing completion path. Remove its
  hand-authored JSON profile injection.
- Add release-only source containment to the live test adapter: the fixed smoke
  scenario may return and cite only its declared three-page `docs.python.org` source
  set, with at least two distinct pages represented in final citations. This is a
  verification constraint, not a production web-source policy or a new runtime
  controller.
- Extend release evidence so the fixed scenario proves the confirmation handoff,
  a non-empty Chinese report with at least three cited claim bindings and two
  distinct declared first-party sources. Preserve the frozen 2026-07-17 version-1
  attestation as historical evidence; only a separately selected successful real
  release run may produce a redacted version-2 attestation for this smoke contract.
  Deterministic tests prove both attestation schemas and the new seams without
  spending model or web calls or manufacturing a new release claim.

## Capabilities

### New Capabilities

- `research-confirmation`: Candidate-to-fact admission for a model-led research
  conversation, with a single outstanding-decision result when authority is not yet
  present.

### Modified Capabilities

- `hitl1-node`: Delegate complete-proposal confirmation to the new domain boundary
  while retaining existing graph, persistence, and bounded model-failure ownership.
- `evaluation-hardening`: Make the one existing full-real release scenario exercise
  a model-led Chinese confirmation and bounded first-party evidence rather than a
  profile fixture bypass.
- `research-run-experience`: Render every material typed proposal constraint in the
  shared confirmation view before a person can accept it, without silently dropping
  fields beyond the current eight-line projection cap.
- `project-structure`: Register the new pure confirmation domain module and its
  focused deterministic test surface in the existing downstream structure inventory.

## Change Focus

- **Primary module / causal owner:** proposed `domain/research_confirmation.py`, the pure candidate-to-fact admission boundary for one current research proposal.
- **Question:** How can free-text model-led confirmation preserve a person's request and authority while producing only accepted facts or one actionable outstanding User Decision, without making the domain module a graph, persistence, terminal, or provider controller?
- **Necessary adjacent/external contracts:** `human-interaction-contract` supplies the existing closed proposal, candidate, resolution, feedback, and visible-control contracts; `hitl1-node` answers how an admitted outcome maps to the existing checkpoint/profile writer and route; `research-run-experience` answers how every material typed proposal constraint becomes visible before confirmation; `evaluation-hardening` answers how the singular public-entry release seam proves the real handoff; `tests/scenarios/canaries.py` supplies a test-only web adapter whose source filter must not become production policy; `tests/assets/release_attestation.py` supplies the frozen v1 provenance contract and the versioned redacted-attestation validation boundary.
- **Evidence seam:** pure domain admission tests, real-HITL1/fake-capability lifecycle tests, deterministic release-runner and release-attestation contract tests, and the existing manually selected `release_e2e` public-entry test.
- **Not in scope:** `backend/` or `frontend/`; a global source allowlist; web-search/product policy changes; a second release runner; model/provider retry redesign; automatic user acceptance; changing the existing non-interactive auto-profile policy; a new graph controller; rewriting or backfilling the historical v1 attestation; creating a fresh attestation without a separately selected real release run; treating one live run as a general research-quality proof.
- **Triggered review policies:** human-interaction-integrity, node-agent-workflow-integrity, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Whether a proposed research profile may direct active research | The Primary User confirms the visible current proposal, either through natural text or the existing control | An `AcceptedResearchFacts` outcome is validated by Research Confirmation and consumed by HITL1 before its existing profile writer | human-decision | Only the currently displayed complete proposal can be admitted; a revision requires a new confirmation | Reuse correlated HITL1 input and the existing profile writer; avoid an adapter-specific action parser | Domain result tests plus real-HITL1 lifecycle tests |
| Whether a model interpretation can create a research fact | A zero-tool semantic-intake candidate interprets one reply against one current proposal | Research Confirmation validates the candidate shape and resolves it to accepted facts or an outstanding decision; HITL1 alone maps that result to state | non-bypassable | A candidate has no route, checkpoint, artifact, or accepted-fact authority; ambiguity and invalid output preserve a confirmable proposal | Reuse `SemanticCandidate`, `InteractionProjection`, and existing bounded fallback instead of adding a second controller | Candidate-admission tests and the existing semantic fallback lifecycle seam |
| Whether the smoke scenario may use a source | The fixed user request asks for Python official documentation only | The release test adapter validates returned/cited canonical URLs against the declared three-page Python source set | non-bypassable | The release proof fails rather than silently broadening to another source; production source behavior is unchanged | Keep the constraint in the existing test adapter rather than adding a product source-policy layer | Deterministic adapter/runner tests and the manual release report |
| Whether a release attestation may claim the new smoke facts | A separately authorized operator selects and reviews one successful real release run; neither a model nor a deterministic test supplies that proof | The versioned attestation builder/validator verifies a complete matching `ReleaseReport`; selected-run provenance remains operator evidence, and the committed v1 artifact remains its own historical contract | non-bypassable | v1 cannot acquire new invariant names, and v2 rejects a failed, mismatched, or unpaired report; raw report/model/source content and credentials remain excluded | Reuse the singular runner and redaction scanner instead of creating a second release lane or recasting old evidence | v1-preservation and synthetic-v2 contract tests, followed only by a separately selected real release run |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Semantic-intake provider or structured-output failure | Existing bridge `NodeProblem` and HITL1's existing typed feedback path | Existing HITL1 semantic-intake loop; no new retry or repair bound | Non-terminal feedback preserves the current proposal | Confirm the visible proposal with its existing control or a later clear reply | Existing HITL1 semantic-fallback lifecycle tests, updated for the domain result boundary |
| Invalid, stale, or incomplete candidate/confirmation | Research Confirmation's deterministic validation result; HITL1 retains correlation validation | No automatic semantic admission; preserve or reissue the current outstanding decision through the existing HITL1 path | Current proposal remains pending, or existing invalid-input handling applies | Supply a fresh correlated response to the displayed proposal | Pure admission tests and HITL1 correlation tests |
| No declared first-party source-set result in the manual release smoke | Release test adapter and release assertion, not product lifecycle state | No fallback to another source; one selected manual release attempt retains the current runner bound | Release evidence fails with bounded diagnostics | Correct the test integration or rerun after the declared source is available | Test-only adapter and release-runner tests |
| A historical v1 attestation is used to imply new smoke evidence, or a v2 payload contains unredacted evidence | Versioned attestation validator and scanner | No automatic conversion, backfill, or cross-version comparison; reject a mixed schema or sensitive payload | Historical evidence stays historical; a new claim is absent until a selected run produces a matching v2 payload | Keep v1 unchanged, correct the bounded builder or perform a new selected run | Attestation compatibility and sensitivity tests |

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HITL1 profile brief | node-agent | Propose a compact research approach from the immutable original request, without answering the research question | Original request is user-provided data; the brief is advisory candidate data | Existing zero-tool HITL1 bridge and its existing invocation budget | `StructuredBrief`; Research Confirmation/HITL1 admit only after a current explicit user decision | Existing HITL1 brief repair/recovery behavior | Existing brief tests plus new candidate-to-fact tests |
| HITL1 semantic intake | node-agent | Interpret one free-text reply only against the supplied current proposal | Reply and proposal are untrusted-to-model data; no model result is a lifecycle command | Existing zero-tool semantic bridge and three-call cap | `SemanticCandidate`; Research Confirmation determines accepted facts or outstanding decision, HITL1 performs state effects | Existing HITL1 semantic fallback behavior | Existing semantic lifecycle tests plus new domain admission tests |
| Research Confirmation | no-agent | Validate a typed candidate and explicit human decision; it performs no cognitive interpretation | Receives already bounded typed contracts, never a runtime handle, provider fact, route, or raw model authority | No tools and no model invocation | Typed accepted-facts or outstanding-decision result; HITL1 remains the lifecycle adapter | Does not own provider failure, retry, terminal, or checkpoint recovery | Pure domain tests |

## Impact

- Affected code is limited to `deerflow_research/`: the human-interaction/profile
  domain boundary, HITL1 adapter/prompt tests, release scenario and its test-only live
  web adapter, release acceptance tests, and test-evidence assets as required by
  `evaluation-hardening`.
- Existing public lifecycle actions and the `ResearchRunExperience` typed projection
  remain compatible. No DeerFlow host API, `backend/`, or `frontend/` change is
  proposed.
- The fixed smoke request is:
  `请只使用 Python 官方文档，用中文为一个现有 Python Web 服务写一份升级到 Python 3.12 前的检查清单：列出三项最重要的兼容性或运行时变化，并为每项给出具体来源链接。`
