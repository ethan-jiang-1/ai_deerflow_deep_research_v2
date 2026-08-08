# Session-Drift Guardrail：外部方案的选择性借鉴

> 主计划：[`../policy-gate-injection-layer.md`](../policy-gate-injection-layer.md)
> 外部输入：`/Users/bowhead/ai_tool_deepresearch/_backlog/plans/session-drift-guardrail-analysis/`
> 审查日期：2026-07-31
> 结论：借鉴其 **feedback-loop 分工与反模式**，不复制其 JS 文件、requirement ID、archive wrapper 或
> 另一项目的 runtime / guideline authority。

## 1. 为什么这份外部分析值得借

外部项目面对的不是“缺少更多 policy 文本”，而是两类不同问题：

1. **内容/语义 drift**：同一事实在 writer、reader、reentry、gate、时间投影等不同 consumer 被不同方式
   解释；
2. **生命周期执行缺口**：已有 guidance/checker 没有在 apply/archive 时稳定回到 Agent 上下文，也没有
   与最终 transition 绑定。

它的最终建议（`08-final-recommendation-openspec-feedback-loop.md`）避免了把两者混为一个万能
checker。这个区分正好补足本计划：`control-placement` 提供 change 设计的语言和最小 record；
未来 guardrail 才负责跨 session 再次触发 semantic review、保留 finding，并在可机械部分做 closeout。

## 2. 本仓库的适用性已核实

| 本地事实 | 已核实状态 | 含义 |
| --- | --- | --- |
| OpenSpec 版本 | `openspec --version` = `1.7.0` | 可以探索 `operations.apply/archive.guidance` 作为 event-triggered prompt push |
| Codex apply/archive skill | 已读取可选 `operationGuidance`，并明确它只是 additive advisory | guidance 可以在每次 apply/archive 重新出现，不能声称它已经运行 checker |
| `openspec/config.yaml` | 当前没有 `operations:` block；现有 archive guidance 是普通 context/rules 文本 | 这是尚未使用的 attach point，不是已交付能力 |
| archive flow | `.codex/skills/openspec-archive-change/SKILL.md` 当前允许 warnings 后继续，并以 raw `mv` 完成 move | 当前同样存在“task/文字不等于 deterministic closeout”的生命周期缺口 |
| `openspec/governance/` | 已有 project req/spec/architecture/charter checker | 可作为 deterministic facts 的 producer；不应成为 policy 正文或 cognitive judge |

因此可迁移的是 **责任分工**，不是外部仓库的文件路径或“已经有 finalizer”的事实。

## 3. 要借的五个设计决定

### 3.1 三个 surface 绝不互相冒充

| Surface | future role | 明确不负责 |
| --- | --- | --- |
| `openspec/policies/control-placement.md` | 说明何时需要 review、作者应回答什么、已有 policy 如何组合 | 运行时 authority、跨 session state、机器 pass/fail |
| `openspec/guardrails/` | 保存 risk-led review protocol、impact packet、challenger/dossier 规则、change-local findings 与 guardrail-owned closeout coordination | 重新定义 graph route、让一个 LLM 自动批准自己、复制 governance checker |
| `openspec/governance/` | 产生现有 project 的 deterministic verdict，供 guardrail coordinator 调用 | 承载 policy 内容、判断 cognitive answer 是否“够好”、用 prose 推断事实或拥有 guardrail 流程 |
| `tasks.md` | 跨 session 保存 plan/closeout review 和可执行 finding | 触发器、语义 proof 或 archive authority |
| `operations.apply/archive.guidance` | 在 OpenSpec 事件发生时把当前 review posture 推回 Agent context | 执行命令、证明 review 做得好、替代 normal task |

**instruction 是 push channel，task 是 durable work ledger，deterministic checker/finalizer 才能闭合
机械条件。** 三者不能互相冒充。

### 3.2 用 change 事件触发，不用每个 session 的 banner

外部压力测试否决了 `SessionStart` hook：它容易多 harness 漏触发、产生无关噪声和 alarm fatigue。
本仓库同样同时有 Codex skill、OpenSpec CLI 和 project guidance；若未来启用它，应优先：

- `operations.apply.guidance`：第一次 target edit 前、以及 resumed apply 时触发计划 review；
- `operations.archive.guidance`：archive 前针对 **当前 selected change 的 actual diff** 触发 closeout review；
- 简短的 `AGENTS.md` 指针只作 bootstrap fallback，不复制长 checklist。

`actual diff` 必须绑定 selected change 的 owned surface / approved baseline。若 worktree 中无法可靠分离
其它未关联修改，guardrail 只能报告 missing-boundary，不能把整个工作树冒充成已 review。

### 3.3 finding 必须变成 task，而不是聊天里的一句“注意”

semantic review 发现的工作应成为普通未完成 task，至少含：

- 被保护的 requirement、reader question 或 known historical lineage；
- direct owner / authoritative surface；
- 最小纠正动作；
- 能证明已纠正的 done condition，或诚实的 `limited/inconclusive` evidence boundary。

这比保存“LLM quality score”更有用：下一 session 的 apply 仍然能读到具体未完成工作，但没有伪造
semantic proof。

### 3.4 closeout review 看实际变更，不只看 proposal

proposal 阶段的 `Control Placement Review` 能使作者先问对问题，但 BUG-011 证明实际 implementation
仍可能引入 broad guard。future archive guardrail 因此应：

1. 读取 proposal/design/delta/tasks 和 selected change 的 approved baseline；
2. 用当前 diff 与历史 replay corpus 找相邻 consumer / legal route / direct fact；
3. 若有 finding，写回 task 并停止 archive；target 修改回到 apply；
4. 若没有 semantic finding，才运行 deterministic checks / normal archive transition。

