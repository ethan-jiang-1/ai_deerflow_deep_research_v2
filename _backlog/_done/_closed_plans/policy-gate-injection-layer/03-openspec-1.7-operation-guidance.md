# 03 — OpenSpec 1.7.0 的两个 operation guidance 时机

> 主计划：[`../policy-gate-injection-layer.md`](../policy-gate-injection-layer.md)
> 配套审查目录：[`README.md`](README.md)
> 外部借鉴：`/Users/bowhead/ai_tool_deepresearch/_backlog/plans/session-drift-guardrail-analysis/`
> 核验日期：2026-07-31
> 本文性质：设计分析与落地前验证清单；不实现 runtime，不声称当前仓库已经有 guardrail。

## 先说结论

OpenSpec 1.7.0 确实补上了本计划一直缺的两个**生命周期注入时机**，但准确名称不是两个
“自动检查器”，而是两个 operation 下的 advisory guidance：

```yaml
operations:
  apply:
    guidance: [ ... ]
  archive:
    guidance: [ ... ]
```

它们解决的是两个不同的时间问题：

| 时机 | 要把 Agent 重新拉回什么问题 | 最适合承载的内容 | 不能承载的内容 |
| --- | --- | --- | --- |
| `operations.apply.guidance` | **动手前/继续动手时**，这次 change 的计划、owner、影响面和历史反例是否仍然成立 | plan review、policy 路由、impact 线索、finding 写回 `tasks.md` 的要求 | 已执行 checker 的证明、自动写 task、阻止编辑、授予 runtime authority |
| `operations.archive.guidance` | **准备收口时**，实际 diff 是否仍在批准边界内，所有 finding/机械前提是否真的闭合 | actual-diff closeout、selected-change 边界、未完成 task 复核、回到 apply 的指示 | 语义质量 pass、替代 native archive、强制停止、证明整个 worktree 已审查 |

因此推荐的组合不是“把更多文字塞进 `config.yaml`”，而是：

```text
rules.tasks                         = 跨 session 的持久 obligation
operations.apply.guidance           = apply 事件的 plan-review prompt push
operations.archive.guidance         = archive 事件的 actual-diff prompt push
openspec/guardrails/（后续 change） = 编排 finding、fresh review、dossier 与机械 closeout
openspec/governance/                = 产生既有 deterministic checker verdict
```

一句话：**instruction 是 push channel，task 是 durable work ledger，deterministic coordinator 才能
闭合机械前提。** 任何一层都不能冒充另一层。

---

## 1. 为什么现在必须把这两个时机单独拿出来

### 1.1 原案真正想纠正的不是“少一条规则”

原案的直觉是：团队遇到问题时往往直接改 graph、gate、adapter、checkpoint 或 projection，
没有在设计阶段先问“这是认知候选、确定性事实、人工决定，还是 route/admission”。最近 BUG-001～016
的 lineage 使这个判断有了现象证据：

- BUG-001 → BUG-013：协议解析越做越精确，却把自然确认误当成 profile 字段；
- BUG-006 → BUG-007：把内部 graph route 暴露给用户选择，修文案不能修错的 authority；
- BUG-008 → BUG-010 → BUG-014：局部 timeout/retry 修好后，相邻 consumer 仍丢失共同的 provider fact；
- BUG-011：一个 broad guard 吞掉了 final-delivery 的既有 legal route；
- BUG-012 → BUG-016：有 diagnostic reference 被误当成 reference record 已发布。

这些案例并不证明“所有逻辑应该移到 prompt”，也不证明单一 policy 能消灭 regression。它们证明的
是一个更窄、也更可行动的命题：**在实现开始和收口之前，必须再次问 boundary/authority/evidence
问题；而问题的答案不能只留在作者当次 session 的聊天记录里。**

### 1.2 每个 OpenSpec change 的天然盲区

一个 change 的 proposal/spec/design/tasks 通常只描述自己。它不会自动知道：

1. 另一个 change 最近改过同一 consumer 或同一 legal route；
2. 历史 bug 已经暴露过相同的“第二套 control”模式；
3. 作者在上一次 session 中写下的担忧，下一次 session 可能完全看不到；
4. proposal 中的“预计影响”与最终实际 diff 已经发生偏移。

`rules.tasks` 可以保存跨 session 的工作，但只有在 apply/archive 时**重新把工作推回当前 Agent**，
它才会变成反馈环。因此 1.7.0 的两个 operation guidance 不是装饰性新字段，而是刚好接在
“持久 obligation 已存在、但人会遗忘”这个断点上。

