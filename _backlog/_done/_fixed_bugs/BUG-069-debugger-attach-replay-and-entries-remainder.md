# BUG-069: C4b CLI 接线剩余——attach/replay 意图存储未消费、RED-014 三入口未落地

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 已修复（2026-09-27）

## 症状

`./run/tui-workflow-debugger.sh --attach <bundle_id>`（或 `--replay <id>`）能启动
TUI，但意图只被存到 `_attach_intent`/`_replay_intent` 就无人消费——attach/replay
行为不发生，也无任何提示。TUI 中不存在 RED-014 要求的 Attach/Replay 入口
（按钮与 slash 命令）；runbook-030 §6 文档化的 attach/replay 流程从 shell 不可达。

## 根因

C4b change（`2026-09-02-connect-tui-workflow-debugger`）部分落地：提交 `e7b0c9e`
自述 "partial apply, plan checkpoint"。in-app 调试循环（start/advance/context/
detach，`debug_mode=True` 直构）已完整；CLI→app 链断在（a）`main()` 丢弃
`--debug`、（b）launcher 不注入 `--debug`、（c）launcher 不启用 `src_fixtures`、
（d）attach/replay 意图无消费路径、（e）RED-014 三入口未建。测试盲区：Pilot
journey 直构 app 绕过 CLI 链，entry 测试只断言 `--help` 转发语法，pytest
`pythonpath` 配置掩盖了路径契约。(a)(b)(c) 已由 change
`repair-debugger-cli-entry-conformance`（2026-09-27 归档）修复；本卡追踪
(d)(e)。

## 复现

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh --attach b_xxxxxxxxxxxxxxxxxxxx
# TUI 打开（fixture workbench），但无 attach 行为、无 Attach/Replay 入口
```

## 修复关联（已完成，2026-09-27）

**消费**：`--attach <id>` 经 `_initialize` → `_debug_attach`（`open_attach` 生命周期
校验、接上 durable checkpoint、不自动推进）；`--replay <id>` → `_debug_replay`
（`RunTraceProjector.project_full(live=False)` 只读渲染帧序列/route/next/terminal，
**不取 lease、不建会话、不写**）。

**三入口**（RED-014 的已交付子集）：New Run / Attach / Replay 各有 **按钮**、
**slash**（`/attach`、`/replay`）、**启动参数**三条等价路径，全部落到同一组 typed
方法。RED-014 还要求"命令面板动作"作为第三条等价通路，以及 Node Context / Files
分栏与带 posture 的 attach 候选面——这些**未交付**，登记在 BUG-071。
`--attach/--replay` 隐含 fixture 调试器组合（`_build_app` 推断 debug_mode；parser
要求 `--fixture`；launcher 按需补 `--fixture --debug`）。
另修一处按钮引入的 UX 缺陷：点击调试按钮后焦点留在按钮，导致后续 Enter（step 节奏键）
到不了 composer；现在按钮动作结束后归焦 composer。

**回归锁**：`make tui-journey` 新增 [5a] Attach 按钮重开保留 bundle、
[5b] `/replay` 只读渲染（断言无调试会话、渲染出帧）与 [1] 三入口存在性；
`test_demo_tui.py::test_tui_attach_and_replay_intents_require_the_fixture_workbench`
锁 CLI 校验与 debug_mode 推断。

**剩余 RED-014 UI 面**（另行登记 BUG-071）：命令面板（command palette）归一、
专门的 Node Context 分栏（含 coverage strip）与 Files 分栏
（`OperatorWorkspaceReader` typed pages）。spec 不需要 delta（RED-013/014 条款已在，
属实现追平）。
