# OpenSpec 产品边界与可移植性文档集

> 角色：导航与文档职责说明  
> 决策入口：[`../openspec-product-boundary-portability.md`](../openspec-product-boundary-portability.md)

## 使用边界

这组文件只定义未来 OpenSpec portability 改造的最终方案。它们不直接覆盖当前 main specs、active
delta、code、tests、`project-structure.toml` 或 runtime authority。实施必须通过后续独立 OpenSpec
changes 完成。

## 文档职责

| 文件 | 唯一职责 | 不承担 |
| --- | --- | --- |
| [主计划](../openspec-product-boundary-portability.md) | 最终目标、范围、不可变决定、V1 边界和总体完成状态 | 逐文件归属、采用步骤、迁移细节 |
| [`01-review-findings.md`](01-review-findings.md) | 当前事实、风险与设计推导的 review 依据 | 新决策、实施顺序、采用 contract |
| [`02-boundary-and-file-matrix.md`](02-boundary-and-file-matrix.md) | 内容 owner、依赖方向、目标拓扑和当前文件处置 | rollout 顺序、跨仓发布流程 |
| [`03-adoption-contract.md`](03-adoption-contract.md) | export boundary、profile 选择、采用流程、证据和成功定义 | 当前仓迁移顺序、结构 authority |
| [`04-migration-and-proof.md`](04-migration-and-proof.md) | change 切片、兼容、恢复、guards、验证和关闭门槛 | 重新解释产品或 portable 内容归属 |
| 本文件 | 导航、术语和一致性规则 | 架构或实施决定 |

## 按问题阅读

| 你要回答的问题 | 阅读 |
| --- | --- |
| 最终到底要建成什么？ | 主计划 |
| 为什么这些边界是必要的？ | `01` |
| 某段内容或某个文件应该归哪里？ | `02` |
| 另一个产品怎样复制、绑定并证明采用成功？ | `03` |
| 当前仓库按什么顺序改、失败时如何恢复？ | `04` |

完整设计 review 的最小顺序是：主计划 → `02` → `03` → `04` → `01`。`01` 放在最后，是因为它
提供核验依据，不应先用历史问题塑造执行方案。

## 术语

| 术语 | 本文档集中的含义 |
| --- | --- |
| Portable Kernel | 与产品、host 和仓库 layout 无关的最小 change admission / authority / evidence 规则与纯 validator |
| Reusable Profile | 项目显式启用、change 按 trigger 选择的附加 authoring/review contract |
| Local Composition | 当前仓库把 kernel/profile 接到本地 paths、budgets、policy set 和 verification route 的组合层 |
| Product Front Door | `openspec/product/README.md` 的产品导向与 owner 路由入口 |
| Native Authority | OpenSpec specs/changes，以及 code/contracts/tests 等已声明事实 owner |
| Adoption Spike | 在真实 sibling repository 中以真实 changes 验证采用成本与语义适配 |
| Portable Release | 同时通过机械 fixtures 和真实 sibling adoption 的固定 source revision |

## 一致性规则

1. 每个事实只在其职责文件中完整陈述；其他文件只给短摘要和链接。
2. 主计划改变目标决定时，必须在同一编辑中同步拥有相关细节的 `02`、`03` 或 `04`。
3. `01` 只能提供 evidence 和 rationale，不能推翻或新增目标决定。
4. 若两份 normative 文档对同一问题给出不同答案，视为文档缺陷；实施前先修正文档，不以“后写的
   覆盖先写的”继续执行。
5. 当前 repository authority 与本计划冲突时，当前 authority 继续有效，直到一个 accepted change
   完成迁移、验证并退休旧入口。

## Reviewer 输出建议

Review 应按 finding 严重度报告：

- 冲突的 owner 或重复 authority；
- portable source 中残留的产品、路径、framework 或 requirement binding；
- adoption contract 无法真实执行的地方；
- migration 缺少 consumer、recovery、negative proof 或 deletion closure 的地方；
- 能以更小边界达到相同终态的删减建议。

Review 不需要提出另一套完整蓝图；若发现问题，应指出应修改本文件集中的哪个唯一 owner。