### 1.3 为什么不能只用普通 `rules`

`rules` 是按 artifact id 施加的写作规则，例如 `rules.proposal`、`rules.design`、`rules.tasks`。
它回答“写这个 artifact 时必须遵守什么形式/内容约束”，不回答“某个 lifecycle operation 发生时
现在要重新做什么”。把下面这种写法当成 apply/archive hook 是错误的：

```yaml
rules:
  apply:       # 不是 OpenSpec 1.7 的 operation hook
    - "..."
  archive:     # 也不是
    - "..."
```

OpenSpec 1.7 支持的 operation id 只有 `apply` 和 `archive`，而且入口位于顶层 `operations`，字段
只有 `guidance`。这一区分要写进本计划，否则未来很容易把“artifact rule 已存在”误认为“事件已接线”。

---

## 2. OpenSpec 1.7.0 的实际契约（已核验，不是推测）

### 2.1 语法与返回形状

本地 `openspec --version` 为 `1.7.0`。CLI 的 project-config schema 和生成模板确认了如下最小
形状：

```yaml
schema: spec-driven

# context / rules 仍按原有语义工作
rules:
  tasks:
    - "把发现的后续工作写成 tasks.md 中的未完成 task"

operations:
  apply:
    guidance:
      - "在第一次 target edit 前复核当前 change 的 plan"
      - "把 actionable finding 写回 tasks.md，不要只留在聊天里"
  archive:
    guidance:
      - "以 selected change 的 actual diff 做 closeout review"
      - "未完成 finding 不得被描述为已收口"
```

两条指令会把 guidance 作为独立字段返回：

```bash
openspec instructions apply --change "<change-name>" --json
openspec instructions archive --change "<change-name>" --json
```

成功时的关键输出形状是：

```json
{
  "context": "...",
  "operationGuidance": [
    "...",
    "..."
  ]
}
```

`apply` 的完整 JSON 还包含 `contextFiles`、tasks、progress、blocked/all-done 状态和内建
`instruction`；`archive` 的完整 JSON 还包含 archive workflow 所需的 change/root context。这里的
`operationGuidance` 不能替代任何一个 CLI-controlled 字段。

### 2.2 读取时机与热更新含义

1.7.0 的 parser 在指令请求时读取 `openspec/config.yaml`，不是在项目初始化时把 guidance 固化到
change 中。因此：

- 改完 config 后，下一次 `instructions apply/archive` 会看到新数组；
- 已经开始的 Agent turn 不会被“回溯注入”，也不会在每一次文件编辑时自动再次调用 CLI；
- “每次 resumed apply 都重新提醒”是因为 apply workflow 会再次获取 instructions，而不是因为
   OpenSpec 监听了编辑事件；
- guidance 本身不会写入 proposal/design/tasks，也不会产生审查 provenance。

这正好支持“跨 session 提醒”，但不支持“跨 session 状态存储”。状态仍必须落在 `tasks.md`、
change-local dossier 或未来 guardrail-owned store。

### 2.3 解析失败与降级边界

CLI 对 `operations` 采用逐字段、尽量保留其它配置的 resilient parsing。已核验的行为包括：

| 配置问题 | CLI 行为 | 设计含义 |
| --- | --- | --- |
| 未写 `operations` | 不返回 `operationGuidance` | 这是当前仓库的现状，不代表机制失效 |
| 未知 operation id | 警告并忽略该 id | 不能用自定义 `submit`/`precommit` 名称假造第三个时机 |
| `guidance` 不是字符串数组 | 警告并忽略该 operation 的 guidance | 配置错误不能被当成已完成 review |
| 数组含空字符串 | 空项被过滤 | 不要用空项表达“有意跳过” |
| guidance 为空数组 | 省略 `operationGuidance` | 无提示与空提示等价 |
| 其它未知字段 | 警告；已知 `guidance` 仍按支持的字段读取 | 不要把 `command`、`blocking`、`runner` 等未支持字段写进去 |

更重要的是消费端边界：

- `openspec-apply-change` skill 把 `operationGuidance` 定义为 optional additive advice；它要求 Agent
  考虑每一条，但明确说这不是 task completion evidence、不能绕过 blocked state、不能取代内建
  instruction，也不是 enforceable check；
- `openspec-archive-change` skill 在 archive workflow 前尝试读取它，但把 lookup 规定为 optional；
  命令失败或 JSON 无效时继续 archive，且不应把错误报告成阻断；
