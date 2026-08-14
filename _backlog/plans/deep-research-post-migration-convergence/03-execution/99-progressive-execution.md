# 99 - Progressive Execution

> 导航: [执行层索引](README.md) | [Candidate Register](candidate-register.md) | [根总导航](../README.md)
> 角色: 最终逐步执行总计划
> 输入: [70-78 findings](../02-audit-findings/) 的54个最终Candidate；change映射以 [80 - Remediation Change Map](80-remediation-change-map.md) 为准
> 状态: 尚未开始；全局预算15个change（00-14）；checkbox只记录change closure，不替代active change的 `tasks.md`

## 不可跳过的执行协议

每一步都按同一个transaction完成，不批量预创建changes：

1. 在当前HEAD重验该步Candidate、consumer/data/export scope与前置gate；事实变化先修findings/register/map；
2. 只有该change所含全部decision/data/export gate关闭后才创建；一个smallest primary causal owner、一个bounded
   program outcome，一次一个active change；
3. proposal/design/delta冻结Candidate集合，并为每个内部stage明确target、owner、retirement、surface grade、
   decision authority、negative path、recovery与guard；
4. `tasks.md` 按stage承担逐文件工作；每个stage先做red/known violation，再迁移owner/behavior/evidence，
   最后删除old surface；
5. focused tests、相关lanes、full deterministic verify、governance与strict OpenSpec通过；
6. archive change，记录未运行的live/external evidence，更新所有linked Candidate最终disposition；
7. 确认无active change和意外worktree变化，再进入下一步。

若某项change仍缺任一产品决定、外部consumer或retained data，禁止先创建再等待。记录decision owner和缺失
证据后，只能继续准备依赖独立的前置项；最终closeout前所有blocked Candidate必须有授权结论。

**数量控制:** 本计划只允许 `00-14` 十五个槽位。内部stage不得升级成独立change；确需第16个时，必须先
修改`80`并获得明确批准，默认通过合并或取消另一个槽位保持总数仍为15。change不得夹带新功能或未审计重构。

## Phase A - 先恢复可复现交付

- [ ] **00 `restore-repository-automation-delivery`**: OR-C01, OR-C02, OR-C04。

验收：clean clone获得current CI workflows和可复现OpenSpec skills/install route；required artifacts由Git tracked；
`.gitignore`不再允许ignored copy冒充delivery；deterministic/manual-live/suspended lane语义不变。

**Gate A:** 00已archive；clean-clone trackedness negative control有效。Gate A前禁止所有产品cleanup。

## Phase B - 低风险证据与private减法

这四项都小，但primary owner不同，因此逐项创建、验证和archive；不建立虚假的“misc cleanup”owner：

- [ ] **01 `subtract-empty-test-scaffolding`**: TA-C01/C02、OR-C04 scaffold half；删除marker、空
  `tests/e2e`和registry row，保留TA-C03 suspension。
- [ ] **02 `retire-superseded-dpt-report`**: TA-C05、OR-C06；先对照TA-C06/C07 provenance，再删除
  report与shape-only test。
- [ ] **03 `subtract-demo-compatibility-helpers`**: EC-C04；把独有cases迁到canonical profile/preflight。
- [ ] **04 `subtract-topic-planner-legacy-helper`**: RC-C02；由canonical Bundle-profile tests承接行为。

**Gate B:** 01-04均archive；无orphan selector/registry/export；TA-C03/C04/C06/C07、EC-C01/C03与RC-C07
guards仍可证伪。任何public/persisted consumer命中都必须回到对应边界Candidate，不能在这些change中顺手处理。

## Phase C - Evaluation boundary收敛

先完成evaluation package consumer与retained Evaluation Bundle inventory，再创建05；零caller shim不另付一项
change成本，而是作为同一owner的首个stage。

- [ ] **05 `converge-evaluation-boundary-compatibility`**: EV-C02/C03/C04。Stage 1删除`compute_metrics()`
  shim；Stage 2把imports迁到唯一supported facade；Stage 3迁移/过期missing-`evidence_layer` records后删除default reader。

**Gate C:** evaluation domain authority与supported import route唯一；missing layer不升级为live；EV-C05 fail-closed
archive admission和TA-C04 evidence joins保持不变。

## Phase D - Node cognition与产品词典

- [ ] **06 `converge-node-cognition-contract-and-language`**: NC-C01/C02、OR-C03。Stage 1关闭legacy
  capability cohort/default并令missing/invalid ref fail closed；Stage 2用一张bounded term table纵向同步AI-facing
  policy、code、spec、test与registry。
- [ ] **07 `restore-product-glossary-ownership`**: NC-C03、EC-C02、OR-C05；逐段迁移独有规则后删除
  design/status residue，保留EV-C01 distinctions、`_Avoid_`和ADR history。

**Gate D:** required capability ref唯一；current identity不再使用`Phase Agent`；CONTEXT只承载current terms与
必要`_Avoid_`，没有丢失Evaluation Workspace/Bundle/Review/Run等真实不同概念。

