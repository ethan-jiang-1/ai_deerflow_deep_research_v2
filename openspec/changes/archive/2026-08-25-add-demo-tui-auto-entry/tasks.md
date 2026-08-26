# Tasks: add-demo-tui-auto-entry

## 1. 代码入口（--auto 投影）

- [x] 1.1 `scripts/demo_tui.py` argparse：新增 `--auto` 开关（help 注明 010 自动全跑、
  HITL1/HITL2 由 graph-owned 策略回答）；`--auto` 无 `--embedded-smoke` 时报错
  （`parser.error("--auto applies only with --embedded-smoke")`）；parser 构造/校验
  抽为 `_build_parser()` / `_validate_args()`（demo_sessions 先例，供确定性测试）
- [x] 1.2 `_initialize()`：preflight 通过且 `self.mode == "embedded_smoke" and
  self.auto` 时，自动派发一次
  `StartRun(question=self.AUTO_QUESTION, scripted=True, profile_intent=None)`
  （复用 graph 已支持的 scripted 起始契约 → non_interactive_policy
  auto_profile + auto_proceed；TUI 不自建 profile、不回答 HITL）；与 020 侦察
  循环（onboarding）互斥分支
- [x] 1.3 banner（on_mount）：auto 形态在 mode_label 追加 `· auto`（可见标识，
  RED-001 embedded-smoke 标识要求的子形态）
- [x] 1.4 `Makefile`：新增 `demo-tui-real-auto` target（`demo_tui.py
  --embedded-smoke --auto`，010 自动入口）

## 2. 确定性回归（集成测试，无真实模型）

- [x] 2.1 `tests/integration/test_demo_tui.py` 用例：embedded_smoke+auto →
  只派发一个 `StartRun`（`scripted is True`、`profile_intent is None`、
  `question == AUTO_QUESTION`）且到达 `Terminal`（零输入）
- [x] 2.2 用例：fixture+auto → `StartRun.scripted is False`（auto 只作用于
  embedded-smoke，fixture 保持交互）
- [x] 2.3 用例（apply 阶段补齐 scenario 2 缺口）：`--auto` 无
  `--embedded-smoke` 时 `_validate_args` 抛 `SystemExit`；`--embedded-smoke
  --auto` 组合被接受
- [x] 2.4 focused 测试转绿（3 auto 用例全绿）

## 3. 契约与回归收口

- [x] 3.1 在 `openspec/governance/req-registry.yaml` 登记新 ID（按 polish
  报告的 reservation）：`RED-010`（research-demo-tui — Demo TUI 提供显式
  零人工自动全跑入口），描述与 delta spec 一致；确认无 already-assigned 冲突
- [x] 3.2 对照 delta spec（`specs/research-demo-tui/spec.md` ADDED requirement）
  逐 scenario 核对测试覆盖：auto 派发 scripted start 直达终态（2.1）/
  auto flag 只限 embedded-smoke（2.2 + 2.3）/ HITL1+HITL2 以 graph-owned
  phase 经过（2.1 到达 Terminal 的 scripted 语义）
- [x] 3.3 `UV_OFFLINE=1 make verify` 全绿（fast 2650 + integration
  301[4 skipped] + workflow 35）
- [x] 3.4 `openspec validate add-demo-tui-auto-entry --strict` 通过

## 4. bug 归档与战役衔接

- [x] 4.1 BUG-061 补充修复关联（change 名 + 验证证据），按
  `_backlog/bugs/README.md` 流程 git mv 至 `_done/_fixed_bugs/` 并同步
  三个 README（编号权威 → BUG-062）
- [x] 4.2 在
  `_backlog/plans/tui-interactive-campaign-progress.md` §3 Phase 4 勾项、
  §4 加进展行、§5 状态更新（BUG-061 从"⚠️ 待走"改"✅ 已归档"）
- [x] 4.3 `_backlog/_local_demo/README.md` 010 行与 runbook-010 补 openspec
  change 背书引用（`add-demo-tui-auto-entry`，已归档
  `archive/2026-08-25-add-demo-tui-auto-entry/`）
