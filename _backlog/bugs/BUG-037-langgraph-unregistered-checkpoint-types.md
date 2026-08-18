# BUG-037: langgraph checkpoint 反序列化 "unregistered type" 警告（未来版本会阻塞）

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 活跃

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

无关联 change。修复方向：在 harness 的 checkpoint 序列化配置中显式注册应用
类型（或改为纯 dict/原始类型投影），并在升级 langgraph 前完成；可先用
`LANGGRAPH_STRICT_MSGPACK=true` 做一次全量测试扫描出全部未注册类型。
