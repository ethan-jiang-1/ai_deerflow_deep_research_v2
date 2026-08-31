# Plan: doc gate 扩到 docs/ 层 + fresh-agent 生命周期叙事 —— CLS-056 的两个收尾

> 类型: 设计 | 更新: 2026-08-31
> 前序: [`agent-legibility-feedback-hardening.md`](../_done/_closed_plans/agent-legibility-feedback-hardening.md)（CLS-056，同源于 `/Users/bowhead/deepseek-harness/_faq_on_digested/07_borrowing-harness-idea/`）
> 落地方式: **1 个 OpenSpec change** + 1 个 `_backlog` todo；prose 修复已按账本纪律提前执行（见落地关联）。

## 一句话目标

CLS-056 关闭时把文档门禁的范围**故意**限定在 entry-chain（archived design.md Decision 5），
这留下一个已被现实击中的盲区；同时 FAQ 里唯一没被借走的「叙事层」（fresh-agent worked
example）仍是新人最大的词汇税。本 plan 只关这两件事，沿 CLS-056 的成本纪律：
**只有「新的可机器执行结构」才开 change，修 prose 走账本。**

---

## 背景 / 现状

### 缺口 A：doc gate 的 docs/ 层盲区（有现行漂移做铁证）

- `check_doc_hygiene.py` 的三条规则（ADR index ↔ 目录、entry-chain 相对链接、UTF-8/尾换行）
  只扫描 `ENTRY_DOCS` 6 个入口文件。`deep_research_harness/docs/` 下 9 个文档**不设防**。
- **现行证据**：commit `54886b8`（"separate portable practice from product context"）按 PRS-009
  删掉 `docs/runtime-architecture.md` 指向 `project-structure.toml` 的相对链接，但**只删链接
  没重写句子**，留下悬空片段（"The canonical machine-readable structure registry is /"）。
  门禁对此照绿——盲区不是假设，已经漏过一次。
- 门禁自身机制健康：`--self-test` 负例控制已存在（archived design.md Decision 4），本次是
  **扩展范围**，不是新建门禁。

### 缺口 B：叙事层缺失（词汇税）

- `CONTEXT.md` 以约 60 个术语做到「一词一 owner」（CLS-056 体检已判 ✅），但 fresh agent
  建立生命周期心智模型仍需反复回读：`Run Refinement` / `Refinement Continuation` /
  `Correlated Research Response` / `Accepted Profile Note` 的区别散在定义里，缺一条时间线。
- FAQ 语料自己的范式是 *follow-a-fresh-agent*：跟随一个新参与者走完第一个任务。本仓对应物
  是一篇**run 生命周期 worked example**。这是 prose 工作 → 账本 todo，不开 change。

### 已排除（不翻案）

| 项 | 排除理由 |
|---|---|
| CLAUDE.md 改 symlink | CLS-056 已裁定 `@AGENTS.md` import ✅，且 import 契约被 `check_change_guidance.py` 机器守护 |
| 悬空句检测（dangling-prose checker） | 本质是语义判断，不可机械化；硬造只会产出永绿假门禁（违反本仓「无造假断言」纪律） |
| 接入 `make verify` | application-independent 铁律（`check_harness_dependency_direction.py` 是回归锚） |
| 任何 `deerflow/` 改动 | submodule 只读 |

---

## 决策 / 方案

### 载体 1：OpenSpec change `doc-gate-docs-layer`（propose 时加日期前缀）

