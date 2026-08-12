# Alignment Audit 30 - OpenSpec Governance And Historical Residue

> 审计日期: 2026-08-12
> Git 快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 核心问题: `openspec/config.yaml` 的设计思想是否仍适配 V2，治理门禁是否保护真实边界

返回[总览](alignment-audit-00-current-state.md)，整改步骤见
[50 - Remediation Roadmap](alignment-audit-50-remediation-roadmap.md)。

## 结论

`openspec/config.yaml` 不是整体过时。其 authority 模型和 change focus 思想是当前有效
设计；历史残渣集中在 **V1 物理拓扑**：它继续把根 `backend/`、`frontend/` 当成
DeerFlow upstream mirrors，而 V2 根目录真正的上游边界是 `deerflow/` git submodule。

这段残渣已经扩散到 guide、Charter、policy、7 份 main specs、结构清单和 README，
并导致架构检查对不存在目录空扫描后通过。故它不是文案洁癖，而是保护对象错误。

## 仍然成立的治理思想

以下 `openspec/config.yaml` 内容与当前仓库一致，应在迁移时保留：

- `:18-30`：approved main specs 定义 required behavior；code、typed contracts、tests
  与 runtime authority 定义 current fact；未知与 proposal 不得伪装成现状。
- `:24-27`：`project-structure.toml` 是结构 inventory；Agent Charter 只指导 design
  / admission，不创造 runtime behavior、authority 或 permission。
- `:38-55`：change 从一个 primary module / causal owner 开始，只在提出具体 interface、
  authority、compatibility 或 observed-failure question 后扩大相邻范围。
- `:57-84`：Focus Card、closed seam classification、conditional policy reviews、
  lowest responsible deterministic evidence seam 等规则与当前 DRC main spec/checker 一致。
- `operations` guidance 明确是 advisory，不执行 command、不完成 task、不授予 archive
  authority；当前 Charter 的 authority line 也已存在。

因此整改不应重写 OpenSpec 哲学，只需迁移其 physical boundary model，并补足能验证该
模型的 detector。

## 当前物理事实

仓库自己的权威边界是：

```text
deep_research_harness/   downstream product, owned and mutable here
openspec/                downstream design/governance authority
_backlog/                task and plan ledger
deerflow/                gitlink 160000 @ 66b9e7f2, leverage only, never modify
```

证据：

- 根 `AGENTS.md:3-25,42-46` 明确上述两层模型。
- `git ls-files --stage deerflow` 返回 mode `160000`、commit
  `66b9e7f21212490cf92fafac137542b9deb06615`。
- 根目录没有 `backend/` 或 `frontend/`。
- `deep_research_harness/pyproject.toml:64-65` 正确依赖
  `../deerflow/backend/packages/harness`。

注意：不应为了验证这个边界去扫描或理解 DeerFlow 源码。需要保护的是 gitlink/path/
diff 边界，而不是把 submodule 纳入 downstream architecture inventory。

## Findings

### A-001 - P1 - V2 上游物理边界仍是 V1 叙述

#### 直接残渣

`openspec/config.yaml` 有三处直接错位：

- `:6-9`：称根 `backend/` / `frontend/` 是 upstream DeerFlow mirrors；
- `:63`：proposal 必须声明不修改这两个目录；
- `:82`：archive 前要求保持这两个目录 clean。

相同模型被复制到：

- `deep_research_harness/AGENTS.md:3-7`
- `openspec/agent-charter/charter.md:6-13`
- `openspec/policies/local-context.md:48-54`
- 7 份 main specs、26 次路径 token occurrence：
  `deep-research-agent-charter`、`demo-pipeline`、`deployment-configuration`、
  `evaluation-hardening`、`hitl1-node`、`local-configuration-profiles`、
  `project-structure`
- `openspec/governance/project-structure.toml:16`：
  `forbidden_source_roots = ["backend", "frontend"]`
- `deep_research_harness/README.md:53-56`：Quick Start 要求 sibling harness 在
  `../backend/packages/harness`，与 `pyproject.toml` 实际路径不一致。

并非所有包含单词 `backend` 的 spec 都是错误。例如 persistence backend、database
backend 是领域术语；整改必须只迁移作为**根路径/上游镜像**的引用，不能盲目全局替换。

#### 历史来源

`git blame openspec/config.yaml:3-10` 显示旧边界来自 V2 scaffold commit：

```text
33c0db53 2026-08-08 chore: scaffold V2 - app content from V1 + deer-flow(ethan) submodule
```

之后仅有两次相关修改：

