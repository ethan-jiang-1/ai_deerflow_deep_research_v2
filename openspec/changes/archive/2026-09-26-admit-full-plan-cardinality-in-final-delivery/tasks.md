# Tasks

## 1. Cardinality fix (tdd)

- [x] 1.1 RED: add a final-delivery unit test that builds a plan with 7 writable conclusions and 9 mandatory uncertainties (the real incident's scale), asserts `plan_order_layout` constructs, `render_final_artifacts` produces artifacts, and `_validate_final_artifacts` passes. Verify: the test fails against current code with the `too_long` pydantic error (the reproduced incident).
- [x] 1.2 GREEN: remove `max_length=8` from `FinalDeliveryLayoutCandidate.conclusion_order/uncertainty_order` in `domain/publication.py`. Verify: 1.1 passes; existing publication/final-delivery tests stay green.

## 2. Closed-category feedback (tdd)

- [x] 2.1 RED: add a test asserting `parse_layout_candidate` on a well-formed JSON object failing the typed layout validation (e.g. missing `conclusion_order`) raises a ValueError whose message is exactly `final_layout_schema_invalid` with a non-None bounded `.detail` naming the failing field, and that `_canonical_layout_code` maps it to itself. Verify: fails against current code (bare pydantic message, collapsed code).
- [x] 2.2 GREEN: catch `ValidationError` in `parse_layout_candidate`, raise the closed category with a local bounded `_schema_detail` projection (≤3 errors, msg ≤120 chars); add `final_layout_schema_invalid` to `_LAYOUT_LITERAL_CODES`. Verify: 2.1 passes.

## 3. Read-back failure fact (tdd)

- [x] 3.1 RED: add a node-level test where the publication/read-back path raises and assert the event recorder received one bounded validation fact with a closed code (`final_delivery_readback_failed` or an existing literal code) before the WORK_FAILED disposition. Verify: fails against current code (no fact recorded).
- [x] 3.2 GREEN: record the closed-code fact in the final `except` branch via `_record_layout_validation_fact`, mapping exception messages in the closed code set directly. Verify: 3.1 passes.

## 4. Spec sync and gates

- [x] 4.1 Sync the MODIFIED FID-001 delta into `openspec/specs/final-delivery-node/spec.md` (complete requirement text with the two added clauses, all ten scenarios). Verify: `openspec validate --specs --strict` passes.
- [x] 4.2 From repo root run `python3 openspec/governance/check_project_gate.py --phase closeout` directly; exit 0.
- [x] 4.3 From `deep_research_harness/` run `UV_OFFLINE=1 make verify` directly; exit 0.
- [ ] 4.4 From repo root run `openspec validate admit-full-plan-cardinality-in-final-delivery --strict` and `git diff HEAD --check`; exit codes measured directly.
- [x] 4.5 Real-machine validation: recompute the startup fingerprint, restart the Gateway, and re-run `make demo-real` with the cracked stdin script (see `_backlog/plans/demo-real-gateway-closeout.md`); the run must pass `final_delivery` and reach `研究流程已完成`.
