# Proposal: split-project-structure-manifest

## Change Focus

- **Primary module / causal owner:** `openspec/governance/project-structure.toml` 与 `openspec/governance/check_project_architecture.py` —— 结构 registry 的 shape 与其 loader（PRS-004 要求的精确可枚举结构权威 + PRS-009 的「exact inventory 单一权威」措辞）。
- **Seam classification:** deterministic-guardrail — 语义决策是「manifest 从单文件扁平清单拆为契约 + 按 owner 折叠的清单文件，且 checker 对 (path, kind, owner) 集合与「必须存在」断言保持逐字等价」；无认知责任、无产品运行时行为。
- **Question:** `project-structure.toml` 1343 行中 ~1280 行（96%）是 256 条扁平 `[[required_paths]]`（每条重复 `kind`/`owner`，去规范化），`[imports]`/`[node_packages]`/`[guide]` 等真正的结构规则被清单淹没，违反渐进式披露；如何在不削弱「每个登记文件必须存在、owner 必须是注册 PRS id」等任何机械断言的前提下，把契约与清单拆开并按 owner 折叠？
- **Necessary adjacent/external contracts:** `openspec/specs/project-structure/spec.md`（第 4 行 `> structure:` 引用与 PRS-004/PRS-009 中「exact inventory SHALL remain only in project-structure.toml」的单一文件措辞）；`openspec/governance/architecture-policy.md`（authority 表与 Synchronized Changes 第 2 步的单文件措辞）；`openspec/config.yaml`、`openspec/README.md`、`openspec/change-guidance/README.md`、`openspec/change-guidance/local/deep-research.md`（指向「该 toml 是唯一精确清单」的指针措辞）；`openspec/tests/governance/test_project_gate.py` 与 `deep_research_harness/tests/contract/test_live_architecture_contract.py`（manifest 拷贝/构造的负例夹具）。
- **Evidence seam:** `check_project_architecture.py`（全量 + 拆分后 (path, kind, owner) 集合与原扁平清单等价的确定性契约断言）+ 负例走查（删任意登记文件 / 乱 owner / 漏登记新清单文件 → 红）+ `check_project_gate.py --phase plan/closeout` + `openspec validate --strict`。
- **Not in scope:** 产品运行时行为；`deerflow/`；`make verify`；`check_doc_hygiene.py`（独立 doc-layer 门禁，不动）；`[guide]` 机制与 AGENTS.md 生成块（渲染不依赖 required_paths，内容不变）；`[imports]`/`[node_packages]` 的语义。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

`openspec/governance/project-structure.toml` 是 PRS-004/PRS-009 反复锚定的「唯一精确可枚举结构权威」，但它把两种读者、两种变更节奏塞进一个文件：真正的结构规则（root、所有权层、import 方向、node 包语法、gitlink 锁、guide 标记）只有 ~58 行，其余 ~1280 行（96%）是 256 条扁平 `[[required_paths]]` 三元组。每条 path 重复写 `kind`（filesystem 已知道）与 `owner`（几乎由所在目录/包决定），每新增一个文件 +5 行。想读「domain→engine 的 import 方向」的人必须滚过 256 条机械路径，`[imports]`/`[node_packages]` 反而埋在清单中段。这违反渐进式披露：高信号的规则被低信号清单淹没，清单也没有按 owner 折叠。`_backlog/plans/project-structure-manifest-split.md` 记录了完整方案对比（拆分 + 折叠 vs 目录派生 / owner 并入 registry / 生成式清单），本 change 按推荐方案实施。

## What Changes

- `openspec/governance/project-structure.toml`：移除全部 `[[required_paths]]`（~1280 行），保留契约（header + `[upstream_gitlink]`/`[package]`/`[fixture_imports]`/`[ignored_paths]`/`[imports]`/`[node_packages]`/`[guide]`），新增 `[inventory]` 表（`path = "openspec/governance/required-paths.toml"`）声明清单文件位置。文件从 1343 行降到 ~60 行。
- 新建 `openspec/governance/required-paths.toml`：清单按 owner 折叠为 `[paths.<PRS-XXX>]` 分段，段内 `files = [...]` / `directories = [...]`。256 条 (path, kind, owner) 语义不变，约 ~300 行。
- `openspec/governance/check_project_architecture.py`：`load_manifest` 读契约文件 + 经 `[inventory]` 加载清单文件，把 `[paths.<id>]` 段展开回 `RequiredPath` 集合；保留全部既有校验（路径规范化/唯一/kind/owner∈requirement_ids∧registered/禁入 upstream root/非空/ignored file 已登记/每条必须存在）。`render_guide_block`/`_validate_guide`/`--render-guide` 不动（不依赖 required_paths）。
- `openspec/specs/project-structure/spec.md`：PRS-004 与 PRS-009 措辞从「仅 project-structure.toml」改为「manifest = 契约文件 + 清单文件」；`> structure:` 引用保持在契约文件。
- 治理文档指针：`architecture-policy.md`、`config.yaml`、`openspec/README.md`、`change-guidance/README.md`、`change-guidance/local/deep-research.md` 同步「清单位于两文件」措辞。
- 测试/夹具：manifest 拷贝/构造点同步（新增 required-paths.toml 进隔离副本；负例夹具改构造分组清单）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `project-structure`: **PRS-004** —— 结构 registry 的精确清单从单一 `project-structure.toml` 扩展为契约文件 + 清单文件两件套，checker 机械保持 (path, kind, owner) 集合与「必须存在」断言等价；**PRS-009** —— 「exact inventory SHALL remain only in …」措辞改为 manifest 两文件（契约 + 清单），其它契约指针链接到 manifest 而非单文件。

## Impact

- 代码：`openspec/governance/check_project_architecture.py`（load_manifest 增 INVENTORY_RELATIVE + `[inventory]` 校验 + 分组清单展开，~40 行改动）。
- 结构：`openspec/governance/project-structure.toml`（-~1280 行）；新建 `openspec/governance/required-paths.toml`（~300 行）；两文件都登记为 required path（owner PRS-004）。
- 文档：`openspec/specs/project-structure/spec.md`（PRS-004/PRS-009 delta）、`architecture-policy.md`、`config.yaml`、`openspec/README.md`、`change-guidance/README.md`、`change-guidance/local/deep-research.md`。
- 验证门：`check_project_architecture.py`（全绿 + 负例红）、`check_project_gate.py --phase plan/closeout`、`check_project_reqs.py`、`openspec validate --strict`、`git diff HEAD --check`（退出码直测）。
- 不动：`deerflow/`、`make verify`、`check_doc_hygiene.py`、AGENTS.md 生成块、req-registry.yaml（无新 requirement）。
