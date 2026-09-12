## Why

`research-graph-lifecycle` 的 REG-008 要求：任何超出 hard checkpoint-size bound 的 state
update 都必须以类型化失败被拒绝，且 checkpoint 不得被修改。但今天这条义务在 live 路径上
**没有执行者**：`serialize_research_state`/`validate_research_state` 仅被离线迁移脚本
(`scripts/retained_run_data_migration.py`) 与单元测试调用；`_validate_current_graph_checkpoint`
只校验 `schema_version` 与 `repair_counts`；LangGraph 的 `AsyncSqliteSaver` 直接把
`channel_values` 落进 SQLite，项目 serde 只做类型白名单、不做大小限制。原始设计曾明确把
whole-state bound 选为"逐字段上限无法阻止 reducer 累积越过安全线"的 backstop
(`2026-07-12-.../design.md:165`)，该 backstop 目前未接线。校准测量（85 个 retained store）：
最大整态 7,905 B、最大单次 node update 1,593 B、最大单 channel 字段 1,622 B，相对 65,536 B
的 bound 有 8–40 倍余量，说明强制不会误伤观测到的合法 run。

## What Changes

- **写侧强制（主强制点）**：把项目 checkpoint serde 变为有界 serde，在 `dumps_typed` 中
  对整个 checkpoint 的 `channel_values` 做聚合 bound 校验、对单条 write 的 value 做更新级
  校验；越界在字节写入 SQLite 之前抛类型化错误，保证"checkpoint is not mutated"。
- **节点级可归因早拒绝**：graph node wrapper 在节点 update 被提交前按同一阈值与同一
  canonical serializer 校验，使 REG-008 的"a node returns a state update"场景带
  phase/attempt 归因地失败。
- **准入同源**：读侧 `_validate_current_graph_checkpoint`（编译前）、写侧（落盘前）与离线
  迁移路径复用同一个 `validate_checkpoint_values` / canonical serializer，schema、legacy
  字段与大小只有一处定义。
- **失败语义（类型化终态）**：越界 → 终态 `BLOCKED` + `RunFailureCode.CHECKPOINT_INCONSISTENT`
  + 新增 `TerminalReason.INTERNAL_BLOCKED`（不谎报为 `GATE_BLOCKED`）+ `FailureCertainty.DIRECT`；
  不 repair、不自动重启；incident 有界，`status`/投影诚实呈现。
- **子上限关系**：明确 `MAX_WORK_UNIT_BLOCK_BYTES`(40,960) 严格小于聚合
  `MAX_CHECKPOINT_STATE_BYTES`(65,536)，且聚合 bound 是唯一裁决者——每个子块都在各自上限内
  也不豁免聚合越界。
- **校准证据**：记录 retained store 的 state 尺寸分布，证明阈值与余量。

## Capabilities

### New Capabilities

（无。）

### Modified Capabilities

- `research-graph-lifecycle`: REG-008 的 hard checkpoint-size bound 从"测试/离线迁移级"升为
  **live 运行时强制**；新增越界时的类型化终态与 incident 语义（相邻 REG-004/REG-013 的
  blocked/incident 投影需保持自洽）。

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/state.py`（bound、canonical
  serializer、类型化越界错误）
- `deep_research_harness/src/deerflow_deep_research/runtime/checkpoint.py`（有界 serde）
- `deep_research_harness/src/deerflow_deep_research/runtime/bundle_lifecycle.py`
  （写/读准入统一）
- `deep_research_harness/src/deerflow_deep_research/graph/builder.py`（node-wrapper 早拒绝）
- `deep_research_harness/src/deerflow_deep_research/runtime/bundle_graph.py`（异常 → 终态）
- `deep_research_harness/src/deerflow_deep_research/domain/lifecycle.py`（新增
  `TerminalReason.INTERNAL_BLOCKED`）、`runtime/run_experience.py`
  （`_failure_code_for_control` 与终态文案/投影映射）
- 测试：新增确定性集成测试（真实 SQLite：越界更新 → 类型化失败 + checkpoint 字节前后不变）、
  读侧准入测试、bound 嵌套断言、校准证据；调整受影响的状态契约测试
- `deerflow/` 不修改，也不 source-browse。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/`
  —— checkpoint 持久化边界是越界的强制点；`domain/state.py` 是 bound 与 canonical serializer
  的相邻契约 owner，`graph/builder.py` 是可归因的节点级准入点。
- **Seam classification:** deterministic-guardrail —— 纯确定性持久化/准入边界与阈值，不触碰
  任何 LLM 角色、prompt、候选语义或 wire 格式。
- **Question:** 能否让 REG-008 的 hard checkpoint bound 在 live 写入路径上真正执行、以诚实的
  类型化终态呈现，且不误伤观测到的合法 run？
- **Necessary adjacent/external contracts:** `research-graph-lifecycle`（REG-008 的 bound 与
  REG-004/REG-013 的 blocked 终态/incident 投影如何自洽）；`work-unit-kernel`
  （`MAX_WORK_UNIT_BLOCK_BYTES` 子上限如何与聚合 bound 嵌套）；`gate-kernel`（blocked 终态由
  gate 还是通用持久化边界写入，谁是直接事实 owner）。
- **Evidence seam:** 新增确定性集成测试：经真实 SQLite saver 驱动，越界 node update →
  类型化失败、SQLite 字节前后不变（复用 retained-checkpoint cutover 的字节比对范式）；读侧
  准入测试；bound 关系断言（子块 < 聚合，且子块合规不豁免聚合越界）；校准统计。
  `UV_OFFLINE=1 make verify` 全绿。
- **Not in scope:** 巨型文件拆分；在无新校准证据下更改 bound 数值；删除 `ResearchGraphState`
  （离线迁移仍依赖它）；任何 `deerflow/` 修改或框架源码浏览。
- **Triggered review policies:** change-admission, authority-and-projections, control-and-recovery, participant-outcomes, control-placement, workflow-outcome-review

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| A node update / checkpoint may cross into persisted graph state | Node/model proposes the candidate update contents | `domain/state.py` canonical serializer + bound; `runtime/checkpoint.py` serde and `graph/builder.py` node wrapper admit | non-bypassable | Checkpoint is never mutated by an over-bound state; run ends BLOCKED with `CHECKPOINT_INCONSISTENT` | Reuses existing `serialize_research_state`/`validate_research_state` as the single canonical serializer instead of adding a parallel size check | Oversized-update integration test with before/after SQLite byte comparison |
| Which terminal cause a bound breach carries | None (no human judgment) | `domain/lifecycle.py` `TerminalReason.INTERNAL_BLOCKED` + `RunFailureCode.CHECKPOINT_INCONSISTENT` | non-bypassable | Blocked terminal is honest; not mislabeled as a gate decision | Reuses existing BLOCKED/incident projection path instead of a new outcome channel | Typed terminal + status projection assertion |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| State update / checkpoint exceeds the hard size bound | `domain/state.py` bound + canonical serializer; `runtime/` admits at the write boundary | None — deterministic internal invariant breach; no repair or retry | `BLOCKED`, `RunFailureCode.CHECKPOINT_INCONSISTENT`, `TerminalReason.INTERNAL_BLOCKED`, `FailureCertainty.DIRECT` | Do not continue the run; start a fresh run and provide the diagnostic reference | Integration test: typed failure, checkpoint bytes unchanged, honest status projection |
