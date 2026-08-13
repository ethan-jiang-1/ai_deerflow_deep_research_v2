# A-003 Option B - Rubric Is Completely Review-Only

> Stage: 4 - `reconcile-evaluation-rubric-authority`
> 类型: mutually exclusive product decision
> 状态: **REJECTED ALTERNATIVE - 2026-08-12**

## 调整内容到底是什么

CES 保持完全 review-only；EVH required behavior 改为 execution admission 不解析
criteria，当前实现差异登记为独立 code change。

## 主要风险

required behavior 与当前 admission/typed fixtures 不一致；若只改 spec 却不披露，会制造
“文档已对齐、代码未对齐但看不见”的新假象。

## 可能副作用

后续实现可能需要删除或重构 criterion binding，影响 manifest、fixture control-integrity
和测试；这些副作用本 no-code plan 不实施也不能验证。

## 控制与停止条件

- 明确 `DEFERRED-CODE-CHANGE` 与受影响 seam。
- 本 Stage 不改实现，不能把 A-003 标成 code-conformant。
- 选择本项即排除 Option A；实现 work 只能在另一个获授权 code change 中开始。

## 排除理由

产品 owner 选择了 Option A：criterion IDs 可以只作为 admission 的 control-integrity
metadata。故本项“完全不解析 criteria”的合同不成立。此排除不是对 review-only 价值的否定：
Rubric criteria 正文、model-facing input 和 quality verdict 仍然完全留在 review 侧。

## 审阅结论

- [x] 已审阅：本项完整表达了被拒绝的另一条合同及其 code-gap 风险。
- [x] 已排除：2026-08-12，产品 owner 选择 A-003 Option A，而非 Rubric 完全 review-only。
- [x] 排除后仍保留其风险记录，避免日后误将 Option A 扩展为 Rubric 正文或 verdict 可执行。
- [ ] 需要修改或补充，原因：
