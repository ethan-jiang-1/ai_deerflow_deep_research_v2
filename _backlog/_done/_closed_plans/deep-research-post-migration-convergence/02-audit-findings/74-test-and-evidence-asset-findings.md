# 74 - Test And Evidence Asset Findings

> 取证基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 范围: tracked test scaffolding、selectors、executable evidence registries、release records 与其 current routes
> 排除: 不以测试数量或年代授权删除；不读取 `deerflow/`

## 当前证据 spine

测试资产不是一个可以按目录整体保留或删除的 owner。当前至少有五种不同责任：

| 资产 | 当前责任 | 删除判断 |
| --- | --- | --- |
| pytest selector | 在最低责任 seam 证明 current behavior 或 failure | owning behavior 迁移后逐 selector 判断 |
| negative/suspension guard | 阻止退役入口复活或 suspended lane 被误激活 | 先证明 planted violation 仍被检测 |
| executable registry/join | 把 requirement、risk、selector、lane 和 evidence class 连起来 | 只能随 owning row 做 subtraction |
| dated attestation/baseline | 保存某个 evidence epoch 的事实和限制 | historical route 清楚即可，不证明 current freshness |
| empty marker/scaffold | 只维持 Git 目录或结构 registry | 无 tool/package/owner consumer 时删除 |

`make verify` 会执行 `scripts/check_test_assets.py`、requirement coverage 和各 deterministic lane。
checker 明确拒绝空 collection；因此 registry 不是一批被动文档，也不能靠删 selector 或缩小扫描范围
制造绿色。

## Finding TA-01: 9 个 `.gitkeep` 中 8 个已经没有作用

tracked markers：

- `config/.gitkeep`
- `docker/.gitkeep`
- `scripts/.gitkeep`
- `src/deerflow_deep_research/resources/.gitkeep`
- `tests/e2e/.gitkeep`
- `tests/fixtures/.gitkeep`
- `tests/graph/.gitkeep`
- `tests/integration/.gitkeep`
- `tests/unit/.gitkeep`

除 `tests/e2e` 外，其余八个目录都已有 tracked current files。Git 不需要 marker 才能保留这些目录，
package、pytest collection 和 `project-structure.toml` 也只依赖真实目录/文件，不依赖 `.gitkeep`。
这八个 marker 是可直接证明无行为消费者的 private repository residue。

## Finding TA-02: `tests/e2e` 是唯一空 scaffold，但 governance 把它当 current structure

`tests/e2e` 只有 `.gitkeep`，没有 selector、fixture、package initializer、Make/CI path 或 current docs
consumer。唯一正向 inbound reference 是：

- `openspec/governance/project-structure.toml` 将目录登记为 `PRS-001` required path。

`pyproject.toml` 使用整个 `tests` 作为 `testpaths`；删除空子目录不会改变 collection。当前 release/live
lanes 也不使用 `tests/e2e`：full-real selector 在明确 suspended 的目录，live canaries 在 current scenario
owner 下。因而 target topology 不需要空 `e2e` 分类。删除必须同时缩减 structure registry，不能只删
`.gitkeep` 后让 checker 失败，也不能为了 checker 保留空目录。

## Finding TA-03: EVH-024 是明确 suspended 的受控资产，不是 orphan test

`tests/scenarios_suspended/evh_024_release_acceptance.py` 不符合默认 `test_*.py` collection 名称，并且：

- 没有 Make target、CI workflow、published command 或 active selector claim；
- `test_release_suspension.py` 明确验证它存在但不能进入 active lanes；
- local README 指向 suspended diagnosis，并要求先建立小于十秒的 deterministic loop；
- `release_e2e` marker 被保留为 suspension marker；
- EVH-024 的 current deterministic evidence 由其他 collected selectors 承担，不由 suspended selector
  冒充完成证据。

这是一个有 owner、inactive invariant 和 reactivation gate 的 suspension boundary。机械删除会抹掉未来
诊断材料；机械移回普通 tests 则会复活一个未经授权的 credentialed execution surface。

## Finding TA-04: Evidence registries 体量大，但它们是 current executable joins

`tests/assets/`、`tests/scenarios/`、`tests/fixtures/provider_shapes/` 与
`scripts/check_test_assets.py` 当前连接：

- alive/retired requirement IDs 与 `@impl` evidence；
- selector、marker expression、lane 和 evidence authenticity class；
- incident、fault、workflow/node conformance、provider-shape archive；
- cognitive-program boards、calibration cases 与 requirement impacts。

