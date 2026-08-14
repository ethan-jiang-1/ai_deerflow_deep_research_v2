# 76 - Evaluation Boundary Findings

> 取证基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 范围: cognitive evaluation domain/runtime、`evals/` controls、live report/evidence helpers与术语边界
> 排除: 不运行 credentialed live evaluation；本地 `evals/runs` 无 retained files，不代表外部 archive为空

## Canonical evaluation distinctions

| Concept | Authority/lifecycle | Must not be called |
| --- | --- | --- |
| Evaluation Execution Case | versioned finite execution declaration | arbitrary prompt/script |
| Evaluation Run Workspace | one invocation's mutable isolated work directory | host workspace / Run Bundle |
| Evaluation Run Bundle | immutable execution evidence | Deep Research Run Bundle / verdict |
| Review Record | separate immutable assessment referencing a Bundle | Bundle mutation / execution status |
| Node Evaluation Run | one node + explicit production branch | copied model call / whole graph |
| Flow Evaluation Run | bounded graph flow integration lane | node diagnosis substitute |
| Evidence Layer | authenticity/claim boundary of captured evidence | execution status / quality result |

这些名称相近但不是 aliases。合并 Workspace、Bundle、Review Record 或 product Run Bundle 会破坏 writer、
immutability和decision authority。当前 cleanup目标是删除重复 compatibility surfaces，同时保留这些区分。

## Finding EV-01: Evaluation domain objects 的 ownership 已经清楚，应保留

`domain/evaluation.py` 拥有 immutable contracts；runtime runner创建 workspace/bundle，review service只读
Bundle并另写 Review Record。Runner status只有 completed/failed，Review Result才有
pass/limited/inconclusive/failed。main specs、ADRs、docs和 tests共同保护“不自动 review、不修改 Bundle、
不把 deterministic handoff冒充 cognitive quality”。

因此“Evaluation Run/Bundle/Workspace/Review”不是一个术语多说法。需要清理的是 glossary尾部复制的设计
论证归属（NC-C03），不是删掉这些 canonical distinctions。

## Finding EV-02: Missing `evidence_layer` default 是 persisted compatibility reader

`EvaluationBundleManifest` 与 `ReviewRecord` 的 `evidence_layer` 默认
`deterministic_handoff`；current runner明确写 layer，review从 verified manifest派生，tests则删掉 manifest
字段来验证 old bundle仍按 deterministic handoff读取。这个 default防止旧 record被提升为 live-quality，
语义是保守兼容，不是普通 default。

本地 `evals/runs` 没有文件，无法关闭私有/外部 retained Evaluation Bundles。删除 default前必须有 archive
inventory或 retention cutover；未知/缺失 layer绝不能推断 credentialed live。

## Finding EV-03: Runtime evaluation `contracts.py` 是兼容 re-export 层

`runtime/evaluation/contracts.py` 只从 `domain.evaluation` re-export；runtime package `__init__` 再从该层
导出。current production modules可直接依赖 domain owner，仓库内外部-style imports主要通过
`runtime.evaluation` facade，focused tests也使用该 facade。该层没有行为，但 package facade可能是 operator/
test integration surface。

目标应是一个明确 public import route，而不是 domain和runtime contracts两个同等 authority。先枚举当前
imports并选择 facade或domain作为 supported route，再删除中间 module；不能让删除造成循环 import或把
runtime assembly变成 contract owner。

## Finding EV-04: `compute_metrics()` 是零行为、零 consumer 的 legacy shim

`tests/eval/metrics.py::compute_metrics()` 对任何 dict都返回空 dict，docstring还引用早已完成的 task 5.5；
repository-wide scan无 caller，只有自身 `__all__` export。current live metrics使用 typed metric functions和
`ValidatedEvaluationOutcome`。该 shim既不保存行为也不能充当 old report reader，属于 test support residue。

## Finding EV-05: Live report legacy classifier 是 current boundary guard，不是 reader

`classify_live_report()` 将同时缺少 `report_schema_version` 和 `metrics_schema` 的 payload分类为 LEGACY；
archive scanner随后只接受 EVIDENCE_V1，并明确拒绝 legacy/unknown schema。它不会执行或迁移 legacy report，
而是给 dated baseline和旧 archive一个可解释 classification，再在 current archive admission fail closed。

`live-evaluation-baseline-2026-07-17.md` 正被 current docs标成 legacy report schema。只要该历史证据仍被导航，
classifier有明确 consumer和 negative path。未来若 retention policy删除所有 legacy evidence，可重新审计，
但当前不能因命中 legacy就删。

## Finding EV-06: `parse_profile_response()` 污染 live-evaluation tests，但不属于 evaluation contract

`test_live_evaluation.py` 为解析固定 profile文本而临时 import profile compatibility wrapper。这使 evaluation
test成为旧 parser API consumer，却没有 evaluation-specific语义。迁到 `parse_profile_input()` 后应随 PC-C02
删除 wrapper，不在 evaluation runtime新增 adapter。

