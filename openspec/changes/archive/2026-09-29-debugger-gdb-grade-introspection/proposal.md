# Proposal

## Why

以 GDB 为标尺的第二轮挤压发现三个"像 debugger 但我们还没有"的缺口：**`bt`（怎么走
到这的）**——attach/长会话后没有任何命令能回看走过的节点路径；**`print var`**——想知道
"profile 定了什么深度"这类单字段查询只能翻大 JSON；**`watch`（观察点）**——"字段一变
就停"（如 `degraded_profile` 一变、`proposal_version` 一变）是 GDB 最锋利的武器，对
非确定性 Agent 研究尤其有价值（连续推进时只在关键状态翻转处停下）。

## What Changes

- 驱动会话新增观察点配置：`set_watch_fields(bundle_id, fields)`（只接受
  `BundleLocalState` 的类型化字段名，拒绝未知字段）；drive 在每个边界后比对观察字段
  与驱动启动时的基线，**任一变化即停**，命中字段经快照 `watch_hits`（加法字段）携带。
- 工作台三个新命令：`/bt`（走过的节点路径 + 当前位置，连续 visit 计数显示如
  `hitl1×3`）、`/state [字段]`（单字段有界查询；无参=字段名清单）、`/watch [字段]`/
  `/unwatch <字段>`（观察点管理，列表/增删）。
- 驱动快照加法扩展：`watch_hits: tuple[str, ...] = ()`。

## Change Focus

- **Primary module / causal owner**: `runtime/debug_driver.py`（观察点语义）+
  `scripts/demo_tui.py`（三个命令的呈现）；字段权威是 `runtime/bundle_lifecycle.py`
  的 `BundleLocalState`（43 个类型化字段即白名单）。
- **Seam classification**: `deterministic-guardrail`——观察点是确定性状态比对；bt/state
  是既有事实的有界投影；无认知面、无新 authority。
- **Question**: 操作者能否用 GDB 级的内省回答"怎么走到这的 / 某个状态字段现在是什么 /
  字段一变就停"？
- **Necessary adjacent/external contracts**: `local-workflow-debug-driving`（观察点语义
  与快照加法字段）；`research-demo-tui`（三命令渲染）。
- **Evidence seam**: 驱动矩阵（观察点停止/拒绝未知字段）+ TUI pilot（/bt、/state、
  /watch 渲染）+ 既有门禁；live 快速档复跑。
- **Not in scope**: 条件断点（表达式）、反向步进、改状态写入；`deerflow/` 不动。
- **Triggered review policies**: `none: 确定性状态比对与有界投影，无新 authority、
  无认知面变化。`

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `local-workflow-debug-driving`: LDD-009 观察点（会话级字段观察，边界比对即停，
  未知字段拒绝）。
- `research-demo-tui`: RED-017 工作台 `/bt`、`/state`、`/watch` 内省命令。

## Impact

- `domain/debug_driving.py`（快照加法字段 watch_hits）
- `runtime/debug_driver.py`（set_watch_fields + 驱动循环比对）
- `scripts/demo_tui.py`（/bt、/state、/watch、/unwatch + 渲染）
- 测试：矩阵观察点红绿、pilot 三命令红绿
