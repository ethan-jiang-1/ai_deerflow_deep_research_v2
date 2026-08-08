# BUG-013: HITL1 将自然确认当作字段数据，阻塞首次真实研究

> 严重级别: P0 | 发现: 2026-07-26 | 状态: 已修复（2026-07-31，已验证回归）

## 症状

真实入口 `make demo-real` 在已经展示完整研究建议后，要求用户“确认或修正”。
用户输入在该上下文中自然且明确的“确认”时，CLI 不会将其理解为接受当前建议，
而是把它作为 profile 字段文本提交。三次零识别输入后，图在 `hitl1` 终止；研究
从未进入 topic planning、检索或报告阶段。

现场 run `r_y5hkuk0XU3qQN18yMayBxgWWiNF2x3gqG5k4QOj5xR4` 的保留
`run-summary.json` 记录 `blocked@hitl1`、`failure_category=input.invalid_response`
和诊断引用 `diag_sXTfvC54yIHQYfDvJyXu3O1Q`。其生命周期记录显示三次
`suspended@hitl1` 后才成为 blocked；事件 #20 以相同的闭合 failure code 终止。
保留记录有意不存储原始回答，故原始“确认 / 趣确认 / 确认”序列以用户提供的 CLI
transcript 为准，bundle 只验证该终态和阶段。

这是 P0，而不只是文案问题：它阻断了面向中文首次使用者的主研究工作流，且发生在
任何实际研究工作之前。run 的 durability 是 `same_process`，进程结束后只能检查，
不能从该记录继续；唯一已知绕过是用户碰巧输入 adapter 的精确口令或手写完整 JSON。

## 根因

这是意图、展示和受控传输协议三层脱节，而不是模型生成失败或中文枚举别名遗漏。