- `40cbf448`：加入 cognitive-program-first seam discipline；
- `6efd6d26`：flatten agent charter policy topology。

两次都未迁移 lines 6-9，所以这是有 Git 来源的迁移残渣，不是当前有意采用的双上游
布局。

#### 影响

- change author 被告知保护不存在目录，却未被 config 明确要求保护真实 gitlink。
- README 的安装前置条件会把使用者导向不存在路径。
- main specs 把旧拓扑固化为 required behavior；只改 config 会继续留下相互矛盾的
  current authority。
- `backend/` / `frontend/` 将来意外出现时，读者还可能误以为它们是合法 upstream
  mirror，而不是 topology drift。

#### 修复边界

一个 OpenSpec change 应同步迁移 config、guide、Charter/policy、上述 main specs、
structure manifest、README 与 detector tests。不要逐文件零散修词，否则在迁移中间会
形成新的权威冲突。

### A-002 - P1 - 上游边界门禁存在空扫描假绿

`check_project_architecture.py:714-733` 的 upstream-import 检查逻辑是：对 manifest
中的每个 `forbidden_source_root` 调用 `_python_files(root / upstream_root)`，再检查其
Python import。当 `root/backend` 和 `root/frontend` 不存在时，迭代为空，不产生错误，
于是门禁报告：

```text
Architecture governance passed
```

这条绿色结果只证明“两个不存在目录内没有 Python import downstream”，没有证明：

- 当前 `deerflow` 路径仍是 gitlink；
- gitlink commit 是否被意外变更；
- downstream change 是否包含 `deerflow/` 内的 diff；
- 是否意外生成新的根 `backend/` / `frontend/` topology；
- closeout 记录是否检查真实 upstream boundary。

#### 正确的保护模型

在不探索 DeerFlow 源码的前提下，门禁应至少验证：

1. 根 `deerflow` 存在且在 Git index 中 mode 为 `160000`；
2. downstream structure manifest 不把 `deerflow/` 当 source root 或 required-path
   inventory 扫描；
3. 普通 Deep Research change 的 declared diff/closeout 范围不得包含 `deerflow` gitlink
   或 submodule worktree 修改；若未来真要升级 submodule，必须由单独明确批准的 boundary
   change 拥有；
4. 根 `backend/` / `frontend/` 不应被描述为 upstream mirrors，必要时可显式禁止它们
   作为新的 downstream source roots；
5. detector fixture 必须证明错配 manifest 或缺失/非 gitlink `deerflow` 会失败，避免
   再次出现空扫描通过。

这不是建议把 `deerflow/` 源码纳入 AST scan；那既违反仓库边界，也把 upstream
implementation details 变成 downstream governance 负担。

## 为什么现有绿色检查没有发现残渣

| 检查 | 实际检查内容 | 为什么没发现 |
| --- | --- | --- |
| `openspec validate --specs --strict` | OpenSpec artifact 结构和 requirement/scenario 语法 | 不判断路径是否存在或跨 spec 语义是否真实 |
| `check_project_specs.py` | Purpose/Requirements/req header 与少量历史 regex | active terminology regex 不包含 V1 root topology |
| `check_project_architecture.py` | manifest 路径、layer/import 等结构规则 | upstream import rule 对不存在目录空迭代 |
| `check_agent_charter.py` | Focus Card、policy lookup、conditional record shape | 不判断 config/Charter 中 upstream path 的现实性 |
| closeout task rule | 要求记录指定目录 clean | 指定的仍是不再存在的旧目录 |

因此 `doctor: healthy`、49/49 strict 和 architecture passed 都是真实结果，但它们的证明
范围比“OpenSpec 思想没有历史残渣”窄。

## A-008 的治理关联

OpenSpec context/Charter 的 “choose one policy” 与 comma-separated 多 policy 的机械合同
也有错位，但不属于上游拓扑残渣。详见
[20 - Context / A-008](alignment-audit-20-context.md#a-008---p2---charter-index-的-policy-基数错位)。

## 最小完成条件

治理迁移完成后应能同时回答“什么是上游”和“门禁如何知道”：

- config、root/local guides、Charter/policy、main specs、manifest、README 对根物理布局给出
  同一个答案；
- 正常 `make verify` 通过；
- 将 fixture 中 `deerflow` 从 gitlink 模型改成普通 directory/missing，focused detector
  必须 red；
- 给普通 change 注入 `deerflow` gitlink/diff 变更，closeout detector 必须 red；
- 任何检查都不需要读取 DeerFlow 源码内容。
