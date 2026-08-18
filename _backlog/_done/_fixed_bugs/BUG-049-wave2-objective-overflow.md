# BUG-049: wave2 synthesis prompt 无界证据投影顶破 NodeExecutionRequest.objective 上限——003 确定性 blocked

> 严重级别: P0 | 发现: 2026-08-18 | 状态: 活跃（本地修复已落地并经 run 4 验证：wave2 在 6 条 accepted refs 下正常完成到 a3，不再触发 objective 溢出）

## 症状

第三次真实 003 run（bundle `b_Ameegc4A2N9W67xBmZ-m2sRSC5FkSstSULWA55hXaxg`，诊断引用
`diag_9756fb3ce18dcd6b1a4d199e`）：

- `RESULT: FAIL`，终态 `blocked`，`output.structured_invalid / candidate_invalid` @
  `wave2_synthesis`，hitl2/readiness/final_delivery 未执行。
- wave2 第 3 次尝试（a3）**20ms 内终止、零模型调用**（事件 75→77，
  13:54:29.475 started → .495 terminal）。
- 前两次 wave2（a1/a2）正常完成；差异 = targeted_evidence 每轮新增 ~2.5-3.7 KiB
  证据提交，第 6 条 accepted ref 后 a3 爆掉。

## 根因

**又是一对"必须一致却不一致"的上限（与 BUG-047 同类）：**

- `domain/context.py`: `NodeExecutionRequest.objective` 上限 **16,384 字符**（全域契约）；
- `domain/synthesis.py`: `MAX_SYNTHESIS_EVIDENCE_TOTAL_BYTES = 96 KiB`（store 读证据预算）；
- `graph/nodes/wave2_synthesis/prompts.py`: `build_synthesis_prompt` 把**全部**证据
  `model_dump` 进 objective，**无任何投影上限**（对比：readiness/final_delivery 各有
  `_bounded_evidence` 8 KiB 上限）。

证据内容 14,821 字节（6 条）经 JSON 序列化 + 转义膨胀 + 脚手架 → objective 超过
16,384 字符 → pydantic `ValidationError`（ValueError 子类）→ `_pre_model_problem`
兜底桶 `candidate_invalid`（多行校验消息不匹配任何类别模式）→ `_exhausted_update`
blocked。已用真实 bundle 数据离线精确复现（ValidationError: "String should have at
most 16384 characters"）。

离线复现证据（真实 bundle，确定性）：

```text
RAISED: ValidationError
  objective: String should have at most 16384 characters
  input starts: 'Use the activated accept.../untrusted-source-data>'
```

## 复现

```bash
cd deep_research_harness
# 任一 003 run 在 wave2 gate 补证轮后证据累积超限时必然触发；
# 离线确定性复现：以 ≥16 KiB 内容的 SynthesisEvidence 序列调用
# build_synthesis_prompt(topic_registry=…, evidence=…, open_questions=…)
# → pydantic ValidationError（objective 超 16384 字符）
```

## 修复关联

已由 change `fix-request-envelope-coherence` 落地（2026-08-18）：信封对齐
（readiness 16,384 / final_delivery 24,576）与 wave2 拟合投影（44,800 字节上限）
均有不变量测试锁死；类别保真（synthesis_request_shape_invalid）纵深防御就位。
待 honest-degraded-delivery 的 003 复跑一并做终验后归档。