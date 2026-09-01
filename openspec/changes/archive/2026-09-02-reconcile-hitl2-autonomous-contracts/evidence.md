# Cpre Execution Evidence (append-only)

## Task 1.2 — red baseline captured 2026-09-02 (before any sync edit)

Scan pattern (exact stale clauses from task 1.2, rg-equivalent `-n`):

`HITL-2 presentation SHALL render|must re-suspend at HITL2|user chooses rerun at HITL2|retained HITL-1 or HITL-2 session|semantic HITL-1/HITL-2 guidance|Existing HITL2 choice identifiers|second human stop|awaiting_hitl2|active_hitl2_subject`

Expected matches before migration:

- `openspec/specs/rerun-node/spec.md:121` — `user chooses rerun at HITL2`
- `openspec/specs/rerun-node/spec.md:122` — `must re-suspend at HITL2`
- `openspec/specs/research-run-experience/spec.md:257` — `HITL-2 presentation SHALL render`
- `openspec/specs/research-demo-tui/spec.md:161` — `retained HITL-1 or HITL-2 session`
- `openspec/specs/research-graph-lifecycle/spec.md:598` — `Existing HITL2 choice identifiers`
- `openspec/specs/research-cli-onboarding/spec.md:75` — `semantic HITL-1/HITL-2 guidance`
- `deep_research_harness/docs/run-lifecycle-walkthrough.md:52` — `second human stop`
- `openspec/governance/req-registry.yaml` — no matches (REN-001/REN-006 summaries carry
  decision-flavored wording — "HITL2 decision payload", "old HITL2 proceed decision" —
  without matching the exact clauses; corrected in task 2.2)
- `deep_research_harness/tests/fixtures/run_updates.py:175,209,211` — `awaiting_hitl2`,
  `awaiting_invalid_hitl2_choice`
- `deep_research_harness/tests/integration/test_demo_run_update_adapters.py:41,76`
- `deep_research_harness/tests/integration/test_demo_real.py:175`
- `deep_research_harness/tests/integration/test_refinement_round_workflow.py:452` —
  `test_active_hitl2_subject_survives_independent_direction_admission`
- `deep_research_harness/tests/integration/test_demo_tui.py:202`

Task 4.1 re-runs the same scan and must exit 1 (no matches) on current authority,
docs, and tests (archives excluded).

## Task 1.1 — review findings folded into planning artifacts (2026-09-02)

- `workflow-control.md` reference resolved: content lives in proposal.md's Control
  Placement Review / Workflow Outcome Review sections; task 1.1 wording fixed.
- Five-capability keep/retire matrix added as design.md §D5; every delta hunk must
  trace to a Retire cell; Keep cells constrain the sync.

## Task 1.3 — plan gate

`check_project_gate.py --phase plan` exit 0 (change-guidance, delta-specs,
requirement-reservation, strict-validation all passed) before any sync edit.

## Task 2.4 — remaining HITL2 audit (2026-09-02, delegated read-only audit)

`grep -rn -i "hitl[-_ ]\?2" openspec/specs/` → 122 matches across 16 files. Every
match classified: AUTONOMOUS / INTERNAL-CONTROL / FUTURE-GATED / VIOLATION.
Result: **0 VIOLATIONS**. Owning `hitl2-node/spec.md` confirmed autonomous
(lines 14-39: validator + autonomous `proceed`, no interrupt/resume, future human
decision requires its own reviewed change). Internal controls retained:
`hitl2_rerun_payload` (rerun-node 24), `hitl2=real` recipe keys, `REPAIR_HITL2`,
`Hitl2Decision` fixture routes, `hitl2_auto_proceed` trace marker. FUTURE-GATED only
in cognitive-node-interface (dossier), cognitive-program-evidence, evaluation-hardening
(evidence class), hitl2-node:39. Per-file totals recorded in the audit transcript;
no archive edited. Verdict PASS.

## Section 3 — fixture/test migration (2026-09-02)

### Task 3.1 red evidence (tests rewritten against still-stale renderers/fixtures)

- `pytest tests/integration/test_demo_run_update_adapters.py tests/integration/test_refinement_round_workflow.py -x -q`
  → **1 failed, 6 passed**: `test_standalone_adapters_render_safe_invalid_choice_feedback_without_wire_data`
  failed exactly on the deterministic red expectation —
  `assert '上一次选择无效；请只输入上方显示的选项 ID，例如 zh。' in cli` failed because the
  still-stale renderer hardcoded the retired HITL2 `proceed` example for a language-choice
  rejection.

### Presentation-adapter sync (minimal, presentation-only)

- `scripts/demo_real.py` + `scripts/demo_tui.py`: invalid-choice example now derives from
  the first advertised option id (retired HITL2 `proceed` hardcoded string removed).
