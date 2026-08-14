# 99 - Progressive Execution

> 角色: 最终逐步执行总计划
> 输入: `70-78` 的54个最终Candidate；change映射以 `80-remediation-change-map.md` 为准
> 状态: 尚未开始；checkbox只记录阶段/change closure，不替代active change的 `tasks.md`

## 不可跳过的执行协议

每一步都按同一个transaction完成，不批量预创建changes：

1. 在当前HEAD重验该步Candidate、consumer/data/export scope与前置gate；事实变化先修findings/register/map；
2. 只有gate关闭后，使用OpenSpec CLI创建一个change；一个primary causal owner，一次一个active change；
3. proposal/design/delta明确target、retirement、surface grade、decision authority、negative path、recovery与guard；
4. `tasks.md` 承担逐文件工作，先做red/known violation，再迁移owner/behavior/evidence，最后删除old surface；
5. focused tests、相关lanes、full deterministic verify、governance与strict OpenSpec通过；
6. archive change，记录未运行的live/external evidence，更新所有linked Candidate最终disposition；
7. 确认无active change和意外worktree变化，再进入下一步。

若某一步仍缺产品决定、外部consumer或retained data，禁止创建假实施change。记录decision owner和缺失证据后，
只能进入一个依赖独立且不会扩大双authority的后续step；最终closeout前所有blocked Candidate必须有授权结论。

## Phase A - 先恢复可复现交付

- [ ] **00 `restore-repository-automation-delivery`**: OR-C01, OR-C02, OR-C04。

验收：clean clone获得current CI workflows和可复现OpenSpec skills/install route；required artifacts由Git tracked；
`.gitignore`不再允许ignored copy冒充delivery；deterministic/manual-live/suspended lane语义不变。

**Gate A:** 00已archive；clean-clone trackedness negative control有效。Gate A前禁止所有产品cleanup。

## Phase B - 低风险证据与private减法

这些仍逐项创建、验证、archive，不合并成misc cleanup：

- [ ] **01 `subtract-empty-test-scaffolding`**: TA-C01, TA-C02；删除8个冗余marker、空`tests/e2e`与registry row，保留TA-C03 suspension。
- [ ] **02 `retire-superseded-dpt-report`**: TA-C05, OR-C06；先对照TA-C06/C07 provenance，再删report与shape-only test。
- [ ] **03 `subtract-demo-compatibility-helpers`**: EC-C04；把独有cases迁到canonical resolver/preflight后删除private helpers。
- [ ] **04 `subtract-topic-planner-legacy-helper`**: RC-C02；canonical Bundle-profile tests承接后删short-state helper/export/test。
- [ ] **05 `subtract-evaluation-test-compatibility`**: EV-C04；删除零caller metrics shim，不改typed metric authority。

**Gate B:** 01-05均archive；无orphan selector/registry/export；TA-C03/C04/C06/C07与EV-C05 guards仍可证伪。

## Phase C - Node cognition与词典收敛

- [ ] **06 `close-node-capability-migration`**: NC-C01 + OR-C03；删除legacy cohort/default，missing/invalid capability在model/tool前fail closed。
- [ ] **07 `converge-node-cognition-language`**: NC-C02；批准bounded term table后，纵向同步AI-facing policy、code、spec、test与registry。
- [ ] **08 `restore-product-glossary-ownership`**: NC-C03, EC-C02, OR-C05；保留EV-C01 distinctions和ADR history，移除重复design/dormant status ledger。

**Gate C:** required capability ref唯一；current identity不再使用`Phase Agent`；CONTEXT只承载current terms与必要
`_Avoid_`，没有丢失Evaluation Workspace/Bundle/Review/Run等真实不同概念。

## Phase D - Run/Bundle/Journal owner收敛

- [ ] **09 `retire-session-lifecycle-binding`**: RS-C01；先把negative invariants/evidence迁到DRH/REJ/PRS owners，再退役RES capability/IDs。
- [ ] **10 `consolidate-run-observation-ownership`**: RS-C02..C04；迁移RUS语义、rename Bundle capabilities、修RWB registry，同时保留RS-C05 guards。

**Gate D:** Bundle/Journal/current operator boundaries各有唯一owner；Local Session Workbench仍可用但不宣传broker；
binding/session store不能复活、不能在Bundle loss后提供recovery。

## Phase E - Export与support边界逐项决策

