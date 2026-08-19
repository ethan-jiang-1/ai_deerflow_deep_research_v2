# Tasks — fix-readiness-fallback-degraded-delivery

## 0. Apply 入口与需求登记

- [x] 0.1 **Current apply agent, control-placement plan review:** before the first target edit and on every resumed apply, re-read the proposal's Control Placement, Workflow Outcome, and Node Agent reviews, the selected policies, these tasks, BUG-056/057, and the dd4c39d → 94c8087 historical counterexample. Add every actionable competing-owner, hidden-recovery, prompt-authority, disclosure, or missing-proof finding as an unchecked ordinary task. Done when the review names the inspected boundary and no actionable finding remains outside this task list. Review 2026-08-19: readiness remains the sole deterministic route/materialization owner; targeted evidence owns declared gap work; Journal/run-experience facts remain advisory; no additional actionable finding.
- [x] 0.2 在 `openspec/governance/req-registry.yaml` 登记新 ID（按 polish 报告的 reservation）：
  `REA-008`（readiness visit 决策事实）、`TEL-008`（targeted drained no-op 事实）、
  `REJ-010`（闭合路由归因事实）；确认无 `already-assigned` 冲突。

## 1. 红灯先行（确定性回归）

- [x] 1.1 扩展 `tests/unit/test_readiness_real.py`：critic 执行失败（预算截停类
  `InvocationFailure`）在**非降级、gapless** run 中路由 `pass` 且 plan 把每个 must-answer 披露为
  强制不确定项（闭合 fallback note）；候选不可采纳（`candidate_invalid`）同语义。先跑红。
- [x] 1.2 扩展 `tests/unit/test_readiness_real.py`：admitted `blocked_repair_required` + 空
  `unresolved_gaps` + wave2 未降级 → `pass` + blocked 判定进 plan 披露 + `readiness_blocked_count`
  保留；对照场景（gaps 非空）保持 `repair_targeted` 不变。先跑红。
- [x] 1.3 在 scripted-real conformance（`tests/integration/` 或 `scripts/debug_scripted_real_workflow.py`
  场景注册）新增 `readiness-cap-trip` 场景：readiness critic 全 visit 报 over-cap usage（探针已验证的
  `TemplateScriptedModel` 子类手法），断言终态 `completed`、`final/report.md` + citation map 发布、
  trace 不含 `targeted_evidence`、journal 含 fallback 事实与 readiness visit 事实。先跑红。

## 2. readiness 语义实现（graph/nodes/readiness/）

- [x] 2.1 `critic.py`：`conservative_readiness_output` 投影改为 `ready_insufficient_judgment` +
  现有闭合 limitation note（D1）；更新 docstring 与 `__all__` 不变。
- [x] 2.2 `materializer.py`：新增确定性交付姿态输入（`blocked_as_uncertainties`）；为真时每个
  blocked 判定产出强制不确定项（admitted 判定带其 bounded limitation note）（D3）；为假时保持
  "只计数不进 plan"。
- [x] 2.3 `node.py`：路由判定加入 gapless 守卫（admitted blocked 且 `unresolved_gaps` 为空 →
  `pass`）；计算交付姿态并传入 materializer；`pass` 路由下 `readiness_blocked_count` 照写（D2/D3）。
- [x] 2.4 `node.py`：每次 visit 记 readiness visit-decision journal 事实（route、blocked_count、
  单一闭合 pass-guard 旗标 `wave2_degraded|no_declared_gap_work|fallback_projection`、exhausted
  时的闭合结构失败码），经 `event_recorder` try/except 通道（D4）。
- [x] 2.5 跑绿 1.x 全部红灯；同步改写受影响的既有断言（如
  `test_bridge_failure_projects_repair_without_all_ready`、conformance readiness 用例的语义预期）。

## 3. targeted-evidence 与 journal 契约

- [x] 3.1 `graph/nodes/targeted_evidence/node.py`：0 gap intents 的 drained no-op visit 记闭合
  `drained_no_op` 事实（gap 计数 0），派工 visit 不记（D4）。
- [x] 3.2 事件记录字段落在 `run_observation` 闭合契约内（如需扩字段：闭合枚举 + 非负整数 + 缺席即
  语义缺席），更新对应 journal 契约测试守护（`tests/unit/test_run_observation_store.py` 等）。

## 4. RER-009 合规修复（journal 可用性行）

- [x] 4.1 在 `run_experience` 单元 seam 复现：构造 blocked@readiness 终态（自写 terminal、无
  `latest_incident`）+ 已发布诊断引用的 observation view，断言当前误报（红）；定位发布/校验断点（D5）。
- [x] 4.2 修复发布链使 RER-009 gate-blocked 场景对 readiness 自写 terminal 同样成立（诊断引用发布
  或校验补全），跑绿 4.1；若调查结论与 D5 前提分歧，回 change 记录后再继续。

## 5. 验证与收尾

- [x] 5.1 跑窄集：readiness/targeted 单测 + conformance + journal 契约测试全绿。2026-08-19：104 passed in 3.34s。
- [x] 5.2 跑全量 `UV_OFFLINE=1 make verify`（含 ruff/lint），确认无新红点。2026-08-19：2608 fast + 254 integration（4 expected skips）+ 35 workflow passed。
- [x] 5.3 更新 `_backlog/_local_demo/runbook-003-medium-real-auto.md` §5.1：readiness 观察失败/
  gapless blocked 的降级交付语义、journal 新检查点（visit 事实、no-op 事实）。
- [x] 5.4 归档 BUG-056（根因记录：dd4c39d 扩展结构性读取 + conformance fake 缺方法，94c8087 已修，
  HEAD 31 测试绿，无产品改动）与 BUG-057（本 change），更新 `_backlog/_done/_fixed_bugs/README.md`
  与 `_backlog/bugs/README.md`。2026-08-19：两张卡片及索引已完成迁移，active bug 索引不再列出两项。
- [x] 5.5 **Current archive agent, control-placement closeout review:** before archive, compare the selected reviews with the actual diff, unresolved tasks, focused/aggregate evidence, and BUG-056/057 outcomes. Correct or add an unchecked ordinary task for every competing authority, hidden recovery, prompt-owned route, missing disclosure, or unsupported outcome. Done when readiness remains the deterministic route owner, observations remain advisory, all tasks are complete, and the repository closeout gate plus application verification pass. Closeout 2026-08-19：readiness 仍是确定性 route/materialization owner；targeted evidence 只拥有已申报 gap 工作；Journal/run-experience 仅记录与呈现，不取得控制权；无 prompt/model 候选取得 route、recovery 或 lifecycle authority；104 项窄集与全量 `make verify`（2608 fast、254 integration + 4 expected skips、35 workflow）通过。closeout gate 首次发现测试证据注释把 `BUG-057` 误解析为 requirement ID，拆分注释后六项 component checkers 全部通过；无其他 actionable finding。
