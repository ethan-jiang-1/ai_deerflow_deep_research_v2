# Deep Research 迁移后收敛：总导航

> 类型: 架构健康审计 / 迁移收口 / 删除计划
> 审计状态: 当前基线审计完成；54 个最终 Candidate 已取证；implementation 未开始
> 产品范围: `deep_research_harness/`
> 变更治理: `openspec/`
> 当前 active OpenSpec changes: 0

## 先看哪一层

这套目录不是一条要求从 `00` 顺读到 `99` 的长计划。它把同一项工作拆成三种职责：

```text
01-audit-contracts/   怎么审：判定口径、删除门槛、证据规则
        ↓
02-audit-findings/    审出了什么：9 个领域的事实、风险与最终 Candidate
        ↓
03-execution/         接下来怎么做：Candidate 总账、change 映射、逐步执行顺序
```

| 你现在要回答的问题 | 直接入口 | 是否需要继续读别层 |
| --- | --- | --- |
| “审计最后发现了什么？” | [02 - Audit Findings](02-audit-findings/) | 从该层索引选择领域；不必先读 `00-50` |
| “下一步到底做什么？” | [99 - Progressive Execution](03-execution/99-progressive-execution.md) | 默认执行入口；遇到 Candidate 或 gate 再查同层另外两份文件 |
| “某个 Candidate 的证据和状态在哪里？” | [Candidate Register](03-execution/candidate-register.md) | 沿链接回到对应 finding 尾部 |
| “为什么这样判定删除、迁移或保留？” | [01 - Audit Contracts](01-audit-contracts/) | 只读与问题有关的合同，不必六份通读 |

编号表示文档角色，不表示一条连续执行流水线：`00-50` 是六类审计合同，`70-78` 是九份实际审计
结果，`80` 是 Candidate 到 change 的映射，`99` 才是最终逐步执行总计划。三个子目录各有自己的
`README.md`，进入后会继续说明阅读顺序。

## Revision contract

本目录跨过三种 revision，不能只写一个“当前 commit”混淆事实：

| Revision | 角色 | 结论 |
| --- | --- | --- |
| `a733d329902e779a108401f1305c937174f6e492` | 原始 plan snapshot | 保存最初审计问题和口径，不是最终发现 |
| `5bb41c16a45ff3caae6e5b1e900610c91bf68336` | 应用与 current main-spec 取证基线 | `70-78` 的代码/spec/test结论以此为准 |
| `c92ed9d028ab6ac1bb144adba62c02ba94cc2f2b` + 本目录审计 worktree | 审计综合 revision | 只更新计划/发现；未改应用、tests或main specs |

`5bb41c1 -> c92ed9d` 没有产品代码或 current spec变化，因此现有 findings仍对应当前应用事实。实施任何
Candidate前仍须在当时 HEAD做 focused revalidation；若产品事实已变，先更新对应 findings，不整库重做
没有受影响的审计。

## 审计目的与边界

终态目标是：`deep_research_harness/` 只有当前必要实现和证据；一个领域概念只有一套 current language；
旧入口、兼容分支、迁移字段、过期测试和记录在消费者/数据切换后退出；必要 historical evidence与
anti-resurrection guard明确保留。`openspec/` 拥有 required behavior与change lifecycle，不成为第二套runtime。

审计不读取或修改 `deerflow/` 源码，不以零 `legacy` 字符串或删除行数为成功标准，也不重写
`openspec/changes/archive/`、`_backlog/_done/` 与 ADR历史。public、persisted、cross-boundary表面没有
consumer/data/support closure时，只能形成 decision/migration Candidate，不能静默删除。

## 审计结论

本次从应用、tests、current specs、governance、entry/docs与本机 retained-data风险样本中形成 9 份 findings，
每份最后一个二级章节都是 `## 最终审计 Candidate`：

