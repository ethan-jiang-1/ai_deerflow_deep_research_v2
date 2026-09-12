## Context

见 `proposal.md` − Why。设计需要以下当前事实（均已核实）：

- live 写入路径：`bundle_graph` 经 `BundleLifecycle.open_graph_checkpoint`
  (`runtime/bundle_lifecycle.py:485`) 取得 SQLite saver，`AsyncSqliteSaver.aput` 把**整个
  checkpoint** 交给 `self.serde.dumps_typed(...)`，`aput_writes` 对**每条** write value 调用
  `dumps_typed`。项目 serde 由 `runtime/checkpoint.py:build_deep_research_checkpoint_serde()`
  提供，是唯一注入点。
- 读侧准入口：`_validate_current_graph_checkpoint` (`bundle_lifecycle.py:963`) 在编译图之前
  读最新 checkpoint，只校验 `schema_version` 与 `repair_counts`，不校验大小。
- 离线路径：`scripts/retained_run_data_migration.py:247` 调 `validate_research_state` 校验
  迁移产物。
- live channel state 是**部分态**（`bundle_graph._initial_graph_state` 注释明说
  "deliberately partial"），所以不能用要求必填字段的 `ResearchGraphState` 去校验 live 值。
- 同一 serde 也服务通用 host / `infra_probe`（`graph_host.py:95,204`），其 state 形状不同且极小。
- 校准：85 个 retained store 最大整态 7,905 B、最大单 write 1,593 B、最大单字段 1,622 B；
  `MAX_CHECKPOINT_STATE_BYTES=65,536`、`MAX_WORK_UNIT_BLOCK_BYTES=40,960`。
- 终态模式：节点/ gate 通过 state update 写 `terminal_status`/`terminal_reason`/`latest_incident`
  （如 `engine/gate_kernel.py:307`、`topic_planning/node.py:91`）；`RunFailureCode.CHECKPOINT_INCONSISTENT`
  已存在，其文案为"不要继续当前运行；请提供诊断引用"且不可恢复，语义精确匹配。

## Goals / Non-Goals

**Goals:**

- 让 REG-008 的 hard bound 在 live 写入路径上不可绕过地执行，且越界时 checkpoint 不被修改。
- 越界以诚实的类型化终态呈现，与既有 blocked/incident 投影自洽。
- 写、读、离线迁移三处共享同一个 bound 与 canonical serializer。
- 让 `MAX_WORK_UNIT_BLOCK_BYTES` 与 `MAX_CHECKPOINT_STATE_BYTES` 的嵌套关系成为可测不变量。

**Non-Goals:**

- 不改变 bound 数值（除非新校准证据）。
- 不拆分巨型文件、不删除 `ResearchGraphState`（离线迁移仍依赖）。
- 不引入 retry/repair/自动重启。
- 不修改也不 source-browse `deerflow/`。

## Decisions

**1. 主强制点：有界 serde 的 `dumps_typed`，度量实际落盘字节。**
包装 `build_deep_research_checkpoint_serde()` 返回的 `JsonPlusSerializer`：在 `dumps_typed`
里先调用父类序列化，再对产出的字节做 bound 校验，超限抛 `CheckpointStateBoundExceeded`——
此时 SQL 尚未执行，checkpoint 未被修改。`aput`（整个 checkpoint）与 `aput_writes`（单条
write）都经过它。
- 度量口径（apply 修正）：以**实际序列化字节长度**为准，而不是把 `channel_values` 重新用
  canonical JSON 序列化。原因：共享 serde 也会序列化框架值（agent 图的 `Send`、
  `__pregel_tasks` 等内部 channel），canonical JSON 无法处理它们，会对非 DR 图误报（apply
  中实测触发）。字节口径对所有图都稳健；DR 自己的 canonical 度量仍在 node update、读侧准入、
  离线迁移三处执行。
- 理由：这是唯一能对所有写入（含非节点来源与跨节点累积）保证"字节未落盘"的 seam。
- 备选（否）：在 `bundle_graph` 的 `ainvoke` 点之后再读校验——数据已落盘，不满足"checkpoint
  not mutated"；包装整个 saver——需实现完整 `BaseCheckpointSaver` 协议，面更大且易漏；把
  `channel_values` 用 canonical JSON 重新序列化——对框架值误报。

**2. 早拒绝 + 可归因：node wrapper 用同一 helper 校验节点 update。**
`graph/builder._node_wrapper` 在返回前对自身 update 调同一 `validate_checkpoint_values`，
越界即抛同一类型化错误，从而携带 `logical_name`/attempt 归因，满足 REG-008 的"a node returns
a state update"场景。
- 理由：serde 只能从 write channel 推断节点，归因较弱；早拒绝在确定性边界上更精确。
- 备选（否）：只做 serde——归因模糊；只做 wrapper——漏非节点写入与跨节点累积。

**3. 准入同源（schema/legacy/size），字段白名单留在既有 reducer/node-update 边界。**
抽出 `validate_checkpoint_values(values)`（schema + legacy + size）与 canonical serializer，
供写侧 serde、读侧 `_validate_current_graph_checkpoint`、离线迁移复用；live 校验必须**部分态
容忍**（不实例化 `ResearchGraphState`）。离线迁移额外保留其完整 `ResearchGraphState` 结构校验，
只共享 bound/serializer，不降级为部分态校验。字段级"未知字段拒绝"仍由既有 reducer / node
update 承担，**不**并入聚合 `channel_values` 校验——`channel_values` 是内部投影，可能含
LangGraph 内部键，把字段白名单套上去会误伤。
- 理由：消除三处各自持有 schema/size 知识的漂移风险，同时不制造新的误报面。
- 备选（否）：让 live 校验直接构造 `ResearchGraphState`——部分态会误失败；把字段白名单并入
  聚合校验——会因内部键误报。

