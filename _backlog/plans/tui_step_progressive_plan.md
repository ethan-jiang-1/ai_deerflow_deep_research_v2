# TUI 步进轴递进计划

> 类型: 递进执行计划 | 创建: 2026-08-31 | plans 索引: [README.md](README.md)（本文件是当前唯一活跃 plan）
> 设计权威: [archive/tui-interactive-campaign.md](archive/tui-interactive-campaign.md) v5 §10
> 用法: 推进顺序 = 拍板门 → 当前 change；完成一项勾一项，§L 追加一行；验收全绿才进下一个。
> REVIEW 指引: 重点审三处——体验定义（REPL 双面是否是你要的）、C3/C4 验收
> （可判定吗）、拍板门两项（D6/D7）。通过后 openspec-propose C3 开工。
> 体验总纲（2026-08-31 用户定调）: **REPL 双面**——叙述流「走一步啰嗦一堆但一直在跑」
> + 操作面「程序调试式 step」。同一套路两个挡位，不是两套机制。

## 0. 背景与决策链（为什么做这件事——新人从这里重建全程）

1. **起点（2026-08-31 用户批评）**：020 的 TUI 直接跑整个 langgraph 工作流，体验是
   「陪跑整个 run + 等 interrupt」，对人是半黑箱（原话与论证 = archive 战役 v5 §10 触发引语）。
2. **形态修正**：最初设想的「每个 NODE 一个 CLI 被 TUI 逐步调用」被否——节点调用逻辑
   （capability 注入 / attempt 铸造 / gate 评估 / 事件 / budget）全在唯一 `_node_wrapper`
   （`graph/builder.py`），绕过它 = 假 trace + 第二执行权威。正确形态 = **一个图 +
   第三种驱动模式（step mode）**（= D6；论证全文 = archive §10.1）。
3. **研究轨迹**：① 拓扑盘点——11 节点 / 40 typed 边 / 22 route / 4 自环 + 6 类回边、
   7 自然段、四层观察谱系（archive §10.2）——「只有一个观察面」不成立；② checkpoint
   预核——39 个现存 bundle 的逐超步历史在盘上（§附录 A）；③ 实验 E1–E4（§附录 B）——
   回放卡片流实证、BUG-062 可见性验收成立。
4. **体验定调（用户）**：REPL 双面——叙述流「走一步啰嗦一堆但一直在跑」+ 操作面
   「程序调试式 step」；同一套路两个挡位，不是两套机制（§1）。
5. **治理定调（用户）**：承载代码/契约的推进一律走 openspec change 阶梯
   （C3 → C4，流程对齐 020 战役 C1/C2 纪律）——见「推进方式」。
6. **文件演化与取代声明**：独立提案文件 `tui-step-debug-axis.md` 曾短暂存在，为避免
   双套路并入 archive 战役 v5 §10 后删除；本文件是 D6–D8 提案的**执行定稿**——
   archive §10.6 的 D7 原表述（先独立原型再 change）由本文件拍板门的 D7
   （两枚 change 拆分、原型精神收进 C3 首个 spike）**取代**。

## 1. 体验定义（不变量，全轴共同遵守）

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
- C3/C4 全程零凭证（代码 + fixture 测试即可验收）；real 验证跑与 B1 并行线共享网络前置；
- **渐进修订条款（边干边明白）**：每个实验的结论记 §L；结论与本计划冲突时，允许修订
  **未开工**的后续任务序（含 change 载荷切分）；已归档 change 不回改。

## Stage 0 — 拍板门 ⬜

- [ ] **D6 形态**: 一个图 + step mode（弃「每 Node 独立 CLI」）——建议: 通过
- [ ] **D7 拆分与顺序**: 两枚 change——C3 观察叙述先行、C4 步进驱动后行
  （原「零契约原型先行」的精神收进 C3 首个 spike 任务）——建议: 通过
- 门规则: D6 拒 → 轴关闭（本文件归档，TUI 维持现状）；D6 过 D7 拒 → 单枚大 change
  合并推进（不推荐：验收面过大，返工代价高）

## C3 — `add-tui-trace-observation`（观察叙述面）⬜

- [ ] spike（apply 首任务）✅ E1–E3 已完成（2026-08-31，见 §实验清单纪要）：
  `scripts/experiments/tui_trace.py` 草稿已落、4 类样本回放全过——apply 时按测试门固化
