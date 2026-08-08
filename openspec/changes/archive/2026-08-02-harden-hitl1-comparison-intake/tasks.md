## 1. Red Deterministic Evidence

- [x] 1.1 Add red profile-contract tests in `tests/domain/test_profile.py` for v2 comparison-pair normalization/cardinality/distinctness, comparison-required completeness, supported request-language detection, output-language validation, bounded pair parsing, canonical bytes/hash ordering, and v1 legacy decode without inferred facts.
- [x] 1.2 Add red state/lifecycle/run-experience/session-operation tests for v1 checkpoint defaults, exact HITL1 language options, option-id/request-id rejection, local and retained current-option submission, and unchanged HITL2/text/action compatibility.
- [x] 1.3 Add red HITL1 node tests for generic comparison suspension without acceptance, source-explicit pair progress, Chinese presentation, unsupported-language choice, final-round missing-pair block, non-interactive generic-comparison/unsupported-language block, and request/proposal correlation.
- [x] 1.4 Add red HITL1 semantic-path tests proving each documented clear Chinese/English confirmation uses zero semantic bridge calls, while a modifying or ambiguous reply still invokes the bounded semantic path.
- [x] 1.5 Add red persistence and planner-prompt tests proving `request/profile.json`, checkpoint fields, reload behavior, and both planner prompt variants retain the exact pair and accepted language without request-text inference.

## 2. Typed Profile And Checkpoint Contracts

- [x] 2.1 Implement profile schema v2, `ComparisonSubjects`, language enums, local comparison/language seed, bounded subject/input parsing, exact confirmation normalizer, and a v1 retained-profile reader in `domain/profile.py`.
- [x] 2.2 Extend `StructuredBrief`, partial/final profile validation, merge/finalize, canonical serialization/hash, and `profile_state_fields()` so required comparison/language facts have one authoritative representation.
- [x] 2.3 Add bounded controller-owned comparison/language checkpoint fields, defaults, validators, writer ownership, and no-schema-version-bump compatibility in `domain/state.py` and applicable checkpoint contracts.
- [x] 2.4 Update `domain/human_interaction.py` so incomplete comparison/language intake has focused human-safe material and no current-proposal acceptance control, while complete subjects render the typed pair and language.

## 3. Correlated Language Option Transport

- [x] 3.1 Extend `domain/lifecycle.py` so HITL1 supports only the exact advertised `zh`/`en` `CHOICE` options and matching `OPTION` responses, without changing HITL2 choices or action authority.
- [x] 3.2 Extend `domain/run_experience.py` and `runtime/run_experience.py` to render and submit current HITL1 language options through `AnswerRun`, rejecting noncurrent/misadvertised options and leaving visible-control action binding unchanged.
- [x] 3.3 Extend `domain/session_operations.py` and `runtime/session_operations.py` to project and resume only a current retained HITL1 language option under the namespace lock, preserving existing text, action, and HITL2 option resumes.

## 4. HITL1 Admission And Presentation

- [x] 4.1 Merge the local intake seed into validated brief/profile progress in `graph/nodes/hitl1/node.py`; discard model-selected pairs/languages, persist accepted v2 facts, and prevent `accept_suggestion`/acceptance controls for incomplete profiles.
- [x] 4.2 Add the correlated language-choice branch and deterministic localized HITL1 prompt/interaction material, including bounded brief-summary language validation through the existing structural repair budget.
- [x] 4.3 Insert exact local clear-confirmation recognition after response correlation and before `_classify_proposal_reply()`, sharing the existing `accept_suggestion` materialization path with zero bridge calls.
- [x] 4.4 Keep nonmatching revisions, questions, and ambiguity on the existing zero-tool semantic candidate/resolution path; require a typed changed pair/language revision to render as a new proposal version before later acceptance.
- [x] 4.5 Preserve existing bounded intake semantics for degradable fields, but block after the final accepted-answer round when a required comparison pair or output language remains missing; never create a degraded default.
- [x] 4.6 Apply the same typed admission gate before `non_interactive_policy.auto_profile` writes a degraded profile: retain locally explicit pair/language facts, and block without an artifact when a required pair or human language choice is missing.

