# Plan: _local_demo 调试工作台 runbook 补齐

> 类型: 文档补齐 | 创建: 2026-09-02
> 背景: TUI workflow debugger 战役收口后，`_local_demo/` 尚未反映新的调试工作台入口

## 背景 / 现状

C4b 交付了 `run/tui-workflow-debugger.sh`（canonical launcher）和 `make tui-debugger`
alias，以及 `--debug` 节点边界步进 + `--attach`/`--replay` exact-bundle intent。
但 `_local_demo/` 完全没有这些内容的文档——操作者不知道 debugger workbench 怎么用。

当前 `_local_demo/` 覆盖的跑法轴：

| 轴 | 编号 | 入口 | 状态 |
|----|------|------|------|
| CLI | 001–004 | `make demo` 系列 | 不受影响 |
| TUI 自动 | 010 | `make demo-tui-real-auto` | 不受影响 |
| TUI 手动 | 020 | `make demo-tui-embedded-smoke` | 不受影响（B1 等网络） |
| **调试工作台** | **030（新增）** | **`run/tui-workflow-debugger.sh` / `make tui-debugger`** | **待写 runbook** |

## 决策 / 方案

### 1. 新增 `runbook-030-debugger.md`

写一个可操作的 runbook，覆盖 `--fixture` 零凭证模式下的完整调试旅程：

- 启动：`./run/tui-workflow-debugger.sh --fixture`
- 问题提交（Start Step）→ bootstrap commit → hitl1 interrupt
- composer 输入 answer → hitl1 resume
- 多次 Enter advance → 逐步穿过 topic_planning / wave0 / wave1 / wave2 / hitl2 / readiness / final_delivery
- `/context` 查看节点上下文快照
- `/detach` 干净退出（不触发 cancel）
- README 表补 030 行

### 2. 更新 `_local_demo/README.md`  ✅

- 主表加 030 行（调试工作台 fixture）+ 031 行（调试工作台 embedded）
- TUI 轴线段落补第三格：`030 = 调试工作台（节点边界 step/continue，经 DebugRunDriver）`
- runbook-031：embedded 真实图调试旅程（`--embedded`，需 `.env` + 网络）

### 2.5 embedded recorder 接线  ✅

- `build_real_demo_recipe` 增加 `node_agent_bridge_factory` 可选覆盖
- `build_demo_runtime(mode="real")` threads `node_context_recorder_holder`
- `NodeContextRecorder` 经 holder 注入 real 模式的 bridge，与 fixture 相同模式

### 3. handoff-020 处置

handoff-020 是 020 战役的进行中交接文档。战役已收口（所有 change 归档），
但 B1 第 3 跑仍需网络。处置：handoff-020 保留原样（历史 provenance），B1 待网络
恢复后单独执行。不需要修改。

### 4. runbook-020 保留

runbook-020 描述的是 020 手动 TUI 跑法（shared experience 路径），与 debugger
workbench 是不同的入口。B1 跑通后再看是否需要把 020 合并进 030。当前保留。

## 风险 / 取舍

- [风险] runbook-030 写了但 embedded 模式尚未接线（C4b 只做了 fixture）→ runbook
  明确标注"仅 --fixture 零凭证模式，embedded 待后续版本"。
- [风险] Node Context 在纯 fixture 下可能没有 LLM-bearing invocation（fixture node
  是 deterministic 的）→ runbook 应说明"fixture 模式下 /context 显示空属预期；
  embedded 模式才有真实 LLM invocation 的 context snapshot"。

## 落地关联

- 不需要新的 OpenSpec change——runbook 是本地操作文档，不是 contract。
- 对应 progressive plan §7.3 的 "同步 README、COMMANDS" 任务（已勾选 README/COMMANDS
  的 launcher 行，本 plan 补齐 _local_demo 侧的 runbook 文档）。
