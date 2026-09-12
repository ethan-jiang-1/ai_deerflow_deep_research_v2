# TODO: Stage B1 embedded real TUI run (Mode 020)

> 状态: 暂停（外部阻塞） | 优先级: 中 | 更新: 2026-09-12
> 上游: `_backlog/_local_demo/handoff-020-tui-manual.md` | 下游: 无

## Why

Mode 020 TUI 真人交互战役的**主体**——Stage B1（真人 HITL1 的 embedded 真实跑）——
尚未完成。Stage A fixture smoke 全绿，两个 change（`fix-demo-tui-choice-option` 修
BUG-060、`add-demo-tui-auto-entry` 修 BUG-061）已归档；B1 三次尝试全部因
**机器级网络不可达**（`api.deepseek.com` TCP 连接超时）干净 blocked，未立新 bug。
此前此待办只活在 handoff 文档里，无独立条目。

## 现状对齐

- 期间连带修复了 B1 暴露的产品缺陷：BUG-062（wave2 timeout 零重试）、
  BUG-063（interrupt 挂起被误记 internal.unexpected）、BUG-064（进程死亡孤儿无
  attach/resume 入口）——均已修复并归档。
- 战役跑次基线已随尝试重建至 **=10**（详见 handoff 表）；重跑后**唯一新增**即验收对象。
- PASS 判据 7 条见 runbook-020 §3.4；操作四步见 handoff「你要做的事」。

## Current Direction（重启时）

1. 确认网络恢复到 `api.deepseek.com` + Tavily；
2. 重做基线快照（命令输出会重申）；
3. 双击 `RUN-020.command` 跑 B1，按 PASS 判据判定。

## Non-Goals

- 不把 B1 的三连挂当成产品缺陷立新 bug（根因是网络，C1 快失败行为已当场验证生效）。
- 不在网络不可达时反复重触发。

## Next Step

无（暂停）。重启条件：网络恢复且用户授权重跑；参考
[`runbook-020`](../../../deep_research_harness/docs/runbooks/runbook-020-tui-manual.md)
与 `_local_demo/handoff-020-tui-manual.md`。
