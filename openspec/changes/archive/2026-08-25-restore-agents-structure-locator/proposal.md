# Proposal: restore-agents-structure-locator

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_project_architecture.py` 与 `deep_research_harness/AGENTS.md` —— 恢复被 `54886b8` 误删的 canonical structure locator（PRS-004 要求的 marker-bounded generated block 及其渲染/freshness 机制）。
- **Seam classification:** deterministic-guardrail — 语义决策是「generated locator 重新从 registry 确定性渲染、并被 freshness 校验拒绝漂移」；无认知责任、无产品运行时行为。
- **Question:** 主 spec（PRS-004）要求 `deep_research_harness/AGENTS.md` 中的 canonical structure locator "SHALL ... be rendered from the registry"，且其场景要求 "validation finds no hand-maintained conflicting path inventory"；该机制在 `54886b8`（portability 重构）被整体删除（AGENTS block + `render_guide_block`/`_validate_guide`/`--render-guide` + registry `[guide]` 表），如何完整恢复并重新纳入机器强制？
- **Necessary adjacent/external contracts:** `architecture-policy.md`（撤销上一 change 的 "future plan" relabel，恢复对 generated block 的原始描述——恢复后该描述重新为真）；`project-structure.toml`（恢复 `[guide]` 表：`path`/`begin_marker`/`end_marker`）。
- **Evidence seam:** `check_project_architecture.py --render-guide`（确定性渲染）+ 恢复的 `_validate_guide` freshness 校验（marker 缺失/重复/与 registry 不一致 → `guide.*` 非零）+ 负例走查（删 block / 改 block → 红 → 还原）。
- **Not in scope:** 产品运行时行为；`make verify`；`deerflow/`；`check_doc_hygiene.py`（独立 doc-layer 门禁，不动）；不动 PRS-004 的既有文本（新增 PRS-021 单独拥有 checker 的强制行为）。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

`deep_research_harness/AGENTS.md` 的 "Canonical Structure Locator"（`<!-- BEGIN/END GENERATED: PROJECT-STRUCTURE -->` 包裹的 generated block）在 commit `54886b8`（"refactor(openspec): separate portable practice from product context"，即关掉 portability plan 的同一 commit）被整体删除，同时被删的还有整套机制：`check_project_architecture.py` 的 `render_guide_block()`、`_validate_guide()`（marker 恰好一次 + freshness 比较）、`--render-guide` CLI，以及 registry 的 `[guide]` 表。但主 spec（PRS-004 及其 "Generated locator follows the registry" 场景）一直要求它，`architecture-policy.md` 也一直描述它。这是回归：spec-required 机制被误删且无机器拦截。本 change 完整恢复该机制，让 freshness 校验重新生效。

## What Changes

- `openspec/governance/project-structure.toml`：恢复 `[guide]` 表（`path = "deep_research_harness/AGENTS.md"`、`begin_marker`/`end_marker`，与 `2bbaa82` 版本一致）。
- `openspec/governance/check_project_architecture.py`：`StructureManifest` 增 `guide_path`/`begin_marker`/`end_marker`；`load_manifest` 恢复 `[guide]` 解析与校验（`begin_marker != end_marker`、`guide.path == deep_research_harness/AGENTS.md`）；恢复 `render_guide_block(manifest)`、`_validate_guide(root, manifest)`（marker 缺失/重复/漂移 → `guide.*` 非零）并在 `validate_project` 调用；恢复 `--render-guide` CLI。
- `deep_research_harness/AGENTS.md`：恢复 `## Structural Authority` 节 + marker-bounded "Canonical Structure Locator" block（由 `--render-guide` 渲染，不手写）。
- `openspec/governance/architecture-policy.md`：撤销上一 change 的三处 "future plan" relabel，恢复原始描述（恢复后原始描述重新为真）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `project-structure`: 新增 **PRS-021** —— 架构 checker 机械强制 `deep_research_harness/AGENTS.md` 中 generated structure-locator block 的存在（marker 恰好一次）与 freshness（与 registry 渲染一致），并提供 `--render-guide` 再生成入口。

## Impact

- 代码：`openspec/governance/check_project_architecture.py`（恢复 ~80 行 + `_validate_guide`）。
- 结构：`openspec/governance/project-structure.toml`（+`[guide]` 表）；`deep_research_harness/AGENTS.md`（+Structural Authority 节）；`req-registry.yaml`（apply 时 +PRS-021）。
- 文档：`openspec/governance/architecture-policy.md`（撤销 relabel）。
- 验证门：`check_project_architecture.py`（freshness 全绿 + 负例红）+ `check_project_gate.py --phase plan/closeout` + `openspec validate --strict` + `git diff HEAD --check`（退出码直测）。
- 不动：`deerflow/`、`make verify`、`check_doc_hygiene.py`。
