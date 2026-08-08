# 人类交互契约修复计划

> 类型：已完成的实施前修复计划
> 状态：已由 `establish-human-interaction-contract` 与 `harden-hitl1-profile-interaction-lifecycle` 完成并归档
> 更新：2026-07-28
> 前置：[HITL UX 历史调研](human-interaction-remediation/deep-research-hitl-ux-history-research.md)、[语义 UX 分析](human-interaction-remediation/deep-research-semantic-hitl-ux-analysis.md)、[BUG-013](../../bugs/BUG-013-semantic-hitl-input-breaks-first-run.md)

## 本计划要达成什么

把 Deep Research 的人机交互从“用户猜协议、adapter 翻译口令、graph 接收 control”改成：

```text
用户的文字或显式 control
        |
        v
共享的人类交互契约
        |
        +--> 有界语义解释（只产生候选 intent）
        |
        v
graph-owned admission（验证对象、correlation、policy、状态）
        |
        v
统一的反馈 / 下一步 / checkpointed outcome
```

目标不是“让 `确认` 也能通过”。目标是让新手在完整 proposal 后能自然地接受、修改、提问或表达不确定；系统在听清楚时简洁继续，在不清楚时聚焦追问；而任何 graph action 仍然由确定性契约准入。

## 建议审定的产品与架构决定

以下是本计划建议作为硬约束审定的决定，不留给各 adapter 或实现过程临时解释：

1. **不再用自由文本别名授权 action。** `确认` 不会在 CLI/TUI/workbench 各自变成 `accept_suggestion`；raw text 先进入共享语义 intake。显式按钮/选择控件仍可提交当前广告的 typed action。
2. **保留 graph 的最终权威。** Interpreter 只能返回封闭的候选 intent，不能输出 route、写 checkpoint、批准 cost、伪造 request correlation 或直接提交 action。
3. **HITL1 的人类意图是封闭集。** 第一版至少区分 `accept_current`、`request_revision`、`ask_about_current_proposal`、`need_clarification`；取消维持现有显式 lifecycle control。
4. **修改总是先重新展示，再确认。** 只要自然语言被理解为修改 scope、来源标准、引用、受众、深度、cost、time 或 deliverable，就先产生一份可见的修订 proposal。第一版不做“模型认为影响不大所以直接开始”的捷径。
5. **提问和歧义不修改 profile。** “为什么是 moderate？”保留原 proposal；“你看着办”只触发一个最小澄清问题。两者不消耗字段解析失败或 profile rejection budget。
6. **解释器失败也不退回隐藏口令。** Provider/结构化输出/低确定性失败后，保留当前 proposal，给出清晰的 retry/clarify 反馈和真正可见的降级 control；不能要求用户碰巧键入某个内部别名。
7. **确认对象必须完整可见。** 来源质量、引用要求、边界、语言和自定义 note 等实质约束与枚举维度同等属于 proposal projection；用户不能确认看不见的约束。
8. **所有 adapter 使用同一交互投影。** CLI、TUI、workbench 不再各自解释 `action_ids`、维护同义词或决定恢复文案。它们只渲染共享的交互 view 并提交 raw text 或广告 control。
9. **把防复发写成准则。** 本 change 将提出并审查“人类交互完整性” charter policy；它只规定设计/审查问题，不创建 runtime authority。

## 这是旧病，不是 BUG-013 的孤立修补

这份计划的必要性来自最近一串已修 bug。它们并非同一个直接根因；但反复暴露了同一条人类交互链在不同位置的断裂，而不只是彼此独立的“UI 小问题”：

```text
人是否该决定
    -> 人看见的对象是否完整
    -> 人如何表达意图
    -> graph 如何安全准入
    -> 所有 surface 如何反馈和恢复
    -> 测试是否真的走过这条链
```

| 历史 bug | 当时修到的表层 | 本计划补上的长期机制 | 未来必须保留的回归证据 |
| --- | --- | --- | --- |
| BUG-001 | 中文字段 parser、明确接受操作、零识别反馈。 | 接受/修改/提问/歧义先成为人类 intent，不再和字段 parser 混用。 | 中文自然确认、条件修改、提问不再被当字段。 |
| BUG-006 | 可见 `id: description` 与实际 option ID 不一致。 | Visible control 与其 typed binding 来自同一交互 view，而非 adapter 自己翻译。 | 每个可见 control 的标签、后果、可提交形态与 graph admission 一致。 |
| BUG-007 | 用户被要求选内部 HITL2 route。 | 每个 interrupt 先经过“人是否真的拥有此决定”的审查。 | 不重新暴露 autonomous route；只有真实偏好/授权才问人。 |
| BUG-002、BUG-003 | 诊断和等待状态不够可操作。 | 交互反馈必须说明听懂什么、接下来发生什么、现在唯一可做什么。 | 澄清、解释器失败、terminal/retry 在所有 surface 的反馈一致。 |
| BUG-008、BUG-010、BUG-012 | Provider/recovery/diagnostic projection 分裂。 | 恢复由 phase 拥有，从同一 typed fact 投影；解释器失败同样遵守。 | 失败不接受/不修改，保留 current subject 和准确 next action。 |
| BUG-009、BUG-011 | Fixture 或控制路径没有覆盖真实前提/transition。 | 用户旅程测试必须经过真实 controller/lifecycle seam，手造 view 只能做 adapter 辅助测试。 | 每个关键语义 transcript 在真实 HITL1 lifecycle 上执行。 |
| BUG-013 | 自然确认被当字段，随后可见接受动作消失。 | 共享 interaction contract、semantic intake、完整 scope projection 与澄清路径。 | 报告现场与一次失败后的恢复均可完成研究。 |

