# Tasks: restore-agents-structure-locator

## 1. 恢复 registry `[guide]` 表与解析（先数据）

- [x] 1.1 `project-structure.toml` 恢复 `[guide]` 表：`path = "deep_research_harness/AGENTS.md"`、`begin_marker = "<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->"`、`end_marker = "<!-- END GENERATED: PROJECT-STRUCTURE -->"`（与 `2bbaa82` 一致）。
- [x] 1.2 delta spec `specs/project-structure/spec.md` 声明 **PRS-021**（ADDED：checker 强制 locator block 存在与 freshness）。
- [x] 1.3 `check_project_architecture.py`：`StructureManifest` 增 `guide_path`/`begin_marker`/`end_marker` 字段；`load_manifest` 解析 `[guide]` 并校验（`begin_marker != end_marker`、`guide.path == deep_research_harness/AGENTS.md`）。

## 2. 恢复渲染 + freshness（红→绿）

- [x] 2.1 恢复 `render_guide_block(manifest)`（与旧版一致；「Exact inventory / Validate」两行按 PRS-009 重写为 path-free，避免 Harness link OpenSpec 内容）。
- [x] 2.2 恢复 `_validate_guide(root, manifest)`：marker 缺失/重复 → `guide.marker_missing`/`guide.marker_duplicate`；block ≠ `render_guide_block(manifest).rstrip("\n")` → `guide.drift`；在 `validate_project` 中调用。
- [x] 2.3 恢复 `--render-guide` CLI（`print(render_guide_block(manifest), end="")`）。
- [x] 2.4 负例走查：临时删除 AGENTS.md block → `check_project_architecture.py` 红（`guide.marker_missing`，exit 1）→ 还原 → 绿；临时改动 block 一行 → 红（`guide.drift`，exit 1）→ 还原 → 绿；记录输出。

## 3. 恢复 AGENTS.md block + 撤销 relabel

- [x] 3.1 用 `python3 openspec/governance/check_project_architecture.py --render-guide` 渲染 block，加回 `deep_research_harness/AGENTS.md` 的 `## Structural Authority` 节（path-free 措辞；`check_harness_dependency_direction.py` 与 `check_change_guidance.py` 均绿，证明不违反 PRS-009）。
- [x] 3.2 `architecture-policy.md` 撤销上一 change 的三处 relabel（Authority 表行 / Synchronized Changes 第 3 步 / generated block 段），恢复原始描述（`git diff` 归零，policy == reality）。

## 4. 收口

- [x] 4.1 在 `req-registry.yaml` 登记 `PRS-021: project-structure — ...`（apply 正式登记；planning 只 reserve）。
- [x] 4.2 `python3 openspec/governance/check_project_gate.py --phase plan --change restore-agents-structure-locator` 通过（退出码直测）。
- [x] 4.3 `python3 openspec/governance/check_project_gate.py --phase closeout` 通过（退出码直测）。
- [x] 4.4 `openspec validate restore-agents-structure-locator --strict` 与 `git diff HEAD --check` 通过（退出码直测）。
- [x] 4.5 记录 gitlink 证据（`git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status`）；`deerflow/` 零改动，指针未变 `66b9e7f2`。
