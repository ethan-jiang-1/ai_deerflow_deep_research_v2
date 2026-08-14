# 80 - Remediation Change Map

> 角色: 把 `70-78` 的 54 个最终 Candidate 映射成有界 OpenSpec changes、decision gates 与 non-regression obligations
> 状态: 编排完成；implementation 未开始；change names 是建议的稳定 slug，创建前仍须以当时 HEAD 复核
> 硬约束: 一次一个 active change；上一 change archive 并更新 Candidate disposition 后才创建下一项

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

## P0 - Restore reproducible repository delivery

| Order | Change | Candidates | Admission | Terminal invariant |
| --- | --- | --- | --- | --- |
| 00 | `restore-repository-automation-delivery` | OR-C01, OR-C02, OR-C04 (delivery half) | OR-C01 ready；OR-C02 owner decision | clean clone获得 current CI workflows和可复现 OpenSpec workflow；ignored local copies不能冒充 delivery |

推荐 target 是恢复 repository-tracked workflows与 project-owned OpenSpec skills，因为 current README、AGENTS、
tests和先前 tracked history都声明该 owner。若 Repository Governance Owner选择 versioned external skills，必须在
同一 gate中提供 clean-install route并同步所有正向 docs；不能只删承诺。此 change archive前，后续 cleanup
change一律不创建。

## Ready ordered changes

这些 change不需要产品语义或 retained-data猜测；顺序用于先验证治理通路，再收敛 domain owner：

| Order | Change | Primary Candidates | Attached obligations | Prerequisite / closure |
| --- | --- | --- | --- | --- |
| 01 | `subtract-empty-test-scaffolding` | TA-C01, TA-C02, OR-C04 (scaffold half) | TA-C03 | 00；删除 marker/empty directory/registry row，collection与suspension不变 |
| 02 | `retire-superseded-dpt-report` | TA-C05, OR-C06 | TA-C06, TA-C07 | 00；先完成provenance对照，再删report与shape-only test |
| 03 | `subtract-demo-compatibility-helpers` | EC-C04 | EC-C01, EC-C03 | 00；behavior cases迁到canonical resolver/preflight |
| 04 | `subtract-topic-planner-legacy-helper` | RC-C02 | RC-C07 | 00；canonical Bundle profile tests覆盖short-state helper行为 |
| 05 | `subtract-evaluation-test-compatibility` | EV-C04 | EV-C05, TA-C04 | 00；零caller shim/export消失，typed metrics证据不减 |
| 06 | `close-node-capability-migration` | NC-C01, OR-C03 | TA-C04 | 00；required capability ref成为唯一request contract，missing ref fail closed |
| 07 | `converge-node-cognition-language` | NC-C02, OR-C03 | OR-C07 | 06；一张bounded term table驱动AI-facing/code/spec/test纵向rename |
| 08 | `restore-product-glossary-ownership` | NC-C03, EC-C02, OR-C05 | EV-C01, OR-C08 | 07 term table；glossary只留current terms，ADR历史不改写 |
| 09 | `retire-session-lifecycle-binding` | RS-C01, OR-C03 | RS-C05, TA-C04 | 00；有效negative invariants迁到DRH/REJ/PRS owner后退役RES capability |
| 10 | `consolidate-run-observation-ownership` | RS-C02, RS-C03, RS-C04, OR-C03 | RS-C05, EC-C01, TA-C04 | 09；Bundle/Journal owner唯一，workbench保留且registry不再宣传broker |

Order 01-05都是低风险减法，但仍各自保持一个 primary causal owner；不合并成“misc cleanup”。Order 06-10
改变 current spec/AI-facing/capability ownership，必须单独 archive，不能为了减少 change 数量横向打包。

## Export and support decisions

以下项只有在 decision evidence落盘后才能起草。若 owner决定继续支持，Candidate应标 `rejected` 或
`guard-retained` 并记录 support/review trigger，不创建伪删除 change。

| Suggested order | Change | Candidates | Required decision evidence | Dependency |
| --- | --- | --- | --- | --- |
| 11 | `retire-recipe-constructor-alias` | EC-C06 | supported Python constructor/import consumers | 07；可证明 public recipe仍固定 all-real |
| 12 | `converge-evaluation-contract-exports` | EV-C03 | package import support route与consumer inventory | 05 |
| 13 | `converge-refinement-admission-api` | RC-C01 | external Python method support；workbench disposition mapping | 10；PC-C05 non-regression |
| 14 | `converge-profile-compatibility-readers` | PC-C01, PC-C02, RC-C03 | profile/proposal schema matrix、retained profiles/checkpoints、participant producers、Python exports | checkpoint inventory；EV-C06 attached |
| 15 | `resolve-non-interactive-marker-compatibility` | EC-C07 | supported host producers、notice、stale-marker denial与rollback | 00 |
| 16 | `resolve-legacy-checkpointer-precedence` | EC-C05, PC-C07 | supported deployment configs、conflict behavior、provider parity与rollback | 00 |
| 17 | `resolve-model-endpoint-config-aliases` | RC-C04 | supported AppConfig/host versions与producer inventory | 00；可复用16的deployment inventory，不共用决策 |
| 18 | `resolve-full-fake-demo-contract` | FM-C01 | zero-credential UX target：fixture graph、诚实simulator或retire | 03；FM-C03 non-regression |

