# Design: split-project-structure-manifest

## Context

现状（见 proposal.md — Why）：`openspec/governance/project-structure.toml` 1343 行中
~1280 行（96%）是 256 条扁平 `[[required_paths]]`（path/kind/owner 三元组），真正的
结构契约（`[upstream_gitlink]`/`[package]`/`[fixture_imports]`/`[ignored_paths]`/
`[imports]`/`[node_packages]`/`[guide]`）只有 ~58 行，且被清单夹在中间（42–1046 与
1065–1338）。

约束（决定本设计的边界）：

- 唯一机械消费者是 `check_project_architecture.py`（stdlib-only，零外部依赖）：`load_manifest`
  读单文件，`_validate_required_paths` 只做「每条登记路径必须存在且 kind 正确」；每条路径的
  owner 必须 ∈ `requirement_ids` ∧ ∈ req-registry；`[imports]`/`[node_packages]`/`[guide]`
  的语义与校验是本 change 不可动的既有契约。
- `render_guide_block`/`_validate_guide`/`--render-guide` 不遍历 required_paths（生成块只含
  roots/layers/node grammar/命令），所以拆分不影响 `deep_research_harness/AGENTS.md` 生成块内容。
- 主 spec 已存在（`openspec/specs/project-structure/spec.md`），checker 的 `_validate_spec_authority`
  在主 spec 存在时只校验其 `> structure: openspec/governance/project-structure.toml` 引用恰好一次。
- 结构 registry 是「自我治理」对象：新清单文件必须同时登记为 required path（owner PRS-004），
  否则 checker 报 `path.missing` 自我否决。

## Goals / Non-Goals

**Goals:**

- 契约（规则）与清单（枚举）分离：读规则的人打开 `project-structure.toml` 只看到 ~60 行契约。
- 清单按 owner 折叠：256 条三元组 → `[paths.<PRS-ID>]` 分段，总量降到 ~300 行。
- (path, kind, owner) 集合与「必须存在」断言相对现状**逐字等价**：checker 全量校验不变，
  拆分前后同一仓库状态通过/拒绝结果一致。
- 全部 6 个 component checker、`openspec validate --strict`、gate plan/closeout 绿。

**Non-Goals:**

- 不引入目录派生/glob 清单（会削弱「每个登记文件必须存在」的精确语义；见决策 D1 备选）。
- 不改 `[imports]`/`[node_packages]`/`[guide]` 语义；不动 AGENTS.md 生成块；不新增 requirement
  ID（不写 req-registry.yaml）。
- 不做生成式清单（manifest-as-code）；不动 `check_doc_hygiene.py`/`make verify`/`deerflow/`。

## Decisions

### D1. 文件布局：契约保留 `project-structure.toml` 名，清单用新文件 `required-paths.toml`

- 契约（header + `[upstream_gitlink]`/`[package]`/`[fixture_imports]`/`[ignored_paths]`/
  `[imports]`/`[node_packages]`/`[guide]` + 新增 `[inventory]` 表）留在
  `openspec/governance/project-structure.toml`。
- 新建 `openspec/governance/required-paths.toml` 承载全部 `[paths.<PRS-ID>]` 清单段。
- `[inventory]` 表：`path = "openspec/governance/required-paths.toml"`，checker 校验其等于
  `INVENTORY_RELATIVE` 常量（复用 `[guide]` 的「声明 + 常量校验」模式）。
- **备选 B（反向）**：清单留在 `project-structure.toml`、契约改名 `project-structure-contract.toml`。
  不选：让「读规则」入口顶着陌生文件名，且 `[imports]` 权威文件的落点反而要改 prose；
  而 A 方案下所有既有「project-structure.toml 是 registry」指针只需要增补「+ required-paths.toml」，
  语义更直白。
- **备选 C**：不拆文件只压缩。不选：目录/owner 阅读者仍被契约与清单混排干扰，渐进式披露不彻底。

### D2. 清单 schema：`[paths.<PRS-ID>]` 分段，段内 `files`/`directories` 数组

