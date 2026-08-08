## 1. Reader Contract And Static Checker

- [x] 1.1 Add a zero-external-dependency reader-inventory checker under canonical `agent/scripts/` that derives the exact eleven-node denominator from the current topology and validates only the fixed card interface and non-runtime authority notice.
- [x] 1.2 Extend the reader fixture/contract seam with red cases for a missing card, missing identity field, missing commitment state, forbidden Charter identity, out-of-order heading, and missing authority notice; add the focused test-evidence and requirement-impact records required by the test-evidence policy; then make the checker pass every valid card without importing or executing the runtime.
- [x] 1.3 Register the checker and focused test paths in `openspec/governance/project-structure.toml`, update its checker/fixtures, regenerate the generated `agent/AGENTS.md` locator, and prove the architecture checker rejects a missing registered path or an upstream registry entry.

## 2. Eleven Node-Local Reader Cards

- [x] 2.1 Rewrite `hitl1`, `topic_planning`, `wave0`, `wave1`, `wave2_synthesis`, and `targeted_evidence` `workflow.md` files to the fixed product-responsibility-first shape while retaining each current symptom, owner, admission, route, tool-posture, feedback, and narrow proof navigation required by NRI-001/NRI-002.
- [x] 2.2 Add `bootstrap` and `rerun` cards that state intentional deterministic-controller exclusion, trusted input/scope, deterministic transition/recovery authority, and rejected prompt/capability-first edits without inventing a model or human path.
- [x] 2.3 Add the `hitl2` card that separates its current autonomous continuation from its conditional human-decision responsibility and names the unresolved preference/authorization required before an interaction change.
- [x] 2.4 Add `readiness` and `final_delivery` cards that distinguish their accepted-but-deferred cognitive responsibilities from current deterministic fallback/publisher mechanisms and identify the activation prerequisites without creating a critic/composer call.

## 3. Verification And Spec Synchronization

- [x] 3.1 Run the focused reader checker/contract tests and `python3 openspec/governance/check_project_architecture.py`; confirm exact eleven-card coverage, fixed identity/heading structure, no runtime reader registration, and no `backend/` or `frontend/` edits.
- [x] 3.2 Re-read all cards, proposal, design, and deltas as one contract. Confirm every card leads with product responsibility; participation, commitment, current mechanism, deterministic authority, and audit-only branch evidence remain separate; and no card asserts new model, tool, human, route, state, checkpoint, or lifecycle behavior.
- [x] 3.3 Run `cd agent && UV_OFFLINE=1 make verify`, `openspec validate normalize-cognitive-node-interfaces --strict`, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all` and preserve unrelated work.
- [x] 3.4 Sync this change's delta specs into `openspec/specs/`, then add CNI-001 through CNI-005, NRI-003, and PRS-014 to the active requirement registry so no archived Change 0 delta remains normative. Re-run strict validation and the registry/structure checks, then stop for explicit apply/closure direction; do not archive or begin Change 2 without that direction.