- 因此 **guidance 丢失时，系统不会自动 fail closed**。如果未来需要 hard closeout，必须有独立的
  guardrail coordinator/finalizer 或 CI admission；不能把“配置里写了 hard-stop”当成实现。

### 2.4 这两个字段到底新增了什么

它们新增的是**稳定的 prompt delivery attach point**，不是新的 authority：

| 已有机制 | 能做什么 | 仍然缺什么 |
| --- | --- | --- |
| `context` | 给所有 artifact instruction 注入项目背景 | 不区分 apply/archive，不提示 change-specific closeout |
| `rules.<artifact>` | 约束某个 artifact 的写法 | 不在 lifecycle event 发生时再次出现 |
| `operations.apply.guidance` | apply 时推送 plan/admission review posture | 不执行 review、不保存 finding |
| `operations.archive.guidance` | archive 时推送 actual-diff/closeout posture | 不验证 diff、不控制 archive transition |
| `openspec/governance` checker | 给确定性结构/契约 verdict | 不编排跨 session 语义审查 |
| 未来 `openspec/guardrails` | 编排 impact、fresh challenge、dossier、closeout | 不能成为第二套 runtime state/authority |

---

## 3. 两个时机的职责必须刻意不同

### 3.1 `apply`：先审计划，再碰 target

`apply` guidance 的任务不是复述整个 policy，而是在 Agent 即将开始或继续实现时把最容易遗忘的
问题推到最前面。建议只要求以下动作：

1. 读取当前 change 的 Focus Card、相关 delta/spec、design、tasks，以及 `openspec/policies/` 中
   被触发的 policy；
2. 先回答本次 target edit 改变的是哪一个 decision：candidate interpretation、direct fact、
   evaluator、materializer、admission、route、recovery 还是 presentation；
3. 指出事实 owner、deterministic admission owner、failure owner 和最低 evidence seam；
4. 对照相似 historical bug lineage，明确“本次为什么不会重复那个错层”，或承认仍有 unknown；
5. 若审查发现了真实工作，把它追加为 `tasks.md` 中的**未完成 task**，包括 owner、最小修复和 done
   condition；然后才继续实现。

这里的“先”是 workflow posture，不是 CLI 强制顺序。若内建 apply instruction 说 change blocked、
task 不清楚或用户明确选择了其它范围，guidance 不能覆盖这些控制输入。

#### 第一次 apply 与 resumed apply

| 场景 | apply guidance 的价值 | 不应声称 |
| --- | --- | --- |
| 第一次实现 | 将原案的 boundary/authority 问题放在第一处 target edit 之前 | 已经完成 semantic review |
| 中途换 session 继续 | 从 config 重新推送 review posture，并从 `tasks.md` 恢复未决 finding | 上一次 session 的推理仍然在上下文中 |
| apply 已经 all-done | 提醒先复核 change 与 evidence，再进入 archive | 可以跳过 archive 的 actual-diff review |
| apply 被 CLI 判定 blocked | 帮 Agent 解释需要补哪个 artifact，但不能绕过 blocked | guidance 自己能解锁 change |

### 3.2 `archive`：只对实际变更做 closeout

archive guidance 不应该再开一轮没有边界的“全仓智能审查”。它要问的是：**这个 selected change
实际改了什么，是否仍符合批准的 scope，是否有未闭合 finding？** 最小闭环应包含：

1. 解析 selected change 的 `changeRoot`、approved baseline/merge-base 和 owned surface；
2. 计算 actual diff，并把 unrelated worktree 修改标为 `missing-boundary`，而不是把整个 worktree
   当成已审查；
3. 对照 proposal/spec/design/tasks，检查 scope drift、未声明 consumer、被吞掉的 legal route 和
   evidence seam mismatch；
4. 运行已有 deterministic checks（strict validation、project/charter/architecture checker、focused
   tests 等），但把它们的 verdict 与 semantic review 分开记录；
5. 将新的 finding 写回未完成 task；只要有 actionable finding，就回到 apply，而不是继续描述为
   closeout clear；
6. 只有在 boundary、task、deterministic prerequisites 都清楚时，才允许未来的 closeout coordinator
   调用受支持的 native archive transition。

`archive.guidance` 的关键是**把 Agent 的注意力绑定到 actual diff**，不是把 archive 变成一个由 prompt
决定的审批仪式。当前 skill 明确 guidance lookup 失败也继续，因此在 coordinator 尚未存在时，
这段 guidance 只能降低遗漏概率，不能提供安全级别保证。

