## Why

After topic planning was aligned with its output budget, fresh explicit-profile Bundles
still block in Wave0 or Wave1 even though the tool-window defect is fixed. The
production parser, semantic checks, controller, and lifecycle correctly reject those
responses; the remaining cause is that the model-visible worker and repair programs do
not reliably make the required tool-then-final-JSON completion legible to a real model.

`_backlog/bugs/BUG-024-real-demo-flaky-against-model-contracts.md` is the causal
evidence source: it records the two fresh profile-attributed Bundle outcomes, the
redacted one-worker Wave1 reproduction, the passing focused deterministic baseline,
and the missing selected-context and post-candidate diagnostic facts. This change does
not reinterpret older unattributed runs as evidence for the proposed behavior.

The failure can be observed safely, but the direct evidence-intake live calibration does
not currently bind a `SelectedBundleContext`, so it fails before provider invocation and
cannot be the regression loop for this contract. It also lacks the two bounded facts
needed to distinguish final prose from a parser-accepted candidate that later fails
deterministic validation.

## What Changes

- Define compact, explicit JSON-only completion envelopes for the initial and existing
  one-shot repair programs of both Wave0 source intake and Wave1 evidence extraction.
  The initial programs make the permitted retrieval-then-final-candidate sequence,
  exact allowed keys, minimum valid shape, no-prose/no-fence rule, and final self-check
  visible; repair programs provide the same closed final envelope with their existing
  zero-tool posture.
- Preserve every deterministic owner and bound: result schemas, parser and semantic
  validators, provenance and new-source floors, tool windows, budgets, one-shot repair,
  controller retry, ledger, gate, routes, Bundle lifecycle, and selected-profile policy.
  The change does not relax a candidate contract or make prompt compliance an admission
  decision.
- Extend the Bundle-local Event Journal with only the missing closed diagnostic facts:
  final response shape (`empty`, `prose`, `fenced`, `embedded_json`, or `json_object`)
  at the existing initial/repair candidate boundary, plus exact canonical codes from a
  Wave0/Wave1 post-candidate deterministic validation boundary. These remain read-only
  observations and never retain raw draft/response, prompt, tool result, exception text,
  provider body, URL, or artifact path.
- Repair every selected live evidence-intake calibration branch to resolve one explicit
  demo profile and create and bind a real selected Run Bundle and its Journal before
  resolving the production bridge. Each invocation will still run only its named branch
  and existing branch-specific parser/validator. Wave0/Wave1 worker and repair branches
  additionally assert the closed response-shape and canonical validation facts at their
  existing candidate boundary; critic branches do not fabricate worker validation facts.
  The focused output-contract matrix runs each changed initial worker branch once per
  available explicit profile and remains a live dependency check, not a full-pipeline
  claim.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `wave0-node`: Wave0 initial and repair cognitive programs gain a compact final output
  envelope and retain safe structural/post-candidate validation evidence.
- `wave1-node`: Wave1 initial and repair cognitive programs gain a compact final output
  envelope and retain safe structural/post-candidate validation evidence.
- `run-event-journal`: Bundle-local validation observations expose a closed response
  shape and post-candidate canonical codes without becoming lifecycle authority.
- `work-unit-kernel`: the shared submit-validation boundary records its canonical
  rejection as `post_candidate` rather than conflating it with parser repair stages.
- `evaluation-hardening`: selected evidence-intake live calibration uses an admitted
  Bundle and explicit profile to prove the focused production output-contract seam.

## Impact

- Affected production areas: `graph/nodes/wave0/`, `graph/nodes/wave1/`, the existing
  Run Event Journal contract and its recorder, and the shared work-unit submit boundary.
- Affected evidence areas: Wave0/Wave1 prompt and work-unit integration tests, Journal
  contract tests, and `tests/scenarios/evidence_intake_live.py` with its selected live
  test.
- Affected governance: `openspec/governance/req-registry.yaml` pre-registers the new
  `WAN`, `WON`, `WOU`, and `EVH` requirement IDs; existing `REJ` IDs are modified in
  place. No policy or checker behavior changes.