**4. 失败语义：终态 BLOCKED，精确 incident，不 repair。**
越界 → `terminal_status=BLOCKED`、`RunFailureCode.CHECKPOINT_INCONSISTENT`、
`TerminalReason.INTERNAL_BLOCKED`、`FailureCertainty.DIRECT`，incident 经既有
`TerminalIncidentProjection` 写入 Bundle-local State（`state.json`），不写入已被拒绝的 graph
checkpoint。
- 理由：这是内部不变量破裂，确定性、用户不可修，fail-closed 最诚实；`GATE_BLOCKED` 的文档语义是
  gate 疲劳/预算（`domain/lifecycle.py:75` `@impl REG-004`），复用它等于谎报；既有
  `RunFailureCode` 文案已表达"不要继续"。
- 已知既有做法：项目现有代码/规格把非 gate 的 blocked 也复用 `GATE_BLOCKED`（如
  `bootstrap/node.py:48`、`hitl1-node` spec 的 `INPUT_INVALID_RESPONSE`）。这是既有词汇欠债，本
  change 不回改已有节点的既有值，只为新的越界终态引入专用值，并在 apply 时同步任何枚举
  blocked/terminal reason 的词汇或投影。
- 备选（否）：repair/retry（不解决根因、可能反复越界）；复用 `GATE_BLOCKED`（不诚实）；
  仅抛进程错误不落终态（run 状态不诚实，违反可检查 bundle）。

**5. 子上限与聚合上限的关系：聚合是唯一裁决者。**
不追求一条"子块 + 其余字段 ≤ 聚合"的算术不变量——其余字段没有单一上界，该命题不可测。正确关系
是：`MAX_WORK_UNIT_BLOCK_BYTES` 必须严格小于 `MAX_CHECKPOINT_STATE_BYTES`，且**即使所有子块都在
各自上限内，聚合仍由 whole-state bound 裁决**；写侧聚合校验是唯一阻止"合法子块累积越界"的执行
点。任务只固化"子块严格嵌套 < 聚合"与"子块合规不构成越界豁免"。
- 理由：原始设计正是用 whole-state bound 兜住"reducer 累积很多小 ref"
  (`2026-07-12-.../design.md:165`)；子块上限不是豁免通道。
- 备选（否）：定义"其余字段合法上界"——不存在这样的单一边界，会造出不可测的伪不变量。

## Risks / Trade-offs

- [误伤合法 run] → 校准证据显示 8–40 倍余量；绑定测试用真实 fixture 全流程回归；不改阈值。
- [serde 与通用 host/probe/agent 图共享，形状与类型不同] → 写侧只按**实际序列化字节**度量，
  不假设 DR 字段语义、不重新 JSON 序列化；对 probe/agent 图的极小或框架值 state 无影响
  （apply 中实测的 `Send` 误报即由字节口径消除）；加 probe/agent 回归。
- [LangGraph 可能包装 saver 抛出的异常，类型化错误被吞/变形] → 集成测试断言类型化终态与
  checkpoint 字节不变，而非只断言异常类型。
- [终态写入自身被 bound 拦截] → 终态写 Bundle-local `state.json`（`BundleStateStore`），不写
  graph checkpoint；设计与测试明确这一分离。
- [热路径成本] → 每次 superstep 一次 ≤64 KiB 的 canonical 序列化，可忽略；只作用于 project
  值，不含 metadata。
- [新 `TerminalReason` 值影响下游消费者] → 是向前兼容的 closed-set 新增；同步投影/测试并加
  契约断言。

## Migration Plan

- 无数据迁移。既有 retained checkpoint 若越界，读侧准入按新规则拒绝（观测数据中无此类）。
- 回滚：去掉 serde 有界包装与 node-wrapper 提前校验即可恢复到当前行为；无持久化格式变化。
- 上线顺序：先落 domain helper + 有界 serde（写侧）→ 读侧统一 → node-wrapper 早拒绝 →
  终态映射 → 绑定测试与校准证据。

## Open Questions

- `TerminalIncidentProjection.diagnostic_ref` 在越界时是否总能提供（当前多为可选）；若无，
  incident 仍可只带 `code`/`phase`/`certainty`。不影响 spec、approach 或任务拆分。

## Apply Review Record

- **Control-placement review（2026-09-13，apply agent）**：逐行核对 `## Control Placement Review`
  的实现落点，发现并修正一处实质偏差——原设计拟在写侧对 `channel_values` 用 canonical JSON 重新
  序列化来度量 bound，但共享 serde 也会序列化 agent 图的框架值（`Send`、`__pregel_tasks`），
  canonical JSON 无法处理，会对非 DR 图误报（集成测试 `test_scripted_real_workflow_debug` 实测
  被误判为 worker 失败）。修正为"以实际序列化字节长度为准"（Design Decision 1），DR canonical
  度量保留在 node update、读侧准入、离线迁移三处；Design 与该 policy 的行已同步。其余行与实现
  一致，`non-bypassable` posture 成立。
