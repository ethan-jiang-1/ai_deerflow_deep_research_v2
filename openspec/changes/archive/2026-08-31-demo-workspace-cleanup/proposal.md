# Proposal: demo-workspace-cleanup

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/soft_bundle.py` — CLS-045 定位的 operator root handle；新增 `report` / `clean` 两个动词，Makefile 公共入口新增 `demo-workspace-report` / `demo-clean` targets 包一层。`demo-pipeline` capability 的新 requirement **DPL-014** 拥有「operator 工作面如何盘点与保守清理」这条决策。
- **Seam classification:** wiring — operator tooling 的组合/适配面；无认知责任、无模型可见行为、无产品生命周期契约变化；清理守卫是脚本内确定性策略。
- **Question:** 操作者如何在不经手 `rm -rf` 的前提下，获得 demo workspace 的只读全量盘点，并在永不摧毁可恢复（非 terminal）bundle 的前提下清理 terminal bundle 与日志？
- **Necessary adjacent/external contracts:** DPL-007（auto-run 保留策略——本 change 不动它，交互张力如实记录）；BUG-064 attach 语义（非 terminal = 可 resume，故不可删）；`docs/local-operations.md`（"no cleanup command" 现状陈述须同步）；`COMMANDS.md` §2/§3；`_backlog/todos/todo-demo-workspace-cleanup-command.md`（设计约束来源）。
- **Evidence seam:** `tests/contract/test_soft_bundle_cli.py` 扩展（tmp-root fixture：terminal 可删、非 terminal 必留、状态不可读 fail-closed、CONFIRM 门、logs 分离、基线警示）+ 真实树 dry-run 走查（workspace 现存真实 bundle）。
- **Not in scope:** auto-run sweep `_clean_run_bundles()` / DPL-007（BUG-052 语义不变；它与 attach 的张力记为 known interaction，留给后续独立决策）；产品运行时与生命周期权威（report/clean 是 operator 视图，非 lifecycle authority）；`deerflow/`。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

`.deep-research-demo-runs/` 只增不减（本机 67+ bundles），操作者清理只有手 `rm -rf`——有误删可恢复 bundle 的风险，也会破坏 exact-bundle 基线快照纪律（`_backlog/todos/todo-demo-workspace-cleanup-command.md`，2026-08-31 复核清理命令仍不存在）。调查发现既有机制已覆盖一半：`soft_bundle.py` 的 `_clean_run_bundles()`（DPL-007/BUG-052）在 run 前自动归档上次 run 子树（保留 3 份），但它 (a) 不受操作者控制、(b) 不区分生命周期状态（suspended/可 resume 的 bundle 同样被卷进 archive，attach 随之不可见）——所以操作者显式、保守、状态感知的清理面仍是真缺口。BUG-064 attach/claim 已落地（6df126f），保守清理的配套语义已具备。

## What Changes

- `scripts/soft_bundle.py` 新增两个动词（命名避开既有 `clean` 动词——它的「归档 prior runs」语义被 `test_clean_removes_prior_run_bundles` 钉死且被 run 流程依赖，原地演进会破坏已测契约）：
  - **`workspace-report`**：只读盘点——遍历 workspace scopes，列出每个 bundle 的 id、lifecycle status（读 bundle 内 `run-summary.json` 的 `status`；terminal = `completed|stopped|cancelled|blocked`）、大小；非 terminal 标注 `resumable`；**状态不可读 = 非 terminal**（fail-closed）；输出顶部声明这是 operator 视图（非 lifecycle authority）。附带 logs 目录与归档目录的规模摘要。
  - **`workspace-clean`**：默认 **dry-run**（只列将删项与将留项，零删除）；`CONFIRM=1` 才真删，且只删 terminal bundle 目录及其 soft-bundle 记录；**永不修改/删除非 terminal bundle**；`--logs` 单独清理 logs（同样受 CONFIRM 门控）；删除后打印 exact-bundle 基线失效警示。
- `Makefile` 新增 `demo-workspace-report` 与 `demo-clean` targets（`DEMO_ARGS` 透传，入口 preflight 同既有 demo targets）。
- 文档同步：`docs/local-operations.md` 的 "no cleanup command" 现状段改写为新命令说明；`COMMANDS.md` §2/§3 更新。
- `req-registry.yaml` 登记 **DPL-014**（apply 任务）。

## Capabilities

### New Capabilities

（无 —— 新 requirement 归入已有 `demo-pipeline` capability）

### Modified Capabilities

- `demo-pipeline`: 新增 **DPL-014** —— demo operator workspace 经由 soft-bundle handle 提供只读盘点与守卫清理：报告列出 bundle 生命周期状态并标注可恢复项；清理默认 dry-run、显式确认后仅删 terminal、永不触碰非 terminal、日志分离清理、删除后警示基线失效；状态不可读按非 terminal 处理；DPL-007 的 auto-run 保留策略不变。

## Impact

- 代码：`scripts/soft_bundle.py`（+`report`/`clean` 动词与可参数化的纯函数核心）、`Makefile`（+2 targets）。
- 测试：`tests/contract/test_soft_bundle_cli.py` 扩展（tmp-root fixtures，零网络）。
- 结构：`req-registry.yaml`（+DPL-014，apply 登记）；`project-structure.toml` 预计零改动（scripts 目录已有登记，无新文件路径）。
- 文档：`docs/local-operations.md`、`COMMANDS.md`。
- 不动：`_clean_run_bundles()`/DPL-007、产品 runtime、`make verify` 车道、`deerflow/`。
- 验证门：`pytest tests/contract/test_soft_bundle_cli.py`；真实树 `report` + `clean`（dry-run）走查；`check_project_gate.py --phase plan` / `--phase closeout`；`UV_OFFLINE=1 make verify`；`openspec validate --strict`；退出码均直测。
