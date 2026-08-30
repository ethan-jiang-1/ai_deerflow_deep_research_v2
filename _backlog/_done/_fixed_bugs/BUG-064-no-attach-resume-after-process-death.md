# BUG-064: 断网/进程死亡即失去 run：无 attach/resume 入口，孤儿 bundle 不可恢复也不可 inspect

> 严重级别: P1 | 发现: 2026-08-30 | 状态: 已修复（add-suspended-run-recovery）
>
> **证据修正（2026-08-30 归档时）**：该孤儿 bundle 于 15:33 网络恢复后自行续跑到
> `terminal=completed`（挂起的 wave1 调用 69 分钟后返回）——"进程死亡"实为
> "冻结失联"，恢复需求与全部缺陷点（无 attach 入口、inspect 拒绝、journal
> 误标）依然成立；自愈属侥幸（依赖同一次挂起调用的存活），真进程死亡的恢复
> 缺口由本修复补齐。
> 发现场景: 020 战役 Stage B1 第 2 跑（用户报告："网络一旦断了 TUI 就死了，没有 resume 这样的东西"）

## 症状

embedded 真实跑进行中网络断开 → TUI 进程树整体死亡（tui 日志 14:23:45 后零写入，
屏幕冻结在 "wave1 model_tool started"）→ run bundle 遗弃在 wave1 中段：

- run-summary：`status=suspended`、`journal_availability=complete`（53 事件、
  0 dropped）——domain 已把"进程死亡"视为 suspended（restart_durable 语义下合理）；
- 重开 TUI：**无任何"继续上次 run"入口**——只有侦察模式 + 新跑（= 重付
  hitl1 交互 + planning + wave0 全部成本）；
- `make demo-sessions inspect <bundle>`：拒绝——"Run Bundle or its contained
  Event Journal is unavailable for safe inspection"（非 terminal 的 suspended
  bundle 连只读投影都不给）；
- 无人认领 66+ 分钟，无超时、无收割、无提示。

## 既有设施（本 bug 不是要从零造恢复能力）

- `restart_durable` + graph.sqlite 按 phase attempt checkpoint；
- suspended → resume 契约已存在：`runtime/session_workbench.py::resume()`、
  `runtime/bundle_lifecycle.py::resume()`、`runtime/bundle_graph.py::resume()`；
- `legal_next_action` 门控已存在：terminal → `REFINE`（允许时）/ `START`，
  绝不 `RESUME`；suspended（等人）→ `RESUME`；
- 状态模型 `active|suspended|completed|stopped|cancelled|blocked` + generation ≤ 2。

**缺口在四件事**：(a) TUI presentation 无 attach 面（启动不扫描未完成 bundle）；
(b) "进程死亡中段"的 suspended 与"等人输入"的 suspended 共用语义，但 resume
路径只定义了 pending-input 回答，mid-execution orphan 的 resume 未定义/未测；
(c) TUI 自身死于断网（presentation 鲁棒性——应显示降级状态而非死掉）；
(d) safe-inspect 只认 terminal，孤儿诊断不可用。

## 根因（待 change 内确认）

恢复能力躺在 runtime/domain 层，但生命周期 UX 契约缺失：长跑 agentic loop
是 durable 对象，却没有"死亡后重新认领"的入口；进程死亡与 human-interrupt
两种挂起未区分；presentation 层把"网络断"当致命错误而非可重试降级。

## 复现

1. `make demo-tui-embedded-smoke`，hitl1 确认后等图跑到 wave0/wave1；
2. 断网（或直接杀 TUI 进程树）；
3. 观察：TUI 冻结/死；bundle suspended 遗弃；重开 TUI 无恢复入口；
   inspect 拒绝。

## 修复关联

未开始。独立 change（与 BUG-062 互补：062 让 loop 不死——in-run 重试；
064 让死了能回来——attach/resume）。分层落点：TUI attach 面 =
presentation adapter；orphan resume 语义 + inspect 放宽 = domain/runtime。
注意两点：(1) resume/重试若以"同 bundle 新 generation"落地，runbook §5.2
exact-bundle 绑定规则要同步演进；(2) 不得把 route/profile admission 下放给
TUI（plan v4 原则）。UX 期望形态见 bug 内引用的 handoff-020 战况表
（2026-08-30 run 1/run 2 两个活标本）。
