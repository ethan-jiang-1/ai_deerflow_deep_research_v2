# 99 - Progressive Execution

> 导航: [执行层索引](README.md) | [Candidate Register](candidate-register.md) | [根总导航](../README.md)
> 角色: 最终逐步执行总计划
> 输入: [70-78 findings](../02-audit-findings/) 的54个最终Candidate；change映射以 [80 - Remediation Change Map](80-remediation-change-map.md) 为准
> 状态: 00 已于 2026-08-14 archive 并同步 main spec（commit `8661693`）；01 已于同日 archive 并同步 main spec（commit `47a3bb5`）；02 已于同日 archive 并同步 main spec（commit `9b68e4d`，全量验证的范围外 node-agent 基线失败已如实记录为 evidence-limited）；03 已于同日 archive 并同步 main spec（commit `84d533a`）；04 已于同日 archive 并同步 main spec（commits `4ef1d69`、`8a18dbd`）；05 已于 2026-08-15 archive 并同步 main spec（commit `4d91571`）；06 已于同日 archive 并同步 main spec（commit `69a2dcd`）；07 已于同日 archive 并同步 main spec（commit `a8293b6`）。全局预算8个change（00-07）已关闭；checkbox只记录change closure，不替代active change的 `tasks.md`

## Propose 后强制 Polish

每个 admitted change 在 `propose` 生成全部 apply-required artifacts 后，必须立即进入
`$polish-openspec-change <change-name>`，再考虑 `apply`。这是 change lifecycle 的强制
阶段，不是可选 review，也不占用额外 change budget：

1. `openspec-propose` 自己完成后会按其边界停止；调度者必须把已生成的 active change 直接交给
   `polish-openspec-change`，不得从 `propose` 跳到 `apply`；
2. polish 至少完成一轮 whole-change coherence 和一轮最高风险的 risk-led pass，逐项把 proposal、
   design、delta specs、tasks 与实际 owner/accepted spec/test seam 对齐；
3. 由既有事实能确定的 stale reference、缺失 task、术语、验证或 scope 不一致，必须在同一次
   polish 中修正所有受影响的 change artifacts；涉及新产品决定、外部 consumer/data、权限或冲突
   authority 的问题必须报告 `not ready`，不得用假设进入 apply；
4. 只有 polish 最终报告 `ready for apply`，且 strict OpenSpec、`git diff --check` 与该 change 已声明的
   planning/governance checks 通过，才可开始 `tasks.md` 的实现。polish 不修改 target code、tests、
   accepted specs、governance files 或 task completion state；
5. apply/archive review 仍对实际 diff、workstream scope 与 evidence 负责。polish 证明 planning
   artifacts 已准备好，不批准 runtime behavior、external closure 或 archive。

## 不可跳过的执行协议

每一步都按同一个transaction完成，不批量预创建changes：

1. 在当前HEAD重验该步Candidate、consumer/data/export scope与前置gate；事实变化先修findings/register/map；
2. 00必须先按现行单owner Focus Card完成并archive；之后ordinary change继续使用一个smallest primary causal
   owner，program change使用一个bounded program outcome和多个owner-scoped workstream；
3. 只有change内全部decision/data/export gate关闭后才创建并完成 `propose` artifacts。program proposal一次冻结完整Candidate budget，
   每个workstream明确owner、target、retirement、surface grade、decision authority、negative path、recovery、
   evidence与not-in-scope；
4. 每个 newly proposed change 按上节完成 `$polish-openspec-change` 并获得 `ready for apply`；任何 `not ready`
   结论先在 planning 层关闭，禁止以“之后再 polish”或新增 implementation task 的方式绕过；
5. `tasks.md` 按workstream/stage承担逐文件工作；每个stage先做red/known violation，再迁移owner/behavior/evidence，
   最后删除old surface；一个workstream不得修改另一个workstream未声明的contract；
6. focused tests、相关lanes、full deterministic verify、governance与strict OpenSpec通过；
7. ordinary change或program全部workstream完成后一次archive，记录未运行的live/external evidence，更新所有
   linked Candidate最终disposition；program workstream不能单独archive或把尾项静默defer；
8. apply/archive review逐workstream把实际diff、tasks与evidence对回冻结scope；checker只证明结构和Candidate
   budget闭合，不代替语义scope review；
