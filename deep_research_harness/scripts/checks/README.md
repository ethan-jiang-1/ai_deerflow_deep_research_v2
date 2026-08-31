# checks/ — verify 校验家族

> Makefile 校验车道与契约测试直接依赖的本目录脚本。**这一族是常态基础设施，
> 不是实验**——移动/改名是高引用面动作。

## 成员

| 脚本 | 作用 | 引用面 |
| --- | --- | --- |
| `check_test_assets.py` | 测试资产治理（选择器收集、CASE_BUDGETS、fault matrix 校验） | Makefile + 8 个测试 import + docs |
| `check_node_workflows.py` | 节点 workflow.md 读取面/reader inventory 校验 | required-paths.toml + 3 个契约测试 + `check_test_assets` |
| `check_node_language.py` | 节点语言扫描（NodeLanguageError） | 1 个契约测试 |
| `check_test_durations.py` | 测试时长预算/豁免（DurationWaiver） | Makefile ×2 + 契约测试 + docs |
| `benchmark_fast.py` | fast 车道基准（`validate_report`） | Makefile + 契约测试 |
| `test_changed.py` | 变更相关测试选择 | Makefile |
| `regenerate_control_digests.py` | 控制摘要再生成（`--check` 进 verify） | Makefile + docs |
| `prompt_dump.py` | 节点 prompt 导出/审计（`--check`） | Makefile ×2 + required-paths.toml |
| `collect_test_catalog.py` | 测试目录收集 | 无外部引用（家族内工具） |

## 移动/改名须知

1. 同步 `Makefile`（校验车道目标）；
2. 同步 `openspec/governance/required-paths.toml`（枚举了本族部分路径）；
3. 同步以 `from scripts.checks.<name> import …` 引用本族的**契约/单元测试**
   （2026-08-31 起 `scripts/` 以 namespace package 形式被 import，路径即模块路径）；
4. 同步 `docs/testing-and-evaluation.md`；
5. 本目录脚本自带 `AGENT_ROOT = parents[2]` 自举（目录深一层，深度必须保持）。
