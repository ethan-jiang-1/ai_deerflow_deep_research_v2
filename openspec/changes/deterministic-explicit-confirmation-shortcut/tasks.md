# Tasks

## 1. Deterministic shortcut (tdd)

- [ ] 1.1 RED: add a hitl1 node unit test where the capabilities stub counts model calls; a complete-proposal interaction with reply `confirm` resolves to ACCEPT_CURRENT_PROPOSAL with zero model invocations. Verify: the new test fails against current code (classification goes to semantic intake).
- [ ] 1.2 GREEN: implement the closed confirmation-phrase table (frozen tuple: `confirm`, `确认`; ASCII case-insensitive exact match after strip) as a pre-classification branch in `_classify_proposal_reply`, returning `SemanticCandidate(intent=HumanIntent.ACCEPT_CURRENT_PROPOSAL)` before the intake loop. Verify: 1.1 passes; phrase-table positive/negative cases pass; existing hitl1 tests stay green.
- [ ] 1.3 Add negative cases: partial/mixed replies (e.g. `confirm please`, `确认并加深`) do NOT take the shortcut and still reach semantic intake; assert model-call count is exactly the bounded intake path's. Verify: tests pass.

## 2. Spec and registry

- [ ] 2.1 Sync the ADDED `HIC-005` requirement into `openspec/specs/human-interaction-contract/spec.md` (header `> req:` line gains `HIC-005`; requirement text and scenarios verbatim from the delta). Verify: `openspec validate --specs --strict` passes.
- [ ] 2.2 Register `HIC-005` in `openspec/governance/req-registry.yaml` and add the `@impl HIC-005` tag on the new unit test. Verify: `python3 openspec/governance/check_project_reqs.py` exits 0 with zero orphans.

## 3. Verification gate

- [ ] 3.1 From repo root run `python3 openspec/governance/check_project_gate.py --phase closeout` directly (no pipe); exit code 0 required.
- [ ] 3.2 From `deep_research_harness/` run `UV_OFFLINE=1 make verify` directly; exit code 0 required.
- [ ] 3.3 From repo root run `openspec validate deterministic-explicit-confirmation-shortcut --strict` and `git diff HEAD --check`; exit codes measured directly.
