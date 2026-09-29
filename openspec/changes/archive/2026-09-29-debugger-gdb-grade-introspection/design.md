# Design

## Context

GDB 标尺第二轮挤压的三个缺口（bt / print var / watch）。`/inspect` 已覆盖
work-unit 清单（info threads 对应物）；`/replay` 覆盖事后回放。BundleLocalState 是
43 字段 dataclass → 字段白名单直接来自 `dataclasses.fields`。

## Goals / Non-Goals

**Goals:** /bt（路径回看）、/state（单字段有界查询）、/watch（观察点即停）、快照携带
命中字段；全部无头可验。

**Non-Goals:** 条件表达式断点、反向步进、任何状态写入；不改 hitl 节点与图。

## Decisions

1. **观察点是会话级配置不是边界命令**：`DebugRunDriver.set_watch_fields(bundle_id,
   fields) -> tuple[str, ...]`（返回接受集；未知字段名整组拒绝）。不经 execute/ledger
   ——它不是边界变更，与 stop_policy 同级。快照加法字段
   `watch_hits: tuple[str,...] = Field(default=(), max_length=8)` 携带命中。
2. **比对语义 = GDB watch**：基线取**驱动启动时**的观察字段值；每个边界提交后与基线
   比对，任一变化 → 停 + 命中入快照 + **基线推进到当前值**（重复驱动不空触发）。
   驱动循环每边界本就要读 durable state（断点检查），观察比对复用同一次读取。
3. **/state 有界渲染**：值 repr 截断 160 字符；tuple 截前 6 项；无参列字段名（43 个
   分行太长 → 一行逗号连接班）。未知字段 → `未知字段: <name>（/state 看字段清单）`。
4. **/bt 分组渲染**：连续同名 visit 合并计数（`hitl1×3`），尾部标注
   `· 当前: <waiting_for>（等待）`；无 trace → `轨迹: （尚无已提交边界）`。
5. **REQ 登记**：LDD-009、RED-017。

## Risks / Trade-offs

- 每边界一次 `read_state` 已存在（断点检查），观察比对复用同读，无新增 I/O。
- 观察字段值可能很大（如 execution_trace）→ /state 截断渲染；比对用完整值。
- watch 基线按驱动启动捕获：设置观察点**之前**发生的变化不触发（GDB 语义同）。
