# Design

## Context

已核实的引擎事实（2026-09-29 读码）：

- 驱动是闭合命令集（advance_one/drive_until/pause_request/answer/cancel/detach），
  **显式不是 lifecycle authority**——一切状态写入经 lifecycle 准入（LDD 文档串）。
- 图已有 **generation 级 rerun**：`graph/nodes/rerun/`（planner 节点）、
  `MAX_RERUN_GENERATIONS = 2`（`domain/lifecycle.py`）、HITL2 广播 `rerun` 选项。
  这是"整图重跑一代、由 rerun planner 规划"，**不是**节点级重执行。
- executor 每次调用重新 compile + saver（`debug_driver._invoke_once`），checkpoint
  经 langgraph（`aget_state`/`interrupt_after`）；langgraph 的 time-travel 能力
  **未被封装**，直接用会绕过 controller 的字段所有权
  （`execution_trace` 等 last_write_wins、CONTROLLER 独占写）。
- 状态字段所有权表（`domain/state.py`）把 `interaction_feedback`、trace 等列为
  CONTROLLER 写——任何"回滚已提交节点产出"都必须走 controller。

## Goals / Non-Goals

**Goals:**

- 停在边界上可重跑刚提交的节点（同输入重执行），额度有限、诚实计费提示。
- `/run` 默认自动「确认」HITL 提案跑通全流程；单步/显式 `/pause` 前永不代答；
  代答逐条明示，代答后仍未推进达阈值即停回人工。
- 全部行为经 lifecycle 准入；驱动不成为第二 authority。

**Non-Goals:**

- 改输入重跑 / 状态手术 / 注入假结果（Stage 3）。
- 改 rerun planner 的 generation 语义（复用评估，不改动其契约）。
- HITL2 决策的自动代答（只自动 hitl1 的"确认提案"；HITL2 是方向决策，仍必停）。

## Decisions

1. **节点重跑走 lifecycle 准入（路线 a，spike 已裁决可行，2026-09-29）**。机制全部
   落实：(a) `state.json` 的 phase/trace/terminal 是**图值的镜像投影**
   （`sync_graph_progress` 只拷贝）→ 回滚 = checkpoint fork + 重新投影，无独立
   权威需要外科手术；(b) checkpointer 是 `AsyncSqliteSaver`（完整历史）且
   `RootBoundedCheckpointSaver.__getattr__` 全委托 → `aget_state_history` 可用；
   (c) attempt 序号在图值（`next_attempt_ordinal_by_work_id`）→ fork 自然回退，
   重跑同 id 重写 work 目录（容忍度由红测试实证）。形态：lifecycle 新增
   `rewind_last_boundary` 准入——校验停点姿态后 fork 到最后已提交节点之前的
   checkpoint、重投影 state、追加一条 rewind journal fact（append-only 不删除）；
   驱动 `rerun_node` = 该准入 + 同一租约内重新执行同一节点。已知细节：hitl1 重跑
   复用确定性 request_id（序号 fork 回退）→ 工作台卡片去重键带帧号，durable
   pending 由重投影自然回退。
2. **auto_hitl 是显式 drive 策略**：`StopPolicy.auto_hitl: bool = False`（驱动契约
   默认显式关）；工作台 `/run` 与 Start Run **默认传 True**（用户拍板"默认自动+
   可停"），`/run --no-auto-hitl` 显式关。单步 advance_one 永不代答；HITL2 方向
   决策永不代答。代答 = 驱动以操作者名义提交 `answer(「确认」)` 走既有 semantic
   intake；驱动快照携带代答事实供工作台逐条明示。停止条件（纯函数
   `auto_hitl_should_stop` 便于单元锁）：同一 drive 内连续 2 次代答未被接受
   （feedback kind ∈ {clarification, semantic_invalid, semantic_unavailable}）
   → 停回人工停点并渲染 hitl1 回复。
3. **authority 台账**：重跑与代答都经既有 lease + cursor 幂等（expected_cursor
   携带、command_id 去重）；fork/重投影/rewind fact 全部发生在 lifecycle 准入内，
   驱动不获得任何新写权限。
4. **REQ 登记**：新 req id `LDD-007`、`LDD-008`、`RED-016` 在 apply 时写入
   `openspec/governance/req-registry.yaml`（一行式条目，跟 RED-015/LDD-006 同格式）。

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
|---|---|---|---|---|---|---|
| 节点重跑的回滚写入 | 无认知面——确定性重执行 | controller `retry_last_boundary` 准入；journal/work-unit 记账为准 | 驱动只发命令，不做第二 authority | 字段所有权不变；失败=typed 拒绝+停点保持 | 复用 lease/cursor 幂等，不引入 time-travel 旁路 | 驱动矩阵：重跑后 trace/journal 断言 |
| auto-hitl 代答 | hitl1 semantic intake（既有）分类「确认」 | drive 策略合成 answer；接受与否由图判定 | 操作者显式策略，逐条明示 | HITL2 仍必停；连续未接受即回人工 | 不新增认知面；复用 answer 命令全链 | 矩阵：代答→接受/拒绝→停止 条件表 |

## Risks / Trade-offs

- **回滚不变量风险**（高）：evidence/journal 是否允许尾帧撤销——spike 先行，
  红线即降级（见 Decisions 1）。
- **auto-hitl 默认值争议**：默认开会替操作者确认其未读提案——已由用户拍板
  （"默认自动+可停"），但渲染必须醒目 + `/run --no-auto-hitl` 显式关闭路径
  保留在设计中评估。
- **额度消耗**：embedded 下重跑=再烧一次真实调用；入口处明示成本提示。
