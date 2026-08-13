# 71 - Run, Bundle, Session And Observation Findings

> 审计类型: lifecycle authority / retained observation / capability ownership / anti-resurrection guards
> 审计基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 审计结论: 生产 topology 已完成 Bundle authority 迁移，current specs/registry 仍保留 session store、broker 和 binding recovery 的旧正向叙述

## 当前 authority spine

当前代码已经形成一条可验证的 authority chain：

```text
trusted conversation scope
  -> BundleLifecycle discovers/validates an available Run Bundle
  -> Bundle-local Research State owns lifecycle truth and legal mutation
  -> RunObservationStore records bounded Bundle-local Event Journal facts
  -> BundleWorkbench / LocalBundleWorkbench projects authorized controls and observations
```

`RunObservationStore` 的公开 callable surface 只有 `cleanup / inspect / publish / record_event`，
没有 bind、discover、reopen、resume、start 或 control。以下模块已经不存在，并由 tests 阻止复活：

- `deerflow_deep_research.domain.run_session`
- `deerflow_deep_research.runtime.run_session`
- `deerflow_deep_research.runtime.session_operations`
- `deerflow_deep_research.runtime.session_lifecycle_binding`

当前概念边界：

| Fact / surface | Current owner | 不拥有 |
| --- | --- | --- |
| Run existence、status、legal transition | Bundle directory + Bundle-local State / `BundleLifecycle` | Journal、manifest、binding、external checkpoint |
| retained execution observation | `domain/run_observation.py` + `runtime/run_observation.py` + `run-event-journal` | Run selection、resume、recovery |
| local discovery/control projection | Bundle lifecycle + `runtime/session_workbench.py` | 独立 session broker、provider reopen |
| operator surface name | `Local Session Workbench` | 通用产品 session domain |

`Local Session Workbench` 是 `deep_research_harness/CONTEXT.md` 明确定义的 operator surface 名，
不是机械 rename 对象。问题是把 Bundle discovery、artifact view、Journal 和已删除 binding 继续统称为
current session domain。

## Finding RS-01: `research-run-session` main spec 引用已删除实现

`openspec/specs/research-run-session/spec.md` 的前半已改写为 Run Bundle/Journal 语义，但后半仍把
`retained-session store`、`RunSessionView` 和 `ResearchSessionOperationBroker` 写成 current required
behavior。production 中对应 symbols/modules 不存在；实际 publisher/reader 是
`RunObservationStore`、`BundleRunObservationPublisher` 和 workbench projections。

更严重的是 registry 与 main spec 已经不是同一语义：

- `RUS-001` registry 仍声明 authoritative checkpoint binding，main spec/current code 明确禁止它；
- `RUS-002` registry 说 lifecycle trace，current owner 已是 Run Event Journal；
- `RUS-003` 到 `RUS-008` 大量语义与 RDO、RWB、REJ、DRH requirements 重叠。

证据：

- `openspec/specs/research-run-session/spec.md`
- `openspec/governance/req-registry.yaml` 中 `RUS-001` 至 `RUS-008`
- `deep_research_harness/src/deerflow_deep_research/domain/run_observation.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/run_observation.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/bundle_lifecycle.py`
- `deep_research_harness/tests/unit/test_run_session_store.py`
- `deep_research_harness/tests/unit/test_run_observation_store.py`
- `deep_research_harness/tests/assets/requirement_evidence.py`

Requirement disposition 应按语义而不是按 prefix 批量搬运：

| IDs | Current truth | Target disposition |
| --- | --- | --- |
| `RUS-001` | registry 的 checkpoint binding 语义已退役；main body 已被 DRH-001/003 取代 | `[DEPRECATED]`；不得拿同一 ID 重新定义 Bundle discovery |
| `RUS-002` | Journal 记录语义仍有效 | 唯一 clauses 合入 REJ owner；与 REJ 重复部分退役 |
| `RUS-003` | local Bundle inspection 仍有效 | 合入 RDO/RWB/REJ-004 owner |
| `RUS-004/005/006` | safe diagnosis、worker class、diagnostic publication 仍有效 | 合入 REJ 与 worker-failure owner；移除不存在的 store/broker symbols |
| `RUS-007/008` | observation 不得恢复 lost Bundle 仍有效 | 由 DRH-006 与 REJ-003/004 拥有，保留负向证据 |

