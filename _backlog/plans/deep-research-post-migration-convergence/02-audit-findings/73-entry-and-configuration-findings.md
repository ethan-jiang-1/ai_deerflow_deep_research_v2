# 73 - Entry And Configuration Findings

> 审计类型: product/operator entry / command ownership / configuration compatibility / dormant direction
> 审计基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 审计结论: current entries 大多有独立责任；应删除的是 full-fake bypass、test-only compatibility helpers 和 active glossary 中的 dormant product direction，不是把 CLI/TUI/workbench 全部合并

## Entry inventory

| Surface | User | Unique responsibility | Disposition |
| --- | --- | --- | --- |
| Dedicated Agent + reflected `deep_research` tool | Primary User | current recommended product route；fixed all-real control | keep |
| standalone real CLI | contributor/operator | credentialed scriptable smoke/calibration over shared Run result | keep |
| demo TUI | contributor/operator | visual presentation adapter over shared `RunUpdate` | keep；fake execution path 由 FM-C01 决定 |
| fixture graph command | maintainer/operator | deterministic complete graph-composition proof | keep |
| `demo-sessions inspect` | operator/support | one-shot, read-only Event Journal inspection | keep |
| Local Session Workbench | local operator | interactive fixed-profile Bundle controls + observations | keep |
| no-graph full-fake commands | contributor/operator | zero-credential presentation bypass | product decision，见 FM-C01 |

`demo-sessions` 与 workbench 都读取 Bundle observation，但前者是单一 non-mutating command，后者还
投影 legal controls、pending response、timeline 和 artifact metadata。当前没有证据证明两者责任重复到
足以删除其一。

## Finding EC-01: Product route 与 operator tools 已有明确边界

README、main specs 和 tests 一致声明 Dedicated Agent + reflected tool 是 current product route；CLI、
TUI、fixture demo 和 workbench 是 operator/evaluation surfaces，不是 versioned product CLI、Primary
User TUI 或通用 recovery client。这些边界测试能阻止 demo surface 意外升级成第二个 public product
authority，应保留。

证据：

- `deep_research_harness/README.md` 的 Entry Surfaces
- `deep_research_harness/src/deerflow_deep_research/tool.py`
- `deep_research_harness/config/public-skill/deep-research-controller/SKILL.md`
- `deep_research_harness/scripts/demo_real.py`
- `deep_research_harness/scripts/demo_tui.py`
- `deep_research_harness/scripts/demo_sessions.py`
- `deep_research_harness/scripts/session_workbench.py`
- `deep_research_harness/tests/contract/test_demo_commands.py`
- `openspec/specs/deployment-configuration/spec.md`
- `openspec/specs/research-cli-onboarding/spec.md`
- `openspec/specs/research-local-session-workbench/spec.md`

## Finding EC-02: Dormant Primary-User TUI/local-first direction 不应留在 current glossary

`deep_research_harness/CONTEXT.md` 把 `Local-First Deployment` 标为 `dormant`；ADR 0002/0008 保存了
历史的 Primary User TUI/local-first decision，current README 则明确 Demo TUI 不是 current Primary
User TUI。dormant direction 仍放在 current product glossary 会让读者误以为它是待启用 current
concept，也增加 Demo TUI 与 Primary User Interface 的名称冲突。

历史决策应保留在 ADR 并保持 status/supersession 路由；current glossary 应删除 dormant term，只保留
当前 `Operator Interface`、`Demo TUI`、`Local Session Workbench` 和 Current Recommended User Route
等真实概念。若产品重新启动 local-first，需要新 decision/change，而不是复活 glossary 状态。

证据：

- `deep_research_harness/CONTEXT.md` 的 `Local-First Deployment`
- `deep_research_harness/docs/adr/0002-tui-is-the-primary-user-interface.md`
- `deep_research_harness/docs/adr/0008-start-with-a-local-first-tui.md`
- `deep_research_harness/README.md`
- `deep_research_harness/docs/local-operations.md`

## Finding EC-03: Old-root/legacy entry checks 是 migration admission guards，不是死代码

configurator 检测 `skills/custom/deep-research-controller` 和 shared legacy Agent root，并拒绝静默
覆盖/迁移；architecture/config tests 也阻止 former `deerflow_research` source root、legacy public skill
和 legacy shared Agent 复活。这些 guards 保护单一 current entry 和 source root，仍有明确 violation，
不能因命中 `legacy` 就删除。

