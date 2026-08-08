## Why

Wave0 already loads two local capability resources, but the reusable source-intake and
repair method still lives mainly in Python prompt builders. That leaves the production
agent with short policy supplements and makes a cognitive change look like ordinary
string/control-flow maintenance instead of a versioned agent workflow.

## What Changes

- Make the runtime-loaded Wave0 initial source-intake and pre-candidate repair
  capabilities the canonical bounded cognitive methods for their respective tasks.
- Narrow their Python prompt projections to trusted assignment, closed output contract,
  validation category, and delimited untrusted draft/retrieval observations.
- Add a versioned, deterministic Wave0 cognitive-program corpus and production-path
  regressions for normal retrieval handoff, adversarial source content, shortfall,
  malformed-output repair, and post-candidate validation isolation.
- Extend the closed evaluation-case contract only as needed to validate that Wave0
  corpus; it remains deterministic-only and is not a selected-live case.
- Preserve the existing runtime tool policy, parser, artifact writer, submit validator,
  ledger, work-unit controller, gate, retry, and graph-route ownership.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave0/`; its worker and repair prompt builders presently own the reusable cognitive method while its subgraph orchestrates the deterministic handoff.
- **Question:** Can the two production-loaded Wave0 Markdown resources become the sole method owner for permitted source intake and one structural repair without granting source admission, recovery, or graph control?
- **Necessary adjacent/external contracts:** `agents/phase_prompt.py` answers whether the exact declared resource is loaded; `runtime/node_agent_bridge.py` answers which configured tools/budget are enforced; `domain.work_units` and the work-unit component answer parser, artifact, submission, ledger, retry, and gate admission; `domain/evaluation.py` and `runtime/evaluation/` answer the closed Wave0 corpus fixture, digest verification, and production-scenario adapter. None becomes a new cognitive-method owner.
- **Evidence seam:** exact production renderer/resource and bounded prompt-projection tests; scripted real `RuntimeNodeAgentBridge` execution through the real Wave0 worker/controller; the existing adversarial worker/ledger/gate seam; repair and post-candidate submission-validation isolation; and a closed zero-API cognitive-program corpus.
- **Not in scope:** `WorkSpec`, `Wave0WorkerOutput`, result contracts, URL/content validation, artifact paths, ledger, source floor, retry budget, graph topology, topic registry, Wave1, synthesis, final delivery, public controller, `backend/`, and `frontend/`.
- **Triggered review policies:** node-agent-workflow-integrity, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Source-intake method | Worker proposes bounded source metadata and limitations from permitted retrieval observations | Existing `Wave0WorkerOutput` parser, artifact writer, submit validator, and ledger decide whether a candidate becomes a submission | advisory | A candidate cannot create content refs, accepted coverage, ledger records, retry, or route | Remove the parallel Python-owned method while retaining the existing admission chain | Production renderer/resource regression plus scripted real bridge/worker/controller handoff |
| Structural repair eligibility | Repair proposes one corrected candidate from the initial draft and retained observations | Wave0 subgraph invokes repair only after the initial parser failure; parser rechecks the repaired result | bounded-repair | One repair has no tool; post-candidate submission validation never returns to repair | Reuse the existing one-repair branch; avoid a second validation/recovery controller | Scripted malformed initial/repaired candidate and post-candidate validation rejection tests |
| Tool posture and untrusted source material | Worker may use only the existing retrieval capability to reason about untrusted material | Runtime bridge and `ExecutionPolicy` enforce configured tool subset, roots, budget, cancellation, and safe failure | non-bypassable | Capability text cannot expand tools, paths, tool-call bound, or turn untrusted content into instruction authority | Keep tool policy outside Markdown and avoid capability-selected execution | Renderer posture assertion and scripted adversarial-source/no-permitted-tool paths |
| Evaluation evidence layer | No Wave0 corpus candidate or reviewer selects live-quality evidence | Existing selected-live admission and immutable manifest/review derivation own evidence-layer eligibility | non-bypassable | The deterministic-only corpus is rejected before execution when selected live and cannot create a live manifest/review | Reuse the existing selected-live allowlist and evidence-layer derivation; avoid a second live runner | Selected-live rejection before runs-root test and deterministic corpus review test |

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave0 source-intake worker | node-agent | Given one trusted topic assignment, which independently useful source metadata candidates and honest limitations follow from permitted retrieval? | Topic projection is trusted scope; retrieved pages, snippets, tool observations, and model output remain untrusted data | Required retrieval posture; runtime bridge and `ExecutionPolicy` enforce configured allowlist, roots, 1--3 calls, cancellation | `Wave0WorkerOutput`; parser, artifact writer, submit validator, and controller admit | Runtime normalizes tool/provider failure; controller owns existing retry/gate bound | Exact resource rendering, scripted real bridge/worker/controller, and existing adversarial worker/ledger/gate test |
| Wave0 pre-candidate repair | node-agent | Can the supplied untrusted initial draft and retained observations be reformatted into one closed candidate without inventing evidence? | Assignment and closed validation category are trusted constraints; draft/observations are untrusted | Forbidden; runtime bridge enforces zero model-visible tools | `Wave0WorkerOutput`; same parser/admission chain | Only one repair after initial parser failure; malformed repair becomes existing structured-output failure | Scripted initial-malformed/repair-success and repair-malformed tests |
| Source validation, ledger, gate, retry, and route | no-agent | Deterministic source evidence admission and lifecycle control require typed facts and persistent work-unit ownership | Candidate is untrusted until validation; ledger/gate facts are not model inputs | No agent surface | Existing validator/controller/gate remain sole owners | Existing typed rejection, retry, degraded coverage, and terminal behavior remain unchanged | Post-candidate validation isolation and controller/gate regression suite |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| No eligible tool, tool/provider failure, or cancellation | Existing runtime normalized invocation outcome and controller attempt record | Runtime enforces invocation boundary; existing work-unit controller applies its bounded retry/gate behavior | Existing failed/degraded/exhausted outcome; no submission is fabricated | Existing controller-selected retry, gate route, or terminal projection | Scripted invocation-failure real-worker test |
| Initial structured candidate malformed | Wave0 parser result | Wave0 subgraph invokes exactly one existing zero-tool repair | Existing structured-output failure if repair remains malformed | Existing controller retry/gate path | Scripted initial/repair failure test |
| Post-candidate submission validation failure | Existing submit validator typed result | Existing work-unit controller; no Wave0 repair | Existing validation failure and controller retry/gate path | Existing controller-selected retry, gate route, or terminal projection | Post-candidate validation rejection does not produce a repair request |
| Source shortfall or adversarial retrieval content | Candidate limitations and deterministic validation/source-floor facts | Existing validator/controller/gate only; capability can record no authority-bearing success | Existing degraded, repair, or exhausted outcome | Existing controller/gate legal route | Closed corpus plus controller/gate regression |
| Deterministic corpus selected as live | Selected-live allowlist admission | No execution/recovery; existing selected-live entrypoint rejects the unregistered case | No manifest/review/provider invocation or evidence layer is created | Caller must use the deterministic runner or explicitly selected existing live corpus | Selected-live rejection before runs-root test |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave0-node`: Wave0 runtime capabilities own the bounded source-intake/repair
  cognitive method while deterministic tool, source-admission, and lifecycle owners
  remain non-bypassable.
- `evaluation-hardening`: The control evaluator accepts and verifies the closed,
  deterministic-only Wave0 cognitive-program corpus without granting it live or
  release evidence status.

## Impact

- Affected code: Wave0 capability Markdown, `prompts.py`, scoped graph/evaluation
  tests, Wave0 control assets, and the minimum typed evaluation fixture/loader/subject
  extension under `deep_research_harness/`.
- Affected specifications: `openspec/specs/wave0-node/spec.md`,
  `openspec/specs/evaluation-hardening/spec.md`, and the requirement registry.
- No public API, persistent schema, external dependency, `backend/`, or `frontend/`
  change is proposed.