```toml
schema_version = 1
contract = "project-structure-inventory"

[paths.PRS-001]
files = ["deep_research_harness/README.md", ...]
directories = ["deep_research_harness/src/deerflow_deep_research", ...]

[paths.PRS-015]
files = [...]
```

- `owner` 变段键（不再逐条重复）；`kind` 变两个数组（不再逐条写）；段内路径保持字典序。
- **备选 D**：保留扁平 `[[required_paths]]` 只搬到新文件。不选：省不了行数，白拆。
- **备选 E**：目录 root + 默认 owner + 覆盖表。不选：把「登记文件必须存在」变成派生规则，
  需重设计门禁强度与负例，是语义变更而非纯重构（plan 已记录，择机单独做）。

### D3. Checker：`load_manifest` 加载两文件，分组段展开回 `RequiredPath`，校验逐字保留

- 常量 `INVENTORY_RELATIVE = PurePosixPath("openspec/governance/required-paths.toml")`。
- `load_manifest`：解析契约文件（原样）→ 校验 `[inventory]` 表存在且 `path == INVENTORY_RELATIVE`
  且 `schema_version == 1` 且 `contract == "project-structure-inventory"` → 解析清单文件 →
  按文件内段序 + 段内 files-then-directories 展开为 `list[RequiredPath]`。
- 展开后复用既有全部校验，一字不改：`_relative_path` 规范化/禁 `..`/禁绝对路径、路径去重、
  kind ∈ {file, directory}、owner ∈ requirement_ids ∧ registered、禁 upstream root、
  非空、`ignored_paths.path` 必须是已登记 required file、`_validate_required_paths` 的
  「必须存在 + kind 正确」。
- 段键必须匹配 `ID_RE`（`^[A-Z]{3}-\d{3}$`），且段内 files/directories 均为非空字符串数组。
- **等价性保障**：拆分后清单展开的 (path, kind, owner) 集合与拆分前扁平清单集合完全一致
  —— apply 用脚本对拍（拆分前旧清单 vs 拆分后展开集合），并留一条确定性契约断言。

### D4. Spec/权威措辞

- `> structure: openspec/governance/project-structure.toml` 引用保持在契约文件（主 spec 原文不动，
  delta 只改 PRS-001/PRS-004/PRS-009 的措辞：引入「project-structure manifest = 契约文件 + 清单文件」）。
- 两文件都登记为 required path（owner PRS-004）：`required-paths.toml` 新增一条，`project-structure.toml`
  既有条目保留。

## Risks / Trade-offs

- [checker 解析重写引入回归] → 保留全部既有校验函数不动，只换「取数来源」（分组段展开）；apply 先写
  等价性对拍脚本 + 负例走查（删登记文件 / 乱 owner / 漏 `[inventory]` / 漏登记新清单文件 → 红）。
- [主 spec 之外还有大量散文指向单一文件] → 本 change 同步更新 `architecture-policy.md`、
  `config.yaml`、`openspec/README.md`、`change-guidance/README.md`、`change-guidance/local/deep-research.md`
  的措辞（「manifest = 契约 + 清单」），不留过时断言。
- [MODIFIED delta 携带大段 verbatim 文本，行数多] → 逐字复制 main spec 对应块再编辑；用
  `openspec validate --strict` + `check_project_specs.py` 兜底 header/场景格式。
- [owner 折叠改变阅读顺序（区域 → owner）] → 段内按路径字典序；`governance/README.md` nav 表
  增补「清单文件」行说明读法。

## Migration Plan

- 原子落地：checker 改动与清单新格式同一 commit（checker 先支持两种格式再切换会更复杂，不需要
  兼容窗口——本仓无外部消费者，gate 是确定性的）。回滚 = revert 该 commit（含删除 required-paths.toml）。
- apply 顺序：改 checker（新增 INVENTORY_RELATIVE + `[inventory]` 校验 + 分组展开）→ 用脚本从旧清单
  机械生成 `required-paths.toml`（对拍集合等价）→ 清空旧 `[[required_paths]]` → 更新 spec/治理文档措辞
  → 跑全部 checker 与负例。

## Open Questions

无。
