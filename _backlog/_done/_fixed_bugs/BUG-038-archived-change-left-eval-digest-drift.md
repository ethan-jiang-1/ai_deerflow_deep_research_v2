# BUG-038: 归档 change 遗留 eval 控制 digest 漂移，`make verify` 在 HEAD 上红

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 已修复（openspec/changes/honest-delivery-and-real-run-diagnostics）

## 症状

干净 HEAD 上 `make test-fast`（含 `tests/eval`）挂 35 个，全部死于
`load_case_registry` 抛 `evaluation_runtime_control_digest_mismatch`；
`test_cognitive_evaluation_suite` 的场景装配整体不可用。

## 根因

归档 commit `13249bb`（2026-08-18-low-scale-real-auto）修改了
`domain/synthesis.py`（+73 行）和 `tool.py`，但未按 `d09bad1` 确立的惯例同步刷新
`evals/control/cases/*.json` 中钉住的 runtime-control digest
（`wave2-cognitive-program-v1.json` 的 `synthesis_result_schema_digest`、
`public-controller-direction-loop-v1.json` 的 tool.py digest）。该 change 的完成凭
证是部分车道（commit 自述 "Verified: 2069 unit/graph/contract tests"），未跑含
eval 的 fast 车道，漂移随归档进入主线。流程层缺口：验证条目按部分车道绿勾选，
违背 governance `test-evidence-policy` 的"归档前过全量门"要求——策略已存在，
失守在执行。

## 复现

`git stash -u` 全部工作树改动后：`.venv/bin/python -m pytest tests/eval -q` →
同样 35 failed（2026-08-18 实测确认预存在）。

## 修复关联

在 honest-delivery-and-real-run-diagnostics apply 内机械刷新两处 digest（沿用
`d09bad1` 的 bump 模式，不引入新机制）；修复后 `tests/eval` 107 passed。
经验沉淀：`_backlog/_learning/2026-08-18-honest-delivery-apply.md`
（Next-Time Standard：触碰被钉文件同步刷新 digest；归档前全量门全绿）。
系统性守则已在 `openspec/governance/test-evidence-policy.md`，无需新 change。
