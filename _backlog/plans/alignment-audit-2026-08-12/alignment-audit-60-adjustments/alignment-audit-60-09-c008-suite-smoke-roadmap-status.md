# C-008 - Suite Smoke Roadmap Status

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `RELABEL-PLANNED`
> 状态: **REVIEW REQUIRED**

## 调整内容到底是什么

用 registry 的实际有限范围描述 current Suite coverage；将 targeted evidence, readiness,
final delivery 等未覆盖节点的完整覆盖写成 roadmap target，而不是 current fact 或新
SHALL。

## 主要风险

可能把其他 calibration evidence 错写成“完全无覆盖”，或把 target 重新写成带期限/义务
的隐性 requirement。

## 可能副作用

读者对当前 evaluation 完整度的判断会降低；这是证明强度校准，不是删除已经存在的
case。没有 active owner 的 target 也可能长期未完成。

## 控制与停止条件

- 列出实际 registered cases，区分 Suite case 与其他 evidence seam。
- 使用 `target`，不用 required/current 语气。
- 不新增 case、Runner、spec requirement 或 test。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 2 planning
- [ ] 需要修改或补充，原因：