contract tests覆盖 orphan selector、空 collection、duplicate ID、invalid evidence class、错误 lane 和
requirement mismatch。故不能因 registry 大或含历史 discovery row 整体删除。真正的 residue 是：owning
requirement/selector 已退役后仍留下的单行 claim、impact 或 fixture；它们应随对应 authority cluster 同批
减少，而不是另建第二套总 registry 或一次 wholesale rewrite。

## Finding TA-05: Superseded imported workflow report 只被 shape-only test 保护

已删除的 historical parity report 自身声明已被
`release-attestation-2026-07-17.json` supersede。它没有进入 `docs/README.md`、产品 README 或 current
testing guide；唯一 current inbound consumer 是 `test_release_evidence_report.py`，该测试逐字保护旧
`NOT READY`、`2 of 3` 和 “full-real not executed” 形状。

当前 docs index 已把读者路由到 dated live baseline、accepted release attestation 和 regression-descent
policy。旧 report 不再拥有 current verdict，shape-only test 也不验证当前 behavior。删除前只需把仍有
独特历史价值的 failure/provenance fact 与三份 current records 做一次对照；不能为了保留旧测试而继续
制造第二份 release verdict。

## Finding TA-06: Dated baseline 与 release attestation 是历史证据，不是 current freshness

`live-evaluation-baseline-2026-07-17.md` 和 `release-attestation-2026-07-17.json` 都由 current docs index
明确导航，并由 contract tests 验证 provenance、redaction、已知失败和 evidence limitation。它们分别
保存一个 partial live epoch 与一个 accepted isolated run；正文已禁止把它们提升为 current release
result、provider distribution 或 general quality threshold。

年代本身不构成删除理由。需要收敛的是 role：dated artifacts 只作 frozen historical evidence；current
lane 状态由 workflow/config/current guide 投影。未来 evidence epoch 可新增新 artifact 或显式 supersede，
不能静默改写旧数据来伪造 freshness。

## Finding TA-07: Regression descent 是 current policy，不是 dated report 残留

`docs/regression-descent.md` 仍由 testing guide、contract tests 和 live/release defect workflow 正向引用。
它规定 provider-only observation 如何下沉为最低可复跑 deterministic seam，并区分不能 replay 的 live
rationale。这是 current evidence governance；它与某一份 2026-07-17 report 不同，不应随旧 report
一起删除。

## 最终审计 Candidate

### TA-C01 - Delete eight redundant `.gitkeep` markers

- **证据**: 九个 tracked markers 的目录 inventory；除 `tests/e2e` 外八个目录均已有 tracked files。
- **当前 owner**: 无行为 owner；marker 只曾用于 Git 保存空目录。
- **目标 owner**: 真实 current files 和既有 structure registry 继续拥有目录存在性。
- **Disposition**: `delete`。
- **迁移条件**: 无行为迁移；确认 packaging/pytest 不按 marker filename 消费即可。
- **删除条件**: 删除八个 marker 后目录仍非空；structure checker、pytest collection 和 lint 通过。
- **保留负向护栏**: 不删除目录、真实文件或对应 required-path entries；不触碰 `tests/e2e` marker，后者由
  TA-C02 处理。
- **OpenSpec change slice**: `restore-delivery-and-subtract-dead-assets` 的 `test-structure` workstream。

### TA-C02 - Retire the empty `tests/e2e` scaffold and registry entry

- **证据**: `tests/e2e` 只有 `.gitkeep`；无 selectors/Make/CI/docs consumer；structure registry 有一条
  `PRS-001` required-directory entry。
- **当前 owner**: project-structure registry 人为维持一个空分类。
- **目标 owner**: current deterministic/live/suspended selectors 留在已有实际目录；未来 full E2E lane 由
  新 change 明确创建，而不是预留空目录。
- **Disposition**: `delete`。
- **迁移条件**: structure delta 同步批准删除 required path；证明 pytest testpaths 和 lane selections 不变。
- **删除条件**: `.gitkeep`、空目录和 registry entry 同批消失；structure、asset、lane-selection checks 通过。
- **保留负向护栏**: EVH-024 仍保持 suspended；不得借删除空 e2e scaffold 激活 release selector或缩小
  tests root 扫描。
- **OpenSpec change slice**: `restore-delivery-and-subtract-dead-assets` 的 `test-structure` workstream，与
  TA-C01 同批。

### TA-C03 - Retain the EVH-024 suspension boundary

- **证据**: suspended selector、local README、`test_release_suspension.py`、marker registration、EVH-024
  deterministic evidence rows和 suspended diagnosis。