### 3.3 为什么不能把两个时机写成同一段 checklist

同一段长 checklist 会同时犯三种错：

- apply 阶段过早要求 archive 证据，作者为了填表而不是为了做正确设计；
- archive 阶段重新讨论已批准的抽象，却没有检查实际 diff 的 scope drift；
- 两个入口都写“运行 checker/阻止归档”，最终没人知道谁拥有 transition。

因此 guidance 应短、按时机分工；深度解释留在 `openspec/policies/`，跨 session 状态留在 tasks/dossier，
确定性闭合留给 checker/finalizer。

---

## 4. `rules.tasks` 与两个 guidance 如何组成反馈环

### 4.1 `rules.tasks` 是持久 obligation，不是触发器

建议把跨 session 的最小义务写在 `rules.tasks`，例如：

```yaml
rules:
  tasks:
    - >-
      When a change triggers a review policy, tasks.md MUST retain an unchecked
      plan/closeout review task until its owner, minimal correction, and
      deterministic or bounded-evidence done condition are recorded.
```

这条 rule 的作用是让任何创建/更新 `tasks.md` 的 Agent 都看到同一要求。它**不**会：

- 自动发现 change 是否触发 policy；
- 自动创建 task；
- 自动运行 challenger/checker；
- 自动阻止 `openspec archive`。

如果现有 change 已有 tasks，迁移必须显式补入 obligation；不能假设新增 rule 会修改历史文件。

### 4.2 apply guidance 消费并产生 obligation

apply 事件的推荐顺序是：

```text
读取 apply instructions
        │
        ▼
读取 Focus Card / policy / delta / tasks / 历史 lineage
        │
        ▼
提出本次 plan review 问题
        │
   ┌────┴────┐
   │         │
无 finding   有 finding
   │         │
继续最小实现  写入 [ ] task（owner + action + done condition）
             │
             ▼
          再继续实现或暂停等待用户/后续 session
```

finding 必须指向可执行的工作，而不是“模型觉得可能不够好”。例如：

```markdown
- [ ] Review: BUG-011 lineage — verify the new guard cannot swallow the
      existing final-delivery route; owner: workflow-outcome owner; done when
      the focused negative test and route table are added.
```

这条 task 不是 semantic proof；它只是把未决问题从作者 session 搬到 change 的 durable ledger。

### 4.3 resumed apply 消费未决 finding

下一次 session 重新 apply 时，guidance 再次出现，Agent 必须先读未完成 task。正确行为是：

1. 复核 task 仍对应当前 scope，而不是机械打勾；
2. 找到 direct owner 和最低 evidence seam；
3. 完成修复并运行对应证据，或把 task 细分并明确 `limited/inconclusive`；
4. 只有 done condition 真满足才勾选；否则保留未完成并报告阻塞。

这样跨 session 的记忆来自文件和证据，而不是“上次模型应该记得”。

### 4.4 archive guidance 消费并收口 obligation

archive 事件把同一条 ledger 放回实际 diff 语境：

```text
未完成 task / 新 closeout finding
          │
          ├── 有 actionable finding ──▶ 留 [ ]，回到 apply
          │
          ├── boundary 不可信 ───────▶ 报 missing-boundary，停止声称 clear
          │
          └── 无 finding 且机械前提齐全 ─▶ coordinator/finalizer → native archive
```

在没有 coordinator 的阶段，Agent 仍可能绕过这段 advisory guidance；文档必须诚实标记为
`review-required`/best-effort，而不能写成“archive 被 policy gate 住了”。

---

## 5. 目录分层：policy、guardrails、governance 各自只做一件事

用户已经明确 policy 应位于 OpenSpec 根下的独立子目录，而不是 `governance` 内部。两个 operation
入口让这个边界更重要：config 只路由，不应成为三套正文的容器。

| Surface | 现在/未来职责 | 明确不拥有 |
| --- | --- | --- |
| `openspec/policies/` | policy 正文：触发条件、review 问题、组合方式、non-authority boundary | runtime state、跨 session runner、archive transition |
| `openspec/config.yaml` | 短 context、artifact rule、apply/archive guidance 路由 | 长篇 policy、checker verdict、blocking flag |
| `openspec/guardrails/` | 后续独立 change 的 impact packet、fresh-session challenge、finding/dossier、provenance、closeout coordinator | graph/node route、模型自我批准、第二套 governance registry |
| `openspec/governance/` | 现有结构/需求/Charter checker 的 deterministic verdict producer | policy 正文、语义质量 judge、guardrail orchestration |
| `tasks.md` | change-local durable work ledger | 触发器、质量证明、archive authority |
| `AGENTS.md`/skill | 薄 bootstrap 指针和 workflow 消费规则 | 另一份长 checklist 或隐式状态机 |

