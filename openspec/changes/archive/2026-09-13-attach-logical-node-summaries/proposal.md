# attach-logical-node-summaries

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/domain/identifiers.py`——`LogicalPhase` 已是节点名与顺序的单一权威，一句话语义作为其旁的冻结 mapping 归它所有；`graph/topology_snapshot.py` 是生成文档的唯一渲染方。
- **Seam classification:** wiring —— 只新增文档投影用的静态数据与渲染文本，无认知面、无人工决策面、无运行时行为变化（拓扑 node/edge/可达性校验不变）。
- **Question:** 能否把已存在于各 workflow.md H1 的一句话语义挂上统一命名数据，使生成的 topology 文档自解释，同时不重命名任何稳定契约？
- **Necessary adjacent/external contracts:** `deep_research_harness/tests/contract/test_topology_snapshot.py`（已有的 regenerate-and-compare 断言将继续逐字覆盖新输出）；各节点包 `workflow.md` H1（降级为投影，由新测试钉住）。
- **Evidence seam:** `tests/contract/test_topology_snapshot.py`（regenerate-and-compare + H1↔summary 投影匹配）+ `UV_OFFLINE=1 make verify`。
- **Not in scope:** 逻辑名/State 键/spec 目录重命名；`NodeSpec` 契约变更；运行时行为；`deerflow/`。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

Every workflow node has a stable but semantically opaque logical name (`wave0`, `wave1`, `wave2_synthesis`, `hitl1`, `hitl2`, ...). The one-sentence human meaning of each node already exists as the H1 title of its `workflow.md`, but that meaning was never attached to the unified naming data: the `LogicalPhase` enum, `NodeSpec`, and the generated topology document all carry bare names only. A new reader listing `graph/nodes/` or reading the generated topology doc gets no semantic signal and must open all eleven workflow files to decode the vocabulary.

## What Changes

- Add one canonical one-line summary per logical node, owned next to the `LogicalPhase` enum in `src/deerflow_deep_research/domain/identifiers.py` (the existing single authority for phase names and order).
- Extend `render_topology_snapshot()` so the generated `docs/deep-research-topology.md` node list renders as `` - `wave0` — Acquire authoritative-source evidence for assigned work `` instead of a bare name.
- Pin the projection with tests: the generated document stays in sync with `render_topology_snapshot()`, and every node package `workflow.md` H1 title matches the canonical summary.
- Non-goals: no logical-name renames, no `NodeSpec` contract change, no checkpoint/State key change, no runtime behavior change. `wave`/`hitl` names remain stable contracts.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — no spec-level behavior changes; the topology snapshot's node/edge/reachability semantics are untouched. Pure generated-doc and code-data addition, declared via `skip_specs: true`.)

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/identifiers.py` — new frozen summary mapping.
- `deep_research_harness/src/deerflow_deep_research/graph/topology_snapshot.py` — render summaries.
- `deep_research_harness/docs/deep-research-topology.md` — regenerated.
- `deep_research_harness/tests/contract/test_topology_snapshot.py` — new projection-match test alongside the existing regenerate-and-compare test.
- `deep_research_harness/AGENTS.md` generated structure block — unchanged; node names unchanged everywhere.
