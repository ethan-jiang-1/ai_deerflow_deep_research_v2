# Node Agent Capability 测试设计

> 类型：实施前测试计划。每条能力的测试必须在无 credential、无网络条件下可运行；live demo 只作补充证据。
> 更新：2026-07-27

## 测试分层

同一 capability 不能只靠“输出 JSON 能 parse”证明。建议四层共同成立：

| 层 | 使用的 fake / seam | 要证明什么 |
| --- | --- | --- |
| A. 静态结构 | AST/resource inventory、capability declaration | 每个 production request 有 local capability，MD 存在、章节完整、无 generic fallback。 |
| B. 最终消息 | pure renderer + deterministic synthetic fixture + prompt catalog | 最终 system 是 base + 正确 node-local policy；human message 的 assignment/output/untrusted section 顺序与内容正确。 |
| C. 权限执行 | `CapturingChatModel`、`ScriptedChatModel`、`ScriptedTool`，经真实 `RuntimeNodeAgentBridge` | 禁止工具的能力拿不到工具；必需工具的能力少调用会失败；每个工具姿态与 bridge enforcement 一致。 |
| D. 节点行为 | 真实 node/subgraph/lifecycle + scripted bridge/model/tool result | parser、repair、route、state、artifact 和恢复语义符合该能力；模型不能越权。 |

现有 `tests/fixtures/fake_models.py` 已有 `ScriptedChatModel`、`CapturingChatModel`、
`BlockingChatModel`；`tests/fixtures/scripted_tools.py` 已有 `ScriptedTool` 和
`scripted_web_tools()`。foundation change 应复用、补强它们，不需要真实 provider。

## 所有 capability 共同的结构测试

1. `NodeExecutionRequest` 在 production construction 时缺 capability reference 必须失败；
   测试 helper 只能显式使用 test fixture capability。
2. 每个 `graph/nodes/*/prompts.py` direct builder 都能被 inventory 找到，且其 branch 与
   local `capabilities.py` / `capabilities/*.md` / catalog case 一一对应。
3. 每份 policy 必须含 `Role`、`Method`、`Tool posture`、`Authority limits`、
   `Completion and uncertainty`；不能以改标题的 common text 逃过检查。
4. render/bridge/catalog 的 captured system message 必须逐字相同；bridge 不再接受任意
   full-system override。
5. capability posture 与 request 数值相容：`forbidden => tools_enabled=False`；
   `required => minimum_tool_calls>=1`；限制上限时 `tool_call_limit` 必须存在且足够。
6. catalog 只能使用 synthetic fixture，不能解析模型、工具、网络、真实 prompt/user data。

## 每个 branch 的最低行为证据

