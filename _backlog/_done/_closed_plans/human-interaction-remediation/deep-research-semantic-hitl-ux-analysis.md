# Deep Research HITL：从协议填表到人类交互契约

> 类型：设计探索，非实施计划
> 更新：2026-07-26
> 证据基础：[历史调研](deep-research-hitl-ux-history-research.md) 与 [BUG-013](../../bugs/BUG-013-semantic-hitl-input-breaks-first-run.md)

## 目的与状态

本文讨论怎样让 Deep Research 不再反复出现同一类 UX bug：人被要求猜 control token、选择内部 route、确认看不见的 scope，或在失败后面对没有可信下一步的提示。

它明确处于 OpenSpec proposal **之前**。这里记录的是推荐方向、备选方案、invariant 和未决问题；它不授权模型调用、新 checkpoint field、新 code module 或新 policy。

## 核心诊断

当前问题不是中文字符串不够，而是人的表达和 machine control envelope 之间缺少语义交互层：

```text
今天

人的文字
    |
    +--> adapter 的精确 token 分支 --> typed action
    |
    +--> profile parser -----------> 字段 patch / rejection counter
    |
    +--> 其他任何内容 ------------> invalid input / 最终终止

候选方向

人的文字或可见 control
    |
    v
共享的人类交互契约
    |
    v
封闭的人类意图 / 已验证的候选修改 / 聚焦澄清
    |
    v
graph 验证 current subject、correlation、policy 与 state transition
```

候选方向不意味着模型可以执行 action。它要求系统先分清“人想做什么”和“graph 允许怎样改变状态”。

## 临时通用语言

以下术语是本轮探索的产品语言，不是 class name 或 wire field。

| 术语 | 含义 | 不是什么 |
| --- | --- | --- |
| **交互对象** | 此刻让人参与的 proposal、问题、偏好或失败事实。 | Raw prompt string 或隐藏 checkpoint dump。 |
| **人类意图** | 受 phase 约束的封闭含义，例如接受当前 proposal、要求修改、提问、要求澄清。 | Raw sentence、action id 或 graph route。 |
| **语义解释** | 在当前交互对象的语境中，把回复有界地归入候选人类意图。 | 授权、路由、profile 持久化或 policy enforcement。 |
| **准入决定** | Controller/graph 验证解释出的 intent 对 current request 合法，因而可以产生 state transition。 | Model confidence 或 adapter heuristic。 |
| **显式控制** | 当前 request 中可见、有标签的 UI control，故意提交 typed action。 | 塞在自由文本框里的 magic phrase。 |
| **语义歧义** | 系统无法安全判断人属于哪个合法 intent。 | 伪造、过期、格式错或未广告的 control envelope。 |
| **实质性修改** | 可能改变研究 scope、来源标准、cost/time、deliverable 或必须回答事项的修改。 | 隐藏的 parser side effect。 |
| **人类交互契约** | 一个 interrupt 的目的、对象、合法 intent、安全 control、反馈、恢复和证据的 owned definition。 | 第二个 lifecycle controller 或 graph 的替代品。 |

`确认` 出现在完整可见 proposal 之后，是需要理解的语义情形；过期 request id 或 client 伪造的 `accept_suggestion` 是必须 fail-closed 的传输情形。两者不能共享一个 retry counter 或同一条错误文案。

## 第一个问题：人是否该决定？

BUG-007 建立了最重要的顺序：不要先给内部 graph decision 润色 prompt，而要先问它是否应该由人决定。正常 HITL2 route menu 被移除，就是因为 graph 已拥有继续所需事实，人并没有。

同样的审查应适用于每个未来 interrupt：