**完成条件不是 BUG-013 绿了。** 任何实施方案若只新增“确认”别名、只改变 CLI 文案、或只通过 hand-written `AwaitingInput` 测试，就没有满足这张表，不能视为修复了旧病。

## 目标交互行为

| 用户回合 | 系统应立即反馈 | 状态后果 |
| --- | --- | --- |
| `确认` / `可以` / `开始吧`，且同一完整 proposal 刚刚可见 | 简短说明将按哪些范围、来源和交付物开始。 | Graph 仅在 proposal 当前、完整、关联正确时接受。 |
| `可以，但只采用一手资料，并给出引用` | 复述新增限制，展示修订 proposal，并请确认。 | 不开始；等待针对修订对象的确认。 |
| `为什么是 moderate？` | 解释此建议，再展示原 proposal。 | 不改 profile，不改变可接受动作。 |
| `你看着办` / 互相矛盾的限制 | 只问一个指出歧义的具体问题。 | 保留同一交互对象；不扣字段错误预算。 |
| 过期、伪造、未广告 typed control | 说明当前 control 不可用，安全时重现当前有效交互。 | 继续既有 fail-closed 行为。 |
| 语义解释器不可用或输出不合法 | 明说系统没能理解这次回复，proposal 没有改变；给可见 fallback。 | 不接受、不修改、不终止为用户错误。 |

## 目标模块与权责

| 模块 / seam | 新职责 | 明确不负责 |
| --- | --- | --- |
| `domain/` 的人类交互 contract | 定义 interaction subject、closed intent、修订/澄清/反馈结果、material visibility 与有效组合。 | 模型调用、route、checkpoint I/O、adapter 文案分支。 |
| 有界 semantic-intake adapter | 将 raw text 与当前 interaction subject 解释为已验证结构化候选结果；可给出有界解释或澄清问题。 | 直接接受 proposal、写 profile、决定 route 或 policy。 |
| `graph/nodes/hitl1` | 调用解释器、验证结果、保存最小安全交互状态、决定何时 re-propose / clarify / accept。 | 让 adapter 决定 intent，或把模型输出直接作为 action。 |
| `runtime` / `ResearchRunExperience` | 从 checkpointed/controller-owned facts 产生统一 `InteractionView`；验证已广告 control 并转交 lifecycle。 | 从 context JSON 猜 control、解释用户语义、持有第二份状态权威。 |
| CLI / TUI / workbench adapters | 展示对象、反馈、visible controls；发送 raw text 或共享 control selection。 | 词表、JSON 教学、action alias、route 或 retry policy。 |
| Charter policy | 在未来交互设计中强制提问正确的问题。 | 定义某个具体 action、retry 数量或 state field。 |

## 分阶段修复计划

### 阶段 0：把交互 contract 变成可审查的设计对象

1. 在未来 change 的 design/spec 中定义 `InteractionSubject`、`HumanIntent`、`InteractionResolution`、`InteractionFeedback` 与可见 control 的概念和 owner。
2. 明确区分三类失败：语义歧义、解释器失败、传输/关联无效；它们分别的 owner、预算、terminal disposition 和 legal next action。
3. 把现有 HITL1、CLI、TUI、workbench 的操作清单作为 migration baseline；HITL2 继续保持 agent-led，不重新引入用户 route 菜单。
4. 将上方“旧病映射表”纳入 change 的 traceability：每一个历史机制至少有一个 requirement 和 deterministic evidence seam，不能只在 proposal 中引用 bug 标题。
5. 先写红色的真实 lifecycle transcript：完整 proposal 后输入 `确认` 当前必然失败；修复后该 transcript 必须通过。

### 阶段 1：建立深的共享 domain contract

