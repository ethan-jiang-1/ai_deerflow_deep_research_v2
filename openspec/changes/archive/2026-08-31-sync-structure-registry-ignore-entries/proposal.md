# Proposal: sync-structure-registry-ignore-entries

## Why

BUG-066：`openspec/governance/check_project_architecture.py` 在**干净工作树**上即红
（`ERROR [ignore.entries] ignore entries must exactly match the registered policy`）。
根因是注册契约单侧漂移：`deep_research_harness/.gitignore` 在 commit `07a7a1c`
（BUG-032 后续，verify uv cache 迁入工作区）新增了 `.uv-cache/`（第 11 项），而
`project-structure.toml` 的 `[ignored_paths].entries` 注册策略仍是旧 10 项。治理门在
干净树即失败，任何结构合规验证都无法给出绿信号。

## What Changes

- `openspec/governance/project-structure.toml` 的 `[ignored_paths].entries` 追加
  `".uv-cache/"`（对齐 `.gitignore` 实际第 11 项；追加于列表末尾，与 `.gitignore` 行序一致）
- `project-structure` spec **新增 requirement PRS-022**：把"注册 ignore 策略必须与
  harness `.gitignore` 精确有序一致、漂移即 fail closed"这条**检查器已在执法的行为**
  （`check_project_architecture.py:554-565`）登记为规范 requirement——spec 追平既有
  执法，不发明新行为
- PRS-022 登记 `openspec/governance/req-registry.yaml`
- 修复后 `check_project_architecture.py` 于干净工作树退出 0；BUG-066 按 bugs 治理关闭

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `project-structure`：**ADDED Requirement** "Registered ignore policy mirrors the
  harness gitignore"（PRS-022）——把 ignore.entries 的 fail-closed 执法行为从 checker
  代码提升为规范 requirement；其余 requirement 文本零变化

## Impact

- `openspec/governance/project-structure.toml`：单行（entries 列表 +1）
- `openspec/specs/project-structure/spec.md`：archive 时同步 PRS-022（delta 已在本
  change）
- `openspec/governance/req-registry.yaml`：登记 PRS-022 一行
- 治理门恢复绿：干净树 `check_project_architecture.py` exit 0
- BUG-066 关闭：archive 时按 `_backlog/bugs/README.md` 流程迁移 `_backlog/_done/_fixed_bugs/`
  并同步计数与 Next ID

## Change Focus

- **Primary module / causal owner:** `openspec/governance/project-structure.toml`（结构
  manifest——registered ignore policy 的唯一精确权威，PRS-009）
- **Seam classification:** deterministic-guardrail —— 修复确定性治理门（架构检查器）的
  注册策略数据与事实源之间的漂移，并把该执法行为登记为规范 requirement；无认知面、
  无人工决策面、无运行时行为变化
- **Question:** 注册的 `[ignored_paths].entries` 是否与实际 `.gitignore` 精确有序一致
  使治理门在干净树退出 0，且该 fail-closed 执法行为是否已登记为规范 requirement？
- **Necessary adjacent/external contracts:** `deep_research_harness/.gitignore`（事实源，
  本次不改）；`openspec/governance/check_project_architecture.py`（ignore.entries
  执法者，本次不改，作为证据缝）；`openspec/governance/req-registry.yaml`（PRS-022
  登记处）
- **Evidence seam:** `check_project_architecture.py` 于干净工作树 exit 0（OpenSpec-only
  governance，按 @impl 声明免平行 pytest）；delta spec 的 fail-closed scenario 由同一
  检查器行为背书
- **Not in scope:** `.gitignore` 任何内容改动；registry 其他事实（imports/required-paths/
  upstream_gitlink）；BUG-032 的 uv-cache 迁移行为本身；`deerflow/` gitlink（本次
  不触及、不源码浏览，遵守 ordinary downstream work 边界）
- **Triggered review policies:** none: 单行 manifest 数据同步加既有执法行为的规范登记，无新代码路径、无认知面、无行为变化