9. 确认无active change和意外worktree变化，再进入下一步。

若某项change仍缺任一产品决定、外部consumer或retained data，禁止先创建再等待。记录decision owner和缺失
证据后，只能继续准备依赖独立的后续项；改变执行顺序或分组必须先同步`80`，不能在active change内临时处理。

**数量控制:** 本计划只允许 `00-07` 八个槽位。workstream/stage不得升级成独立change；确需第9个时，必须先
修改`80`并获得明确批准，默认通过合并或取消另一个槽位保持总数仍为8。change不得夹带新功能或未审计重构。

## Owner Decision Packets

下列 packet 是下一步准入的最小授权输入，不是 agent 可以替代的产品、support 或 retained-data 决定。每个
Owner 的回复必须选定 target 或 bounded retained-support，并给出受支持 consumer/data 的 inventory、notice/denial、
recovery/rollback 与 removal/review trigger；没有这些输入不得创建 change。

- **02 Evaluation Owner（已授权，2026-08-14）:** 只支持已文档化的
  `deerflow_deep_research.runtime.evaluation` facade，保持 domain 为 fact authority，`runtime.evaluation.contracts`
  是不受支持的 module-private re-export。source-controlled 与本机 `evals/runs/` support inventory 均为空；未声明的
  private/external Evaluation Bundle 或 Review Record 不因此被推断为空，而是在 cutover 后明确不受支持：任何 missing/
  unknown `evidence_layer` 必须在 Review/quality claim 前拒绝，不写入、不回填也不升级为 live quality。紧急 rollback
  只能恢复旧 reader；若未来要重新纳入旧 records，必须另建有 inventory、hash-preserving migration 与 retention 决定的 change。
- **05 Product + Python Support Owner（已授权，2026-08-14）:** 零凭据 proof统一迁到 fixture graph，退休 no-graph
  `bind_full_fake()`，不保留另一个 simulator。`ResearchGraphRecipe.create()` 与
  `parse_profile_response()` 对 third-party Python consumer clean-cutover，不保留 external support。已盘点的
  source-controlled current inputs是唯一 supported scope；未盘点的旧/外部 Bundle mode、profile、proposal 或 checkpoint
  input明确拒绝，不保留 reader。紧急 rollback只能恢复旧 reader，不能改写 payload；任何未来重新支持均须另建 change
  决定 inventory、notice、removal trigger与迁移/retention。
- **06 Runtime + Deployment Owner:** 必须分别决定 `disable_clarification` 的 trusted-producer support window、legacy
  `checkpointer` 相对 `database` 的 precedence，以及 AppConfig endpoint aliases。每项都要列出 supported producer/
  config version，定义 conflicting/stale input 的 notice 或 fail-closed denial，以及回滚期间 writer/reader 的一致选择。
- **07 Data Owners:** 必须按 checkpoint、Bundle terminal、Journal manifest/event 与 persisted Run diagnostic result
  分别给出 supported-data inventory。每个 family 要有 dry-run count、old/new reader-writer matrix、restart/replay
  proof、rollback action 与 post-cutover count；未知数据只能保留 reader或拒绝，不能被静默改写为 current provenance。

## Phase A - 合法引入program change

- [x] **00 `admit-bounded-program-change-workstreams`**: governance bootstrap，不实施54个Candidate。

以OpenSpec change-admission governance为唯一primary owner，更新`openspec/config.yaml`、local-context policy、
应用Focus Gate、`check_agent_charter.py`及其contract tests。普通proposal仍须恰有一个`## Change Focus`；program
proposal必须有一个`## Program Focus`和逐项`### Workstream Focus: <stable-id>`，每个workstream保留现有Focus
Card全部字段、Candidate/obligation IDs与独立policy routing。checker至少对budget/union不等、重复ID、缺owner、
缺field和未登记workstream的known-invalid fixtures fail closed；actual diff scope由apply/archive review负责。
`program`只拥有planning/closure，不成为runtime authority或workstream之间的共享writer。

**Gate A:** 00已archive；ordinary route没有变宽；program route的positive/negative fixtures和strict validation
通过。归档证据：`openspec/changes/archive/2026-08-14-admit-bounded-program-change-workstreams/`，main spec
已同步，commit `8661693`。Gate A前不得创建任何多owner change，也不得直接用01的program形态修改repository。