| Findings | 最终结论 | Candidate |
| --- | --- | --- |
| [70 - Node Cognition](02-audit-findings/70-node-cognition-findings.md) | 删除 legacy capability cohort/default；随后纵向统一 Node cognition language；glossary恢复纯词典职责 | NC-C01..C03 |
| [71 - Run, Bundle, Session, Observation](02-audit-findings/71-run-session-and-observation-findings.md) | 退役 lifecycle-binding与混合 Run Session capability；保留 Local Session Workbench与防复活guards | RS-C01..C05 |
| [72 - Fixture And Implementation Mode](02-audit-findings/72-fixture-mode-findings.md) | 保留 `src_fake`/explicit mixed；no-graph full-fake会写出不诚实 `all_real`，需产品决策；old/missing mode需数据迁移 | FM-C01..C04 |
| [73 - Entry And Configuration](02-audit-findings/73-entry-and-configuration-findings.md) | 保留职责不同的entry；删除private demo helpers；constructor/marker/checkpointer按export/support边界处理 | EC-C01..C07 |
| [74 - Tests And Evidence Assets](02-audit-findings/74-test-and-evidence-asset-findings.md) | 删除8个冗余 `.gitkeep`、空 `tests/e2e` 与superseded DPT报告；保留EVH-024、registries、dated evidence与regression policy | TA-C01..C07 |
| [75 - Persisted Compatibility](02-audit-findings/75-persisted-compatibility-findings.md) | profile、checkpoint、terminal reason、Journal reader、checkpointer均需按各自persisted/deployment边界迁移；refinement facts保留 | PC-C01..C07 |
| [76 - Evaluation Boundary](02-audit-findings/76-evaluation-boundary-findings.md) | Workspace/Bundle/Review/Node-or-Flow Run是不同概念；清理re-export与零行为shim前分别关闭import/data边界 | EV-C01..C06 |
| [77 - OpenSpec And Records](02-audit-findings/77-openspec-and-record-findings.md) | clean clone已失去tracked CI与project OpenSpec skills；这是所有cleanup前的P0 blocker；current history/projections大多保留 | OR-C01..C08 |
| [78 - Residual Compatibility Sweep](02-audit-findings/78-residual-compatibility-sweep-findings.md) | 补齐refinement/planner/profile-HITL/AppConfig/diagnostic-location；确认recipe fingerprint、mount alias probe与业务fallback不是残留 | RC-C01..C07 |

共 54 个 Candidate。完整证据、current/target owner、迁移/删除条件与保留 guard在各 findings尾部；
[Candidate Register](03-execution/candidate-register.md) 是唯一导航总账，不复制或取代这些事实。

## 最高优先级 blocker

commit `5bb41c1` 删除了 tracked CI workflows与项目 OpenSpec skills，随后忽略整个 `.github/`、`.agents/`。
本机 ignored copies掩盖了问题，但 clean clone中两类文件的 tracked count都是零，而 README、AGENTS、docs与
tests仍正向依赖它们。因此：

1. 首个实施 change必须关闭 OR-C01/OR-C02/OR-C04 的 repository-delivery问题；
2. 在 clean clone可复现 CI/OpenSpec workflow前，不开始产品 cleanup；
3. 推荐恢复 repository-tracked owner；若 Governance Owner批准 external/versioned install，必须同批修正
   所有正向承诺并证明 clean setup可复现。

## Retained-data evidence

本机 ignored workspace只用于发现迁移风险，不能证明外部支持已经关闭：

- 326份 Bundle `state.json` 全为schema v3：263 `all_real`、3 `fixture`、60缺
  `implementation_mode`；零 `full_fake`、零 `repair_exhausted`；
- 24份profile均为schema v2；28个 `graph.sqlite` 的opaque serialization不能靠raw string排除旧state；
- 169份Run Observation `journal-manifest.json`：56 v2、113 v3；1,042条events：616 v2、426 v3；
  169份summary均为current writer的v2；
