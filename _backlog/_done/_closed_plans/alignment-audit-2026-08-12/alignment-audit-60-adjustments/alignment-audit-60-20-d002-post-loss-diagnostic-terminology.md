# D-002 - Post-Loss Diagnostic Terminology After A-004

> Stage: 6 - `normalize-post-decision-terminology-status`
> 类型: conditional terminology sync
> 状态: **STAGE 6 PLANNING COMPLETE - APPLY NOT AUTHORIZED**

## 调整内容到底是什么

按 Stage 5 决定分别写清 bytes retention、supported reader、participant presentation 和
no-authority/no-recovery；Support Handoff 仍按已确认的 capability status 表述。

## 主要风险

用一个 “retained/unavailable” 词概括三个问题会重新制造歧义；planned Support Handoff
也可能被误写成 current external store。

## 可能副作用

glossary 会更精确但更长；若实现与 required behavior 不同，文档必须同时展示两层事实，
不会再有简单的“一句话答案”。

## 控制与停止条件

- bytes、reader、presentation 三个问题逐项回答。
- 任何 code gap 继续标 deferred；CONTEXT 不新增 schema、reader 或 authorization behavior。
- A-004 已在 Stage 5 选定并同步；本文件只允许其既有决定进入 Stage 6 planning，仍不得
  以此授权 apply。

## 审阅结论

- [x] 调整内容准确：只投影 Stage 5 已接受的 bytes/reader/presentation 边界。
- [x] 风险与副作用已充分披露：见 Stage 6 D-002 Adjustment Record。
- [x] 条件同步方式获准；A-004 已完成，Stage 6 planning 已获授权。
- [ ] 需要修改或补充，原因：

Stage 6 planning 的 closed occurrence allowlist、Before/After、风险、副作用、控制和
verification 记录于
`stage-6-planning/00-stage-6-planning-baseline-and-adjustment-records.md`。任何实际 glossary
或 ADR 修改仍等待单独 `APPLY` 授权；`DEFERRED-TOOLING-CHANGE A-004-T01` 不在本 Stage。