## Phase B - 恢复交付并清除已取证死资产

- [x] **01 `restore-delivery-and-subtract-dead-assets`**: OR-C01/C02/C04、TA-C01/C02/C05、EC-C04、RC-C02。已 archive 并同步 main spec（`47a3bb5`）。

OR-C02 选择的推荐 repository-tracked route已关闭，且未引入 versioned external installer。归档 program 曾冻结五个workstream：

1. `delivery`: 恢复current CI workflows和可复现的 repository-tracked OpenSpec skill route，建立clean-clone trackedness guard；
2. `test-structure`: 在delivery关闭后删除8个marker、空`tests/e2e`与精确registry row；
3. `evidence-report`: 对照baseline/attestation/regression provenance后删除DPT report与shape-only test；
4. `demo-adapter`: 把独有cases迁到canonical profile/preflight后删除private helpers；
5. `topic-planner`: 由canonical Bundle-profile tests承接short-state behavior后删除legacy helper/export。

五个workstream都按上列顺序留下闭环证据，并在全部关闭后一次archive；没有 partial archive、scope drift或
外部 installer。冻结scope的 forward-repair/rollback 规则未被触发。

**Gate B:** clean clone获得可复现CI/OpenSpec workflow；无orphan marker/scaffold/selector/registry/export；
TA-C03/C04/C06/C07、EC-C01/C03、RC-C07 guards和deterministic/manual-live/suspended lane语义仍可证伪。

**01 closeout（2026-08-14）:** `openspec/changes/archive/2026-08-14-restore-delivery-and-subtract-dead-assets/`
保存 proposal、polish后计划、五个workstream evidence与 archive-closeout；主规格已同步，commit为`47a3bb5`。Git-index
guard、bounded dedicated-index `--no-local` clean-clone preflight、focused tests、five governance checks、strict
OpenSpec与`UV_OFFLINE=1 make verify`均通过。manual-live CI未运行，仍为`workflow_dispatch`；本 change未作
live/release claim，也没有把该未运行证据当作已关闭风险。

## Phase C - Evaluation boundary收敛

先完成evaluation package consumer与retained Evaluation Bundle inventory，再创建02；零caller shim不另付一项
change成本，而是同一owner的首个stage。

- [x] **02 `converge-evaluation-boundary-compatibility`**: EV-C02/C03/C04。已 archive 并同步 main spec（`9b68e4d`）。Stage 1删除`compute_metrics()`
  shim；Stage 2把imports收敛到唯一 supported facade；Stage 3删除missing-`evidence_layer`的default reader，使未盘点的 private/external records在 Review/quality claim 前明确拒绝，不迁移、回填或改写其内容。

**Gate C:** evaluation domain authority与supported import route唯一；missing layer不升级为live；EV-C05 fail-closed
archive admission和TA-C04 evidence joins保持不变。

**02 admission recheck（2026-08-14）:** `compute_metrics()` 仍是零 caller、零行为的 test helper residue，
`runtime/evaluation/contracts.py` 仍是 domain contract的纯 re-export；但`runtime.evaluation` facade有仓内
integration/evaluation consumer，且没有 repository-authorized Python support boundary。更重要的是，application
tree内没有可盘点的 retained `evals/runs` records，不能推断 private/external Evaluation Bundle或Review archive为空。
Evaluation Owner必须先提供 supported Python import route决定与 retained-record inventory/retention cutover；在此之前
02保持`not ready`，不创建 change。

**02 authorization decision（2026-08-14）:** User 以 Evaluation Owner 身份授权上述 clean cutover。唯一 supported
Python route 是`runtime.evaluation` facade；`.contracts` 没有 third-party support promise。未声明的 missing/unknown-layer
Evaluation Bundle 或 Review Record 不在支持范围，reader 必须 fail closed，且不得产生 Review、live-quality 或其他
provenance upgrade；现有 explicit-layer records 不变。紧急 rollback 是恢复该 reader 后再重试，不能在失败读入时改写
payload。该决定关闭02的 decision/data gate，允许创建 proposal；它不关闭05-07的独立 gates。