它们的 review trigger 是 supported installation baseline 明确不可能再包含旧 entry，且 project structure
已有等强度 planted violation coverage。在此之前 disposition 是 retain guard，不是永久兼容 reader：
它们只拒绝旧路径，不执行旧路径。

证据：

- `deep_research_harness/scripts/configure.py`
- `deep_research_harness/tests/contract/test_configure.py`
- `deep_research_harness/tests/contract/test_public_skill.py`
- `deep_research_harness/tests/contract/test_agent_provisioning.py`
- `deep_research_harness/tests/contract/test_architecture_governance.py`
- `openspec/specs/deployment-configuration/spec.md`
- `openspec/specs/project-structure/spec.md`

## Finding EC-04: 两个 demo compatibility helpers 只有测试 consumer

`_demo_core._resolve_demo_models()` 自称 compatibility helper，production entry 使用
`resolve_real_demo_model_profile()`；`check_credentials_available()` 也只被 unit tests 直接调用，current
entry preflight 使用 `demo_readiness_report()` / `validate_real_demo_prerequisites()`。仓库内没有其他
production consumer。

这些 helper 和只保护 helper shape 的 tests 可以删除，保留对 canonical profile resolver、缺失选择、
credential redaction 和 preflight-before-Bundle 的行为测试。`DemoAppConfig` 仍被 real demo/evaluation
test adapters 使用，不属于该删除项。

证据：

- `deep_research_harness/scripts/_demo_core.py`
- `deep_research_harness/tests/unit/test_demo_core.py`
- repository-wide current reference scan（排除 history/venv）

## Finding EC-05: Legacy checkpointer 是外部 config promise，不能由 local-profile 证据批准删除

local profile initializer 删除 copied `checkpointer`，validator 拒绝 profile 内 legacy section；当前仓库
可见 root/profile config 只使用 `database`。但 runtime `resolve_effective_provider()` 明确优先
`app_config.checkpointer`，doctor/probe/GraphHost 和 main specs/tests 都保护该 precedence。它接受的是
deployment-provided AppConfig，外部支持范围不能由仓库内 config 样本推断。

因此这不是立即 cleanup。Deployment Owner/product 必须决定 generic runtime 是否结束 legacy
checkpointer support、冲突时 fail 还是切到 database、怎样通知和回滚。完整 Candidate 在 persisted
compatibility report 中。

证据：

- `deep_research_harness/src/deerflow_deep_research/runtime/checkpoint.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/{probe,startup_snapshot,diagnostics,graph_host}.py`
- `deep_research_harness/scripts/local_profiles.py`
- `deep_research_harness/tests/unit/test_startup_snapshot.py`
- `openspec/specs/runtime-integration/spec.md`
- `openspec/specs/deployment-configuration/spec.md`
- `openspec/specs/local-configuration-profiles/spec.md`

## Finding EC-06: `ResearchGraphRecipe.create()` 是无人使用的 compatibility constructor

`ResearchGraphRecipe.create()` 只把参数原样转给 `ResearchGraphRecipe.all_real()`，正文也明确称它为
compatibility constructor。current production、scripts、runtime assembly 与 fixtures 都不调用它；唯一
consumer 是 `test_topology_and_implementation.py` 把它与 `all_real` 并列，验证两者都不接受 caller-selected
implementation modes。换言之，当前测试在保护 alias 的 signature，而不是独有行为。

这是 exported Python surface，不能只凭 private dead-code 规则删除；但仓库内 consumer 已经封闭，目标
constructor 也明确。实施时需先确认项目对第三方 Python import 的 support boundary；若没有承诺外部
consumer，可 clean break 删除，并把 fixed-all-real invariant 只留在 canonical `all_real()` 上。

证据：

- `deep_research_harness/src/deerflow_deep_research/runtime/research.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/bundle_graph.py`
- `deep_research_harness/tests/graph/test_topology_and_implementation.py`
- repository-wide tracked reference scan

## Finding EC-07: `disable_clarification` 是现行受信输入 alias，不是可直接删的旧字符串

