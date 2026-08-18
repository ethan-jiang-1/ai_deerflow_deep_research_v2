# Wave2 Synthesis Validation-Feedback Contract Fidelity (BUG-040/041/043)

## Why

Two consecutive real mode-003 runs after the BUG-035/036/037 fix blocked at the same
place: wave2's first output mirror-fed wave1's claim-verdict shape (BUG-043), the
one repair could not recover because the repair prompt never carried the
open-question disposition contract (BUG-040), and the resulting blocked terminal
reported only the generic `output.structured_invalid` instead of the real
`..._question_coverage_invalid` category (BUG-041). All three are one causal theme:
**the wave2 validation→repair→terminal feedback loop drops or blurs exactly the
typed facts an operator or the model needs to make the coverage contract real.**

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/` — the node's prompt builders and its semantic-validation→repair→terminal loop own the feedback contract, the open-question disposition contract, and the terminal category projection.
- **Seam classification:** cognitive-program — two fixes touch the model-visible prompt/output contract (initial + repair) and the third fixes how the validation category is projected to the terminal; the deterministic validator, materializer, preview, and gate remain the admission and route owners. BUG-041's projection fix is a faithful-projection change over the existing typed category, not a new model decision.
- **Question:** When wave2 semantic validation fails (especially open-question coverage), how do the repair prompt and the bounded terminal carry the concrete contract and category — the full open-question disposition list plus the missing ids as trusted detail — instead of a terse category string or a generic `output.structured_invalid`, so the model can repair non-blindly and the operator can diagnose without checkpoint archaeology?
- **Necessary adjacent/external contracts:** `domain/run_experience.py` (`NodeProblem`, `TerminalIncidentProjection`): the typed detail field the bounded terminal needs to project the specific validation category (authority-and-projections question). `domain/synthesis.py` (`SynthesisResult`): the strict `extra_forbidden` shape and the `source_questions`/`resolved_questions` contract that parse/validate the candidate (fact-owner question). `agents/structured_output.py` / runtime bridge: the requested zero-tool posture and its runtime enforcer are unchanged (node-agent tool-posture question).
- **Evidence seam:** `tests/graph/test_wave2_synthesis_real.py` (prompt-objective assertions, repair-on-coverage-error, still-invalid-repair terminal incident, terminal category assertion), plus focused `prompts.py` unit assertions over the rendered initial and repair requests.
- **Not in scope:** no gate/verdict changes, no materializer/artifact changes, no graph routing changes, no provider/model/tool changes, no DeerFlow/src changes, no soft-bundle CLI changes (BUG-042 is its own change), no live-model or research quality claims. The real 003 run remains an operator runbook step.
- **Triggered review policies:** node-agent-workflow-integrity, workflow-outcome-review, authority-and-projections, change-admission

## What Changes

- **BUG-040 — repair prompt carries the open-question disposition contract and the
  concrete missing details.** `build_synthesis_repair_prompt` gains the same
  `open_question_pairs` (id+text) the initial prompt receives, and
  `_validate_synthesis_semantics` surfaces the specific failing fact (which projected
  question ids are missing from both `gap[].source_questions` and
  `resolved_questions`, or are duplicated/foreign) as trusted validation detail. The
  repair objective then names the complete open-question list and the concrete
  missing ids, so a coverage-class repair is non-blind.
- **BUG-041 — bounded terminal carries the specific validation category.** The
  second-validation failure path builds its `NodeProblem` with the real category
  (`synthesis_question_coverage_invalid` etc.) instead of pinning the generic
  `OUTPUT_STRUCTURED_INVALID`; `NodeProblem` and `TerminalIncidentProjection` gain an
  optional bounded `validation_category` field (a category string, not the id
  detail). The projection consumers follow:
  `runtime/run_experience.py`'s `_publish_observation` projects
  `failure_category = incident.validation_category or incident.code.value` into the
  journal event and `run-summary.json` (so `soft-bundle inspect` shows the concrete
  category), and `_failure_for_terminal` threads the category into the terminal
  `RunFailure`, which `scripts/demo_real.py`'s generic `_failure_lines`
  (the non-provider branch that already renders `worker_failure_category`) renders
  as one extra detail line. The provider-only
  `_terminal_failure_presentation.py` path is not involved (a wave2
  `OUTPUT_STRUCTURED_INVALID` failure has no provider fields). The generic
  `output.structured_invalid` code remains for pure parse failures.
- **BUG-043 — initial prompt output contract gains a concrete example and an explicit
  negative contrast.** `_expected_synthesis_output()` adds one minimal example object
  of the required findings/relations/gaps shape and an explicit "return
  findings/relations/gaps, NOT a wave1 claims-verdict list (`claims[]` with
  `claim_id/verdict/...`)" contrast, so the evidence shape's mirror pressure no longer
  dominates.

No product defaults change; the same open-question contract is re-used by both
prompt paths, and parse-category failures keep today's generic code.

## Node Agent Review

| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wave2 initial synthesis | node-agent | Which findings/relations/gaps honestly summarize the accepted evidence and dispose every projected Wave1 open question exactly once. | Trusted assignment/output contract (topics, accepted refs, open_question id+text pairs, expected output with example + negative contrast); evidence and any draft stay delimited untrusted data. | Forbidden; the existing zero-tool capability request is carried through the unchanged runtime bridge. Tool grant, permission, and tool resolution remain runtime-owned. | `SynthesisResult`; parser, semantic validator, materializer, preview, and gate own admission, publication, and routing. | Wave2 node owns its one existing structured repair bound and the exhausted terminal. | `tests/graph/test_wave2_synthesis_real.py` prompt-objective + repair/reject fixtures |
| Wave2 structured repair | node-agent | How can the invalid draft be structurally repaired (esp. coverage) without adding evidence, routes, or gate authority. | Same trusted open-question disposition contract + concrete missing-id detail; draft and evidence remain delimited untrusted data. Cannot grant evidence, route, retry, or admission. | Forbidden; zero-tool repair request through the unchanged bridge. | `SynthesisResult`; same deterministic validator/materializer/gate owner path. | Wave2 node; one repair bound, then bounded exhausted terminal with the real category. | `tests/graph/test_wave2_synthesis_real.py` coverage-repair + still-invalid-terminal fixtures |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Wave2 initial candidate fails parser (JSON/extra-forbidden) | `parse_synthesis_output` | Wave2 node; its existing one zero-tool repair | Non-publication + one repair; still invalid → exhausted with the parse category (`output.structured_invalid`) | Operator inspects the typed terminal incident / diagnostic | `test_real_synthesis_repairs_malformed_output_once_without_tools`, `test_real_synthesis_malformed_output_fails_without_artifact` |
| Wave2 candidate fails semantic validation, incl. question coverage | `_validate_synthesis_semantics` (typed category + id detail) | Wave2 node; one zero-tool repair now carrying the full open-question contract + concrete missing ids | Non-publication + one repair; still invalid → exhausted carrying the real semantic category via new `validation_category` | Operator sees `synthesis_question_coverage_invalid` (etc.) in incident/diagnostic instead of generic code | new coverage-repair + terminal-category fixtures in `test_wave2_synthesis_real.py` |
| Repair provider/invocation failure | runtime invocation boundary | existing `invoke_and_normalize` dispositions | exhausted with the safe provider/incident category (unchanged) | existing terminal handling | existing provider-failure tests retained |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `wave2-synthesis-node`: the initial AND repair prompt contract carry the
  open-question disposition contract plus a concrete example/negative-contrast output
  shape; a coverage/findings semantic failure enters one bounded repair that receives
  the concrete missing-id detail; a still-invalid repaired candidate reaches the
  bounded exhausted terminal carrying the specific validation category
  (`validation_category`) instead of only the generic structured-invalid code.

## Impact

- Code: `graph/nodes/wave2_synthesis/prompts.py` (initial + repair builders,
  expected-output contract), `graph/nodes/wave2_synthesis/node.py`
  (`_synthesis_validation_category`, second-validation `except` path, repair-prompt
  wiring, `SynthesisValidationFailure` carrier), `domain/run_experience.py`
  (`NodeProblem`/`TerminalIncidentProjection` bounded `validation_category` field
  and `RunFailure` optional `validation_category`), `runtime/run_experience.py`
  (`_publish_observation` + `_failure_for_terminal` projection consumers),
  `scripts/demo_real.py` (generic `_failure_lines` detail line).
- Tests: `tests/graph/test_wave2_synthesis_real.py` — extend prompt-objective tests,
  add coverage-repair non-blindness test, add still-invalid-terminal category test;
  all deterministic, offline, no network/API keys; `make verify` stays offline-green.
- Docs: BUG-040/041/043 cards move to `_done/_fixed_bugs/` on completion.
- No changes to `deerflow/` or public DeerFlow interfaces; ordinary downstream work
  neither modifies nor source-browses the `deerflow/` gitlink.