因此，未来 `guard rails`（跨 session 提交前检查）应作为独立 change，目录放在
`openspec/guardrails/`；本文件只描述它如何消费两个 operation attach point，不提前创建空实现目录。

---

## 6. 推荐的 guidance 草案（仅供后续 change 使用）

下面是**短路由草案**，不是现在就修改 `openspec/config.yaml` 的授权。它刻意不复制
`control-placement.md` 全文，也不写尚未验证的命令名/硬阻断字段。实际接入前应先完成第 9 节 probes。

```yaml
operations:
  apply:
    guidance:
      - >-
        Before the first target edit and on every resumed apply, read the
        selected change Focus Card, applicable openspec/policies, delta, design,
        and unchecked tasks. Re-check the decision owner, direct fact,
        deterministic admission owner, legal route, and lowest evidence seam.
      - >-
        Compare the plan with the selected historical lineage. Turn each
        actionable semantic, authority, scope, or evidence finding into an
        unchecked tasks.md task with owner, minimal correction, and done condition;
        do not leave it only in chat or a dossier.
      - >-
        Treat this guidance as advisory: preserve CLI-controlled blocked state,
        task status, user scope, and built-in apply instructions.
  archive:
    guidance:
      - >-
        Before closeout, bind review to the selected change, its approved
        baseline/merge-base, owned surface, and actual diff. Do not treat an
        unbounded worktree scan as proof; report missing-boundary when separation
        is not reliable.
      - >-
        Reconcile actual diff with proposal, specs, design, and tasks; run the
        applicable deterministic checks and record their results separately from
        semantic review. Keep actionable findings as unchecked tasks and return
        to apply.
      - >-
        Guidance is advisory and does not replace native archive checks or grant
        archive authority. A future guardrail-owned coordinator/finalizer must
        own any mechanical closeout decision.
```

### 6.1 为什么草案只写三条左右

`openspec/config.yaml` 是 information map，不是 handbook。当前项目 context 已有明确的短路由约束，
且入口文档有 140 行 warning / 180 行 hard limit。若把 policy 正文、bug 长表、质量 rubric 全塞进
guidance，会造成：

- 每次 apply/archive 都重复消耗 context；
- OpenSpec 更新或多个 adapter 修改时发生文案 drift；
- Agent 把“读过 checklist”误报成“做过 review”；
- 真正重要的 finding 反而被长文本淹没。

深度内容应通过 canonical path 指向 `openspec/policies/` 和未来 `openspec/guardrails/`，而不是复制。

### 6.2 与当前 `rules` 的组合方式

建议保持以下层次，不把三种语义混成一句：

| 层 | 写什么 | 何时出现 | 结果是否持久 |
| --- | --- | --- | --- |
| `rules.proposal/design` | Focus Card、policy selection、Control Placement Review 的记录要求 | 写对应 artifact | 写进 artifact |
| `rules.tasks` | finding 必须留下 owner/action/done condition 的 durable obligation | 写/改 `tasks.md` | 写进 tasks |
| `operations.apply.guidance` | 读取上述记录并重新做 plan review | 每次 apply instruction lookup | 否 |
| `operations.archive.guidance` | 将 review 绑定 actual diff，检查是否可 closeout | 每次 archive instruction lookup | 否 |
| `openspec/guardrails` dossier | 保存 review input digest、impact、objection、evidence、disposition | 后续 coordinator 运行 | 是，change-local |

`rules` 不应引用一个“自动运行”的命令，`guidance` 也不应伪装成 `blocking: true`。若需要命令结果，
由后续 guardrail coordinator 明确执行并保存 provenance。

---

## 7. 未来 Guardrails 如何真正解决“每个 change 只管自己”

### 7.1 两个 guidance 只是入口，跨 session 能力在第三层

用户指出的核心痛点是：每次 OpenSpec change 是独立赛事，只看自己，不看别的影响。两个 guidance
能把 review 问题在两个事件重新推送，但它们不自动搜历史、不产生 reviewer identity，也不保存
跨 change 影响集合。未来 guardrail 应补的是**编排**，不是再写一份 policy：