- [ ] delta fact 契约：节点边界闭集 fact（`node/seq/route/duration_ms/input_summary/
  output_delta/failure_category?`，带 capability/phase 归因）——v4 §5.3 推迟项落地
- [ ] `tui_trace.py` 固化为交付物（serde 边界同 runtime，`_config` 同构；只读不动 `src/` 契约）
- [ ] TUI 叙述流（run 挡）：卡片自动连放 + 内层叙述行跟随 work unit/attempt/模型调用
  计数（presentation adapter = `scripts/demo_tui.py`）；含 E5 手感调参（结论记 §L）
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
- [ ] real recipe 接线 + 实施验证: E4 运行时部分（`ainvoke(None)` 逐格推进、与
  hitl1 GraphInterrupt 共存、与 refinement `snapshot.tasks` 断言互作用——
  步进/连续不共用同一 config 混跑）；编译层已预核通过
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
  （`verify_b1_pass.py` 已就绪）→ 记 handoff-020；撞茬走 `../bugs/` 流程（编号权威 BUG-067——BUG-066 已被架构检查器漂移占用，见 §L）
- [ ] B2 CHOICE 专项（条件式：typed OPTION 修复已归档；战后仍决定覆盖才跑）
- [ ] C Gateway observer（可选：预写观察问题清单，否则直接关闭）
- [ ] 战役收口：证据折叠 runbook-020 附录、阶梯表状态、handoff-020 删除
  → 收口后按治理把 `archive/` 三文件整组 `git mv` 进 `../_done/_closed_plans/`
  （plan ID 从 CLS-058 起）并同步 README 索引

## 附录 A — 技术 grounding（2026-08-31 预核）

| 断言 | 证据 |
| --- | --- |
| 逐超步 checkpoint 历史已持久化 | 现存 39 个 bundle 的 `graph.sqlite` 均含逐超步 checkpoints、`checkpoint_ns=''`（位于 `.deep-research-demo-runs/workspace/**/b_*/`）——「每 Node 输入输出流化存储」已经在盘上；帧数随 run 复杂度 11–15 不等（首测 6 包各 11 行，实验扩样见附录 B 纪要） |
| checkpoint 位置与打开方式 | `bundle_lifecycle.py:71` `_GRAPH_FILENAME = "graph.sqlite"`（`private_root(bundle)` 下）；读侧 = `AsyncSqliteSaver.from_conn_string` + `saver.serde = build_deep_research_checkpoint_serde()`（`runtime/checkpoint.py:112-128`，与 runtime 同一 msgpack 类型边界） |
| 回放 API 可用 | `CompiledStateGraph.aget_state_history` 在装好的 langgraph 已确认存在；`config` 与 `BundleGraphExecutor._config` 同构（`thread_id=<bundle_id>, checkpoint_ns=''`） |
| 事件对齐 | 每超步的耗时/结果可由 checkpoint 自带 `created_at` 差分得出；`diagnostics/events.jsonl`（node fact 含 attempt_id）留给 attempt 级细节；TUI 现已在读该文件 |
| 未决项（收窄） | `interrupt_after` 变体的**编译**已通过（11 节点全列出，2026-08-31）；**运行时行为**（`ainvoke(None)` 逐格推进、与 hitl1 内部 GraphInterrupt 共存、与 refinement `snapshot.tasks` 断言互作用）= 实验 E4，C4 propose 前完成 |

## 附录 B — 实验清单（spikes——边干边明白）

| # | 实验 | 要回答的问题 | 方法 | 归属 | 状态 |
| --- | --- | --- | --- | --- | --- |
| E1 | 回放数据形状 | `aget_state_history` 能否出 (step, node, state)？差分能否约简成卡片？ | `scripts/experiments/tui_trace.py`（只读尖刺）对 4 类样本回放 | C3 spike 首任务 | ✅ 2026-08-31 |
| E2 | 耗时来源 | 节点耗时靠 events 对齐还是 checkpoint 自带 ts？ | 同上对照 | C3 spike | ✅ 每帧有 `created_at`，相邻差分即耗时；events 留给 attempt 级细节 |
| E3 | 失败/挂起可见性 | blocked/suspended 包能否出「走到哪 + 失败类别」？ | BUG-062 real 包 + fixture suspended 包 | C3 spike | ✅ 见纪要 |
| E4 | step 变体运行时 | `ainvoke(None)` 逐格推进？与 hitl1 GraphInterrupt 共存？与 refinement 断言互作用？ | fixture recipe + memory checkpointer 逐格脚本 | C4 propose 前置 spike | 🟡 编译层已过；运行时未决 |
| E5 | 叙述流手感 | 卡片密度/噪声/节奏（REPL 手感） | fixture TUI 实跑调参 | C3 TUI 任务 | ⬜ 迭代性质，结论进 §L |