`tool.py` 同时接受 canonical `non_interactive=true` 与 `disable_clarification=true`，而
`runtime-operations`、`runtime-integration` main specs 和 focused tests 明确把后者定义为 existing trusted
compatibility marker。它不是 public reflected-tool argument，也不进入 checkpoint；但它是 host/runtime
context 的 cross-boundary trusted-input promise，仓库无法枚举所有 host producer。

current writer `ResearchRunExperience` 只发 canonical marker，说明内部迁移已完成；外部 host producer 与
support window仍未知。因此它不能跟普通 alias 一起机械删除。Product/Runtime Integration Owner 需要决定
是否结束 marker compatibility；若结束，应先观测或枚举 producer，给 stale producer 明确 denial，并保留
canonical policy validation。不能把 alias 静默解释成 interactive request，因为那会改变 admission 语义。

证据：

- `deep_research_harness/src/deerflow_deep_research/tool.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/run_experience.py`
- `deep_research_harness/tests/unit/test_non_interactive.py`
- `openspec/specs/runtime-operations/spec.md`
- `openspec/specs/runtime-integration/spec.md`

## 最终审计 Candidate

### EC-C01 - Keep distinct current entry surfaces

- **证据**: README Entry Surfaces；scripts/Make targets；public tool/skill；CLI/TUI/session/workbench tests
  与 owning specs。
- **当前 owner**: product route、real operator CLI、TUI presentation、fixture proof、one-shot inspection、
  interactive workbench 各有独立 adapter/contract。
- **目标 owner**: 不变；entry index 继续只作路由，不成为行为 authority。
- **Disposition**: `keep`。
- **迁移条件**: FM-C01 单独处理 fake path；RS candidates 单独收敛 session/Bundle terminology。
- **删除条件**: 不适用。未来删除任一 entry 必须先证明 unique outcome 被明确 replacement 接管、所有
  Make/docs/test consumers 迁移且更高等级 behavior 不变。
- **保留负向护栏**: product fixed all-real；operator surfaces 非 public product authority；inspection
  read-only；workbench fixed profile；real entry preflight before Bundle/model/tool work。
- **OpenSpec change slice**: 无 keep-only change；相关 sync 分别进入 FM/RS changes。

### EC-C02 - Move dormant local-first direction out of current language

- **证据**: `CONTEXT.md::Local-First Deployment`; ADR 0002/0008；README 明确 Demo TUI 非 Primary UI。
- **当前 owner**: current product glossary 承载 dormant historical direction。
- **目标 owner**: ADR 保存历史及 status；current glossary 只保留实际 entry/operator concepts。
- **Disposition**: `migrate then delete`。
- **迁移条件**: 核对 ADR status/supersession 和 current docs 路由；确认没有 active spec/roadmap commitment。
- **删除条件**: current code/spec/entry 不依赖 dormant term；ADR 足以解释历史；删除 glossary term 后
  Demo TUI/Local Session Workbench distinction仍清晰。
- **保留负向护栏**: tests/docs 继续声明 Demo TUI/workbench 不是 Primary User product route；未来复活
  必须新 OpenSpec change 和 product decision。
- **OpenSpec change slice**: `restore-product-glossary-ownership`，与 NC-C03/OR-C05 同批。

### EC-C03 - Retain old-entry rejection guards

- **证据**: configure old skill/Agent detection；architecture old-root tests；public skill/provisioning tests。
- **当前 owner**: deployment configurator 和 project-structure admission。
- **目标 owner**: 不变；明确它们是 rejection/anti-resurrection，不是 compatibility execution。
- **Disposition**: `retain guard`。
- **迁移条件**: 术语清理时保留 planted old paths 和 exact failure expectations。
- **删除条件**: 只有 Deployment Owner 关闭旧安装 baseline，且另一个 current guard 能检测相同并行 entry/
  source-root violation 时才能重新审计。
- **保留负向护栏**: old source root、legacy custom skill、legacy shared Agent 不得成为 fallback、alias、
  overwrite target 或第二 authority。
- **OpenSpec change slice**: 无独立 change；作为 entry/config changes 的 non-regression requirement。

### EC-C04 - Delete test-only demo compatibility helpers

- **证据**: `_demo_core._resolve_demo_models` 与 `check_credentials_available` 仅有 unit-test references；
  current entries 使用 canonical profile/preflight APIs。