- `scripts/demo_tui.py` composer: CHOICE-mode gate generalized from
  `mode=="choice" and phase=="hitl1"` to `mode=="choice"` — every CHOICE prompt is
  exact-match-only; the fallthrough that forwarded composer text existed only to serve the
  retired synthetic HITL2 choice fixture and is now dead-path fail-closed. This matches
  synced RED-009 (forwarding carve-out removed). No `src/deerflow_deep_research` change.
- `tests/fixtures/run_updates.py`: deleted `awaiting_hitl2()` and
  `awaiting_invalid_hitl2_choice()` (production-shaped synthetic HITL2 prompts); added
  `awaiting_invalid_language_choice()` on the current HITL1 language CHOICE contract.
- `tests/integration/test_demo_tui.py`: `test_tui_forwards_unadvertised_choice_to_graph_owned_validation`
  → `test_tui_holds_unadvertised_text_on_choice_prompts` (exact-match-only, prompt held).
- `tests/integration/test_demo_real.py`: HITL2 leg of the update sequence replaced with
  the HITL1 language CHOICE leg; CLI still forwards unadvertised text as a shared text
  answer for graph-owned validation (REC contract unchanged).
- `tests/integration/test_refinement_round_workflow.py`:
  `test_active_hitl2_subject_survives_independent_direction_admission` →
  `test_active_hitl1_choice_subject_survives_independent_direction_admission`; valid
  HITL1 CHOICE pending (full `SupportedLanguageOption` set, phase="hitl1",
  bootstrap-committed trace); same DRH-005 invariant asserted (independent direction
  admission preserves pending subject, cursor, mode, waiting_for="hitl1").

### Green runs

- Task 3.2: `pytest tests/integration/test_demo_run_update_adapters.py tests/contract/test_run_experience_contract.py -q` → **36 passed**.
- Tasks 3.3+3.4: `pytest tests/integration/test_demo_real.py tests/integration/test_demo_tui.py tests/integration/test_demo_cli.py tests/integration/test_refinement_round_workflow.py -q` → **86 passed**.
- Task 3.5: no test-owned registry referenced any renamed/removed asset (grep clean);
  `scripts/check_test_assets.py` now lives at `scripts/checks/check_test_assets.py`
  (2026-08-31 scripts/ reorganization; task's literal path is stale, semantic check
  unchanged) → **exit 0** (425 central claims, 3016 deterministic tests). No
  `evaluation-hardening` semantic change.
- Task 3.6: `pytest tests/unit/test_hitl2_real.py tests/graph/test_research_graph.py tests/integration/test_demo_cli.py tests/contract/test_run_experience_contract.py -q` → **35 passed** (valid/malformed HITL2, full graph completion, no second prompt, HITL1 typed-choice coverage).

## Section 4 — closeout (2026-09-02)

### Task 4.1 bounded scans

- Exact stale-clause scan over `openspec/specs`, `req-registry.yaml`,
  `run-lifecycle-walkthrough.md`, harness `tests/` + `scripts/` (excluding
  regenerated `__pycache__` bytecode): **exit 1, no matches** (red baseline in
  §Task 1.2 above is fully retired).
- `-i "hitl2"` sweep of the walkthrough: 4 remaining mentions, all autonomous or
  internal-control (§4 heading autonomous HITL2, autonomous validation wording,
  "never chosen by a user", `repair_hitl2` readiness back edge).
- Full 122-match specs audit recorded under Task 2.4: PASS, 0 violations.

### Task 4.2 scope proof

`git diff --name-only`: five main specs, req-registry, walkthrough, demo_real.py,
demo_tui.py (presentation adapters), 4 test files + fixtures, change artifacts.
**No `deep_research_harness/src/` edits; no `deerflow/` edits** (`git diff
--submodule=short` shows no gitlink change). No runtime/public API/topology/
checkpoint schema/dependency change.

Out-of-payload-but-necessary additions (documented, non-contract): two harness
scripts README prose lines and `openspec/governance/check_project_architecture.py`
docstring `@impl PRS-022`, plus `_backlog` BUG-067 ledgers. These repair a
**pre-existing clean-tree closeout-gate failure** (verified on a pristine HEAD
worktree before any local edit: both checkers exited 1 at commit 16f481c) caused by
commit 3965640. Registered and closed as BUG-067; zero accepted-contract text
changed, so no OpenSpec delta is implicated. Cpre's HITL2 payload remains atomic.

### Closeout gate

- BUG-067 fixed: `check_project_req_coverage.py` exit 0 ("Requirement
  implementation evidence passed"); `check_harness_dependency_direction.py`
  exit 0 ("Harness dependency direction passed").
- Full `check_project_gate.py --phase closeout` re-run after fixes: recorded below.
