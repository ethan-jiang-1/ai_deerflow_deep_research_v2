# Deep Research HITL UX 历史调研

> 类型：调研 / 复盘，非实施计划
> 更新：2026-07-26
> 范围：本地归档 change、已修复 bug、现行规格、源码、确定性探针和保留的 real-demo run；未发起真实模型或网页请求。
> 关联现场：[BUG-013](../../bugs/BUG-013-semantic-hitl-input-breaks-first-run.md)

## 阅读方式

本文刻意区分三件常被混在一起的事：

1. **已验证事实**：保留 run、源码、契约和确定性探针已经证明的当前行为。
2. **历史模式**：多个已修 bug 虽然表面不同，却反复暴露出的结构性缺口。
3. **候选系统方向**：下一轮设计讨论的假设，不是已批准的实现或 OpenSpec proposal。

配套的[语义 UX 分析](deep-research-semantic-hitl-ux-analysis.md)展开第三项。本文先回答：为什么再加一个 parser 词条或再补一句文案，仍会重演同类问题。

## 结论先行

这次 `make demo-real` 的失败不是模型偶发，也不是 HITL2、provider 恢复或 retained session 的问题。它是当前 HITL1 交互契约的确定性结果：

```text
展示完整 proposal
  -> CLI 只把精确的 "采用建议" 翻译为 typed action
  -> "确认" 被作为普通文本提交
  -> profile 字段 parser 识别不到任何字段
  -> HITL1 消耗一次“未识别输入”重试
  -> 连续三次后，研究尚未开始就被阻塞
```

保留 run `r_y5hkuk0XU3qQN18yMayBxgWWiNF2x3gqG5k4QOj5xR4` 确认了
`blocked@hitl1`、`input.invalid_response` 和诊断引用
`diag_sXTfvC54yIHQYfDvJyXu3O1Q`；它从未进入 topic planning 或检索。

更深的问题不是中文同义词不够。系统把面向人的对话做成了传输协议外面包一层文本：人必须猜自己的句子到底该是内部 action 别名、schema patch，还是封闭 enum 值。结果是上下文中显然合理的回答会意外失效，而普通提问还可能意外变成 profile 修改。

项目已经修过好几个同类形态的缺陷，每个局部修复都有价值，但还没有一条共同规则把以下问题连在一起：

- 这个决定究竟应不应该由人做；
- 人此刻正在决定的完整对象是什么；
- 人可以用自然语言表达哪些含义；
- 理解到该含义后，哪个 machine action 才合法；
- CLI、TUI、workbench 如何一致地展示同一个安全下一步。

没有这份共享交互契约，下一阶段仍可能用另一个 action id、另一个 UI 或另一条错误信息重新造出同一个问题。

## 最小复现与因果事实

最小确定性复现是：刚展示了完整 HITL1 proposal、当前 request 广告
`accept_suggestion`，用户输入 `确认`。

| 边界 | 已验证行为 | 对用户的后果 |
| --- | --- | --- |
| CLI adapter | [`demo_real.py`](../../../agent/scripts/demo_real.py) 仅把精确 `采用建议` 变成 `AnswerRun(... response_kind="action" ...)`；任何其他非空文本都是 text response。 | 人看到的“确认”对系统并不等于接受。 |
| 传输验证 | [`human_input.py`](../../../agent/src/deerflow_deep_research/runtime/human_input.py) 正确拒绝伪造或未广告的 typed action。 | 这条严格控制边界是合理的，应保留。 |
| Profile parser | [`profile.py`](../../../agent/src/deerflow_deep_research/domain/profile.py) 识别固定的 profile 术语，不识别接受、提问或犹豫意图。 | `确认` 没有任何已识别字段。 |
| HITL1 controller | [`hitl1/node.py`](../../../agent/src/deerflow_deep_research/graph/nodes/hitl1/node.py) 对零识别增加 `profile_rejection_round`，第三次阻塞。 | 一次正常确认被计成一次无效 profile 提交。 |
| Shared projection | [`prompts.py`](../../../agent/src/deerflow_deep_research/graph/nodes/hitl1/prompts.py) 的 follow-up context 丢弃 `action_ids`；[`run_experience.py`](../../../agent/src/deerflow_deep_research/runtime/run_experience.py) 从该 context 读取可见 action。 | 第一次失败后，即使图侧仍允许接受，CLI 也丢失了隐藏的恢复口令。 |

两个额外确定性探针表明这远不止一个词：

| Proposal 之后的自然回复 | 当前 parser 结果 | 为什么有害 |
| --- | --- | --- |
| `确认` | 无已识别字段 | 清晰接受变成消耗重试的错误。 |
| `可以，但只采用有影响力团队或社区的一手资料，并给出引用。` | 无已识别字段 | 关键的来源/引用约束无法通过正常路径表达。 |
| `为什么是 moderate？` | 因句中出现 `moderate` 而识别为 `cost_tolerance` | 一个解释请求可能被当作 profile 修改，丢掉 proposal-confirmation 语境。 |
| `你看着办，差不多吧` | 无已识别字段 | 不确定性被惩罚，而不是被澄清。 |

