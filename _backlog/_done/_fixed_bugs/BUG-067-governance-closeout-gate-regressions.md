# BUG-067: 治理 closeout 门干净树即红——scripts 重组遗留依赖方向误报与 PRS-022 证据缺口

> 严重级别: P1 | 发现: 2026-09-02 | 状态: 活跃

## 症状

`python3 openspec/governance/check_project_gate.py --phase closeout` 在干净树
（HEAD = 16f481c，无任何本地改动）上即失败，两个成员检查器非零：

1. `check_harness_dependency_direction.py`：
   `deep_research_harness/scripts/README.md` 与 `scripts/checks/README.md` 命中
   forbidden token `openspec/`。
2. `check_project_req_coverage.py`：`uncovered requirement: PRS-022`。

后果：任何 OpenSpec change 都无法通过 closeout 归档（Cpre 首当其冲被阻）。

## 根因

commit 3965640（2026-08-31 scripts/ 三层重组）在两份 README 的正文里写了完整
治理路径 `openspec/governance/required-paths.toml`。依赖方向检查器是对 harness
全树的字面 token 扫描（`openspec/`、`../openspec`、`openspec.governance`），
不分代码还是文档 prose，于是把这两处引用当成下游依赖。同批重组把提供
`check_test_assets.py` 等引用面重排，但从未有 test/governance docstring 携带
`@impl PRS-022`——coverage 检查器要求 main spec `> req:` 声明的每个需求都有
evidence 引用（tests docstring 或 governance `.py` docstring），PRS-022
（registry `[ignored_paths]` 与 `.gitignore` 镜像 + 架构检查器 fail-closed）的
owning checker `check_project_architecture.py` 的 docstring 只列到 PRS-021，
缺 PRS-022。

与 BUG-066 同族：都是"结构/治理清单同步面"在重组时漏了一类引用面；BUG-066
漏的是 manifest `[ignored_paths]`，本 bug 漏的是文档 prose token 与 evidence
docstring。

## 复现

```bash
git worktree add /tmp/head-check HEAD && cd /tmp/head-check
python3 openspec/governance/check_project_req_coverage.py   # exit 1, PRS-022
python3 openspec/governance/check_harness_dependency_direction.py  # exit 1, 2 README
```

## 修复关联

随 Cpre（reconcile-hitl2-autonomous-contracts）closeout 解阻一并落地，但不属于
Cpre 的契约载荷（零 spec/runtime 变更，故不走独立 OpenSpec change）：

1. 两份 README 的治理路径引用改为裸名 `required-paths.toml` + 文字指向仓库根
   OpenSpec 治理目录（与两文件其余处已有的裸名引用一致；PRS-009 要求的是
   "link to or validate against"清单，字面 token 并非契约要求）。
2. `check_project_architecture.py` docstring 补 `@impl PRS-022`（它正是该需求
   声明的 owning checker）。
