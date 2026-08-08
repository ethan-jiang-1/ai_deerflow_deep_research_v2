## 1. Change Admission

- [x] 1.1 Create the proposal, design, node-agent-reader-interface delta, and task
  plan with the five-node focus, authority boundary, and exclusions.

## 2. Node-Local Reader Interfaces

- [x] 2.1 Recheck HITL1 source/spec/test ownership; add its source worksheet and
  package-local `workflow.md`, then run its human-interaction reader task.
- [x] 2.2 Recheck topic-planning source/spec/test ownership; add its source
  worksheet and package-local `workflow.md`, then run its planner-repair reader task.
- [x] 2.3 Recheck Wave0 source/spec/test ownership; add its source worksheet and
  package-local `workflow.md`, then run its work-unit admission reader task.
- [x] 2.4 Recheck Wave1 source/spec/test ownership; add its source worksheet and
  package-local `workflow.md`, then run its baseline/repair reader task. Its done
  condition identifies `node.py::build_real` as the top-level baseline-loading
  owner, treats the injected `_wave1_worker` duplicate test as non-top-level proof,
  and labels the missing baseline load and completion-only gate as implemented
  limitations without proposing a runtime fix.
- [x] 2.5 Recheck targeted-evidence source/spec/test ownership; add its source
  worksheet and package-local `workflow.md`, then run its worker/critic/return-edge
  reader task.
- [x] 2.6 Review the five projections together: retain only node-specific facts that
  change a maintenance decision, label unresolved facts as implemented limitations,
  and confirm no runtime-rendered capability body changed.

## Reader Task Records

- 2026-07-29: Given only `hitl1/workflow.md` and a natural reply whose semantic
  candidate and repair are both invalid, the review reached
  `node.py::_classify_proposal_reply`,
  `prompts.py::build_semantic_intake_prompt`, and
  `test_semantic_invalid_output_repairs_once_then_preserves_proposal`. It retained
  the checkpointed proposal with non-terminal feedback and rejected direct profile
  publication, brief-prompt edits, and graph-edge edits as first changes.
- 2026-07-29: Given only `topic_planning/workflow.md` and a confirmed-profile plan
  whose initial and repair candidates leave one must-answer question uncovered, the
  review reached `node.py::_generate_plan`, `prompts.py::build_planner_prompt`,
  `domain/topics.py::materialize_topic_plan`, and
  `test_uncovered_question_is_repaired_then_exhausts`. It selected bounded
  exhaustion without topic state and rejected direct profile, model-id, and graph
  edits as first changes.
- 2026-07-29: Given only `wave0/workflow.md` and a retrieval-backed worker whose
  draft and zero-tool repair are malformed, the review reached
  `subgraph.py::run_wave0_work_units_real`,
  `prompts.py::build_wave0_repair_prompt`, and
  `test_real_wave0_malformed_repair_fails_without_artifact_admission`. It selected
  the classified worker/controller boundary and rejected direct ledger, source, and
  graph-route edits as first changes.
- 2026-07-29: Given only `wave1/workflow.md` and a Wave0-baseline URL treated as
  new in a top-level real Wave1 run, the review reached `node.py::build_real` for
  baseline loading, `subgraph.py::_wave1_worker` for caller-supplied classification,
  and `test_real_wave1_baseline_duplicate_is_not_admitted_as_new_coverage` as a
  direct-subgraph proof only. It recorded the missing top-level load and
  completion-only gate as implemented limitations, rejecting prompt, ledger, and
  graph-edge edits as first changes.
- 2026-07-29: Given only `targeted_evidence/workflow.md` and a valid same-gap
  candidate whose `route="next"` is thought to require a different return target,
  the review reached `subgraph.py::run_gap_workers`, the shared admission boundary,
  and `graph/builder.py::build_research_graph`. It selected
  `test_gap_worker_crosses_real_resolver_artifact_validator_and_ledger` as the
  worker/admission proof seam, identified the builder's unconditional Wave2 return
  edge, and rejected direct route-field, critic-prompt, and ledger edits as first
  changes.

## 3. Evidence And Verification

- [x] 3.1 Run the cited lowest-responsibility deterministic test modules for the
  five projections and record their result. For Wave1, run the direct worker/
  baseline tests separately from any top-level node evidence, and record that the
  former does not verify baseline loading.

  2026-07-29: `test_hitl1_node.py` plus `test_topic_planning_node.py` passed 42;
  Wave0 worker/gate/validation/work-unit modules passed 50; Wave1 work-unit,
  targeted-evidence, and topology modules passed 47. The Wave1 baseline-duplicate
  case remains direct-subgraph evidence only; this change adds no top-level baseline
  behavior claim.
- [x] 3.2 Run `openspec validate roll-out-node-reader-interfaces --strict`,
  `python3 openspec/governance/check_project_reqs.py`,
  `python3 openspec/governance/check_project_specs.py`,
  `python3 openspec/governance/check_project_architecture.py`,
  `python3 openspec/governance/check_agent_charter.py`, and `git diff HEAD --check`.
  Record `git status --porcelain=v1 --untracked-files=all` and confirm no changes
  under `backend/` or `frontend/`.

  2026-07-29: strict OpenSpec validation and all four project governance checks
  passed. `git diff --check` and `git diff HEAD --check` passed; status contained
  only this documentation rollout and its progressive-plan records, with no
  `backend/` or `frontend/` paths.
- [x] 3.3 Run `cd agent && UV_OFFLINE=1 make verify`; record any baseline failures
  or skips separately and confirm `backend/` and `frontend/` remain clean.

  2026-07-29: `UV_OFFLINE=1 make verify` completed successfully, including
  governance, lock, ruff, test-asset and requirement-coverage checks, and the
  deterministic fast/integration/workflow lanes. No baseline failures were observed;
  no `backend/` or `frontend/` paths changed.

## 4. Completion

- [x] 4.1 Sync the accepted delta to the main node-agent-reader-interface spec,
  archive the completed change, and confirm no shared doc infrastructure, checker,
  metadata, or runtime behavior was added.

  2026-07-29: synced the renamed and modified NRI-001/NRI-002 requirements to
  `openspec/specs/node-agent-reader-interface/spec.md`, retaining Wave2's existing
  specialized scenarios. Archive review confirmed that the rollout adds only five
  package-local projections and five worksheets; no shared documentation mechanism,
  checker, metadata, runtime behavior, `backend/`, or `frontend/` change was added.
