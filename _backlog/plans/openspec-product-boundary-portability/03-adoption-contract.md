# 跨项目采用与分发契约

> 角色：V1 portable artifact、目标仓库责任、adoption evidence 与成功定义的唯一权威  
> 前提：内容边界以 [`02-boundary-and-file-matrix.md`](02-boundary-and-file-matrix.md) 为准

## 适用范围

V1 面向具有以下特征的 sibling product：

- 使用 OpenSpec 管理 behavior changes；
- 是 DeerFlow 或 LangGraph 风格的 node-centric agent workflow；
- 至少有一个 deterministic decision boundary；
- 可以有 LLM-bearing node、human decision 或 recovery flow，但不要求三者全部存在；
- 拥有自己的 product terminology、specs、code/tests、project structure 和 requirement namespace。

V1 不承诺适用于任意软件项目，也不要求目标产品采用 Deep Research 的 module layers、node grammar、
fixture recipe 或 evaluation model。

## 分发形态

V1 是 **target-owned template snapshot**：

1. 采用 change 固定一个 source repository 和 commit；
2. 按 allowlist 复制 portable files；
3. 记录每个复制文件的 digest；
4. 复制后由目标仓库拥有，不自动跟随 source；
5. 升级必须由目标仓库另开 change，重新选择 revision、检查 diff 并证明兼容。

V1 不发布 package、submodule、generator、远程 include 或自动同步服务。两个真实产品多次出现相同
升级摩擦之前，不创建跨仓 versioning contract。

## Export Allowlist

只有以下 target 拓扑中的文件可进入 portable snapshot：

| 单元 | Source path | 采用规则 |
| --- | --- | --- |
| Kernel prose | `openspec/change-guidance/core/**` | 必须全部复制且 byte-identical |
| Workflow-control profile | `openspec/change-guidance/profiles/workflow-control/**` | 启用该 profile 时全部复制 |
| Node-agent profile | `openspec/change-guidance/profiles/node-agent/**` | 项目存在 LLM-bearing node authoring surface 时独立启用 |
| DeerFlow downstream profile | `openspec/change-guidance/profiles/deerflow-downstream/**` | 仅 DeerFlow downstream 产品选择 |
| Pure validator | `openspec/governance/change_guidance_kernel.py` | 必须复制且 byte-identical |

Portable snapshot 不携带 source project 的 `@impl` annotations。Source 与 target 各自在 local
wrapper/tests 中绑定自己的 requirement IDs。

## Export Denylist

以下内容不得通过 V1 snapshot 传播：

| 类别 | 例子 | 目标仓库做法 |
| --- | --- | --- |
| Product context | `product/README.md`、Deep Research glossary | 新写自己的 product front door 与 terminology route |
| Required/pending behavior | `specs/`、active changes、archive | 新写自己的 specs/changes；source archive 不复制 |
| Local authoring composition | `openspec/config.yaml`、`change-guidance/README.md` | 组合 target profiles、paths 和 local obligations |
| Project governance data | `project-structure.toml`、`req-registry.yaml` | 按 target topology/IDs 创建 |
| Local checker wrapper | `check_change_guidance.py` | 写 target wrapper 并调用相同 kernel |
| Project checkers | architecture、req/spec/coverage checkers | 由 target 决定是否需要并自行拥有 |
| Runtime/product material | code、tests、prompts、ADRs、operator docs | 不从 source 模板化 |
| Requirement identity | `DRC-*`、`PRS-*`、`EVH-*` | target 分配自己的 namespace |

不得先复制整个 `openspec/` 再删除 denylisted 内容；这种方式无法证明 export boundary 本身正确。

## Snapshot 完整性

采用 evidence 必须记录：

- source repository 与 commit；
- allowlisted 相对路径；
- selected profiles；
- 每个 portable file 的 SHA-256；
- target commit；
- local files 的清单；
- portable files 在 adoption diff 中是否被修改。

Core、selected profiles 和 kernel validator 任一文件被本地编辑，adoption 即不满足 V1 success。
需要补充的 target 规则放入 local composition；若必须改变 portable semantics，则把它记录为 source
portability finding，并在仍 active 的 Source Program Change 中修正、发布新 candidate。

