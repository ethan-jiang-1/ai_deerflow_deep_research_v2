# C-005.b - Remove Current Dependency On Archived Change

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `UNAMBIGUOUS-RETIRE` + `RELOCATE-LINK-OWNER`
> 状态: **REVIEWED - PLANNING ONLY; NOT AUTHORIZED FOR APPLY**

## 调整内容到底是什么

current CONTEXT 不再以 archived change 名称作为当前规则来源，改链 current
policy/spec/ADR；archive artifact 本身保持原样。

## 主要风险

可能误把“解除 current 依赖”做成删除历史，或者丢失决定 provenance。

## 可能副作用

读者不再从 glossary 直接看到历史 change 名称，需要通过 ADR/Git 或 archive 导航追溯
来源。

## 控制与停止条件

- 不修改 archive；current owner link 与 historical provenance 分开。
- archive 搜索命中不作为 current-state 证据。
- 若 current owner 未找到，停止而不是把 archive 继续当 runtime/behavior authority。

## 审阅结论

- [x] 调整内容准确：2026-08-12，退役“该纪律来自 archived plan”的当前来源宣称；
  seam-first 规则和现有 `local-context` policy 链接保留。
- [x] 风险与副作用已充分披露：关闭计划仅从 current glossary 退场，历史 artifact 保留，
  追溯仍可经 archive、ADR 或 Git 完成。
- [x] 批准进入 Stage 2 planning（不包含创建 OpenSpec change 或 apply 授权）
- [ ] 需要修改或补充，原因：
