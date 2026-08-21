# BUG-060: Demo TUI 把 composer 输入一律按 text 提交，hitl1 language CHOICE 轮无法被合法回答

> 严重级别: P1（不阻塞 010 B1 主线——英文固定问题确定性 en 不触发 CHOICE；但封锁条件性 B2 的 CHOICE 覆盖） | 发现: 2026-08-20 | 状态: 已修复（change `fix-demo-tui-choice-option`；RED-009 注册，verify 全绿）

## 症状

在 embedded-smoke 真实图（或任何把 HITL1 推到 language CHOICE 的 run）中，
当 HITL1 发出 `mode=CHOICE` 的 language interrupt（选项 `zh`/`en`）时，
Demo TUI 的用户无法合法作答：

1. composer 任何输入都被构造为默认 `AnswerRun(value=...)`（即
   `response_kind=text`），而该轮要求 typed OPTION——
   `run_experience.py::_prepare_intent` 以
   `hitl1_language_answer_requires_option` 拒绝 text；
2. "Start proposal" 按钮只在当前 prompt 暴露 `accept_current_proposal`
   visible control 时显示，language CHOICE 轮没有该 control——按钮不出现，
   也不能用它选语言。

即：language CHOICE 轮在 Demo TUI 里是**死路**（输入被拒 + 无可用按钮）。

## 根因

presentation adapter 缺投影：`scripts/demo_tui.py::on_input_submitted()`
对 composer 输入只构造默认 text `AnswerRun`，不感知当前 prompt 的
CHOICE mode 与 options；没有任何路径把用户选择投影为
`response_kind=option` + `option_id` 的 typed `AnswerRun`。

属 presentation 层缺陷，不是 route/profile admission 的问题——shared
typed interaction boundary（`AnswerRun` 的 option 语义）与
`_prepare_intent` 的校验本身工作正常（fixture CHOICE 场景的契约测试覆盖
校验侧）。

## 复现

代码级确定性复现（无需真实凭证）：

- `scripts/demo_tui.py:577`：`self._dispatch(AnswerRun(value=value))` ——
  所有 composer 输入固定为 text；
- `runtime/run_experience.py:357-358`：hitl1 CHOICE 且
  `response_kind != "option"` → `raise ValueError("hitl1_language_answer_requires_option")`；
- `scripts/demo_tui.py:515`：Start proposal 按钮的显示条件是
  `accept_current_proposal` visible control 存在，language CHOICE 轮无此
  control。

真实路径：`make demo-tui-embedded-smoke` + 一个 unspecified-language 问题
（不含 ASCII 字母与汉字），HITL1 将发出 language CHOICE，TUI 侧作答必被
拒。（010 战役 B1 的英文固定问题不触发此路径。）

## 修复关联

已修复（change `fix-demo-tui-choice-option`，2026-08-21 归档）：

- `scripts/demo_tui.py`：compose() 按 `SupportedLanguageOption` 闭集静态生成
  选项按钮组，`_render_view()` 每帧按当前 hitl1 CHOICE 广告选项切可见性/
  label；`on_input_submitted()` 对 hitl1 CHOICE 轮实现 exact-match——composer
  输入精确等于广告选项 id 时派发 typed OPTION
  （`AnswerRun(value=option_id, response_kind="option", option_id=option_id)`），
  不匹配时不派发；选项按钮点击派发同一 typed OPTION。TEXT 轮与 hitl2 CHOICE
  轮的转发行为不变（后者自由文本转发 graph 侧校验是受保护现有行为）。
- 契约注册：RED-009（research-demo-tui）登记于 req-registry。
- 确定性回归：`tests/integration/test_demo_tui.py` 4 个 RED-009 用例
  （渲染/按钮 typed OPTION/exact-match/非匹配不派发+轮转复位+hitl2 回归锚）；
  `tests/contract/test_run_experience_contract.py` 2 个回放用例（同一 seam：
  typed OPTION 接受 resume、text 投影为 `input.invalid_response` Fault 不
  resume）。
- 验证：`UV_OFFLINE=1 make verify` 全绿（fast 2641 + integration 261 +
  workflow 35）；`openspec validate --strict` 通过。
- 前置关系解除：010 战役 Stage B2（language CHOICE 专项）前置条件 (a)
  已满足（runbook-010 §4 已更新）。
