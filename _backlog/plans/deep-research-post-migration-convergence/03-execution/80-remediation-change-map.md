# 80 - Remediation Change Map

> 导航: [执行层索引](README.md) | [默认执行入口](99-progressive-execution.md) | [Candidate Register](candidate-register.md)
> 角色: 把 `70-78` 的 54 个最终 Candidate 映射成有界 OpenSpec changes、decision gates 与 non-regression obligations
> 状态: 编排完成；implementation 未开始；change names 是建议的稳定 slug，创建前仍须以当时 HEAD 复核
> 硬约束: 全局预算 8 个 change（00-07）；一次一个 active change；上一 change archive 后才创建下一项

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

## Why change 00 exists

现行 OpenSpec Focus Gate 要求每个 proposal 恰有一个 `## Change Focus`，且只有一个 smallest primary causal
owner。直接把多个 owner 塞进一个 change 会绕过已有治理，因此 00 必须先按现行单 owner 规则完成一次治理
bootstrap；它不实施任何审计 Candidate，也不能和 01 合并，否则会让新规则在批准自己之前被使用。

00 archive 后，普通 change 仍默认使用单一 `## Change Focus`。只有本表明确标记为 `program` 的 change
才可使用新形态：

- `program` 只是OpenSpec planning/verification/archive的包装单位，不是runtime owner、fact authority、writer
  或新的产品层；program decision authority只批准scope、顺序和archive，不替代workstream semantic owner；
- 一个 `## Program Focus` 冻结 program outcome、完整 Candidate budget、workstream 顺序、shared archive
  invariant、program failure/recovery、split/expansion rule 与 not-in-scope；
- 每个 `### Workstream Focus: <stable-id>` 重复现有 Focus Card 的 owner、seam、question、adjacent contracts、
  evidence、Candidate/obligation IDs、not-in-scope 与 triggered policies；review records和tasks都可追溯到
  该 workstream；
- declared Candidate budget必须与workstream Candidate/obligation IDs的集合完全相等且无重复；不得以 program
  名义创建共享runtime authority、共享helper或跨 workstream writer；
- 每个 workstream独立关闭admission、cutover、negative path、recovery与evidence，但只有全部 workstream完成后
  才能一次archive整个 change；未关闭工作不能静默defer到未来 change；
- checker机械拒绝budget/union不等、重复ID、空/重复owner、缺失字段和未登记workstream，并用known-invalid
  fixtures证明敏感度；actual diff/contract是否越界由apply/archive review对照tasks、paths和evidence审计，
  不伪称静态checker能判断语义。

program部分完成后若某workstream失败，recovery owner必须选择在冻结scope内forward repair，或回滚该
workstream及受其依赖的后续workstream到change前invariant；已完成且无依赖的workstream不得被无理由回滚。
若两条路线都不能关闭，program保持active并回到计划层批准re-scope、整体rollback或“一进一出”重排；不得
partial archive。

## Change budget

原审计编排有26个OpenSpec change，第一轮按共同owner压到15个；本轮把OpenSpec固定成本与语义owner解耦，
在保留owner-scoped workstream后固定为8个，较26个减少18个（约69%），较15个再减少7个（约47%）。
内部workstream/stage都是同一个change的`tasks.md`分段，不另占change：