Order 14所需 checkpoint inventory可与 PC-C03 的 migration discovery复用，但 profile/proposal input与
`repair_counts` 是不同 contract，不得同 change修改。Order 16/17同理：共享 deployment inventory不代表
checkpointer precedence与model endpoint fields是同一个兼容承诺。

## Persisted migration changes

每一项先用 dry-run/inventory证明支持范围，再定义 write-new/read-old、one-time migration或explicit rejection。
本机 ignored数据只能证明风险存在，不能关闭外部数据。

| Suggested order | Change | Candidates | Admission gate | Terminal invariant |
| --- | --- | --- | --- | --- |
| 19 | `retire-full-fake-implementation-mode` | FM-C02 | 18 target decision + retained Bundle inventory | no current writer/reader/spec承诺旧enum；old input按批准策略收敛 |
| 20 | `close-bundle-state-mode-compatibility` | FM-C04 | supported missing-mode states migrated/expired | supported State显式携带诚实mode；missing不升级为all-real truth |
| 21 | `retire-frozen-repair-counts-state` | PC-C03 | all checkpoint providers/data + restart/replay/rollback | gate kernel唯一拥有repair attempts；old checkpoint明确迁移或拒绝 |
| 22 | `retire-repair-exhausted-terminal-reason` | PC-C04 | retained Bundle data + exact target outcome decision | old failure永不投影为success；closed enum只含current reasons |
| 23 | `converge-run-observation-schema-readers` | PC-C06 | 10 + Journal retention/migration | v3 manifest/event current；summary v2不被误删；old records不制造provenance |
| 24 | `close-evaluation-evidence-layer-compatibility` | EV-C02 | retained Evaluation Bundle/review inventory | every supported manifest显式layer；missing永不升级为live |
| 25 | `close-run-failure-diagnostic-location-compatibility` | RC-C06 | retained/public Run result inventory | exact diagnostic publication truth；old terminal迁移、过期或明确拒绝 |

Order 19与20都修改 implementation mode，但明确不把 explicit `full_fake` 与 missing provenance合并解释。
Order 21-25可以在各自 data gate关闭后调整相对顺序；不得越过自身 gate，也不得并行 active changes。

## Non-regression ledger

下列 Candidate的审计结论是保留 current distinction、guard或historical evidence，不创建 keep-only change：

- `FM-C03`; `EC-C01`, `EC-C03`; `TA-C03`, `TA-C04`, `TA-C06`, `TA-C07`;
- `PC-C05`; `EV-C01`, `EV-C05`; `OR-C07`, `OR-C08`; `RC-C05`, `RC-C07`。

`RS-C05` 也是 retained guard，但必须随 Order 09/10迁移 evidence owner。`EV-C06` 是 Order 14 的 linked
consumer，`OR-C03/C04/C06` 是 owner-local/structural/evidence umbrella，不另建重复 change。

## Candidate coverage

该 map覆盖总账全部 54 个 Candidate：

| Findings | Candidate coverage |
| --- | --- |
| `70` | NC-C01..C03 -> 06-08 |
| `71` | RS-C01..C05 -> 09-10 + attached guard |
| `72` | FM-C01..C04 -> 18-20 + non-regression |
| `73` | EC-C01..C07 -> 03, 08, 11, 15-16 + non-regression |
| `74` | TA-C01..C07 -> 01-02 + attached/non-regression |
| `75` | PC-C01..C07 -> 14, 16, 21-23 + non-regression |
| `76` | EV-C01..C06 -> 05, 08, 12, 14, 24 + non-regression |
| `77` | OR-C01..C08 -> 00-02, 06-10 + umbrella/non-regression |
| `78` | RC-C01..C07 -> 04, 13-14, 17, 25 + non-regression |

## Change closure transaction

每个 admitted change必须完成同一套事务：

1. 在当前 HEAD重验 Candidate consumer/data/export证据；若事实改变，先更新对应 findings与总账；
2. 用 OpenSpec CLI创建一个 change，proposal/design/delta/tasks只拥有一个 primary causal owner；
3. public/persisted/cross-boundary surface写清 decision authority、cutover、negative path、recovery和old-entry closure；
4. red-before-green，迁移 target behavior与negative evidence，再删 implementation/tests/registry/docs；
5. 运行 focused tests、相关 lanes、`UV_OFFLINE=1 make verify`、五个 governance checker与strict OpenSpec；
6. archive change，记录未运行 live/release/Postgres/real-Gateway evidence；
7. 把所有涉及 Candidate更新为最终 disposition/evidence，确认 worktree后才进入下一 order。
