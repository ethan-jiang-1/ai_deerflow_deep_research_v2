# Proposal

## Why

第一次真实 live 窗口（bundle `b_EHlhgNio…`，2026-09-29）实证：调试工作台把 HITL 停点
渲染成截断的机器 context JSON，节点对操作者上一条回答的真实回复（`interaction_feedback`
——"你输入的是「一个一个节点调，怎么个调法」，我还没能把它理解成研究配置。可以…输入
「确认」…"）只存在于 Bundle 状态，工作台零渲染。操作者因此认为"没有对话功能"，把元
问题当答案连烧三轮，flow 永远停在 hitl1。同时 debug 纯文本提交后 composer 不清空
（BUG-078），第二次 Enter 会把同一段文字再消费一轮或静默推进一个节点。共享体验
（`ResearchRunExperience._hitl1_prompt` → `PromptView`）早已解析同一份 context schema
并渲染 goal/missing/剩余轮次/feedback——调试工作台没有接上这套投影。

## What Changes

- 提取 hitl1 context → `PromptView` 的解析为单一投影函数（`ResearchRunExperience`
  委托它，消除双实现风险），作为该 context schema 的唯一解析权威。
- `PendingRequestView`（`domain/debug_driving.py`）扩展两个字段：`prompt`
  （复用共享 `PromptView` 类型：heading/goal/proposed_scope/missing/剩余轮次/指引/
  示例/选项）与 `last_feedback`（类型化 `InteractionFeedback | None`：优先取 checkpoint
  interrupt 上的 `request.interaction.feedback`，回退读 Bundle durable state 的
  `interaction_feedback`——覆盖"提案不完整→followup"场景，此时节点回复只在 state）。
- 驱动 `_pending_request_view` 填充上述投影（`runtime/debug_driver.py`）。
- 工作台 HITL 停点渲染改为**类型化卡片**：`→ 等待 …` 之后渲染 goal/proposed_scope/
  missing/剩余轮次/建议输入，**不再倾倒原始 context JSON**（主 spec 本就禁止显示
  machine brief JSON）。
- 回答消费反馈：answer 后姿态仍回到同节点 `awaiting_hitl` 时，明示
  `↩ 回答已消费 · 未被接受 · 剩余 N 轮` + `hitl1 回复: <feedback.message>`（有
  feedback 才渲染该行；N 缺省时省略）。
- BUG-078：debug 纯文本提交后清空 composer（与所有 slash 路径一致），第二次 Enter
  变为无害空提交。
- `/help` 与 HITL 卡片明示最快通关输入（`确认` / `confirm` / `字段: 值` 修订格式）。

## Change Focus

- **Primary module / causal owner**: 工作台 HITL 停点的呈现投影——
  `deep_research_harness/scripts/demo_tui.py`（debug 渲染路径）为最小呈现 owner；
  携带数据的类型契约归 `domain/debug_driving.py`（`PendingRequestView`）。
- **Seam classification**: `wiring`——不新增模型角色、提示、准入或 authority；把
  已有类型化事实（`PromptView` 投影、`InteractionFeedback`、durable state 的
  `interaction_feedback`）接到既有面板，并修复一条提交路径卫生缺陷。
- **Question**: 操作者在 HITL 停点能否不读机器 JSON 就看到：节点在问什么、对自己
  上一条回答回了什么、还剩几轮？提交一条文本后，重复 Enter 是否不再造成第二次
  答案消费或静默推进？
- **Necessary adjacent/external contracts**:
  - `local-workflow-debug-driving`（LDD-001）：快照的 pending 投影从"title+原始
    context"升级为"title+已解析 prompt 卡片+节点最近反馈"，回答其"操作者能否看到
    所问与所答"的问题。
  - `research-demo-tui`（RED-014）：HITL 停点渲染要求从"title/mode/context/options"
    收紧为"类型化卡片、节点反馈、消费结果，且不倾倒机器 JSON"。
  - `human-interaction-contract`（只读消费）：`InteractionFeedback`/context schema
    v1 不改，仅作为被消费方。
- **Evidence seam**: 无头 TUI pilot（fixture 调试器：卡片渲染、消费行、composer
  清空）+ 驱动矩阵/单元（投影字段、feedback 双通道）+ 现有 `make tui-journey`、
  `make debugger-proof`、`UV_OFFLINE=1 make verify`。真实模型下的 live 确认属
  操作者窗口（交付清单单列）。
- **Not in scope**: Stage 2 节点致动（重跑节点、强制 HITL 通过、drive 自动确认
  语义——另行提案）；debug 工作台的 accept 可见控件提交（`accept_suggestion` 走
  typed 控件而非文字，属 Stage 2 连带）；非 debug 共享路径的 composer 卫生；
  `deerflow/` gitlink（只读框架，不改不源览）。
- **Triggered review policies**: `none: 纯投影与提交卫生——无认知面变化、无新
  runtime authority、无工作流结果语义变化；投影与诊断不成为 lifecycle authority。`

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `research-demo-tui`: RED-014 的 HITL 停点渲染要求修订——停点必须渲染类型化
  prompt 卡片与节点反馈/消费结果，不得倾倒机器 context JSON；提交卫生（composer
  清空）成为工作台要求。
- `local-workflow-debug-driving`: LDD-001 的快照投影要求修订——pending 投影必须
  携带已解析的 prompt 卡片与节点最近反馈（interaction 优先、durable state 回退）。

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/debug_driving.py`
  （`PendingRequestView` 扩展两个字段，默认 None——向后兼容）
- `deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py`
  （提取共享投影函数，`_hitl1_prompt` 委托）
- `deep_research_harness/src/deerflow_deep_research/runtime/debug_driver.py`
  （`_pending_request_view` 填充投影与 state 回退读取）
- `deep_research_harness/scripts/demo_tui.py`（停点卡片渲染、消费反馈行、
  composer 清空、/help 文案）
- 测试：`tests/integration/test_demo_tui.py`（pilot 红绿）、
  `tests/integration/test_debug_driver_matrix.py`（投影断言）、
  run_experience 既有测试保持绿（提取不语义变更）
- 无依赖、无 breaking；`deerflow/` 不动。