| 交互类型 | 人的正当贡献 | 系统责任 | 例子 |
| --- | --- | --- | --- |
| 告知 | 无。 | 不提问，直接继续。 | Graph 已有已验证证据来选下一 route。 |
| 请求偏好 | 目标、受众、约束、取舍。 | 解释真正缺少什么。 | 初始研究问题、来源质量限制。 |
| 确认 proposal | 授权一份完整可见的计划。 | 使对象与后果可见且当前。 | “按此研究范围开始吗？” |
| 修改 proposal | 所希望的偏好或范围变化。 | 解释、验证、展示新对象，并在必要时请求确认。 | “只用一手资料并给引用。” |
| 询问 proposal | 决定前的质疑或问题。 | 解释但不静默改变 proposal。 | “为什么是 moderate？” |
| 澄清含义 | 模糊或矛盾表达。 | 问一个最小的具体问题，保留当前对象。 | “你看着办”。 |
| 恢复 | 对已知失败 state 的回应。 | 说明观察到的失败、已做恢复和唯一合法下一步。 | Provider timeout 已耗尽有界重试。 |

这份分类避免把每一次自由文本都误认为 schema patch 或 graph command。

## 候选系统方向

### 1. 让人类交互契约拥有 Presentation Semantics

每个 human interrupt 的 owning phase 应定义一份有界交互对象，至少包含：

- 为什么此刻要问人，以及这是否真是人的决定；
- 当前关联的对象版本，以及可被确认/修改的全部 material constraints；
- 当前 state 合法的封闭人类 intent；
- 显式 control 的人类标签和后果，而不只是 machine action id；
- 清晰回复会发生什么、修改要经过什么、哪些事实保持不变；
- 语义歧义是什么、谁发出澄清问题、它消耗或不消耗哪个预算；
- 每个参与者需要的安全 status / diagnostic / recovery 事实。

Graph/checkpoint 仍拥有交互对象和 request correlation。CLI、TUI、workbench 只渲染同一契约，并提交 raw text 或可见广告的 control；它们不发明同义词、不判断修改是否实质性、不重建 action eligibility。

这是一个 **deep module** 的方向：adapters 只需学习一个小 interface；解释、验证、澄清和恢复的复杂度放在共享 seam 后面。给每个 adapter 分别加 alias 是 shallow 方案，会把下一处缺陷复制给所有 callers。

### 2. 将自然语言解释为封闭 Intent，再重新验证

完整研究 proposal 的候选 intent 集合保持很小：

```text
accept_current
request_revision(已验证的候选 delta 或明确约束)
ask_about_current_proposal
need_clarification
```

Cancel 仍是既有的显式 lifecycle control，不应靠猜一句话。JSON 或 enum-oriented profile input 可以继续支持 automation 和高级 operator，但它也必须走同一验证 / admission path，不能定义首次用户的主路径。

Semantic interpreter 只得到有界的当前交互契约和当前回复；它可以返回候选 intent、理由或候选 delta，但绝不能：

- 输出 graph route；
- 标记 checkpoint 已接受；
- 决定 cost 或 policy 是否合规；
- 创建 correlated action envelope；
- 在既有授权路径之外保留或发布 raw user content；
- 把未广告 / stale explicit control 变为合法 action。

随后 controller 验证当前已展示对象、request correlation、proposal 完整性、schema/policy 约束和实质性修改确认规则，才更新 state。核心边界是：

```text
semantic interpretation："看起来是 accept_current"
graph admission：        "当前这份 proposal 是否真的可以接受"
```

这保留现有 typed-action 设计正确的部分，却不要求人说出它的 wire protocol。

### 3. 修改、提问与歧义必须成为不同 State Outcome

下表是候选行为模型，尚不是最终 UI copy：