**02 post-04 recheck（2026-08-14，`30edb6e`）:** 文档只示例
`deerflow_deep_research.runtime.evaluation` facade，根包仍只导出 host-facing tool；runtime 内部 modules经
`.contracts` 使用 domain contract，不能据此把其 module-private route宣布为外部 support。建议 Evaluation Owner
选择现有 facade 为唯一 supported import route，但该建议不是授权决定。`evals/runs/` 继续被忽略且本机目录不存在；
focused Evaluation Bundle/live-boundary suite通过（105 passed）。这关闭了仓内枚举，不关闭未盘点的 private/external
Bundle、Review Record 或 retention/cutover。

**02 closeout（2026-08-14）:** `openspec/changes/archive/2026-08-14-converge-evaluation-boundary-compatibility/`
保存 proposal、polish后 artifacts、12项完成任务与 verification evidence；主规格已同步，提交为`9b68e4d`。显式
evidence-layer admission、Review 前 no-write、facade identity、retired module absence、结构 inventory与 typed metrics
retirement均有 focused deterministic proof；requirements/specs/architecture/charter/coverage、strict OpenSpec、Ruff和
whitespace均通过，gitlink保持不变且干净。`tests/eval` 中两条 node-agent fault-injection 断言在干净基线
`c304f453` 复现，`UV_OFFLINE=1 make verify`也仅在 `test-fast` 的其中一条失败；User 已明确授权在此
evidence-limited 状态归档。未运行 credentialed/live、release、Postgres、external-consumer 与 retained-data lanes，
本 change不对它们作通过、compatibility 或 retention 结论。

## Phase D - Node language与产品记录归位

- [x] **03 `converge-node-language-and-product-records`**: NC-C01/C02/C03、EC-C02、OR-C03/C05。已 archive 并同步 main spec（`84d533a`）。

`node-contract-language` workstream先关闭legacy capability cohort/default，令missing/invalid required ref fail closed，
再用一张bounded term table纵向同步AI-facing policy、code、spec、test与registry。其后`glossary-records`
workstream逐段迁移独有规则，删除CONTEXT中的design/status residue和dormant local-first language；保留EV-C01
distinctions、`_Avoid_`、generated projection freshness guard与ADR history。

**Gate D:** required capability ref唯一；current identity不再使用`Phase Agent`；CONTEXT只承载current terms与
必要`_Avoid_`，没有丢失Evaluation Workspace/Bundle/Review/Run等真实不同概念；ADR历史事实未被改写。

**03 admission recheck（2026-08-14）:** 所有当前 graph request builders均已传入`required` capability ref。根包
`__all__`只公开`__version__`和host-facing `deep_research_tool`；`NodeExecutionRequest`、phase-agent factory及其
module paths没有 public facade、文档或 entry-point support promise。它们因此是application-internal contract，03
不得改变根 tool export；仓内 consumer inventory与现有 fail-closed tests构成其 cutover evidence。若未来出现外部
consumer，必须在另一个 change 明确支持边界或compatibility，不得倒推为本 change 的隐含义务。

**03 closeout（2026-08-14）:** `openspec/changes/archive/2026-08-14-converge-node-language-and-product-records/`
保存完成的 program artifacts、七行 glossary owner ledger 与 closeout tasks；主规格已同步，提交为`84d533a`。
Candidate Register 已记录九项最终 disposition：`NC-C01`、`NC-C02`、`NC-C03`、`EC-C02`、`OR-C03`、`OR-C05`已
archive；`EV-C01`、`OR-C07`、`OR-C08`重验后保留为可证伪 guard/history。focused suites、`UV_OFFLINE=1 make verify`、
五个 governance checks、strict OpenSpec、`openspec doctor --json`与git whitespace check均通过。未运行`test-live`、
真实 Demo/TUI、credentialed/external evaluation、`requires_llm`、`release_e2e`与Postgres lanes；它们不构成已关闭的
live/external evidence，也未引入新的 compatibility obligation。

## Phase E - Run/Bundle/Observation authority

04 创建前已完成refinement method的supported consumer matrix；若当时Python export support仍未知，则不得创建04。

- [x] **04 `converge-run-bundle-observation-authority`**: RS-C01..C04、RC-C01、OR-C03。已 archive 并同步 main spec（`4ef1d69`、`8a18dbd`）。

**Gate E:** Bundle/Journal/operator boundaries各有唯一owner；Local Session Workbench仍可用但不宣传broker；
binding/session store不能复活或在Bundle loss后recovery；PC-C05 refinement recovery语义与RS-C05 guards不变。

