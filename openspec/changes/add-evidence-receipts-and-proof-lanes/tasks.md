# Tasks

## 1. Lane registry

- [ ] 1.1 Register every real lane (verify, tui-journey, debugger-proof, tui-experiences, doc hygiene, closeout gate) with command, working directory, covered surfaces and success sentinel in `openspec/governance/proof-lanes.toml`. Verify: a focused test loads the registry, rejects an unknown lane or an empty surface list, and every registered command resolves to a real Make target or script.
- [ ] 1.2 Register the operator-facing lanes' required journeys (the experience ids they must include). Verify: the registry loader rejects an operator lane that names no journey.

## 2. Receipt runner

- [ ] 2.1 Implement `scripts/proof_receipt.py run --lane <lane>`: run the lane, tee the transcript, refuse a valid receipt on a dirty tree, and record command, exit code, revision, cleanliness, duration, tool versions and transcript digest. Verify: a focused test shows a red lane recording exit 1, a dirty tree refused, and a green lane recording exit 0.
- [ ] 2.2 Implement `verify` / `--stale`: report a receipt as stale when a covered surface changed after its revision, and print the exact rerun command. Verify: a focused test edits a covered file and asserts staleness, then edits an uncovered file and asserts it stays valid.
- [ ] 2.3 Wire `make proof LANE=<lane>` and document it in the testing document. Verify: the target runs and its exit code matches the lane's.

## 3. Mutation lane

- [ ] 3.1 Implement `scripts/mutation_check.py` over `tests/mutations/registry.py`: apply each mutation, run its selector, require red, restore, and fail when any mutation stays green or its anchor no longer matches. Verify: a focused test with a planted toothless mutation (a behaviour removal whose selector stays green) exits non-zero.
- [ ] 3.2 Seed the registry with the mutations demonstrated during the debugger work (stop-on-HITL, pending-request carrying, observation publishing, HITL log content, Start Run mode forwarding, pause honoured, hermetic demo root). Verify: `make mutation-check` reports each as RED.

## 4. Gates

- [ ] 4.1 Run `check_doc_hygiene.py`, `check_project_gate.py --phase closeout`, `UV_OFFLINE=1 make verify` and the new lane commands from the repository root and `deep_research_harness/` as applicable, measuring every exit code directly. Verify: every measured exit code is 0.
