## 1. Apply Admission Review

- [x] 1.1 Plan review (current apply agent): before the first target edit, re-read the Change Focus, Control Placement Review, `control-placement` policy, design, and current counterexample; add each actionable correction as an unchecked task. Done when the review confirms that tool admission, executor initial-state write, checkpoint ownership, and node consumption have one owner each.

## 2. Red Deterministic Evidence

- [x] 2.1 Extend `tests/unit/test_non_interactive.py` first with table-driven red cases for false, truthy non-boolean, unknown-key, and missing-key policy values; include the existing `disable_clarification=True` compatibility marker under the same closed-policy rules; assert `interactive_required` and no Bundle/graph mutation.
- [x] 2.2 Add a red `ResearchRunExperience` contract in `tests/contract/test_run_experience_contract.py`: `StartRun(scripted=True)` must dispatch explicit `non_interactive=True` plus the complete policy only on `start`, while subsequent resume/refine dispatches do not reinject it; a record-bearing trace with either bounded policy observation marker must remain a safe observation.
- [x] 2.3 Add red graph-node regressions in `tests/graph/test_hitl1_node.py` and `tests/unit/test_hitl2_real.py` for bounded audit-trace evidence, valid auto-profile/auto-proceed, and truthful blocked behavior with no fabricated profile facts.
- [x] 2.4 Add a red production lifecycle regression in `tests/blocking_io/test_research_runtime.py` using `run_deep_research()`, an explicitly supplied actual `BundleGraphExecutor`, and controlled adapters. Prove initial graph-state policy handoff, checkpoint reload, and that a later action cannot replace the policy; retain a direct fallback assertion that admission does not select graph work.
- [x] 2.5 Run the red selectors with `cd deep_research_harness && uv run --extra operations python -m pytest tests/unit/test_non_interactive.py tests/contract/test_run_experience_contract.py tests/graph/test_hitl1_node.py tests/unit/test_hitl2_real.py tests/blocking_io/test_research_runtime.py`; record the expected failures before implementation.

  Red baseline (2026-08-09): 7 expected failures across strict policy admission,
  scripted start projection, both bounded trace markers, HITL1 auto-profile audit,
  HITL2 forced proceed audit, and composed Bundle checkpoint persistence.

## 3. Trusted Policy Handoff

- [x] 3.1 Introduce the runtime-local immutable closed action-input value. Make `tool.py` apply strict boolean/key validation to every marked input-bearing action, then construct and pass the value only for a new `start`. Preserve the existing `disable_clarification=True` trusted compatibility marker under those same rules, the existing bounded denial, and the public tool schema.
- [x] 3.2 Thread the admitted input through `BundleControl` only for a new Bundle start when trusted composition has supplied a `BundleGraphExecutor`, then make that executor serialize it into initial graph values exactly once. Do not instantiate or select an executor for policy propagation; ensure replay, resume, reproject, and refinement paths do not receive a state-writing input.
- [x] 3.3 Update `ResearchRunExperience` so a scripted `StartRun` projects explicit non-interactive intent and the complete policy only to its start transport context, without producing a response, route, profile, or later policy context.
- [x] 3.4 Update HITL1 and HITL2 to consume only checkpointed policy: retain HITL1 pair/language admission and `GATE_BLOCKED` behavior, force only the existing HITL2 `proceed` result when allowed, and append bounded observation-only trace notes without a new control record.
- [x] 3.5 Introduce a closed `RunTraceEntry` vocabulary for `completed_trace` and `trace_delta` only, retaining `LogicalPhaseName` for lifecycle/failure phase fields. Extend `ResearchRunExperience`'s trace validator only for `hitl1_auto_profile` and `hitl2_auto_proceed`, so graph-owned observation markers remain projectable without acquiring lifecycle authority.

## 4. Focused Verification And Evidence

- [x] 4.1 Make all red selectors green and verify the integration assertion reads the actual Bundle-contained checkpoint rather than a hand-built node state.
- [x] 4.2 Update only the affected test-evidence claims and `RequirementImpact` entries in `tests/assets/evidence.py` and `tests/assets/requirement_evidence.py`; preserve the lowest responsible seam and state any distinct reason for multiple layers.
- [x] 4.3 Run `cd deep_research_harness && uv run --extra operations python -m pytest tests/unit/test_non_interactive.py tests/contract/test_run_experience_contract.py tests/graph/test_hitl1_node.py tests/unit/test_hitl2_real.py tests/blocking_io/test_research_runtime.py`, then `make test-assets`, `make test-req-coverage`, and the relevant requirement/spec governance checks.

  2026-08-09: focused selectors pass (78 passed); `make test-assets` reports 378
  central claims and `make test-req-coverage` passes after the migrated main-spec
  ownership headers were restored.