Proposal projection 还有独立的信任断点：HITL1 存储 `scope_boundaries` 和
`custom_notes`，但 `build_proposal_context()` 只暴露 enum 维度和
`must_answer`。本例“一手资料、必须引用”的限制即使被模型捕获，用户也看不到、无法确认。

## 当前人机交互点清单

此清单区分当前运行时事实与仅为兼容性或 fake fixture 保留的旧类型。

| 交互面 | 当前目的 | 谁拥有决定权 | 风险 / 结论 |
| --- | --- | --- | --- |
| 初始研究问题 | 收集研究目标。 | 人提供目标；没有内部路由外包给人。 | 自由文本合适，因为输入本身就是任务内容，不是隐藏控制。 |
| Real HITL1 | 确认、修改或澄清研究 profile。 | 人提供偏好；graph 拥有 admission 和状态转换。 | 当前系统性缺陷：多种人类含义共用一个字段 parser 和一个重试计数器。 |
| Fake HITL1 | 确定性 fixture 路径。 | Fixture / test controller。 | 不能被误当作真实语义 intake 对新手体验的证明。 |
| HITL2 | 过去曾暴露 route choice；BUG-007 后 real graph 已自主继续。 | Graph / agent。 | 重要先例：不能因为图有 route 就把选择交给人。 |
| CLI / TUI / local workbench 的接受操作 | 同一个 HITL1 授权的呈现。 | Graph 验证 current request；adapter 只提交。 | CLI 用 magic phrase，TUI/workbench 用按钮；人的交互契约并不相等。 |
| Cancel | 经显式 lifecycle control 停止。 | Runtime / lifecycle。 | 必须和语义 profile 输入分开。 |
| Retained inspection | 只读诊断。 | Session / diagnostic authority。 | 绝不能被呈现成 resume 或 recovery authority。 |

当前生产代码只有两处 `interrupt()` 构造，均在 HITL1（real 与 fake）。这**不**意味着规则只应修 HITL1；它意味着 HITL1 是第一个 live adoption point，未来任何人类 interrupt 都应先经过设计 gate。

## 历史序列

| Change 或 bug | 当时的直接修复 | 对本次的长期教训 |
| --- | --- | --- |
| [BUG-001](../../_done/_fixed_bugs/BUG-001-hitl1-localized-intake-and-confirmation.md) 与 `harden-deep-research-real-cli-intake-and-observability` | 增加确定性的本地化字段解析、proposal 持久化、反馈和显式接受。 | 它修复了已解析字段被静默丢失，但把接受建模为 adapter 专属文本别名，仍和字段 parser 并列。 |
| [BUG-002](../../_done/_fixed_bugs/BUG-002-retained-run-diagnostics-are-not-actionable.md) 与 [BUG-003](../../_done/_fixed_bugs/BUG-003-real-cli-run-state-is-not-observable.md) | 改善安全的 retained diagnosis 和进度投影。 | 有 run 记录或 status 事件还不够；人必须看到权威事实、其含义和合法下一步。 |
| [BUG-006](../../_done/_fixed_bugs/BUG-006-demo-hitl2-choice-is-masked-as-protocol-fault.md) | 修复显示的 `id: description` 与实际接受的 option ID 不一致，并保留真实输入错误。 | UI 不能把某物显示成可选，而传输层只接受另一个不可见表示。 |
| [BUG-007](../../_done/_fixed_bugs/BUG-007-hitl2-decision-lacks-actionable-context.md) 与 `make-hitl2-decisions-agent-led` | 移除正常 HITL2 的用户 route selection。 | 首先要问“人是否该决定”，而不是给内部 route 菜单润色。 |
| [BUG-008](../../_done/_fixed_bugs/BUG-008-real-demo-provider-timeout-is-not-recoverable-or-actionable.md)、[BUG-010](../../_done/_fixed_bugs/BUG-010-topic-planning-timeout-is-masked.md)、[BUG-012](../../_done/_fixed_bugs/BUG-012-terminal-diagnostic-reference-diverges-from-bundle.md) | 使 provider/workflow outcome 有界、关联且可操作。 | Recovery 必须由 phase 拥有、从单一事实源投影，并区分 inspection 与 execution；人类理解失败也缺同样纪律。 |
| [BUG-005](../../_done/_fixed_bugs/BUG-005-wave0-real-worker-failure-category-is-opaque.md) | 在 result boundary 保留安全失败分类。 | 好的 projection 不能凭空补回 owner 已经丢掉的事实。 |
| [BUG-009](../../_done/_fixed_bugs/BUG-009-hitl2-zero-tool-fixture-omits-wave2-predecessor.md) 与 [BUG-011](../../_done/_fixed_bugs/BUG-011-completed-final-delivery-skips-gate.md) | 修复 fixture/control-path 分歧。 | 当测试构造了非法 predecessor 或绕过真实 transition 时，全绿没有证明力。 |
| [BUG-013](../../bugs/BUG-013-semantic-hitl-input-breaks-first-run.md) | 已登记，本文不提出修复。 | 将交互契约缺口带回第一个用户回合，并在研究开始前阻断产品。 |