若 requirement 的语义原样迁到新 capability，可以保留 ID 并更新 owner；若 current target 已由另一个
ID 完整覆盖或旧语义已死，原 ID 必须 `[DEPRECATED]`。不得静默重用 ID 表达新语义。

## Finding RS-02: `research-session-lifecycle-binding` 是退役机制的空壳 capability

该 spec 的 Purpose 仍说“bind a retained research session to its checkpoint scope”，registry 的
`RES-001/002/004` 仍把 durable binding、checkpoint reopen verifier 和 binding recovery 描述为
current positive capabilities；正文却几乎全部要求 binding 不得选择、控制或恢复 Run。

这不是保留一个兼容 reader 的证据。当前 production 没有 binding model、writer、reader、owner index、
broker 或 reopen verifier。测试证明的是它们不存在、Journal 没有控制 API、Bundle loss 后不能恢复。
因此负向 invariant 应迁到 Bundle/Journal/structure owner，不能让一个已删除机制继续拥有 current
capability name。

证据：

- `openspec/specs/research-session-lifecycle-binding/spec.md`
- `openspec/governance/req-registry.yaml` 中 `RES-001` 至 `RES-006`
- `deep_research_harness/tests/unit/test_session_lifecycle_binding.py`
- `deep_research_harness/tests/integration/test_session_lifecycle_binding.py`
- `deep_research_harness/tests/contract/test_session_operations_broker.py`
- `deep_research_harness/tests/integration/test_observation_lifecycle_separation.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/run_observation.py`

`RES-001` 至 `RES-006` 的旧 mechanism semantics 应标为 `[DEPRECATED]`；仍需长期保持的禁止恢复语义
应由 DRH-006、REJ-004 和 project-structure requirements 以自己的 ID 表达。

## Finding RS-03: 两个 capability 名仍把 Bundle contract 称为 session

`research-session-discovery-and-operations/spec.md` 的正文已经只接受 trusted scope、Bundle id、
Bundle-local State 和 lifecycle result；`research-session-artifact-view/spec.md` 也只描述 selected
Run Bundle 的 fixed contained metadata。它们没有独立 session fact、session identity 或 session
lifecycle。

这两个属于语义不变的 capability rename：

- `research-session-discovery-and-operations` -> `run-bundle-discovery-and-operations`
- `research-session-artifact-view` -> `run-bundle-artifact-view`

已有 `RDO-*`、`RSV-*` IDs 可保留，因为 requirement semantics 和 owner 不变；只需同步 capability
path/name、registry mapping、tests/docs references。历史 changes 不改写。

证据：

- `openspec/specs/research-session-discovery-and-operations/spec.md`
- `openspec/specs/research-session-artifact-view/spec.md`
- `deep_research_harness/src/deerflow_deep_research/runtime/session_workbench.py`
- `deep_research_harness/src/deerflow_deep_research/domain/session_workbench.py`
- `deep_research_harness/tests/integration/test_session_operations_lifecycle.py`
- `deep_research_harness/tests/unit/test_session_operation_resolver.py`

## Finding RS-04: Local Session Workbench 应保留，但 registry 仍宣传已删除 broker

`research-local-session-workbench/spec.md` 已要求 workbench 直接使用 Run Bundle lifecycle interface，
明确禁止 session broker；production 也使用 `LocalBundleWorkbench`/`BundleWorkbench`。但是 requirement
registry 的 `RWB-002/006/007` 仍写 authorized broker、through the broker、broker-projected controls。

