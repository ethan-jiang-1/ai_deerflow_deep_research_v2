# 03 - Execution：执行收敛

> 这一层把 9 份 findings 的 54 个 Candidate 变成可逐项实施、验证和归档的 OpenSpec changes。

## 默认阅读顺序

1. 先看 [99 - Progressive Execution](99-progressive-execution.md)：它是最终逐步执行总计划，回答“现在做哪一步”。
2. 只在需要查某个 Candidate 的状态和原始证据时看 [Candidate Register](candidate-register.md)。
3. 准备创建具体 OpenSpec change 时再看 [80 - Remediation Change Map](80-remediation-change-map.md)，确认分组、依赖和 admission gate。

| 文件 | 唯一职责 | 不承担什么 |
| --- | --- | --- |
| [99 - Progressive Execution](99-progressive-execution.md) | P0、Phase A-I、00-07逐步顺序和阶段验收 | 不复制每个 Candidate 的完整证据 |
| [Candidate Register](candidate-register.md) | 54 个 Candidate 的 disposition/admission 总账，并链接回 finding | 不决定 change 的执行顺序 |
| [80 - Remediation Change Map](80-remediation-change-map.md) | Candidate 到00-07共8个changes的唯一映射、workstream、依赖和gate | 不是另一份逐步 checklist |

```text
finding 尾部 Candidate
  -> Candidate Register（状态与证据入口）
  -> 80 Change Map（如何组成 change）
  -> 99 Progressive Execution（何时执行与如何验收）
  -> openspec/changes/<admitted-change>/（真正的实施任务）
```

因此 `80` 和 `99` 不是两个竞争的总计划：`80` 管映射，`99` 管推进。日常继续本计划时，从 `99` 开始。
8是引入owner-scoped program workstream后的全局上限：00支付一次治理成本，01-07承接全部Candidate；内部
workstream/stage不得再裂变，第9项需要计划层明确批准。

[返回总导航](../README.md) | [查看审计结果](../02-audit-findings/)
