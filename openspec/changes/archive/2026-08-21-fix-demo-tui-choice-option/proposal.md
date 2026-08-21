# Proposal: fix-demo-tui-choice-option

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py` — presentation adapter；`on_input_submitted()` 把 composer 输入恒构造为 text `AnswerRun`，CHOICE 轮又无选项渲染，BUG-060 的两个症状都落在这一层。
- **Seam classification:** wiring — presentation-only 投影层缺陷；shared typed boundary 与 admission 校验已正确，无认知责任。
- **Question:** 用户对当前广告 CHOICE 选项的选择，如何以 shared run experience 所要求的 typed option answer 到达它——而 TUI 不自建 response envelope、不伪造 option id、不接管 admission？
- **Necessary adjacent/external contracts:** RED-009（本 change 新增并注册）；RED-007 control 提交边界维持不动；`human-interaction-contract` 与 `run_experience.py::_prepare_intent` 校验维持不动。
- **Evidence seam:** `tests/integration/test_demo_tui.py`（fake experience CHOICE 路径：渲染 + typed OPTION 派发）；`tests/contract/test_run_experience_contract.py`（`ReplayTransport` 回放 hitl1 CHOICE suspension：typed OPTION 接受 / text 拒绝）；现有单测 `test_hitl1_language_choice_requires_a_current_typed_advertised_option`（brokered admission）。
- **Not in scope:** `run_experience.py` / hitl1 admission 代码改动；Gateway observer 模式新增本地选项派发；自由文本→option 猜测映射（文本别名）；capability 归因 observation fact（已推迟）。
- **Triggered review policies:** change-admission

## Why

BUG-060：Demo TUI 的 composer 把所有输入一律构造为默认 text `AnswerRun`，
而 HITL1 language CHOICE 轮（`mode=CHOICE`，选项 `zh`/`en`）要求
`response_kind=option` + 该轮合法 `option_id`（`run_experience.py::
_prepare_intent` 以 `hitl1_language_answer_requires_option` 拒绝 text）；
且该轮没有 `accept_current_proposal` visible control，"Start proposal"
按钮不显示——CHOICE 轮在 TUI 里是死路。010 战役的 Stage B2（language
CHOICE 专项）以本修复为前置。

## What Changes

- Demo TUI（fixture 与 embedded-smoke 模式）在当前 prompt 为 **HITL1
  CHOICE**（language）模式时渲染 graph-owned 广告选项（如 `zh`/`en`），
  并把用户的选择派发为 `response_kind=option` + 该轮合法 `option_id` 的
  typed `AnswerRun`（按钮点击与 composer 精确匹配广告 id 两条等价路径）；
- TEXT 模式轮与 hitl2 CHOICE 轮的现有转发行为不变（后者自由文本本就
  转发 graph 侧校验，且 `AnswerRun.option_id` 的 Literal 闭集只覆盖
  language 选项）；
- 派发仍只经 `ResearchRunExperience`（TUI 不自建 response envelope、不自行
  判定 phase/option 合法性——admission 校验留在 shared boundary）；
- 确定性回归：fixture CHOICE 路径的 TUI 测试（选项渲染 + typed OPTION
  派发 + admission 接受），不依赖真实模型；
- Gateway observer 模式不新增本地选项派发行为（其转发语义维持现状）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `research-demo-tui`: 交互提交边界（现 RED-007 "submits visible controls
  without text aliases" 只覆盖 control 与自由文本转发）——新增 CHOICE 轮
  选项渲染与 typed OPTION 派发要求（**RED-009**，新注册 requirement），含
  TEXT 轮不变与 TUI 不自建 envelope 的边界。

## Impact

- 代码：`deep_research_harness/scripts/demo_tui.py`（presentation adapter：
  CHOICE 轮选项渲染 + `on_input_submitted` 派发分支）；
- 测试：`deep_research_harness/tests/integration/test_demo_tui.py`
  （fixture CHOICE 路径确定性回归）；
- 不动：`runtime/run_experience.py`（`_prepare_intent` 校验已正确）、
  `human-interaction-contract` spec、graph/hitl1 admission；
- bug：修复后按流程归档 BUG-060（`_backlog/_done/_fixed_bugs/`）；
- 验证门：`UV_OFFLINE=1 make verify`（deep_research_harness）。
