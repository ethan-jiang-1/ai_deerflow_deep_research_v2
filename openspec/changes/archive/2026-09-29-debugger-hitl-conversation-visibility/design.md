# Design

## Context

已核实的现状（读码 + live bundle 证据，2026-09-29）：

- hitl1 节点产出两路人机对话事实：(a) checkpoint interrupt 上的
  `HumanInputRequest.context`（schema-v1 机器 JSON：brief_summary /
  proposed_dimensions / missing_dimensions / accepted_rounds_remaining /
  instructions，`graph/nodes/hitl1/prompts.py`）与可选 `request.interaction`
  （`InteractionProjection`：subject + `feedback` + controls）；
  (b) durable state 的 `interaction_feedback`（`domain/state.py`，CONTROLLER
  last-write-wins）。关键不对称：**interaction 只在提案完整时挂上 interrupt**
  （`node.py` L1013），"提案不完整 → followup"场景（live 卡死的那次）节点回复
  **只在 durable state**。
- 共享体验 `ResearchRunExperience._hitl1_prompt`（`runtime/run_experience.py`
  L756-833）已把同一份 context 解析成 `PromptView`（goal/proposed_scope/missing/
  recognized/rounds/rejection_category/body_lines/answer_example），并优先消费
  `request.interaction`；普通模式 TUI 已经渲染这些字段（`系统: <feedback>` 等）。
- 调试链路完全没接：`runtime/debug_driver.py::_pending_request_view` 只投影
  request_id/phase/mode/title/context/options（interaction 被丢弃）；
  `scripts/demo_tui.py::_log_debug_action` 把 context 原文倾倒进日志（400 字截断）。
- 主 spec 既有约束：RED-001 禁止显示 machine brief JSON；LDD-001 要求快照携带
  "title and guidance"（实现未解析 guidance）；RED-014 要求停点说清所问与合法动作。
- BUG-078：`on_input_submitted` debug 纯文本分支无 composer 清空（所有 slash
  路径都有）；第二次 Enter 按新姿态路由 → 重复消费一轮答案或静默 advance。

## Goals / Non-Goals

**Goals:**

- 操作者在 HITL 停点不读机器 JSON 就能知道：问什么、上一条回答换来了什么回复、
  还剩几轮；最快通关输入（`确认`/`confirm`/`字段: 值`）被明示。
- context 解析只有一个权威（共享体验与调试驱动共用同一投影函数）。
- BUG-078 修复：debug 纯文本提交后 composer 清空，重复 Enter 无害化。
- 全部无头可验（fixture pilot + 驱动矩阵 + 单元），live 确认单列给操作者。

**Non-Goals:**

- 不改 hitl1 节点、context schema、`InteractionFeedback` 契约（只读消费）。
- 不改共享（非 debug）路径的任何渲染与提交行为——包括其 composer 卫生。
- 不做 accept 可见控件的 typed 提交、不做节点致动/自动确认（Stage 2，另案）。
- 不动 `deerflow/`。

## Decisions

1. **解析权威单一化**：从 `_hitl1_prompt` 提取模块级
   `project_hitl1_prompt(request, *, request_id) -> PromptView`（仍在
   `runtime/run_experience.py`，静态辅助函数随迁），`ResearchRunExperience`
   委托它。驱动投影调用同一函数。理由：schema 演进只改一处；备选（TUI 自己
   json.loads）违反"呈现层不解析机器载荷"的既有语义。
2. **契约扩展走加法**（change-guidance 的 additive 词汇规则）：
   `PendingRequestView` 增加两个默认 None 的可选字段——`prompt: PromptView | None`
   （复用共享类型，跨 domain 引入 `domain.run_experience`，无环）与
   `last_feedback: InteractionFeedback | None`（复用
   `domain.human_interaction` 类型）。不新增枚举值、不改既有字段含义；
   `context` 原样保留（携带≠显示）。
3. **feedback 双通道合并规则**：`request.interaction.feedback` 优先；interrupt 无
   interaction（或不带 feedback）时回退读 Bundle durable state 的
   `interaction_feedback`（驱动在构建快照时已有 state 读取路径；构造
   `InteractionFeedback(kind, message)` 时按其校验失败即放弃——不造权威）。
   该规则写进 LDD-006 场景。
4. **渲染**：`_log_debug_action` 的 awaiting_hitl 分支改为——首行保留
   `→ 等待 {node} 输入（{mode}）：{title}`；有 card 时渲染 goal/proposed_scope/
   missing/rounds/guidance/example/选项（ bounded 行数与既有 400 字预算同级），
   无 card 时渲染 title/mode + `（节点上下文为非公开 schema，未解析）` 有界注记；
   `last_feedback` 存在时渲染 `hitl1 回复: <message>`。去重键仍为
   `hitl:{request_id}`（同请求不重写）。**删除原始 context 倾倒**。
5. **消费反馈行**：`_render_debug_result` 在 answer 提交后、新姿态仍为
   awaiting_hitl 且下一节点含同一 HITL 节点时，写
   `↩ 回答已消费 · 未被接受 · 剩余 N 轮`（N 缺省时省略该段）。判定用快照事实
   （posture + pending_request + prompt.accepted_rounds_remaining），不做推断。
6. **BUG-078 修复**：debug 纯文本分支在 echo 后加
   `composer.value = ""`；不额外加去重守卫（cursor/command_id 幂等已在驱动层；
   清空后第二次 Enter 落入既定空提交行为：awaiting_hitl 打印等待提示，
   paused 边界为 runbook-030 节奏）。
7. **REQ 登记**：新 req id `LDD-006`、`RED-015` 在 apply 时写入
   `openspec/governance/req-registry.yaml`（一行式条目，跟 RED-014/LDD-005 同格式）。

## Risks / Trade-offs

- **fixture 组合测不到 feedback 全链**：fixture hitl1 的 context 是纯文本（非
  schema），无 interaction。缓解：feedback 渲染用"合成 PendingRequestView 直调
  `_log_debug_action`"的无头测试锁（mount 上下文内直调，确定性）；驱动层投影
  （含 state 回退）在 `test_debug_driver_matrix.py` 用真图+改写 state 断言。
  真模型下的 live 确认标注为操作者步骤（交付清单）。
- **`PromptView` 跨 domain 引入轻微耦合**：两个 domain 契约互不 import 对方
  （debug_driving → run_experience 单向），无环；比"在驱动里重造卡片类型"便宜。
- **回退读 state 的一致性窗口**：feedback 与 interrupt 可能短暂错代（state 先写
  interrupt 后发）。投影只展示"最近一次回复"，语义上可接受；不做跨源一致性断言。
- **消费行依赖"同节点再停"判定**：hitl1 多轮重问天然满足；若未来节点在 answer
  后停在*另一个* HITL 节点，不渲染消费行（诚实：那是新请求，不是拒绝）。
