# BUG-037: langgraph checkpoint 反序列化 "unregistered type" 警告（未来版本会阻塞）

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 已修复（openspec/changes/honest-delivery-and-real-run-diagnostics）

## 症状

每次真实 run（003；002 无此输出）都会在终端打印一批：

```
Deserializing unregistered type deerflow_deep_research.domain.state.ContentRef
  from checkpoint. This will be blocked in a future version.
  Set LANGGRAPH_STRICT_MSGPACK=true to block now, or add to allowed_msgpack_modules
  to allow explicitly: [('deerflow_deep_research.domain.state', 'ContentRef')]
Deserializing unregistered type deerflow_deep_research.domain.work_units.AttemptStatus ...
Deserializing unregistered type deerflow_deep_research.domain.wave1.Wave1OpenQuestionRef ...
```

功能当前正常（checkpoint 能读），但 langgraph 已声明未来版本会**阻塞**未注册
类型的反序列化——届时真实 run 的 checkpoint 恢复会直接失败。

## 根因

checkpoint（msgpack 序列化）写入时使用了应用自有 pydantic 类型
（`ContentRef`、`AttemptStatus`、`Wave1OpenQuestionRef` 等），但未注册进
langgraph 的 `allowed_msgpack_modules`。属于应用与框架的注册契约缺失，是
时序炸弹：升级 langgraph 后 003/全部真实 run 的恢复路径会断。

## 复现

任意真实 run（`make demo-real-scripted ...`）终端输出尾部可见；或在应用
checkpoint 恢复路径设置 `LANGGRAPH_STRICT_MSGPACK=true` 即可让警告变成硬错误。

## 修复关联

已修复：`openspec/changes/honest-delivery-and-real-run-diagnostics/`。根因比
原记录更具体：(a) 真实 run 的 Bundle 内图存储 `open_graph_checkpoint` 打开
`AsyncSqliteSaver` 时**未接**应用 serde（用库默认），而 GraphHost 早已接；
(b) `Wave1OpenQuestionRef`（`wave1_open_questions` 投影的实类型）不在
`allowed_msgpack_modules`。修复：注册第三类型 + saver 打开后立即赋
`build_deep_research_checkpoint_serde()`。确定性证据：
`tests/unit/test_checkpoint_msgpack.py`（三类型往返、strict 子进程用例、
saver 接线验证）；`Makefile` `test-strict-checkpoint` 车道纳入
`tests/unit/test_bundle_graph_journal.py`（全图经 bundle 图存储跑在
`LANGGRAPH_STRICT_MSGPACK=true` 下，87 passed，零 unregistered 警告）。原"无
关联 change"段落系修复前状态。

## 修复后真机验证（2026-08-18，tasks.md 6.1）

修复后 003 run（bundle `b_T0Pu…`，真实 DeepSeek + Tavily）：完整 run 终端
**零 "Deserializing unregistered type" 警告**（修复前每次真实 run 必现）；
事后诊断用应用 serde 成功解码 `graph.sqlite` 全部 checkpoint writes
（`latest_gate_feedback` × 6、`degraded_decisions` × 1、`unresolved_gaps` × 4
等），证明 bundle 图存储的序列化边界与注册类型集完全一致、恢复路径健康。