- [x] 4.4 Repair and verify migration-drift governance metadata discovered by the complete deterministic gate: restore migrated main-spec header ownership and synchronize the registered Harness ignore entries without changing their intended ignore behavior.

  2026-08-09: restored `EVH-029` and `WSN-008` main-spec ownership headers and
  registered the intentional `.agents/`/`.claude/` Harness ignores. Verified by
  `make test-assets`, `make test-req-coverage`, and `UV_OFFLINE=1 make verify`.
- [x] 4.5 Repair and verify remaining downstream migration drift exposed by the deterministic gate: retain the submodule-based Docker compose contract and restore the root PR workflow that owns the Harness deterministic CI lane.

  2026-08-09: Docker contracts now resolve the submodule compose source and root PR
  workflows own deterministic and manual live lanes. Verified by the targeted Docker
  and workflow contracts plus `UV_OFFLINE=1 make verify`.
- [x] 4.6 Repair and verify the live-canary composition drift: the generic `infra_probe` host must not receive the lifecycle-only `ResearchRecipe` after the GraphHost migration; recipe ownership remains with `run_deep_research()`.

  2026-08-09: `mixed_recipe` now enters `BundleGraphExecutor(recipe=...)`, which is
  supplied to start/resume; the generic host is absent. Verified by
  `tests/unit/test_live_evaluation.py` (49 passed) without a live-provider call.

## 5. Change Closeout

- [x] 5.1 Run `openspec validate restore-noninteractive-policy-propagation --strict`, `cd deep_research_harness && UV_OFFLINE=1 make verify`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and confirm `deerflow/`, `backend/`, and `frontend/` remain clean.

  2026-08-09: strict validation and `git diff HEAD --check` pass. `UV_OFFLINE=1
  make verify` stops at the pre-existing main-spec ownership-header errors for
  `evaluation-hardening: EVH-029` and `wave2-synthesis-node: WSN-008`. The recorded
  porcelain status shows no changes under `deerflow/`, `backend/`, or `frontend/`.
  Final verification: strict validation passed; `UV_OFFLINE=1 make verify` passed
  (2388 fast, 220 integration with 4 expected skips, and 35 workflow tests); and
  `git diff HEAD --check` passed. The control-case `tool_schema_digest` now equals
  the actual `tool.py` SHA-256. `git status --porcelain=v1 --untracked-files=all`
  records only this downstream change, migration repairs, and the user-owned
  `deep_research_harness/uv.lock` modification.
- [x] 5.2 Synchronize the accepted deltas into the main specs and archive this change only after every implementation and evidence task is complete.

  2026-08-09: synchronized the accepted deltas into `research-run-experience`,
  `runtime-integration`, and `runtime-operations`; `openspec validate --specs` and
  the change strict validation pass. Archive target:
  `openspec/changes/archive/2026-08-09-restore-noninteractive-policy-propagation/`.
- [x] 5.3 Archive-closeout review (current archive agent): re-read the Control Placement Review against the actual diff, unresolved tasks, and deterministic evidence; add every actionable finding as an unchecked task. Done when the selected change has no unresolved control-placement finding and the recorded verification proves the one-writer/checkpoint invariant.

  2026-08-09: no actionable control-placement finding. `tool.py` remains the sole
  policy-admission owner; `BundleGraphExecutor` is the sole initial-state writer;
  the selected Bundle checkpoint is the durable continuation owner; and HITL1/HITL2
  consume only checkpointed policy. The focused lifecycle proof and
  `UV_OFFLINE=1 make verify` provide the deterministic evidence.
- [x] 5.4 Update `_backlog/plans/cli-tui-entry-integrity-repair_plan.md` items 1.1--1.5 with this change name, focused verification commands, strict validation, sync/archive location, and the next unfinished stage.

  2026-08-09: Stage 1 backlog status records the focused suite, strict validation,
  full deterministic gate, synced main specs, archive target, and Stage 2 as next.