每项先关括号内gate；owner选择继续支持时，把Candidate标`rejected/guard-retained`并记录review trigger，
不强行为了勾选而删除。

- [ ] **11 `retire-recipe-constructor-alias`**: EC-C06（Python constructor support scope）。
- [ ] **12 `converge-evaluation-contract-exports`**: EV-C03（supported import facade与consumer inventory）。
- [ ] **13 `converge-refinement-admission-api`**: RC-C01（10已archive；workbench disposition mapping；method export scope）。
- [ ] **14 `converge-profile-compatibility-readers`**: PC-C01, PC-C02, RC-C03, EV-C06（joint profile/proposal schema matrix、retained profiles/checkpoints、participant producers、Python exports）。
- [ ] **15 `resolve-non-interactive-marker-compatibility`**: EC-C07（host producer inventory、notice、stale-marker denial、rollback）。
- [ ] **16 `resolve-legacy-checkpointer-precedence`**: EC-C05, PC-C07（supported deployment configs、conflict behavior、provider parity、rollback）。
- [ ] **17 `resolve-model-endpoint-config-aliases`**: RC-C04（supported AppConfig versions/producers；可复用16的inventory但独立决策）。
- [ ] **18 `resolve-full-fake-demo-contract`**: FM-C01（明确zero-credential UX选择；保留FM-C03 fixture/mixed真实性边界）。

**Gate E:** 每个export/config/input alias要么已迁移删除，要么有批准的bounded support owner；没有永久
“先留着”的unknown。no-graph fake path不再把非graph execution写成`all_real`/research-completed truth。

## Phase F - Persisted schema逐项迁移

默认按19-25推进；某项data gate未关闭时可先做一个依赖独立的后项，但不能跳过该项最终closure。
每一步必须有inventory/dry-run、old/new reader-writer matrix、restart/replay、rollback与post-cutover evidence。

- [ ] **19 `retire-full-fake-implementation-mode`**: FM-C02（18 target decision + retained Bundle inventory）。
- [ ] **20 `close-bundle-state-mode-compatibility`**: FM-C04（60个local missing-mode样本只是风险下界；supported states须迁移/过期）。
- [ ] **21 `retire-frozen-repair-counts-state`**: PC-C03（all checkpoint providers/data；gate kernel仍是唯一repair authority）。
- [ ] **22 `retire-repair-exhausted-terminal-reason`**: PC-C04（retained Bundle data + exact failure mapping/rejection）。
- [ ] **23 `converge-run-observation-schema-readers`**: PC-C06（10已archive；56个local v2 manifests与616条v2 events；summary v2保持current）。
- [ ] **24 `close-evaluation-evidence-layer-compatibility`**: EV-C02（retained/private Evaluation Bundle/review inventory）。
- [ ] **25 `close-run-failure-diagnostic-location-compatibility`**: RC-C06（retained/public Run result inventory；不得伪造Journal publication）。

**Gate F:** supported persisted records全部处于批准schema或明确rejection；无silent authenticity upgrade、failure-to-
success mapping或旧reader永久悬空；PC-C05 refinement recovery、RC-C05 guards保持不变。

## Phase G - 最终全量复审与关闭

- [ ] 逐条检查Candidate Register全部54项，写最终disposition、change/archive evidence或approved retain decision。
- [ ] 重跑00中的tracked/current-term/legacy/compat/entry/config/serializer/export/spec/requirement/test-registry扫描。
- [ ] residual current matches逐条落入current behavior、approved old-input、negative guard或historical；建立小且有owner的allowlist。
- [ ] 第二次核对entry/public/persisted/AI-facing surfaces，不允许双writer、双entry、双authority或无期限compat reader。
- [ ] 检查每个retained guard的known/planted violation与scope escape；quiet不等于dead。
- [ ] 检查main specs、retired IDs、requirement/structure/evidence registries、CONTEXT、ADR status与current docs routes。
- [ ] 记录净删除files/LOC/tests/requirements与净新增concept；数字只描述结果，不作为成功理由。
- [ ] 记录未运行live/release/Postgres/real-Gateway、外部deployment/data/Python consumer evidence及接受风险。
- [ ] 更新本README的revision/status与审计结论，形成closeout，然后按backlog lifecycle归档整个plan目录。

**Final Gate:** README完成定义全部满足；Candidate Register无`ready/blocked/unknown`；任何保留compatibility都有
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
