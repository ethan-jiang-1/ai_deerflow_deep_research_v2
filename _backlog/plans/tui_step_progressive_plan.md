# TUI 步进轴递进计划

> 类型: 递进执行计划 | 创建: 2026-08-31 | plans 索引: [README.md](README.md)（本文件是当前唯一活跃 plan）
> 设计权威: [archive/tui-interactive-campaign.md](archive/tui-interactive-campaign.md) v5 §10
> 用法: 只推进「当前 Stage」；完成一项勾一项，§L 追加一行；本 Stage 全绿才进下一 Stage。
> REVIEW 指引: 重点审三处——§0 体验定义（REPL 双面是否是你要的）、C3/C4 验收
> （可判定吗）、Stage 0 两项拍板（D6/D7）。通过后 openspec-propose C3 开工。
> 体验总纲（2026-08-31 用户定调）: **REPL 双面**——叙述流「走一步啰嗦一堆但一直在跑」
> + 操作面「程序调试式 step」。同一套路两个挡位，不是两套机制。

## 0. 体验定义（不变量，所有 Stage 共同遵守）

- **叙述流**: 每个节点边界一张卡（节点名 → 输入摘要 → 输出 delta → route →
  耗时/预算 → failure category）；wave 内层 work unit / attempt / 模型调用以
  只读叙述行跟随，不设暂停点；composer 常驻（沿用 020 TUI 的 composer +
  `/ls` `/cat` `/inspect`，这就是 REPL 的种子）。
- **操作面**（任意边界可抓控制）:

  | 操作 | 语义 | 量级 |
  | --- | --- | --- |
  | step | 推进一个节点边界后停 | 一次 run **9–20** 个停点（11 节点 / 40 边 / 4 自环 + 6 类回边） |
  | continue | 跑到下一个边界 | 同上 |
  | run | 自动连放到终态 | 全程 |
  | inspect | 当前边界卡片 + 历史边界 checkpoint 回看 | 每边界 + 全部历史 |
  | answer | HITL1 interrupt 应答（唯一需要人的步） | 每 run 1–3 轮 |
  | cancel / attach | 任意边界取消 / 进程死后恢复 | 全程（attach = C2 已落地） |

- **量级底线**: 最短 happy path 跨 9 个边界，真实 run 典型 10–20，加内层叙述行
  一次 run 几十条——不存在「只有一个观察面」。
- **契约红线**: StartRun / AnswerRun / CancelRun / ContinueRun、typed OPTION、
  HITL1 admission 一个不换；TUI 不获得 route/profile admission 权。

## 技术 grounding（2026-08-31 预核，全部实锤）

| 断言 | 证据 |
| --- | --- |
| 逐超步 checkpoint 历史已持久化 | 现存 39 个 bundle 的 `graph.sqlite` **各含 11 行 checkpoints**、`checkpoint_ns=''`（含 fixture 与 B1 real 证据包，位于 `.deep-research-demo-runs/workspace/**/b_*/`）——「每 Node 输入输出流化存储」已经在盘上 |
| checkpoint 位置与打开方式 | `bundle_lifecycle.py:71` `_GRAPH_FILENAME = "graph.sqlite"`（`private_root(bundle)` 下）；读侧 = `AsyncSqliteSaver.from_conn_string` + `saver.serde = build_deep_research_checkpoint_serde()`（`runtime/checkpoint.py:112-128`，与 runtime 同一 msgpack 类型边界） |
| 回放 API 可用 | `CompiledStateGraph.aget_state_history` 在装好的 langgraph 已确认存在；`config` 与 `BundleGraphExecutor._config` 同构（`thread_id=<bundle_id>, checkpoint_ns=''`） |
| 事件对齐 | 每超步的耗时/结果用 `diagnostics/events.jsonl` 对齐（node started/completed fact 已含 attempt_id）；TUI 现已在读该文件 |
| 未决项（唯一） | `interrupt_after` 编译变体与 refinement `snapshot.tasks` 断言的相互作用——Stage 4 实施时验证；Step 1–3 只读侧，不触及 |

## 推进方式：openspec change 阶梯（2026-08-31 用户定调）

一切承载代码/契约的推进都走 openspec change，流程与 020 战役 C1/C2 同一纪律：
**propose（四件套）→ polish（apply readiness 硬化）→ apply（TDD 红→绿）→
`UV_OFFLINE=1 make verify` 全绿 → archive（delta 同步主 spec）**。
新契约需求 ID 在 propose 时登记 req-registry（RED/WSN 先例）。

| # | change | 载荷层 | 前置 |
| --- | --- | --- | --- |
| C3 | `add-tui-trace-observation` | 观察叙述面：runtime delta fact + 读侧回放 + TUI run 挡 | Stage 0 两拍板 |
| C4 | `add-tui-step-driving` | 步进驱动面：step_run + TUI 挡位 + real 接线 | C3 归档且叙述流 fixture 验收过 |
| — | real 验证跑（无 change） | 操作跑次（同 B1 性质） | C4 归档 + 网络 |

门规则（统一）：

- 每个 change 只有「验收全绿 → archive → 进下一个」与「⛔ 回 Stage 0 关轴/收缩」两种出口；
- C3 内部任务序**先尖刺后契约**——原「零契约原型先行」的精神收进 C3 第一个任务，
  体验风险在写 delta fact 契约之前消化；
