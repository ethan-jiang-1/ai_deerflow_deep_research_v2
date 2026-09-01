# C3 Execution Evidence (append-only)

## Task 1.1 — dated facts re-verified 2026-09-02 (before implementation)

- `openspec list --json` → empty (C0 archived).
- `domain/run_observation.py:36` → `MAX_EVENT_RECORDS = 256`; eviction priority is
  outcome-blind (`runtime/run_observation.py` `_append_bundle_event`).
- `scripts/experiments/tui_trace.py` exists — zero-contract read-side spike
  (arbitrary path + SQLite + graph compile).
- `domain/lifecycle.py:485` `make_node_visit_id` — `g{gen}-{phase}-a{n}` reuses the
  same id after HITL resume (visit id is not a uniqueness key).
- `agents/middleware.py` — `BudgetMiddleware.model_calls` / tool counters exist in
  memory; no durable per-invocation activity facts.
- `runtime/node_agent_bridge.py` — `render_node_cognitive_control_program` at :338;
  `agent.ainvoke` at :428; no durable capture between admission and first provider
  call. Capture seam = between those points.

## Task 1.2 — plan gate

`check_project_gate.py --phase plan --change add-local-workflow-debug-observation`
exit 0 (guidance/delta-specs/reservation incl. LDO-001..008/strict-validation).