**实验纪要（E1–E3，2026-08-31）**：metadata.`writes` 在当前 langgraph 为 `None`
→ 卡片 delta 用相邻超步差分；超步几何 = 起点帧 + N 边界帧 + 终态帧
（fixture completed **11 帧/9 边界**、real completed 15 帧、real blocked 12 帧、
suspended 4 帧）；`scripts/experiments/tui_trace.py` 草稿已落（零契约只读，C3 apply 按测试门固化）。

## L. 进展记录（append-only）

| 日期 | Stage | 事项 | 结果 |
| --- | --- | --- | --- |
| 2026-08-31 | — | 文件创建；体验定义定调（REPL 双面：叙述流 + 操作面） | 📋 Stage 0 待拍板 |
| 2026-08-31 | — | Review 就绪化：技术 grounding 预核全绿——39 个现存 bundle 的 graph.sqlite 各含 11 行逐超步 checkpoints、`aget_state_history` 可用、serde 边界与 `_config` 同构确认；留存策略验证项关闭 | 📋 Stage 0 待拍板（D6/D7） |
| 2026-08-31 | — | 用户定调：按 openspec change 推进——阶梯重构为 **C3 `add-tui-trace-observation`（观察叙述面）→ C4 `add-tui-step-driving`（步进驱动面）→ real 验证跑（无 change）**；原 Stage 1–3 折叠进 change 任务序（先尖刺后契约），流程对齐 C1/C2 纪律（propose→polish→apply→verify→archive） | 📋 Stage 0 待拍板（D6/D7） |
| 2026-08-31 | E1–E3 | 实验 3 枚完成（`scripts/experiments/tui_trace.py` 只读尖刺）：4 类样本回放全过——fixture completed 11 帧/9 边界卡、real completed 15 帧、**BUG-062 real blocked 12 帧（wave2 16min 单卡可见、blocked 原因键在终卡 Δ）**、suspended 4 帧（HITL 停点 + 等待内容可读）；耗时 = 相邻 checkpoint ts 差（metadata.writes 为 None → 差分法）；E4 编译层通过、运行时部分留 C4 spike | ✅ C3 数据形状实证成立；差分法替代 events 对齐，卡片字段闭集可定稿 |
| 2026-08-31 | — | `deep_research_harness/scripts/` 分层重组：根 = 常态入口/运维 + README 导读、`checks/` = verify 校验家族 9 文件、`experiments/` = 实验尖刺（tui_trace.py 迁入）；引用面同步 Makefile ×8 + required-paths.toml ×2 + 13 测试 import + docs；bootstrap parents[1]→[2]；结构注册表不枚举 scripts/，无需立 change | ✅ 门禁全绿（fast 2674 + integration 302[4 skip] + workflow 35 + ruff check/format；wheel-exclusion 一测因沙箱禁 uv 缓存环境性未跑，与重组无关）；顺手登记 **BUG-066**（架构检查器干净树即红，存量 ignored_paths 漂移，修复 = 单行 registry 同步走微 change） |
| 2026-08-31 | — | openspec 微 change `sync-structure-registry-ignore-entries` 闭环：propose → polish（plan gate 四组件全绿 + reservation PRS-022 映射 task 1.2）→ apply（registry `[ignored_paths]` +`.uv-cache/`、req-registry 登记 PRS-022、checker 干净树 exit 0）→ delta 同步主 spec（PRS-022 requirement + header）→ archive `2026-08-31-sync-structure-registry-ignore-entries`；BUG-066 关闭迁移 `_done/_fixed_bugs/`（编号权威 → BUG-067） | ✅ 治理门恢复绿，change 收口 |
