# BUG-059: wave2 synthesis 别名映射不收录 evidence 内 claim_id，模型引用 claim 被拒致 blocked

> 严重级别: P0（阻断——004 第 4 跑 wave2_synthesis 初始+repair 两次候选均 `synthesis_finding_backing_ref_invalid` 后 blocked） | 发现: 2026-08-19 | 状态: 已修复（change `fix-synthesis-claim-ref-aliases`；待 004 复跑确认归档）

## 症状

真实 mode-004 run（bundle `b_sLVVSNG2v8O9FFI1fbYJyZGESYBVBs3ByO571yciGOg`，
BUG-058 修复后 wave0/wave1 均 a1 一次通过）在 wave2_synthesis 阻断：
初始 + repair 两次候选都判 `synthesis_finding_backing_ref_invalid`。

## 根因

`wave2_synthesis/node.py::_evidence_aliases` 从每份 evidence JSON 提取可投影
别名，但只认 `source_id` / `canonical_url` / `support_refs` / `counter_refs`
四个键——**不提取 `claim_id`**。

wave1 result.json 的一等公民实体是 `claims[].claim_id`
（`claim:w1_c1` ...），synthesis 模型把 finding 的 `backing_refs` 指向它所
综合的那几条 claim——语义完全正确、id 真实存在于 accepted evidence——却因
别名盲区未被投影到所在 evidence 的 submission_ref，落入
`backing_refs <= accepted` 检查失败。

真实模型复现（2026-08-19，temperature 0.2，json_object，完整 24KB entry
预算无截断）：19 个 finding 的 backing_refs 里，14 个用 source_id（合法，
aliases 已覆盖）、6 个用 `claim:w1_c1`–`c6`（盲区）→ 整份候选被拒。模型还
观察到第二种失败形状：简写 `src1`–`src5`（wave1 worker 在 claims
support_refs 里自造的简写——aliases 已天然覆盖，因为 support_refs 被提取）。

与 BUG-058 同缺陷类：真实模型引用形状 vs 确定性契约边界的盲区。

## 复现

```bash
cd deep_research_harness
# /tmp/repro_synthesis.py：用 blocked bundle 的两份真实 evidence 构建
# build_synthesis_prompt → 调真实 DeepSeek → parse_synthesis_output →
# _validate_synthesis_semantics
```

实测输出（节选）：

```json
{"finding_id":"f_14","backing_refs":["claim:w1_c1"]},
{"finding_id":"f_15","backing_refs":["claim:w1_c2"]},
```

`_evidence_aliases` 对该 evidence 返回 11 个别名（source_id/canonical_url/
support_refs），不含任何 `claim:*` → 投影失败。

## 修复关联

change `fix-synthesis-claim-ref-aliases`：

1. `_evidence_aliases` 的提取键加入 `claim_id`（与 source_id 并列，同样只
   收 evidence JSON 内 dict 键命中 `claim_id` 的字符串值）——claim ref 投影
   到其所在 evidence 的 submission_ref，`accepted` 检查自然通过；
2. 横切说明：`question_id`（open_questions）不在本次修复——synthesis 对
   question 的引用走 `source_questions`/`resolved_questions` 的确定性处置
   契约（独立校验路径），无 observed failure，不扩大证据外范围。

修复落地后 004 复跑验证 wave2_synthesis 通过。
