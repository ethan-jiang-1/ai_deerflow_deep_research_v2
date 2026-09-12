## Why

coding-agent 友善度审查发现 `deep_research_harness/docs/` 的顶层把**活文档**与**冻结的
point-in-time 证据**混在一起，且 `docs/README.md` 索引漏掉了被 13 处引用的
`run-lifecycle-walkthrough.md`。混放的长期风险是真实的：未来读者或 agent 可能「顺手更新」
带日期的历史证据去对齐新跑批，从而**悄然篡改历史证明**。目录边界是编码「生命周期/权威」
的最便宜、对 agent 最强的持久信号；这也是本仓已有 `adr/`、`runbooks/` 子目录的同一原则。

## What Changes

- 新建 `docs/evidence/`，把两份**冻结证据**移入：
  `live-evaluation-baseline-2026-07-17.md`、`release-attestation-2026-07-17.json`。
- **不**移动 `regression-descent.md`：它是**活**的策略 + 持续增长的发现台账
  （含 "Current … Awaiting Closure"），混入冻结区会错误抑制必要更新。
- 重写 `docs/README.md` 为三块：**Living References** / **Generated** / **Frozen
  Evidence**，并补上此前缺失的 `run-lifecycle-walkthrough.md`。
- `check_doc_hygiene.py` 的 `DOC_LAYER_DOCS` 同步新路径（并说明 evidence/ 中的
  release-attestation 为非 markdown、不在 checker 范围）。
- 同步引用：`docs/testing-and-evaluation.md` 的 attestation 链接；三个 contract 测试的
  证据路径常量（`test_release_attestation.py`、`test_release_evidence_provenance.py`；
  `test_regression_descent.py` 不变）。
- `docs/adr/README.md` 0005 索引句去掉 TUI 机制残留（决策 current，机制已 dormant），
  与 ADR-0002 的 status postscript 口径一致。
- 无运行时/spec 行为变化；docs-layer 范围本就由 `check_doc_hygiene.py` 的显式枚举承载，
  PRS-020 的「under `docs/`」定义已覆盖子目录。

## Capabilities

### New Capabilities

（无——纯文档层重组 + 治理枚举同步。）

### Modified Capabilities

（无。`.openspec.yaml` 声明 `skip_specs: true`。可观察行为、运行时契约与 PRS-020
requirement 语义均不变；只有 docs 文件路径与 checker 的注册枚举变化。）

## Impact

- `deep_research_harness/docs/evidence/`（新目录，2 个冻结件）
- `deep_research_harness/docs/README.md`（三块索引 + 补 run-lifecycle-walkthrough）
- `deep_research_harness/docs/testing-and-evaluation.md`（attestation 链接）
- `deep_research_harness/docs/adr/README.md`（0005 索引句）
- `openspec/governance/check_doc_hygiene.py`（`DOC_LAYER_DOCS` + 自测路径 + docstring）
- `deep_research_harness/tests/contract/{test_release_attestation,test_release_evidence_provenance}.py`
- 无 `src/`、无运行时、无 `deerflow/` 改动。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/docs/` 的文档层组织，由
  `openspec/governance/check_doc_hygiene.py` 的注册枚举（PRS-020）背书。
- **Seam classification:** wiring —— 仅文档目录/索引重组与治理枚举同步，无认知面、无人工
  决策面、无运行时行为变化。
- **Question:** 能否按「生命周期」而非「主题」重排 docs 顶层，让冻结证据与活文档在路径
  上分离、索引完整，同时保持 `check_doc_hygiene.py` 绿、所有相对链接与证据路由解析？
- **Necessary adjacent/external contracts:** `openspec/governance/check_doc_hygiene.py`
  （docs-layer 范围与链接校验的唯一执法者，本次同步）；三个 contract 测试
  （冻结证据的可发现性/来源路由）；`required-paths.toml` PRS-020 只注册 checker 本身，
  无需变更。
- **Evidence seam:** `check_doc_hygiene.py --self-test` 与 `check_doc_hygiene.py` exit 0；
  `tests/contract/{test_release_attestation,test_release_evidence_provenance,test_regression_descent,test_topology_snapshot}.py` 通过。
- **Not in scope:** 删除或改写任何历史证据正文；按 architecture/operations/evaluation 再
  切主题子目录（过度组织）；移动 `regression-descent.md`（活文档）；`deep-research-topology.md`
  的单文件 `generated/` 目录（仅索引标注）；任何 `src/` 或 runtime 行为；
  为拓扑单开目录；`deerflow/`。
- **Triggered review policies:** none: 纯文档层重组与治理枚举同步，无新运行时路径、无认知面、无 workflow outcome、无 node-agent 面。
