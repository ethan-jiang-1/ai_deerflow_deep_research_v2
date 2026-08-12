# C-010.a - Final Report Artifact Versus Export

> Stage: 2 - `retire-stale-context-concepts`
> 类型: current claim retirement
> 状态: **REVIEWED - PLANNING ONLY**

## 调整内容到底是什么

保留 Bundle 中 current `final/report.md` artifact；退役“Primary User 已可 reopen/copy/export”
这一 current claim。它没有当前 public entry，本轮也不把未来的读取、复制或导出预先定义为
`planned`，不再由文件存在推导用户能力或产品承诺。

## 主要风险

状态拆分可能误删真实 report artifact，或反过来继续把 artifact 路径当 public export
contract。

## 可能副作用

词典仍须区分 artifact 与 capability；收回旧 ADR/CONTEXT 的措辞会显露一个未被拥有的
产品空缺。未来若需要该能力，必须另开产品 change，不能把它从文件路径中推导出来。

## 控制与停止条件

- current artifact 链接 final-delivery owner。
- export 明确没有 current entry，也不是本轮创建的 future commitment。
- 将来如要实现，独立定义 public entry、authorization、read boundary 和 retention semantics。
- 不修改 publisher、Bundle 或 public lifecycle API。

## 审阅结论

- [x] 调整内容准确：2026-08-12，保留 current `final/report.md` artifact；退役 Primary User
  已可 reopen/copy/export 的 current claim，不将该能力预先标为 `planned`。
- [x] 风险与副作用已充分披露：不删除 artifact，不把受控内部路径当 public contract；未来
  若要实现 report access/export，必须以独立产品 change 定义边界。
- [x] 批准进入 Stage 2 planning（不包含创建 OpenSpec change 或 apply 授权）
- [ ] 需要修改或补充，原因：
