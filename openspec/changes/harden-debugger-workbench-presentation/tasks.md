# Tasks

## 1. Truthful operator state (RED-014 clause)

- [x] 1.1 Map `awaiting_hitl`, `paused_at_boundary` and `terminal` to prompt lines that name the next legal composer action, and render an explicit no-session posture on the first debug screen and after detach, cancel or a refused start. Verify: the operator-eye capture at 100×30 shows `姿态: 无调试会话 …` after `/detach`, `/cancel` and a refused start, and the posture-specific prompt while a session is live. ✓ Harness step [11] and the capture at 100×30 confirm each state; the stale `paused_at_boundary · 下一节点: —` line is gone.
- [x] 1.2 Stop the shared pending indicator for workbench input so it can never own `#inspect`, and echo the operator's input to the log instead. Verify: reproduced headlessly first (after a 2.4 s dwell the pane held the pending hint instead of the prompt), then re-checked green. ✓ `_assert_pane_stable` asserts after ≥1.3 s at every checkpoint.

## 2. Workbench-only controls and guidance

- [x] 2.1 Hide the shared entry buttons in the workbench while keeping them in the DOM, and give the workbench a hint line that documents its commands. Verify: the tiered layout test asserts `#start-research`/`#accept`/`#cancel` are present-but-hidden, and the hint names `/context`, `/files`, `/attach`, `/cancel`. ✓ Recorded in the design: omitting the buttons from the DOM broke the shared render path and the app never reached Ready.
- [x] 2.2 Clear the composer after every workbench slash command. Verify: the capture shows an empty composer after `/context`, `/files`, `/attach`, `/detach` and `/cancel`. ✓

## 3. On-demand panes and a declared minimum size

- [x] 3.1 Fold the Node Context and Files panes until asked for, bound their heights, and show them when the operator opens them. Verify: the supported-tier layout test asserts both panes start folded, appear on `/context` and `/files`, and leave the log ≥3 rows at 100×30 and 120×45. ✓
- [x] 3.2 Declare 100×30 as the supported minimum and state the limitation below it while keeping entries and composer usable. Verify: the degraded-tier test asserts the notice names both the current and supported sizes at 80×24, every remaining pane is inside the screen, the log keeps ≥4 rows, the panes stay folded and the composer keeps focus. ✓

## 4. Verification method (the hard-won part)

- [x] 4.1 Assert after a realistic dwell at every operator checkpoint (no shared-hint takeover, no blank pane, expected posture retained). Verify: `make tui-journey` green with a ≥1.3 s dwell per checkpoint. ✓ Red-capable: the pre-fix build fails this assertion by construction (reproduced).
- [x] 4.2 Assert layout visibility in two tiers (degraded 80×24; supported 100×30 and 120×45). Verify: the TUI suite green. ✓
- [x] 4.3 Record the operator-eye pane capture as the diagnostic procedure of record for what assertions still miss, in `docs/testing-and-evaluation.md`. Verify: doc hygiene passes from the repository root. ✓

## 5. Gates

- [x] 5.1 From the repository root run `python3 openspec/governance/check_project_gate.py --phase plan --change harden-debugger-workbench-presentation` and `--phase closeout`; from `deep_research_harness/` run `UV_OFFLINE=1 make verify` and `make tui-journey`; from the repository root run `openspec validate harden-debugger-workbench-presentation --strict`, `git diff HEAD --check`, and `check_doc_hygiene.py`. Measure every exit code directly (no pipes). Verify: every measured exit code is 0. ✓ plan gate 0 (delta valid, RED-014 already-assigned), closeout gate 0, `UV_OFFLINE=1 make verify` 0, `make tui-journey` 0 (15 checkpoints with dwell), `openspec validate --strict` 0, `git diff HEAD --check` 0, doc hygiene clean — all measured directly