每个 portable Markdown link 必须指向同一 allowlist 内、且随所选 profile 一起复制的文件，或是纯
文本的 target-local owner role；portable prose 不得硬链接 source product/config/spec/local paths。
因此 target 不需要为了修链接而编辑 portable files。

## Target-Owned 文件

目标仓库必须自己拥有以下 composition：

| Target surface | 必须回答 | 不能复制 |
| --- | --- | --- |
| `openspec/product/README.md` | 产品价值、terminology/spec/current-fact/governance owner routes | Source product prose |
| `openspec/README.md` | Native、product、guidance、governance 的阅读入口 | Source project path inventory |
| `openspec/config.yaml` | Authoring truth order、enabled profiles、local Focus/review obligations、verification route | Source product names/commands |
| `change-guidance/README.md` | Enabled profiles、canonical policy names 与 triggers | Disabled profile 或 source-local policy |
| `change-guidance/local/**` | Target module map、budgets、Program Focus 或其他本地扩展 | Portable rule 的改写副本 |
| `governance/check_change_guidance.py` | CLI、filesystem binding、enabled set、local fields/budgets | Product-independent validation logic |
| Target specs/changes | 自己的 required/pending behavior | Deep Research requirements |
| Target structure/ID governance | 自己的 paths、imports、gitlinks、IDs | Deep Research manifests/IDs |

## Local Binding 最小契约

V1 不规定统一 TOML/YAML schema。Target wrapper 与 authoring routes 必须共同回答：

1. product front door 在哪里；
2. core 和 enabled profile 文档在哪里；
3. enabled profiles 是否完整且彼此组合无冲突；
4. proposal 可选择哪些 canonical policies；
5. 哪些 local fields、review records、entry docs 和 budgets 额外生效；
6. project structure authority 在哪里；
7. 本地 deterministic verification entry 是什么。

第 6 项只能给 owner link，不能复制 source/test/import/gitlink 字段。第 7 项由本地 Makefile或等价
入口拥有；portable validator 不执行 shell command，也不把 command 当通用配置。

## Profile 选择语义

Profile 使用两道门：

1. **Project enablement**：local composition 声明该 profile 可用，并提供完整 docs/checker binding；
2. **Per-change trigger**：proposal 只有在真实 changed surface 命中 trigger 时才选择具体 policy。

| Profile | Project enablement 条件 | Per-change trigger 示例 | 不表示 |
| --- | --- | --- | --- |
| workflow-control | 项目有状态、失败、恢复、human decision 或 participant outcome | retry、terminal、state writer、human action、control placement 发生变化 | 已批准某个 retry/route/state |
| node-agent | 项目允许 LLM-bearing workflow nodes | cognitive role、tool posture、candidate admission、repair/model classification 变化 | 每个 node 都调用模型或已有 recovery policy |
| deerflow-downstream | 项目以 DeerFlow public API 作为上游 boundary | change 涉及 DeerFlow interface、gitlink 或 upstream compatibility | 可以读取或修改 upstream source |

Profile 文本、review table、product page 和 `openspec/config.yaml` 均不能授予 model invocation、
tool permission、state write、graph route 或 recovery behavior。

## Adoption 流程

目标仓库按以下顺序采用：

1. 建立一个 adoption evidence boundary：优先创建一个 target-native Program Change；否则登记将被
   复用的 active changes，或由 target decision owner 批准最小 bounded change set。共同声明 source
   revision、selected profiles 和 non-goals。
2. 先建立 target 自己的 product front door、specs/changes baseline 与 structure owner。
3. 按 allowlist 复制 kernel、selected profiles 和 pure validator，保存 digests。
4. 编写 target local router、config、wrapper 和必要 local policies；不编辑 portable files。
5. 增加 core-only、enabled-profile、disabled-profile 和 local-binding fixtures。
6. 优先在一个 target-native Program Change 中完成三类真实 workstream；若 target 不支持 program
   form，则复用已经 active、且会按 portable practice 实际执行的真实 changes，或由 target decision
   owner 批准最小 bounded change set，并运行 target 自己的 deterministic verification。历史 archive
   只能提供背景或 counterexample，不能证明 adoption。
7. 写 adoption evidence，列出所有 local files、deviations、negative proofs 和 unresolved limitations。
8. 只有全部 success criteria 通过，才把 source revision 标记为该 target 的 adopted snapshot。

## 真实 Sibling Adoption Spike