## 最终审计 Candidate

### EV-C01 - Keep the Evaluation Workspace/Bundle/Review/Run distinctions

- **证据**: domain contracts、runner/review writers、CONTEXT definitions、ADRs、cognitive-evaluation specs/tests。
- **当前 owner**: evaluation domain分别拥有 case、workspace、bundle、review和 node/flow run lifecycle。
- **目标 owner**: 不变；glossary只保留定义，设计论证迁回 ADR/spec owner。
- **Disposition**: `keep`。
- **迁移条件**: NC-C03处理 glossary-only ownership时不得合并这些概念。
- **删除条件**: 不适用；任何合并需先替代 isolation、immutability、review separation与 run granularity。
- **保留负向护栏**: Evaluation Bundle不是 product Run Bundle；Runner不产质量 verdict；Review不改 execution。
- **OpenSpec change slice**: 无 keep-only change；作为 `restore-product-glossary-ownership` 的 non-regression。

### EV-C02 - Retain missing-layer compatibility until Evaluation Bundle data closes

- **证据**: model default、explicit current writers、review-derived layer、old-manifest test；external archive未知。
- **当前 owner**: Evaluation Bundle persisted manifest compatibility。
- **目标 owner**: explicit `EvidenceLayer` on every current manifest/review；missing old input只保守解释为 deterministic。
- **Disposition**: `migrate then retire` reader。
- **迁移条件**: inventory retained bundles/reviews；backfill explicit layer或批准 retention expiry；验证 hashes不变。
- **删除条件**: supported records无 missing layer；writers/tests/specs都要求 explicit field。
- **保留负向护栏**: missing/unknown永不提升为 credentialed live；review layer必须由 verified manifest派生。
- **OpenSpec change slice**: `close-evaluation-evidence-layer-compatibility`。

### EV-C03 - Converge evaluation contract imports onto one supported route

- **证据**: runtime `contracts.py` pure re-export；domain owns models；runtime facade/tests consume exports。
- **当前 owner**: domain facts + runtime compatibility projection。
- **目标 owner**: domain remains fact authority；Evaluation Owner指定一个 supported import facade。
- **Disposition**: `migrate then delete` intermediate re-export module。
- **迁移条件**: enumerate internal/package consumers；choose supported import route；avoid circular dependency。
- **删除条件**: no imports of runtime contracts module；facade/export tests and evaluation lanes pass。
- **保留负向护栏**: runtime不得复制 contract definitions；public import failure必须明确而非 silent duplicate type。
- **OpenSpec change slice**: `converge-evaluation-contract-exports`。

### EV-C04 - Delete the unused `compute_metrics()` shim

- **证据**: zero callers；always-empty result；stale task docstring；typed metric functions are current。
- **当前 owner**: 无 behavior owner；test helper export residue。
- **目标 owner**: individual typed metric functions + `ValidatedEvaluationOutcome`。
- **Disposition**: `delete`。
- **迁移条件**: 无 caller migration；确认 no dynamic string import in test registry。
- **删除条件**: function和 `__all__` entry同批删除；metric/live tests与 asset checker通过。
- **保留负向护栏**: insufficient authority remains typed non-pass；hard invariants still fail independently of metrics。
- **OpenSpec change slice**: `subtract-evaluation-test-compatibility`。

### EV-C05 - Retain live-report classification and fail-closed archive admission

- **证据**: dated legacy baseline route；classifier tests；archive scanner rejects non-EVIDENCE_V1 records。
- **当前 owner**: live evaluation evidence intake/retention boundary。
- **目标 owner**: 不变。
- **Disposition**: `retain guard`。
- **迁移条件**: 无；historical routing cleanup须保留 explicit classification。
- **删除条件**: only after retention owner proves no supported legacy evidence and replacement guard rejects malformed/unknown
  archive records with equal sensitivity。
- **保留负向护栏**: partial version markers fail invalid；legacy never enters current archive；sensitive/oversize input rejected。
- **OpenSpec change slice**: 无 keep-only change；TA-C06 的 non-regression。

### EV-C06 - Remove evaluation's dependency on the profile parser wrapper

- **证据**: one live-evaluation test import；no evaluation runtime consumer；PC-C02 identifies canonical parser。
- **当前 owner**: test convenience dependency。
- **目标 owner**: `parse_profile_input()` in profile domain。
- **Disposition**: `delete dependency`。
- **迁移条件**: test asserts through `ProfileParseResult.partial` without changing fixed-profile semantics。
- **删除条件**: evaluation tests no longer import wrapper；PC-C02 can close export。
- **保留负向护栏**: fixed live profile still parses deterministic time budget and no credential/provider behavior changes。
- **OpenSpec change slice**: part of `converge-profile-compatibility-readers`，not an evaluation mega-change。
