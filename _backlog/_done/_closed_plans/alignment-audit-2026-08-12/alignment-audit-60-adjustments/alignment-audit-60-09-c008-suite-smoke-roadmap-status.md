# C-008 - Remove False All-Node Smoke Coverage Claim

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEWED - PLANNING ONLY; NOT AUTHORIZED FOR APPLY**

## 调整内容到底是什么

删除 “Every LLM-Bearing Node has at least one such smoke scenario” 这个错误的 current
claim。保留 Node Cognitive Smoke Scenario 的定义，并以 versioned evaluation case registry
为当前覆盖范围的唯一事实来源。

不在本 cleanup 中为 targeted evidence、readiness 或 final delivery 写 roadmap target、
交付承诺或新的 SHALL；是否补充这些 case 是独立产品决定。

## 主要风险

可能把这些节点的其他确定性或 calibration evidence 错写成“完全无覆盖”，或为求完整而
顺手写入未来 case 的隐性 requirement。

## 可能副作用

读者会更准确地看到 Suite 不是全节点覆盖；这是证明强度校准，不是删除已有 case、测试
或其他 evidence seam。

## 控制与停止条件

- 核对实际 registered cases，区分 Suite case 与其他 evidence seam。
- 只删除错误的全覆盖 current claim，不以 `target` 或 future requirement 替换。
- 不新增 case、Runner、spec requirement 或 test。

## 审阅结论

- [x] 调整内容准确：2026-08-12，registry 当前有 8 个 case，覆盖 HITL1、topic planning、
  Wave0、Wave1、Wave2 与 public controller；targeted evidence、readiness、final delivery
  没有 Suite case，虽各自仍有其他确定性 evidence。
- [x] 风险与副作用已充分披露：只校准当前 claim，不添加 roadmap 或未来覆盖承诺。
- [x] 批准进入 Stage 2 planning（不包含创建 OpenSpec change 或 apply 授权）
- [ ] 需要修改或补充，原因：
