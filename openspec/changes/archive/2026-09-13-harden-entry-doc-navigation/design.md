# Design — harden-entry-doc-navigation

## Context

runtime/ 的 34 个文件均有高质量模块 docstring（权威边界声明 + @impl 标签），缺的是簇级索引；根目录散件大多已在别处拥有权威描述（deployment-configuration spec 管 `skills/public/`、local-operations.md 管 `profiles/`、deerflow/AGENTS.md 管 `config.yaml` 约定），缺的是根 README 的登记行；Direction Controls 的内容在 `docs/runtime-architecture.md`（Public Controls / Ordinary Controller Loading）与 owning spec `deep-research-harness-run-bundles` 中已各有一份更完整的表述。见 proposal.md — Why。

## Goals / Non-Goals

**Goals:**
- runtime/ 获得一份与 node 包 workflow.md 同级的簇级 reader index。
- 根目录首次 `ls` 的每个居民在根 README 布局表有一行去向。
- Direction Controls 从三重转述收缩为单一指针块，消除漂移源。
- 修复 RUN-010 腐烂指针与 RUN-020 跟踪矛盾。

**Non-Goals:**
- 不修改 `deerflow/` submodule 的任何文件（铁律）。
- 不改任何 `src/` 行为、不拆 runtime/ 子包、不动 project-structure registry。
- 不重写契约内容——收缩后的指针块不转述 refine/resume 规则，只指路。

## Decisions

1. **runtime/README.md 作为树内 reader index，而非 AGENTS.md 或子包拆分。**
   harness AGENTS.md 明令 "Do not add nested AGENTS.md files"；子包拆分要动 project-structure spec + registry + import，无行为收益。树内 README 有先例：`tests/assets/README.md`（"support library, not tests"）。头部沿用 COMMANDS.md 的自声明模式："只是索引，不是第二权威；权威是代码、docstring、specs 与 tests"。按挖出的 5 簇组织，每簇给：文件清单、一行职责、关键 owning spec / proof seam 指针。**为什么不用表格塞进 harness AGENTS.md**：该文件已 123 行、踩 120 行预算预警线，加行必先删行；且 runtime/ 簇结构变化频率高于 AGENTS.md 的决策表，放同层会制造同步负担。

2. **入口路由挂在 docs/README.md 的 Living References 表，而非 AGENTS.md。**
   docs/README.md 已是"人类/操作读者"的路由层且分类清晰（Living/Generated/Frozen），加一行即达；AGENTS.md 保持决策导向不膨胀。

3. **Direction Controls 收缩为纯指针块，不留转述。**
   Direction Controls 位于 `deep_research_harness/README.md`（不是仓库根 README；根 README 从未包含该节）。runtime-architecture.md 的 Public Controls 表 + Ordinary Controller Loading 节已覆盖全部内容且更权威；owning spec 是 `deep-research-harness-run-bundles`。收缩块只保留：一句话定性（"refine/resume 方向控制与 Agent 加载是 lifecycle 契约"）+ 两个链接 + spec 点名。这样该 README 从"第三份转述"降为"路由"，与仓库 "authority-and-projections" 政策一致。该文件在 `check_doc_hygiene.py` ENTRY_DOCS 管辖内，收缩后的链接会被 rule 2 自动核验。

4. **RUN-020.command 用 `git rm --cached` 对齐 ignore 规则，本地保留。**
   `RUN-*.command` 在 .gitignore:240 已声明为本地便利件；RUN-020 是规则生效前的历史提交，跟踪状态与规则矛盾。对齐后两份 launcher 定位一致（本地文件、COMMANDS.md 索引）。备选"移出 ignore"被否：双击启动器含本机路径假设，不属于可复现产物。

5. **根 README 布局块补行按"居民 → 去向"最小格式。**
   根 README 的布局是一段 fenced code block（非 Markdown 表格），补行沿用同格式，每行只答"这是什么、去哪读权威"，不转述细节：`config.yaml`/`.env` → gitignored 宿主运行时配置/凭证（宿主约定见 deerflow 自带文档，本仓只登记存在与性质）；`profiles/` → local-operations.md；`skills/public/` → deployment-configuration spec 物化产物；`RUN-*.command` → 本地启动器，COMMANDS.md 索引；`CONTEXT*.md` → 词汇边界文档。
   注意：根 README 不在 `check_doc_hygiene.py` 的 ENTRY_DOCS 管辖内（该 checker 管根/harness AGENTS.md、harness README、docs/README 等六件），所以布局块与 Direction Controls 的修改不会被 checker 保护——链接正确性由本 change 的任务级核验承担；而 `deep_research_harness/README.md` 在管辖内，2.2 新增行会被 rule 2 自动检查。

## Risks / Trade-offs

- [runtime/README.md 与代码漂移] → 头部非权威声明 + 收尾 gate（check_doc_hygiene / closeout gate）+ 簇级粒度（不列到行号/函数级），漂移面小。
- [指针块指向的 runtime-architecture 节名将来改名] → 链接走相对路径锚点，closeout gate 的链接走查任务覆盖；仓库已有 doc-hygiene 检查链接解析。
- [git rm --cached 影响依赖 RUN-020 内容的 CI/协作者] → 文件仍在磁盘且在 COMMANDS.md 有 runbook 链接说明其来源；无任何构建/测试引用 tracked 状态。
- [文档行数预算] → 根 README 净变化预计为负（Direction Controls 收缩 > 布局表新增），harness AGENTS.md 本 change 不触碰。
