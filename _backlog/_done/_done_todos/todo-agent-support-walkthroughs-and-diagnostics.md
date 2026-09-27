# TODO: agent-support walkthroughs and local diagnosis

> 状态: 已完成（2026-09-27，DONE-008；阶段 0 走查由 change `run-agent-support-evidence-walkthroughs` 交付） | 优先级: 中 | 更新: 2026-09-27
> 上游: 已关闭 plan [`deerflow-harness-agent-support-improvement.md`](../_done/_closed_plans/deerflow-harness-agent-support-improvement.md)（其阶段 0–3 未启动，关闭原因是"证据纪律那一半已被 change 链吸收"） | 下游: `todo-controller-evaluation-repetition`（阶段 2 的存活分支）

## 完成结论（2026-09-27，证据见 change `run-agent-support-evidence-walkthroughs` 的 `evidence/`）

- **阶段 0 完成**：两条只读走查 + 一页证据表（输入/期望实际/权威结果/证明强度/缺口 owner/最低红灯 seam）。
  走查 A（BUG-072 重放）实测卡点：LDD-003 无路由且义务仅为蕴含（A-2）、ADR 树零入链（A-3）、
  make 外 uv 缓存陷阱（A-4）、CI 治理步骤静默坏掉（A-5，本次已修 f51c8d2）。
  走查 B（direction-loop 案例）实测：typed result 闭合且诚实、禁止动作有运行时强制层，
  未测得语义失败;模型自主选择 UNVERIFIED（B-3）。
- **阶段 1（本地诊断 JSON）: no-go**——前提"Coding Agent 卡在文本解析"未获证实;重启条件:未来实测卡在解析。
- **阶段 2（controller/节点认知评测重复）: go**——非因失败,而是 B-3 是走查留下的唯一开放证据问题;
  需人批预算与排期,另立 `todo-controller-evaluation-repetition`。
- **阶段 3（公共 tool 读诊断）: no-go**——未测得 typed result + legal_next_action 不足;维持现状,默认仍需人裁决。
- 路由类小修（A-2/A-3/A-4）已记录在证据表,属可另行排期的文档路由修复,未随本 todo 展开。

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