| Capability | C 层 fake 运行 | D 层真实 node seam | 必须断言 |
| --- | --- | --- | --- |
| `hitl1.profile_brief` | `CapturingChatModel` 返回有效 profile JSON；没有 tool resolver 调用。 | HITL1 首次 proposal path。 | system 有 profile-brief policy；proposal 仍 advisory，尚未 accepted。 |
| `hitl1.profile_brief_repair` | scripted malformed 后 valid repair JSON；零工具。 | HITL1 brief structured-output repair。 | repair 不产生 action/route/checkpoint authority；只恢复合法 profile。 |
| `hitl1.semantic_intake` | scripted candidate for `确认`、条件修改、提问、歧义；零工具。 | 完整 proposal 的真实 HITL1 lifecycle transcript。 | `确认` 可成为 candidate acceptance；修改重展示 proposal；问题/歧义不消耗 profile rejection budget。 |
| `hitl1.semantic_intake_repair` | scripted invalid candidate 再 valid clarification candidate。 | HITL1 semantic repair/recovery path。 | 不合法 route/action fields 被拒；失败保留 current proposal 和合法 fallback。 |
| `topic_planning.profile_decomposition` | capturing model 证明无工具；scripted valid plan。 | topic planning materialization。 | 所有 must-answer 被覆盖、topic 不重叠；工具 resolver 未调用。 |
| `topic_planning.plan_repair` | scripted malformed plan 后 repaired plan；零工具。 | planner output validation repair。 | repair 保留 confirmed profile、不生成外部事实、返回 contract-valid plan。 |
| `wave0.authoritative_source_intake` | `ScriptedTool` + model tool call；少于一调用时 bridge fails。 | Wave0 work-unit submission path。 | 至少一次且不超三次；结果来源可 materialize；degraded 不被伪造成 fetched。 |
| `wave0.source_intake_repair` | capturing model/zero tools，untrusted draft 注入。 | Wave0 parser repair。 | repair 不能调用 search/fetch，不能新增 draft/tool result 外的 URL/title。 |
| `wave1.evidence_extraction` | one scripted web search + model tool call。 | Wave1 work-unit path。 | 恰好一次；Wave0 URL 不重新取；claim refs 只能来自 assigned result。 |
| `wave1.evidence_extraction_repair` | zero tool + malformed draft fixture。 | Wave1 parser repair。 | 不创建新 claim/source/question；不支持时保留 open question。 |
| `wave2.evidence_synthesis` | capturing model + tool resolver trap（若调用即失败）。 | Wave2 synthesis and gap routing。 | runtime 没提供工具；findings 有 backing refs；不足时产生 gap，不编造。 |
| `wave2.synthesis_repair` | zero tool + invalid finding fixture。 | Wave2 repair path。 | 修复不添加 evidence/relations；unsupported finding 变 gap 或被删除。 |
| `targeted_evidence.gap_source_intake` | exactly one `ScriptedTool` search。 | targeted work-unit path。 | 一次 search；gap id 不变；无关证据不能标 resolved。 |
| `targeted_evidence.gap_source_intake_repair` | zero tool + malformed targeted draft。 | targeted repair path。 | 不能搜索或变更 gap；无法支持 resolved 时为 deferred/unresolved。 |
| `targeted_evidence.source_diagnostic` | `CapturingChatModel` + tool resolver trap。 | `run_source_diagnostic` / dispatcher。 | 无工具、只处理 assigned source ids、source prompt injection 不改变输出 authority。 |
| `targeted_evidence.claim_verification` | `CapturingChatModel` + tool resolver trap。 | `run_claim_verifier` / dispatcher。 | 无工具、refs 只能是 assigned refs、缺证据返回 uncertain。 |

## Prompt 语义测试不是“测试模型聪明”

确定性 fake model 不能证明真实模型永远会推理正确，但它能证明系统没有把正确行为变成
不可能：正确 policy 进入了系统消息、错误权限未被提供、输出被正确 parser/gate 消费、
repair 不越权。质量评估 change 再用固定小语料和多种 scripted output 检查能力的题面。

建议为每个 capability 建一个小型 scenario fixture：

```text
given: trusted assignment + optional untrusted data + tool transcript
when:  capability runs through the real renderer/bridge/node seam
then:  message policy, tool posture, parsed result, state effect, and prohibited effect
       are all asserted
```

其中“prohibited effect”尤其重要：HITL 不能接受/route，repair 不能新增事实，critic/synthesis
不能拿工具，检索 worker 不能绕过最小工具调用。

## 需要保留的端到端证据

以下不是每次 unit test 的替代品，而是在 foundation + HITL change 之后必须保留的真实
journey transcript：

```text
展示完整 proposal
  -> 用户输入“确认”
  -> semantic-intake capability 给出 acceptance candidate
  -> graph 校验当前 proposal 后开始 topic planning
  -> topic planner 使用自己的 zero-tool capability
  -> Wave0 使用自己的 required-tool capability
```

另一个反向 transcript：

```text
Wave2 获得不足 evidence
  -> synthesis capability 无工具、产生 gap
  -> targeted worker 以一次搜索补 gap
  -> source diagnostic / claim verifier 无工具、只评估 assigned data
```

二者共同证明不是只有一段 prompt 文本变漂亮，而是能力、权限和 graph 编排真正一致。
