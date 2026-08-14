# 78 - Residual Compatibility Sweep Findings

> 取证基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 角色: 对 `70-77` 之外的 current-source compatibility/legacy/alias/fallback 命中做最后一轮定义级反查
> 范围: `deep_research_harness/src*`、current tests/docs/main specs；history/archive/_done 只用于消歧

## Sweep classification

本轮不把所有 `schema_version=1`、业务 fallback 或局部变量 `alias` 当迁移残留。一个命中只有在旧表面、
兼容 consumer/data、目标 owner 或 guard 能被具体指出时才进入 Candidate。结果分为：

| Cluster | 审计结论 |
| --- | --- |
| refinement wrapper | 有 current consumers；迁移消费者后可删 wrapper |
| topic planner short-state helper | test-only legacy helper；可删 |
| profile/HITL old inputs | persisted/participant compatibility；需支持与数据 cutover |
| config field aliases | external AppConfig input；需 support decision |
| recipe fingerprint / workspace alias probe | current drift/readiness guard；保留 |
| diagnostic location legacy branch | current spec-owned terminal-data compatibility；需 retained-data decision |
| synthesis/provider aliases and semantic fallback | current normalization/business behavior；不是 migration residue |

## Finding RC-01: `BundleLifecycle.refine()` 是仍被 current consumer 使用的 compatibility wrapper

`BundleLifecycle.admit_refinement()` 返回包含 disposition 与 State 的 `RefinementAdmission`，是 current
admission owner；`BundleLifecycle.refine()` 只返回其中的 State，并明确标记为 compatibility wrapper。
它仍被 Local Session Workbench、两个 lifecycle integration suites 和 HITL lifecycle tests调用，所以不是
dead code。production Bundle control已直接使用 `admit_refinement()`。

目标是先让 workbench消费 admission并保留现有 `BundleControlResult` 投影，再迁移只依赖 State 的 tests。
consumer归零后 wrapper可删；直接删除会破坏 current operator surface，永久保留则让两套 refinement API
继续竞争同一个 admission owner。

证据：

- `runtime/bundle_lifecycle.py`
- `runtime/bundle_control.py`
- `runtime/session_workbench.py`
- `tests/integration/test_{research_lifecycle_tool,hitl1_lifecycle,session_operations_lifecycle}.py`

## Finding RC-02: `planner_inputs_from_state()` 只维持 legacy short-state 测试路径

production topic planning调用 `planner_assignment_from_state()`，从 selected Bundle读取 canonical profile并
拒绝 checkpoint projection drift。`planner_inputs_from_state()` 直接读取旧 short fields，docstring明确称其为
fixture/catalog-only legacy helper；唯一 consumer是一条 focused unit test，`src_fake` 和 catalog都未调用它。

它绕开 canonical profile authority且没有独有 fixture能力。删除前只需确认测试覆盖已经由 canonical reader、
missing profile ref 和 projection mismatch cases承接；随后删除 helper、export与 shape-only test。

证据：

- `graph/nodes/topic_planning/prompts.py`
- `tests/graph/test_topic_planning_prompts.py`
- repository-wide tracked reference scan

## Finding RC-03: Profile/HITL compatibility 是一组 persisted 与 participant input contracts

profile v1/absent schema、`legacy_unspecified` request language、`ProposalValues` schema v1/v2、缺失
`proposal_version` 时的 first-version fallback，以及 profile parser的四个 JSON aliases都进入 current reader或
participant/model input边界。它们不能因名称旧就分别删除：old checkpoint/profile可能同时依赖多个字段，
而 `_JSON_ALIASES` 还接受 model/participant产生的长字段名。

PC-C01/C02已处理 duplicate helper与 v1 profile reader，但尚未明确这一组输入的联合 support boundary。
实施应先建立 profile/proposal schema support matrix，枚举 retained checkpoint/profile数据与 supported
participant producers，再决定 read-old/write-new、明确拒绝或有期限保留。不能把
`legacy_unspecified` 静默映射成 `unspecified`，因为前者表示旧数据缺少 intake fact，后者是 current language
derivation的真实结果。

证据：

- `domain/profile.py`
- `domain/human_interaction.py`
- `domain/state.py`
- `graph/nodes/hitl1/node.py`
- `tests/domain/test_{profile,human_interaction}.py`
- `tests/graph/test_hitl1_node.py`

## Finding RC-04: model endpoint field aliases 属于 external AppConfig input

`node_agent_bridge._configured_endpoint_authority()` 从 selected AppConfig model读取 `base_url`、
`openai_api_base`、`api_base`，只有全部有效且归一化后一致才投影 endpoint authority；冲突、credential-bearing
或 malformed值均不投影。它不从已创建的 model object反射私有连接信息。

