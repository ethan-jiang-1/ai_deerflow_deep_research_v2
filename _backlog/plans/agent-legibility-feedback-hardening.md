# Plan: 借用 DSH Harness 思路 —— 让 fresh coding agent「不糊涂、不乱发挥」的渐进加固

> 类型: 设计 | 更新: 2026-08-25
> 落地方式: **1 个 OpenSpec change** + 2 个 `_backlog` todo。change 只包「新的可执行门禁」，其余走账本。

## 一句话目标

本仓库已经是「borrowed harness」的深度实践者——入口链、正确路径、可执行反馈、Skills、
ADR、运行时查询都已存在。所以这不是从零搭 DSH，而是**用 DSH 的「三问 + 六缺口」做一次诚实
体检，只关真实缺口**；并且承认 **change 很贵，所以只开 1 个 change**：把 DSH 最值钱、本仓
最缺的一环——「文档层机器门禁 + 负例控制」——接到执行。其余全是账本 todo 或明确不做。

---

## 背景 / 现状

### 借用源（只读参考，不在本仓）

`/Users/bowhead/deepseek-harness/_faq_on_digested/07_borrowing-harness-idea/` 三条可迁移结论：

1. **「不糊涂」靠外置，不靠聪明** —— 一个事实一个 owner；当前事实与决策理由分开；负知识也要有 owner。
2. **「不乱发挥」靠正确路径 + 早失败，不靠自律** —— 先问归属再实现；每条可机械判断的规则配一个 `exit non-zero` 命令，并证明负例会失败。
3. **照搬顺序 + 边界** —— 先立规矩 → 铺正确路径 → 接可执行反馈；插件图 / invariant / 运行时 inspect 是「组合压力」的产物，普通项目跳过。

判断 Development Harness 的**三问**：规则住在哪里？正确入口明确吗？错误何时被发现？

### 本仓现状（已确认）

| 机制 | 本仓对应物 | 状态 |
|---|---|---|
| 入口链 | 根 `AGENTS.md`(201 词) → `deep_research_harness/AGENTS.md`(764 词) → `CONTEXT.md`(术语 owner) → `docs/` → `openspec/specs/` | ✅ |
| CLAUDE.md 分流 | 根与 harness 均 `@AGENTS.md` import | ✅ |
| 正确路径 | Application Focus 表 + LLM-Node Authoring Gate + `change-guidance/` 三 profile | ✅ 强 |
| 可执行反馈 | `make verify` + `openspec/governance/` 6 checker + `check_project_gate.py` + red-before-green | ✅ 强 |
| 决策理由 | `docs/adr/`（28 条） | ⚠️ 缺发现层（G1） |
| 术语 owner | `CONTEXT.md`（`product/README.md` 明确） | ✅ |
| 运行时查询 | `doctor.py` / `demo-sessions inspect` / `render_topology.py` / `prompt_dump.py` | ✅ 大部分 |
| Skills | `.agents/skills/` + 全局 grillme | ✅（宿主已做 catalog 摘要/正文 on-demand） |
| 工作账本 | `_backlog/`（bugs/todos/plans + `_done/`） | ✅ |

### 三问打分（体检基线）

| 问 | 现状 | 最痛例子 |
|---|---|---|
| 规则住在哪里？ | 大多已外置到 AGENTS.md / specs / checker | 但「人类文档层」（AGENTS.md/CONTEXT.md/README/adr）**无机器兜底**，外置了却会漂（G3/G4） |
| 正确入口明确吗？ | Application Focus + change-guidance 已明确 | 基本达标，无需新 change |
| 错误何时被发现？ | 编译/测试/CI 已覆盖；文档错误无门禁 | 文档漂移要等 review——杠杆最高、本仓最缺的一档 |

---

## 体检结论：四个缺口，但只有一个是「change 级」

| 缺口 | 内容 | 处置 |
|---|---|---|
| **G1** | `docs/adr/` 无 README/index、无生命周期状态、负知识散落 | **进 change**（index 是门禁要校验的数据） |
| **G2** | 运行时查询已有，缺一条 canonical 指针（等价 `--dump-config` 的一句话承诺） | **todo**（一行，无需 change） |
| **G3** | 文档层无 `exit non-zero` 门禁 + 负例控制 | **change 的核心**（唯一 change 级缺口） |
| **G4** | `architecture-policy.md` 声称有「generated locator block + registry markers」，但 toml/checker/AGENTS.md 三处都不存在 | **进 change**（门禁要写「one home」就得先把它钉死） |

