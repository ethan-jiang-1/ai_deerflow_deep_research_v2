## 1. Admission and Red Evidence

- [x] 1.1 **Current apply agent plan-review obligation:** re-read `proposal.md` Change Focus, Control Placement Review, Node Agent Review, Workflow Outcome Review, this task list, the Wave1 capability/prompt/subgraph seam, both main specs, and the selected renderer/worker/evaluation tests before editing. Add every actionable finding as an unchecked ordinary task; confirm the two-resource boundary, deterministic-only corpus boundary, and no-`backend`/`frontend` scope remain accurate. (`WON-010`, `EVH-028`)
- [x] 1.2 Register `WON-010` and `EVH-028` with their main-spec owners and add red renderer/resource and prompt-projection regressions for extraction and repair.
- [x] 1.3 Extend `tests/graph/test_node_agent_capability_cohort.py`, `tests/graph/test_cognitive_program_evidence.py`, and the existing scripted real `tests/integration/test_wave1_work_units.py` seams for exact capability-method binding, baseline duplicate containment, parser/local-semantic repair, and post-candidate validation isolation.

## 2. Method Ownership

- [x] 2.1 Expand `wave1-evidence-extraction.md` with assignment, one permitted retrieval, baseline-newness, untrusted-data, claim/reference, uncertainty, self-check, closed-result, and authority-limit method; preserve metadata posture.
- [x] 2.2 Expand `wave1-evidence-extraction-repair.md` with same-assignment, untrusted draft/observation, baseline constraint, no-invention, self-check, closed-result, zero-tool, and authority-limit method.
- [x] 2.3 Narrow `prompts.py` to bounded assignment/output/category/untrusted projections without changing schema, floor, validator, repair placement, artifact, ledger, critic, controller, gate, retry, or route owners.
- [x] 2.4 Green: `UV_OFFLINE=1 uv run --extra operations python -m pytest tests/graph/test_node_agent_capability_cohort.py tests/integration/test_wave1_work_units.py -q` (`98 passed`).

## 3. Evaluation and Documentation

- [x] 3.1 Add the smallest `wave1_cognitive_program` typed fixture, control validation, and production-scenario adapter beside the existing HITL1/Wave0 cognitive-program owners. The closed corpus covers normal handoff, adversarial retrieval text, baseline duplicate containment, malformed parser repair, local-semantic repair, and post-candidate validation isolation; no SourceDiagnostic, ClaimVerifier, generic corpus abstraction, provider, or web call enters scope. (`EVH-028`)
- [x] 3.2 Add versioned Wave1 case, contract, rubric, and registry assets. Bind the two capability digests and worker schema digest; prove the deterministic corpus is rejected by selected-live admission before runs-root, manifest, review, subject, provider, or release-evidence creation. (`EVH-028`)
- [x] 3.3 Update the existing Wave1 reader and Cognitive Evaluation documentation with method/data/tool/admission/evidence boundaries; do not create a parallel lifecycle guide.

## 4. Verification and Closeout

- [x] 4.1 Green: `UV_OFFLINE=1 make format`, `make lint`, `make test-assets`, `make test-req-coverage`, focused Wave1/cognitive-evaluation tests (`187 passed`), and `UV_OFFLINE=1 make verify` all passed; no implementation-owned warning was emitted.
- [x] 4.2 Green: strict OpenSpec, Agent Charter, `git diff --check`, and `git diff HEAD --check` passed. `git status --porcelain=v1 --untracked-files=all -- backend frontend` and `git diff --name-only HEAD -- backend frontend` are empty. No live provider call ran.
- [x] 4.3 **Archive-closeout review:** re-read the proposal's Control Placement, Node Agent, and Workflow Outcome reviews, final diff, deterministic/limited evidence, unresolved-task set, and Git-verified boundary. No new actionable finding remains: no capability gains tool, admission, critic, retry, gate, route, or source-quality authority, and the corpus remains selected-live-ineligible. (`WON-010`, `EVH-028`)
