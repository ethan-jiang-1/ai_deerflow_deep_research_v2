## 1. Dossier Contract and Evidence

- [x] 1.1 Add failing deterministic dossier-validator tests in
  `agent/tests/contract/test_deferred_activation_dossiers.py` for the exact HITL2, readiness, and
  final-delivery denominator; reject duplicate identity, grouped records, inferred active programs,
  missing or wrong successor changes, invalid commitment/authority combinations, and any
  production-source import of the dossier module.
- [x] 1.2 Add the test-owned activation-dossier record type, closed three-record collection, and
  pure validator in `agent/tests/assets/deferred_activation_dossiers.py`, grounded in the accepted
  specs and current source/proof seams without importing it at runtime.
- [x] 1.3 Register the focused contract selector and a distinct dossier-specific `CNI-004` impact in
  `agent/tests/assets/evidence.py` and `agent/tests/assets/requirement_evidence.py` so the records
  are discoverable as non-runtime planning evidence and cannot become model, state, route, or
  lifecycle authority. Retain the existing reader-card-shape impact and keep
  `scripts/check_node_workflows.py` scoped to reader-card shape.

## 2. Three Separate Dossiers

- [x] 2.1 Create the HITL2 dossier: record its conditional/unresolved trigger, present autonomous
  continuation, typed human-choice admission boundary, legal successor
  `introduce-hitl2-human-decision-experience`, and explicit prohibition on raw internal route UX
  or an inferred model loop.
- [x] 2.2 Create the readiness dossier: record the accepted-but-deferred read-only per-question
  judgment, deterministic hard-rule/materializer/route owners, future candidate/evaluation
  boundaries, and legal successor `activate-readiness-evidence-critic-loop` without changing the
  fallback.
- [x] 2.3 Create the final-delivery dossier: record the accepted-but-deferred report-composition
  candidate bounded by the readiness plan, integrity-gate/publisher/terminal owners, future
  candidate/evaluation boundaries, and legal successor
  `activate-final-report-composition-loop` without changing formatting or publication.

## 3. Verification and Closure

- [x] 3.1 Run `cd agent && uv run --extra operations pytest tests/contract/test_deferred_activation_dossiers.py tests/contract/test_node_workflow_reader_interface.py tests/unit/test_hitl2_real.py tests/unit/test_readiness_real.py tests/unit/test_final_delivery_real.py`; ensure no runtime import, active branch claim, prompt, tool, interrupt, state, route, or lifecycle behavior is introduced.
- [x] 3.2 Run `cd agent && UV_OFFLINE=1 make verify`, `openspec validate
  prepare-deferred-cognitive-and-human-decision-dossiers --strict`, project requirement/spec
  governance, and `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`
  and confirm `backend/` and `frontend/` remain clean before requesting archive authorization.
- [x] 3.3 Present HITL2, readiness, and final-delivery dossiers separately and obtain fresh explicit
  Scope Card approval before proposing `introduce-hitl2-human-decision-experience`,
  `activate-readiness-evidence-critic-loop`, or `activate-final-report-composition-loop`.
