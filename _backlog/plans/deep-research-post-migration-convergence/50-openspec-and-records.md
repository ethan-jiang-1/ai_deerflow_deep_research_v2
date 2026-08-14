# 50 - OpenSpec And Records

> 角色: 规格、治理 metadata、词典、ADR、当前文档与历史材料的同步边界
> 结果落点: `71`、`74`、`77` 与 owner-local Candidate slices；不创建横向 spec-cleanup mega-change

## OpenSpec 的位置

`openspec/` 是开发和 required-behavior authority，不是清理对象本身。清理必须通过它回答：

- 哪个 capability 当前拥有该行为？
- 旧 capability 是 rename、merge、retire，还是仍需要 compatibility requirement？
- requirement ID 如何保持 never-reuse 和 alive/pending/retired 三态？
- 哪些 structural/test governance entries 随代码删除同步收缩？

不能只删代码再把 main spec 留作“以后参考”，也不能只改 spec 让旧代码自然失去意义。

## Main spec 处理

### Capability rename

当 capability 名已不表达 current owner（例如 session 名下实际只剩 Run Observation）时：

1. 明确 target capability 和语义边界；
2. 枚举其他 specs、code、tests、docs 对旧 capability path/name 的 current 引用；
3. 用 delta 定义 rename/retirement，不手工搬目录冒充语义不变；
4. requirement IDs 不复用；保留现有 ID 还是 retire + 新 ID 由语义是否连续决定；
5. archive/sync 后运行 requirement/spec/coverage checks；
6. old capability directory/entry 关闭，必要 negative invariant 归 target owner。

### Capability retirement

只有当所有 requirements 已被 target owner 承接或明确不再 required，且 current consumer/data 已关闭，
才能 retire。退役不能留下一个只说“旧东西不得工作”的永久 capability；若 anti-resurrection invariant
长期必要，应由现行边界 capability 拥有。

### Requirement cleanup

- retired ID 在 registry 永久占位，不删除、不复用；
- requirement title 是稳定语义锚点，不为代码 rename 无意义 churn；
- scenario 只保留 current behavior、migration/rejection 或真实 negative path；
- 过期 implementation detail 从 requirement 中移除，但 observable compatibility promise 必须保留到
  cutover 完成；
- A-009 不自动升级为全局 assertion-semantic catalog；高风险切换可建立有界 requirement-risk-to-test seam。

## Governance metadata

每个 structural deletion 同步审查：

- `project-structure.toml` required path、node package、import policy、gitlink lock；
- generated `AGENTS.md` locator（只通过 checker render/update route）；
- `req-registry.yaml` 和 main spec `> req:`；
- requirement evidence annotations；
- charter policy route、Focus Card conditional reviews；
- test asset registries和 verification Make targets。

checker 自身只有在被保护规则改变时才修改。不能通过缩小扫描范围或删掉 negative fixture 让 cleanup 通过。

## CONTEXT.md

目标角色是 current domain glossary：

- term 定义一到两句，说明是什么；
- `_Avoid_` 列真正会混淆 current readers 的 alias；
- 不复制 requirement、运行机制清单、迁移步骤或 current-status ledger；
- 不把 planned/dormant concept 写成 current capability；确有领域价值时可保留带状态的定义；
- 具体事实由 owning spec/code 反向核验。

上次 alignment audit 的 C-006 明确撤回了“为变短而整体搬走尾部六段”的提议。本计划不自动
推翻该决定。只有在新 canonical-language change 中逐段证明内容重复、owner 已存在、current reader
已重路由，才处理对应段落；否则保持。

## ADR

ADR 是历史决策记录，不因目标变化而删除或重写成今天的观点：

- hard-to-reverse、surprising、real trade-off 才新建 ADR；
- superseded/dormant/deferred status 清楚即可；
- current docs/CONTEXT 不应把 superseded ADR 当作现行 authority；
- 若缺少 index 导致 current reader 无法判断 status，可建立最小导航，但不复制 ADR 事实；
- ADR filename/title 中的历史术语可保留，正文由 superseding decision 指向 current owner。

## Current docs 与历史证据

| Record | 处理规则 |
| --- | --- |
| README / docs index / operations docs | 只描述 current supported route，历史证据放清楚的 reference link |
| Generated topology | 从 current graph regenerate，不手改 |
| dated baseline/release report | 保留为有日期的 evidence；不作为 current freshness proof |
| OpenSpec archive | 默认不可变历史；只修 current inbound route 或损坏链接，不统一术语 |
| `_backlog/_done` | 默认历史；不因 residual scan 改写 |
| active plan/todo/bug | 必须使用 current path/term，或明确讨论旧表面 |

## OpenSpec change admission

每个实施批次必须：

- 使用 CLI scaffold change；
- Focus Card 选择一个 primary causal owner；
- 选择所有实际触发 policies；本计划预计至少常触发 `local-context`、`change-admission`，涉及
  persisted/control boundary 时再选择 `authority-and-projections`、`control-placement`、
  `workflow-outcome-review` 等；
- proposal 明确退休对象和净 concept change；
- design 分开 verified current behavior、approved target、unknown cutover facts；
- tasks 包含 red-before-green、consumer/data inventory、old-entry closure、registry sync 和 archive evidence。

## 记录层完成条件

- current main specs 只定义目标行为或有期限 migration/rejection behavior；
- 没有 capability 只作为无 owner 的历史名容器；
- requirement IDs、structure registry、test evidence 和代码同步；
- glossary 只承载 current language，ADR status 与 current docs 路由清楚；
- archive/_done residual 不被误报为 current drift；
- OpenSpec strict validation和五个项目 checker通过，且 checker scope 未被悄悄缩小。