- **当前 owner**: evaluation-hardening owns retained diagnostic material；suspension guard owns inactivity。
- **目标 owner**: 不变。
- **Disposition**: `retain guard`。
- **迁移条件**: 无。相关 test cleanup 必须验证 selector仍不被 collection/Make/CI/claims选择。
- **删除条件**: 不适用当前计划。只有 product/evaluation owner明确永久放弃该诊断目标，并迁移所有独特
  EVH-024 risk/provenance evidence后，才可另行审计删除。
- **保留负向护栏**: no active selector claim、no command/workflow、less-than-ten-second prerequisite、
  credentialed execution需新 approved change。
- **OpenSpec change slice**: 无 keep-only change；作为所有 test-asset changes 的 non-regression gate。

### TA-C04 - Keep executable evidence registries and subtract rows only with their owner

- **证据**: `check_test_assets.py` joins、asset/requirement contract tests、non-empty collection guard与
  Make `test-assets` gate。
- **当前 owner**: evaluation/test-evidence governance及每个 row 对应的 owning requirement/risk。
- **目标 owner**: 不变；每次 behavior retirement在同一个 change 内删除 orphan row/fixture/selector。
- **Disposition**: `keep` registry mechanism; `delete` only grounded owner-local rows。
- **迁移条件**: 每个 subtraction先给出 displaced requirement/risk 到 retained proof 的映射。
- **删除条件**: 不适用 wholesale deletion；单行删除条件是 selector/requirement已退役或 replacement proof
  已 collected，所有 joins仍非空且无 orphan。
- **保留负向护栏**: empty catalog、orphan selector/ID、duplicate join、错误 evidence class和 lane escape
  继续 fail closed。
- **OpenSpec change slice**: 不建 registry-cleanup mega-change；作为 NC/RS/FM/PC owning changes 的
  mandatory evidence-subtraction task。

### TA-C05 - Delete the superseded imported workflow report and its shape-only test after evidence comparison

- **证据**: report 自标 superseded；current docs 无 inbound route；只有
  `test_release_evidence_report.py` 逐字保护旧 verdict shape。
- **当前 owner**: superseded pre-acceptance snapshot和 implementation-shape test。
- **目标 owner**: dated live baseline保存 partial live evidence；release attestation保存 accepted run；
  regression descent保存 current defect policy。
- **Disposition**: `migrate then delete`。
- **迁移条件**: 逐项核对旧 report 的独特 provenance/failure fact；真正仍需导航的历史事实先进入正确
  dated owner，不复制旧 verdict全文。
- **删除条件**: current docs/spec/tests不引用旧 report；replacement records覆盖所需证据角色；删除 report
  和 shape-only test后 EVH evidence/coverage checks通过。
- **保留负向护栏**: 不改写 frozen attestation；不把 historical success当 current release result；不删除
  deterministic lower-seam evidence。
- **OpenSpec change slice**: `restore-delivery-and-subtract-dead-assets` 的 `evidence-report` workstream。

### TA-C06 - Preserve dated baseline and attestation as explicitly historical evidence

- **证据**: docs index/testing guide routes；baseline limitation assertions；attestation schema、hash、redaction
  与 source-run validation tests。
- **当前 owner**: respective frozen evidence epochs。
- **目标 owner**: 不变；current guide/workflow拥有 lane freshness，dated records只保存当时事实。
- **Disposition**: `historical`，保留。
- **迁移条件**: current wording cleanup只能增强 status/routing，不得改写 evidence payload或历史结果。
- **删除条件**: 不适用当前计划；需新的 retention/provenance policy明确批准且不丢失审计链。
- **保留负向护栏**: exact provenance、redaction、source hash和“不证明 current result”限制继续验证。
- **OpenSpec change slice**: 无；TA-C05 的 mandatory non-regression evidence。

### TA-C07 - Keep regression descent as current evidence policy

- **证据**: testing guide、`test_regression_descent.py`、deterministic selector collection和 live/provider-only
  rationale contract。
- **当前 owner**: test/evaluation governance。
- **目标 owner**: 不变。
- **Disposition**: `keep`。
- **迁移条件**: 无；only terminology changes随 owning test-evidence capability同步。
- **删除条件**: 不适用，除非有 replacement policy完整接管 live defect 下沉、不可 replay rationale和
  retained evidence mapping。
- **保留负向护栏**: live success不能替代 lower seam；不可 replay observation不能伪装 deterministic pass；
  selector retirement必须映射 displaced risks。
- **OpenSpec change slice**: 无 keep-only change。