**04 admission recheck（2026-08-14）:** `BundleLifecycle.refine()` 的 direct current callers恰为
`runtime/session_workbench.py`、`tests/integration/test_research_lifecycle_tool.py`和
`tests/integration/test_hitl1_lifecycle.py`；前者是待迁移的Local Session Workbench projection，后二者是
application-internal test consumers。host-facing `deep_research_tool`只在内部构造 lifecycle，`BundleControl`
已直接调用`admit_refinement()`；root `__all__`没有暴露 lifecycle/workbench，README/docs也没有 direct Python
import route。因此`runtime.bundle_lifecycle`及state-only wrapper是application-internal contract，04不承诺新的
public facade或compatibility window。workbench必须改为消费`RefinementAdmission`并保持自己的
`BundleControlResult`投影；若发现外部 consumer，须在另一个 change明确支持边界或迁移。上述 focused lifecycle、
workbench、admission、recovery与workflow suites在当时 HEAD通过（60 passed），构成04 proposal的admission evidence。

**04 closeout（2026-08-14）:** `openspec/changes/archive/2026-08-14-converge-run-bundle-observation-authority/`
保存完成的 change artifacts 与 17 项完成任务；`BundleLifecycle.refine()` 已删除，Local Session Workbench只消费
`admit_refinement().state`并保留既有 `BundleControlResult` projection。`research-run-session` 与
`research-session-lifecycle-binding` main specs 已退役，`RUS-*`/`RES-*` ID 保留为 `[DEPRECATED]`；RDO/RSV capability
已收敛为 Run Bundle 名称，Journal、Bundle-loss、诊断、结构与 namespace 的证明都迁至当前 owner。严格 OpenSpec、
requirement/spec/architecture governance、focused runtime/no-resurrection suites、`UV_OFFLINE=1 make verify` 与 git
whitespace check通过；`deerflow` gitlink保持 `66b9e7f…` 且 submodule工作树干净。未运行live/release/Postgres/real-Gateway、
external Python consumer与retained-data inventory lanes；本 change没有作这些外部闭合或上游兼容性声明。

## Phase F - Run input与composition truth

创建05前一次性批准zero-credential UX，关闭recipe/profile parser Python export、supported Bundle mode、profile、
proposal与checkpoint producer inventories。

- [x] **05 `converge-run-input-and-composition-contracts`**: FM-C01/C02/C04、EC-C06、PC-C01/C02、
  RC-C03、EV-C06。已 archive 并同步主规格（`2026-08-15-converge-run-input-and-composition-contracts`，`4d91571`）。

`composition-mode` workstream依次迁移`ResearchGraphRecipe.create()` consumers、替换/退役no-graph full-fake
path、迁移/拒绝explicit `full_fake` records，并在missing-mode states关闭后删除default reader。`profile-proposal`
workstream用一张schema matrix收敛profile/proposal readers、evaluation consumer和Python export。两个workstream
共享的program终态是：每个admitted run input只产生显式、诚实、版本明确的composition truth。

**Gate F:** no-graph execution不再写成`all_real`/research-completed truth；supported State显式携带诚实mode；
profile/proposal旧输入要么已迁移/拒绝，要么有批准的bounded support；FM-C03、PC-C05与RC-C05保持current。

**05 post-04 recheck（2026-08-14，`30edb6e`）:** no-graph `bind_full_fake()` route和其`all_real`
State writer仍存在；`ResearchGraphRecipe.create()`与`parse_profile_response()`仍是 Python export surfaces，而 profile/
proposal/checkpoint producers不可由仓内样本穷举。Product Owner的 zero-credential UX 选择、Python support boundary、
以及 supported Bundle mode/profile/proposal/checkpoint producer inventories仍未提供。相关组合 baseline command通过
（149 passed）；不得因此把05 proposal的 product/data gates视为关闭。

**05 current-HEAD recheck（2026-08-14，`e92a941`）:** 当前无 active change。`scripts/demo.py`、
`scripts/demo_tui.py` 与 README仍把零凭据 full-fake presentation 路由到无 graph executor 的
`bind_full_fake()`；不能由既有实现反推零凭据产品体验的目标选择。`ResearchGraphRecipe.create()`仍是只转发
`all_real()` 的导出兼容构造器，`parse_profile_response()`仍在 domain export 中，仓内 tests仍消费两者；
`BundleLocalState.from_dict()`仍将缺失 `implementation_mode` 默认成 `all_real`。仓内 source/test 的枚举不能
证明 third-party Python consumer 或 profile/proposal/checkpoint retained producer 为空。因此 Gate F 仍为
`not ready`，不得 `propose`：