1. 在 `domain/` 建立单一的人类交互模块，令其接口接收当前 subject 和一个已验证的候选解释，返回封闭 resolution；把复杂的合法组合、材料可见性与 revision-confirmation 规则隐藏在该模块内。
2. 保持既有 `HumanInputRequest` 的 correlation/transport 职责；不要把人类语义塞进 raw context JSON 或让它成为第二个 pending-request authority。
3. 为 profile delta、source/citation boundaries、proposal question、clarification 和 interpreter-failure feedback 建立严格的长度、schema、redaction 与 checkpoint 兼容性验证。
4. 先写 domain fixture：接受、带限制修改、提问、歧义、矛盾、无效解释器输出、过期控制。它们必须可在无模型/无网络条件下运行。

### 阶段 2：加入受限的 semantic-intake invocation

1. 复用现有零工具 `NodeExecutionRequest -> NodeExecutionResult` seam，而不是另建通用聊天 agent 或修改上游 DeerFlow。
2. 定义专用、版本化、extra-forbid 的结构化输出：只允许候选 closed intent、候选 profile delta、对当前 proposal 的有界解释或一个聚焦澄清问题。
3. 语义 invocation 必须使用独立、明确的执行预算和结构化输出 repair policy；其 provider/retry disposition 由 HITL1 拥有并写入 workflow outcome review。
4. 为测试注入 scripted interpreter results；没有 credential 时仍能覆盖全部 intent 与 failure branch。
5. 输入为 explicit typed action 时跳过解释器，走既有严格 action admission；输入为 raw text 时不得在 adapter 层短路成 action。

### 阶段 3：重写 HITL1 的 admission 与 state transition

1. 保留完整原 proposal，直到它被接受、取消或以修订 proposal 替换；一次提问或模糊回复绝不能把它降级为缺字段 profile。
2. `accept_current` 仅在 request、proposal version、完整性和 policy 全部通过时落为 graph-owned acceptance。
3. `request_revision` 先经 domain validation，形成新的可见 proposal，随后等待新的确认；不静默开始。
4. `ask_about_current_proposal` 将有界解释反馈 checkpoint 化后重新广告原交互对象；不写 profile progress。
5. `need_clarification` checkpoint 化最小澄清事实，保留当前 proposal 和所有合法 controls；它不增加 `profile_rejection_round`。
6. 重新定义真正“字段/结构无效”的有界预算，使它不再吞并语义对话。旧 checkpoint 默认值必须仍可读，旧回答不可被追溯重解释。

### 阶段 4：让 projection 成为单一人类事实

1. `ResearchRunExperience` 从 controller-owned request/interaction result 投影 `InteractionView`；不再只从可丢失的 context JSON 推断 `action_ids`。
2. 交互 view 至少包含：当前对象摘要、material constraints、当前反馈、可接受的人类回应类型、visible controls、当前 legal next action、是否仍在同一 proposal version。
3. 每个 visible control 都有稳定 control id、面向人的标签/后果和与底层 typed action 的受控绑定；机器 action id 不作为普通用户语言显示。
4. 第一次解释失败、澄清或 revision 之后，仍验证可接受的 control 在 graph 和 projection 中一致存在或一致不可用。

### 阶段 5：统一 CLI、TUI 与 workbench

1. CLI 首次 proposal 用自然语言说明三条路径：可以确认、告诉系统想改什么、或问为什么；不以 JSON 和 enum 列表作为主教学。
2. CLI 的降级 fallback 是明确显示的 control selection，不是输入框内的隐藏词；共享 runtime 将 selection 安全绑定到当前广告 action。
3. TUI 保留真正的接受按钮，同时其文本输入也走 semantic intake；按钮与文本不能产生不同的 graph admission 语义。
4. Workbench 的授权 resume 继续由 broker 管理，但文本和显式 control 均消费同一 `InteractionView` / control binding；它不得自己翻译 action id。
5. 所有 surfaces 在澄清、解释器失败、修订 proposal 和 stale control 情形下呈现相同的“我听懂了什么 / 接下来发生什么 / 为什么不能开始”。

### 阶段 6：兼容性、恢复和安全披露

1. 新 checkpoint field 必须有安全 default；现有 `same_process`、restart-durable 和只读 inspection 语义不改变。
2. Semantic interpreter 的 transient provider/structured-output failure 必须有一个 phase-owned、有界恢复表；耗尽后保留 proposal，不能把用户回复标为 terminal invalid input。
3. Feedback、run summary 与 diagnostics 不保留或显示 raw user reply、完整模型 prompt、provider body、凭据、主机路径或隐藏 control 内容。
4. 取消、伪造 action、stale request、重复 delivery 继续走现有 fail-closed/control paths，不进入自然语言 fallback。

### 阶段 7：把复发防线写进治理与文档