Sibling product 必须与 Deep Research 至少在以下四项明显不同：

- 产品目标和 glossary；
- application root、package/test root；
- module ownership 或 node package shape；
- requirement namespace 与 verification command。

若 target 使用 DeerFlow，仍不得修改上游源码。若 target 只使用 LangGraph，可不启用
`deerflow-downstream`。

必须由同一个 adoption evidence boundary 覆盖三类 workstream：

| Workstream | 必须证明 |
| --- | --- |
| Deterministic validation workstream | Core 能选出 owner/evidence，且不强迫 node-agent review |
| LLM-bearing node workstream | Node-agent profile 能闭合 cognition、tool enforcement、candidate admission、failure bound 与 proof |
| Human decision / recovery workstream | Workflow-control 能闭合 typed decision、authority、recovery、terminal disposition 与 legal next action |

这三个 workstreams 使用 target 自己的 specs、code、tests 和 IDs。优先不拆分；若 target-native
ownership 无法在一个 Change 中合法表达，则最小拆分必须由 target decision owner 批准，并在 adoption
evidence 解释每个 owning scope。复用的 active Change 必须在其原 owning scope 内真正使用新 practice，
不能事后只补一张 review 表。不能在 source repo 内用假 runtime 目录模拟。

## 合成 Fixture 的职责

机械 fixtures 必须覆盖：

- 中性 product/path/package 能通过；
- core-only 项目不需要 profile 文件或 review records；
- 两个独立 profiles 的 triggered policies 同时适用却只提供一份 review 时失败；
- disabled 或 unknown policy 被选择时失败；
- triggered review 缺列、重复或 posture 非法时失败；
- product/local path 不存在、越出 repo 或角色重复时失败；
- portable source 出现 source product literal、path 或 requirement ID 时失败；
- local wrapper 缺少 enabled profile 文档时失败。

Fixtures 不证明 policy 的领域适用性、agent 能否选对 semantic owner 或 target runtime behavior；
这些由真实 spike 和 target executable evidence 负责。

## Adoption Evidence

Target adoption change 在 `evidence/portable-practice-adoption.md` 记录：

| 字段 | 内容 |
| --- | --- |
| Source | repository、commit、snapshot date |
| Export | allowlisted paths、profiles、file digests |
| Target | repository、adoption change set、每个 owning commit |
| Local composition | 新建或修改的 target-owned files |
| Kernel integrity | portable files 是否 byte-identical |
| Representative workstreams | 三类 workstream 的 owner、trigger、evidence 与结果 |
| Negative proofs | 每个 boundary 的 planted violation 与恢复后通过证据 |
| Deviations | 任何无法自然映射或需要 source correction 的事项 |
| Decision | accepted、needs-source-fix 或 rejected |

Source release closeout 必须引用 target repository、target commit 和该 evidence；不能只引用口头结论。

## 成功定义

同时满足以下条件才算 adoption success：

- portable files 与 source revision digest 一致；
- target 只启用真实需要的 profiles；
- target product README 能路由到自己的 terminology、specs、current facts 和 governance；
- target 使用自己的 specs、IDs、structure policy、code/tests 和 verification；
- 三类代表性 workstream 均闭合；
- core、profile dependency、local binding 和 export neutrality 均有 planted negative；
- target 不含 Deep Research glossary、Run Bundle、layer map 或 requirement IDs；
- adoption 不需要修改 DeerFlow upstream；
- evidence 中没有未关闭的 kernel fork 或 authority conflict。

以下任一情况即失败：

- 必须编辑 kernel 或 selected profile 才能接入；
- 复制了 source specs/registry/architecture guard 后再删改；
- product README 成为 runtime/spec/structure authority；
- disabled profile 仍产生义务；
- 只用合成 fixture 宣称成功；
- target 的 local wrapper 与 structure/spec owner 形成第二份事实来源。

## 后续升级

升级时，target 新建 change，对比旧 revision 与新 revision 的 portable allowlist，重新：

- 审核 profile dependency 和 local wrapper compatibility；
- 运行所有 mechanical fixtures；
- 至少重放受影响的代表性 workstream/evidence seam；
- 更新 provenance 与 digests。

Source 不对 target 自动推送。未来若建立 package/generator，必须另行定义 version、consumer
inventory、rollback、deprecation 和 release authority；不由 V1 隐含承诺。