1. Product Owner须明确批准 recommended fixture-graph proof并退休 `bind_full_fake()`，或批准一个另命名、显式
   persisted/result semantics 的 honest no-graph simulator；
2. Python Support Owner须为 `ResearchGraphRecipe.create()` 与 `parse_profile_response()` 分别决定 clean cutover
   或 bounded third-party support，并给出通知/拒绝、rollback与 removal trigger；
3. Product + Data Owners须提供 supported Bundle mode、profile、proposal 与 checkpoint producer/data inventory；
   每个旧 input须选择迁移、明确拒绝或有期限 reader，并给出恢复/rollback与完成计数，不能以本机零命中替代。

**05 authorization decision（2026-08-14）:** User以 Product + Python Support Owner身份确认上述 recommended
fixture-graph target、两个 Python surface的clean cutover，以及未盘点旧/外部 input的explicit rejection；rollback
只恢复旧 reader。该决定关闭05的proposal admission decision/data/export gates，授权创建
`converge-run-input-and-composition-contracts`；它不宣称 Gate F已实现，apply必须证明无 graph execution不再写成
`all_real`/research-completed truth、supported State显式携带mode，且旧 input按已批准的拒绝路径fail closed。

**05 proposal + polish（2026-08-14）:** active program change
`converge-run-input-and-composition-contracts` 已生成 proposal、七个 delta specs、design 与19项未完成 tasks；
polish 的 whole-change pass补齐七-delta scope与真实 focused-test seams，risk-led pass把 legacy/full-fake
accepted-spec cleanup精确绑定到 sync task，并把两个 clean-cutover Python surface的consumer/denial/rollback
evidence并入 input matrix。最终 strict OpenSpec、Agent Charter、project specs、project requirements、doctor和
`git diff --check`通过；05为 `ready for apply`。这只是 planning readiness，不代表 Gate F已实现，也不授权
implementation/archive。

**05 closeout（2026-08-15）:** `openspec/changes/archive/2026-08-15-converge-run-input-and-composition-contracts/`
保存完成的 change artifacts、三个 closeout corrections与验证证据；apply implementation为`66e1e73`，archive
commit为`4d91571`。FM-C01以固定 fixture graph 退休 no-graph full-fake route；FM-C02/C04关闭`FULL_FAKE`与
missing-mode default并拒绝未盘点 retained/external state；EC-C06删除`ResearchGraphRecipe.create()`；PC-C01/C02、
RC-C03关闭旧 profile/proposal/checkpoint reader与 parser wrapper；EV-C06仅迁移 evaluation test consumer；FM-C03、
PC-C05与RC-C05重验后保留为可证伪 guard。`UV_OFFLINE=1 make verify`的最终 lane evidence为 fast `2594/0`、
integration `243/0/4 skipped`、workflow `35/0`；requirements/specs/architecture/charter/coverage、strict OpenSpec、
doctor与git whitespace均通过，`deerflow` gitlink仍为`66b9e7f…`且干净。未运行`test-live`、credentialed real
Demo/TUI/Gateway、`requires_llm`、`release_e2e`、Postgres、external Python-consumer和retained-data inventory lanes；
它们没有被当作 live/external compatibility closure，也没有留下05的兼容性义务。

## Phase G - Runtime host input compatibility

创建06前一次关闭host trusted-context producer、supported deployment config/provider和AppConfig version inventories。

- [x] **06 `converge-runtime-input-compatibility`**: EC-C05/C07、PC-C07、RC-C04。已 archive 并同步 main spec（`69a2dcd`）。

`trusted-context` workstream决定`disable_clarification`到`non_interactive`的support window、notice、stale denial与
rollback。`deployment-config` workstream分别决定checkpointer precedence与endpoint field aliases；共享inventory，
不共享语义决定。owner决定继续支持时，在原workstream落实bounded support、guard和review/removal trigger。

