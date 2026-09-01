# scripts/ — 可执行脚本目录导读

> 本目录按「稳定性」分三层：**根 = 常态入口/运维**、`checks/` = verify 校验家族、
> `experiments/` = 实验尖刺。新增脚本先看该放哪层（规则见各子目录 README）。

## 根目录：常态入口与运维（Makefile / required-paths / 文档直接引用）

| 类别 | 脚本 |
| --- | --- |
| Demo 入口 | `demo.py`、`demo_fixture_graph.py`、`demo_real.py`、`demo_tui.py`、`demo_sessions.py` |
| Demo 内部库（`_` 前缀，不独立运行） | `_demo_core.py`、`_inspect_view.py`、`_terminal_failure_presentation.py` |
| 环境/运维 | `configure.py`、`prepare.py`、`local_profiles.py`、`doctor.py`、`live_preflight.py`、`release_preflight.py` |
| 会话/工作区工具 | `soft_bundle.py`、`session_workbench.py` |
| 诊断入口 | `debug_scripted_real_workflow.py`（required-paths 治理内） |
| 一次性迁移 | `retained_run_data_migration.py` + `retained_run_data_inventory.json` |
| 文档渲染 | `render_topology.py`（拓扑快照渲染，`graph/topology_snapshot.py` 配套） |

## 子目录

- [`checks/`](checks/README.md) — verify 校验家族（Makefile 校验车道 + 契约测试 import）。
- [`experiments/`](experiments/README.md) — 实验尖刺（零契约，进/出都有明确规则）。

## 规则

1. **常态脚本**改动若涉及 Makefile / `required-paths.toml`（仓库根 OpenSpec 治理
   目录）/ 契约测试引用，须同步全部引用面（`grep -rn "scripts/<name>" Makefile docs/ tests/`）。
2. **实验脚本**放 `experiments/`，不进 verify 门；毕业（转正）或删除，不长期滞留。
3. 目录布局不受 `project-structure` 结构注册表枚举（其只管 src/tests/fixtures 分层），
   但 `required-paths.toml` 枚举了其中若干文件路径——移动它们必须同步该文件。