## 5. Downstream Profile Consumption

- [x] 5.1 Extend HITL1 prompt helpers and presentation payloads only with typed profile facts required for deterministic Chinese/English interaction; do not add a duplicate fact owner.
- [x] 5.2 Extend `PlannerInputs`, state extraction, initial planner payload, and repair payload in `graph/nodes/topic_planning/prompts.py` with exact comparison/language fields and constraints; do not read `profile.json` or re-infer from prose.
- [x] 5.3 Update focused graph/integration fixtures and assertions so the accepted comparison pair and language survive request-bundle write/reload and only the legal accepted route enters topic planning.

## 6. Verification And Archive Evidence

- [x] 6.1 Run the narrowest profile, lifecycle/run-experience, session-operation, HITL1, and prompt tests while completing each red-green slice; record selectors and results in this task file before archive.
- [x] 6.2 Run `cd deerflow_research && make test-intake` and `uv run --extra operations python -m pytest tests/graph/test_topic_planning_prompts.py tests/graph/test_topic_planning_node.py tests/integration/test_topic_planning_lifecycle.py -q` after the focused suites pass.
- [x] 6.3 Run `openspec validate harden-hitl1-comparison-intake --strict`, the architecture/evidence checks required by the repository, `cd deerflow_research && UV_OFFLINE=1 make verify`, and `git diff HEAD --check`; record actual commands, results, and `git status --porcelain=v1 --untracked-files=all` here before archive.
- [ ] 6.4 When credentials are healthy, run the supplemental stateful demo replay: Chinese generic comparison suspension, explicit pair entry, clear Chinese confirmation with zero semantic classification, then topic planning/provider outcome inspection. Record it separately from deterministic acceptance evidence.

## Verification Evidence

- `uv run --extra operations python -m pytest tests/domain/test_human_interaction.py tests/graph/test_hitl1_prompts.py tests/graph/test_hitl1_node.py -q` - `69 passed`.
- `uv run --extra operations python -m pytest tests/unit/test_state_contracts.py tests/unit/test_human_input_runtime.py tests/contract/test_run_experience_contract.py tests/contract/test_session_operations_broker.py tests/unit/test_request_bundle.py tests/graph/test_topic_planning_prompts.py -q` - `110 passed`.
- `uv run --extra operations python -m pytest tests/graph/test_topic_planning_prompts.py tests/graph/test_topic_planning_node.py tests/integration/test_hitl1_lifecycle.py tests/integration/test_topic_planning_lifecycle.py -q` - `42 passed`.
- `cd deerflow_research && make test-intake` - `82 passed`.
- `cd deerflow_research && uv run --extra operations python -m pytest tests/graph/test_topic_planning_prompts.py tests/graph/test_topic_planning_node.py tests/integration/test_topic_planning_lifecycle.py -q` - `32 passed`.
- `openspec validate harden-hitl1-comparison-intake --strict` - `Change 'harden-hitl1-comparison-intake' is valid`.
- `cd deerflow_research && python3 ../openspec/governance/check_project_architecture.py ..` - passed.
- `cd deerflow_research && make test-assets` - passed: 13 incidents, 11 real nodes, 7 critical faults, 8 model-workflow nodes, 347 central claims, and 2455 deterministic tests.
- `cd deerflow_research && make test-req-coverage` - passed.
- `cd deerflow_research && UV_OFFLINE=1 make verify` - passed: governance, lock, Ruff, test-asset, requirement-coverage, fast, integration, and workflow gates.
- `git diff HEAD --check` - passed.
- `cd deerflow_research && env -u VIRTUAL_ENV uv run --extra operations --extra demo-real python scripts/live_preflight.py --require-web` - passed: `model=deepseek, web=tavily`.
- `cd deerflow_research && printf '' | make demo-real DEMO_ARGS='--question "比较两种储能路线的成本、风险与适用场景"'` - live run `r_fg1tCMkToonOn7sU--1NPU56kg_1OvJYE8HZb4nTlL4` suspended at HITL1. Its Chinese prompt requested the two specific routes and exposed no numbered acceptance/start control. EOF then produced the local demo adapter's expected exit `130`.
- `cd deerflow_research && printf '%s\n%s\n' '可以，我觉得你说的挺好' '1' | make demo-real DEMO_ARGS='--question "比较锂离子电池和全钒液流电池的成本、风险与适用场景"'` - live run `r_yDwIBC2UpKLLHBlXQh--7IMGbLIbe5JpCldYN3B0cxA` blocked at HITL1 before profile publication with `budget.exhausted` (`diag_CGHlT1N2-c1wKefa0QYpvVCo`). It therefore did not reach the required clear-confirmation or topic-planning observations; `6.4` remains incomplete.

