# Tasks: restore-deterministic-verification-gate

## 1. 治理登记与红测先行

- [x] 1.0 在 `openspec/governance/req-registry.yaml` 登记 `EVH-031: evaluation-hardening — deterministic lane selection references only live markers and passes from a clean checkout`（ID 未被占用先查）；跑 `python3 openspec/governance/check_project_reqs.py .` 确认 Unregistered 消失（@impl 无——登记本身不实现需求）
- [x] 1.1 在 `tests/contract/test_scripted_real_debug_command.py` 模块 docstring 补 `@impl SCR-001`，在归属 canonical-path/no-discovery 声明的确定性测试（`tests/contract/test_import_boundaries.py` 或 `tests/integration/test_scripted_real_workflow_debug.py`，以断言覆盖为准；都不覆盖则在契约测试补一条断言）补 `@impl PRS-019`——先跑 `UV_OFFLINE=1 make test-assets` 确认当前红（`missing deterministic @impl: PRS-019,SCR-001`），补位后绿
- [x] 1.2 改 `tests/contract/test_test_lane_selection.py:33-36` 三常量断言为「不含 postgres」的新值（`DETERMINISTIC_EXCLUDE == "requires_llm or release_e2e"`、`FAST_EXPRESSION == "not (requires_llm or release_e2e or workflow)"`、`WORKFLOW_EXPRESSION == "workflow and not (requires_llm or release_e2e)"`）——先跑该单文件确认红（`tests/assets/selection.py` 还是旧值），再进任务 3.2 同步（@impl EVH-031）
- [x] 1.3 改三处「release_e2e 收集为空」断言为「收集到 suspended 选择器」：`tests/contract/test_test_lane_selection.py:112-113`、`tests/contract/test_test_structure_retirement.py:63`、`tests/contract/test_release_suspension.py:33`（并同步 :18 `SUSPENDED_SELECTOR` 常量与 :32 `is_file` 断言的旧文件名）——先跑确认红（旧文件名不可收集），执行 3.4 改名后绿（@impl EVH-031）
- [x] 1.4 在 `tests/integration/test_local_entry_environment.py` 加红测：在拷贝项目里**构造** `profiles/demo/config.yaml`（`database.backend: sqlite` + 指向 `profiles/demo/.deer-flow/data` 的绝对 `sqlite_dir`、无 checkpointer 段）与 `extensions_config.json` 后 `profile-check PROFILE=demo` 应 returncode 0；同时断言该测试不读取本机 `profiles/` 内容——先跑确认当前红（本机与干净 checkout 都红），修复后绿（@impl EVH-031）

## 2. lint 修复

- [x] 2.1 `tests/contract/test_import_boundaries.py:391-392,404-405` 四处 E501：超长字符串字面量改相邻拼接，最终字符串值逐字节不变；验证 `uv run ruff check tests/contract/test_import_boundaries.py` 无 E501 且该文件单测绿（复用既有 PRS-001..018/FSI @impl，不新增）

## 3. marker 退役与同步（单一来源，同一次编辑完成全部引用面）

- [x] 3.1 `pyproject.toml:52` 移除 `postgres` marker 注册；`Makefile` 删除 `test-postgres` target、其注释（:192-196）与 `.PHONY` 列表中的 `test-postgres`（@impl EVH-031）
- [x] 3.2 同步 lane 表达式：`Makefile:114,120,152,157` 四处 `-m` 去掉 `or postgres`；`scripts/benchmark_fast.py:19` `FAST_EXPRESSION` 同步；`tests/assets/selection.py:6,16,20` 三常量同步（单一来源常量）（@impl EVH-031）
- [x] 3.3 同步 `tests/assets/inventory.py:45` 的 VerifiedLane 表达式数据行（`"not (requires_llm or release_e2e or postgres)"` → `"not (requires_llm or release_e2e)"`；:49 的 `"1 postgres skip"` 是记录性结果描述、非 marker 引用，**保持不动**）与 `tests/contract/test_verification_gate_contract.py:55` 的 Makefile 原文断言（@impl EVH-031）
- [x] 3.4 `git mv tests/scenarios_suspended/evh_024_release_acceptance.py tests/scenarios_suspended/test_evh_024_release_acceptance.py`；同步 `tests/contract/test_release_suspension.py` 的 `SUSPENDED_SELECTOR` 文件名；校对 `tests/scenarios_suspended/README.md` 提及的文件名；`UV_OFFLINE=1 uv run --no-sync --extra operations python -m pytest tests/scenarios_suspended --collect-only -q` 应收集到 `test_evh_024_release_acceptance.py` 且被 `-m "not (requires_llm or release_e2e)"` 排除（模块 import 安全性已验证：`tests.scenarios.release` 离线 import ok）（@impl EVH-031）

## 4. integration 环境测试封闭化

- [x] 4.1 按 1.4 的红测实现：`_copy_harness` 中对 `PROFILES_ROOT` 的 copytree 加 ignore（不再拷贝本机 gitignored 的 `profiles/` 内容），测试 setup 中构造被检的 demo profile 后执行 `profile-check`；验证 `UV_OFFLINE=1 uv run --extra operations python -m pytest tests/integration/test_local_entry_environment.py -q` 全绿（@impl EVH-031）

## 5. 全量验证与收尾

- [x] 5.1 `cd deep_research_harness && UV_OFFLINE=1 make verify` 的 governance、lint、test-assets、requirement coverage 和 test-fast（2817 项）均绿；常规 `test-integration`（256 项）与 `test-workflow`（35 项）随后分别绿，均排除 periodic clean-copy 场景；`test-postgres` 目标不存在。（@impl EVH-031）
- [x] 5.2 `openspec validate restore-deterministic-verification-gate --strict` 过；`git diff HEAD --check` 无输出；按 openspec/config.yaml tasks 规矩记录：`git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status --porcelain=v1 --untracked-files=all`，并 review `git diff --submodule=short`