**Gate G:** 已关闭。唯一支持的 trusted marker 是带闭合 policy 的 `non_interactive=true`；任何
`disable_clarification=true` 在 Bundle、sandbox、graph 或 policy write 前返回 `interactive_required`。
`database` 是唯一 provider-classification input，任何非空 legacy `checkpointer` 在 factory/open 前以
`legacy_checkpointer_unsupported` 被拒绝，且 GraphHost/diagnostics 保持同一不泄漏投影。endpoint observation
仅来自 exact selected `base_url`；`openai_api_base` 或 `api_base`（单独或同时出现）都只导致无 observation，
不能影响 model/provider/retry/route/lifecycle。旧 root、mount/config drift guards 仍为可证伪 guard；应急恢复只允许
经批准的完整本地 reader hotfix/revert，不能重新引入局部 compatibility switch。

**06 post-04 recheck（2026-08-14，`30edb6e`）:** `disable_clarification` alias与 legacy `checkpointer`
precedence仍是当前受测行为，endpoint alias reader仍接收 external AppConfig shape。仓内 tests只能证明当前 canonical
writer、conflict与fail-closed behavior，不能枚举 trusted-context producer、supported deployment provider或 AppConfig
versions。Runtime/Deployment Owner仍须分别决定 marker support window、checkpointer precedence和 endpoint alias
support，再提供 notice、denial与 rollback route；focused baseline tests已通过（149 passed），不构成这些决定。

**06 post-05 recheck（2026-08-15）:** 05已 archive，但当时尚未改变`disable_clarification`、legacy
`checkpointer` precedence或 AppConfig endpoint alias的support contract，也没有提供 trusted-context producer、deployment
provider或 supported AppConfig version inventory。因此当时 Gate G为`not ready`：Runtime/Deployment Owner必须为
EC-C05/C07、PC-C07与RC-C04分别授权迁移/明确拒绝/有期限 support，并给出notice、denial、rollback、review/removal
trigger与完成计数；不得把05对外部 profile/proposal/Bundle inputs的reject decision外推到deployment configuration。

**06 authorization + closeout（2026-08-15）:** Runtime/Deployment clean-cutover decision已授权：不登记任何
host producer、deployment provider 或 AppConfig version 的 support window；source-controlled canonical writer/local
reader 是唯一 support inventory，其他 external/private producer/config 不被推断为空而是无 support promise。active
program change `converge-runtime-input-compatibility` 通过强制 polish 后实现并 archive 于
`openspec/changes/archive/2026-08-15-converge-runtime-input-compatibility/`。其 clean-cutover matrix 与
archive-closeout 记录 EC-C05、EC-C07、PC-C07、RC-C04 及 EC-C03/RC-C05 guard 的各自 disposition；三份 main
spec 已同步。trusted-context、provider/diagnostics、node bridge focused suites（35、95、110 passed）、
`UV_OFFLINE=1 make verify`、requirements/specs/architecture/charter governance、strict OpenSpec 和 whitespace
检查均通过。credentialed/external-runtime lanes 未运行，因为它们不能建立未登记的 support promise；gitlink
`66b9e7f…` 和 `deerflow` worktree 保持不变且干净。提交为 `69a2dcd`。

## Phase H - Retained run data compatibility

07只在04 archive后创建，并分别关闭checkpoint、Bundle、Journal与public/persisted Run result inventories；本机
样本只提供风险下界。每个workstream都要有dry-run、old/new reader-writer matrix、restart/replay、rollback、
negative evidence和post-cutover count。

- [x] **07 `converge-retained-run-data-compatibility`**: PC-C03/C04/C06、RC-C06。已 archive 并同步 main spec（`a8293b6`）。

`repair-lifecycle-data` workstream迁移graph checkpoints后删除`repair_counts`，再迁移/拒绝old Bundle terminal并
退役`REPAIR_EXHAUSTED`。`observation-result-data` workstream收敛Journal manifest/event readers，再迁移/过期old
diagnostic-location results；不得把absence伪造成Journal publication或把failure映射成success。

**Gate H:** supported persisted records处于批准schema、明确rejection或有时限retained support；无silent
authenticity upgrade、failure-to-success mapping或无期限reader；summary v2、RS-C05和EV-C05 guards保持不变。

