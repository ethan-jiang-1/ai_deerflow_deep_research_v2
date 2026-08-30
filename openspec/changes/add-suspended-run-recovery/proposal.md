# Proposal: add-suspended-run-recovery

## Why

020 战役 B1 第 2 跑（bundle `b_yFAvXIr8…`，BUG-064）实证：网络断开使 TUI 进程
树死亡，bundle 遗弃为 `status=suspended`、journal 完整（53 事件、0 dropped），
但——重开 TUI 无任何"继续上次 run"入口（只能新跑 = 重付全部成本）；
`make demo-sessions inspect` 拒绝该 bundle（safe-inspect 只认可安全读取的
形态）；无人认领 66+ 分钟无超时无提示。同时 BUG-063 实证：正常 HITL 挂起
在 journal 里被记为 `failure_category=internal.unexpected`——2026-08-30 实
跑监控中被当场误读为内部故障。恢复能力躺在 runtime/domain（`restart_durable`
+ checkpoint + `session_workbench.resume()` + `legal_next_action`），但：
suspend≠fail 的分类学没有建立，孤儿（进程死亡、无 pending input）拿到的
`legal_next_action` 是 REFINE（全重跑）而非可恢复，呈现层没有任何 attach 面。

## What Changes

- **journal 失败分类学修正（BUG-063）**：`graph/builder.py::observed_run` 的
  catch-all 把 LangGraph `interrupt()` 挂起记成 `internal.unexpected`——
  区分挂起（suspension，正常等人/等恢复）与真实未分类异常：挂起 attempt 不
  再携带 `internal.unexpected` 失败类别。
- **safe-inspect 放宽（BUG-064d）**：非 terminal（suspended/active）bundle
  的只读诊断投影可用——`inspect` 的 inspectability 判定不再因 bundle 非终态
  而不可用（保留既有 INVALID_REFERENCE / 记录缺失等拒绝语义不变）。
- **orphan 恢复语义（BUG-064b）**：进程死亡遗留的 suspended bundle（无
  pending input）的 `legal_next_action` 从 REFINE 改为 **RESUME**；提供从
  durable checkpoint 继续执行的恢复入口（复用既有
  `bundle_graph.resume` 的 lease+checkpoint 再入机制），不伪造任何人类应答。
- **TUI attach 入口（BUG-064a）**：`demo_tui.py` 启动时扫描 demo workspace，
  发现未完成 bundle（suspended）时呈现 attach 卡片（继续 / 查看 / 放弃新跑）；
  TUI 不获得任何 admission/route 权威，继续决策仍走 lifecycle。