| 人说 | 候选人类意图 | 应立即看到的反馈 | Controller 后果 |
| --- | --- | --- | --- |
| `确认`、`可以`、`开始吧`，且刚展示过同一份完整 proposal | 接受当前 proposal | 简短回执：将按何 scope、来源标准和交付物开始。 | 只 admit 当前 correlated proposal，并开始研究。 |
| `可以，但只用...一手资料，并给出引用` | 请求修改 | 复述新增限制并展示修订后的对象。 | 验证候选 delta；不应在未经审阅的解释后静默开始。 |
| `为什么是 moderate？` | 询问当前 proposal | 回答问题，再展示不变的 proposal。 | 不修改 profile，不消耗 rejection budget，不丢失接受可用性。 |
| `你看着办` 或相互矛盾的约束 | 需要澄清 | 针对真正歧义问一个小问题。 | 保留对象并等待；不算 invalid protocol。 |
| 无效 / stale / 未广告 typed control | 传输无效 | 说明该 control 当前不可用；安全时展示当前合法交互。 | 保留既有 fail-closed 行为。 |

第一版对已解析修改的保守默认应是：

```text
修改 -> 修订后的可见 proposal -> 显式确认 -> 开始
```

这避免系统假装自己已经准确理解实质性的来源、成本或范围变化。未来可以为严格定义的非实质编辑设计 direct acceptance，但规则必须显式且可测试，不能成为 parser 的偶然副作用。

### 4. 确认必须覆盖真正重要的内容

只有人能查看实质对象时，“已确认”才有意义。Proposal view 应以安全的人类语言披露至少：

- 研究目标和预期 deliverable；
- 相关时的深度、受众、cost/time 姿态；
- must-answer questions；
- 来源标准、纳入/排除边界、引用要求、语言限制及其他 material notes；
- 修改后的影响，再要求重新确认。

这不是要求展示 raw model JSON、隐藏 field 或不安全诊断。它要求：若某条存储的 constraint 被当作用户同意的一部分，用户不能完全看不见它。

### 5. 让歧义可恢复，而不是可惩罚

当前 `profile_rejection_round` 混合了两件不同的事：

- 格式错或无法识别的字段提交；
- 尚未建立意图的普通人类语言。

候选模型把它们分开。语义歧义保留当前交互对象并请求聚焦澄清；它不能仅因用户提问或自然确认就消耗“错误 profile 回答”预算、升级成 `input.invalid_response`。

真实 parser/schema failure 仍可有有界恢复，但每个 phase 必须命名 owner 和 budget，如同 provider recovery。反馈应该说明系统听懂什么、还缺什么和唯一合法下一步；不能默认把 JSON schema 或 enum inventory 倒给新手。

### 6. Semantic Interpreter 也必须有诚实的失败路径

语义输入不等于假装理解。若 bounded interpreter 返回 malformed output、低置信 / 矛盾含义或 provider failure：

- graph 必须保留当前 proposal，不能变更 profile/action；
- phase-owned recovery 必须有明确且有界的 repair/retry policy；
- Text surface 必须给真实可见的 fallback control 或聚焦 retry/clarify path，不能回退为未文档化 magic phrase；
- 有按钮的界面可以提交明确广告的 typed action；
- 终端界面仅可把清晰标注的独立 control selection 作为降级 fallback，不能把它伪装为自然语言 alias；
- Outcome 必须区分“当前无法理解这句话”“你的回答无效”和“当前 action 已不被授权”。

具体 model/provider budget 和 terminal disposition 仍是未决设计，必须在实现前写进 owning spec，不能由 adapter 临时决定。

## 已考虑的备选方案

| 方案 | 为什么诱人 | 为什么不能解决这类 bug |
| --- | --- | --- |
| 给 `确认`、`好的`、`ok` 等增加 alias | 看起来最小。 | 不能区分接受、提问和带条件修改；依赖语言；会制造更多隐藏词汇。 |
| 每个 adapter 自己解析更多自然语言 | 不碰 graph。 | 语义 policy 复制到 CLI/TUI/workbench，行为继续漂移，graph 无法审计人实际表达的含义。 |
| 让模型直接提交 typed action 或 profile state | 看起来像真正对话。 | 解释与授权合并，模型得到它不该有的 route/checkpoint/cost 权力。 |
| 要求所有人写 JSON 或填结构化表单 | 确定性、易验证。 | 把普通研究用户当 API client，用更显式方式重造原来的信任问题。 |
| 三次失败后给更好的错误文案 | 风险低、改动小。 | 保留错误分类，仍会丢掉原交互对象。 |
| 共享的有界 intent interpretation 加 graph admission | 需要认真设计。 | 最符合既有 authority model，同时使自然语言可用、可测、跨 adapter 一致；这是推荐继续验证的方向。 |