**07 post-04 recheck（2026-08-14，`30edb6e`）:** 04 archive 已满足唯一 ordering prerequisite。ignored local
Bundle 样本仅作风险下界：358 份`state.json`中298份显式 mode、60份缺 mode、0份为`full_fake`；201份 Journal
manifest中56份为v2、145份为v3，另有201份 current `run-summary.json`。这些计数不读取 payload，也不能证明
external checkpoint/Bundle/Journal/public Run result支持范围为空。Checkpoint、Bundle terminal、Journal和 diagnostic
result inventories，以及 dry-run、old/new reader-writer、restart/replay、rollback matrices仍是 proposal 前置条件；
focused state/Journal baseline tests通过（149 passed）。

**07 closeout（2026-08-15）:** `converge-retained-run-data-compatibility` 已在强制 polish 后完成两个
workstream，并归档至`openspec/changes/archive/2026-08-15-converge-retained-run-data-compatibility/`；五份
main specs 已同步，提交为`a8293b6`。source-controlled inventory 明确为零 supported records；四个 family
都有 migration/reject disposition、old/new reader-writer matrix、write/reload/replay 与 planted-negative proof。
current checkpoint、Bundle、Journal 与 terminal readers 不保留 old runtime branch，Summary v2 保持 current；唯一
恢复仍是 Data Owner 批准的完整 local reader hotfix/revert。focused retained-data suites、Demo CLI/TUI/adapter suite、
strict OpenSpec、requirements/specs/architecture/charter governance 和 whitespace 检查均通过。`make verify` 的
selector registry 及 cognitive digest failures 为已记录且与本 change无关的 evidence-limited baseline；未对
credentialed/live、external deployment/data 或 Python consumer 作通过或 support claim。

## Phase I - 最终全量复审与关闭

- [x] 逐条检查Candidate Register全部54项，写最终disposition、change/archive evidence或approved retain decision。
- [x] 重跑01中的tracked/current-term/legacy/compat/entry/config/serializer/export/spec/requirement/test-registry扫描。
- [x] residual current matches逐条落入current behavior、approved old-input、negative guard或historical；建立小且有owner的allowlist。
- [x] 第二次核对entry/public/persisted/AI-facing surfaces，不允许双writer、双entry、双authority或无期限compat reader。
- [x] 检查每个retained guard的known/planted violation与scope escape；quiet不等于dead。
- [x] 检查main specs、retired IDs、requirement/structure/evidence registries、CONTEXT、ADR status与current docs routes。
- [x] 记录净删除files/LOC/tests/requirements与净新增concept；数字只描述结果，不作为成功理由。
- [x] 记录未运行live/release/Postgres/real-Gateway、外部deployment/data/Python consumer evidence及接受风险。
- [x] 更新[根 README](../README.md)的revision/status与审计结论，形成closeout，然后按backlog lifecycle归档整个plan目录。

**Phase I closeout（2026-08-15）:** [04 - Final Closeout](../04-final-closeout.md) records the 54-row
closure, residual allowlist, authority/surface/recovery/guard review, accounting, verification, and explicit
evidence limits. It confirms zero active changes and no unresolved Candidate; the known selector/digest baselines
and unrun live/external lanes are limitations, not fabricated passing evidence.

**Final Gate:** satisfied with the evidence limits recorded in the closeout. Candidate Register has no current
`ready`, `blocked`, or unknown row; every retained compatibility has an authority, owner, trigger, and fail-closed
behavior. The `00` program route still mechanically rejects missing owners, open Candidate budgets, and unregistered
workstreams, and the eight apply/archive reviews record no unexplained scope drift.

## 每个change的最低验证

从repository root运行：

```bash
python3 openspec/governance/check_project_reqs.py .
python3 openspec/governance/check_project_specs.py .
python3 openspec/governance/check_project_architecture.py .
python3 openspec/governance/check_agent_charter.py .
python3 openspec/governance/check_project_req_coverage.py .

cd deep_research_harness
UV_OFFLINE=1 make verify
cd ..

openspec validate <change-name> --strict
openspec doctor --json
git diff HEAD --check
git status --porcelain=v1 --untracked-files=all
git ls-files --stage deerflow
git submodule status -- deerflow
git -C deerflow status --porcelain=v1 --untracked-files=all
git diff --submodule=short
```

每个change另加最窄focused tests、cutover/dry-run/negative-control evidence。上述命令不证明live behavior、
external consumer/data closure、semantic product decision或upstream compatibility；未运行项必须显式记录。
