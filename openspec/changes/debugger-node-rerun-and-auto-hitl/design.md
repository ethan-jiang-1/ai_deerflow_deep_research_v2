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

1. **节点重跑走 lifecycle 准入的新控制路径（路线 a）**，不直接用 langgraph
   time-travel（路线 c 违反字段所有权），不伪装成 generation rerun（路线 b 粒度
   错误：会重跑整图一代）。形态：controller 提供 node 级 `retry_last_boundary`
   准入——回滚该节点本次 visit 的 committed 产出（execution_trace 尾帧、work
   unit attempt 记账、相关 evidence 指针），重入该节点 superstep。**本 change
   的第一个任务是可行性 spike**：controller 是否能以事务方式回滚尾帧而不破坏
   journal/evidence 不变量；不能则降级为"显式说明的整代 rerun 快捷方式"并回报
   用户重审范围。
2. **auto_hitl 是 drive 策略不是命令**：`StopPolicy.auto_hitl: bool = True`
   （加法默认值；单步 advance_one 永不代答）。代答 = 驱动以操作者名义提交
   `answer(「确认」)`，走既有 semantic intake 与轮次会计；日志逐条写
   `⚙ drive 策略代答: 确认（auto-hitl）`。停止条件：同一 request 连续 2 次
   代答未被接受（提案不完整/语义拒绝）→ 停回人工停点并渲染 hitl1 回复。
3. **authority 台账**：重跑与代答都经既有 lease + cursor 幂等（expected_cursor
   携带、command_id 去重）；代答不产生新的写权限，重跑的回滚写入全部由
   controller 在准入内完成。

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