`git status --porcelain=v1 --untracked-files=all` at final verification:

```text
 M _backlog/plans/real-demo-stabilization-bugfix-program.md
 M deerflow_research/src/deerflow_deep_research/domain/human_interaction.py
 M deerflow_research/src/deerflow_deep_research/domain/lifecycle.py
 M deerflow_research/src/deerflow_deep_research/domain/profile.py
 M deerflow_research/src/deerflow_deep_research/domain/run_experience.py
 M deerflow_research/src/deerflow_deep_research/domain/session_operations.py
 M deerflow_research/src/deerflow_deep_research/domain/state.py
 M deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/node.py
 M deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/prompts.py
 M deerflow_research/src/deerflow_deep_research/graph/nodes/topic_planning/prompts.py
 M deerflow_research/src/deerflow_deep_research/runtime/human_input.py
 M deerflow_research/src/deerflow_deep_research/runtime/run_experience.py
 M deerflow_research/src/deerflow_deep_research/runtime/session_operations.py
 M deerflow_research/tests/contract/test_run_experience_contract.py
 M deerflow_research/tests/contract/test_session_operations_broker.py
 M deerflow_research/tests/domain/test_human_interaction.py
 M deerflow_research/tests/domain/test_profile.py
 M deerflow_research/tests/graph/test_hitl1_node.py
 M deerflow_research/tests/graph/test_hitl1_prompts.py
 M deerflow_research/tests/graph/test_topic_planning_prompts.py
 M deerflow_research/tests/integration/test_hitl1_lifecycle.py
 M deerflow_research/tests/integration/test_topic_planning_lifecycle.py
 M deerflow_research/tests/unit/test_human_input_runtime.py
 M deerflow_research/tests/unit/test_request_bundle.py
 M deerflow_research/tests/unit/test_state_contracts.py
?? openspec/changes/harden-hitl1-comparison-intake/.openspec.yaml
?? openspec/changes/harden-hitl1-comparison-intake/design.md
?? openspec/changes/harden-hitl1-comparison-intake/proposal.md
?? openspec/changes/harden-hitl1-comparison-intake/specs/hitl1-node/spec.md
?? openspec/changes/harden-hitl1-comparison-intake/specs/human-interaction-contract/spec.md
?? openspec/changes/harden-hitl1-comparison-intake/specs/research-graph-lifecycle/spec.md
?? openspec/changes/harden-hitl1-comparison-intake/specs/research-run-experience/spec.md
?? openspec/changes/harden-hitl1-comparison-intake/specs/research-session-discovery-and-operations/spec.md
?? openspec/changes/harden-hitl1-comparison-intake/specs/runtime-operations/spec.md
?? openspec/changes/harden-hitl1-comparison-intake/specs/topic-planning-node/spec.md
?? openspec/changes/harden-hitl1-comparison-intake/tasks.md
```