因此 capability 和 operator name 保留，registry descriptions、test names/docstrings 中把 broker 当
current owner 的措辞必须同步。`WorkbenchSessionView` 等 workbench-local projection symbol 是否 rename
应按可读性在同一 change 决定，但不能据此删除 workbench 行为。

证据：

- `deep_research_harness/CONTEXT.md` 的 `Local Session Workbench`
- `openspec/specs/research-local-session-workbench/spec.md`
- `openspec/governance/req-registry.yaml` 中 `RWB-001` 至 `RWB-008`
- `deep_research_harness/src/deerflow_deep_research/runtime/session_workbench.py`
- `deep_research_harness/src/deerflow_deep_research/domain/session_workbench.py`
- `deep_research_harness/tests/integration/test_session_workbench.py`

## Finding RS-05: 负向 guards 有效，但 evidence ownership 已漂移

以下 tests 仍有独特价值：它们能检测旧 module/path 或 observation-as-authority 的复活，不应因
生产实现已删除而删除：

- `tests/unit/test_run_session_store.py`
- `tests/contract/test_session_operations_broker.py`
- `tests/unit/test_session_lifecycle_binding.py`
- `tests/integration/test_session_lifecycle_binding.py`
- `tests/integration/test_observation_lifecycle_separation.py`
- `tests/contract/test_session_operations_contract.py`

但它们当前用 `@impl RUS-*` / `@impl RES-*` 让退役 capability 看似拥有 active production evidence。
实施退役时应把 guards 迁到 DRH/REJ/PRS/RWB 等 current owner，并为 import/path guard 保留 planted
violation：临时创建同名 module 或向 Journal 增加 control method 必须使 guard 失败，恢复后通过。

## 最终审计 Candidate

### RS-C01 - Retire lifecycle-binding capability and its positive registry claims

- **证据**: `research-session-lifecycle-binding/spec.md`; registry `RES-001..006`;
  absence guards in `test_session_operations_broker.py`; Bundle-loss tests；current RunObservation API。
- **当前 owner**: 一个无 production implementation 的 `research-session-lifecycle-binding` capability；
  registry 仍声明 binding/reopen/recovery。
- **目标 owner**: Bundle loss/no-recovery 由 DRH-006；Journal non-authority 由 REJ-004；removed-module
  boundary 由 project structure/architecture guard。
- **Disposition**: `migrate then delete`。
- **迁移条件**: 将仍有效的 negative clauses 和 evidence claims 映射到 current IDs；为每个
  `RES-*` 判定旧语义已死并标 `[DEPRECATED]`；不得复用 ID。
- **删除条件**: main capability directory、registry capability mapping 和 current docs 不再声明
  lifecycle binding；所有 anti-recovery/import guards 在新 owner 下 collected；strict coverage 无 orphan。
- **保留负向护栏**: binding/index/checkpoint 不得 select/reopen/recover Bundle；Journal 不得增加
  lifecycle control API；foreign/deleted Bundle 仍 indistinguishable/unavailable。
- **OpenSpec change slice**: `retire-session-lifecycle-binding`。

### RS-C02 - Consolidate `research-run-session` into current Bundle/Journal owners

- **证据**: `research-run-session/spec.md`; registry `RUS-001..008`;
  `domain/runtime/run_observation.py`; `run-event-journal/spec.md`;
  `deep-research-harness-run-bundles/spec.md`; current evidence registry。
- **当前 owner**: `research-run-session` 混合 Bundle discovery、Journal、diagnostic store、已删除 broker
  和 no-recovery guards。
- **目标 owner**: DRH owns Bundle existence/control/loss；REJ owns retained events/diagnostics/health；
  RDO/RWB owns local authorized projection；worker failure capability owns worker classification semantics。
- **Disposition**: `migrate then delete`。
- **迁移条件**: 按 `RUS-001..008` 逐条做 semantic parity table；独有且语义不变的 requirement 可随
  owner 移动，重复或旧语义 ID 标 `[DEPRECATED]`；替换 `RunSessionView`、broker、retained-session
  store 等不存在的 symbol references。
