# 02 - Audit Findings：审计结果

> 这一层是审计真正“挖出来的内容”。每份文件末尾的 `## 最终审计 Candidate` 是该领域的最终动作候选。

## 怎么读

只关心某个领域时直接打开对应文件；不必先读审计合同。想看全部 54 个动作及其状态，转到
[Candidate Register](../03-execution/candidate-register.md)。

| 文件 | 审计对象 | Candidate |
| --- | --- | --- |
| [70 - Node Cognition](70-node-cognition-findings.md) | node 身份、AI-facing contract、capability migration 和术语 | NC-C01..C03 |
| [71 - Run, Bundle, Session And Observation](71-run-session-and-observation-findings.md) | lifecycle authority、Bundle/Journal owner、workbench 和负向 guard | RS-C01..C05 |
| [72 - Fixture And Implementation Mode](72-fixture-mode-findings.md) | fixture graph、full-fake 路径和持久化 implementation mode | FM-C01..C04 |
| [73 - Entry And Configuration](73-entry-and-configuration-findings.md) | 产品/运维入口、demo helper、constructor 和配置兼容 | EC-C01..C07 |
| [74 - Tests And Evidence Assets](74-test-and-evidence-asset-findings.md) | test scaffold、registry、历史报告和 current evidence policy | TA-C01..C07 |
| [75 - Persisted Compatibility](75-persisted-compatibility-findings.md) | profile、checkpoint、Bundle state、Journal schema 和 checkpointer | PC-C01..C07 |
| [76 - Evaluation Boundary](76-evaluation-boundary-findings.md) | evaluation 领域概念、persisted layer、export 和 test shim | EV-C01..C06 |
| [77 - OpenSpec And Records](77-openspec-and-record-findings.md) | CI/skill 交付、main specs、registry、CONTEXT、ADR 和历史边界 | OR-C01..C08 |
| [78 - Residual Compatibility Sweep](78-residual-compatibility-sweep-findings.md) | 前八域之外的 compatibility、alias 和 fallback 定义级反查 | RC-C01..C07 |

这些文件保存证据、现状、目标 owner、删除或迁移 gate，以及明确应保留的 guard。不要把其中的
Finding 编号直接当任务编号；真正进入执行的是每份尾部的 Candidate。

[返回总导航](../README.md) | [进入执行层](../03-execution/)
