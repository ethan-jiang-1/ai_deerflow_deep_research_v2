## 1. Manifest 数据同步（Synchronized Changes 第 2 条）

- [x] 1.1 `openspec/governance/project-structure.toml` 的 `[ignored_paths].entries`
      追加 `".uv-cache/"`（列表末尾，与 `deep_research_harness/.gitignore` 第 11 行对齐；
      不动其他任何 registry 事实）
- [x] 1.2 `openspec/governance/req-registry.yaml` 登记 PRS-022 一行
      （`PRS-022: project-structure — <requirement 语句>`，与本 change delta 的
      "Registered ignore policy mirrors the harness gitignore" 一致）
- [x] 1.3 干净工作树验证：`openspec/governance/check_project_architecture.py` 退出 0
      （ignore.entries 与全量结构检查一并通过）

## 2. Locator 与 fixture 确认（Synchronized Changes 第 3/4 条）

- [x] 2.1 确认 `deep_research_harness/AGENTS.md` 生成 locator 无 diff——locator 刻意
      不覆盖 ignore entries；如检查器报不一致，用其 `--render-guide` 再生成后复核
- [x] 2.2 确认无契约 fixture 需要更新——ignore.entries 为 OpenSpec-only governance
      `@impl` 执法（check_project_architecture.py），按政策不要求平行 pytest 树

## 3. BUG-066 关闭（bugs 治理流程；路径以仓库根为基准）

- [x] 3.1 `git mv _backlog/bugs/BUG-066-architecture-checker-ignore-policy-drift.md
      _backlog/_done/_fixed_bugs/`
- [x] 3.2 更新 `_backlog/_done/_fixed_bugs/README.md`（加 BUG-066 表格行；
      Next available bug ID BUG-066 → BUG-067）与 `_backlog/_done/README.md`
      （`_fixed_bugs/` 计数 65 → 66、Next 列 BUG-066 → BUG-067）
- [x] 3.3 更新 `_backlog/bugs/README.md`（移除该活跃行；Next available bug ID 保持
      BUG-067）

## 4. Change 收口

- [x] 4.1 `openspec validate sync-structure-registry-ignore-entries` 通过
- [x] 4.2 按 openspec-archive-change 流程归档本 change
