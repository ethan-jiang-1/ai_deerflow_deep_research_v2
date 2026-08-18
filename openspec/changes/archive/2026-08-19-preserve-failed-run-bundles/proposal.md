## Why

BUG-052：`scripts/soft_bundle.py` 的 `_clean_run_bundles` 在每次 control run 前
`shutil.rmtree` 整个 `deep-research` 子树——run 1–3 的失败现场（state.json、
events.jsonl、checkpoint、诊断 bundle）在 run 4 前被销毁，BUG-047/049/050 的取证
只能靠 soft-bundle 记录残片。操作员重跑排障循环里，"重跑"本身在销毁要排障的
证据。战役计划（fix-003-blocking-bugs-three-changes）明确要求本任务先于
honest-degraded-delivery 的多次真实 003 复跑落地：先装消防栓，再灭火。

## What Changes

- `scripts/soft_bundle.py`：`_clean_run_bundles` 由删除改为**归档**——存在的
  `deep-research` / `scripted-real` 子树移入 `RUNS_ROOT/archive/<name>-<UTC时间戳>/`，
  保留最近 `3` 份归档（每名字独立计数），更旧的删除；随后照旧重建空目录。
- 归档目录不进入 bundle 发现范围（在 trusted scope 的 `archive/` 前缀下，
  discovery 语义不变）；归档操作输出一行可 grep 的日志
  （`archived prior run bundles -> <rel-path>`），无归档时保持原行为输出。
- 契约测试：已有 patch 点（`tests/contract/test_soft_bundle_cli.py` 对
  `_clean_run_bundles` 的 patch）不破坏；新增单测断言——带内容的旧子树被移入
  archive、新空目录重建、第 4 份归档触发最旧删除。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `run-bundle-discovery-and-operations`：RDO 增补——操作员重跑的准备步骤 SHALL
  归档（而非删除）既有 run 子树，bounded 保留最近 3 份；归档 SHALL 不进入
  bundle 发现范围。

## Impact

- 代码：`deep_research_harness/scripts/soft_bundle.py`（单函数）。
- 测试：`tests/contract/test_soft_bundle_cli.py` 新增归档行为用例。
- 行为：重跑不再销毁失败现场；磁盘占用有界（≤3 份/子树名）。
