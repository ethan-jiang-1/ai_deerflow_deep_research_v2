## 1. Apply Admission Review

- [ ] 1.1 Plan review (current apply agent): before the first target edit, re-read the Change Focus, Control Placement Review, `control-placement` policy, design, and current counterexample; add each actionable correction as an unchecked task. Done when the review confirms that tool admission, executor initial-state write, checkpoint ownership, and node consumption have one owner each.

## 2. Red Deterministic Evidence

- [ ] 2.1 Extend `tests/unit/test_non_interactive.py` first with table-driven red cases for false, truthy non-boolean, unknown-key, and missing-key policy values; include the existing `disable_clarification=True` compatibility marker under the same closed-policy rules; assert `interactive_required` and no Bundle/graph mutation.
- [ ] 2.2 Add a red `ResearchRunExperience` contract in `tests/contract/test_run_experience_contract.py`: `StartRun(scripted=True)` must dispatch explicit `non_interactive=True` plus the complete policy only on `start`, while subsequent resume/refine dispatches do not reinject it.
- [ ] 2.3 Add red graph-node regressions in `tests/graph/test_hitl1_node.py` and `tests/unit/test_hitl2_real.py` for bounded audit-trace evidence, valid auto-profile/auto-proceed, and truthful blocked behavior with no fabricated profile facts.
- [ ] 2.4 Add a red production lifecycle regression in `tests/blocking_io/test_research_runtime.py` using `run_deep_research()`, an explicitly supplied actual `BundleGraphExecutor`, and controlled adapters. Prove initial graph-state policy handoff, checkpoint reload, and that a later action cannot replace the policy; retain a direct fallback assertion that admission does not select graph work.
- [ ] 2.5 Run the red selectors with `cd deep_research_harness && uv run --extra operations python -m pytest tests/unit/test_non_interactive.py tests/contract/test_run_experience_contract.py tests/graph/test_hitl1_node.py tests/unit/test_hitl2_real.py tests/blocking_io/test_research_runtime.py`; record the expected failures before implementation.

## 3. Trusted Policy Handoff

- [ ] 3.1 Introduce the runtime-local immutable closed action-input value. Make `tool.py` apply strict boolean/key validation to every marked input-bearing action, then construct and pass the value only for a new `start`. Preserve the existing `disable_clarification=True` trusted compatibility marker under those same rules, the existing bounded denial, and the public tool schema.
- [ ] 3.2 Thread the admitted input through `BundleControl` only for a new Bundle start when trusted composition has supplied a `BundleGraphExecutor`, then make that executor serialize it into initial graph values exactly once. Do not instantiate or select an executor for policy propagation; ensure replay, resume, reproject, and refinement paths do not receive a state-writing input.
- [ ] 3.3 Update `ResearchRunExperience` so a scripted `StartRun` projects explicit non-interactive intent and the complete policy only to its start transport context, without producing a response, route, profile, or later policy context.
- [ ] 3.4 Update HITL1 and HITL2 to consume only checkpointed policy: retain HITL1 pair/language admission and `GATE_BLOCKED` behavior, force only the existing HITL2 `proceed` result when allowed, and append bounded observation-only trace notes without a new control record.

## 4. Focused Verification And Evidence

- [ ] 4.1 Make all red selectors green and verify the integration assertion reads the actual Bundle-contained checkpoint rather than a hand-built node state.
- [ ] 4.2 Update only the affected test-evidence claims and `RequirementImpact` entries in `tests/assets/evidence.py` and `tests/assets/requirement_evidence.py`; preserve the lowest responsible seam and state any distinct reason for multiple layers.
- [ ] 4.3 Run `cd deep_research_harness && uv run --extra operations python -m pytest tests/unit/test_non_interactive.py tests/contract/test_run_experience_contract.py tests/graph/test_hitl1_node.py tests/unit/test_hitl2_real.py tests/blocking_io/test_research_runtime.py`, then `make test-assets`, `make test-req-coverage`, and the relevant requirement/spec governance checks.

## 5. Change Closeout

- [ ] 5.1 Run `openspec validate restore-noninteractive-policy-propagation --strict`, `cd deep_research_harness && UV_OFFLINE=1 make verify`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm `deerflow/`, `backend/`, and `frontend/` remain clean.
- [ ] 5.2 Synchronize the accepted deltas into the main specs and archive this change only after every implementation and evidence task is complete.
- [ ] 5.3 Archive-closeout review (current archive agent): re-read the Control Placement Review against the actual diff, unresolved tasks, and deterministic evidence; add every actionable finding as an unchecked task. Done when the selected change has no unresolved control-placement finding and the recorded verification proves the one-writer/checkpoint invariant.
- [ ] 5.4 Update `_backlog/plans/cli-tui-entry-integrity-repair_plan.md` items 1.1--1.5 with this change name, focused verification commands, strict validation, sync/archive location, and the next unfinished stage.
