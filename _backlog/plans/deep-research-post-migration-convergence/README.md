# Plan: Deep Research 迁移后收敛与退役

> 类型: 架构健康审计 / 迁移收口 / 删除计划
> 状态: 活跃计划，尚未创建实施 change
> 创建: 2026-08-13
> 产品范围: `deep_research_harness/`
> 变更治理: `openspec/`
> 基线快照: `a733d329902e779a108401f1305c937174f6e492`

## 目的

本计划把长期迭代和多次迁移后的仓库收敛到一个明确终态：

1. `deep_research_harness/` 是唯一 Deep Research 产品核心；
2. 一个领域概念只有一套当前说法，代码、规格、测试和参与者投影使用同一语言；
3. 旧入口、兼容分支、迁移字段、过期实现和只证明旧机制的测试完成迁移后被删除；
4. 必须保留的历史证据与负向防回退检查被明确隔离，不再冒充当前拓扑；
5. `openspec/` 继续拥有 required behavior 和 change lifecycle，不成为第二套运行时架构。

这不是一次以字符串匹配或代码行数为目标的 cleanup。删除对象必须先证明它不再拥有当前
行为、没有未迁移消费者，并且其必要行为证据已经由目标实现承接。

## 目标终态

```text
Current user/operator entry
          |
          v
deep_research_harness public/runtime boundary
          |
          v
one canonical typed/domain contract per material fact
          |
          v
one current implementation path + lowest responsible evidence

openspec main spec/delta -------------- required behavior
CONTEXT.md ---------------------------- current domain glossary only
ADR ----------------------------------- durable historical decision and status
archive/_done ------------------------- historical evidence, never current authority
```

完成后不要求仓库中绝对不存在 `legacy`、旧词或历史路径。要求的是：所有当前命中都有明确
分类；旧词只能存在于不可变历史、明确兼容输入或能检测旧路径复活的负向证据中，不能继续
出现在当前生产身份、默认值、入口、模型策略或无期限兼容分支里。

## 权威与边界

| 事项 | 当前权威 | 本计划的角色 |
| --- | --- | --- |
| Required behavior | owning main spec；pending behavior 由唯一 active delta 拥有 | 识别需修改/退役的 capability，不直接改写行为 |
| Current runtime fact | typed contracts、代码、Bundle-local authority、测试 | 建立候选和消费者证据，不替代事实 owner |
| 产品术语 | `deep_research_harness/CONTEXT.md`，并受 owning spec/code 反向核验 | 规划 canonical term 决策与同步顺序 |
| 精确结构 | `openspec/governance/project-structure.toml` | 要求每次删除同步 registry 与 guard |
| 历史 | `openspec/changes/archive/`、`_backlog/_done/`、superseded ADR | 只作迁移风险证据，不批量改写 |
| 上游框架 | `deerflow/` gitlink 和公开接口 | 不读源码、不修改、不把上游清理纳入范围 |

## 计划导航

| 文档 | 回答的问题 |
| --- | --- |
| [00 - Baseline And Audit Contract](00-baseline-and-audit-contract.md) | 用什么范围、分类和证据判定残留？ |
| [10 - Ubiquitous Language](10-ubiquitous-language.md) | 如何做到一个概念一套当前说法？ |
| [20 - Retirement And Cutover](20-retirement-and-cutover.md) | 公开、持久化、跨边界表面怎样迁移后删除？ |
| [30 - Code And Entry Surfaces](30-code-and-entry-surfaces.md) | 生产代码、配置、脚本和入口按什么顺序收敛？ |
| [40 - Tests And Evidence](40-tests-and-evidence.md) | 怎样删除过期测试而不丢失行为与防回退证据？ |
| [50 - OpenSpec And Records](50-openspec-and-records.md) | main specs、registry、CONTEXT、ADR 和历史材料如何同步？ |
| [Candidate Register](candidate-register.md) | 当前已发现候选、证据、风险级别和待证明条件是什么？ |
| [99 - Progressive Execution](99-progressive-execution.md) | 如何一次一个 OpenSpec change 步步推进并最终关闭计划？ |

## 工作原则

1. **先定目标语义，再删实现。** 不能从旧名字推导旧行为，也不能从测试绿色推导该行为仍应保留。
2. **一次收敛一个 authority cluster。** owning spec、typed contract、实现、测试与治理记录同批闭环。
3. **公开/持久化/跨边界先迁移消费者。** 私有实现可直接重塑；持久化枚举、配置和外部可见结果不能静默破坏。
4. **测试随行为走。** 保留行为证据和负向 guard；删除只锁定旧实现形状或旧文案的断言。
5. **历史不定义目标拓扑。** archive 和 `_done` 默认不改；只有它仍被 current 入口引用为权威时才修路由。
6. **删除产生净收缩。** 不用新的兼容层、manager、registry 或永久 alias 替换旧层，除非它明确退休更多复杂度。
7. **一个 active change。** 每个批次通过 OpenSpec proposal/design/specs/tasks 实施、验证、归档后再启动下一批。

## 总体依赖

```text
P0 reproducible inventory and candidate classification
 |
 +--> P1 canonical language decisions
 |       |
 |       +--> P2 public/persisted cutover decisions
 |               |
 |               +--> P3 production and entry-path retirement
 |                       |
 |                       +--> P4 test/evidence subtraction
 |                               |
 |                               +--> P5 spec/governance residual closure
 |                                       |
 +---------------------------------------+--> P6 final re-audit
```

测试、spec 和治理同步不是最后才做的“大扫尾”。P4/P5 表示最终跨批复核；每个实施 change
仍必须同时修改自己的测试和 owning delta。

## 完成定义

本计划只有在以下条件全部满足后才能移入 `_backlog/_done/_closed_plans/`：

- 每个登记候选都有 `retired / migrated / renamed / guard-retained / historical / rejected`
  的最终 disposition 和证据；没有无限期 `unknown`；
- 当前生产、配置、模型策略、CLI/API/agent-facing 投影中不存在未批准的旧术语或旧入口；
- 每个 public/persisted/cross-boundary 退役项都已关闭消费者、数据与失败恢复路径；
- 目标行为的最低责任测试仍在，旧实现耦合测试和孤立 registry/fixture 已删除；
- main specs、requirement registry、structure registry、CONTEXT、ADR status 和当前 docs 一致；
- 残留扫描有小而明确的 allowlist，且 allowlist 只允许历史、兼容输入或负向 guard；
- `UV_OFFLINE=1 make verify`、严格 OpenSpec、Gitlink 边界和 whitespace 检查通过；
- 最终报告记录净删除、保留项及理由、未运行的 live/release evidence 和下次 drift review trigger。

## 不在范围

- 不读取或修改 `deerflow/` 源码；
- 不为追求零匹配而重写 `openspec/changes/archive/` 或 `_backlog/_done/`；
- 不顺手重构与退役候选无关的业务逻辑；
- 不把测试 LOC、文件数或概念数单独作为删除目标；
- 不在本 plan 中决定尚未完成消费者/数据调查的 breaking change；
- 不自动启动 A-009 全局语义 traceability；只有具体高风险退役 change 需要时才使用有界映射。

## 落地方式

本目录是分析和执行路线，不是 active change。每个被准入的批次先用 OpenSpec 建立自己的
Focus Card、owning capability delta、迁移/删除条件和测试任务。实施状态只记录在该 change 的
`tasks.md`；本计划只更新候选 disposition 与阶段关卡，不建立第二个逐文件任务账本。
