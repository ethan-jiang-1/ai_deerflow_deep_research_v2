# A-004 Option B - External Diagnostic Retention

> Stage: 5 - `reconcile-post-loss-diagnostic-authority`
> 类型: mutually exclusive product decision
> 状态: **REJECTED ALTERNATIVE - 2026-08-12**

## 调整内容到底是什么

Required behavior 允许特定 external diagnostic 在 Bundle loss 后留存，同时规定它不能
恢复、选择或授权 Run；实现工作另案定义 typed owner、retention/redaction、authorization、
reader 和 deletion semantics。

## 主要风险

非权威记录可能事实上变成 shadow authority，或造成隐私、删除、授权和数据寿命不清；
只改 spec 而没有实现 owner 会留下重大 conformance gap。

## 可能副作用

后续需要新增 schema/store/reader/tests 和用户呈现，扩大数据治理面；“删除 Bundle”不再
等同于删除全部诊断 bytes。

## 控制与停止条件

- 本 Stage 只作产品/spec 决定并登记 `DEFERRED-CODE-CHANGE`。
- 没有完整 lifecycle owner 前，不把该 capability 写成 current。
- 选择本项即排除 Option A；任何实现需另一个获授权 code change。

## 排除理由

产品 owner 选择了 Option A：supported diagnostics 与 Bundle 同寿命，Bundle loss 后不支持
外部读取。这不否定“外部资料永远不能形成 lifecycle authority”的 invariant；相反，该
invariant 继续约束任何未来另行提出的数据能力，但本项不建立 post-loss retention capability。

## 审阅结论

- [x] 已审阅：本项完整表达了被拒绝的 external retention 合同及其 data-governance/code-gap 风险。
- [x] 已排除：2026-08-12，产品 owner 选择 A-004 Option A，而非 external diagnostic retention。
- [x] 排除后仍保留其风险记录，避免以后将“external record 无 authority”误读成“已允许外部留存”。
- [ ] 需要修改或补充，原因：