guardrail 不能用 semantic checker 判定 table “答案正确”。它只让当前 Agent 带着更准确的历史与 diff
重新做一次可解释 review。

### 3.5 deterministic closeout 必须很窄

外部方案的 finalizer 思路值得借：它只聚合 direct facts（artifact/task status、strict validation、
existing checker result、native archive result），不判断语义 review 质量，也不重写 archive mechanics。

按本计划的目录边界，future finalizer / closeout coordinator 属于 `openspec/guardrails/`；它只调用
`openspec/governance/` 已有或新增的 deterministic verdict，而不把 guardrail 正文搬回 governance。
future change 仍须验证本仓库的 supported archive adapters、native `openspec archive` side effects、
sync ordering 和 failure modes，才确定 coordinator 的小 interface 与实际 runner 文件；这些是 contract
细节，不改变上述物理职责边界。

## 4. 明确不照搬的东西

| 外部被否决 / 有条件机制 | 本仓库的处理 | 原因 |
| --- | --- | --- |
| 对每个 change 强制一张可机检的 semantic-object schema | 不做 | 容易造出第二 registry、被填写成空话；机器无法裁决 cognitive truth |
| “两个 source 必须一致”的全仓 consumer scanner | 不做 v1 | source 的粒度可能故意不同；不完整扫描会制造假信心或误报 |
| SessionStart / Claude-only hook | 不做 | 对 Codex/其它入口不可移植，且不按 risk/change 触发 |
| 一个 LLM judge 自动给予 quality pass | 不做 | 自我评价、provider drift 与 sample coverage 不能构成 runtime/merge authority |
| 直接复制外部 `finalize-change-archive.mjs` 或 `--yes` archive 流程 | 不做 | archive adapter、sync 语义、CLI side effect 和 project checker 名称均不同；必须先做本地实验 |
| 把完整 guardrail checklist 复制进每个 skill/adapter | 不做 | OpenSpec update 和多入口会导致文案 drift；config operation guidance + 薄路由才是 single delivery path |

## 5. 对当前分期的改变

### V1：先建立 policy 与最小 disclosure record

当前 `add-openspec-control-placement-policy` 保持小范围：

- 创建 `openspec/policies/` 与 `control-placement`；
- 以 `Control Placement Review` 让作者披露受影响 decision/fact、owner、posture、invariant、reuse 与
  deterministic seam；
- checker 只校验**已声明 record 的存在/shape/闭合 posture/必要组合**，不推断 prose 是否充分；
- 用 BUG-011、BUG-001→013、BUG-012→016 等 historical lineage replay，确认问题是否会在实现前被提出。

这个表不是被外部分析否决的 semantic object schema：它不登记全 repo object inventory、不把每项需求映射到
一张卡，也不让 checker 评价“语义答案正确”。它只是触发 change 的最小 disclosure；其价值必须由 review
和反例回放验证。

### V2：`add-cross-session-cognitive-guardrails` 建 feedback loop

只有 V1 的 triggering / replay evidence 足以说明 record 有用后，才设计 V2：

```text
rules.tasks 生成 plan/closeout review obligation
        +
operations.apply/archive.guidance 在实际 change 事件推送 risk-led review
        +
finding 写回 tasks.md，跨 session 回到 apply
        +
guardrail dossier 记录 diff/impact/evidence/disposition
        +
deterministic closeout 只检查必要机械条件，再调用合法 archive transition
```

认知变更再叠加现有 calibration、fresh-session challenger 与 human escalation；deterministic change 则只需要
正确的 direct seam。二者共用 feedback loop，但不共用一个“质量分数”或 blocking threshold。

## 6. V2 立项前必须完成的本地验证

1. 用一个 disposable change 读取 `openspec instructions apply/archive --json`，证明 project-config
   `operations` guidance 的 delivery、缺失行为和 Codex skill consumption；
2. 枚举本仓库实际支持的 archive adapter / command，不把“仓库里有 Markdown 文件”当成 supported path；
3. 对选中的 archive mechanism 做 side-effect probe：spec sync、task warning、collision、move 和失败后
   worktree 状态都必须可观察；不能先写 main spec 再猜测 rollback；
4. 定义 selected-change diff / owned-surface boundary；无法分离时明确 stop，而不是 scan 全 worktree；
5. 用 BUG-011、BUG-013、BUG-015、BUG-016 加一个认知 branch case，验证 guidance→finding→task→resume 的
   闭环；未抓到的 case保留为反例；
6. 最后才决定 guardrail-owned closeout coordinator 的 narrow interface、它消费的 governance verdict、
   tests 和 accepted spec；不改变它位于 `openspec/guardrails/` 的职责边界。

## 7. 认知题的证据模型

ordinary test asset 仍是确定性 guardrail 的底座，却不能判定“这个解释/研究判断是否有用”。
future guardrail 应分层记录：

| 层 | 能证明 | 不能证明 |
| --- | --- | --- |
| direct deterministic seam | candidate 不越权、route/state/invariant 正确、用户承诺的 command 真能执行 | model / semantic output 质量 |
| bounded live calibration | 指定 case、model/config/time/budget 下符合 rubric 的证据 | 跨模型、跨时间、跨任务的一般质量 |
| fresh-session challenge + human review | 作者 session 未见的反例、scope 漏洞、无证据的 quality claim | 自动替代价值判断或成为 runtime authority |

因此 V2 的关键不是“找一个更聪明的 test”，而是让每种 claim 走向它诚实的证据层，并让未决的
semantic finding 跨 session 留在 tasks / dossier 中等待正确的 owner。
