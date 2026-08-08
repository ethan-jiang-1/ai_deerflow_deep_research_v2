## 1. Synchronize Accepted Documentation

- [x] 1.1 Apply the `hitl2-node` delta: update the accepted capability purpose
  directly, rename the legacy interrupt requirement, and synchronize its fake-path
  scenario with autonomous fixture routing. Do not modify HITL2 runtime code or tests.
- [x] 1.2 Apply the `research-graph-lifecycle` delta: make HITL1 the only current
  graph-owned interrupt/resume surface and state that HITL2 never creates a pending
  request or accepts a raw-route choice. Preserve all existing HITL1 correlation and
  closed-action guarantees.
- [x] 1.3 Synchronize `openspec/governance/req-registry.yaml` entry `HIT-002` with
  the accepted autonomous HITL2 requirement. Treat the registry as an index, not an
  additional behavior change.
- [x] 1.4 Inspect the resulting diff to confirm only the two accepted specs and
  `HIT-002` registry summary change at apply time; keep `agent/` runtime code/tests,
  `backend/`, and `frontend/` unchanged.

## 2. Evidence And Closure

- [x] 2.1 Run the focused autonomous-path evidence:
  `cd agent && UV_OFFLINE=1 uv run --extra operations pytest tests/unit/test_hitl2_real.py tests/graph/test_hitl_nodes.py tests/graph/test_research_graph.py tests/contract/test_deferred_activation_dossiers.py`.
- [x] 2.2 Run `cd agent && UV_OFFLINE=1 make verify` before archive.
- [x] 2.3 Run `openspec validate introduce-hitl2-human-decision-experience --strict`
  and `git diff HEAD --check`; record `git status --porcelain=v1
  --untracked-files=all` and confirm `backend/` and `frontend/` remain clean.
