# TODO: agent-support walkthroughs and local diagnosis

> 状态: 待排期 | 优先级: 中 | 更新: 2026-09-27
> 上游: 已关闭 plan [`deerflow-harness-agent-support-improvement.md`](../_done/_closed_plans/deerflow-harness-agent-support-improvement.md)（其阶段 0–3 未启动，关闭原因是"证据纪律那一半已被 change 链吸收"） | 下游: 各自独立的 change

## Why

那份 plan 的阶段 0–3 从未启动：它先要求用两条只读走查**证明**确有可消费性/语义失败，再
决定是否建东西。plan 因"结论已被吸收"关闭时，这些阶段必须留在账上，否则就成了孤儿工作。

## 待办（按顺序，每阶段可独立停止）

1. **阶段 0（优先，只读）**：走查两条真实路径并出一页证据表——维护本应用的 Coding Agent
   （从意图定位 owner / 最低红测 / 验证命令的实际卡点）与专用 Agent（意图映射、typed
   result、诚实呈现、禁止动作）。工具已就位：调试器探索面 `/harness`、`/targets`、
   `/inspect <id>`、`/context <node>#<n>`；证据形式用 `make proof` 回执。
   **无实质失败即停止相关分支，不为了凑满而造工作。**
2. **阶段 1（仅当阶段 0 证实）**：`demo_sessions inspect` 的可选 `--format json` 受限投影
   （固定版本、脱敏、闭集字段、available/incomplete/unavailable 明确；默认文本与退出码
   语义不变），owner = `deep_research_harness/scripts/demo_sessions.py`。
3. **阶段 2（可独立）**：用现有评测路线验证 controller 的自主判断（复用
   `public-controller-direction-loop@v1` 等案例的真实 loader/受控模型重复评审）；
   研究节点质量另立案例并先经人批准成本与来源边界。与
   [`todo-adopt-framework-engineering-protocols.md`](todo-adopt-framework-engineering-protocols.md)
   的"评测可复现协议"相交时先定 owner 与去重。
4. **阶段 3（需人先裁决）**：是否让专用 Agent 经公共 tool 读取选中 Bundle 的诊断——属
   AI-facing 语义扩面，须人批准产品用途与披露范围后单列 change；默认保持现状。

## Non-Goals

不重写 `AGENTS.md`、不批量增设 skills/catalog/ADR、不把 journal/TUI/诊断升级为状态或恢复
权威、不把 deterministic green 当模型认知质量。细节与理由见已关闭 plan 的原文。