| Order | Mode | Change | Primary Candidates | Attached obligations | Admission / terminal invariant |
| --- | --- | --- | --- | --- | --- |
| 00 | ordinary | `admit-bounded-program-change-workstreams` | none; governance bootstrap | current Focus Card、policy routing与checker guards | OpenSpec Governance Owner；在不放宽普通change的前提下，新增可机械校验的bounded program route；known-invalid proposal会失败 |
| 01 | program | `restore-delivery-and-subtract-dead-assets` | OR-C01, OR-C02, OR-C04; TA-C01, TA-C02, TA-C05; EC-C04; RC-C02 | OR-C06; TA-C03/C04/C06/C07; EC-C01/C03; RC-C07 | 00；先恢复clean-clone delivery，再按五个owner-local workstream删除已取证的repository/test/private residue；current lanes与guards不变 |
| 02 | ordinary | `converge-evaluation-boundary-compatibility` | EV-C02, EV-C03, EV-C04 | EV-C05, TA-C04 | 01；evaluation owner在consumer/data gates关闭后同批收敛metrics shim、import facade和persisted evidence layer |
| 03 | program | `converge-node-language-and-product-records` | NC-C01, NC-C02, NC-C03; EC-C02; OR-C03, OR-C05 | EV-C01, OR-C07, OR-C08 | 01；先关闭Node request contract并批准term table，再把glossary/design/status记录归还各owner；ADR history不改写 |
| 04 | ordinary | `converge-run-bundle-observation-authority` | RS-C01..C04, RC-C01, OR-C03 | RS-C05, EC-C01, PC-C05, TA-C04 | 01；Bundle lifecycle为primary owner，先迁negative evidence，再收敛capabilities、workbench projection与refinement API |
| 05 | program | `converge-run-input-and-composition-contracts` | FM-C01, FM-C02, FM-C04; EC-C06; PC-C01, PC-C02; RC-C03; EV-C06 | FM-C03, PC-C05, RC-C05, TA-C04 | 01；composition与profile/proposal两个workstream共享一个终态：admitted run input只产生显式、诚实、版本明确的composition truth |
| 06 | program | `converge-runtime-input-compatibility` | EC-C05, EC-C07, PC-C07, RC-C04 | EC-C03, RC-C05 | 01；trusted-context与deployment-config两个workstream分别关闭producer/support matrix，使host输入的shape、precedence和failure明确 |
| 07 | program | `converge-retained-run-data-compatibility` | PC-C03, PC-C04, PC-C06, RC-C06 | EV-C05, RS-C05 | 04；repair lifecycle与Run observation/result两个workstream完成dry-run、迁移/拒绝、rollback及old-reader closure；不伪造lifecycle或publication truth |

推荐 01 的delivery workstream恢复 repository-tracked workflows 与 project-owned OpenSpec skills。若 Governance
Owner选择versioned external delivery，必须在同一个workstream提供clean-install route并同步所有正向承诺；
delivery workstream关闭前不得进入01的四个subtraction workstream。

## Program workstream map

| Change | Workstream | Owner-scoped outcome | Candidate / obligation |
| --- | --- | --- | --- |
| 01 | `delivery` | repository automation/skill delivery在clean clone可复现 | OR-C01/C02、OR-C04 delivery half |
| 01 | `test-structure` | 删除空marker/scaffold及精确registry row | TA-C01/C02、OR-C04 scaffold half、TA-C03/C04 |
| 01 | `evidence-report` | 对照provenance后删除superseded DPT report与shape-only test | TA-C05、OR-C06、TA-C06/C07 |
| 01 | `demo-adapter` | 独有cases迁到canonical profile/preflight后删除private helpers | EC-C04、EC-C01/C03 |
| 01 | `topic-planner` | canonical Bundle profile tests承接short-state behavior后删除helper | RC-C02、RC-C07 |
| 03 | `node-contract-language` | required capability ref唯一，AI-facing/code/spec/test纵向使用term table | NC-C01/C02、OR-C03 |
| 03 | `glossary-records` | glossary只保留current definitions，design/status回到ADR/spec owner | NC-C03、EC-C02、OR-C05、EV-C01、OR-C07/C08 |
| 05 | `composition-mode` | recipe API与persisted mode只表达真实composition | FM-C01/C02/C04、EC-C06、FM-C03、RC-C05 |
| 05 | `profile-proposal` | profile/proposal readers、evaluation consumer与Python export共享批准schema matrix | PC-C01/C02、RC-C03、EV-C06、PC-C05 |
| 06 | `trusted-context` | `disable_clarification`按host producer inventory迁到明确marker contract | EC-C07、EC-C03 |
| 06 | `deployment-config` | checkpointer precedence与endpoint aliases分别获得bounded support决定 | EC-C05、PC-C07、RC-C04、RC-C05 |
| 07 | `repair-lifecycle-data` | checkpoint/Bundle records迁移后退役`repair_counts`与`REPAIR_EXHAUSTED` | PC-C03/C04、RS-C05 |
| 07 | `observation-result-data` | Journal和Run result old readers在retention关闭后退出 | PC-C06、RC-C06、EV-C05 |

02与04继续使用ordinary change：它们已有真实单一primary owner，改成program不会减少change数量或提高边界
清晰度。

## Why the floor is eight

8不是按Candidate平均切分，而是本次减少固定成本后的执行下限：

- 00是治理bootstrap，不能循环地让尚未批准的program规则批准自己；
- 01可合并五个低风险workstream，因为Candidate集合已穷举、共同终态是clean-clone baseline，且delivery先行
  gate阻止machine-local residue继续掩盖结果；
