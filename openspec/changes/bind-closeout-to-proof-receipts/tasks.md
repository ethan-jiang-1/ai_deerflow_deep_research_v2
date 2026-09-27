# Tasks

## 1. Checker

- [ ] 1.1 Implement `openspec/governance/check_proof_receipts.py` over the `selected-change-closeout.py` attestation (`git diff --name-only <base_commit>..<head_commit>`): intersect the touched files with the lane registry's surfaces, and require a valid runner-produced receipt per required lane (exit zero, clean tree, revision still covering the surfaces, matching transcript digest, success sentinel present). Verify: focused tests pass a fresh receipt, fail a stale one, fail a missing one, fail a hand-written claim, and fail a transcript whose digest or sentinel does not match.
- [ ] 1.2 Support `--mode warn|enforce` (warn is the default for the measured window) and always print the active mode; exit zero with `no selected change` when no attestation or active change is present. Emit the exact rerun command (`make proof LANE=<lane>`) for every failure, and stay silent when no registered surface is touched. Verify: a change touching only uncovered files exits zero.
- [ ] 1.3 Provide `--self-test` planted-violation coverage for each rule, including a receipt whose recorded surfaces were narrowed after the fact.

## 2. Aggregate registration

- [ ] 2.1 Register the checker in `check_project_gate.py`'s component inventory, update its printed wording and the project-structure inventory, and keep `check_project_gate.py` orchestration-only (exit-code preservation, no rule semantics). Verify: a focused test asserts the registered set, and that the aggregate still preserves each component's exit code.
- [ ] 2.2 Update the closeout guidance that restates the composition (selected-change-closeout guide, local Delivery Lanes sentence) so no document claims a different component set.

## 3. Roll-out

- [ ] 3.1 Run the checker in warn-only mode against the most recent archived changes; record how many would have failed and why. Verify: the measurement is recorded in the change's tasks with the exact command and counts.
- [ ] 3.2 Flip closeout to treat a missing or stale receipt as a failure, and record one real closeout that exercised it.

## 4. Gates

- [ ] 4.1 Run `check_project_gate.py --phase plan/closeout`, `openspec validate --strict`, `check_doc_hygiene.py`, `UV_OFFLINE=1 make verify` and the lane commands, measuring every exit code directly. Verify: every measured exit code is 0.