## Phase E - Run/Bundle/Observation authority

先完成refinement method的supported consumer matrix；若export support仍未知，不创建08。

- [ ] **08 `converge-run-bundle-observation-authority`**: RS-C01..C04、RC-C01、OR-C03。Stage 1迁移
  negative invariants后退役RES；Stage 2迁移RUS、rename Bundle capabilities并修RWB registry；Stage 3迁移
  workbench/refinement consumers后删除state-only wrapper。

**Gate E:** Bundle/Journal/operator boundaries各有唯一owner；Local Session Workbench仍可用但不宣传broker；
binding/session store不能复活或在Bundle loss后recovery；PC-C05 refinement recovery语义不变。

## Phase F - Implementation mode与recipe surface

先批准zero-credential UX target，并一次性关闭recipe constructor export与supported Bundle mode inventories。
这些共同决定composition/provenance truth，因此只创建09。

- [ ] **09 `converge-implementation-mode-and-recipe-surface`**: FM-C01/C02/C04、EC-C06。Stage 1迁移
  `ResearchGraphRecipe.create()` consumers；Stage 2替换/退役no-graph full-fake path；Stage 3迁移/拒绝explicit
  `full_fake` records并退役enum；Stage 4迁移/过期missing-mode states后删除default reader。

**Gate F:** no-graph execution不再写成`all_real`/research-completed truth；supported State显式携带诚实mode；
FM-C03 fixture graph与explicit mixed composition保持current。

## Phase G - External support boundaries

每项只在自己的support matrix全部关闭后创建；owner决定继续支持时，在同一change内落实bounded support、guard和
review trigger，不为追求删除而破坏外部contract。

- [ ] **10 `converge-profile-proposal-compatibility`**: PC-C01/C02、RC-C03、EV-C06；同一schema matrix
  驱动profile/proposal readers、evaluation consumer和Python export收敛。
- [ ] **11 `resolve-non-interactive-marker-compatibility`**: EC-C07；按host producer inventory处理
  `disable_clarification` marker、notice、stale denial和rollback。
- [ ] **12 `converge-runtime-configuration-compatibility`**: EC-C05、PC-C07、RC-C04；共享一次
  deployment/AppConfig inventory，分stage决定checkpointer precedence与endpoint field aliases。

**Gate G:** profile/proposal/marker/config输入要么迁移删除，要么有批准的bounded support owner；unsupported、
conflicting、stale input继续fail closed；old-root和mount/config drift guards仍可证伪。

## Phase H - Remaining persisted compatibility

每项创建前分别关闭所需inventories；本机样本只提供风险下界。change内部每个stage都要有dry-run、old/new
reader-writer matrix、restart/replay、rollback、negative evidence和post-cutover count。

- [ ] **13 `retire-repair-lifecycle-compatibility`**: PC-C03/C04。Stage 1迁移graph checkpoints后删除
  `repair_counts`；Stage 2迁移/拒绝old Bundle terminal后退役`REPAIR_EXHAUSTED`。
- [ ] **14 `converge-run-observation-result-compatibility`**: PC-C06、RC-C06。Stage 1收敛Journal
  manifest/event readers；Stage 2迁移/过期old diagnostic-location results，且不得伪造Journal publication。

**Gate H:** supported persisted records处于批准schema、明确rejection或有时限retained support；无silent
authenticity upgrade、failure-to-success mapping或无期限reader；summary v2、RS-C05和EV-C05 guards保持不变。

## Phase I - 最终全量复审与关闭

- [ ] 逐条检查Candidate Register全部54项，写最终disposition、change/archive evidence或approved retain decision。
- [ ] 重跑00中的tracked/current-term/legacy/compat/entry/config/serializer/export/spec/requirement/test-registry扫描。
- [ ] residual current matches逐条落入current behavior、approved old-input、negative guard或historical；建立小且有owner的allowlist。
- [ ] 第二次核对entry/public/persisted/AI-facing surfaces，不允许双writer、双entry、双authority或无期限compat reader。
- [ ] 检查每个retained guard的known/planted violation与scope escape；quiet不等于dead。
- [ ] 检查main specs、retired IDs、requirement/structure/evidence registries、CONTEXT、ADR status与current docs routes。
- [ ] 记录净删除files/LOC/tests/requirements与净新增concept；数字只描述结果，不作为成功理由。
- [ ] 记录未运行live/release/Postgres/real-Gateway、外部deployment/data/Python consumer evidence及接受风险。
- [ ] 更新[根 README](../README.md)的revision/status与审计结论，形成closeout，然后按backlog lifecycle归档整个plan目录。

**Final Gate:** [根 README](../README.md)完成定义全部满足；Candidate Register无`ready/blocked/unknown`；任何保留compatibility都有
decision authority、owner、review/removal trigger和failure behavior。

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