## 重复失败模式

已修 bug 可归入以下重叠的类别：

| 模式 | 例子 | 重复缺口 |
| --- | --- | --- |
| **协议泄露** | BUG-001、BUG-006、BUG-013 | 人被要求输出内部字段/值/action 编码，而不是通过可见控制或被理解的人类回合表达意图。 |
| **权责泄露** | BUG-007、BUG-013 | graph-owned route/admission 被交给人，或人的合法偏好被迫塞进 graph-control grammar。 |
| **投影分裂** | BUG-002、BUG-003、BUG-006、BUG-012、BUG-013 | Graph/runtime 有一份事实，CLI/TUI/inspect 却渲染出有损、错配或独立重建的版本。 |
| **没有参与者契约的恢复** | BUG-003、BUG-008、BUG-010、BUG-013 | 系统记录了重试或终态，却没告诉人“听懂了什么、现在还可能什么、唯一合法下一步是什么”。 |
| **证据盲区** | BUG-006、BUG-007、BUG-009、BUG-011、BUG-013 | 测试验证 parser、fixture 或内部 route，却没有覆盖触发功能的完整用户可见 transition。 |

这就是为什么“再修一次 parser”不是充分计划：它只会处理协议泄露的一个实例，其余四类仍会在下一个入口复现。

## 缺失的 Seam

当前在 response 已经成为有效 control object 之后，owner 很明确：

```text
checkpointed proposal + current interrupt
                 |
                 v
        graph 验证 correlation 与 action
                 |
                 v
           checkpoint transition
```

缺的是这之前的 seam：人需要明白自己可以表达什么，系统需要先把该表达归入封闭含义，之后才谈 graph 是否允许状态改变。

```text
人的文字 / 显式 UI control
                 |
                 v
          人类交互契约              <-- 当前没有共享 owner
          - 为什么问、谁该决定
          - 当前完整的交互对象
          - 合法的人类意图
          - 反馈与恢复语义
                 |
                 v
       graph-owned validation 与状态转换
```

`HumanInputRequest` 当前提供 transport correlation 和低层 mode；`PromptView` 提供安全 presentation projection。两者都没有表达用户是在接受、修改、提问还是要求澄清，也没有携带完整、面向人的 action affordance。Adapters 因此各自填补这个缺口。

## 必须保留的约束

历史修复同时建立了一些绝不能在“更语义化”时倒退的约束：

- graph/controller 仍是接受 proposal、修改 profile、选择 route、写 checkpointed control state 的唯一权威；
- request correlation、stale response denial、advertised-action validation 必须继续 fail-closed；
- model output 只能 advisory 且必须验证；不能把 raw model/user/provider 内容泄露进诊断或 retained projection；
- 自动恢复必须有明确 owner、有界预算、terminal disposition 和一个合法 next action；
- retained bundle 是诊断，不是隐式 execution resume；
- 确定性 fixture 必须证明真实相关 seam，不能用手写状态假装用户旅程。

## 候选准则，而非现有 Policy

证据支持探索一条暂名为 **人类交互完整性** 的长期规则：

> 面向用户的 interrupt 是产品交互契约，不是带一段 prose 的序列化 control request。暴露它之前，必须说明人要做的决定、完整可见的对象、回复可能代表的封闭含义、admit 每种含义的 graph authority、歧义的恢复方式，以及证明该回合的新手用户旅程。

仅当它在 HITL1 之外也被证明有用时，才值得进入 Deep Research agent charter。它不能作为抢占 owning capability spec 的口号；配套分析会说明其触发条件、边界和审查问题。

## 新 OpenSpec Proposal 之前的问题

1. Deep Research 有哪些交互类型，哪些当前或未来 state 真正需要人的决定而不是 agent recommendation？
2. 最小的封闭 intent vocabulary 是什么，才能让人接受、修改、提问或要求澄清，而无需了解 action ID 或 JSON？
3. 如何把自然语言 interpretation 与 graph-authorized action 分开，避免 interpreter 获得 route、cost 或 checkpoint 权力？
4. proposal 的修改涉及 scope、来源标准、cost、time 或输出时，何时必须重新确认，哪些 material constraints 必须可见？
5. semantic interpretation 不可用或不确定时，怎样提供诚实 fallback，而不重新引入隐藏 magic phrase？
6. 哪些确定性 transcript 必须先红后绿，包括本例 `确认`、带约束修改、提问、歧义和 stale/forged action？

## 非结论

本文尚不授权：

- 把任意自然语言当 typed action；
- 引入拥有 route 或 checkpoint authority 的通用聊天 agent；
- 用 model output 替换所有确定性 profile validation；
- 未先分类用途就把同一种交互机制套到所有 text field；
- 修改 `backend/` 或 `frontend/`；
- 在 interaction model 和 fallback 决策审查前开启新的 OpenSpec change。