- No changes under `deerflow/`, `backend/`, or `frontend/`; DeerFlow continues to be
  used only through the existing public runtime integration.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/` capability resources and prompt builders; they own the model-visible evidence-extraction completion program that freshly reproduced final prose after a retained tool call.
- **Seam classification:** cognitive-program because the candidate contract and controller correctly fail closed, while the model-visible initial and repair method must reliably request the bounded final representation.
- **Question:** Can both evidence workers make their existing retrieval-or-repair turn end in one compact, contract-valid JSON candidate, while any remaining malformed or later-invalid candidate is distinguishable from Bundle-local safe facts?
- **Necessary adjacent/external contracts:** `graph/nodes/wave0/` answers whether the shared output-envelope family also covers the flash Wave0 failure; `graph/components/work_units.py` answers how the shared deterministic submit boundary records one post-candidate fact without changing controller behavior; `domain/run_observation.py` and `runtime/run_observation.py` answer how the closed facts remain redacted Journal projections; `scripts/_demo_core.py` answers which existing registry resolves one explicit profile and its safe revision; `runtime/bundle_lifecycle.py` and `runtime/projection.py` answer how the test-owned Bundle is admitted and reduced to `SelectedBundleContext`; `tests/scenarios/evidence_intake_live.py` answers how one selected calibration branch composes those existing authorities. No new DeerFlow interface or upstream modification is required.
- **Evidence seam:** prompt/capability unit tests for the exact model-visible closed envelopes; scripted real Wave0/Wave1 work-unit integration tests for parser, local validation, repair, controller, and Journal handoff; one explicitly selected Bundle-bound invocation of each changed initial worker branch per available explicit profile; then one fresh all-real demo Bundle per available profile that must advance through both Wave0 and Wave1. The live loop proves only real model/tool output behavior not reproducible by scripted turns, and the demo confirmation proves advancement through the affected phases only.
- **Not in scope:** changing model defaults or profile selection; increasing budgets or tool windows; relaxing schemas, parser, provenance, source/newness floors, or submission validation; changing repair or controller bounds, ledger/gate/routes/lifecycle; retaining raw diagnostics; guarantees about later full-delivery quality or upstream DeerFlow changes.
- **Triggered review policies:** authority-and-projections, node-agent-workflow-integrity, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Initial tool-bearing worker completion | Wave0/Wave1 worker proposes one final JSON candidate after its existing permitted retrieval. | Existing worker parser and Wave1 local semantic validator classify the candidate; submission validation, controller, and ledger remain downstream owners. | advisory | Candidate text cannot admit evidence or bypass schema, source/newness, or submission checks; the existing one-shot repair remains the only pre-candidate recovery. | Reuses the existing request, parser, validator, and work-unit pipeline instead of adding a model-controlled success path. | Scripted real worker integration proves tool order, parser/semantic admission, and non-admission. |
| Zero-tool structural repair completion | Repair proposes only a JSON re-expression of the bounded untrusted draft and retained observations. | Existing Wave0/Wave1 subgraphs parse and validate the repaired candidate. | bounded-repair | One repair, no model-visible tool, and no invention beyond existing trusted/untrusted boundaries; later submission failure never re-enters repair. | Makes the existing repair's completion envelope explicit rather than adding retries or fallback agents. | Focused repair integration preserves request bounds and both validation facts. |
| Final response shape and post-candidate code | No cognitive or human decision; a deterministic classifier projects the already-observed response boundary and validator result. | Parser/subgraph and existing post-candidate validator own the direct fact; the Event Journal records a redacted projection. | advisory | Journal data cannot select a Bundle, accept a candidate, schedule recovery, alter a route, or change a terminal outcome. | Reuses the Bundle-local Journal rather than raw logs, an external store, or a diagnostic controller. | Journal domain/recorder tests plus work-unit handoff tests load the persisted projection and verify no raw content. |
| Selected calibration profile and Bundle binding | The operator selects one registered profile and one corpus case; no model or prompt may choose either. | The existing explicit-demo resolver returns the sole configured model together with its safe profile evidence; Bundle lifecycle and runtime projection own admission and `SelectedBundleContext`. | non-bypassable | Absent, unknown, non-unique, or unavailable prerequisites fail before Bundle admission/provider invocation; retained profile data remains observation-only. | Reuses the existing trusted profile resolver, Bundle lifecycle, Journal recorder, and dependency resolver instead of adding a test-owned identity path. | Zero-API runner setup tests prove model/evidence pairing, admission ordering, selected context, and no provider/rubric on preflight failure. |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Final candidate is empty, prose, fenced, embedded JSON, or invalid JSON | Existing worker parser and subgraph own the canonical structural result; Journal projects its closed response shape and code. | Existing Wave0/Wave1 subgraph invokes at most one zero-tool repair; existing work-unit controller owns later attempt retry. | Existing structured-output failure and controller exhaustion behavior. | Inspect the selected Bundle Journal, then use only the lifecycle action already returned by the terminal result. | Scripted malformed-turn integration retains separate initial/repair facts and reaches existing non-admission. |
| Parser-accepted candidate fails Wave1 local semantic validation | Existing Wave1 local validator owns canonical codes; Journal retains its closed stage and response shape. | Existing Wave1 subgraph applies its existing one zero-tool repair; controller remains bounded as today. | Existing structured-output/controller outcome. | Inspect the selected Bundle Journal; no model-selected retry or profile switch is implied. | Scripted semantic-invalid candidate proves repair, revalidation, and no early ledger admission. |
| Parser-accepted candidate fails later Wave0 or Wave1 submission/artifact validation | Existing submit/artifact validator owns canonical codes and controller owns failed attempt aggregation. | No cognitive repair; existing work-unit controller owns its existing retry/exhaustion bound. | Existing submission-validation/controller terminal behavior. | Inspect the selected Bundle Journal and follow the typed terminal lifecycle action. | Work-unit integration proves one correlated post-candidate Journal code, no repair request, and no ledger publication. |
| Journal persistence is incomplete or unavailable | Existing Journal recorder owns its health projection. | No recovery is added; graph and lifecycle retain their current behavior. | Existing Journal-health observation, independent of research terminal outcome. | Use the existing typed lifecycle result; do not reconstruct a Run from diagnostics. | Recorder persistence/retention tests prove health changes without changing the work result. |
| Selected calibration profile, credential, Bundle, or branch prerequisite is unavailable | Existing explicit-profile resolver, strict branch preflight, Bundle lifecycle, and dependency resolver own the direct failure. | No in-case recovery or fallback profile; the selected one-attempt live case stops before provider invocation. | Existing live preflight or hard-invariant failure with no rubric disposition. | Supply the missing prerequisite or select one registered available profile and start a fresh case. | Zero-API setup tests prove no Bundle for pre-admission failure, no provider call, and no rubric result. |

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave0 initial source intake | node-agent | From one scoped assignment and permitted retrieval, propose bounded source metadata, facts, and limitations in the closed final JSON shape. | Assignment constrains scope; retrieved/model material remains untrusted and cannot confer evidence or control authority. | Existing 1--3 retrieval request window, enforced by the runtime bridge policy. | Existing `Wave0WorkerOutput`; parser, source validation, submission validator, and controller decide admission. | Existing parser then at most one zero-tool repair; controller owns all later retry/exhaustion. | Real-bridge scripted worker test observes tool window, candidate handoff, Journal fact, and ledger non-admission on failure. |
| Wave0 structural repair | node-agent | Re-express only the bounded untrusted draft and retained observations as a valid closed JSON candidate. | Bounded assignment/category are trusted constraints; draft and observations remain untrusted. | Existing zero-tool request, enforced by the runtime bridge policy. | Existing `Wave0WorkerOutput` and deterministic validators. | Existing single repair attempt; no submission failure feedback or added retry. | Focused repair integration asserts exact request posture and separate parser facts. |
| Wave1 initial evidence extraction | node-agent | After one permitted retrieval, propose new baseline-aware sources, claims, and open questions in the closed final JSON shape. | Topic/baseline constrain scope and newness; retrieved/model material remains untrusted. | Existing exactly-one retrieval request window, enforced by the runtime bridge policy. | Existing `Wave1WorkerOutput`; parser, local semantic validator, submission validator, and controller decide admission. | Existing parser/local-semantic repair then controller retry/exhaustion. | Scripted real worker test and selected live Bundle calibration observe production bridge/parser/semantic handoff. |
| Wave1 structural repair | node-agent | Re-express the bounded draft and retained observations without promoting baseline material or inventing evidence. | Bounded topic/baseline/category are trusted constraints; draft and observations remain untrusted. | Existing zero-tool request, enforced by the runtime bridge policy. | Existing `Wave1WorkerOutput` and deterministic validators. | Existing one repair only; later submission failure remains controller-owned. | Focused repair integration asserts the retained-boundary and non-admission behavior. |
| Response-shape and post-candidate Journal facts | no-agent | Deterministic classification is sufficient; no model judgment is permitted or needed. | Only existing parser/subgraph/validator outputs may supply closed classifications. | No tool or model invocation. | The Journal is inspection-only; it admits no candidate and has no control consumer. | Existing recorder health behavior only; never a research recovery. | Journal model/recorder reload tests prove redaction, correlation, and no lifecycle effect. |
