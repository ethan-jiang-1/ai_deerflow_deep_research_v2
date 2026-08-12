# D-002 - Post-Loss Diagnostic Terminology After A-004

> Stage: 6 - `normalize-post-decision-terminology-status`
> 类型: conditional terminology sync
> 状态: **WAITING FOR A-004 DECISION**

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
- A-004 未选择前，本文件不得进入 planning 或 apply。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 条件同步方式获准；等待 A-004
- [ ] 需要修改或补充，原因：
