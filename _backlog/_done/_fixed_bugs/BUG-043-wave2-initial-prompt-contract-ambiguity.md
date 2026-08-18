# BUG-043: wave2 初始提示词输出契约区分度不足，模型镜像了证据里的 wave1 claims 形状

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 已修复 ✅

## 症状

同 BUG-040 的 run：wave2 **首轮**输出不是 synthesis 契约（findings/relations/
gaps），而是一个完整、格式良好的 **wave1 claim-verdict JSON**（`claims[]` 带
`claim_id/verdict/support_refs/counter_refs/reason`）——被 `SynthesisResult` 的
`extra_forbidden` 拒绝（`claims` 不是合法键）。触发 repair 后模型立刻产出了
正确形状，说明它理解力足够，首轮是被证据形状"带偏"了。

## 根因

（假设，标为待验证）wave2 prompt 的证据块本身就是 claim-verdict 形状——
`_evidence_aliases()` 甚至专门从证据里提取 `support_refs/counter_refs`（wave1
verdict 字段）；而输出契约 `_expected_synthesis_output()` 只是一份抽象 key
清单（required_keys 等），没有具体示例对象，也没有"这不是 claim 复核任务、
不要返回 claims 数组"的对照。证据形状的镜像压力强于契约描述。

## 复现

解码 run `b_SOh4…` 的 `graph.sqlite` `messages` 倒数第三条（wave2 首轮输出，
712 字符的 claims payload）对照 `_expected_synthesis_output()`。

## 修复关联

Change `wave2-synthesis-validation-feedback-contract`（WSN-011）：
`_expected_synthesis_output()` 增 `"example"` 键（一个最小合法
findings/relations/gaps 对象）并在 `"instruction"` 中加负面对照（"return
findings/relations/gaps, NOT a wave1 claims verdict list (`claims[]` …)"）；
初始与 repair 共用同一 builder。确定性测试：
`test_expected_output_contract_has_example_and_negative_contrast`（新增）。

