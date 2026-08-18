# BUG-051: wave1 open-question id 跨 work unit 碰撞，dict() 去重静默丢弃问题文本

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 活跃

## 症状

run 3 bundle（b_Ameegc4A…，已销毁，数字来自排障摘录）实测
`read_wave1_open_questions(accepted_refs)` 返回两条**同 id 不同文本**的 open
question：

```text
('q:w1_q1', 'Does the January-October 2024 CABIA power battery installation…')   # 来自 w0000
('q:w1_q1', "Did CABIA's January-October 2024 total power battery install…")     # 来自 w0001
```

wave1 repair 重跑（w0001、w0002，runbook §6 认定为正常）使多个 work unit 各自
从 `q:w1_q1` 起编号，id 只在 work unit 内唯一，跨 unit 碰撞。

## 根因

`wave2_synthesis/node.py`（open questions 解析处）：

```python
resolved_texts = await …read_wave1_open_questions(wave0_refs)
text_by_id = dict(resolved_texts)   # 同 id 后者覆盖前者——前一条文本静默丢失
```

`dict()` 以 id 为键，碰撞时**后读入的文本覆盖先读入的**，被覆盖的 open question
从未进入 synthesis prompt，也无需被 disposition——静默数据丢失，无任何事件/日志。
（graph state 的 `wave1_open_questions` 只有 1 条，也说明上游投影即已丢一条。）

## 复现

任一触发 wave1 repair 重跑的 003 run（常态路径）+ 检查
`read_wave1_open_questions` 返回的 (id, text) 列表是否存在同 id 多文本。

## 修复关联

待讨论：id 应带 work 前缀（`q:w0000:w1_q1`）全局唯一，或解析处对碰撞显式
失败/合并并记事件。涉及 wave1 契约与 wave2 disposition 合同，建议随 BUG-050
一并进 change 评审。

## 修复关联

已由 change `honest-degraded-delivery` 落地（2026-08-18）：实现与回归见该
change 的 tasks/design；真实 003 复跑验证见 runbook §5.1/§7。