- 02有独立evaluation data/import support gate；并入01会让P0 delivery被外部Evaluation Bundle阻塞，并入03
  又没有共同term/record终态；
- 03的两个workstream由同一term table串联，先纵向改current language，再收窄glossary ownership；
- 04必须先固定Bundle/Journal authority；07随后才能迁移retained records。把两者锁进同一个change会让未知
  external data把authority cutover变成长时间active且难以回滚的事务；
- 05处理用户run input到composition truth，06处理host/runtime input support；producer、decision authority、
  failure与rollback不同，合并只会制造一个名义上的“input cleanup”umbrella；
- 07可以合并两类retained-data workstream，因为都在04之后、使用同一dry-run/count/restart/replay/rollback
  协议，但仍分别拥有schema和terminal invariants。

因此不建议压到7。若未来证据证明02没有external consumer/data且可在01前完全关闭，或证明04与07能在创建
前一次性关闭全部retention gate，可以回到本计划重新审议；不能在执行中临时吞并。

## Split and growth rule

不得因为workstream/stage任务多就自动新建change。新增第9个change必须先修改本计划并获得明确批准；默认
采用“一进一出”，即合并或取消另一个槽位后仍保持8个。若一个program workstream变成长期blocked，不允许
把已完成部分先archive、把尾巴悄悄裂成新change：要么在创建前关闭gate，要么整体不admit，要么回到计划层
批准重排。任何新功能、无关重构或尚未审计scope都不能借program change进入。

## Non-regression ledger

下列 Candidate的审计结论是保留 current distinction、guard或historical evidence，不创建 keep-only change：

- `FM-C03`; `EC-C01`, `EC-C03`; `TA-C03`, `TA-C04`, `TA-C06`, `TA-C07`;
- `PC-C05`; `EV-C01`, `EV-C05`; `OR-C07`, `OR-C08`; `RC-C05`, `RC-C07`。

`RS-C05` 也是 retained guard，但必须随04迁移 evidence owner，并在07迁移数据时重验。`EV-C06` 是05的
linked consumer；`OR-C03/C04/C06` 是 owner-local/structural/evidence umbrella，不另建重复 change。

## Candidate coverage

该 map覆盖总账全部 54 个 Candidate；00是治理前置，不占Candidate：

| Findings | Candidate coverage |
| --- | --- |
| `70` | NC-C01..C03 -> 03 |
| `71` | RS-C01..C05 -> 04 + attached guard；07重验guard |
| `72` | FM-C01..C04 -> 05 + non-regression |
| `73` | EC-C01..C07 -> 01, 03, 05-06 + non-regression |
| `74` | TA-C01..C07 -> 01 + attached/non-regression |
| `75` | PC-C01..C07 -> 05-07 + non-regression |
| `76` | EV-C01..C06 -> 02-03, 05 + non-regression |
| `77` | OR-C01..C08 -> 01, 03-05 + umbrella/non-regression |
| `78` | RC-C01..C07 -> 01, 04-07 + non-regression |

## Change closure transaction

每个 admitted change必须完成同一套事务：

1. 在当前 HEAD重验 Candidate consumer/data/export证据；若事实改变，先更新对应 findings与总账；
2. 00按现行Focus Card创建并只修改program-change admission governance、checker和tests；其known-invalid
   structural/budget fixtures通过、archive后才允许program proposal；
3. 用OpenSpec CLI创建表中一个change；ordinary proposal声明一个smallest primary causal owner；program
   proposal冻结一个bounded program outcome、完整Candidate集合和每个owner-scoped workstream，`tasks.md`不得
   带入未审计scope；
4. 每个workstream/stage分别写清owner、decision authority、cutover、negative path、recovery和old-entry closure；
5. 每个stage red-before-green，迁移 target behavior与negative evidence，再删 implementation/tests/registry/docs；
6. 运行 focused tests、相关 lanes、`UV_OFFLINE=1 make verify`、五个 governance checker与strict OpenSpec；
7. ordinary change或program全部workstream关闭后一次archive，记录未运行live/release/Postgres/real-Gateway
   evidence；apply/archive review逐workstream核对实际diff、tasks和evidence没有越界，并把所有涉及Candidate
   更新为最终disposition/evidence；
8. 确认无active change和意外worktree变化后才进入下一order。
