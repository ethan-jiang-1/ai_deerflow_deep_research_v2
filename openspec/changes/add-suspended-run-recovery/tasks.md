# Tasks: add-suspended-run-recovery

## 1. TDD 红（确定性，零凭证零网络）

- [ ] 1.1 `tests/graph/test_builder_suspension_journal.py`（新建）：注入
  graph human-interrupt 信号穿过 node visit → 断言 attempt 事实不再携带
  `failure_category=internal.unexpected` 且以挂起语义记账（REJ-011 场景 1）；
  真异常注入 → `internal.unexpected` 照旧 + 异常仍 re-raise（REJ-011 场景 2）
- [ ] 1.2 `tests/unit/`（bundle_lifecycle 既有文件或新建）：构造
  active+suspended+无 pending request 的 BundleLocalState → 断言投影
  `legal_next_action=RESUME`；pending 存在 → RESUME（既有语义）；
  terminal → REFINE/START 不变（REG-023 三场景）
- [ ] 1.3 `tests/unit/`（run_observation / session_workbench）：构造
  journal 完整的非 terminal bundle → 诊断视图 available（RWB-009 场景 1）；
  journal 缺失 / 非法引用 / 记录损坏 → unavailable 逐字不变（RWB-009 场景 2）
- [ ] 1.4 `tests/integration/test_demo_tui.py`：存在 RESUME bundle → 启动
  出现 attach 投影（bounded 列表 + phase summary + 三选）；无 → 启动零变化
  （RED-011 场景 1+3）；选择继续 → 走 lifecycle resume 路径（RED-011 场景 2）
- [ ] 1.5 孤儿续跑确定性用例：fixture checkpoint 的 orphan resume → 图从
  checkpoint 继续、无伪造人类应答、到达自然终态（REG-023 场景 2）

## 2. 实现（design D1-D4，逐 decision 对应）

- [ ] 2.1 `graph/builder.py::observed_run`：interrupt 信号先于 catch-all
  识别并记挂起事实（D1；apply 取证信号类型，R3 备选分支同任务内调整）
- [ ] 2.2 `runtime/bundle_lifecycle.py::result_for_state`：is_active 非待答
  分支投影 RESUME（D2 上）；`runtime/bundle_graph.py`：无应答续跑变体
  （lease/checkpoint/journal envelope 机制复用，D2 中）；`runtime/
  session_workbench.py::resume`：孤儿（无 pending）继续入口（D2 下）
- [ ] 2.3 `runtime/run_observation.py`（或其上游判定）：inspectability 与
  终态解耦——用保留孤儿 `b_yFAvXIr8…` 复现拒绝点后精确修（D3；真机冒烟
  作为补充证据，不进 verify 门）
- [ ] 2.4 `scripts/demo_tui.py`：启动扫描 + attach 卡片（继续/查看/放弃）
  （D4）
- [ ] 2.5 任务 1 全部用例转绿；既有全部回放零漂移（R4）

## 3. 契约与门

- [ ] 3.1 在 `openspec/governance/req-registry.yaml` 登记新 ID：REG-023、
  REJ-011、RWB-009、RED-011（描述与各 delta spec 一致；确认无冲突）
- [ ] 3.2 对照四个 delta spec 逐 scenario 核对测试覆盖（1.1-1.5），在本
  文件勾注对应关系
- [ ] 3.3 `UV_OFFLINE=1 make verify` 全绿（fast + integration + workflow）
