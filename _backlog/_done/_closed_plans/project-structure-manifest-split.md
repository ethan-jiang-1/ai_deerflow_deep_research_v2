# Plan: project-structure.toml 拆分与折叠（渐进式披露）

> 类型: 设计 | 更新: 2026-08-25

## 背景 / 现状

`openspec/governance/project-structure.toml` 现在 1338 行（~35KB），是本仓「唯一精确可枚举结构权威」（PRS-004）。拆开看：

| 段 | 行 | 占比 | 内容 |
|---|---|---|---|
| 结构契约（header + `[upstream_gitlink]` / `[package]` / `[fixture_imports]` / `[ignored_paths]` / `[imports]` / `[node_packages]`） | 1–41, 1047–1063 | ~58 行（4%） | 真正的「架构规则」：root、所有权层、import 方向、节点包语法、gitlink 锁 |
| `[[required_paths]]` 清单 | 42–1046, 1065–1338 | ~1280 行（96%） | 256 条 `path`/`kind`/`owner` 三元组 |

问题不在「规则太多」，而在**两种读者、两种变更节奏被塞进同一个扁平数组**：

1. **读规则的人**（想搞懂 `domain → engine` 的 import 方向、node 包必须有哪些文件）必须滚过 256 条机械路径；`[imports]`/`[node_packages]` 反而被埋在清单中段（1050–1063 行）。
2. **清单本身是去规范化的**：每条 path 重复写 `kind`（filesystem 已知道是文件还是目录）与 `owner`（几乎由所在目录/包决定）；每新增一个文件就 +5 行扁平 TOML。

这违反渐进式披露：高信号的「规则」被低信号的「清单」淹没，清单也没有按 owner/目录折叠。

## 决策 / 方案

**推荐：拆分（A）+ 按 owner 折叠（B）一步做**，同时保留 checker 的全部强制语义（校验的 (path, kind, owner) 集合与「必须存在」断言一字不变）。

- **A. 拆成两个文件**
  - `project-structure.toml` 保留 ~58 行结构契约，新增一个指向清单的键（或 checker 约定加载同级清单文件）。
  - 新建 `required-paths.toml`（清单）。
  - 效果：读规则 → 58 行文件；读清单 → 清单文件。
- **B. 清单按 owner 折叠**
  - 扁平 `[[required_paths]]`（path/kind/owner）改为 `[paths.<PRS-XXX>]` 分段，段内 `files = [...]` / `directories = [...]`。
  - 256 条 → ~256 行 path 字符串 + 19 个 owner 段头 ≈ 300 行。
  - `owner` 变段键（不再逐条重复）；`kind` 变 files/directories 两个数组（不再逐条写）。
  - checker 解析逻辑改（结构变了），校验语义不变。

**结果**：契约文件 58 行（-96%），清单文件 ~300 行（-76%）；总量 1338 → ~358 行（-73%），且「读规则」路径从 1338 行降到 58 行。

### 备选（考虑过，本次不选）

| 方案 | 思路 | 为什么不这次做 |
|---|---|---|
| C. 目录 root + 派生 | 只登记目录 root + 默认 owner，checker 走目录派生「必须存在」集合 | 改变「每个登记文件必须存在」的精确语义，需重新设计门禁强度 + 负例控制；是语义变更，不是纯瘦身 |
| D. owner→path 并进 req-registry.yaml | 去掉 required_paths 的 owner 字段，所有权只留在 registry 散文 | 丢失 checker 现有的「owner 必须是注册 PRS id」机械交叉校验；registry 散文不可机读；省不了几行 |
| E. 生成清单（manifest-as-code） | 紧凑源 + 脚本生成全量清单 | 256 条规模引入生成步骤/漂移风险，过度设计 |
| F. 只重排不瘦身 | 同文件内按目录重排 | 不解决长度，纯化妆，不选 |

## 风险 / 取舍

- [拆分触及「结构权威」契约本身] → self-referential 变更：`spec.md` 第 4 行 `> structure: …project-structure.toml` 与多处「exact inventory SHALL remain only in project-structure.toml」要随 delta 改成「契约文件 + 清单文件」两处；checker 的 `SPEC_REFERENCE` 逐字节匹配同步改。
- [新清单文件本身也是被治理路径] → 必须在清单里把 `required-paths.toml`（owner PRS-004）与 `project-structure.toml`（owner PRS-004，现有 883 行条目）都登记为 required file，否则 checker 报 `path.missing` 自我否决拆分。
- [checker 解析重写引入回归] → 用现有负例 + 新增「拆分后 (path, kind, owner) 集合与原扁平集合等价」的契约测试兜底（red-green）。
- [owner 折叠改变可读顺序] → 原清单近似按路径/区域排序，改为按 owner 分段；「这个路径属于谁」更直接，但「按目录浏览」退化。缓解：段内按路径排序；清单顶部放「区域 → owner」速查注释。
- [大量散文文档断言「仅在此 toml」] → 一次性更新 nav/authority 措辞（见下），避免留下「单一权威在单文件」的过时断言。

## 落地关联

实施走 `openspec/changes/`（建议 change 名 `split-project-structure-manifest`），不在 `_backlog` 直接改。必须同步的触点：

- **核心**：`openspec/governance/project-structure.toml`（拆）+ 新建 `openspec/governance/required-paths.toml` + `check_project_architecture.py`（loader 读两文件、解析 `[paths.<id>]` 分段）。
- **spec**：`openspec/specs/project-structure/spec.md`（via delta：改 `> structure:` 引用 + 「only in project-structure.toml」措辞）。
- **治理文档**：`openspec/governance/architecture-policy.md`（authority 表 + Synchronized Changes 第 2 步）、`openspec/governance/README.md`（nav 表）、`openspec/config.yaml`（第 18 行「exact structural inventory」）、`openspec/README.md`（第 17 行）、`openspec/change-guidance/README.md`（第 33 行）、`openspec/change-guidance/local/deep-research.md`（第 39 行）。
- **测试/夹具**：apply 时 grep 全仓对 `project-structure.toml` 的拷贝/构造点逐一核对（当前已知 `openspec/tests/governance/test_project_gate.py` 的隔离 temp 副本机制、`deep_research_harness/tests/contract/test_live_architecture_contract.py`）。
- **收尾**：跑 `check_project_architecture.py` + `check_project_reqs.py` + `check_project_gate.py` 全绿再归档。
