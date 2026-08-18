## 1. 测试先行

- [x] 1.1 `tests/contract/test_soft_bundle_cli.py` 新增 `test_clean_run_bundles_
      archives_prior_subtrees`：在 `RUNS_ROOT/deep-research` 与 `scripted-real`
      放哨兵文件 → 调 `_clean_run_bundles()` → 断言两子树重建为空、哨兵文件
      出现在 `archive/` 下各一个带时间戳的目录里、stdout 含
      `archived prior run bundles`
- [x] 1.2 新增 `test_clean_run_bundles_prunes_to_three_archives`：预置 3 个旧
      归档目录（命名 `<name>-<旧时间戳>`）→ 调用 → 断言该名字下仍恰 3 份且
      最旧者被删
- [x] 1.3 新增空目录场景：`RUNS_ROOT` 初始为空 → 调用 → 不创建任何归档、
      两子树存在且为空（保持既有行为，现有 patch 点测试不破坏）
- [x] 1.4 运行新用例确认红（当前实现删除哨兵文件）

## 2. 实现

- [x] 2.1 `scripts/soft_bundle.py`：`_clean_run_bundles` 改为对每个受管子树名
      归档——存在且非空则 `rename` 到
      `RUNS_ROOT/archive/<name>-<UTC毫秒>`（冲突时 `-N` 递增），prune 同名
      最旧直到 ≤3，重建空子树；归档发生时打印
      `archived prior run bundles -> <repo-relative path>`；rename/prune 异常
      原样传播
- [x] 2.2 ruff 通过；新用例转绿；`tests/contract/test_soft_bundle_cli.py`
      既有用例全绿（含 `_clean_run_bundles` patch 点）

## 3. 回归与验证

- [x] 3.1 `UV_NO_CACHE=1 .venv/bin/python -m pytest tests/contract -q` 全绿
- [x] 3.2 `openspec validate preserve-failed-run-bundles --strict` 通过
- [x] 3.3 更新 BUG-052 卡片（修复关联指向本 change）