- **当前 owner**: private compatibility helper + implementation-shape tests。
- **目标 owner**: `resolve_real_demo_model_profile`、`demo_readiness_report`、
  `validate_real_demo_prerequisites`。
- **Disposition**: `delete`。
- **迁移条件**: 将 helper tests 中独有的 supported-profile/blank-credential cases并入 canonical API tests。
- **删除条件**: current tracked source 无 helper consumer；canonical tests 覆盖相同行为；demo focused tests
  与 lint 通过。
- **保留负向护栏**: explicit model selection、one matching credential、safe revision、no secret projection、
  preflight failure before adapter/Bundle。
- **OpenSpec change slice**: `subtract-demo-compatibility-helpers`；不与 exported constructor、glossary 或
  persisted/config decision 混批。

### EC-C05 - Decide legacy checkpointer support explicitly

- **证据**: runtime resolver precedence；doctor/probe/GraphHost consumers；local profiles reject legacy；
  current repository config samples use database；specs/tests explicitly require legacy precedence。
- **当前 owner**: deployment AppConfig compatibility contract and `resolve_effective_provider()`。
- **目标 owner**: 由 Deployment Owner 决定 database-only contract，或批准有期限 legacy reader。
- **Disposition**: `product decision`。
- **迁移条件**: 枚举 supported deployment configs；选择 conflict/rejection behavior、notice window、backup/
  rollback；验证 GraphHost 与 diagnostics 同步 cutover。
- **删除条件**: 见 `75-persisted-compatibility-findings.md::PC-C07`。
- **保留负向护栏**: doctor/GraphHost 必须同选一个 provider；不得静默选择错误 durability；DSN/secret
  不得进入 output；local profile isolation继续拒绝 legacy section。
- **OpenSpec change slice**: `converge-runtime-configuration-compatibility`，在产品/support decision 后准入。

### EC-C06 - Delete the `ResearchGraphRecipe.create()` constructor after export-scope closure

- **证据**: `create()` 只转发 `all_real()`；production/entry/fixture 无 consumer；唯一 reference 是
  fixed-all-real signature test。
- **当前 owner**: exported compatibility alias 与 implementation-shape test。
- **目标 owner**: `ResearchGraphRecipe.all_real()` 是唯一 production recipe constructor；
  `from_adapters()` 与 fixture `mixed_recipe()` 分别拥有 explicit composition seams。
- **Disposition**: `delete`，但先关闭外部 Python import support scope。
- **迁移条件**: Runtime Integration Owner确认该包不承诺未登记第三方 constructor consumer，或完成其
  通知/迁移；将 invariant test 改为只保护 `all_real()` 不接受 mode selection。
- **删除条件**: tracked consumers 为零；export/docs/spec 无 `create()` route；focused graph/runtime tests通过。
- **保留负向护栏**: public runtime仍只能构造 all-real；caller不得通过 adapters、implementations或
  implementation_modes 改写 production composition。
- **OpenSpec change slice**: `converge-implementation-mode-and-recipe-surface`；因 surface grade不同，不与 private demo
  helpers或 `disable_clarification` 决策捆绑。

### EC-C07 - Decide the `disable_clarification` trusted-context compatibility window

- **证据**: tool admission reader、canonical internal writer、main-spec compatibility requirements与双 marker
  focused tests；无可枚举 external host producer inventory。
- **当前 owner**: Runtime Integration trusted-context contract。
- **目标 owner**: canonical `non_interactive=true` + closed `non_interactive_policy`；或由 Product/Runtime
  Integration Owner批准有期限的 alias reader。
- **Disposition**: `product decision`。
- **迁移条件**: 枚举/观测 supported host producers；确定 notice window、stale-marker denial code与 rollback；
  证明 internal writers只发 canonical marker。
- **删除条件**: supported producers已迁移；main specs/tests移除 positive alias promise；old marker有明确拒绝
  或被完全关闭，且不会静默退回 interactive behavior。
- **保留负向护栏**: 两种 marker在兼容期均要求 exact closed policy；resume/refine不得重新注入 checkpoint
  policy；caller/presentation input不得伪造 trusted context。
- **OpenSpec change slice**: `resolve-non-interactive-marker-compatibility`，取得 product/support decision后准入。