```text
apply.guidance
    │  当前 Agent 先做 plan review
    ▼
tasks.md（未决 finding 的 durable ledger）
    │  下一 session 继续消费
    ▼
guardrails/impact packet
    │  branch inventory + historical lineage + selected diff
    ▼
fresh-session challenger / bounded calibration / human review
    │
    ├── objection → 新的未完成 task → 回到 apply
    └── no actionable objection
             ▼
archive.guidance（再次提醒 actual-diff closeout）
             ▼
deterministic closeout coordinator/finalizer
             ▼
native archive transition
```

### 7.2 Guardrail 的最小输入

后续 change 至少要能构建下表的 impact packet；缺任何一项时应报告 unknown，而不是猜：

| 输入 | 能回答什么 | 不能推导什么 |
| --- | --- | --- |
| selected change + merge-base/approved baseline | 哪些文件/能力属于本次实际 diff | 整个 worktree 都归本 change |
| Focus Card + delta/spec/design/tasks | 作者声明的 owner、scope、要求和未决工作 | 声明本身正确 |
| branch/capability inventory | 哪些相邻 consumer/route/evaluator 可能受影响 | 每个相邻文件一定被影响 |
| historical bug lineage | 是否出现已知的错层模式、应提出哪个反例 | 本次一定会回归 |
| deterministic checker/test result | 结构、契约、route/invariant 的机械事实 | model 输出有价值 |
| bounded calibration corpus/rubric | 指定 case/model/config/budget 下的认知证据 | 跨模型/跨时间的一般质量 |
| fresh-session challenge record | 作者上下文之外的 objection 与遗漏 | 自动替代人类价值判断 |

### 7.3 finding、dossier、task 的分工

- `dossier` 记录“审查过什么、看到了什么证据、谁在何时审查”；它不是 source of truth，也不是
  lifecycle authority；
- `tasks.md` 记录“还必须做什么”；任何 actionable finding 必须有普通未完成 task；
- source/spec/test/corpus 仍是各自事实源；不能用 dossier 中的 `pass` 文本闭合 task；
- 没有可信 reviewer/orchestration identity 时，只能称为 fresh review record，不能声称安全级别的
  独立审查。

### 7.4 认知题为什么仍不能变成普通 test asset

传统程序的 invariant、parser、state transition 可以用 deterministic test 做很强的判断；“研究解释
是否贴题、证据是否足够、合成是否有价值”没有同样稳定的 oracle。正确做法不是放弃 test，而是分层：

| 证据层 | 适用 claim | 诚实结论 |
| --- | --- | --- |
| deterministic seam | candidate 不越权、route/state/invariant、command 真可执行 | `clear` 或机械 `blocked` |
| bounded live calibration | 固定 case/model/config/time/budget 的 rubric 表现 | `pass` / `limited` / `inconclusive`，带 provenance |
| fresh-session challenge + human review | 发现作者未见的反例、scope 漏洞、无证据 quality claim | review finding 或人工 disposition |

两个 guidance 只负责在正确时机要求进入这套证据层；它们本身不能制造 cognitive oracle。

---

## 8. 反例与不采用的方案

### 8.1 不能用 `SessionStart` banner 代替 operation timing

每个 session 都显示完整 guardrail banner 看似不会遗漏，实际上有三个问题：

1. 同一个 Agent 在非 OpenSpec 工作中也被打扰，产生 alarm fatigue；
2. Codex、Claude、CI、手工 CLI 等入口不一定共享 hook，触发覆盖率反而不可见；
3. 它没有 selected change、actual diff 或 task 状态，无法回答“现在该审什么”。

change 事件是更窄、可解释的触发器；若另有 session bootstrap，只放一条指向本文/README 的短路由。

### 8.2 不能把 semantic review 写成可机检的全仓 schema

要求每个 change 填一张庞大的 source→consumer→evaluator→route 对象表，会很快变成第二套
governance registry：作者填满字段，checker 只验证非空，reviewer 仍不知道答案是否正确。当前推荐
的 `Control Placement Review` 只做最小 disclosure；跨 session guardrail 以 impact packet + objection
为输入，不把所有认知事实强行结构化成可自动判真的 schema。

### 8.3 不能让一个 LLM judge 自动给 quality pass

单次 judge 受 provider drift、样本覆盖和 prompt 自证影响。它可以提出 objection 或整理证据，不能
独占 merge/archive authority；认知质量的 `limited`/`inconclusive` 必须是允许的结果。

### 8.4 不能把 guidance 当 executable hook

下面这些字段在 1.7.0 不是受支持的契约：

