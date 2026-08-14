# 75 - Persisted Compatibility Findings

> 取证基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 本地 retained-data 快照: 2026-08-13 当前工作机；ignored/untracked，只用于发现风险
> 边界: 本地样本不能代表外部部署、其他工作区、私有 evaluation runs 或第三方 Python consumers

## Persisted surface inventory

| Surface | Current writer | Current reader | Compatibility evidence |
| --- | --- | --- | --- |
| Bundle `state.json` | schema v3 | strict `BundleLocalState.from_mapping` | mode 可缺省；refinement fields 可缺省 |
| graph checkpoint `graph.sqlite` | LangGraph + project serde | runtime graph host | project state fields可能留在 opaque checkpoint |
| `request/profile.json` | profile schema v2 | `ResearchProfile.model_validate` | model直接接受 v1/v2 |
| Run Observation manifest/events | manifest/event schema v3 | v1/v2/v3 reader | old records标 incomplete，不伪造 upgrade |
| `run-summary.json` | summary schema v2 | v1/v2 reader | v2 是 current writer，不是 legacy |
| deployment AppConfig | external deployment | provider resolver/doctor/GraphHost | legacy `checkpointer` 优先于 `database` |

本机发现 326 份 `state.json`，全部 schema v3：263 `all_real`、3 `fixture`、60 缺
`implementation_mode`，没有 `full_fake` 或 `repair_exhausted`。24 份 profile 全为 schema v2；另有 28 个
`graph.sqlite`。

Run Observation 必须按它自己的精确路径计数，不能与 evaluation/diagnostic 的通用 `manifest.json` 混合：
169 份 `diagnostics/journal-manifest.json` 中 56 份 schema v2、113 份 schema v3；对应
`diagnostics/events.jsonl` 共 1,042 条 event，其中 616 条 schema v2、426 条 schema v3；169 份
`diagnostics/run-summary.json` 全为 schema v2。另有 63 份 `.reports/**/observations/*/manifest.json`
属于 diagnostic report envelope，schema 为 v1，不是 Run Observation manifest。以上数量只描述当前
ignored workspace，不是 migration completion evidence。

## Finding PC-01: Profile compatibility 有两个 reader，但只有一个进入 runtime

`RequestBundleStore.read_profile()` 直接调用 `ResearchProfile.model_validate()`；模型明确接受 schema v1/v2，
缺 schema 也按 v1 解释。`read_legacy_profile()` 则是 exported helper，仅有 definition/export和 focused test
consumer，runtime reader不调用它。两者不是两个独立 data authorities，但形成了重复 compatibility API。

本地 24 份 retained profile 全为 v2，不能证明外部 v1 数据不存在。正确减法是先把 v1 support policy
绑定到 canonical runtime reader，再删除无人使用 helper；是否进一步停止 v1 reading 是独立 data/support
decision。不能先删 model 的 v1 branch，因为 absent schema 与 `legacy_unspecified` 都是 persisted semantics。

## Finding PC-02: `parse_profile_response()` 是 test-only compatibility wrapper

wrapper 只返回 `parse_profile_input(text).partial`，production HITL1 使用 richer `ProfileParseResult`。当前
consumers位于 domain tests和 live-evaluation tests；后者因此把一个 legacy convenience API 当 evaluation
fixture seam。把这些 tests迁到 `parse_profile_input()` 后，wrapper没有独有行为或 public record contract。

它是 exported Python symbol，实施前仍需关闭包级 external-consumer support boundary；仓库内没有理由永久
保留两种 parser 名称。

## Finding PC-03: `repair_counts` 是 frozen checkpoint schema，不是普通 dead field

`ResearchGraphState.repair_counts` 在 current spec 中明确称 frozen/superseded，repair authority已移到 gate
kernel；但字段仍在 typed state、writer-ownership表、rerun planner输出、fixtures与大量 tests中。生产
writer会在 rerun projection中写空字典，因此“没有 current writer”不成立。

本地 `state.json` 不含该字段，因为它属于 graph checkpoint而非 Bundle State。28 个 `graph.sqlite` 的
raw string absence 不能作为 checkpoint inventory：serialization可能压缩、msgpack或存储在 provider外部。
删除需要 schema-version/cutover strategy、retained checkpoint data inventory和 stale checkpoint behavior，
不能作为 private field直接删。

## Finding PC-04: `REPAIR_EXHAUSTED` 没有 current writer，但仍是 closed persisted enum

