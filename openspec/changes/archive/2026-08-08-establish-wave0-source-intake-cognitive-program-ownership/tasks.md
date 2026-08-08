## 1. Admission and Requirement Traceability

- [x] 1.1 **Current apply agent plan-review obligation:** re-read `proposal.md` Change Focus, Control Placement Review, Node Agent Review, Workflow Outcome Review, this task list, the Wave0 capability/prompt/subgraph seam, the `wave0-node` main spec, and the selected renderer/real-worker/evaluation tests before editing. Add every actionable finding as an unchecked ordinary task; confirm the two-resource/one-worker boundary and no-`backend`/`frontend` scope remain accurate. (`WAN-009`)
- [x] 1.2 Added `WAN-009` and `EVH-027` to `openspec/governance/req-registry.yaml` and their main-spec owner headers. Red coverage initially reported both identifiers uncovered; green `UV_OFFLINE=1 make test-req-coverage` passes after the Wave0/evaluation implementation and test owners were added.

## 2. Red Deterministic Handoff Regressions

- [x] 2.1 Added production renderer/resource regressions for initial worker and repair. The final system policy contains the exact activated capability body and its required/forbidden posture, while reader-only Wave0 workflow prose remains absent. (`WAN-009`)
- [x] 2.2 Added Wave0 prompt-builder ownership regressions. Worker and repair objectives now carry bounded assignment, closed category, output contract, and delimited untrusted data only; schemas, limits, capability selection, parser, and recovery remain deterministic owners. (`WAN-009`)
- [x] 2.3 Retained the existing scripted real bridge/worker/ledger/gate adversarial-source and retrieval-shortfall seams, and bound their missing untrusted-data/shortfall assertion to the exact Wave0 production resource. Repair remains pre-parser and zero-tool; post-candidate validation does not enter repair. (`WAN-009`)

## 3. Runtime Cognitive-Method Ownership

- [x] 3.1 Expanded `wave0-authoritative-source-intake.md` into the bounded initial method: assignment interpretation, available-permitted retrieval, untrusted-data discipline, independent candidate selection, honest shortfall, self-check, closed response, and authority limits. Existing metadata and required-tool binding remain compatible.
- [x] 3.2 Expanded `wave0-source-intake-repair.md` into the bounded one-repair method: same assignment, untrusted draft/observation handling, no evidence invention, self-check, closed response, zero-tool posture, and authority limits.
- [x] 3.3 Reduced `graph/nodes/wave0/prompts.py` to invocation-specific assignment/category/output/untrusted-data projections. `WorkSpec`, typed parser/schema validation, 1--3 runtime call bound, repair placement, artifact writer, submit validator, controller, gate, and routes are unchanged.
- [x] 3.4 Green: `UV_OFFLINE=1 uv run --extra operations python -m pytest tests/graph/test_node_agent_capability_cohort.py tests/graph/test_wave0_worker.py tests/integration/test_wave0_work_units.py tests/integration/test_adversarial_worker_path.py -q` (`128 passed`).

## 4. Versioned Wave0 Cognitive Evidence

- [x] 4.1 Added typed `wave0_cognitive_program` evaluator contract/loader support for exactly five case kinds and the `source_intake_capability_digest`, `source_intake_repair_capability_digest`, and `worker_schema_digest` controls. Scenario/capability/control/rubric identity remains closed; mutation tests reject missing or duplicate data. (`EVH-027`)
- [x] 4.2 Added `wave0-cognitive-program-v1` beside `wave0-worker-v1` with closed normal retrieval, adversarial observation, shortfall, malformed-initial/one-repair, and post-candidate validation-isolation scenarios. The corpus binds the two capability ids, assignment fragments, forbidden effects, and rubric criteria; existing real runtime bridge/worker/controller integrations remain its production boundary proof, while the corpus itself requires neither provider nor web API. (`WAN-009`, `EVH-027`)
- [x] 4.3 Green: `UV_OFFLINE=1 uv run --extra operations python -m pytest tests/eval/test_cognitive_evaluation_suite.py -q` (`38 passed`). The closed corpus runs and records only a `deterministic_handoff` review. It remains absent from the selected-live allowlist; selected-live admission fails before runs-root, manifest, review, subject/provider invocation, or release claim. Live source-quality evidence is recorded as not collected/limited. (`WAN-009`, `EVH-027`)

## 5. Reader and Evaluation Documentation

- [x] 5.1 Updated the existing Wave0 workflow reader and Cognitive Evaluation Suite documentation to distinguish runtime-loaded method, bounded assignment/output data, runtime tool enforcement, deterministic source admission, and the boundary between deterministic handoff and credentialed live-quality evidence. No competing lifecycle or source-admission guide was added.
- [x] 5.2 Green: `UV_OFFLINE=1 make format`, `make lint`, `make test-assets`, and `make test-req-coverage` passed. The focused Wave0/resource lane passed `128` tests and the evaluator lane passed `38`; no implementation-owned warning was emitted.

## 6. Whole-Change Verification and Closeout

- [x] 6.0 Repaired the `Node Agent Review` Markdown separator row; `check_agent_charter.py` and the full verification gate pass its declared `node-agent-workflow-integrity` review shape.
- [x] 6.0a Repaired the `Control Placement Review` Markdown separator row; `check_agent_charter.py` and the full verification gate pass its declared `control-placement` review shape.
- [x] 6.1 Green: `cd deep_research_harness && UV_OFFLINE=1 make verify`, root `openspec validate establish-wave0-source-intake-cognitive-program-ownership --strict`, `git diff HEAD --check`, and `git diff --check` passed. Git status records the active change, its scoped implementation, and the pre-existing progressive-plan edit; `git diff --name-only HEAD -- backend frontend` and `git status --porcelain=v1 --untracked-files=all -- backend frontend` are empty. No live provider command ran.
- [x] 6.2 **Archive-closeout review:** re-read the proposal's Control Placement, Node Agent, and Workflow Outcome reviews, final diff, deterministic/limited evidence, unresolved-task set, and Git-verified boundary. The only actionable findings were the two proposal table separator repairs recorded as 6.0 and 6.0a. No capability method selects tools or paths, admits evidence, duplicates source validation/retry control, or overclaims source quality. The deterministic corpus remains selected-live-ineligible and live quality remains not collected/limited. (`WAN-009`)
