# Tasks: add-suspended-run-recovery

## 1. TDD 红（确定性，零凭证零网络）

- [x] 1.1 `tests/graph/test_node_wrapper.py`（既有
  `TestWrapperJournalEvents` 缝，沿用 catch-all 测试先例）：注入
  `langgraph.errors.GraphInterrupt` → 断言 attempt 事实
  `outcome="suspended"` 且不再携带 `failure_category=internal.unexpected` /
  `worker_failure_category=unknown`（REJ-011 场景 1）
  → `test_wrapper_records_human_interrupt_suspension_without_internal_unexpected`
  （红→绿）；真异常路径由既有
  `test_wrapper_records_safe_unknown_boundary_failure_and_preserves_the_exception`
  锁定（REJ-011 场景 2，零漂移）
- [x] 1.2 `tests/contract/test_research_lifecycle_contract.py`：构造
  active+suspended+无 pending request 的 BundleLocalState → 断言投影
  `legal_next_action=RESUME`（REG-023 场景 1）
  → `test_suspended_orphan_without_pending_input_projects_resume`；
  pending 存在 → RESUME 既有语义 + terminal → REFINE 不变（REG-023 场景 3）
  → `test_pending_input_resume_projection_unchanged` +
  `test_terminal_projection_keeps_refine`
- [x] 1.3 `tests/integration/test_session_workbench.py`：fixture 孤儿
  bundle（lifecycle.start + sync_graph_progress(pending=None) + journal
  establish）→ workbench 诊断 available（RWB-009 场景 1）
  → `test_diagnosis_is_available_for_a_suspended_bundle_with_complete_journal`
  ——**apply 发现：诊断在无活持有者时对非 terminal bundle 本已可用**
  （15:05 实跑拒绝 = 冻结 TUI 进程持锁的正确保守行为），故本任务定性为
  契约锁，2.3 无产品改动
- [x] 1.4 `tests/unit/test_demo_tui_attach.py`：扫描只认 RESUME 投影、
  卡片渲染（bounded + phase + 三选）、无恢复项零变化、workbench 失败容忍
  （RED-011 场景 1+3 + 呈现纯函数）
  → 5 用例全绿；场景 2（继续走 lifecycle）→ 经验层
  `test_continue_run_adopts_orphan_bundle_and_routes_empty_resume` +
  控制层 `test_orphan_resume_with_no_messages_continues_from_checkpoint`
- [x] 1.5 孤儿续跑确定性用例：控制层 orphan + 空消息 → executor
  `continue_run` 被调用且不构造应答
  → `test_orphan_resume_with_no_messages_continues_from_checkpoint`；
  waiting + 空消息 → 不 continue（应答契约不变）
  → `test_waiting_bundle_with_no_messages_does_not_continue`；
  执行器层 continue → `ainvoke(None)`（无伪造 Command(resume)）
  → `test_executor_continue_run_reenters_checkpoint_without_a_response`

## 2. 实现（design D1-D4，逐 decision 对应）

- [x] 2.1 `graph/builder.py::observed_run`：`except GraphInterrupt`
  （`langgraph.errors`，已核实为 Exception 子类）先于 catch-all 记
  `outcome="suspended"` 后 re-raise；其余异常路径逐字不变（D1；R3 未触发）
- [x] 2.2 孤儿恢复三层：`runtime/bundle_lifecycle.py::result_for_state`
  is_active 非待答分支投影 RESUME（D2 上）；
  `runtime/bundle_graph.py::BundleGraphExecutor.continue_run`——lease +
  checkpoint + `ainvoke(None)` 无应答续跑（D2 中）；
  `runtime/bundle_control.py::_resume`：`pending_request_id is None and
  not messages` → continue 分支（D2 下改为控制层入口——design 原拟的
  session_workbench.resume 是状态投影层、无图执行权，生产 resume 入口在
  controller，已按实际权威落点实现并在此记录）
- [x] 2.3 inspectability：**无需产品改动**——诊断对非 terminal 本已可用
  （1.3 契约锁）；实跑拒绝 = 活持有者锁的保守语义，予以保留并记录
- [x] 2.4 `scripts/demo_tui.py`：`_scan_recoverable_run`（discover 只认
  RESUME）+ `_attach_card_lines`（bounded 卡片）+ `_render_recon` 注入 +
  侦察关键词「继续」（`ContinueRun` 派发）/「查看」（诊断渲染）/
  「新跑」（放弃清卡）（D4）
- [x] 2.5 任务 1 全部用例转绿；既有回放零漂移：node wrapper 16、
  lifecycle contract 13、session workbench（含新增）全绿、demo_tui 52、
  run_experience contract 18、orphan resume 3、attach 5

## 3. 契约与门

- [x] 3.1 `openspec/governance/req-registry.yaml` 登记 REG-023、REJ-011、
  RWB-009、RED-011（描述与各 delta spec 一致；登记前各自原无占用）
- [x] 3.2 对照四 delta spec 逐 scenario 核对：REJ-011 两场景 → 1.1；
  REG-023 三场景 → 1.2 + 1.5；RWB-009 两场景 → 1.3（场景 1 绿锁 +
  场景 2 既有拒绝用例群）；RED-011 三场景 → 1.4（投影/路由/零变化）+
  1.5 路由链
- [x] 3.3 `UV_OFFLINE=1 make verify` 全绿（fast + integration + workflow）——**2026-08-30 实跑 exit 0**：lock-check/lint/format/assets ✅ + fast 2666（2656 + 本 change 10 个新用例）+ integration 306 + workflow 35
