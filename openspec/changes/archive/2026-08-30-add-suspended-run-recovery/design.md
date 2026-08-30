# Design: add-suspended-run-recovery

## Context

实证现场：`b_yFAvXIr8…`（2026-08-30，网络断 → TUI 进程树死亡）。

已核代码事实：

- **挂起即异常**：`graph/nodes/hitl1/node.py:1067` 用 `langgraph.types.interrupt()`
  发起 HITL 挂起；挂起信号以异常形态穿过 `graph/builder.py::observed_run`
  的 `except Exception` catch-all → 记 `failure_category="internal.unexpected"`
  + `worker_failure_category="unknown"` 后 re-raise（BUG-063 现场：run 1 两处、
  run 2 两处，且同一 attempt_id 之后成功复活——挂起不是崩溃）。
- **孤儿 recovery 缺口**：`bundle_lifecycle.result_for_state`（:860-871）
  对 `is_active` 状态：`waiting`（有 pending request）→ RESUME；无 pending
  → refinement 存在给 STATUS，否则给 **REFINE（全重跑）**。孤儿拿到 REFINE。
- **resume 再入机器已存在**：`bundle_graph.resume`（:657+）在
  `execution_exclusion` lease + `open_graph_checkpoint` 下 `ainvoke(Command(
  resume=response…))`——但要求 `AcceptedHumanResponse`，且 workbench 层的
  `resume(bundle_id, expected_request_id, …)` 做 pending request 匹配
  （`RESPONSE_MISMATCH`）。孤儿无 pending request，进不去。
- **inspect 拒绝链**：`scripts/_inspect_view.py:20` 的拒绝文案由
  `session_workbench.diagnosis()`（:262-278）的
  `WorkbenchDiagnosisView(UNAVAILABLE)` 投影，上游是
  `RunObservationStore.inspect()` 的 inspectability 判定（run 2 现场
  journal 完整仍被拒——具体拒绝点在 apply 用真实孤儿 bundle 复现定位）。
- **会话内 resume 路由**：`run_experience.py:376/411` 的 `("resume", …)`
  只服务本进程已持有 `_pending_request` 的会话——跨进程孤儿恢复没有入口。

## Goals / Non-Goals

**Goals:**

- 挂起 attempt 的 journal 事实如实区分"等恢复"与"真崩溃"（063）；
- 非 terminal bundle 的只读诊断可用（inspectability 放宽）；
- 孤儿（suspended、无 pending）获得 `legal_next_action=RESUME` 与从
  checkpoint 继续的恢复入口（不伪造人类应答）；
- TUI 启动 attach 投影（继续/查看/放弃），零权威。

**Non-Goals:**

- terminal 不可变性与其 REFINE/START 路径；gateway observer；多 bundle
  并发认领（lease 互斥已保证）；journal schema_version 升级；
  TUI 获得 route/admission 权威；断网时长跑图自身的存活（那是 C1/提供商
  层韧性）；`deerflow/` gitlink。

## Decisions

### D1 挂起分类：在 catch-all 之前识别 interrupt 信号

`observed_run` 在 `except Exception` 之前显式捕获 langgraph 的人类中断信号
类型，记 attempt 事实（outcome 用既有值域内可表达挂起语义的形态，如
outcome="suspended"——journal 已有 outcome 字段是自由字符串值域，不加新
类别字段、不升 schema），然后照常 re-raise。其余异常路径逐字不变。

- 理由：不升 schema、不加事件类别即满足 REJ-011 的"复用既有字段"；
- apply 取证点：确认 langgraph 公开的信号类型（`GraphInterrupt` 或
  `interrupt()` 抛出的具体异常）及其在 re-raise 后被 graph 机制消费的形态，
  用 `tests/graph/test_builder_suspension_journal.py`（新建）锁定。

### D2 孤儿恢复入口：resume 语义扩展为"应答 OR 继续"

`bundle_lifecycle`/`bundle_graph`/`session_workbench` 三层协同：

- `result_for_state`：`is_active` 且非 waiting（无 pending request）→
  `legal_next_action = RESUME`（原 REFINE/STATUS 分支保留给……不再可达？
  不——REFINE/STATUS 的既有语义绑定 refinement 投影；孤儿改判 RESUME 后，
  原"无 refinement → REFINE"分支不再从 is_active 投影（orphan 就是这个
  形态），refinement 存在的 STATUS 分支保留不变）。
- 恢复执行：`bundle_graph.resume` 增加无应答变体（不构造
  `AcceptedHumanResponse`，`ainvoke(None, config)` 从 checkpoint 续跑），
  lease/`ensure_live()`/journal envelope 机制逐字复用。
- **apply 修正（实际落点）**：孤儿的执行入口在
  `bundle_control._resume`（controller 持有图执行权；`session_workbench.resume`
  是状态投影层、无图执行权，不在此实现）——`pending_request_id is None and
  not messages` → `executor.continue_run`。
- 取消/失败语义不变：续跑后图自然走向终态。

### D3 inspectability——apply 取证结论：无需产品改动

复现取证（真实孤儿 `b_yFAvXIr8…` + fixture）：`RunObservationStore.inspect`
与 workbench `diagnosis` 对非 terminal 且 journal 完整的 bundle **本已可用**
（`tests/integration/test_session_workbench.py::test_diagnosis_is_available_
for_a_suspended_bundle_with_complete_journal` 绿锁）。15:05 实跑拒绝的真实
原因 = 冻结 TUI 进程持有 journal 锁——对正在写入的 journal 拒读是正确的保守
语义，予以保留。本 facet 定性为契约锁（RWB-009），无产品改动。

### D4 TUI attach 卡片：只投影，不决策

`demo_tui.py` 启动扫描（复用 workspace bundle 发现），过滤
`legal_next_action == RESUME` 的 bundle，呈现最近 N 个（bounded）+
phase summary，三选：继续（走 lifecycle resume）/ 查看（走诊断投影）/
放弃新跑（走既有 StartRun）。无 RESUME bundle 时启动零变化。

## Risks / Trade-offs

- **R1 孤儿 checkpoint 的真实形态未在真机上取证**（graph.sqlite 停在
  wave1 中段）：apply 用保留的 `b_yFAvXIr8…` 真实孤儿做恢复冒烟（不进
  verify 门，作补充证据）；确定性测试用 fixture checkpoint。
- **R2 续跑与 execution lease 的交互**：孤儿恢复时 lease 必然无持有者；
  `ensure_live()` 语义需在续跑路径上等价成立——apply 用 lease 单测锁定。
- **R3 interrupt 信号类型的可捕获性**：langgraph 信号若在 node 帧内已转换
  为其他形态，则 D1 的捕获点后移——apply 取证后若不成立，改为在
  `_record_node_event` 调用点按信号类型分支（同一 seam，任务内调整）。
- **R4 既有回放零漂移**：waiting→RESUME、terminal→REFINE/START、
  internal.unexpected 对真崩溃的记录——全部既有用例必须逐字保持绿。
