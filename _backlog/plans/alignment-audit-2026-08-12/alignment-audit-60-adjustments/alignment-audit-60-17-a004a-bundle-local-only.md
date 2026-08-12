# A-004 Option A - Bundle-Local-Only Diagnostics

> Stage: 5 - `reconcile-post-loss-diagnostic-authority`
> 类型: mutually exclusive product decision
> 状态: **PENDING PRODUCT DECISION**

## 调整内容到底是什么

RER/RUS/REJ 统一为所有 supported lifecycle diagnosis 都由 Bundle 持有；Bundle loss 后
inspection 返回 unavailable，不读取 external copy。

## 主要风险

为贴合当前实现而选择这一侧，可能忽略真实 support/audit retention 需求；删除宽松 RER
语义也可能被误解成磁盘上绝不可能残留任何非权威 bytes。

## 可能副作用

planned Support Handoff 必须在 Bundle 生命周期内工作；Bundle 删除后 support 可观察性
降低，但 recovery/authority 模型更单一。

## 控制与停止条件

- 分开说明 bytes 是否可能存在、supported reader 是否读取、participant 是否展示。
- 选择理由必须是产品/lifecycle 决定，不只是“代码目前如此”。
- 选择本项即排除 Option B；若未能满足 support 需求，停止而不是静默删需求。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 选择此合同，排除 A-004 Option B
- [ ] 需要修改或补充，原因：
