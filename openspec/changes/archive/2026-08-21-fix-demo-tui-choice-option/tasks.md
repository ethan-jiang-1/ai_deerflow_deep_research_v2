# Tasks: fix-demo-tui-choice-option

## 1. 测试先行（红）

- [x] 1.1 在 `tests/integration/test_demo_tui.py` 增 fake-experience 用例：
  CHOICE `AwaitingInput`（广告 `zh`/`en`）到达时，选项按钮组渲染且可见
- [x] 1.2 用例：点击某选项按钮 → 派发的是 `response_kind="option"` 且
  `option_id` 为该广告选项 id 的 `AnswerRun`（typed OPTION，非 text、
  非 `SelectControlRun`）
- [x] 1.3 用例：hitl1 CHOICE 轮 composer 输入**精确等于**某广告选项 id（如
  `zh`）→ 派发该 id 的 typed OPTION `AnswerRun`（兑现现有 placeholder 广告的
  键盘路径）
- [x] 1.4 用例：hitl1 CHOICE 轮 composer 输入**不匹配**任何广告 id → 不派发
  任何 `AnswerRun`（无 text 派发、无伪造 option id）；TEXT 轮自由文本行为
  不变（仍派发 text `AnswerRun`）；CHOICE→TEXT 轮转后选项按钮组消失、
  composer 语义复原；现有 hitl2 CHOICE 文本转发用例
  （`test_tui_forwards_unadvertised_choice_to_graph_owned_validation`）
  保持绿（回归锚）
- [x] 1.5 在 `tests/contract/test_run_experience_contract.py` 增回放用例
  （`ReplayTransport` 构造 hitl1 CHOICE suspension）：typed OPTION
  `AnswerRun(value="zh", response_kind="option", option_id="zh")` 成功 resume
  （transport 收到 resume 调用）；text `AnswerRun` 被拒——shared boundary 的
  拒绝经 `handle()` 投影为闭合 `input.invalid_response` Fault 且不派发
  resume（`hitl1_language_answer_requires_option` ValueError 不逸出
  handle）——在 TUI 派发的同一 seam 上确定性证明 delta scenario 1 的接受
  主张
- [x] 1.6 跑 `make test-integration` 与 `make test-contract`（或各自 focused
  目标）确认新用例红

## 2. 实现（绿）

- [x] 2.1 `scripts/demo_tui.py`：compose() 按 `SupportedLanguageOption`
  闭集静态生成选项按钮组；`_render_view()` 每帧按当前 hitl1 CHOICE 广告
  选项切可见性与 label（数据只用 shared 投影的 option id/label；离开
  hitl1 CHOICE 时隐藏）
- [x] 2.2 选项按钮回调：派发 `AnswerRun(value=<广告选项 id>,
  response_kind="option", option_id=<同一广告选项 id>)`（typed contract 强制
  value == option_id，按 D1，不混用 `SelectControlRun`）
- [x] 2.3 `on_input_submitted()`：hitl1 CHOICE 轮当前时，提交文本与广告
  选项 id 精确相等 → 派发该 id 的 typed OPTION（D1 路径 b）；不相等 →
  不派发（D2 防呆）；其他轮（TEXT / hitl2 CHOICE）转发行为不变
- [x] 2.4 跑 1.x 新用例转绿

## 3. 契约与回归收口

- [x] 3.1 在 `openspec/governance/req-registry.yaml` 登记新 ID（按 polish
  报告的 reservation）：`RED-009`（Demo TUI 以 typed OPTION 回答广告 CHOICE
  prompt），描述与 delta spec 一致；确认无 already-assigned 冲突
- [x] 3.2 对照 delta spec
  （`specs/research-demo-tui/spec.md` ADDED requirement）逐 scenario 核对
  测试覆盖：选广告选项被 admission 接受 / 文本不伪造 option / TEXT 轮不变
- [x] 3.3 `UV_OFFLINE=1 make verify` 全绿
- [x] 3.4 `openspec validate fix-demo-tui-choice-option --strict` 通过

## 4. bug 归档与战役衔接

- [x] 4.1 BUG-060 补充修复关联（change 名 + 验证证据），按
  `_backlog/bugs/README.md` 流程 git mv 至 `_done/_fixed_bugs/` 并同步
  三个 README（编号权威已是 BUG-061，无需再动）
- [x] 4.2 在
  `_backlog/plans/tui-interactive-campaign-progress.md` §3 Phase 3 勾项、
  §4 加进展行、§5 状态更新
- [x] 4.3 （Stage B2 前置就绪标记）runbook-010 §4 的前置条件 (a) 可勾
