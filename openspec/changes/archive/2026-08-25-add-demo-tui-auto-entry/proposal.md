# Proposal: add-demo-tui-auto-entry

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py` — presentation adapter；composer 提交恒构造 `StartRun(question, scripted=False)`（原 :605 行），`_initialize` 没有"就绪后自动派发固定问题"的分支，TUI 一层缺失 scripted 起始契约的显式入口（BUG-061）。
- **Seam classification:** wiring — presentation-only 投影层缺陷；scripted 起始契约（`StartRun(scripted=True, profile_intent=None)` → `non_interactive_policy` auto_profile + auto_proceed）与 admission 校验已存在于 shared boundary（`runtime/run_experience.py::_prepare_intent`），TUI 只是把它投影成显式入口，无认知责任。
- **Question:** Demo TUI 如何把 graph 已支持的 scripted 起始契约投影成"embedded-smoke preflight 通过后自动派发固定问题、真人零按键到终态"的显式入口，而不自建 profile 策略、不回答 HITL1/HITL2、不触碰 Gateway observer 模式？
- **Necessary adjacent/external contracts:** RED-010（本 change 新增并注册）；`execution-intent` EXI-001（scripted start 的 non_interactive_policy 契约，TUI 只提交不实现）；`research-run-experience` RER-001/RER-004（shared run updates 与 preflight 的呈现）；`research-demo-tui` RED-001（embedded-smoke 模式的本地真实图路由定义，本 change 在其上加显式入口）。
- **Evidence seam:** `tests/integration/test_demo_tui.py`（`test_tui_auto_mode_submits_fixed_scripted_question`：auto 派发 scripted `StartRun` 且直达 Terminal；`test_tui_auto_mode_stays_interactive_when_embedded_only`：fixture+auto 保持交互）。
- **Not in scope:** `run_experience.py` / graph / engine 的 scripted 策略改动；CLI 自动跑（`make demo-real-scripted`）改动；Gateway observer 模式的自动入口；hitl1/hitl2 人工回答行为改动；`deerflow/` gitlink 不改动、不 source-browse（ordinary downstream work）。
- **Triggered review policies:** change-admission

## Why

BUG-061：`scripts/demo_tui.py` 的 composer 提交永远构造
`StartRun(question=value)`（`scripted=False` 默认），且没有任何
`--auto`/`--scripted` 开关——全自动机制只存在于 CLI（`make demo-real-scripted`）。
结果：TUI 一层无法复现 010 自动形态（同一固定例子、真人零按键、TUI 自主到
终态），`RUN-010.command` 类入口无从拉起"自动全跑"。010 runbook 已写好验收
判据，但入口不存在。

## What Changes

- Demo TUI 新增 `--auto` 开关（仅限 `--embedded-smoke`；argparse 校验
  `--auto` 无 `--embedded-smoke` 时报错）：embedded-smoke preflight 通过后，
  `_initialize` 自动派发一次 `StartRun(question=<003 固定问题>, scripted=True,
  profile_intent=None)`——graph 拥有的 scripted 策略（auto_profile +
  auto_proceed）自动回答 HITL1/HITL2，真人零按键，TUI 自主到 `terminal_status=completed`；
- banner 标注 `· auto`，标识自动形态；
- `Makefile` 新增 `demo-tui-real-auto` target（010 自动入口，`demo_tui.py
  --embedded-smoke --auto`）；
- fixture 与 Gateway observer 模式不获得 auto 行为（CLI 拒绝该 flag 组合；
  类层 fixture+auto 保持交互）；
- 确定性回归：集成测试 2 用例（auto 派发 scripted StartRun 且直达 Terminal；
  fixture+auto 仍保持交互），不依赖真实模型。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `research-demo-tui`: 现有模式定义（RED-001）已含 embedded-smoke 本地真实图
  路由，但缺"显式零人工自动全跑入口"要求——新增 **RED-010**（新注册
  requirement）：embedded-smoke 模式提供 `--auto` 显式入口，preflight 后派发
  固定 scripted start，fixture/Gateway 模式保持交互。

## Impact

- 代码：`deep_research_harness/scripts/demo_tui.py`（`--auto` argparse +
  `_initialize` 自动派发分支 + banner 标注）、`deep_research_harness/Makefile`
  （`demo-tui-real-auto` target）；
- 测试：`deep_research_harness/tests/integration/test_demo_tui.py`（2 用例，
  BUG-061 已带，20 passed）；
- 不动：`runtime/run_experience.py`（`_prepare_intent` 与 scripted 策略已正确）、
  graph/hitl1/hitl2、CLI 自动跑、Gateway observer 模式；
- 文档：runbook-010-tui-auto.md（已写入口，本 change 补背书）、
  `_backlog/_local_demo/README.md`（010 行已写"✅ 已落地"，本 change 使其有
  openspec 背书）；
- bug：归档 BUG-061（`_backlog/_done/_fixed_bugs/`）；
- 验证门：`UV_OFFLINE=1 make verify`（deep_research_harness）。
