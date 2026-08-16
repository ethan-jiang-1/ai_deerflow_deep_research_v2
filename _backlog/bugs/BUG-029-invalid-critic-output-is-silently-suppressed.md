# BUG-029: 非法 critic 输出被静默丢弃

> 严重级别: P1 | 发现: 2026-08-15 | 状态: 活跃

## 症状

当 Wave1 critic 返回语法正确但不符合结构化契约的结果时，用户最终只看到缺少 review artifact
或 `research.blocked`。Event Journal 没有记录具体的验证阶段、受影响的 critic、字段或安全的
错误类别。定位 BUG-027 只能通过离线安全解码 checkpoint，而不是正常诊断接口。

## 根因

`graph/nodes/wave1/review.py::_dispatch_missing_reviews` 捕获 `ValueError` 后直接 `continue`。
非法输出既不产生 review artifact，也没有产生有界、脱敏的诊断事件；后续 gate 只能观察到
artifact 缺失，失去了直接因果信息。

## 复现

让任一 Wave1 critic 返回不能通过其 Pydantic/枚举验证的 JSON。执行 `_dispatch_missing_reviews`
后，检查没有该 critic artifact，且 Journal 中不存在可区分该契约失败的 validation code 或
diagnostic reference。

## 修复关联

需要新的 OpenSpec change：在不保存原始模型输出、prompt 或密钥的前提下，写入固定的 critic
种类、validation stage、闭合错误代码、关联 work/review id 和可选 diagnostic reference。该
事件只能是观察，不能参与路由或生命周期判定。

2026-08-16 现状同步：`graph/nodes/wave1/review.py::_dispatch_missing_reviews` 仍为
`except ValueError: continue`，无有界诊断事件；runtime-observability 三件套已归档
（event recorder 与 Journal 基础设施可用），但尚未覆盖该 critic 校验失败路径。BUG-027
（枚举契约）已结案，本卡承接其"非法结果可诊断性"部分。