这些 names来自外部 AppConfig shape，不是本包定义的三个可任意删 Python aliases。删除任一 reader前需由
Runtime Integration/Deployment Owner确认 supported DeerFlow/AppConfig versions与 producer inventory。当前
fail-closed conflict和redaction行为应保留。

证据：

- `runtime/node_agent_bridge.py`
- `tests/unit/test_node_agent_bridge.py`
- `research-run-experience` 与 `node-agent-runtime` main specs

## Finding RC-05: recipe compatibility fingerprint 与 workspace alias probe 是 current guards

recipe `compatibility_fingerprint` 把 topology、logical nodes、adapter kinds、state schema与 recipe revision绑定，
focused test证明 composition drift会改变 fingerprint。workspace “alias probe”则验证 host path与 sandbox
`/mnt/user-data` path确实指向同一 Bundle文件，并验证 POSIX read/write/cleanup；这里的 alias是挂载别名，不是
历史同义词。

两者都有 current consumer和可证伪 failure，不是 cleanup对象。未来若改名只能作为术语澄清，不得降低
drift/readiness sensitivity；本计划不创建 keep-only change。

证据：

- `runtime/research.py`
- `runtime/work_unit_storage.py`
- `domain/bundle.py`
- `tests/unit/test_research_runtime_capabilities.py`
- `tests/domain/test_work_unit_bundle.py`
- `deployment-configuration` main spec

## Finding RC-06: legacy diagnostic-location branch 仍由 current terminal contract拥有

`RunFailure` 对 provider diagnostic terminal要求 `diagnostic_ref` 与精确 `diagnostic_location`；对没有
provider recovery/observation的旧 terminal则要求该字段 absent。`research-run-experience` main spec正向定义
这一兼容行为，说明它不是注释残留。仓库内 fixtures覆盖 current locations，但 retained/public Run result数据
范围未知。

若 Product/Run Experience Owner要结束 old terminal reading，必须先枚举 retained result consumers/data，
决定 stale record rejection或migration，且不能制造 `bundle_journal` truth。否则保留 branch与 negative guard。

证据：

- `domain/run_experience.py`
- `runtime/run_experience.py`
- `tests/fixtures/run_updates.py`
- `openspec/specs/research-run-experience/spec.md`

## Finding RC-07: 其余高频 alias/fallback 命中是 current domain behavior

Wave 1/Wave 2 synthesis aliases把多种 provider/model output字段归一到 canonical evidence/finding refs；
readiness与HITL semantic fallback是 owning specs明确要求的 bounded failure behavior；Work Unit
`SUPERSEDED` 是当前 attempt terminal code。它们不是迁移兼容层，也没有第二 authority。

这类命中不会登记 deletion change。相关 owner未来改变 provider contract、semantic exhaustion或 concurrent
attempt policy时，应在自己的 change中重新审计，而不是由本计划的 residual zero-match目标驱动。

## 最终审计 Candidate

### RC-C01 - Migrate consumers and delete the state-only refinement wrapper

- **证据**: canonical `admit_refinement()`；production Bundle control已使用它；workbench与 focused tests仍消费
  `BundleLifecycle.refine()`。
- **当前 owner**: state-only compatibility wrapper与其 current consumers。
- **目标 owner**: `RefinementAdmission` 是唯一 admission result；workbench只投影自己的 control result。
- **Disposition**: `migrate then delete`。
- **迁移条件**: workbench处理 accepted/deduplicated/conflict dispositions且observable result不变；tests改走
  canonical admission或workbench boundary；确认无支持的外部 Python consumer。
- **删除条件**: tracked/external-supported consumers归零；wrapper与shape-only tests删除；refinement workflow、
  replay/recovery和workbench tests通过。
- **保留负向护栏**: operation-key digest conflict、duplicate receipt、active-Bundle conflict、CAS/restart/replay、
  textless selection与Bundle loss behavior不变。
- **OpenSpec change slice**: `converge-refinement-admission-api`，在 RS capability owner收敛后实施。

### RC-C02 - Delete the legacy short-state planner helper

- **证据**: `planner_inputs_from_state()`只有一条 test consumer；production用 canonical Bundle profile reader；
  fixture/catalog无调用。
- **当前 owner**: test-only legacy short-state convenience与export。
- **目标 owner**: `planner_assignment_from_state()` + canonical profile projection validation。
- **Disposition**: `delete`。
- **迁移条件**: 确认 canonical tests覆盖 request fallback、profile dimensions、language、comparison与degraded flag。
- **删除条件**: helper/export/test归零；topic-planning focused tests通过；production prompt behavior不变。
- **保留负向护栏**: missing/invalid profile ref、projection mismatch、current refinement generation mismatch继续 fail closed。
- **OpenSpec change slice**: `subtract-topic-planner-legacy-helper`，可与低风险 helper subtraction批次合并。

