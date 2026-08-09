# BUG-024: real demo (`make demo-real-scripted`) flakily fails at different nodes with deepseek-v4-flash

> 严重级别: P1 | 发现: 2026-08-10 | 状态: 活跃

## 症状

`make demo-real-scripted`（默认问题，deepseek-v4-flash）连续三次真实 run，每次都挂在**不同节点、不同失败类别**：

| Run | 失败点 | 失败类别 | 现象 |
| --- | --- | --- | --- |
| 1（修复前） | wave1 | `agent_invocation` | 模型单次响应并发调多个 web 工具，超 `tool_call_limit=1`，被拒 3 次 → `gate_blocked` |
| 2（修复后） | topic_planning | `budget.exhausted` | 零工具节点的 `per_call_output_token_cap=2048` / `wall_time=60s` 被超 |
| 3（修复后） | wave0 | `structured_output` | 模型产出 JSON 不合规（`sources/baseline_facts/limitations` 契约），1/3 topic 三次尝试全败 |

诊断引用: `diag_49S1w5uxd8C_1bcU_Fu5ZPgX`（wave1）、`diag_4dfKqbo-2X8Y3F_jgw8Q5Bjt`（topic_planning）、`diag_YIGwIwtleMN6mnybBiwJqDwb`（wave0）。指纹分别为 `754e1a58…`（wave1）、`26c9dcf2…`（topic_planning）。

## 根因

**deepseek-v4-flash 与 demo 各节点的紧契约/紧预算系统性不匹配**。demo 每个节点都有严格约束（`max_model_calls=1`、`per_call_output_token_cap=2048`、`wall_time=60s`、`tool_call_limit=N`、精确 JSON 结构），这些约束显然按更守约的模型校准。deepseek-v4-flash 每次 run 随机违反其中一个 → 触发该节点的 fail-closed → run 失败。这不是单一缺陷，而是一整类「模型不守约 vs 严格契约」的横切问题。

具体到 wave1：请求 `tool_call_limit=1`（spec 要求「exactly one web search call」），模型在单次响应发 2+ 工具调用被拒。该问题已被 `tool-window-truncates-eager-parallel-calls` 修复（窗口改为「执行上限」，超额取首弃余）。

## 复现

```bash
cd deep_research_harness && make demo-real-scripted
```
无 `--question`，用默认问题。每次 run 约 4 分钟，随机在 topic_planning / wave0 / wave1 失败（wave1 修复后未再观察到）。

## 修复关联

- 已归档: `openspec/changes/archive/2026-08-10-tool-window-truncates-eager-parallel-calls/` —— 修 wave1 工具窗口（模型超额调用 → 截断而非 fail run）。
- 未解决（本 bug 的范围）: topic_planning `budget.exhausted`、wave0 `structured_output` 等其它节点紧契约，仍是 open。方向二选一：
  1. 换更守约的 demo 模型（如 `deepseek-v4-pro`，需先验证），属配置选型；
  2. 逐节点放宽预算/契约（各自独立 OpenSpec change），工作量最大。
