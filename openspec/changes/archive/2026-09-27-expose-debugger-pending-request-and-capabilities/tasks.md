# Tasks

## 1. Carry the pending request (LDD-001 additive)

- [x] 1.1 Project the checkpoint interrupt into a bounded `PendingRequestView` and report it on every session snapshot. Verify: the driver matrix asserts a HITL stop carries the request id, mode, title and guidance matching `pending_request_id`. ✓ `test_hitl_stop_carries_the_node_authored_request`
- [x] 1.2 Populate it on attach through a read-only checkpoint read, so a paused Bundle still says what it waits for. Verify: the driver matrix detaches, attaches with a second driver, and asserts the request survives. ✓ `test_attach_reads_the_pending_request_from_the_own_checkpoint`

## 2. Enforce the drive's own stop policy

- [x] 2.1 `drive_until` stops at a HITL boundary (`stop_on_hitl`) instead of re-entering the waiting node. Verify: the matrix counts `_advance` calls and asserts one call, posture `awaiting_hitl`, next node `hitl1`. ✓ measured 64 before the fix, 1 after; `test_drive_until_stops_at_the_hitl_boundary_once`
- [x] 2.2 A pending pause is honoured at the next committed boundary, clears itself, and the drive never returns nothing. Verify: the matrix asserts exactly one committed node, `paused_at_boundary`, and `pause_requested` false. ✓ `test_a_pending_pause_makes_the_next_drive_advance_one_boundary`; `_invoke_once` no longer drops a concurrent pause

## 3. The workbench stops making the operator guess (RED-014)

- [x] 3.1 State the request (title, guidance, mode, options) in the log and the ask plus every posture-legal action in the prompt. Verify: the TUI test asserts the log holds the node-authored title and the prompt holds the ask with `/help`; the harness checkpoints `[2a]` do the same through the real entry. ✓
- [x] 3.2 Expose both start compositions and the driver's pause: `Start Run` button + palette action + `/run [node]` + `/pause`. Verify: the TUI test drives Start Run via `/run`/the button, `/run` to the terminal, and `/pause`'s honest refusal; harness checkpoints `[12]`-`[14]`. ✓
- [x] 3.3 Provide `/help` listing every capability, and keep `hint` in step. Verify: the TUI test and harness checkpoint `[15]` assert the capability list. ✓

## 4. Gates

- [x] 4.1 From the repository root run `check_project_gate.py --phase plan --change expose-debugger-pending-request-and-capabilities`, then `--phase closeout`; from `deep_research_harness/` run `UV_OFFLINE=1 make verify` and `make tui-journey`; from the repository root run `openspec validate ... --strict`, `git diff HEAD --check` and `check_doc_hygiene.py`. Measure every exit code directly. Verify: every measured exit code is 0. ✓ plan 0, closeout 0, verify 0, journey 0 (23 checkpoints), strict 0, diff-check 0, hygiene clean
