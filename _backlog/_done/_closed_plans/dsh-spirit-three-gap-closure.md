# DSH Harness 精神借鉴 · 三个 GAP 的落地计划

> 2026-09-27 | 来源：DSH harness FAQ（deepseek-harness 仓 `_faq_on_digested/07_borrowing-dsh-harness-idea/`）
> 与本仓十维对照的 GAP 分析。**借鉴精神，不照搬机制**——已就位的八成不动，本计划只收拢剩下三个文档层 GAP。
>
> **定位**：plan = 分析与取舍记录。三项实施均为 docs/guidance 改动，不走 OpenSpec change（判据见 §过程判定）；
> 结论被吸收后按 `_backlog/plans/README.md` ritual 关闭。
>
> **落地记录（2026-09-28）**：经用户拍板改走 OpenSpec 主干，载体 change `close-agent-guidance-doc-gaps`
> （skip_specs：纯指引内容，零 delta），已归档于
> `openspec/changes/archive/2026-09-28-close-agent-guidance-doc-gaps/`。GAP 1 相对草稿有一处偏离：
> 独立 `## Mechanism Ladder` 表改为 Application Focus 折叠列——module guide 行数预算 `>=120` 行即
> 常驻告警而现值 119 行，零新行折叠列达成同一验收；理由与备选取舍见该 change 的 design.md。
> 三个产物已落地并过全部门禁（hygiene/self-test、change-guidance、closeout gate、`make verify`），结论被
> change 吸收，本 plan 关闭。
>
> **边界铁律**：`deerflow/` 是 submodule，只 import、绝不修改；本计划任何一环都不触碰它
> （仓库 AGENTS.md 不可谈判 #2）。三项改动全部落在应用侧自有文件。

---

## 背景：十维对照的结论（为什么只做这三个）

DSH FAQ 的十维里，本仓已就位且不动的：变更闭环（OpenSpec 主干 + 新鲜回执 + UNVERIFIED 标注）、
归属（根路由 + owner 表 + `check_doc_hygiene` 机器兜底）、决策记录（ADR 四态 + 取代纪律 + 负知识节）、
入口链（根 router + 字符预算棘轮 + `@import`）、反馈（checker 家族 + mutation-check 负例控制 + test-changed）、
执行链/披露/查询（框架或宿主职责，按压力才建——正确地没建）。

剩下的三个 GAP 共同点：**事实都已在，缺的是显式化**——缺一张表、一张地图、一份对照单。
全部是"写文件"的工程，零架构依赖，且都有现成的机器检查兜底。

---

## GAP 1 · 影响半径阶梯（paved-road ladder）显式化

### 病根

现有两张路由表各管一轴：Application Focus 表回答"**归谁管**"（决策类型 → owner 层），
LLM-Node Gate 回答"**是不是模型的事**"（四类 surface 分类）。缺第三轴：
**同一类行为改动，先试哪个机制、什么时候才许升级**。DSH 的对应教训：乱发挥的典型形态就是
"本可用 L0 配置表达，却一路爬到 L3 改核心"。本仓语境的失败故事：某节点重试/超时行为不对——
`config.yaml` 里 models 已有 `timeout`/`max_retries`、`profiles/` 有四档 profile，
agent 却直接钻进 `graph/nodes/` 或 `engine/` 写死分支，影响半径从一行配置放大到全局行为。

### 落点与理由

- **落点**：`deep_research_harness/AGENTS.md`，Application Focus 表之后新起一节 `## Mechanism Ladder`。
- **为什么在 resident 层**：这张表的价值在"选机制之前就看见"，必须进每轮必读的入口文件。
- **为什么不放 `openspec/change-guidance/`**：应用 AGENTS.md 声明不依赖治理框架、不能反链；
  且 change-guidance 现有内容不同轴（`core/change-practice.md` 的 Change Admission 管"要不要走
  OpenSpec 流程"，`local/deep-research.md` 的 Context Expansion Gate 管"上下文扩展"）——
  不构成第二权威。
- **预算**：当前 7335 / 上限 8200（`check_doc_hygiene.DOC_BUDGETS`），余量 865 字符。
  草稿实测 667 字符（含节标题与表体），粘贴后 ≈8004 / 8200、余量 ≈196——满足本计划
  "≥100 余量"验收；实施当日以实测为准，**不动棘轮、不上调上限**。

### 产物草稿（实施时按此粘贴，可再收紧）

