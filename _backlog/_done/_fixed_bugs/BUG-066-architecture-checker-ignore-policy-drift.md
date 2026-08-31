# BUG-066: 项目架构治理检查器在干净工作树上失败（ignored_paths 注册策略漂移）

> 严重级别: P2 | 发现: 2026-08-31 | 状态: 活跃

## 症状

`openspec/governance/check_project_architecture.py` 在**无本地改动**的工作树上退出码 1：

```text
ERROR [ignore.entries] ignore entries must exactly match the registered policy: deep_research_harness/.gitignore
```

治理门在干净树上即红，任何依赖该检查器的验证都无法给出"结构合规"信号。

## 根因

注册契约单侧漂移：

- `deep_research_harness/.gitignore` 在 commit `07a7a1c`（"fix: relocate the verify uv
  cache into the workspace（BUG-032 follow-up）"）新增了 `.uv-cache/`（第 11 项）；
- `openspec/governance/project-structure.toml` 的 `[ignored_paths].entries` 仍注册
  旧 10 项（末项 `.repro-tmp/`），未同步 `.uv-cache/`；
- 检查器按"entries 必须与 .gitignore 完全一致"执法 → 干净树即失败。

与 2026-08-31 的 scripts/ 分层重组无关（重组未触碰 `.gitignore`，且该错误在其之前
已存在——用 `git status`/`git log` 核实 `.gitignore` 干净于 `07a7a1c`）。

## 修复方向

单行 registry 同步：`project-structure.toml` `[ignored_paths].entries` 追加
`".uv-cache/"`。属结构注册表契约改动 → 按治理走一个微 openspec change
（propose → polish → apply → archive；或经用户同意并入下一个 change 的顺手项）。
修复后 `check_project_architecture.py` 应在干净树退出 0。
