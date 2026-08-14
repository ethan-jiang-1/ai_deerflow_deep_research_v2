# 99 - Progressive Execution

> 导航: [执行层索引](README.md) | [Candidate Register](candidate-register.md) | [根总导航](../README.md)
> 角色: 最终逐步执行总计划
> 输入: [70-78 findings](../02-audit-findings/) 的54个最终Candidate；change映射以 [80 - Remediation Change Map](80-remediation-change-map.md) 为准
> 状态: 00 已于 2026-08-14 archive 并同步 main spec（commit `8661693`）；01 已于同日 archive 并同步 main spec（commit `47a3bb5`）；03 已于同日 archive 并同步 main spec（commit `84d533a`）；当前无 active change。02仍等待 Evaluation Owner 的 supported Python import 决定及 retained `evals/runs` inventory/retention cutover；04仍等待 refinement method 的 supported-consumer matrix。全局预算8个change（00-07）；checkbox只记录change closure，不替代active change的 `tasks.md`

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

- [ ] **02 `converge-evaluation-boundary-compatibility`**: EV-C02/C03/C04。Stage 1删除`compute_metrics()`
  shim；Stage 2把imports迁到唯一supported facade；Stage 3迁移/过期missing-`evidence_layer` records后删除default reader。

**Gate C:** evaluation domain authority与supported import route唯一；missing layer不升级为live；EV-C05 fail-closed
archive admission和TA-C04 evidence joins保持不变。

**02 admission recheck（2026-08-14）:** `compute_metrics()` 仍是零 caller、零行为的 test helper residue，
`runtime/evaluation/contracts.py` 仍是 domain contract的纯 re-export；但`runtime.evaluation` facade有仓内
integration/evaluation consumer，且没有 repository-authorized Python support boundary。更重要的是，application
tree内没有可盘点的 retained `evals/runs` records，不能推断 private/external Evaluation Bundle或Review archive为空。
Evaluation Owner必须先提供 supported Python import route决定与 retained-record inventory/retention cutover；在此之前
02保持`not ready`，不创建 change。

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

先完成refinement method的supported consumer matrix；若Python export support仍未知，不创建04。

- [ ] **04 `converge-run-bundle-observation-authority`**: RS-C01..C04、RC-C01、OR-C03。Stage 1迁移
  negative invariants后退役RES；Stage 2迁移RUS、rename Bundle capabilities并修RWB registry；Stage 3迁移
  workbench/refinement consumers后删除state-only wrapper。

**Gate E:** Bundle/Journal/operator boundaries各有唯一owner；Local Session Workbench仍可用但不宣传broker；
binding/session store不能复活或在Bundle loss后recovery；PC-C05 refinement recovery语义与RS-C05 guards不变。

## Phase F - Run input与composition truth

创建05前一次性批准zero-credential UX，关闭recipe/profile parser Python export、supported Bundle mode、profile、
proposal与checkpoint producer inventories。

- [ ] **05 `converge-run-input-and-composition-contracts`**: FM-C01/C02/C04、EC-C06、PC-C01/C02、
  RC-C03、EV-C06。

`composition-mode` workstream依次迁移`ResearchGraphRecipe.create()` consumers、替换/退役no-graph full-fake
path、迁移/拒绝explicit `full_fake` records，并在missing-mode states关闭后删除default reader。`profile-proposal`
workstream用一张schema matrix收敛profile/proposal readers、evaluation consumer和Python export。两个workstream
共享的program终态是：每个admitted run input只产生显式、诚实、版本明确的composition truth。

**Gate F:** no-graph execution不再写成`all_real`/research-completed truth；supported State显式携带诚实mode；
profile/proposal旧输入要么已迁移/拒绝，要么有批准的bounded support；FM-C03、PC-C05与RC-C05保持current。

## Phase G - Runtime host input compatibility

创建06前一次关闭host trusted-context producer、supported deployment config/provider和AppConfig version inventories。

- [ ] **06 `converge-runtime-input-compatibility`**: EC-C05/C07、PC-C07、RC-C04。

`trusted-context` workstream决定`disable_clarification`到`non_interactive`的support window、notice、stale denial与
rollback。`deployment-config` workstream分别决定checkpointer precedence与endpoint field aliases；共享inventory，
不共享语义决定。owner决定继续支持时，在原workstream落实bounded support、guard和review/removal trigger。

**Gate G:** marker/config输入要么迁移删除，要么有批准的bounded support owner；unsupported、conflicting、stale
input继续fail closed；old-root、mount/config drift guards仍可证伪。

## Phase H - Retained run data compatibility

07只在04 archive后创建，并分别关闭checkpoint、Bundle、Journal与public/persisted Run result inventories；本机
样本只提供风险下界。每个workstream都要有dry-run、old/new reader-writer matrix、restart/replay、rollback、
negative evidence和post-cutover count。

- [ ] **07 `converge-retained-run-data-compatibility`**: PC-C03/C04/C06、RC-C06。

`repair-lifecycle-data` workstream迁移graph checkpoints后删除`repair_counts`，再迁移/拒绝old Bundle terminal并
退役`REPAIR_EXHAUSTED`。`observation-result-data` workstream收敛Journal manifest/event readers，再迁移/过期old
diagnostic-location results；不得把absence伪造成Journal publication或把failure映射成success。

**Gate H:** supported persisted records处于批准schema、明确rejection或有时限retained support；无silent
authenticity upgrade、failure-to-success mapping或无期限reader；summary v2、RS-C05和EV-C05 guards保持不变。

## Phase I - 最终全量复审与关闭

- [ ] 逐条检查Candidate Register全部54项，写最终disposition、change/archive evidence或approved retain decision。
- [ ] 重跑01中的tracked/current-term/legacy/compat/entry/config/serializer/export/spec/requirement/test-registry扫描。
- [ ] residual current matches逐条落入current behavior、approved old-input、negative guard或historical；建立小且有owner的allowlist。
- [ ] 第二次核对entry/public/persisted/AI-facing surfaces，不允许双writer、双entry、双authority或无期限compat reader。
- [ ] 检查每个retained guard的known/planted violation与scope escape；quiet不等于dead。
- [ ] 检查main specs、retired IDs、requirement/structure/evidence registries、CONTEXT、ADR status与current docs routes。
- [ ] 记录净删除files/LOC/tests/requirements与净新增concept；数字只描述结果，不作为成功理由。
- [ ] 记录未运行live/release/Postgres/real-Gateway、外部deployment/data/Python consumer evidence及接受风险。
- [ ] 更新[根 README](../README.md)的revision/status与审计结论，形成closeout，然后按backlog lifecycle归档整个plan目录。

**Final Gate:** [根 README](../README.md)完成定义全部满足；Candidate Register无`ready/blocked/unknown`；任何保留
compatibility都有decision authority、owner、review/removal trigger和failure behavior；00引入的program route
仍能机械拒绝缺owner、Candidate budget不闭合与未登记workstream，apply/archive review没有未解释scope drift。

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
