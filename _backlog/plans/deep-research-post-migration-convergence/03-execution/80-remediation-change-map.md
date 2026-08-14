# 80 - Remediation Change Map

> 导航: [执行层索引](README.md) | [默认执行入口](99-progressive-execution.md) | [Candidate Register](candidate-register.md)
> 角色: 把 `70-78` 的 54 个最终 Candidate 映射成有界 OpenSpec changes、decision gates 与 non-regression obligations
> 状态: 编排完成；implementation 未开始；change names 是建议的稳定 slug，创建前仍须以当时 HEAD 复核
> 硬约束: 全局预算 15 个 change（00-14）；一次一个 active change；上一 change archive 后才创建下一项

## Admission semantics

| 状态 | 含义 |
| --- | --- |
| `ready` | repository evidence足以起草 change；仍须在 proposal前重验 HEAD |
| `ordered` | 自身证据足够，但必须等前置 owner/cutover change archive |
| `decision` | 必须先由 named owner批准 target/support boundary；不能用 cleanup假设代替 |
| `data/export` | 必须先关闭 retained data、external producer或 Python import support scope |
| `non-regression` | 不创建 keep-only change；作为所有相关 change 的 guard |

`decision` 或 `data/export` 不等于无限期保留。调查结束后必须形成 approved migration、bounded retained
support，或 `rejected` disposition，并写 removal/review trigger。

## Change budget

原编排有26个OpenSpec change；按共同primary owner与共同终态合并后固定为15个，减少11个（约42%）。
内部stage是同一个change的`tasks.md`分段，不另占change：

| Order | Change | Primary Candidates | Attached obligations | Admission / terminal invariant |
| --- | --- | --- | --- | --- |
| 00 | `restore-repository-automation-delivery` | OR-C01, OR-C02, OR-C04 delivery half | current CI/OpenSpec delivery guards | P0；clean clone获得可复现CI和OpenSpec workflow，ignored local copy不能冒充delivery |
| 01 | `subtract-empty-test-scaffolding` | TA-C01, TA-C02, OR-C04 scaffold half | TA-C03 | 00；project-structure/test scaffold owner删除marker、空目录和registry row，collection与suspension不变 |
| 02 | `retire-superseded-dpt-report` | TA-C05, OR-C06 | TA-C06, TA-C07 | 00；evidence provenance owner先完成对照，再删除DPT report与shape-only test |
| 03 | `subtract-demo-compatibility-helpers` | EC-C04 | EC-C01, EC-C03 | 00；demo adapter把独有cases迁到canonical profile/preflight后删除private helpers |
| 04 | `subtract-topic-planner-legacy-helper` | RC-C02 | RC-C07 | 00；topic-planner owner由canonical Bundle profile tests承接short-state behavior |
| 05 | `converge-evaluation-boundary-compatibility` | EV-C02, EV-C03, EV-C04 | EV-C05, TA-C04 | 00；evaluation owner在consumer/data gates关闭后同批收敛metrics shim、import facade和persisted evidence layer |
| 06 | `converge-node-cognition-contract-and-language` | NC-C01, NC-C02, OR-C03 | TA-C04, OR-C07 | 00；Node Cognition owner先关闭legacy request contract，再按同一term table纵向rename AI-facing/code/spec/test |
| 07 | `restore-product-glossary-ownership` | NC-C03, EC-C02, OR-C05 | EV-C01, OR-C08 | 06；glossary owner只保留current terms，独有规则先迁owner，ADR历史不改写 |
| 08 | `converge-run-bundle-observation-authority` | RS-C01..C04, RC-C01, OR-C03 | RS-C05, EC-C01, PC-C05, TA-C04 | 00；Bundle lifecycle为primary owner，先迁negative evidence，再收敛capabilities、workbench projection与refinement API |
| 09 | `converge-implementation-mode-and-recipe-surface` | FM-C01, FM-C02, FM-C04, EC-C06 | FM-C03, EC-C04 | 03；composition/provenance owner在UX、export和Bundle data gates关闭后收敛path、constructor、enum与missing-mode reader |
| 10 | `converge-profile-proposal-compatibility` | PC-C01, PC-C02, RC-C03, EV-C06 | PC-C05 | profile/proposal owner先关闭schema、checkpoint、producer与Python-export matrix，再同批迁移readers/consumers |
| 11 | `resolve-non-interactive-marker-compatibility` | EC-C07 | current trusted-context guards | host producer inventory、notice、stale-marker denial和rollback决定已批准 |
| 12 | `converge-runtime-configuration-compatibility` | EC-C05, PC-C07, RC-C04 | EC-C03, RC-C05 | deployment/runtime-config owner一次盘点supported configs/providers/AppConfig versions，分stage收敛checkpointer与endpoint aliases |
| 13 | `retire-repair-lifecycle-compatibility` | PC-C03, PC-C04 | current gate/terminal guards | repair lifecycle owner在checkpoint与Bundle inventories、exact failure mapping和rollback关闭后同批退役field/enum |
| 14 | `converge-run-observation-result-compatibility` | PC-C06, RC-C06 | EV-C05, RS-C05 | 08；Run Observation/Experience owner在Journal retention和public Run result inventory关闭后分stage收敛old readers |

