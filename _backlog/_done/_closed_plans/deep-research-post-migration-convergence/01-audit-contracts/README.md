# 01 - Audit Contracts：审计规则

> 这一层回答“按什么标准审、什么情况下才允许删”，不是审计结果，也不是执行 checklist。

## 怎么读

不需要默认从 `00` 到 `50` 全部通读。`00` 说明共同基线，其余文件按当前问题查阅：

| 文件 | 它回答的问题 |
| --- | --- |
| [00 - Baseline And Audit Contract](00-baseline-and-audit-contract.md) | 审计范围、证据等级、Candidate 分类和关闭条件是什么？ |
| [10 - Ubiquitous Language](10-ubiquitous-language.md) | 如何判断同义词、概念挤压和 canonical term？ |
| [20 - Retirement And Cutover](20-retirement-and-cutover.md) | public、persisted 或跨边界旧表面何时才允许退役？ |
| [30 - Code And Entry Surfaces](30-code-and-entry-surfaces.md) | 生产代码、helper、export、配置和入口如何分类？ |
| [40 - Tests And Evidence](40-tests-and-evidence.md) | 旧测试、fixture、报告、registry 和负向 guard 如何处理？ |
| [50 - OpenSpec And Records](50-openspec-and-records.md) | spec、CONTEXT、ADR、治理 metadata 和历史记录各由谁拥有？ |

## 它与另外两层的关系

这些合同已经用于完成本轮审计。实际取证结论在 [02 - Audit Findings](../02-audit-findings/)，
由结论形成的后续动作在 [03 - Execution](../03-execution/)。执行某个 Candidate 时只有遇到
删除门槛或证据口径问题，才需要回到这一层。

[返回总导航](../README.md)
