# 提案：TUI 步进/调试轴（step-debug mode）——「一个图，第三种驱动模式」

> 类型: 方向提案（未拍板） | 生成: 2026-08-31（当晚讨论）
> 触发: 用户对 020 战役前提的质疑——"TUI 直接跑整个 langgraph 工作流，交互体验不正常，
> 是个半黑箱；是否可以让每个 NODE 支持 CLI 式的一步步调用，输入输出 schema 化存储，
> TUI 串起来做 trace/debug"。用户定位：建议与启发。
> 关联: [`tui-interactive-campaign.md`](tui-interactive-campaign.md)（020 战役计划 v4）、
> [`tui-interactive-campaign-progress.md`](tui-interactive-campaign-progress.md)（进度账本）、
> [`tui-interactive-campaign-review.md`](tui-interactive-campaign-review.md)（冻结）

## 0. 一句话结论

方向采纳：TUI 的第一性体验应从「陪跑整个 run + 等 interrupt」换成「**节点边界的步进/trace/debug**」。
但「每 Node 一个 CLI 入口」字面化**不采纳**——正确形态是**同一个图、同一个权威、第三种驱动模式
（step mode）**，基建已存在约七成，缺的是步进驱动器、节点边界 delta fact、TUI 卡片视图三件事。

## 1. 问题的事实基础（当晚代码核验）

1. **TUI 半黑箱的代码对应**：runtime 全程 `ainvoke`，全仓无 `astream`（`grep -rn astream src/` 零命中）；
   TUI 靠轮询 `diagnostics/events.jsonl`（`demo_tui.py::live_progress_lines`）。
2. **事件契约是闭集且无载荷**（`runtime/events.py:20-34`）：仅
   `phase/operation/outcome/work_id/attempt_id/code/count/…`——无输入输出 delta、无 capability 归因。
   即 plan v4 §5.3 记录的证据限制（"journal 不能归因 semantic-intake capability"）。
3. **节点调用逻辑全部住在 `_node_wrapper`**（`graph/builder.py:135-346`）：capability 注入校验、
   attempt_id 铸造、gate 评估、事件记录、budget handback。绕过 wrapper 逐个调用 node 函数 =
   假 trace（无 gate/事件/budget/checkpoint）= 第二执行权威，违反仓库单一权威铁律。
4. **图本身就是步进引擎，且已用了一半**：
   - checkpoint 逐超步持久化（`open_graph_checkpoint` → SQLite saver；compile 本就 per-action，
     `bundle_graph.py` 各入口都是 `builder.compile(checkpointer=saver)`）；
   - `ResearchState.execution_trace` 已记录已访问节点（`domain/state.py:195,849`，有界）；
   - `BundleGraphExecutor` 已有 4 个驱动入口：`start` / `resume`(Command) /
     `continue_run`(`ainvoke(None)` 孤儿恢复，REG-023) / **refinement 单任务推进**
     （`bundle_graph.py:433` 断言 `snapshot.tasks == ("topic_planning",)` 后 `ainvoke(None)`
     推进一段再 `_project`——「推进一步、投影一次」的生产先例）；
   - HITL1 interrupt 本来就是一种「节点边界暂停」，TUI 已会在边界上应答（AnswerRun/typed OPTION）。
5. **输入输出 schema 化流式存储已存在**：node「输入」= 上一个 checkpoint（typed ResearchState），
   「输出 delta」= 与下一个 checkpoint 的差；`aget_state_history` 可回放（SQLite saver 留存策略
   实施时验证）。回放器可纯读侧实现，对历史 bundle 同样有效。

## 2. 架构判断

| 用户提议成分 | 判定 | 形态 |
| --- | --- | --- |
| 每 Node 支持正常工作流模式 | ✅ 已存在 | 001-004 全自动 CLI = 连续模式 |
| 每 Node 有 CLI 式东西被 TUI 一步步调用 | ⚠️ 方向对，形态修正 | 不是「每 Node 一个 CLI 入口」，而是同一图的 **step mode**：compile 变体 `interrupt_after=LOGICAL_NODES`，每步 `ainvoke(None)` 推进一个节点边界 + `_project` |
| 输入输出 schema 化流式存储 | ✅ 已存在 | checkpoint 逐超步 = 流化存储；缺的只是投影 |
| TUI 串起来 = trace/debug 体验 | ✅ 采纳，是本提案核心 | progress 行 → node 卡片流；run/step 两挡 |
| 「调试模式」定位 | ✅ 与 TUI 产品定义一致 | README 本就定义 Demo TUI 为 contributor/operator visualizer；visualizer 的本分就是 step-through debugger |