### RC-C03 - Resolve the joint profile and proposal input compatibility window

- **证据**: profile/ProposalValues v1/v2 readers、absent-schema default、`legacy_unspecified`、proposal-version
  fallback、JSON aliases与positive tests。
- **当前 owner**: profile persistence、HITL checkpoint与participant/model input readers共同承担兼容。
- **目标 owner**: 明确版本的 canonical profile/proposal input contract；或批准的有期限 read-old policy。
- **Disposition**: `product/data decision`。
- **迁移条件**: 建立联合 schema matrix；inventory supported profiles/checkpoints/producers；定义 notice、old-input
  rejection/migration、restart/replay与rollback。
- **删除条件**: 每个旧输入的 supported consumer/data为零或已迁移；spec/tests/writers/readers同批收敛；不得
  只删单个 enum/default造成旧 payload被误解释。
- **保留负向护栏**: unsupported schema/extra field fail closed；旧数据不制造 language/comparison/proposal事实；
  stale proposal correlation仍被拒绝。
- **OpenSpec change slice**: 扩展 `converge-profile-compatibility-readers`，并在 PC-C03 checkpoint inventory后准入。

### RC-C04 - Decide supported AppConfig endpoint aliases before reader subtraction

- **证据**: selected model config读取三种字段；conflict/malformed/credential tests；外部 AppConfig owner。
- **当前 owner**: Runtime Integration config compatibility reader。
- **目标 owner**: Deployment Owner批准的单一或有期限字段集合。
- **Disposition**: `product/support decision`。
- **迁移条件**: 枚举 supported host/AppConfig versions与producers；确定冲突、notice和rollback行为。
- **删除条件**: stale producers迁移；reader/tests/docs/spec同步；unknown shape不得转向model-object reflection。
- **保留负向护栏**: exact selected config only；conflict/malformed/userinfo fail closed；projection只含normalized origin。
- **OpenSpec change slice**: `resolve-model-endpoint-config-aliases`，可与 PC-C07 deployment support调查共用inventory，
  但分别决策。

### RC-C05 - Retain composition and workspace-alias drift guards

- **证据**: fingerprint drift test；host/sandbox two-way probe与mismatch result；main-spec readiness promise。
- **当前 owner**: graph recipe identity与Work Unit storage readiness。
- **目标 owner**: 不变。
- **Disposition**: `retain guard`。
- **迁移条件**: 无；相关 terminology change不得把挂载alias误写成legacy alias。
- **删除条件**: 仅当 replacement能检测相同 composition/mount drift并有 planted violation evidence时重新审计。
- **保留负向护栏**: topology/implementation drift changes fingerprint；mismatched mount、symlink/non-regular file、
  failed cleanup均不得ready。
- **OpenSpec change slice**: 无 keep-only change；作为 runtime/fixture/deployment changes 的 non-regression。

### RC-C06 - Keep legacy diagnostic-location compatibility until retained results close

- **证据**: current domain validator、positive main requirement、current writer与unknown retained Run results。
- **当前 owner**: Run Experience terminal result reader。
- **目标 owner**: exact current provider diagnostic publication truth；old terminal support由Product Owner定期复核。
- **Disposition**: `migrate then retire` 或有期限 `retain`，需data decision。
- **迁移条件**: inventory supported persisted/public Run results与consumers；定义migration/rejection/rollback。
- **删除条件**: supported old terminals归零；positive compatibility requirement、reader与tests同批关闭。
- **保留负向护栏**: absent old location不得伪造成Journal publication；provider terminal仍要求exact ref/location；
  secrets/raw exceptions不投影。
- **OpenSpec change slice**: `close-run-failure-diagnostic-location-compatibility`，在 Run Experience data inventory后。

### RC-C07 - Keep current normalization and bounded fallback behavior

- **证据**: synthesis provider-shape normalization、readiness/HITL failure policy、Work Unit supersession owners与tests。
- **当前 owner**: 各自domain/engine/cognitive-program contract。
- **目标 owner**: 不变。
- **Disposition**: `keep / rejected as cleanup`。
- **迁移条件**: 无。
- **删除条件**: 本计划不适用；只能由各 owning behavior的显式 redesign重新取证。
- **保留负向护栏**: alias normalization不得制造evidence；fallback保持bounded/non-terminal或typed failure；
  superseded attempt不得被接受为winner。
- **OpenSpec change slice**: 无 keep-only change。