推荐 `00` 恢复 repository-tracked workflows 与 project-owned OpenSpec skills。若 Governance Owner选择
versioned external delivery，必须在同一个 change 内提供 clean-install route并同步所有正向承诺；`00`
archive前不创建产品 cleanup change。

## Grouping floor and split rule

15不是按Candidate平均切分，而是现有Focus Card“一项change一个最小语义owner”约束下的合并下限：

- `05` 合并evaluation shim、import facade和persisted evidence layer，因为三者都由evaluation boundary拥有；
- `06` 合并Node request contract closure与纵向language rename，但把跨领域glossary owner保留为独立`07`；
- `08` 合并RES/RUS/capability/workbench/refinement，因为Bundle lifecycle是共同primary owner，Journal等只作
  named adjacent contracts；
- `09` 合并recipe constructor、execution path和persisted mode，因为它们共同决定composition/provenance truth；
- `12` 合并checkpointer与model endpoint config，因为它们共享deployment/runtime-config owner和support inventory；
- `13` 合并repair checkpoint field与terminal reason；`14` 合并Journal schema与Run diagnostic result，因为各自
  拥有一个可陈述的lifecycle/observation终态。

`01-04` 看似都是低风险减法，但分别属于project structure、evidence provenance、demo adapter与topic planner；
把它们装进“misc cleanup”会伪造primary owner。`10`、`11`也分别属于profile/proposal与trusted-context input，
不能为了数字再并入runtime config。

不得因为内部stage任务多就自动新建change。新增第16个change必须先修改本计划并获得明确批准；默认采用
“一进一出”，即合并或取消另一个槽位后仍保持15个。任何新功能、无关重构或尚未审计的scope都不能借批量
change进入。

## Non-regression ledger

下列 Candidate的审计结论是保留 current distinction、guard或historical evidence，不创建 keep-only change：

- `FM-C03`; `EC-C01`, `EC-C03`; `TA-C03`, `TA-C04`, `TA-C06`, `TA-C07`;
- `PC-C05`; `EV-C01`, `EV-C05`; `OR-C07`, `OR-C08`; `RC-C05`, `RC-C07`。

`RS-C05` 也是 retained guard，但必须随 `08` 迁移 evidence owner。`EV-C06` 是 `10` 的 linked
consumer；`OR-C03/C04/C06` 是 owner-local/structural/evidence umbrella，不另建重复 change。

## Candidate coverage

该 map覆盖总账全部 54 个 Candidate：

| Findings | Candidate coverage |
| --- | --- |
| `70` | NC-C01..C03 -> 06-07 |
| `71` | RS-C01..C05 -> 08 + attached guard |
| `72` | FM-C01..C04 -> 09 + non-regression |
| `73` | EC-C01..C07 -> 03, 07, 09, 11-12 + non-regression |
| `74` | TA-C01..C07 -> 01-02 + attached/non-regression |
| `75` | PC-C01..C07 -> 10, 12-14 + non-regression |
| `76` | EV-C01..C06 -> 05, 07, 10 + non-regression |
| `77` | OR-C01..C08 -> 00-02, 06-09 + umbrella/non-regression |
| `78` | RC-C01..C07 -> 04, 08, 10, 12, 14 + non-regression |

## Change closure transaction

每个 admitted change必须完成同一套事务：

1. 在当前 HEAD重验 Candidate consumer/data/export证据；若事实改变，先更新对应 findings与总账；
2. 用 OpenSpec CLI创建表中一个change；Focus Card只声明一个smallest primary causal owner；proposal/design冻结
   该change的program outcome、Candidate集合、named adjacent contracts和内部stage，`tasks.md`不得带入未审计scope；
3. 每个内部stage分别写清owner、decision authority、cutover、negative path、recovery和old-entry closure；
4. 每个stage red-before-green，迁移 target behavior与negative evidence，再删 implementation/tests/registry/docs；
5. 运行 focused tests、相关 lanes、`UV_OFFLINE=1 make verify`、五个 governance checker与strict OpenSpec；
6. archive change，记录未运行 live/release/Postgres/real-Gateway evidence；
7. 全部stage关闭后一次archive，把所有涉及Candidate更新为最终disposition/evidence，确认worktree后才进入下一order。
