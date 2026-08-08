## Why

Wave1 already loads extraction and repair capabilities, but the reusable method for
one-search evidence expansion, baseline newness, claim binding, uncertainty, and repair
still lives mainly in `prompts.py`. This repeats the owner split removed in Wave0 and
makes a cognitive workflow look like ordinary string maintenance.

## What Changes

- Make the two runtime-loaded Wave1 extraction/repair resources the sole reusable
  cognitive-method owners for their bounded tasks.
- Reduce Python prompts to trusted assignment/output/category and delimited untrusted
  draft/retrieval projections, without changing deterministic validation or recovery.
- Add deterministic renderer, prompt, real bridge/worker, and ownership-boundary
  regressions plus one closed, zero-API Wave1 cognitive-program corpus. The corpus
  proves only method-to-runtime handoff and authority boundaries, never source or
  model quality.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave1/`; its initial and repair prompt builders currently duplicate the bounded evidence-extraction method while the subgraph owns the existing deterministic handoff.
- **Question:** Can the two production-loaded Wave1 Markdown resources become the sole method owner for baseline-aware evidence extraction and one structural repair without granting source/claim admission, critic, recovery, gate, or graph control?
- **Necessary adjacent/external contracts:** `agents/phase_prompt.py` answers whether the exact resource is rendered; `runtime/node_agent_bridge.py` answers configured one-tool/zero-tool enforcement; `domain.wave1`, validation, artifact writer, submit validator, ledger, controller, and gate answer candidate admission and lifecycle; `domain/evaluation.py` and `runtime/evaluation/` own a closed, typed Wave1 control corpus and its deterministic production-scenario adapter. None becomes a cognitive-method owner.
- **Evidence seam:** exact renderer/resource and bounded prompt tests; existing scripted real Wave1 bridge/worker/validator/ledger tests for baseline duplicates and repair; post-candidate validation isolation; and a closed versioned control corpus using scripted adapters. No provider or web API is required.
- **Not in scope:** `Wave1WorkerOutput`, two-new-URL floor, baseline/newness validation, claim/reference validation, artifact/ledger layout, controller/gate/retry, SourceDiagnostic, ClaimVerifier, Wave2, targeted evidence, public controller, `backend/`, and `frontend/`.
- **Triggered review policies:** node-agent-workflow-integrity, workflow-outcome-review, control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Evidence extraction method | Worker proposes bounded new-source, claim, and open-question candidates from one permitted retrieval | Existing parser/local validation, artifact writer, submit validator, ledger, controller, and gate decide admission | advisory | Baseline URLs cannot become new coverage; candidate cannot write evidence or route | Remove parallel Python method without changing validation | Renderer plus real scripted worker/validator/ledger path |
| Structural repair | Repair reformats one untrusted initial draft after parser or local semantic failure | Existing subgraph selects one category and revalidates the repaired candidate | bounded-repair | Zero-tool repair cannot invent sources, claims, refs, or questions; later validation does not repair | Reuse one existing repair branch | Parser/semantic repair and validation-isolation tests |
| Tool posture and untrusted retrieval | Worker reasons over permitted retrieval observations | Runtime bridge and ExecutionPolicy enforce one configured call, roots, budget, cancellation | non-bypassable | Capability cannot widen tools/paths or change baseline/newness authority | Keep operator policy outside Markdown | Renderer posture and scripted bridge test |
| Critic and lifecycle boundaries | No extraction capability selects critics, evidence admission, retry, gate, or route | Existing accepted-result review materializer and controller/gate own those facts | non-bypassable | Candidate output cannot invoke critics or create State/ledger truth | Do not pull critic workflows into this slice | Existing accepted-work and post-validation tests |
| Evaluation evidence layer | No corpus scenario or reviewer selects source-quality or live-evidence status | Existing evaluation control registry, typed fixture, and selected-live admission own corpus identity and eligibility | non-bypassable | The corpus remains deterministic-only and cannot create a live manifest/review | Reuse the existing cognitive-program runner; add only Wave1's typed scenario/adapter boundary | Deterministic corpus and selected-live rejection tests |

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave1 evidence extraction | node-agent | Given trusted topic/baseline scope, which bounded new-source, claim, and uncertainty candidates follow from one permitted retrieval? | Topic/baseline are trusted constraints; retrieval/model material is untrusted | Required one-call posture; bridge/ExecutionPolicy enforce it | `Wave1WorkerOutput`; parser/local validation/writer/validator/controller | Existing normalized failure and bounded controller path | Renderer and scripted real worker path |
| Wave1 pre-persistence repair | node-agent | Can one untrusted draft be reformatted from retained observations without inventing evidence? | Assignment/category trusted; draft/observations untrusted | Forbidden; bridge enforces zero tools | Same typed candidate and admission chain | One repair only after parser or semantic failure | Existing repair tests |
| Validation, critics, ledger, gate, route | no-agent | Typed provenance/admission/review/lifecycle facts need deterministic owners | Candidate remains untrusted until admitted | No agent invocation | Existing validator/materializer/controller/gate | Existing typed recovery | Validation and critic-boundary suites |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Tool/provider/cancellation failure | Runtime normalized outcome | Existing controller retry/gate bound | Existing failed/degraded/exhausted result | Existing controller path | Scripted bridge failure test |
| Parse or local semantic failure | Parser/local validator | One existing zero-tool repair | Structured-output failure if still invalid | Existing controller route | Malformed and baseline-duplicate repair tests |
| Post-candidate submission validation failure | Submit validator | Controller only; no repair | Existing validation failure | Existing retry/gate route | No-repair-after-validation test |
| Deterministic corpus selected as live | Selected-live allowlist admission | No execution or recovery; the existing entrypoint rejects the unregistered case | No manifest, review, provider call, or live-evidence layer | Use the deterministic runner only | Selected-live rejection before runs-root test |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave1-node`: runtime-loaded extraction/repair capabilities own bounded cognition while deterministic admission and lifecycle owners remain non-bypassable.
- `evaluation-hardening`: the evaluation harness accepts and verifies the closed,
  deterministic-only Wave1 cognitive-program corpus without granting it selected-live
  or release-evidence status.

## Impact

Affected code is confined to Wave1 capability Markdown, `prompts.py`, scoped tests,
and the smallest typed evaluation contract/adapter/control assets needed to execute the
closed corpus. No public API, production work schema, provider dependency, `backend/`,
or `frontend/` change is proposed.