- **删除条件**: unique behavior 全部有一个 current spec owner 和 collected evidence；RUS capability
  不再被 current registry/docs/tests 当 authority；no requirement ID 被重用。
- **保留负向护栏**: Bundle loss 后 Journal/diagnostic unavailable；inspection read-only；exact diagnostic
  reference publication、redaction、bounded retention、worker class 和 no external fallback 全部保留。
- **OpenSpec change slice**: `consolidate-run-observation-ownership`，在 RS-C01 后实施。

### RS-C03 - Rename Bundle capabilities without changing semantics

- **证据**: `research-session-discovery-and-operations/spec.md` (`RDO-*`);
  `research-session-artifact-view/spec.md` (`RSV-*`); Bundle lifecycle/workbench implementations and tests。
- **当前 owner**: capability path/name 使用 `research-session-*`，正文只拥有 Run Bundle semantics。
- **目标 owner**: `run-bundle-discovery-and-operations` 与 `run-bundle-artifact-view`。
- **Disposition**: `rename`。
- **迁移条件**: 确认 RDO/RSV requirement semantics 原样不变；枚举 registry、test annotations、docs 和
  structure references；历史 archive 不改。
- **删除条件**: current capability paths、registry mappings 和 current tests/docs 只有 Bundle 名；
  `session` residual 仅保留 Local Session Workbench 专名或 negative/historical context。
- **保留负向护栏**: trusted-scope selection、foreign indistinguishability、no raw path/provider、
  fixed catalog、no recursive discovery、artifact/observation cannot control Run。
- **OpenSpec change slice**: 与 `consolidate-run-observation-ownership` 同批，避免产生临时双 capability。

### RS-C04 - Keep Local Session Workbench and move its registry to the actual owner

- **证据**: product glossary；`research-local-session-workbench/spec.md`；registry `RWB-*`；
  `runtime/session_workbench.py`; workbench contract/integration tests。
- **当前 owner**: code/main spec 已直接依赖 Bundle lifecycle；registry 的 `RWB-002/006/007` 仍写 broker。
- **目标 owner**: Local Session Workbench 继续作为 fixed-profile operator surface；Bundle lifecycle
  result/State writer 拥有 control admission，workbench 只投影和委托。
- **Disposition**: `keep` capability and operator term; `rename` stale registry/test prose。
- **迁移条件**: 对齐 RWB registry descriptions 与 main spec；检查 workbench-local symbols，只有把
  generic session identity 当 domain fact 的才 rename。
- **删除条件**: 不适用 workbench capability 删除；旧 broker wording 的删除条件是 current registry、
  docs 和 tests 不再宣称 broker 存在。
- **保留负向护栏**: fixed trusted profile、no caller scope/path/provider、stale control rejection、
  pending-response/refinement separation、Bundle loss honesty、non-product boundary。
- **OpenSpec change slice**: 纳入 `consolidate-run-observation-ownership` 的 RWB registry sync。

### RS-C05 - Retain anti-resurrection tests under current evidence owners

- **证据**: six guard modules listed in Finding RS-05；current requirement-evidence registry。
- **当前 owner**: guards 被 `RUS/RES` annotations 和 evidence rows 归给退役 mechanism。
- **目标 owner**: DRH-006、REJ-004、PRS structural requirements 和 RWB no-broker requirement。
- **Disposition**: `retain guard`。
- **迁移条件**: 先给每个 guard 绑定 target ID 和 named violation；验证临时同名 module/control method
  会使 test 失败且恢复后通过。
- **删除条件**: guard 本身不随旧 implementation 删除；只有 target architecture rule 被后续明确
  取消且有新 recovery/authority decision 时才可单独评审。
- **保留负向护栏**: 上述 guard 本身即必须保留的负向证据；exception baseline 只减不增。
- **OpenSpec change slice**: RS-C01/RS-C02 的 mandatory evidence-migration task，不另建 guard-only change。