- C3/C4 全程零凭证（代码 + fixture 测试即可验收）；real 验证跑与 B1 并行线共享网络前置。

## Stage 0 — 拍板门 ⬜

- [ ] **D6 形态**: 一个图 + step mode（弃「每 Node 独立 CLI」）——建议: 通过
- [ ] **D7 拆分与顺序**: 两枚 change——C3 观察叙述先行、C4 步进驱动后行
  （原「零契约原型先行」的精神收进 C3 首个 spike 任务）——建议: 通过
- 门规则: D6 拒 → 轴关闭（本文件归档，TUI 维持现状）；D6 过 D7 拒 → 单枚大 change
  合并推进（不推荐：验收面过大，返工代价高）

## C3 — `add-tui-trace-observation`（观察叙述面）⬜

- [ ] spike（apply 首任务）：`scripts/tui_trace.py` 读侧回放尖刺——对 fixture ×2 +
  real ×1（39 个现存 bundle 直接当样本）出卡片流，先验证数据形状再写契约
- [ ] delta fact 契约：节点边界闭集 fact（`node/seq/route/duration_ms/input_summary/
  output_delta/failure_category?`，带 capability/phase 归因）——v4 §5.3 推迟项落地
- [ ] `tui_trace.py` 固化为交付物（serde 边界同 runtime，`_config` 同构；只读不动 `src/` 契约）
- [ ] TUI 叙述流（run 挡）：卡片自动连放 + 内层叙述行跟随 work unit/attempt/模型调用
  计数（presentation adapter = `scripts/demo_tui.py`）
- 验收: `make demo-tui-fixture` 全程叙述流可读、composer 可用；3 bundle 回放全过；
  失败 bundle 出「走到哪 + 失败类别」截断卡片流（BUG-062 可见性验收）；
  verify 全绿；change 闭环归档
- specs delta 落点（propose 时定）: 运行观察投影（RTO 族）+ `research-demo-tui`
- ⛔ 出口: 叙述流体验不成立且不可收敛 → 回 Stage 0（可收缩为纯读侧工具 + fact，
  TUI 部分撤销）

## C4 — `add-tui-step-driving`（步进驱动面）⬜

- [ ] `BundleGraphExecutor.step_run`：interrupt_after 编译变体（同 recipe，非第二权威）
  + 每步拿放 `execution_exclusion`（步进会话绝不常驻锁）
- [ ] TUI 挡位: step / continue / run / inspect（composer 常驻；answer 仍走既有
  AnswerRun typed 契约）
- [ ] real recipe 接线 + 实施验证: interrupt_after 变体与 refinement `snapshot.tasks`
  断言的相互作用（步进/连续不共用同一 config 混跑）
- 验收: fixture 一手 step 走完 ≥9 边界、中途 inspect 历史卡片、可随时切回 run；
  verify 全绿；change 闭环归档
- ⛔ 出口: 体验不成立 → 回 Stage 0 关轴

## 终线 — real 验证跑（操作跑次，无 change）⬜

- [ ] 真实模型 + 步进观察跑一次（固定问题；叙述流全程 + 关键边界 step 停看）
- [ ] 证据: exact bundle + 卡片流与 events/checkpoint 一致性抽查
- [ ] 定位声明: 验**体验**；B1 收尾（§并行线）验 HITL1 契约——互补不混同

## 并行线（020 战役遗留，与本阶梯并行推进）

- [ ] **B1 第 3 跑收尾**（等网络恢复）：`make demo-tui-embedded-smoke` 真人实跑
  （操作单 = `../_local_demo/runbook-020-tui-manual.md` §3）；PASS 7 条核对
  （`verify_b1_pass.py` 已就绪）→ 记 handoff-020；撞茬走 `../bugs/` 流程（编号权威 BUG-066）
- [ ] B2 CHOICE 专项（条件式：typed OPTION 修复已归档；战后仍决定覆盖才跑）
- [ ] C Gateway observer（可选：预写观察问题清单，否则直接关闭）
- [ ] 战役收口：证据折叠 runbook-020 附录、阶梯表状态、handoff-020 删除
  → 收口后按治理把 `archive/` 三文件整组 `git mv` 进 `../_done/_closed_plans/`
  （plan ID 从 CLS-058 起）并同步 README 索引

## L. 进展记录（append-only）

| 日期 | Stage | 事项 | 结果 |
| --- | --- | --- | --- |
| 2026-08-31 | — | 文件创建；体验定义定调（REPL 双面：叙述流 + 操作面） | 📋 Stage 0 待拍板 |
| 2026-08-31 | — | Review 就绪化：技术 grounding 预核全绿——39 个现存 bundle 的 graph.sqlite 各含 11 行逐超步 checkpoints、`aget_state_history` 可用、serde 边界与 `_config` 同构确认；留存策略验证项关闭 | 📋 Stage 0 待拍板（D6/D7） |
| 2026-08-31 | — | 用户定调：按 openspec change 推进——阶梯重构为 **C3 `add-tui-trace-observation`（观察叙述面）→ C4 `add-tui-step-driving`（步进驱动面）→ real 验证跑（无 change）**；原 Stage 1–3 折叠进 change 任务序（先尖刺后契约），流程对齐 C1/C2 纪律（propose→polish→apply→verify→archive） | 📋 Stage 0 待拍板（D6/D7） |
