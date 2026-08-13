# 72 - Fixture And Implementation Mode Findings

> 审计类型: fixture boundary / persisted mode / demo execution path / false-success prevention
> 审计基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 审计结论: fixture graph 是 current deterministic asset；无 graph 的 full-fake path 同时绕过 graph 且写入错误的 `all_real` provenance

## 当前必须区分的概念

| Concept | Current representation | 结论 |
| --- | --- | --- |
| deterministic graph composition | `src_fake` fixture package + fixture recipe + `BundleGraphExecutor` | current、必须保留 |
| explicit test composition | `fixture / mixed / all_real` recipe implementation map | current、必须保留 |
| no-graph lifecycle presentation | `DemoLifecycleTransport.bind_full_fake()` + `BundleControl` fallback | current operator command，但契约自相矛盾 |
| persisted execution provenance | `BundleLocalState.implementation_mode` | public/persisted observation，必须诚实 |
| old serialized enum value | `ImplementationMode.FULL_FAKE` / `"full_fake"` | 没有 current writer；兼容删除需数据/support 决策 |

`mixed` implementation mode 不是 Wave0 worker diagnosis 的 `mixed`，两者不能合并或一起删除。

## Finding FM-01: `src_fake` 和 fixture graph 不是迁移残留

fixture source 使用不同 package `deerflow_deep_research_fixtures`，production wheel 排除它；fixture
entry 只在 child process 通过 `PYTHONPATH=src_fake` 启用。fixture recipe 经
`BundleGraphExecutor` 执行完整 topology，并把 `implementation_mode=fixture` 写入 State，tests 验证
start、status、State reload 和 reprojection 都保持该值。

它提供的是 deterministic graph-composition evidence，不是 production fallback。删除它会丢失
current graph、fan-in、HITL、Bundle/State integration 的零凭据证明，不能被无 graph 的 full-fake
lifecycle presentation 替代。

证据：

- `deep_research_harness/src_fake/deerflow_deep_research_fixtures/`
- `deep_research_harness/scripts/demo_fixture_graph.py`
- `deep_research_harness/scripts/_demo_core.py::build_fixture_demo_recipe`
- `deep_research_harness/scripts/_demo_core.py::build_demo_runtime`
- `deep_research_harness/tests/integration/test_demo_fixture_graph.py`
- `deep_research_harness/tests/contract/test_demo_commands.py`
- `openspec/specs/fixture-source-isolation/spec.md`
- `openspec/specs/demo-pipeline/spec.md`

## Finding FM-02: 当前 full-fake command 持久化为 `all_real`

`make demo`、`make demo-scripted` 和 `make demo-tui-fake` 使用
`DemoLifecycleTransport.bind_full_fake(adapter=...)`，不创建 `DemoRuntime` 或
`BundleGraphExecutor`。`BundleControl._start()` 在没有 graph executor 时传入
`ImplementationMode.ALL_REAL`；随后 `_resume()` 的 no-graph branch 直接把 active lifecycle 标成
completed，并明确说明它不生产 findings/report。

因此 command/documentation 称它为 full-fake，State 却声称 `all_real`。这破坏 persisted execution
provenance，也可能让 inspection/evidence consumer 把一个只走 start/input/completed 的记录当成真实
研究运行。现有 CLI/TUI tests 验证可见流程和“fixture is not completed research”提示，却没有断言
该 Bundle 的 persisted `implementation_mode`，所以测试绿色没有发现矛盾。

证据：

- `deep_research_harness/scripts/_demo_core.py::DemoLifecycleTransport.bind_full_fake`
- `deep_research_harness/scripts/demo.py`
- `deep_research_harness/scripts/demo_tui.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/bundle_control.py` 的 `_start` 与 `_resume`
- `deep_research_harness/tests/integration/test_demo_cli.py`
- `deep_research_harness/tests/integration/test_demo_tui.py`
- `deep_research_harness/README.md`
- `deep_research_harness/docs/local-operations.md`

## Finding FM-03: `FULL_FAKE` enum 不是当前 path 的诚实 writer

`ImplementationMode` 仍接受 persisted `full_fake`，但 current production/fixture recipe 只产生
`all_real`、`fixture` 或 explicit `mixed`；no-graph fallback 也错误地产生 `all_real`。本地忽略数据
的有限 schema scan 发现 326 个 `state.json`：263 个 `all_real`、3 个 `fixture`、60 个缺少该字段、
0 个 `full_fake`。这个本地样本证明当前机器没有该旧值，不能证明外部部署不存在 consumer/data。

所以有两个不同问题：

1. no-graph path 的错误 writer 必须先修正或退休；
2. persisted `full_fake` reader/value 只有在外部支持边界与 retained data inventory 关闭后才能删。

把 `bind_full_fake` rename 成 fixture 不会修复问题，因为它没有 graph、没有 fixture recipe，也不产生
fixture graph behavior。反过来，仅让它写 `FULL_FAKE` 会诚实化 provenance，但会永久保留第二条
无 graph lifecycle execution mechanism。

## Finding FM-04: Main specs 仍把 fallback 当成长期共存机制

`demo-pipeline`、`research-demo-tui`、`runtime-integration` 和
`research-graph-lifecycle` 都把 full-fake/fallback 写成 current required behavior。部分
`research-graph-lifecycle` 文字还用 full-fake 指 deterministic fake graph，进一步混淆 no-graph
presentation 与 fixture graph。

目标必须由产品 owner 二选一：

- **推荐终态**: 零凭据 proof 统一经 fixture graph；presentation-only behavior 由共享 `RunUpdate`
  fixtures 测试；删除 no-graph lifecycle fallback 和 full-fake command/profile。
