# Design: fix-readiness-degraded-route

## Context

See proposal.md — Why. The failure chain (BUG-044, 2/2 real 003 runs):
wave2 gate exhausts its 2-round budget → first exhaustion degrades to pass and
writes `degraded_decisions += ("wave2_synthesis:exhaustion_degraded",)`
(`engine/gate_kernel.py` step 8, gate-owned field per `domain/state.py`
FieldOwnership) → hitl2 → readiness. Readiness's critic then either fails
(`conservative_readiness_output` → all questions `blocked_repair_required`) or
genuinely judges a question `blocked_repair_required`, and the current REA-004
route logic (`graph/nodes/readiness/node.py`) sends any such verdict to
`repair_targeted`. That route re-enters `targeted_evidence` → `wave2_synthesis`
→ the wave2 gate re-evaluates at exhausted budget with the marker already
present → `blocked` (gate_blocked), killing the run before `final_delivery`.

The wave2 gate degradation marker is the exact "repair is closed" signal: it is
written once per budget seeding and a second exhaustion with it present always
blocks (`gate_kernel.py` lines 199-223; `tests/engine/test_gate_kernel.py`
lines 580-621). Therefore any `repair_targeted` route emitted after degradation
is provably a dead end, and the runbook-003 5.1 contract (degraded pass →
hitl2 → readiness → final_delivery → completed with disclosed gaps) requires
readiness to deliver instead.

## Goals / Non-Goals

Goals:
- After wave2 degradation, readiness routes `pass` even when critic verdicts are
  `blocked_repair_required` (admitted or conservative fallback), so the degraded
  run reaches `final_delivery` and the report discloses the unresolved gaps.
- Keep non-degraded runs byte-identical: the repair loop and all gate semantics
  are untouched.

Non-Goals:
- No change to wave2 gate degradation semantics, budgets, or the
  once-per-seeding marker bound.
- No change to structural hard-rule routing (`exhausted` still wins).
- No change to the materializer or report plan shape (gap disclosure already
  works, `tests/unit/test_honest_delivery_disclosure.py`).
- No bridge hang-hardening (separate item, out of scope per runbook-003).

## Decisions

### D1. Route `pass` on `blocked_repair_required` when the wave2 gate has degraded

In `graph/nodes/readiness/node.py` route determination, read the degraded
condition from checkpoint state:

```python
wave2_degraded = exhaustion_degradation_marker("wave2_synthesis") in (
    state.get("degraded_decisions") or ()
)
```

and gate the `repair_targeted` branch on `not wave2_degraded`; the else branch
(`pass`) already covers the degraded case without further changes. The marker
string comes from `engine.gate_kernel.exhaustion_degradation_marker`, the single
definitional source (import direction `graph → nodes → engine` is the existing
rule, used by `graph/nodes/gate_adapter.py`).

Why not alternatives:
- *Route pass only for the conservative fallback (critic failure), not for
  admitted blocked verdicts* — rejected: in a degraded run a genuine
  `blocked_repair_required` is also a dead end (no budget left; the gate blocks
  the next gap evaluation). Distinguishing them adds state coupling with no
  behavioral upside.
- *Loosen the gate to degrade again* — rejected: the once-per-seeding bound is a
  deliberate bounded-degradation guard (BUG-035); re-loosening it would allow
  unbounded degraded loops and contradicts `tests/engine/test_gate_kernel.py`.
- *Make readiness clear the marker / reset budget* — rejected: readiness has no
  gate authority; the degraded state is a fact of the run, not a knob.

### D2. Keep structural failures dominant and count blocked questions

`has_structural_failure(hard_failures) or report_plan_ref is None` stays the
first branch (`exhausted` + BLOCKED), and `readiness_blocked_count` is still
computed from all `blocked_repair_required` verdicts regardless of route, so
diagnostics keep showing why the run degraded. The report plan materializes
`unresolved_gaps` as mandatory uncertainties on the `pass` path — no
materializer change needed.

### D3. Delta spec on `readiness-node` (REA-004) only

The externally visible contract change is readiness routing; the wave2 gate and
gate-kernel specs are unchanged. The `low-scale-real-auto` spec (LSA-001) already
promises the completed-with-disclosure outcome for honest gaps; this change makes
the promise hold under critic failure too, so no delta there.

## Risks / Trade-offs

- [Risk] A degraded run whose critic genuinely finds a NEW repairable defect now
  delivers with disclosure instead of attempting repair → mitigated: repair is
  provably closed (gate blocks), so delivery-with-disclosure is the only
  non-terminal outcome; the disclosed gap keeps the defect visible in the report.
- [Risk] Marker string coupling between readiness and gate kernel → mitigated:
  both use `exhaustion_degradation_marker` (single definition), and the same
  literal already appears in tests and the rerun planner.
- [Risk] Regression on non-degraded repair loop → mitigated: the change is one
  boolean guard; existing `test_candidate_unknown_or_duplicate_question_fails_closed`
  and `test_bridge_failure_projects_repair_without_all_ready` keep passing
  unchanged (their state has no marker).

## Verification

- New unit tests in `tests/unit/test_readiness_real.py`: (1) bridge failure +
  degraded marker → route `pass`; (2) admitted `blocked_repair_required` +
  degraded marker → route `pass` and gap disclosure; (3) degraded marker +
  structural failure → still `exhausted`.
- Full gate: `UV_NO_CACHE=1 make verify`（本机 uv 全局缓存有权限限制，
  `UV_OFFLINE=1` 会在 lock-check 阶段失败；等价窄口径：
  `UV_NO_CACHE=1 .venv/bin/python -m pytest tests/unit tests/graph
  tests/contract` + `ruff`）。
- Real-run validation: `soft-bundle run <root> --mode 003` 应终态
  `completed`、`final/report.md` 存在且 `## Uncertainties` 披露 gap
  （需 `.env` + 网络）。BUG-045 未修前，补证循环仍全部 work.failed，报告
  以 gap 披露为主——这是本 change 预期的诚实降级交付，不是失败；补证收敛
  是 BUG-045 独立 change 的事后验证。
