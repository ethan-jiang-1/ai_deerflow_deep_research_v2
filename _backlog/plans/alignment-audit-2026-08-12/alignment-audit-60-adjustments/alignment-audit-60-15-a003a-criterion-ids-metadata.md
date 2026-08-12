# A-003 Option A - Criterion IDs Are Execution Admission Metadata

> Stage: 4 - `reconcile-evaluation-rubric-authority`
> 类型: mutually exclusive product decision
> 状态: **PENDING PRODUCT DECISION**

## 调整内容到底是什么

CES/EVH 明确 criterion IDs 可以被 admission 读取并校验 control integrity；Rubric content
不进入 model-facing input，Runner 不产出 quality verdict。Stage 6 才同步 ADR/CONTEXT。

## 主要风险

“metadata”可能成为扩大 Rubric execution authority 的模糊入口，未来把 criteria content
或 verdict 逐步带入 Runner。

## 可能副作用

CES 的 “Rubric is not execution input” 必须改成更窄定义；review-only 心智模型会增加
identity、criterion IDs、content 三者的区分成本。

## 控制与停止条件

- spec 必须分别定义 identity、criterion IDs、content、model-facing input、quality verdict。
- 明确禁止 content/judgment authority crossing，并验证当前实现仅满足该窄边界。
- 选择本项即排除 Option B；若 current implementation 超出窄边界，停止并登记 code gap。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 选择此合同，排除 A-003 Option B
- [ ] 需要修改或补充，原因：