- `.reports/**/observations/*/manifest.json` 的63个v1样本属于diagnostic report envelope，不是Journal manifest；
- local `evals/runs`为空，外部/private Evaluation Bundles、deployment configs、Python consumers与Run results未知。

因此 FM-C02/C04、PC-C01..C04/C06/C07、EV-C02/C03、EC-C06/C07、RC-C01/C03/C04/C06等仍有明确
data/export/support gate；“本机零命中”不授权breaking deletion。

## 原始审计合同到结果的覆盖

`00-50` 是审计方法与问题域，`70-78` 才是取证结果。覆盖关系如下：

| Audit contract | 已完成的结果落点 | 关闭状态 |
| --- | --- | --- |
| [00 - Baseline And Audit Contract](01-audit-contracts/00-baseline-and-audit-contract.md) | `70-78`、Candidate Register、tracked/data snapshot | 当前基线高信号范围已关闭；外部unknown显式进入blocked Candidate |
| [10 - Ubiquitous Language](01-audit-contracts/10-ubiquitous-language.md) | `70`, `71`, `72`, `73`, `76`, `77`, `78` | 同义词与不同概念已分开；具体rename/keep见NC/RS/FM/EC/EV/RC Candidate |
| [20 - Retirement And Cutover](01-audit-contracts/20-retirement-and-cutover.md) | `70-73`, `75`, `76`, `78` | 每个可疑public/persisted/cross-boundary surface都有target、gate或retain理由 |
| [30 - Code And Entry Surfaces](01-audit-contracts/30-code-and-entry-surfaces.md) | `70-73`, `76`, `78` | production/helper/export/entry分类完成；无引用不再被误当删除授权 |
| [40 - Tests And Evidence](01-audit-contracts/40-tests-and-evidence.md) | `74` + 所有findings的“保留负向护栏” | orphan/scaffold、historical、suspended、registry与anti-resurrection处理已落Candidate |
| [50 - OpenSpec And Records](01-audit-contracts/50-openspec-and-records.md) | `71`, `74`, `77` + owner-local Candidate slices | capability/ID/registry/glossary/ADR/history/projection同步边界已关闭 |

## 执行入口

执行层只有三个文件，各自职责不能混：

| 文档 | 角色 |
| --- | --- |
| [Candidate Register](03-execution/candidate-register.md) | 54个最终 Candidate的disposition/admission导航 |
| [80 - Remediation Change Map](03-execution/80-remediation-change-map.md) | Candidate到00-25 change、decision/data gate和依赖的唯一映射 |
| [99 - Progressive Execution](03-execution/99-progressive-execution.md) | 默认执行入口；从P0到final re-audit的逐步运行与验收顺序 |

本目录不是 active change，也不建立第二个逐文件任务账本。每个 admitted batch用OpenSpec CLI创建自己的
proposal/design/specs/tasks；一次只允许一个 active change，archive并更新Candidate disposition后再进入下一步。

## 计划完成定义

计划只有在以下条件全部满足后才能移入 `_backlog/_done/_closed_plans/`：

- 54个Candidate都有 `retired / migrated / renamed / guard-retained / historical / rejected` 最终disposition与证据；
- 所有decision/data/export blockers已获授权结论或由明确support contract接管，不存在无限期unknown；
- current production、entry、AI-facing、config、public/persisted surface没有未批准旧身份或双authority；
- tests只保护current behavior、approved compatibility/rejection与necessary negative invariants，无orphan selector/row；
- main specs、requirement/structure registries、CONTEXT、ADR status与current docs一致；
- residual allowlist只含historical、approved old input或falsifiable guard，每项有owner和review/removal trigger；
- repository delivery在clean clone可复现；full deterministic verify、strict OpenSpec、governance、Gitlink与
  whitespace checks通过；
- closeout记录净删除/保留理由，以及未运行live/release/Postgres/real-Gateway evidence与残余风险。