```yaml
operations:
  apply:
    command: ./run-guardrail.sh
    blocking: true
    runner: guardrails
```

即使某个 parser 暂时忽略未知字段，也不能在计划中把它们当作未来 API。要执行命令，必须另立
guardrail coordinator/CI contract，并记录输入、输出和失败语义。

### 8.5 不能把 policy 放回 governance

`governance` 的 deterministic checker 可以被 guardrail 消费，但 policy 正文、跨 session dossier 和
closeout orchestration 是不同职责。混放会导致 checker 被误认为拥有 policy authority，也会让未来
`guardrails` 无法独立演进。目录边界是本次 review 的明确决定：

```text
openspec/policies/    policy prose / review questions
openspec/guardrails/  future orchestration / findings / closeout
openspec/governance/  deterministic verdict producers
```

---

## 9. 接入前必须做的本地 probes

以下不是“以后再看看”的泛泛建议，而是启用 guidance 前的验收条件。没有证据时，主计划只能把
V2 标为 proposed：

| Probe | 最小做法 | 通过标准 | 失败时的诚实处理 |
| --- | --- | --- | --- |
| delivery | disposable change 执行两条 `instructions ... --json` | apply/archive 各出现正确数组，contextFiles/state 仍完整 | 不配置或记录 unsupported |
| hot read | 不重启 CLI，仅改 config 后再次 lookup | 新 guidance 出现，旧 guidance 不被缓存 | 依赖显式重启/版本限制，并记录 |
| malformed config | 字符串、空数组、未知 operation/字段 | 看到 warning，理解为 guidance 缺失而非 review pass | 保持 advisory，不能 fail closed |
| apply resume | 第一个 session 写入 `[ ]` finding，第二个 session重新 apply | guidance + task 都被消费；task 可被有证据地完成 | 不能声称跨 session 闭环 |
| actual diff boundary | change 有 approved baseline，worktree 另有无关修改 | coordinator 能区分或返回 `missing-boundary` | 禁止全 worktree 假审查 |
| archive side effect | disposable change 做 sync、collision、move、失败重试 probe | native archive 的副作用和失败后状态有明确 contract | 暂不做自动 finalizer |
| guidance lookup failure | 模拟旧 CLI/无效 JSON | archive workflow 按 skill 继续，状态报告明确“无 guidance” | 不得把它宣称成 hard gate |
| historical replay | BUG-011、BUG-013、BUG-015、BUG-016 加一个 cognitive branch | review 能提出正确问题；漏抓的 case 保留为反例 | 缩小承诺，不用改词掩盖盲点 |
| fresh-session provenance | 作者 session 与 challenger session 使用可审计 identity/digest | dossier 能证明输入不同且绑定当前 diff | 只能标记 fresh review record |

### 9.1 建议的 probe 输出记录

每次 probe 应记录：OpenSpec 版本、配置 digest、change 名称、命令、stdout/stderr 摘要、退出码、
是否生成 `operationGuidance`、实际 skill 行为和未决限制。不要把 provider body、secret 或完整聊天
记录写进 repo；证据只需足以复现边界。

---

## 10. 分期建议：如何从 advisory 走到真正的提交前检查

### Phase 0：本文件（当前）

- 记录 OpenSpec 1.7 的真实契约与降级边界；
- 保留历史 bug 的来龙去脉和反例；
- 不修改 runtime，不创建空 `openspec/guardrails/`。

### Phase 1：Policy change

- 在 `openspec/policies/` 建立 `control-placement.md` 和 README；
- 更新 Focus Card 的 `Triggered review policies` 与确定性 shape checker；
- 用真实 active change 和 historical replay 验证“先问对问题”是否有用。

### Phase 2：OpenSpec operation guidance change

- 在 `openspec/config.yaml` 增加精简的 `rules.tasks` obligation 和两个 operation guidance；
- 用 disposable change 验证 delivery、resume、lookup failure 和 config line budget；
- 把 guidance 当 prompt-level contract，明确显示 `advisory`，不伪造 blocking；
- 在 apply/archive skill 适配层记录 guidance 被考虑、被跳过或与控制输入冲突的原因（若该适配层可记录）。

### Phase 3：独立 Guardrails change

- 创建 `openspec/guardrails/` 的实际实现与 change-local dossier/impact packet schema；
- 实现 fresh-session challenger、finding→tasks 回写和 selected-change diff boundary；
- 建立窄的 deterministic closeout coordinator，由它独占 native archive 调用；
- 将 governance checker/test verdict 作为输入，不复制 checker 或 policy 正文；
- 对认知变更接入 bounded calibration、human escalation，允许 `limited/inconclusive`。