`TerminalReason.REPAIR_EXHAUSTED` 标注 retained for compatibility；production scan没有 writer，唯一 current
test显式构造并要求 round-trip。当前 replacement outcomes由 gate/kernel的 blocked/typed failure表达。本地
326 states没有该值，但外部 Bundle data未知。

这是典型 read-old/no-write candidate。先确定 retained Bundle support scope和 old input projection，再决定
迁移为哪个 target reason或保留有期限 reader；不能把未知 old reason静默映射成 `completed` 或 generic
failure。

## Finding PC-05: Bundle refinement compatibility fields 仍拥有恢复行为

`current_refinement` 与 `refinement_replay_receipts` 在 `state.json` reader中是 optional，支持旧 states；但
current lifecycle、CAS recovery、duplicate/replay detection和 graph projection仍持续读写它们。本地 326
states都含这两个 keys。这不是 residual alias：前者是当前 applied direction，后者是有界 replay receipt。

字段 optionality 是 compatibility surface，字段本身是 current behavior。任何删除或合并都属于 refinement
recovery redesign，超出 migration residue cleanup；本计划应保留并把“optional old input”与“current fact”
说清楚。

## Finding PC-06: Run Observation old schemas 是显式 incomplete reader，不应误删

current writer产生 manifest/event schema v3；reader接受旧 manifest/event并将它们标记为 legacy/incomplete，
不制造 event watermark或 validation provenance。`run-summary.json` 当前仍写 schema v2，所以本地 169 份
summary v2不是旧 writer residue。批量把所有非 v3 记录称为 legacy会误删 current summary contract。

路径级样本确认 retained Journal 并非只含 current schema：56 份 `journal-manifest.json` 为 v2，events 中
也有 616 条 v2。通用 diagnostic report `manifest.json` 的 63 个 v1 样本与此 reader无关，不能拿来扩大或
缩小 Journal migration scope。

旧 manifest/event reader只有在 retained records迁移或 retention policy关闭后才可退役。当前本地数据已经
证明 v1/v2 records存在，且 external observation data未知，因此 disposition 是 migrate-then-retire，而非
立即删除。

## Finding PC-07: Legacy checkpointer precedence 是 deployment compatibility decision

`resolve_effective_provider()`、doctor、probe与 GraphHost明确让 external AppConfig 的 `checkpointer` 覆盖
`database`；main specs/tests也把冲突 precedence定义成 required behavior。local profile tooling拒绝
`checkpointer` 只证明本地 profile边界已经收敛，不代表 deployment config support结束。

删除需要 Deployment Owner枚举 supported configs、决定 conflict denial/notice/rollback，并保证 doctor与
GraphHost在 migration前后选择同一 provider。否则 cleanup可能静默改变 durability或连接到错误 datastore。

## 最终审计 Candidate

### PC-C01 - Delete redundant profile compatibility APIs while preserving the canonical v1 reader policy

- **证据**: runtime reader直接 `ResearchProfile.model_validate`；`read_legacy_profile` 只有 export/test consumer；
  本地 profile 全 v2但外部 retained data未知。
- **当前 owner**: `ResearchProfile` schema和 `RequestBundleStore.read_profile()`；helper是重复 API。
- **目标 owner**: 一个 canonical runtime reader明确拥有 v1/v2 support；移除 `read_legacy_profile()`。
- **Disposition**: helper `delete`；v1 reader `product decision`。
- **迁移条件**: support owner声明 profile retention范围；tests直接覆盖 canonical reader的 v1 no-invention语义。
- **删除条件**: helper consumers/export归零；停止 v1 reading 还需迁移/过期所有 supported v1 data。
- **保留负向护栏**: unsupported schema fail closed；v1不得制造 comparison/language事实；hash/ref一致性不变。
- **OpenSpec change slice**: `converge-profile-compatibility-readers`。

### PC-C02 - Delete `parse_profile_response()` after test migration

- **证据**: wrapper只投影 `parse_profile_input().partial`；仅 tests消费；production使用 canonical parser。
- **当前 owner**: exported convenience wrapper和 legacy-shaped tests。
- **目标 owner**: `parse_profile_input()` + `ProfileParseResult`。
- **Disposition**: `delete`，先关闭 external Python export scope。
- **迁移条件**: domain/live-evaluation tests改用 canonical result，保留 deterministic recognition cases。
- **删除条件**: tracked/export/docs consumer为零；focused profile和 live-evaluation tests通过。
- **保留负向护栏**: empty/invalid JSON、unknown enum、recognized-fields与 comparison-pair行为继续验证。
- **OpenSpec change slice**: 纳入 `converge-profile-compatibility-readers`。