- **Primary owner**：`openspec/governance/check_doc_hygiene.py`（扩展）+ 其 registry 行（PRS-020 拥有者同步）
- **Seam classification**：`deterministic-guardrail`——语义决策是「docs/ 层的哪些漂移类被机器拒绝」，无认知责任
- **任务序列**（check items 全绿才进下一任务）：
  - **T1 · docs/ 层纳入扫描**：新增 `DOC_LAYER_DOCS` 常量（`deep_research_harness/docs/*.md`
    显式枚举或 glob + 排除表；先全量跑一遍看真实失败面再定清单，不盲扩）。
    套用既有相对链接/UTF-8/尾换行三规则。**不做** ADR 规则（无 adr 目录冲突）、
    **不做** line budget（归 `check_change_guidance.py`）。
  - **T2 · `--self-test` 扩展**：新范围内每条规则补一条植根违规的负例控制
    （坏链接 → 红 → 还原；坏编码 → 红 → 还原）。
  - **T3 · 收口**：governance README 导航行同步；`check_project_gate.py --phase plan`、
    `UV_OFFLINE=1 make verify`、`openspec validate --strict`、退出码直测。
- **引例义务**：change 的 Why 部分引用 `54886b8` 悬空句作为「本门禁本该拦住的类」的证据
  （链接已删所以链接规则拦不住它；它修复后，同类**未来**漂移——docs 层坏链接/坏编码——被 T1 拦住）。
  诚实边界：悬空句这个**类**本身不可机械化，本 change 不假装能拦它。
- **Not in scope**：产品运行时行为、ADR 规则、line budget、`make verify`、叙事文档内容。

### 载体 2：`_backlog` todo `todo-run-lifecycle-walkthrough.md`

- 在 `deep_research_harness/docs/` 写一篇 **run 生命周期 worked example**：
  一个 bundle 从 `start` → HITL1 → topic planning → waves → HITL2 → 终态 →
  `refine`（文本方向）→ textless continuation 走一遍；每个 `CONTEXT.md` 术语在它登场的
  那一步标注（首次出现加粗 + 指向 CONTEXT.md 锚点）。
- **纪律**（防它变成第二权威）：文件头声明 reader projection / 非权威（同节点 `workflow.md`
  的措辞）；事实只 link owner（`../CONTEXT.md`、`runtime-architecture.md`）；**path-free
  于 OpenSpec**（PRS-009）；不引入新术语。
- 从 `deep_research_harness/AGENTS.md` Information Map 挂一行链接（「生命周期怎么走 → 此文」）。

### 拆分原则（复用 CLS-056 的结论）

> 「引入一个新的、可被机器执行的结构/政策」才开 change；「写/改文档、修 prose」走 `_backlog` 账本。

---

## 风险 / 取舍

- **[不可机械化规则的诱惑]** 悬空句检测是语义问题。→ 只修 prose；门禁只扩可机械的类（链接/编码），并在 change 里写明这个诚实边界。
- **[docs 层误伤]** `docs/` 含生成文件（topology）与带日期基线文件（live-evaluation-baseline、release-attestation.json）。→ T1 先全量跑看失败面，显式枚举 + 排除表进常量；JSON 不在扫描范围。
- **[叙事层变成第二权威]** walkthrough 一旦写「规则」就违反 one-fact-one-home。→ 文件头 reader-projection 声明 + 只 link owner + 不造新词；这层暂无机器守护，靠 review 纪律，如实承认。
- **[PRS-009 越界]** harness docs 不得 link OpenSpec 内容。→ 悬空句修复与叙事文档全部 path-free（修复已按此措辞执行）。
- **[范围蔓延]** change 只动一个 checker 的范围常量与 self-test；`make verify`、ADR 规则、budget 均显式 Non-Goal。

---

## 落地关联

- [x] **2026-08-31 已执行（账本级，无需 change）**：修复 `docs/runtime-architecture.md`
  悬空句为 path-free 措辞（"declared by the owning `project-structure` specification"）。
- [ ] OpenSpec change `doc-gate-docs-layer`：propose → polish → apply → archive（T1–T3）。
- [ ] `_backlog/todos/todo-run-lifecycle-walkthrough.md` 建立 → 完成后移 `_done/_done_todos/`。
- **关闭条件**：change 归档 + todo 完成移入 `_done`；届时本 plan `git mv` 至
  `_done/_closed_plans/`（届时领 CLS-057），三处 README 同步。
