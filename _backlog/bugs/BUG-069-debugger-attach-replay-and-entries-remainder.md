# BUG-069: C4b CLI 接线剩余——attach/replay 意图存储未消费、RED-014 三入口未落地

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 活跃

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

## 修复关联

驱动侧能力已存在：`DebugRunDriver.open_attach(AttachRequest)`（runtime/debug_driver.py）；
缺的是 TUI 侧消费（启动时按意图开 attach/replay 会话）与 RED-014 三入口 UI
（New Run/Attach/Replay 按钮与 slash 命令归一）。实现时以
`test_debug_pilot_journey.py` 扩展三入口等价场景（RED-014 已有 @impl 挂点），
入口链回归测试模式沿用 `repair-debugger-cli-entry-conformance` 的 subprocess
探针 + 构造断言。spec 不需要 delta（RED-013/014 条款已在，属实现追平）。