**关键不变量**：交互契约一个不换（StartRun/AnswerRun/CancelRun/ContinueRun、typed OPTION、
HITL1 admission）。HITL1 interrupt 在 step 模型里降格为「需要人插手的那一步」。
换的只是**驱动粒度**（连续 → 可步进）与**观察面**（tick → 节点边界 delta）。

## 3. 缺口三件事（实施物）

1. **步进驱动器** `BundleGraphExecutor.step_run`：
   - 同一 recipe 的 compile 变体（`interrupt_after=LOGICAL_NODES`；compile per-action，无第二权威）；
   - 每步拿一次 `execution_exclusion`，步完即放——**步进会话绝不常驻锁**（用户离开 TUI 不许锁死 bundle）；
   - 每步后 `_project`（`sync_graph_progress` + pending 投影），返回步骤卡片数据。
2. **节点边界 delta fact**：带 capability/phase 归因的闭集新 fact 族（phase / node / route /
   changed-keys 摘要 / wall-time / failure_category）。恰好接住 plan v4 §5.3 推迟的
   「closed observation fact 做精确归因」需求——当初推迟是因为没有产品需求，现在有了。
   走 openspec change。
3. **TUI 视图**：node 卡片流（节点名 → 输入摘要 → 输出 delta → route → 耗时/预算 → failure
   category）+ run/step 切挡；interrupt 点应答继续走现有 AnswerRun/ContinueRun。

## 4. 最小落地路径

- **第 0 步（零契约原型，先做）**：纯读侧 trace projector——读历史 bundle 的 checkpoint +
  events.jsonl，回放渲染 per-node 卡片；先在 fixture 上验证 TUI 体验。不动任何契约，
  对既有 bundle（含 B1 两跑证据）立即有效。
- **第 1 步（openspec change）**：`step_run` + TUI run/step 切挡 + delta fact 契约。
  primary causal owner：runtime（executor）+ presentation adapter（TUI）按各自边界拆分，
  不把 route/profile admission 下放给 TUI。
- **第 2 步（可选，独立增量）**：连续模式的实时 delta 可用 `astream("updates")` 替换
  events.jsonl 轮询——**不要与 step mode 混入同一 change**。

## 5. 诚实边界（不解决什么）

1. 步进停在**节点边界**，不解决节点内部可视性（模型调用内部仍由 journal `model_tool` fact
   + C1 预算机制管）；但「节点名 + 每节点 wall-time + 预算」已足以让 BUG-062 那晚的
   16 分钟挂起**当场可见**（卡在哪个节点、预算还剩多少），而非事后考古。
2. work-unit 级粒度是另一维度（已有 work unit store / attempt 记录），本提案不覆盖。
3. 实施验证点：interrupt_after 编译变体与 refinement 路径 `snapshot.tasks` 断言的相互作用
   （步进与连续不得共用同一 config 混跑）；SQLite saver 的 checkpoint 历史留存策略。

## 6. 与 020 战役的关系（建议，待拍板）

- **B1 不作废**：压的是 HITL1 语义 intake 契约，两跑三 bug（062/063/064）→ C1/C2 两个归档
  change 的价值为真；剩一跑成本极低，网络恢复后照 runbook 收尾。用户感觉「思路错了」的部分，
  错在**把 TUI 的价值押在陪跑整个 run**，不在 HITL1 契约压测本身。
- **新轴建议命名 030（TUI step/debug）**：本提案即其 Stage 0 思考件；拍板后按仓库流程
  先做第 0 步原型，再立 openspec change。
- 020 的 B2/C 照旧条件式，不受本轴影响。

## 7. 决策点（待用户拍板）

- D-A：是否采纳「一个图 + step mode」替代「每 Node 独立 CLI」的形态判断。
- D-B：第 0 步零契约原型是否先做（建议：先做，fixture 上验证体验再谈 change）。
- D-C：030 轴是否立项；B1 第 3 跑是否照旧收尾（建议：照旧，两轴并行不互斥）。