1. 在 Deep Research charter 中提议并评审“人类交互完整性” policy：其触发条件、审查问题和非权威边界来自前置分析，不重复具体 capability 行为。
2. 更新 HITL1 / runtime / adapter 的 owning specs，使未来 change 不能只改文案或 parser 而绕开 interaction contract。
3. 更新 operator-facing demo 文档：它描述可自然表达的确认、修改和提问，不教内部 action token，不承诺 inspection 可以 resume。

### 阶段 8：按用户旅程验收，而不只按 parser 验收

1. 先保持 BUG-013 的最小红色 transcript；修复后它必须在真实 controller/lifecycle seam 通过。
2. 增加条件修改、proposal 提问、歧义澄清、解释器 malformed/provider failure、一次反馈后的接受可用性、stale/forged action 拒绝等 deterministic transcripts。
3. 对 domain、graph、runtime、CLI、TUI、workbench 各在最低责任 seam 建测试；禁止手造 `AwaitingInput` 成为唯一的 user-journey 证据。
4. 对照“旧病映射表”审查每个历史 failure class 的防回归证据；缺少任一类时，计划不能声称已经系统性收口。
5. 运行 strict OpenSpec、project architecture、requirement/spec governance 检查、focused tests 和完整 `UV_OFFLINE=1 make verify`；credentialed real demo 只作补充证据。

## 验收矩阵

| 风险 | 必须证明的结果 |
| --- | --- |
| 再次退化为 magic phrase | `确认`、条件确认等 raw text 都经共享 semantic path；adapter tests 断言没有自有 alias table。 |
| 模型越权 | Interpreter fixture 即使声称接受/route，也不能绕过 graph 的 current/correlation/policy 校验。 |
| 修改被静默误解 | 条件修改必须生成可见修订 proposal，未确认前不得启动研究。 |
| 提问误写 profile | “为什么是 moderate？”后 profile/proposal version 不变，接受 control 仍可用。 |
| 歧义再次被惩罚 | 多次澄清不消耗 profile-field rejection budget，系统只问最小必要问题。 |
| 交互对象仍不完整 | 一手资料、引用、范围与 custom notes 在确认前可见且有回归测试。 |
| Adapter 漂移 | CLI/TUI/workbench 对同一 `InteractionView` 显示相同的对象、反馈、control 与 legal next action。 |
| 恢复破坏安全 | provider failure 不接受/不修改；stale/forged action 仍 fail-closed；无 raw 敏感数据泄露。 |
| 旧运行不可读 | strict-msgpack / checkpoint compatibility 测试证明缺少新增字段的旧 checkpoint 安全默认。 |
| 准则流于口号 | charter policy 有明确 trigger、问题、边界，并由 change admission / review 使用。 |

## 范围与非目标

- 只改 `agent/`；不改 `backend/` 或 `frontend/`。
- 不做通用聊天 agent，不给模型 graph route、成本、权限或 checkpoint ownership。
- 不把所有文本字段都改成 semantic intake；初始研究问题仍是任务内容，HITL2 继续 autonomous。
- 不把 cross-process continuation、provider 全局配置或研究报告质量纳入本 change。
- 不以“更多错误提示”替代正确的 intent / admission / projection 设计。

## 建议的 OpenSpec 交接

本计划审定后，创建一个新的 change，而不是恢复已删除的草稿。建议名称：

```text
establish-human-interaction-contract
```

它应以 `domain/` 的交互语义为 primary causal owner，并修改以下 capability 的 observable contract：

- 新增 `human-interaction-contract`；
- 修改 `hitl1-node`、`node-agent-runtime`、`research-graph-lifecycle`；
- 修改 `research-run-experience`、`research-cli-onboarding`、`research-demo-tui`、`research-local-session-workbench`；
- 视 charter policy 的审查结果修改 `deep-research-agent-charter`；
- 对所有新增 checkpoint/projection field 明确兼容性和 evidence seams。

该 change 的 proposal 不应写成“支持 `确认`”。它的 done condition 应是：首次用户无需理解 schema 或 action token 也能完成一轮安全授权；不清晰的回复得到聚焦澄清而非惩罚；所有最终 action 仍由 graph 的确定性契约证明合法；未来 interaction change 必须经过同一完整性审查。

## 进入 OpenSpec 的准入条件

本计划已经决定了修复方向和边界。创建 change 前只需在 proposal/design 中把以下实现级选择具体化，而不再重开产品方向：

1. 结构化 semantic result 的精确 schema 与安全长度界限；
2. semantic-intake provider/repair/retry 的具体预算；
3. CLI 降级 control 的精确交互形态；
4. 新 checkpoint fields 的最小集合及其旧版本 default；
5. charter policy 是否与 implementation 同 change 落地，或在同一 approved design 下紧随其后。

这些是实现细节的定值，不是“是否要做共享交互契约”的重新讨论。