- **保留终态**: 明确定义一个 no-graph lifecycle simulator，给它诚实的 persisted contract、独立
  名称、不能冒充 research completion 的 terminal/result semantics，并接受新增长期机制的成本。

当前证据无法替产品选择演示体验，因此删除 command 前是 product decision；但“继续现状”不是合法
选项，因为 `all_real` provenance 已经错误。

## Finding FM-05: `mixed` 是 current test composition，不是 residual public mode

explicit mixed recipes 仍用于逐 node 真实/fixture 组合与 failure evidence；specs 和 tests 要求它只由
explicit composition 产生，production public tool 固定 all-real。它应保留，前提是继续阻止 public
mode selector、implicit fallback 和 production fixture package import。

证据：

- `deep_research_harness/src/deerflow_deep_research/graph/implementation_map.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/research.py`
- `deep_research_harness/tests/graph/test_topology_and_implementation.py`
- `openspec/specs/fixture-source-isolation/spec.md`
- node owning specs 中 explicit mixed composition requirements

## 最终审计 Candidate

### FM-C01 - Resolve and retire the no-graph full-fake lifecycle path

- **证据**: `DemoLifecycleTransport.bind_full_fake`; `BundleControl._start/_resume`;
  `scripts/demo.py`; fake branch of `scripts/demo_tui.py`; README/Make targets and tests。
- **当前 owner**: demo transport 通过缺少 graph executor 触发 runtime fallback；State 被写成 `all_real`。
- **目标 owner**: 推荐由 fixture `ResearchGraphRecipe` + `BundleGraphExecutor` 拥有零凭据 graph proof；
  CLI/TUI presentation 继续只消费 shared `RunUpdate`。
- **Disposition**: `product decision`，推荐批准后 `migrate then delete`。
- **迁移条件**: 产品 owner 明确零凭据 command 是否必须保留“只走一次输入就完成”的体验；若不必，
  将 commands/fixtures/tests 迁到 fixture graph；若必须，需先设计诚实 simulator contract，不能沿用
  `all_real` 或 research-completed 语义。
- **删除条件**: 所有 supported commands 都绑定 explicit graph runtime；`BundleControl` 不再靠
  missing executor 提供 execution；README/Make/spec/tests 不再路由 full-fake；旧 command 有明确
  replacement/notice，且 retained Bundle inspection 不会误认 provenance。
- **保留负向护栏**: graph-backed real/fixture route 缺 executor 必须 fail；real route 不得 fallback；
  presentation fault 不得显示 fake completion；fixture package 不得进入 production wheel。
- **OpenSpec change slice**: `resolve-full-fake-demo-contract`，proposal 必须先记录产品选择。

### FM-C02 - Retire persisted `full_fake` mode only after support closure

- **证据**: `domain/lifecycle.py::ImplementationMode`; State reader/writer；本地 326-state mode scan；
  current recipe factories and graph tests。
- **当前 owner**: closed persisted enum reader 接受 `full_fake`，但 current writer 不产生该值。
- **目标 owner**: closed current provenance `fixture / mixed / all_real`；或产品批准的诚实 simulator
  mode（仅在 FM-C01 选择保留时）。
- **Disposition**: `product decision`，推荐在 FM-C01 选择退休后 `migrate then delete`。
- **迁移条件**: 枚举支持范围内 retained data/consumers；决定 old value 是 one-time migrate、read-only
  map 还是明确 unsupported；定义失败和 rollback behavior。
- **删除条件**: support inventory 中无 `full_fake`，或所有记录已迁移/明确拒绝；所有 readers、schemas、
  tests、specs 和 docs 删除该值；旧输入行为有测试。
- **保留负向护栏**: unknown mode fail closed；production remains fixed all-real；fixture/mixed only from
  explicit recipes；provenance cannot default into a stronger authenticity claim。
- **OpenSpec change slice**: `retire-full-fake-implementation-mode`，依赖 FM-C01 和 product/data decision。

### FM-C03 - Keep fixture source and explicit mixed composition

- **证据**: `src_fake`; fixture recipe; fixture graph integration tests; wheel isolation and explicit mixed tests。
- **当前 owner**: fixture package/recipe 与 explicit implementation map。
- **目标 owner**: 不变；只统一把它称为 fixture composition，避免 full-fake alias。
- **Disposition**: `keep`。
- **迁移条件**: 无行为迁移；术语 change 时枚举 docs/spec/tests 中把 fake graph 称作 full-fake 的命中。
- **删除条件**: 不适用。只有出现同等真实性且覆盖相同 graph/Bundle contracts 的 replacement change
  才能重新审计。
- **保留负向护栏**: production wheel/source isolation、child-only `src_fake`、no mode selector、exact
  topology、persisted fixture/mixed provenance。
- **OpenSpec change slice**: FM-C01 中只做 terminology/spec sync；不创建 fixture deletion change。

### FM-C04 - Preserve missing-mode compatibility until retained states are migrated

- **证据**: `BundleLocalState.from_dict` 对缺失 `implementation_mode` 默认 `all_real`；本地 60 个
  schema-v3 states 缺该字段。
- **当前 owner**: Bundle State reader 的 optional-field compatibility。
- **目标 owner**: 所有 supported retained State 显式携带诚实 mode，reader 最终可要求字段存在。
- **Disposition**: `migrate then delete`。
- **迁移条件**: 见 `75-persisted-compatibility-findings.md` 的 persisted-data gate；不得把缺失值和
  explicit `full_fake` 当同一种迁移。
- **删除条件**: supported retained states 已原子迁移或明确不支持；crash/rollback/old-reader behavior
  已定义；missing-field negative test 取代静默 default test。
- **保留负向护栏**: schema mismatch/unknown enum fail closed；迁移不能把未知 provenance 提升为
  all-real evidence。
- **OpenSpec change slice**: `close-bundle-state-mode-compatibility`。