### PC-C03 - Migrate graph checkpoints before deleting `repair_counts`

- **证据**: schema、ownership、rerun writer、fixtures/tests与 main spec均仍含字段；checkpoint data scope未知。
- **当前 owner**: frozen graph-state compatibility projection；gate kernel拥有 actual repair policy。
- **目标 owner**: gate kernel唯一拥有 repair attempts；target graph-state schema不再携带 frozen field。
- **Disposition**: `migrate then delete`。
- **迁移条件**: inventory all supported checkpoint providers/data；定义新 schema或 explicit old-checkpoint rejection；
  dry-run、restart/replay和 rollback到旧 reader的策略。
- **删除条件**: old checkpoints已迁移/过期/明确拒绝；所有 writers、ownership rows、fixtures和 specs同批删除。
- **保留负向护栏**: gate remains sole repair authority；unsupported checkpoint fails before graph mutation；replay不重置
  或伪造 repair budget。
- **OpenSpec change slice**: `retire-frozen-repair-counts-state`，不得与无状态 cleanup混批。

### PC-C04 - Retire `REPAIR_EXHAUSTED` only after Bundle-data support closure

- **证据**: no production writer；one round-trip test；本地 states零命中；external Bundle data未知。
- **当前 owner**: persisted `TerminalReason` compatibility reader。
- **目标 owner**: current gate/lifecycle terminal outcomes，由 Product/Lifecycle Owner指定 exact mapping/rejection。
- **Disposition**: `migrate then delete`。
- **迁移条件**: retained data inventory、target reason decision、old-state read/projection行为和 rollback。
- **删除条件**: supported records无旧值或已迁移；enum/test/spec/residual fixtures同批关闭。
- **保留负向护栏**: 未知 terminal value fail closed；旧 failure不得投影成 success；state identity/revision不变。
- **OpenSpec change slice**: `retire-repair-exhausted-terminal-reason`。

### PC-C05 - Keep current refinement facts and their old-state optional reader

- **证据**: lifecycle/recovery/duplicate/replay production consumers；326 local states均写 keys；spec/tests正向拥有。
- **当前 owner**: Bundle lifecycle refinement admission/recovery。
- **目标 owner**: 不变。
- **Disposition**: `keep`；optional input compatibility暂时保留。
- **迁移条件**: 无。未来若改模型，必须作为 refinement recovery redesign单独取证。
- **删除条件**: 当前计划不适用；需 replacement接管 current direction、receipt去重、CAS restart/replay。
- **保留负向护栏**: digest/operation-key conflict、bounded receipts、round/generation matching与 stale replay denial。
- **OpenSpec change slice**: 无 keep-only change。

### PC-C06 - Preserve old Run Observation readers until retained records close

- **证据**: current v3 manifest/event writers；local 56 v2 + 113 v3 Journal manifests、616 v2 + 426 v3
  Journal events；explicit incomplete classification；current summary writer与 169 local summaries均是 v2。
- **当前 owner**: Run Observation storage/reader contract。
- **目标 owner**: v3 manifest/event target；summary v2继续 current，除非另有 schema change。
- **Disposition**: old manifest/event `migrate then retire`；summary v2 `keep`。
- **迁移条件**: enumerate retained local/external Journals；migrate或制定 retention expiry；验证 stale/partial records。
- **删除条件**: supported old records为零；reader branches/tests/specs关闭；current summary不被误改。
- **保留负向护栏**: old records始终 marked incomplete；不得制造 watermark/generation/validation provenance。
- **OpenSpec change slice**: `converge-run-observation-schema-readers`，在 RS capability收敛后。

### PC-C07 - Decide legacy checkpointer precedence before any deletion

- **证据**: external config reader、doctor/probe/GraphHost consumers、positive main requirements/tests；repo samples不含
  legacy section但不能代表部署。
- **当前 owner**: Deployment AppConfig compatibility contract。
- **目标 owner**: Deployment Owner批准的 database-only contract或有期限 legacy reader。
- **Disposition**: `product decision`。
- **迁移条件**: supported config inventory、conflict behavior、notice、backup/rollback与 provider parity tests。
- **删除条件**: legacy producers迁移；resolver/spec/tests/docs不再正向承诺；stale config明确拒绝。
- **保留负向护栏**: doctor/GraphHost同选 provider；不泄露 DSN；不静默降低 durability。
- **OpenSpec change slice**: `resolve-legacy-checkpointer-precedence`。
