# C-007 - Policy Cardinality

> Stage: 2 - `retire-stale-context-concepts`
> 类型: `UNAMBIGUOUS-RETIRE`
> 状态: **REVIEW REQUIRED**

## 调整内容到底是什么

将 “choose one/only policy” 改为“每个 trigger 路由一个 canonical policy；一个 change
可以因多个 trigger 选择多个 policies”，保持 Focus Card 的 comma-separated contract。

## 主要风险

只强调多 policy 可能诱导 author 每次加载全部 policy，破坏最小上下文原则；漏掉排他
措辞则仍会与 checker 冲突。

## 可能副作用

多 trigger change 可能产生更多 review records，增加 planning/review 成本；checker
行为本身不会变化。

## 控制与停止条件

- 同时保留 “only triggered policies”。
- 用 single-trigger 与 multi-trigger 示例人工核对。
- 不修改 checker；若文案需改变 parser/validation 才成立，停止。

## 审阅结论

- [ ] 调整内容准确
- [ ] 风险与副作用已充分披露
- [ ] 批准进入 Stage 2 planning
- [ ] 需要修改或补充，原因：
