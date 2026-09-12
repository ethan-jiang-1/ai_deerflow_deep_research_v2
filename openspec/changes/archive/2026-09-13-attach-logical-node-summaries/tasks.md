# Tasks — attach-logical-node-summaries

## 1. Canonical summaries in identifiers.py

- [x] 1.1 Add `LOGICAL_NODE_SUMMARIES: Mapping[LogicalPhase, str]` next to `LogicalPhase` in `src/deerflow_deep_research/domain/identifiers.py`, with the eleven summaries taken verbatim from each node package `workflow.md` H1, plus an import-time completeness check (every member, nonblank, no extras); export it in `__all__`. Verify: `uv run python -c "from deerflow_deep_research.domain.identifiers import LOGICAL_NODE_SUMMARIES; assert len(LOGICAL_NODE_SUMMARIES) == 11"`.

## 2. Render summaries in the generated topology doc

- [x] 2.1 Extend `render_topology_snapshot()` in `src/deerflow_deep_research/graph/topology_snapshot.py` to render each node as `` - `name` — Summary `` (em-dash form, matching workflow.md H1 convention); regenerate `docs/deep-research-topology.md` via `uv run python scripts/render_topology.py`. Verify: doc shows summaries and node/edge sections are otherwise unchanged.

## 3. Drift-proofing tests

- [x] 3.1 Extend `tests/contract/test_topology_snapshot.py` (which already owns the regenerate-and-compare assertion) with a projection-match test: each `graph/nodes/*/workflow.md` H1 title equals the canonical summary for that logical name. Verify: `UV_OFFLINE=1 uv run --no-sync python -m pytest tests/contract/test_topology_snapshot.py -q`.

## 4. Gate verification

- [x] 4.1 Run the deterministic project gate and confirm no unrelated drift: `UV_OFFLINE=1 make verify`.