### Phase 4：用数据检验是否值得升级强度

- 以 BUG lineage replay 和前五个触发 change 建 baseline；
- 记录发现了哪些错层、哪些是 false positive、哪些反例未被捕获；
- 不以 policy 引用数、task 数、test 数或单次 LLM 分数宣称 regression 已下降；
- 只有在边界、provenance、archive side effect 和历史数据都稳定后，才讨论更强的 admission policy。

---

## 11. 假设、疑点与当前判定

| 项目 | 当前判定 | 仍需警惕 |
| --- | --- | --- |
| 两个 operation id 是否就是 `apply`/`archive` | **已核实**：1.7.0 parser 只支持这两个 | 升级 OpenSpec 后要重新跑 schema/probe，不要假定向后兼容 |
| guidance 是否会自动执行脚本 | **否**：只返回字符串数组并由 skill 作为 advisory prompt input 消费 | 未来若加入 wrapper，必须另写 executable contract |
| guidance 是否能阻止 archive | **否**：archive skill 对 lookup 失败明确 fail-open；文本本身不具 enforceability | 需要 guardrail-owned coordinator/CI 才能提供机械阻断 |
| `rules.tasks` 是否能保存跨 session 发现 | **能保存 obligation，不能保存自动 verdict** | finding 必须有 owner、action、done condition 和证据引用 |
| archive 是否应该重新审完整 proposal | **不应该**：重点是 selected actual diff 与 scope drift | actual diff boundary 不可信时必须 `missing-boundary` |
| cognitive quality 是否可以普通 test 解决 | **只能解决确定性边界** | calibration、fresh-session challenge 和 human review 仍不可省略 |
| policy 放哪里 | **`openspec/policies/`** | 不把 policy 正文、checker 和 guardrail coordinator 混进 governance |
| guardrails 何时创建 | **独立后续 change** | 本文件不创建空实现目录，也不把 V2 夹带进 V1 |

---

## 12. 最终建议

这两个 OpenSpec 1.7.0 时机值得用，而且应该用得比“在 rules 里再加一段提醒”更精确：

1. `rules.tasks` 先把跨 session obligation 留在 change 内；
2. `operations.apply.guidance` 在实现前和恢复实现时，把 boundary/authority/历史反例重新推回当前 Agent；
3. Agent 发现问题就写回未完成 task，不把结论留在聊天或一次性 dossier；
4. `operations.archive.guidance` 在收口时只看 selected change 的 actual diff、边界和未闭合 finding；
5. 真正需要“提交前一定检查”的地方，由未来 `openspec/guardrails/` 的 coordinator/finalizer 执行
   deterministic closeout，并独占合法 archive transition；
6. 认知质量只输出有 provenance 的 `pass|limited|inconclusive`，不让 guidance 或单一 LLM judge 冒充
   merge authority。

这回答了“传统程序靠 test asset，智力题怎么办”：**测试继续守住可判定的边界；不可判定的认知 claim
走有界 calibration、fresh-session challenge、human review 和可追溯 finding；两个 operation guidance
负责把这套证据流程在正确的生命周期时刻叫回来。** 它们不是万能门禁，却是把“每个 change 只管自己”
转成可持续 feedback loop 的正确第一层。

## 证据索引

- OpenSpec CLI：`openspec --version`、`openspec instructions apply/archive --change <name> --json`。
- 本地配置 parser：`@fission-ai/openspec` 1.7.0 的 `ProjectConfigSchema`、`OPERATION_IDS` 和
  `loadOperationInputs`；配置模板明确 `operations.apply/archive.guidance` 是 per-operation advisory guidance。
- 本地消费契约：`.codex/skills/openspec-apply-change/SKILL.md` 第 3–4 步与
  `.codex/skills/openspec-archive-change/SKILL.md` 第 2 步。
- 本仓库现状：`openspec/config.yaml` 当前没有 `operations:` block；因此本文件的 Phase 2 是 proposed，
  不是已交付能力。
- 历史问题证据：[`01-bug-boundary-evidence.md`](01-bug-boundary-evidence.md)。
- 外部反馈环借鉴：[`02-session-drift-borrowing.md`](02-session-drift-borrowing.md) 及其链接的
  `08-final-recommendation-openspec-feedback-loop.md`、`A-session-lifecycle-and-attach-points.md`。