## 候选长期 Policy：人类交互完整性

若该模式在 HITL1 之外继续成立，下列内容可成为一个聚焦的 Deep Research charter policy；目前还不是。

**触发条件：** 新增、修改或审查任何面向用户的 interrupt、approval、choice、clarification 或 recovery control。

**候选规则：** 暴露交互之前，owning capability 必须说明：

1. 这个决定是否真正由人而非 graph/agent 拥有；
2. 当前完整交互对象，以及人必须看见的 material facts；
3. 该对象合法的封闭 human intents 和 explicit controls；
4. admit 每个 intent 并更新 state 的唯一 controller；
5. semantic ambiguity、invalid input、stale/forged transport control 的区别；
6. 每种失败类的有界恢复和唯一合法 next action；
7. 所有参与 adapter 使用的共享 projection；
8. 一条证明新手可完成目标回合、无需知道 wire token 或 schema 的确定性 transcript。

**边界：** 该规则只指导 design/review；它不创建 route、permission、model invocation、state field、retry budget 或 UI control。具体行为仍由相关 capability spec 和 runtime contract 拥有。

这条候选规则能连接 BUG-001、BUG-006、BUG-007、BUG-008/010/012 与 BUG-013，却不假装它们有同一种实现。至少需要再用一个非 HITL1 interaction 或 recovery surface 反驳 / 验证它的措辞，才应进入 charter。

## 未来 Change 的证据标准

一个实施计划必须在四个不同 seam 提供确定性证据：

| Seam | 必须证明什么 |
| --- | --- |
| Intent interpretation | Scripted fixtures 将接受、修改、提问、歧义和无效 structured output 归入封闭结果集。 |
| Graph admission | current/complete/correlated proposal 可接受；stale、malformed、unadvertised、policy-invalid 均 fail-closed。 |
| Projection | 同一交互对象、action availability、material scope、反馈和合法 next action 在 CLI、TUI、workbench 一致渲染。 |
| 用户旅程 | 真实 controller/lifecycle transcript 覆盖 `确认`、一手资料/引用条件修改、“为什么 moderate？”、歧义、interpreter failure、以及反馈后的可恢复性；不依赖 credential 或 live provider。 |

现有 parser/action tests 仍然有价值，但不能替代最后一行；本次事故正是在它们全绿时发生。

## OpenSpec 之前仍需决定的事

1. 共享 contract 应有怎样的 interaction-subject / intent 类型，HITL1 是 first adopter 还是例外？
2. 哪些 profile 修改足以构成实质性变化，必须展示修订 proposal 并重新确认？
3. Proposal question 是否需要有界的独立 explanation invocation，还是可只用已有 structured proposal 回答？
4. Semantic interpretation 可接受的 provider/model failure 与 repair budget 是什么，CLI 的临时/终态 fallback 应怎样诚实表达？
5. 哪些安全的用户约束可原样回显，哪些必须摘要，如何避免敏感值进入 retained diagnostics？
6. 应扩展 `HumanInputRequest`，还是保持它 transport-only 并由新 domain module 拥有人类交互契约？
7. 候选 policy 在第二个用例检验后应进入 charter，还是先只作为第一个 owning OpenSpec change 的 requirement pattern？

## 什么才算“解决”

只有当首次用户能看见系统理解了什么、能用自然语言清晰地接受/修改/提问、能收到一句简洁真实的反馈，并能继续或得到一个聚焦澄清时，这类问题才算解决。与此同时，malformed 或 stale control 仍不能推进 graph，任何 adapter 都不必知道或教学内部 action token。

这比“`确认` 现在能用了”高得多，也正是避免下一轮缝缝补补的标准。