---

## 成本现实：change 是贵的，所以只开 1 个

上一版按 Phase 数开了 7 个 change，是本计划最大的浪费。重新按「这事的**语义决策**是什么」归因：

- G1（ADR 索引）、G4（一行 prose 修正）**本身不是新行为**，它们是门禁要校验的**数据/前置**；
- G3（verify 脚本 + 文档层政策）**才是新的可执行结构**——新 checker + 它 enforce 的 policy，这是唯一需要 spec/registry/closeout 门的东西；
- G2 是一行指针；skill 路由宿主已做，**不做**。

于是三个缺口（G1/G3/G4）共享同一个因果 owner（**开发 harness 的文档层**）和同一个 seam（**确定性门禁**），
塌缩成**一个 change**，G1/G4 作为它的任务，G3 是它的产出。G2 降级为 todo。

**拆分原则**（此后复用）：*「引入一个新的、可被机器执行的结构/政策」才开 change；「写/改文档、补索引、修 prose」走 `_backlog` 账本，因为它独立于 OpenSpec。*

---

## 落地总览

| 载体 | 内容 | 量 |
|---|---|---|
| **OpenSpec change** `dev-harness-legibility-gate` | 文档层门禁：政策 + `check_doc_hygiene.py` + ADR index/lifecycle/负知识 + 坐实 G4 | **1** |
| **`_backlog` todo** | G2 canonical 运行时查询指针（一行） | 1 |
| **`_backlog` todo** | 修 `_backlog/plans/README.md` 陈旧索引（`openspec-product-boundary-portability.md` 缺文件 / `tui-interactive-campaign-progress.md` 未索引）——本身就是 G3 的活样本，顺手修并留作门禁的引例 | 1 |
| **明确不做** | skill 路由索引（宿主已做）、运行时 inspect 工具、invariant、插件图、任何 `deerflow/` 改动 | 0 |

---

## 单一 change：`dev-harness-legibility-gate`

> 提议时加日期前缀（如 `2026-08-26-dev-harness-legibility-gate`）。planning 阶段不 reserve ID、不写 registry。

### Change Focus（草稿）

- **Primary module / causal owner:** `openspec/governance/doc-hygiene-policy.md`（新，文档层政策）+ `openspec/governance/check_doc_hygiene.py`（新，确定性校验器）
- **Seam classification:** `deterministic-guardrail` —— 该 change 的语义决策是「什么算文档层卫生、怎么被机器拒绝」，是确定性门禁；无认知责任、无产品运行时行为
- **Question:** 开发 harness 的文档层（AGENTS.md / CONTEXT.md / README / docs/adr）如何从「只有 prose 约定、漂移等 review 才发现」，变成「有 `exit non-zero` 门禁 + 每规则负例控制」？
- **Necessary adjacent/external contracts:** `architecture-policy.md`（G4 漂移在其 15/75–80 行）；`project-structure.toml`（仅当选「实现 generated block」时）；`docs/adr/`（index 是校验数据）
- **Evidence seam:** `check_doc_hygiene.py` 自身 + 每规则负例测试（引入回归 → 红 → 还原）
- **Not in scope:** 产品运行时行为、`make verify`（保持 application-independent）、`deerflow/`、运行时 inspect 工具、invariant
- **Triggered review policies:** change-admission

### 内部渐进任务（check items 全绿才进下一任务）

#### T1 · 坐实 G4：prose 不再声称不存在的机器事实

- 二选一：(a) 实现 generated locator block（registry 加 markers + `check_project_architecture.py` 校验 + AGENTS.md 生成 block）；或 (b) 把 `architecture-policy.md` 相关段标注 future plan。**默认选 (b)**（一行，零风险）。
- **Check items：**
  - [ ] 三种 grep（toml marker / checker 引用 AGENTS.md / AGENTS.md block）变为一致：要么三处都实现，要么 policy 明写「future plan」
  - [ ] 不新增结构性路径，不动 `project-structure.toml`（选 b 时）

#### T2 · ADR 发现层 + 负知识（门禁要校验的数据）

