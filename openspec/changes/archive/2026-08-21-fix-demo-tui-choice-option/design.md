# Design: fix-demo-tui-choice-option

## Context

见 `proposal.md` Why（BUG-060）。当前 `scripts/demo_tui.py` 的交互面：

- `on_input_submitted()`（:567-577）：composer 输入在 `Ready` 时派发
  `StartRun(question)`，在 `AwaitingInput` 时一律派发默认 text
  `AnswerRun(value=...)`；
- `_render_view()`（:513-517）：仅当当前 prompt 的 `visible_controls` 含
  `accept_current_proposal` 时显示 "Start proposal" 按钮（派发
  `SelectControlRun`）；
- `render_run_update()` 的 AwaitingInput 分支（:275-290）**已投影
  `options=tuple(option.id ...)`，CHOICE 轮 placeholder 即 "Choose an
  advertised option ID"**，detail 行渲染 `option.id: consequence`——view 层
  已向用户广告"输入选项 ID"交互，dispatch 层从未兑现（BUG-060 全貌）；
- shared boundary（`runtime/run_experience.py::_prepare_intent`，:343-358）：
  对 hitl1 CHOICE prompt 强制 `response_kind=option` 且 `option_id` ∈ 当前
  广告选项（`option.id.value`），text 一律 `hitl1_language_answer_requires_option`
  拒绝。

约束：spec RED-003/RED-007 已划定 TUI 不得自建 response envelope、不得自行
判定 phase；`human-interaction-contract` 与 `_prepare_intent` 校验已正确，
本 change 不动它们。

## Goals / Non-Goals

**Goals:**

- CHOICE prompt 在 fixture/embedded-smoke TUI 中可被合法作答（选项渲染 +
  typed OPTION 派发 + shared admission 接受）；
- 确定性回归覆盖（fixture 路径，无真实模型）。

**Non-Goals:**

- 不改 `run_experience.py` / hitl1 admission / `human-interaction-contract`；
- 不给 Gateway observer 模式新增本地选项派发（其"只转发输入文本或当前
  显示的选中 control 值"语义维持现状）；
- 不做 CHOICE prompt 的自由文本→option 猜测映射（不做 NLU）。

## Decisions

**D1：两条等价派发路径，同一 typed OPTION
——`AnswerRun(value=<广告选项 id>, response_kind="option", option_id=<广告选项 id>)`。**
(a) 选项按钮：动态生成，点击即派发；(b) composer 精确匹配：CHOICE 轮当前时，
提交文本与某广告选项 id **确定性字符串相等**则派发该 id 的 typed OPTION
（兑现现有 placeholder "Choose an advertised option ID" 已广告的键盘路径）。
typed contract（`domain/run_experience.py::AnswerRun`）强制 option 类应答
`value == option_id`（`option_answer_requires_matching_option_id`），且
`option_id` 当前为 `Literal["zh", "en"]`——按钮 label 可用人类可读文本，
但派发的 value/option_id 必须同一广告 id。
备选 A：把选项当 visible_controls 提交（`SelectControlRun`）——不选：control
与 option 是 shared contract 里两个不同的 typed 语义（`_prepare_intent` 对
action/option 各自校验），混用等于让 TUI 伪造 shared 语义。备选 B：语义/短语
式匹配（NLU、acceptance phrase 类别名）——不选：RED-007 禁止 text aliases
的精神；确定性 id 相等不在其列（比对的是 shared advertisement，非语义猜测）。

**D2：HITL1 CHOICE prompt 当前时，composer 非 exact-match 文本不派发。**
行为：hitl1 language CHOICE 轮的作答只有 D1 两条路径；不匹配任何广告 id 的
提交不构造任何 `AnswerRun`（防呆：从 UI 源头杜绝
`hitl1_language_answer_requires_option` 的必然拒绝）。**范围只限 hitl1
CHOICE**：hitl2 CHOICE 的自由文本转发是受保护的现有行为（现有测试
`test_tui_forwards_unadvertised_choice_to_graph_owned_validation` +
`AnswerRun.option_id: Literal["zh","en"]` 装不下 hitl2 选项 id），维持不变。
备选：照旧派发让 boundary 拒绝——不选：把已知必败路径留给
用户撞是 presentation 缺陷本身（BUG-060 的一半症状就是它）。

**D3：选项按钮组在 compose() 按 typed contract 的闭集
（`SupportedLanguageOption`，zh/en）静态生成，`_render_view()` 每帧按当前
广告选项切可见性与 label。**
Textual 的 `mount` 是异步的，同步渲染路径不能动态挂载；静态树 + 每帧
可见性重算与 accept/cancel 按钮同一渲染周期管理，可观察行为与"动态
挂载/卸载"等价且无异步挂载风险。判定"当前是 hitl1 CHOICE 轮"读的是
shared prompt 的 mode/phase 字段（RED-003，同文件 placeholder 已按
`prompt.mode` 分支的先例）；prompt 离开 hitl1 CHOICE 时按钮组隐藏。

**D4：测试走 fixture CHOICE 路径的 shared experience 集成测试
（`tests/integration/test_demo_tui.py` 现有 Pilot 模式）。**
需要一个 fixture 图能到达 CHOICE prompt 的确定性路径（现有 fixture HITL1
adapter 发 TEXT interrupt；若 fixture 无 CHOICE 场景，测试用
monkeypatch/fake experience 构造 CHOICE `AwaitingInput`——沿用该文件现有
的 fake/shared 双轨测试惯例，不新造测试基建）。
证据链三 seam：TUI 派发正确 typed `AnswerRun`（fake experience 集成测）；
`ResearchRunExperience.handle` 接受 typed OPTION / 拒 text（`ReplayTransport`
回放 contract 测——TUI 派发的同一 seam）；brokered admission 校验（现有
单测 `test_hitl1_language_choice_requires_a_current_typed_advertised_option`）。

## Risks / Trade-offs

- [fixture 无真实 CHOICE 场景，回归只能打 fake experience 层] → 接受：
  admission 侧校验已有契约测试；本 change 的因果 owner 是 presentation
  投影，fake 层回归恰好钉住它；Stage B2 真机 CHOICE probe 作为live 佐证
  （010 战役条件项）。
- [动态按钮组引入渲染状态泄漏（上轮选项残留）] → `_render_view() 每次全量
  重算按钮组可见性，测试覆盖 "CHOICE→TEXT 轮转后选项消失"。
- [embedded-smoke 真机首跑撞出新形状（BUG-058/059 类）] → 不在本 change
  范围；010 战役 bug 流程承接。

## Migration Plan

单 PR 级 change，无数据/契约迁移；回滚 = revert 该 commit。BUG-060 归档
在 verify 绿后按 `_backlog/bugs/README.md` 流程执行。

## Open Questions

（无）