- 网络断开时 TUI 呈现降级状态而非进程死亡（BUG-064c）随 attach 面一并按
  既有异常呈现机制处理，本 change 只覆盖其最小可见面。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/`（`bundle_lifecycle` 的 `legal_next_action`/resume 语义与 `run_observation` 的 inspectability）——suspension 是否可恢复、可读、如何认领的权威决策面；`graph/builder.py` 的挂起分类（063）与 `scripts/demo_tui.py` attach 卡片（064a）是其投影。
- **Seam classification:** deterministic-guardrail — 挂起分类、inspectability 判定、legal_next_action 推导都是既有状态事实上的确定性函数；attach 卡片只投影 lifecycle 已判定的合法动作，无认知成分。
- **Question:** 进程死亡遗留的 suspended bundle 如何在不伪造人类应答、不改变 route/admission 权威、不破坏 terminal 不可变性的前提下，被分类为可恢复、可只读诊断、可从 durable checkpoint 认领继续？
- **Necessary adjacent/external contracts:** `domain/lifecycle.py`（`LegalNextAction` 既有枚举——orphan 复用 RESUME 值，不加新值）；`langgraph` checkpoint 再入（`bundle_graph.resume` 既有 lease+`Command(resume=…)` 机制——orphan 继续复用，不新造执行通道）；`run-event-journal`（attempt 事实语义——挂起标签是 journal 记账修正）；`research-demo-tui`（attach 卡片是呈现投影）。
- **Evidence seam:** `tests/graph/test_builder_suspension_journal.py`（063 标签）、`tests/unit/test_run_observation*.py`（inspectability）、`tests/unit/test_bundle_lifecycle*.py`（legal_next_action）、`tests/integration/test_demo_tui.py`（attach 卡片零凭证投影）。
- **Not in scope:** terminal bundle（completed/blocked/stopped/cancelled）的 resume（终态不可变是既有契约，REFINE/START 路径不变）；TUI 获得任何 route/admission 权威；多进程并发认领同一 bundle（execution lease 既有互斥已保证单持有者）；gateway observer 路线；journal schema_version 升级（outcome 值域内的最小修正）；`deerflow/` gitlink 不改动、不 source-browse（ordinary downstream work）。
- **Triggered review policies:** workflow-outcome-review, control-placement

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| 进程死亡孤儿（suspended、无 pending input） | journal attempt 事实如实记账（本 change 起：挂起≠internal.unexpected） | lifecycle resume 从 durable checkpoint 继续（lease 互斥）；不伪造人类应答 | 保持非终态直至图自然终态 | RESUME（本 change：orphan 由此前 REFINE 改归） | legal_next_action 单测 + orphan-resume 集成用例 + safe-inspect 用例 |
| HITL 等人挂起（suspended、有 pending input） | 不变（既有 pending 事实） | 不变（既有 resume 应答路径） | 不变 | RESUME（既有） | 既有回放零漂移 |
| terminal（completed/blocked/…） | 不变 | 不变（无 resume） | 不变 | 不变（REFINE/START） | 既有回放零漂移 |

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 挂起 vs 异常的分类 | 无（不涉认知） | `builder.observed_run` 对 interrupt 信号的确定性识别 | non-bypassable（异常仍 re-raise，记账不吞异常） | journal 事实如实：挂起不冒充内部故障 | 不新增事件类别，复用既有 attempt 事实字段 | graph 层确定性单测 |
| orphan 可恢复判定 | 无 | `bundle_lifecycle.result_for_state`：active+suspended+无 pending → RESUME | non-bypassable（权威在 lifecycle，gate 路由不可绕过） | terminal 不可变不变；lease 互斥不变 | 复用 RESUME 值，不新增 LegalNextAction | lifecycle 单测 |
| attach 卡片呈现 | 用户决定是否继续（决策权在人） | TUI 只渲染 lifecycle 已判定的 legal 动作 | human-decision | 不把 admission 下放 TUI（plan v4 原则）；无选择即不变更 | 复用 workbench 既有扫描/状态投影 | 集成用例（零凭证） |

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `research-graph-lifecycle`: suspended（孤儿）bundle 的 legal next action 语义——active 且无 pending input 的 suspended 状态 SHALL 投影 RESUME（可从 checkpoint 认领继续）。
- `run-event-journal`: 挂起 attempt 的记账语义——interrupt 挂起不得记为 `internal.unexpected` 失败。
- `research-local-session-workbench`: 非 terminal bundle 的只读诊断可用性。
- `research-demo-tui`: 启动时未完成 bundle 的 attach 卡片投影。

## Impact

- **代码**：`runtime/bundle_lifecycle.py`（orphan 的 legal_next_action + 恢复入口参数化）、`runtime/bundle_graph.py`（orphan 再入的 resume 变体——无人类应答的 checkpoint 续跑）、`runtime/run_observation.py`（inspectability 判定）、`graph/builder.py`（挂起分类）、`scripts/demo_tui.py`（attach 卡片）。
- **测试**：各层确定性新用例（上表 evidence seam）；全部既有回放零漂移。
- **运行时行为变化**：断网/进程死亡后重新打开 TUI 可以继续上次 run（而非只能新跑）；journal 不再把正常挂起记为内部故障。
- **战役关系**：B1 第 3 跑若再遇断网，可恢复而非作废；exact-bundle 绑定纪律（resume 不产生新 bundle）随之受益。
- **deerflow gitlink**：本 change 的全部下游工作既不修改也不源码浏览 `deerflow/` gitlink。