- 写 `docs/adr/README.md`（索引：编号/一句话结论/状态）+ 给 28 条 ADR 加生命周期状态头（current / superseded / rejected / archived）+ 负知识索引（「为什么不走 X」）。
- **Check items：**
  - [ ] 读一条 ADR 能答「为什么这样定、什么方案输了、后果是什么」
  - [ ] agent ≤10s 靠 index 定位 owner ADR，不翻目录
  - [ ] 至少一条「rejected/负知识」可被引用，agent 不再反复提已否决方案
  - [ ] index 与目录一致（无孤儿、无缺项）——这一条正是 T4 要机器校验的

#### T3 · 文档层政策写进 governance

- 写 `openspec/governance/doc-hygiene-policy.md`：word budget（根 AGENTS.md ≤ N、harness AGENTS.md ≤ N、CONTEXT.md ≤ N）、一事实一 owner（不重复 standing rule）、入口链完整、ADR index 与目录一致、相对链接/锚点有效。数字以「某文件为准」钉基线。
- **Check items：**
  - [ ] 每条规则可机械判断（能被 T4 脚本拒绝），没有「靠感觉」的条款
  - [ ] 预算/数字标注「以基线文件为准」，不写「以当前 checkout 为准」

#### T4 · 写 `check_doc_hygiene.py` + 负例控制（核心）

- 标准库零依赖、repo 根运行、与现有 6 个 checker 并列；每规则负例控制。
- **Check items（硬指标）：**
  - [ ] 每条规则都做过负例控制：引入回归（坏链接/重复规则/超预算/孤儿 ADR）→ 脚本变红 → 还原
  - [ ] 反馈指明「失败对象 + 违反规则 + 修正入口」，不是一句「检查失败」
  - [ ] **不接进 `make verify`**（Harness gate 保持 application-independent，`check_harness_dependency_direction.py` 仍绿）

#### T5 · 收口

- [ ] `openspec/governance/README.md` 增一行导航
- [ ] 归档前门：`python3 openspec/governance/check_project_gate.py --phase plan --change <name>` → closeout；`cd deep_research_harness && UV_OFFLINE=1 make verify`；`openspec validate <name> --strict`；`git diff HEAD --check`
- [ ] 每个退出码直测（不用 `| tail` 管道吞上游非零）
- [ ] 若 change 引入新 requirement ID，由 apply 任务登记 `req-registry.yaml`（planning 只 reserve）

---

## 两个 todo（不经过 OpenSpec）

- **T-a（G2）**：在 `deep_research_harness/README.md` 或 `deep_research_harness/AGENTS.md` Information Map 补一条 canonical 指针：「想知道这台机器实际 boot 的 profile/recipe → `make profile-check PROFILE=<name>` / `python -m scripts.doctor`」，并标注「opt-in 开发工具，非安全边界」。一行，做完即勾。
- **T-b**：修 `_backlog/plans/README.md` 陈旧索引。这本身就是 G3 的活样本——在 T2/T4 里作为「门禁本该拦住」的引例引用它。

---

## 风险 / 取舍

- **[过度建设]** 本仓已有 6 checker + program form + profiles，再叠加 plugin/invariant/inspect 是负收益。→ 缓解：明确不做清单 + 只开 1 change。
- **[门禁方向]** 若把 `check_doc_hygiene.py` 误接进 `make verify` 会违反 application-independent 铁律。→ 缓解：T4 显式 check item + `check_harness_dependency_direction.py` 作回归锚。
- **[change 边界]** 一个 change 装 G1/G3/G4，风险是变 unbounded。→ 缓解：主 owner 唯一（文档层政策 + checker），G1/G4 是数据/前置，T1–T5 是封闭任务序列；若 review 发现 G4「实现 generated block」路径膨胀，立刻回退到 (b) 一行修。
- **[四个边界]** 可读≠简单、Skill≠enforcement、清理≠回滚、查询≠安全沙箱——内嵌于各 check item。

---

## 附：推进检查表（change 内任务之间 + 归档前的「门」）

- [ ] 上一任务 Check items 全绿才进下一任务
- [ ] 重跑三问，三档无退步（外置没回流人脑 / 入口没变猜代码 / 错误发现位置没后移）
- [ ] 无造假断言（无永绿的检查、无空 invariant 凑数）
- [ ] `deerflow/` 零改动（submodule 只读铁律）
- [ ] 归档前走完 T5 的统一收尾门，退出码直测
