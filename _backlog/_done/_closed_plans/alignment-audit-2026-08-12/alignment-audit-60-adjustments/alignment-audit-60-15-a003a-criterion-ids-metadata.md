# A-003 Option A - Criterion IDs Are Execution Admission Metadata

> Stage: 4 - `reconcile-evaluation-rubric-authority`
> 类型: mutually exclusive product decision
> 状态: **CONFIRMED PRODUCT DECISION - 2026-08-12**

## 调整内容到底是什么

已选择的 required contract 是：Rubric identity 和 criterion IDs 可以被 execution admission
读取，只为校验 case/fixture 的 control integrity。Rubric criteria 的正文不进入 model-facing
input，Runner 不据此产出 quality verdict。Stage 6 才同步 ADR/CONTEXT。

这是一项产品边界决定，不是“因为当前代码这样做，所以规格必须追随代码”。当前实现只能
作为这条窄边界可行的证据；后续仍须通过独立 OpenSpec change 使 CES/EVH 给出同一个答案。

## 主要风险

“metadata”可能成为扩大 Rubric execution authority 的模糊入口，未来把 criteria content
或 verdict 逐步带入 Runner。

## 可能副作用

CES 的 “Rubric is not execution input” 必须改成更窄定义；review-only 心智模型会增加
identity、criterion IDs、content 三者的区分成本。

## 控制与停止条件

- spec 必须分别定义 identity、criterion IDs、content、model-facing input、quality verdict。
- 明确禁止 content/judgment authority crossing，并验证当前实现仅满足该窄边界。
- 已选择本项并排除 Option B；若 current implementation 超出窄边界，停止并登记 code gap。

## 审阅结论

- [x] 调整内容准确：2026-08-12，Rubric 的 identity 与 criterion IDs 仅作为 admission
  control-integrity metadata；criteria 正文、model-facing input 与 quality verdict 不跨入 Runner。
- [x] 风险与副作用已充分披露：metadata 不得成为扩大 Rubric execution authority 的入口；CES
  的 “not execution input” 必须在后续 spec change 中按上述五层边界收窄定义。
- [x] 已选择此合同，排除 A-003 Option B：产品 owner 于 2026-08-12 确认选择 Option A。
- [ ] 需要修改或补充，原因：
