# Plan: Deep Research Model Structured-Output Boundaries

> 类型: 架构审计 / 治理 | 更新: 2026-07-22
> 结论: 不立独立 Change；Python/LangGraph 保持控制权，模型结构化输出只在节点数据边界受控消费
> 状态: 分析完成，移入 `_done/_closed_plans/` 后作为未来节点设计的复查记录

## 结论

最初的问题来自“Markdown 或 agent 输出的 YAML/JSON 会不会成为 controller”。对当前
DeerFlow Deep Research，这不是主风险：流程由 Python 和 LangGraph 的显式节点、固定
conditional edge、受 writer-role 约束的 state reducer 共同控制。模型不能直接返回任意
`route`、phase、gate、ledger 或 checkpoint 更新。

当前也没有生产代码把 Markdown 标题、表格、fenced block 或 YAML 当作控制指令解析。最终
`report.md` 由确定性 writer 生成；LLM writer 仍是 deferred。模型输出 YAML 没有实际消费
路径。因此，不应增加一个泛化的 Markdown/YAML/JSON linter，更不应让 Markdown 成为流程
控制协议。

真正需要保留的规则是：**任何由模型生成、且会被程序消费的结构化数据，都必须在节点本地
经过显式 parse、Pydantic schema、语义/identity 校验和受控权威投影；模型文本本身永远
不是控制权威。**

```text
model text / JSON
        |
        v
node-local parser + frozen Pydantic contract
        |
        v
semantic / identity / evidence validation
        |
        v
deterministic materializer or submit boundary
        |
        v
controller/gate-owned state update -> fixed LangGraph route
```

## 已有真实边界

旧计划“sub-agent 还没有可 lint 的结构化输出”的前提已经过时。当前真实节点已消费如下
模型 JSON；这些都不是 Markdown controller：

| Surface | 结构化消费 | 控制影响与现有约束 |
|---|---|---|
| HITL1 brief | JSON -> `StructuredBrief` | 仅为建议；最终 profile 仍来自经校验的人类响应。首次无效后修复一次，二次失败 blocked。 |
| Topic planning | JSON -> `TopicPlan` -> deterministic topic ids/coverage | 可影响 Wave0 fan-out，但模型不能提供 topic id、route 或 state authority。 |
| Wave0 / Wave1 workers | JSON -> typed worker output -> canonical result -> submit validation | 只能形成候选证据；submit 再验证 result contract、身份、hash、路径和 ledger，模型不能直接写 ledger 或 gate。 |
| Wave2 synthesis | JSON -> `SynthesisResult` + evidence-ref semantics -> `Wave2GatePreview` | `search_required` 是控制敏感数据，但只能先生成 preview，再由确定性 gate 决定 `evidence_needed` 或 `pass`。 |
| Targeted evidence | JSON -> assigned-gap validation -> canonical result/submission | 必须保持 assigned gap identity；首次无效后以无工具 repair 重试，失败不发布部分权威。 |
| Source / claim critics | JSON -> typed critic contracts | 当前是受限审查数据，不直接决定 lifecycle route；接入新的运行时控制前应复核下面的 checklist。 |

`RuntimeNodeAgentBridge` 目前只将最后一条 AI message 投影为有字节上限的 `summary`；它不
统一解析各节点 schema。这个选择是合理的：不同节点需要不同的语义检查、repair prompt、
untrusted-draft 范围和权威 materializer。`ExecutionPolicy.structured_output_type` 仍是未
启用的预留槽，不应仅为“统一 lint”而贸然接通 provider-native structured output。

## 必须保持的节点规则

每个新增或修改的模型结构化输出消费点都应在设计/代码审查中回答以下问题：

1. **显式 schema**：是否使用版本化、冻结、`extra="forbid"` 的 Pydantic contract，且拒绝
   非 object、未知字段、越界值和未支持的 schema version？
2. **语义校验**：除 schema 外，是否验证输入绑定、identity、引用闭合、内容 hash、路径
   containment 或其他该节点真正依赖的语义？
3. **有限 repair**：无效初稿是否至多触发一次、工具关闭的 repair；draft 和 validation
   metadata 是否作为 untrusted data 被严格限长，而不是变成新指令？
4. **失败关闭**：二次无效、wrong identity 或非成功 bridge 结果是否不会写 artifact、ledger、
   checkpoint authority 或部分 route state，并转为已有的受控 failure/gate 路径？
5. **确定性控制投影**：若字段会影响后续工作或路由，是否由 Python materializer/gate 从
   已验证对象派生，而不是直接使用模型给出的 phase、route、gate feedback 或 ledger 字段？
6. **最低责任测试**：是否至少有 valid、malformed/extra-field、语义绑定失败、repair success、
   repair exhaustion/no-partial-authority 的确定性覆盖？

人类自由文本、模型自然语言解释和最终 Markdown 报告不属于这套协议。它们可以是内容数据，
但不得被正则、标题或表格解析为 route、phase、gate、ledger 或 checkpoint authority。

## 现有证据

- LangGraph 的 conditional edge 映射是固定枚举，见
  `agent/src/deerflow_deep_research/graph/builder.py`；模型不能新增边。
- `apply_research_update` 限制 controller/gate/submit/planner 的 writer authority，见
  `agent/src/deerflow_deep_research/domain/state.py`。
- HITL1、topic planning、Wave0/Wave1、Wave2 和 targeted evidence 分别有 JSON parser、
  Pydantic contract、repair 或 fail-closed 测试；worker artifact 在 submit 边界还会再按
  registered result contract、hash 和 containment 验证。
- `test_hitl1_lifecycle.py`、`test_topic_planning_lifecycle.py`、
  `test_zero_tool_node_conformance.py` 和 `test_targeted_evidence_real.py` 覆盖反复坏输出
  不发布部分权威结果的代表性路径。

## 不做的事

- 不把 Markdown、YAML 或自然语言当作通用控制协议，也不做全局文本 linter。
- 不把配置文件严格键校验、root `config.yaml` 模型策略、`backend/` 配置 ownership 与节点模型
  输出混成同一个 Change；它们是独立问题且超出 downstream `agent/` 路线边界。
- 不在当前 bridge 上统一启用 `with_structured_output` 或 `structured_output_type`。这会改变
  tool-calling、节点专属 repair 和 raw-draft untrusted-boundary，需要独立设计与 Change。

## 延后复查触发器

只有发生下列任一事件时，才重新打开一个专门 Change：

- 新模型节点消费结构化输出，但无法满足上述六项规则；
- 模型输出新增控制敏感字段，例如 rerun scope、gate preview、用户可见 lifecycle decision；
- 要采用 provider-native structured output，并需要与现有 tool loop、repair、redaction 和
  fallback 语义兼容；
- SourceDiagnostic / ClaimVerifier 等 critic 路径被接入新的 runtime control 影响。届时先补
  `NodeExecutionResult` success 检查、明确的 schema-invalid failure/repair 策略和 no-partial-
  authority 测试，再允许其影响控制面。

这份计划的结论已被当前架构审计吸收；没有立即需要实施的泛化 linter，因此不保留为 active
plan。
