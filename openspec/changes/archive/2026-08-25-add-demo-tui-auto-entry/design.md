# Design: add-demo-tui-auto-entry

## Context

见 `proposal.md` Why（BUG-061）。当前 `scripts/demo_tui.py` 的入口面：

- argparse（:1700-1722）已有 `--fixture` / `--profile` / `--embedded-smoke`，
  无 auto 开关；`--auto` 不存在；
- `_initialize()`（:974-1003）：preflight 通过后，embedded_smoke 分支只走
  020 侦察循环（`_onboarding = True` + `_render_recon()`），无"就绪后自动
  派发固定问题"的分支；
- 固定问题常量 `AUTO_QUESTION`（:850）已存在（020 侦察模式的 start 按钮
  与触发语共用它，:1374）；
- shared boundary（`runtime/run_experience.py::_prepare_intent`）：已支持
  `StartRun(scripted=True, profile_intent=None)` → `non_interactive_policy`
  auto_profile + auto_proceed（CLI `make demo-real-scripted` 已在用）；
- 类构造 `DeepResearchDemoTUI(mode, profile, auto=False)`（:852-862）已有
  `auto` 参数占位。

约束：RED-001 已定义 embedded-smoke 模式（本地真实图、可见标识、local
preflight）；TUI 不得自建 profile 策略、不得自行回答 HITL；scripted 策略与
admission 已正确，本 change 不动它们。

## Goals / Non-Goals

**Goals:**

- embedded-smoke 模式提供显式 `--auto` 入口：preflight 通过后自动派发一次
  固定 scripted start，真人零按键到终态；
- 确定性回归覆盖（集成测试，无真实模型）；
- 010 与 020 同一例子（共用 `AUTO_QUESTION`）。

**Non-Goals:**

- 不改 `run_experience.py` / graph / engine 的 scripted 策略或 admission；
- 不给 fixture / Gateway observer 模式加 auto 行为（CLI 拒绝该 flag 组合）；
- 不改 CLI 自动跑（`make demo-real-scripted` 已存在，不迁移）；
- 不做"auto 跑完自动回侦察/自动重跑"（010 runbook 只要求单跑到终态）。

## Decisions

**D1：`--auto` 只接受配 `--embedded-smoke`（argparse 报错），类层 auto 只
影响 embedded_smoke 分支。**
`if args.auto and not args.embedded_smoke: parser.error(...)`——fixture 与
Gateway 模式在 CLI 层直接拒绝；类层即使直接构造 `DeepResearchDemoTUI(mode=
"fixture", auto=True)` 也不触发 auto 行为（`_initialize` 只对
`self.mode == "embedded_smoke" and self.auto` 派发，测试
`test_tui_auto_mode_stays_interactive_when_embedded_only` 证明 fixture+auto
的 `StartRun.scripted is False`）。
备选 A：auto 也作用于 fixture——不选：fixture 无真实图/真实 report，010
runbook 验收要求 `final/report.md` 真实内容，auto 在 fixture 无合法语义。
备选 B：auto 作用于 Gateway observer——不选：Gateway 是公共 turns 观察者，
无本地 scripted 策略概念（RED-001：Gateway 只转发输入文本或当前显示
control 值）。

**D2：auto 派发发生在 `_initialize` preflight 通过后，一次
`StartRun(question=self.AUTO_QUESTION, scripted=True, profile_intent=None)`。**
复用 graph 已支持的 scripted 起始契约（`_prepare_intent` → non_interactive_
policy auto_profile + auto_proceed），TUI 不自建 profile 策略、不回答 HITL1/
HITL2；`profile_intent=None` = 默认产品路径（同 004 的 None 意图），与 010
runbook 验收一致。
备选 A：auto 派发 `profile_intent=minimal`——不选：010 定义默认产品路径
（None），minimal 是 003 的声明，混同会破坏 003 对照。
备选 B：auto 时 TUI 模拟"用户输入"逐轮作答——不选：伪造用户输入是
presentation 越权；scripted 短路正是 001-004 已验证的正确机制。

**D3：banner 标注 `· auto`（on_mount 时 mode_label 追加）。**
RED-001 要求 embedded-smoke 可见标识；auto 是 embedded-smoke 的子形态，
必须同样可见，避免把自动跑误认成手动交互跑（010 runbook "你只观察"的
前提就是一眼能认出 auto）。

**D4：测试走现有 Pilot/shared experience 集成测试惯例**
（`tests/integration/test_demo_tui.py` 现有 `_install_scripted` + Pilot 模式）：
- `test_tui_auto_mode_submits_fixed_scripted_question`：embedded_smoke+auto →
  断言只派发一个 `StartRun`，`scripted is True`、`profile_intent is None`、
  `question == AUTO_QUESTION`，且到达 `Terminal`（零输入）；
- `test_tui_auto_mode_stays_interactive_when_embedded_only`：fixture+auto →
  `StartRun.scripted is False`（保持交互）。
证据链两 seam：TUI 派发 seam（集成测试）+ shared `_prepare_intent` 接受
scripted start（现有 CLI contract 测试已覆盖同一契约）。

**D5：auto 与 020 侦察循环互斥分支（`if ... and self.auto: dispatch`
`elif self.mode == "embedded_smoke": onboarding`）。**
embedded_smoke 的两种形态（010 auto / 020 manual）共用一个入口，分支互斥，
不叠加；banner（D3）与测试（D4）分别钉住两种形态。

## Risks / Trade-offs

- [auto 与 020 侦察循环状态互相污染] → D5 互斥分支 + D3 可见标识；测试覆盖
  两种形态（auto 直达 Terminal / manual 进 recon）。
- [010 真机首跑撞出新形状（BUG-058/059 类：真实模型 vs 确定性契约边界）]
  → 不在本 change 范围；010 战役 bug 流程承接。
- [`AUTO_QUESTION` 常量漂移（010 vs 020 不同问题）] → 单常量共用（:850），
  README"01x/02x 同 x 同例子"规则兜底。

## Migration Plan

单 PR 级 change，无数据/契约迁移；回滚 = revert 该 commit。BUG-061 归档
（`_done/_fixed_bugs/`）在 verify 全绿后按 `_backlog/bugs/README.md` 流程执行。

## Open Questions

（无）