```markdown
## Mechanism Ladder

Pick the lowest layer that expresses a behavior change; escalate only on the stated
condition. Config and profiles are app-owned (`config.yaml`, `profiles/`).

| First try | Typical change | Escalate when |
| --- | --- | --- |
| `config.yaml` / `profiles/` | models, tools, retries, toggles | config cannot express it |
| `agents/policies.py`, `middleware.py` | tool/budget posture, repair bounds | a new deterministic gate is needed |
| `graph/nodes/` (`NODE_SPEC`) | add a node, reroute phases | a contract-level change is needed |
| `domain/` / `engine/` | typed contract, invariant, admission semantics | top of ladder; spec-level decision |
```

### 验收

1. `python3 openspec/governance/check_doc_hygiene.py` → exit 0（预算/链接/编码全绿）；
2. 预算数字：`wc -m deep_research_harness/AGENTS.md` 后仍在 8200 内且留 ≥100 余量；
3. 自测法（DSH 05 的检验）：拿一个真实症状（如"某节点对慢 provider 超时"）只看这张表，
   能答出"先试 L0 config/profile，不行才 L1 policy"——答不出就是表没写对；
4. 阶梯不是审批流程、不是价值排序（L3 不比 L0 高级，只是影响半径大）——写成升级条件，
   不写成申请步骤。

---

## GAP 2 · 持久层四层地图（静与动分界显式化）

### 病根

静/动分界的**事实**已全在，但分散在五处：规则层走 PR（仓库 AGENTS.md）、配置层
`config.yaml` + `profiles/`（显式 profile-check）、事实源 Run Bundle 单写者（ADR-0028 与
runtime-architecture 的 State, Content, And Nodes 节）、派生只读观测（Projections And
Observations 节）、"模型可见 ⟺ 可重建"（runbooks 030/031 的 checkpoint+journal 无推断回放 +
`make prompt-dump-check`）。没有一张地图把这些接起来，新 agent 要自己拼；
拼错的症状就是 DSH 04 说的三样：同事实两处存真、回放不出来、会话决定不回写。

### 落点与理由

- **落点**：`deep_research_harness/docs/runtime-architecture.md`，新增 `## Persistence Layers`
  一节，**放在 Projections And Observations 之后、Source And Structural Contract 之前**
  （它链接的两个锚点都已在上方）。
- **该文件在 `DOC_LAYER_DOCS` 内但无字符预算**（仅链接/编码/scope 检查），体量无压力。
- **走形防线（最重要）**：这一节必须是**链接地图，不是第二权威**——每行只放"层 + 速度 +
  owner 指针 + 边界一句话"，不复制 Run Bundle 契约正文。DSH 02 的检验法照用：
  删掉链接以外的复制正文，信息应当不丢；丢了说明在越权复读，立即改回链接。

### 产物草稿

```markdown
## Persistence Layers

Four layers by change speed; each faster layer derives from the slower one and never
writes back except through the owner's explicit action. This is a map, not a second
authority — each row links to its owner.

| Layer | Change speed | Owner / authority | Boundary |
| --- | --- | --- | --- |
| Rule/map | per PR | repo guides and [ADRs](adr/README.md) | not mutable during a run |
| Config | deploy time | root `config.yaml` + `profiles/` | explicit profile check; mismatch fails loud |
| Fact source | append-only | Run Bundle: State, checkpoints, journal (single-writer) | see Harness And Run Bundles above |
| Derived | per read | reports, projections, diagnostics | rebuildable; no second truth |

Disciplines, each already enforced elsewhere:

- Derived observations stay read-only and cannot authorize, resume, or reconstruct a
  Bundle (see Projections And Observations above).
- Model-visible ⟺ reconstructable: Node Context Snapshots and `make prompt-dump-check`
  pin what a node actually received; the debugger replays from checkpoint and journal
  without inference (runbooks 030/031).
- Durable facts chosen mid-session return to their owner — Bundle State, config, or a
  new ADR; a session log is never an authority.
```

### 验收

1. hygiene checker 绿（链接/编码）；
2. 同文件小节引用用纯文本（"see … above"），避免裸锚点的检查盲区——实施时若改用
   markdown 链接，必须确认 checker 对 `#anchor` 的处理后再定；
3. 复读自测：本节不含任何 Run Bundle 契约的复述正文；
4. 不新建任何机制——三条纪律的 enforcement 全部指向已有 owner，本节只做导航。

---

## GAP 3 · runbook/skill 写法对照单（低优先级，顺手做）

### 病根

runbooks 的实践已经很好（每步命令、固定问题、001→004 升级序列、命名规则），
但写法标准只活在已有文件的示范里；下次新写 runbook 的 agent 没有对照单，
容易滑向 DSH 11 说的两个病：散文病（"做好验证"式步骤）和清单病（12 步锁死判断）。

### 落点与理由