1. real CLI 只有在文本**精确等于** `采用建议` 且 `PromptView` 广告
   `accept_suggestion` 时，才构造 correlated typed action；其他非空文本一律成为
   `AnswerRun(value=<文本>)`。见
   [`demo_real.py`](../../../deerflow_research/scripts/demo_real.py#L115-L129)。
2. typed action 的严格性本身是正确的授权边界：plain text 不能伪造 action，只有
   当前 pending request 广告的 action 才能通过。见
   [`human_input.py`](../../../deerflow_research/src/deerflow_deep_research/runtime/human_input.py#L244-L257)。
   但 `确认` 没有先经过“接受当前建议 / 修改偏好 / 需要澄清”的意图分流，而是直接落入
   profile parser。
3. profile parser 只识别封闭枚举短语及英文 `must answer` 形式；`确认` 和
   `采用建议` 都没有可识别 profile field。见
   [`profile.py`](../../../deerflow_research/src/deerflow_deep_research/domain/profile.py#L253-L283) 和
   [`profile.py`](../../../deerflow_research/src/deerflow_deep_research/domain/profile.py#L326-L361)。
   只读探针确认两者的 `recognized_fields` 都是空元组。
4. 零识别会增加 `profile_rejection_round`，第三次直接生成
   `input.invalid_response` 的 blocked terminal。见
   [`hitl1/node.py`](../../../deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/node.py#L490-L519)。
   这正是现场三次后终止的机制，而非 BUG-006 式的错误分类掩盖。
5. 第一次零识别还会抹掉唯一简单恢复路径的可见 affordance：
   `build_followup_context()` 不含 `action_ids`，而 run experience 只从 context
   投影 `PromptView.action_ids`，不从已验证的 pending request 读取它。见
   [`prompts.py`](../../../deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/prompts.py#L135-L155)
   和 [`run_experience.py`](../../../deerflow_research/src/deerflow_deep_research/runtime/run_experience.py#L614-L659)。
   CLI 随后不再显示“采用建议”，也不会把用户后来输入的同一句转换成 typed action。

因此修复不能把任意自然语言直接升级为授权 action，也不能只添加“确认”的字符串别名。
它需要在保留 correlated typed action、闭合 profile 枚举和图拥有最终权限的同时，让
用户能明确表达、系统能解释并在不清楚时可追问其 HITL1 意图。

## 影响

- 用户看见“确认研究范围”“请确认或修正”后给出常规确认，系统却要求其猜测一个
  特殊口令或手写 JSON；提示前后的心理模型不一致。
- 第一次误解就把接受建议的可见操作从下一轮 CLI 中移除，反馈只剩“使用可用值或完整
  JSON”，没有解释系统保留了什么建议、是否还能接受它、或怎样以普通语言继续。
- 真实 provider、topic planning 和搜索并非本次失败原因；用户会把前置交互失败误判为
  “研究质量差”或“模型不可靠”。

## 复现

现场命令和问题：

```bash
cd /Users/bowhead/ai_deerflow_deep_research/deerflow_research
make demo-real DEMO_ARGS='--question "OpenSpec 的普及程度、正面与负面影响；只采用有影响力团队或社区的一手资料，并给出引用。"'
```

当 HITL1 显示完整建议、`操作: 输入 采用建议 以接受当前建议。`，且同时说“请确认或
修正建议范围”时，依次输入现场记录中的 `确认`、`趣确认`、`确认`。等价的最小语义
复现是连续三次输入 `确认`。实际结果是 `input.invalid_response` 和退出码 `1`；预期是：
清晰确认应被引导到受控接受操作，或在确有歧义时收到说明具体缺什么的澄清问题，不能
静默消耗三次零识别预算。

只读核验现场终态：

```bash
make demo-sessions DEMO_ARGS="inspect r_y5hkuk0XU3qQN18yMayBxgWWiNF2x3gqG5k4QOj5xR4"
```

预期输出包含 `Summary: blocked@hitl1` 和上述 diagnostic reference；该命令不继续执行。

## 历史关联

- [BUG-001](BUG-001-hitl1-localized-intake-and-confirmation.md)
  是同一阶段的前序问题：它解决了中文 profile 值、明确 action 和零识别反馈，但把
  “采用建议”作为 presentation adapter 的精确映射。当前缺口是该方案没有涵盖自然确认
  意图，因而是其遗留的契约缺口，不是回到英文-only parser。
- [BUG-006](BUG-006-demo-hitl2-choice-is-masked-as-protocol-fault.md)
  有同样的结构性相似：人类可见交互与机器可接受值不一致。不同在于 BUG-006 发生在
  fake HITL2，且有效的 `response_invalid` 被展示层误报为 `protocol.invalid_result`；本
  bug 的类别从节点到终端都准确为 `input.invalid_response`，问题在意图承接和恢复
  affordance，而非 failure projection。
- [BUG-007](BUG-007-hitl2-decision-lacks-actionable-context.md)
  说明“不要让用户操作图内部控制词”的共同产品原则。它通过让 HITL2 自动推进来修复；
  本 bug 不能照搬自动接受，因为研究范围、成本和受众仍是合法的用户授权边界。需要的
  是可理解的用户确认/修正交互，再绑定到 typed action。
- [BUG-010](BUG-010-topic-planning-timeout-is-masked.md)
  仅共享 real-demo 命令和后续 phase；它发生在已接受 profile 之后的 provider timeout，
  不解释也不修复本次 pre-topic-planning 阻塞。

## 修复与验证

归档 change `establish-human-interaction-contract` 已完成这个交互契约：语义 intake 只产生
受限 candidate，HITL1 仍是 profile 写入、相关性与 route 的唯一权威。它没有增加“确认”
字符串别名，也没有把自由文本升级为 action。当前
`harden-research-run-diagnostics-and-hitl-intake` 的任务 1.7 将这张卡的场景登记为独立回归。

- `tests/graph/test_hitl1_node.py::test_natural_confirmation_writes_current_proposal_and_routes_accepted`
  以 `确认，按这个方案开始吧。` 证明只写入当前 checkpointed proposal；中央 claim
  `hitl1-complete-response` 属于 `FAST` / `real-node-fake-capabilities`。
- `tests/integration/test_hitl1_lifecycle.py::test_mixed_hitl1_natural_confirmation_adopts_the_visible_proposal`
  经过真实 mixed HITL1 lifecycle 证明该 proposal 可被接受。
- 2026-07-31 的本 change focused suite 通过 228 项测试。

这是一条确定性准入/控制权回归，不宣称脚本化 candidate 证明真实语言模型的中文理解质量，
也不属于 live provider-quality 证据。
