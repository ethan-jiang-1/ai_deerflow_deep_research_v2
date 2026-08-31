# Design: demo-workspace-cleanup

## Context

操作者清理缺口（todo-demo-workspace-cleanup-command，2026-08-30 立账）+ 调查发现的
既有机制层积：`soft_bundle.py` 已有 `_archive_run_subtree`（BUG-052，DPL-007 保留
策略）在 run 前自动归档上次 run 子树——不受操作者控制、不分生命周期状态；
BUG-064 attach/claim 已落地（6df126f），suspended bundle 可恢复，故「清不掉的
东西先要能认领」的前置已成立，操作者显式保守清理面成为真缺口。

## Goals / Non-Goals

**Goals:**

- 只读盘点（report）：workspace 全量 bundle 清单 + 生命周期状态 + 大小 + resumable
  标注 + logs/archive 摘要。
- 守卫清理（clean）：dry-run 默认、`CONFIRM=1` 才删、只删 terminal、永不触碰
  非 terminal、logs 分离、删除后基线警示。
- 全部实现为可参数化纯函数核心（root 注入），CLI 动词只做包装——沿用
  `_archive_run_subtree(runs_root, name)` 的可测先例。

**Non-Goals:**

- 不动 `_clean_run_bundles()` / DPL-007 auto-run 保留策略（BUG-052 语义）。
- 不把 report/clean 变成 lifecycle authority：它们是 operator 视图（External Run
  Observation 同族），不能 admit 任何生命周期效果；attach/resume 仍走既有生命周期动作。
- 不做年龄/状态过滤参数（todo 里的「可选」项）：当前体量（67+）下一刀切已够，
  过滤参数等真实需求出现再加（Context Expansion Gate：possible future use 不足扩 scope）。
- 不改产品 runtime、`make verify` 车道、`deerflow/`。

## Decisions

1. **实现在 `soft_bundle.py`，不新建脚本；新动词命名 `workspace-report` /
   `workspace-clean`。** CLS-045 已把 soft-bundle 定位为「stateless root handle over
   existing demo and session entry points」。apply 时发现 `clean` 动词名已被占用
   （cmd_clean = 归档 prior runs，`test_clean_removes_prior_run_bundles` 钉死语义、
   run 流程依赖），原地演进会破坏已测契约，故新动词加 `workspace-` 前缀；
   Makefile targets（todo 命名 `demo-workspace-report` / `demo-clean` 保留）只做包装。
   *Alternative（演进既有 `clean`）rejected：破坏已测语义；* *Alternative（独立
   `scripts/demo_clean.py`）rejected：同一操作者面裂成两个入口。*
2. **状态判定读 run-summary.json，不走 workbench 诊断。** 理由：(a) report 是
   operator 全量视图，workbench 诊断对非 terminal bundle 的可用性受 safe-inspect
   语义约束（BUG-064 之前曾直接拒绝），全量盘点不应被它卡住；(b) run-summary 的
   `status` 字段是 BUG-064 修复引入的 suspension 真相源。诚实边界：这是 operator
   视图读取本地文件（External Run Observation 同族），**非 lifecycle authority**——
   spec 文本已写明。fail-closed：不可读 = 非 terminal = 不删。
   *Alternative（复用 DemoAdapter 逐 bundle 诊断）rejected：语义不匹配全量盘点，
   且逐 bundle 异步开销大。*
3. **workspace-clean 删除 = 真删，不归档。** 操作者显式 `CONFIRM=1` 的意图是释放空间；
   auto-clean 已提供归档保留。两套语义分明：自动=归档保守，显式=真删但有
   dry-run 门 + terminal 门。软删除选项等真实需求（Context Expansion Gate）。
   *Alternative（clean 也走 archive）rejected：与 auto-clean 语义重叠，操作者
   仍然清不掉空间。*
4. **删除对象包含 soft-bundle 记录。** 只删 bundle 目录会留下悬空 manifest 记录，
   `soft-bundle status/inspect` 随即指向不存在的 bundle。成对删除，soft-bundles
   root 本身保留。
5. **基线警示是打印义务，不是状态跟踪。** exact-bundle 基线是战役 runbook 纪律
   （runbook §exact-bundle），工具只在删除后重申警示；不引入基线注册表
   （Context Expansion Gate）。

## Risks / Trade-offs

- **[误删可恢复 bundle]** 核心风险。→ 三重门：默认 dry-run、`CONFIRM=1`、只删
  run-summary 判定的 terminal；不可读 fail-closed；非 terminal 连修改都不做。
  契约测试逐门断言。
- **[与 auto-clean 的张力]** run 前自动归档仍会把非 terminal 卷进 archive（3 轮
  后物理删除），attach 随之不可见——BUG-052 早于 BUG-064 的历史层积。→ 本 change
  不动它（Non-Goal），known interaction 记入 design 与 spec scenario（Auto-run
  retention policy is unchanged），后续是否让 auto-clean 尊重 non-terminal 是独立
  语义决策（可能产生 BUG 账或 change）。
- **[run-summary 缺失的老 bundle]** 67+ 存量 bundle 可能有旧格式/缺文件。→
  fail-closed（不删）+ report 标注 `status unknown`，宁可留垃圾不误删。
- **[Makefile 公共面]** 新 target 必须带 entry-preflight 并遵守 UV_NO_CACHE 约定
  （BUG-032），与既有 demo targets 同形。

## Verification Plan

- 契约测试（`tests/contract/test_soft_bundle_cli.py` 扩展，tmp-root fixtures）：
  report 清单与 resumable 标注；dry-run 零删除；CONFIRM 删 terminal + 记录成对删；
  非 terminal 目录逐字节不动；不可读状态 = 保留；logs 分离门控；基线警示存在。
- 真实树走查：`report`（67+ 真实 bundle）+ `clean` dry-run（应列 0 删或仅 terminal）。
- 门禁：plan/closeout gate、`UV_OFFLINE=1 make verify`、strict validate，退出码直测。