- **落点**：`deep_research_harness/docs/runbooks/README.md`，紧跟命名规则行
  （`📐 手册命名规则固定为 runbook-00X-难度-用途.md`）之后，新增一小节。该文件无字符预算。
- 六条里四条是现有实践的显式化，只补两条缺的：guidance 声明、机械部分下沉 target。

### 产物草稿

```markdown
### 写新 runbook 的对照单

- 开头一句话写"何时用这份"（触发条件），再写前置与花费；
- 每一步给可执行命令或可打开的入口，不写"做好验证"式散文；
- 判断标准写成规则（如"固定问题 = 受控环境"），不写形容词；
- 可机械判断的部分指向真实 make target / checker，不抄成散文步骤；
- 文末声明：本手册是 guidance，不是 checklist，机械部分由对应 target 把关；
- 新增后在本 README 索引加一行（hygiene checker 校验 docs 层链接与编码）。
```

### 验收

hygiene checker 绿；下一份新 runbook 交付时按此对照（那时才真正验收）。

---

## 过程判定

- **不走 OpenSpec change**：三项均为 navigation/operational guidance 文档，不产生运行时行为、
  不改契约语义（test-evidence-policy 权威表把 AGENTS.md 正文定义为 "Authoring bootstrap,
  navigation, commands, and concise operational guidance"）。阶梯是对现有 ownership 的编码
  （engine 拥有 gate、config 拥有旋钮——均已是现状），不引入新的规范语义。
- **停下来问人的条件**：实施中若发现阶梯与某条现行 spec/ADR 冲突（例如某能力配置层与
  engine 均声称拥有），那是规范语义裁决 → 按不可谈判 #1/#5 停下交人，不自行裁决。
- **评审**：属"文档一致性/导航"类 → 自主 review 后直接交付（不可谈判 #5）。

## 证据与回执

交付前记录新鲜回执（命令 + 退出码 + revision）：

```bash
python3 openspec/governance/check_doc_hygiene.py --self-test   # 期望: self-test passed（负例控制，既有守卫）
python3 openspec/governance/check_doc_hygiene.py               # 期望: doc-layer hygiene passed.（exit 0）
git rev-parse HEAD
```

不改任何被 `make verify` 覆盖的运行面，全量 verify 不需要；窄证据即 hygiene checker。

## 不做清单（刻意分歧，按不可谈判 #4 留痕）

- **不建**：执行链管线进应用（loop 归 deerflow/LangGraph）、注入预算/compaction（宿主职责）、
  capability seam 全家桶、双语 hash 配对、inspect 工具（`prompt-dump` 管 prompt 面、
  `profile-check` 管 profile 面；若将来出现"猜生效配置"症状，最小补丁是一条
  effective-config dump 命令——DSH 12 的最便宜一档——仍不是 inspect 工具）。
- **不加**嵌套 AGENTS.md（本仓禁令保留，per-node `workflow.md` projection 是更贴的等价物）。
- **不上调**任何 doc budget 上限（棘轮语义不动；GAP 1 草稿已按余量内设计）。
- **不改** `deerflow/` 任何文件。

## 执行纪律（投资方向纠偏，2026-09-27 用户提醒）

历史教训在 git 里可查：`6471163`（frame project as harness）、`f1b0305`（governance land
tech-debt leftovers）、`5f15b99`（root AGENTS.md 115→53 行，owners carry the rules）、
CLS-056/057（上次借同一份 DSH FAQ，产物全在 harness 层）。密度对比（截至 `16d869a`）：
`src/`+`tests/` 占 384 个提交中的 154（40%），AGENTS/openspec 约束层仅 94（24%）——打扫卫生时顺手落成代码、
少碰 harness 关键文件（入口 MD、openspec 约束/门禁、指引层），投资方向反了。
本计划实施与今后同类工作执行：

1. **只动 harness 层**：本计划三项交付全部是 MD/约束文件；实施中发现的任何代码问题
   （哪怕一行能修）一律记 `_backlog` bug/todo，不顺手修。
2. **每项落完问一句**：这条规则的家在哪？owner 文件、openspec 约束、门禁要不要同步——
   缺家先补家，再谈代码。
3. **默认次序**：打扫类任务的缺口先判层——指引/约束/门禁层能表达的不动代码；只有代码
   own 的事实才动代码，且交付必须携带对应 harness 层回写（规则的家、ADR 或门禁），
   否则下个会话原样再犯。

## 关闭条件

三个产物合入 + hygiene checker 全绿 + 回执记录在案 → 按 plans ritual `git mv` 至
`_done/_closed_plans/` 并更新三处索引。GAP 3 的最终验收挂在下一份新 runbook 上，
可在 plan 里注明"随下次 runbook 交付复核"后先关。
