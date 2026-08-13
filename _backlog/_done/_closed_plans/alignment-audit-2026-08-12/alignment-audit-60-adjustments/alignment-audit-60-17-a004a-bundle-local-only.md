# A-004 Option A - Bundle-Local-Only Diagnostics

> Stage: 5 - `reconcile-post-loss-diagnostic-authority`
> 类型: mutually exclusive product decision
> 状态: **CONFIRMED PRODUCT DECISION - 2026-08-12**

## 调整内容到底是什么

已选择的 required contract 是：所有 supported lifecycle diagnosis 都由 Bundle 持有；Bundle
loss 后 inspection 返回 unavailable，不读取 external Journal、diagnostic 或 Support Handoff。

这不声称物理介质上绝不可能存在任何残留 bytes；它只规定那些 bytes 不构成受支持的保留、
读取或 participant presentation 能力。Support Handoff 仍是 `planned` capability，但若实现，
必须在 Bundle 可用的生命周期内工作。

这是一项产品/lifecycle 决定，不是“当前代码这样做，所以规格只能这样写”。现有 Bundle-local
Journal 与无 external fallback 的实现/测试仅是该合同可行且当前相符的证据；后续仍须通过独立
OpenSpec change 收口 RER/RUS/REJ。

## 主要风险

为贴合当前实现而选择这一侧，可能忽略真实 support/audit retention 需求；删除宽松 RER
语义也可能被误解成磁盘上绝不可能残留任何非权威 bytes。

## 可能副作用

planned Support Handoff 必须在 Bundle 生命周期内工作；Bundle 删除后 support 可观察性
降低，但 recovery/authority 模型更单一。

## 控制与停止条件

- 分开说明 bytes 是否可能存在、supported reader 是否读取、participant 是否展示。
- 选择理由必须是产品/lifecycle 决定，不只是“代码目前如此”。
- 已选择本项并排除 Option B；若未能满足 support 需求，停止而不是静默删需求。

## 审阅结论

- [x] 调整内容准确：2026-08-12，supported diagnostics 与 Bundle 同寿命；Bundle loss 后
  inspection 与 control 均为 unavailable，且不读取 external Journal、diagnostic 或 Support
  Handoff。
- [x] 风险与副作用已充分披露：Bundle 删除后 support/audit 可观察性降低；Support Handoff
  必须在 Bundle 可用期间工作；“未支持外部留存”不等于断言物理 bytes 绝不会残留。
- [x] 已选择此合同，排除 A-004 Option B：产品 owner 于 2026-08-12 确认选择 Option A。
- [ ] 需要修改或补充，原因：
