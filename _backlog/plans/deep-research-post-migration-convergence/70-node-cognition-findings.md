# 70 - Node Cognition Findings

> 审计类型: 术语 / AI-facing contract / graph-to-runtime request / migration closure
> 审计基线: 2026-08-13 @ `5bb41c16a45ff3caae6e5b1e900610c91bf68336`
> 审计结论: capability 迁移已经完成，但双态 request 和 `Phase Agent` 身份仍把迁移过程当成当前架构

## 范围与权威

本审计只检查 `deep_research_harness/` 的 node cognition vertical slice 及其 current
OpenSpec/governance 投影。没有读取 `deerflow/`。术语以
`deep_research_harness/CONTEXT.md` 和 `openspec/agent-charter/concepts.md` 交叉核验，行为以
typed request、renderer、runtime bridge、20-branch evidence denominator 和 owning main specs 为证据。

当前正确的三个概念不能压成一个词：

| Concept | Canonical term | Jurisdiction |
| --- | --- | --- |
| 带模型的逻辑节点 | `LLM-Bearing Node` | 产品/架构对象；回答“这个 node 是否包含模型认知” |
| 模型可见的局部程序 | `Node Cognitive Control Program` | capability Markdown、prompt、model-visible context、feedback |
| 实现与治理分类 | `node-agent` | runtime bridge、request、Focus Card classification；不是产品身份 |

`Phase Agent` 和 `MD controller` 已由
`openspec/agent-charter/concepts.md` 明确标为 superseded。`phase` 仍可表示逻辑执行阶段，
但不能再把一个 model-bearing program 的身份命名为 `Phase Agent`。

## Finding NC-01: 退役身份仍是当前 AI-facing behavior

这不是只剩文件名或注释。当前 package policy 第一行向模型声明
`Deep Research Phase Agent`，renderer tests 明确保护这段身份；factory name、exception type、
renderer symbol、runtime bridge docstring、main specs 和 requirement registry 同时使用旧词。因此
局部 rename 会留下新的双名期，必须做一次从模型策略到治理证据的 vertical rename。

证据：

- `deep_research_harness/src/deerflow_deep_research/resources/node_agent/runtime_policy.md`
- `deep_research_harness/src/deerflow_deep_research/agents/phase_prompt.py`
- `deep_research_harness/src/deerflow_deep_research/agents/factory.py`
- `deep_research_harness/src/deerflow_deep_research/agents/middleware.py`
- `deep_research_harness/src/deerflow_deep_research/agents/policies.py`
- `deep_research_harness/src/deerflow_deep_research/agents/structured_output.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py`
- `deep_research_harness/tests/unit/test_phase_prompt.py`
- `deep_research_harness/tests/unit/test_node_agent_bridge.py`
- `openspec/specs/node-agent-runtime/spec.md`
- `openspec/specs/node-prompt-catalog/spec.md`
- `openspec/governance/req-registry.yaml` 中 `NOA-001/002/005/006/010` 描述

影响：

- model-facing identity 与 product glossary 冲突；
- tests 让旧身份成为受保护行为，普通 residual scan 无法把它识别为 residue；
- `node-agent`、`phase agent`、`LLM-Bearing Node` 看似同义，实际混合了产品对象、认知程序和
  runtime mechanism 三个层次。

## Finding NC-02: 20 个 direct branch 已迁移，request 仍保留无人使用的 legacy cohort

`NodeExecutionRequest` 仍有：

```text
capability_binding: "legacy" | "required" = "legacy"
capability_ref: NodeAgentCapabilityRef | None = None
```

当前生产源码有 17 个 `NodeExecutionRequest(...)` construction expressions；参数化 builder 将它们
投影为 20 个 canonical direct branches。17 个 construction expressions 全部显式传入
`capability_binding="required"` 和 `capability_ref`，没有生产 builder 显式构造 `legacy`。
`tests/assets/node_agent_capabilities.py` 也把 denominator 封闭为 20 个 unique direct cases。

该 request 是 graph-to-agents/runtime 的进程内 typed contract：它没有从 package top level export，
没有 Bundle State serializer，也没有 Evaluation Bundle serializer。当前仓库内没有发现外部格式、
配置或持久化 consumer。因而 `capability_binding` 是 declared cross-boundary internal field，而不是
public/persisted migration field。

证据：

- `deep_research_harness/src/deerflow_deep_research/domain/context.py`
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/**/prompts.py`
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/final_delivery/composer.py`
- `deep_research_harness/src/deerflow_deep_research/graph/nodes/readiness/critic.py`
- `deep_research_harness/src/deerflow_deep_research/agents/phase_prompt.py`
- `deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py`
- `deep_research_harness/src/deerflow_deep_research/__init__.py`
- `deep_research_harness/tests/assets/node_agent_capabilities.py`
- `deep_research_harness/tests/graph/test_node_agent_capability_cohort.py`
- `deep_research_harness/tests/domain/test_node_agent_capability.py`

目标 contract 应只表达终态：每个 `NodeExecutionRequest` 必须有一个
`NodeAgentCapabilityRef`；缺失或无效 ref 在 render、model construction 和 tool resolution 前失败。
不应再由调用者同时声明一个可从 ref presence 推导出的 `required` discriminator。

## Finding NC-03: Main spec 把已完成迁移叙述成当前时间层

`node-agent-capabilities/spec.md` 同时保留：

- `legacy` / `required` 双态 contract；
- first cohort 的 6-row 状态；
- second/next cohort 的 8/14-row 状态；
- final cohort 的 18-row 状态；
- 后续 final-delivery closure 后实际 20-row current denominator。

这些内容可作为 archived change 的历史，但不适合作为 main spec 的 current required behavior。
main spec 应描述 current closed 20-branch capability contract，并把迁移批次和临时 legacy set 从
current requirements 中移除。行为不应因文本收敛而改变：capability metadata validation、四层 prompt
composition、tool posture admission、20-row evidence、deterministic owner 和 failure boundary 都必须保留。

证据：

- `openspec/specs/node-agent-capabilities/spec.md`
- `openspec/specs/cognitive-program-evidence/spec.md`
- `openspec/specs/node-prompt-catalog/spec.md`
- `deep_research_harness/tests/assets/node_agent_capabilities.py`
- `deep_research_harness/tests/graph/test_cognitive_program_evidence.py`

## Finding NC-04: Product glossary 尾部混入了可独立拥有的设计论证

`deep_research_harness/CONTEXT.md` 在 glossary 之后的 `People Initiate Evaluation Review`、
`Reviews Are Separate Immutable Records`、`Review Records Are Traceable`、
`Rubrics Are Case-Specific Review Authorities`、`Evaluation Control And Run Data Are Separate` 和
`The Cognitive Control Program Is The First Modification Seam` 是设计/行为陈述，不是术语定义。

相同决策已经分别有 ADR、cognitive evaluation specs 和 local-context policy owner。继续把这些段落
放在 glossary 中，会让 `CONTEXT.md` 成为第二份设计 authority。应保留所有 glossary term 与
`_Avoid_`，把仅有的 current 路由补到 owning document 后再删除非词典尾部；不能为了缩短文件而
丢失独有语义。

证据：

- `deep_research_harness/CONTEXT.md`
- `deep_research_harness/docs/adr/0011-node-cognitive-control-is-a-first-class-program.md`
- `deep_research_harness/docs/adr/0022-people-initiate-evaluation-review.md`
- `deep_research_harness/docs/adr/0023-reviews-are-separate-immutable-records.md`
- `deep_research_harness/docs/adr/0024-review-records-are-traceable.md`
- `deep_research_harness/docs/adr/0025-rubrics-are-case-specific-review-authorities.md`
- `deep_research_harness/docs/adr/0026-evaluation-control-and-run-data-are-separate.md`
- `openspec/specs/cognitive-evaluation-suite/spec.md`
- `openspec/policies/local-context.md`

## 最终审计 Candidate

### NC-C01 - Close node capability migration

- **证据**: `domain/context.py`; all production `graph/nodes/**/prompts.py`;
  `graph/nodes/final_delivery/composer.py`; `graph/nodes/readiness/critic.py`;
  `tests/assets/node_agent_capabilities.py`; `node-agent-capabilities/spec.md`。
- **当前 owner**: `NodeExecutionRequest.capability_binding` 与
  `node-agent-capabilities` 的 time-layered cohort requirements。
- **目标 owner**: required `NodeExecutionRequest.capability_ref`；agents loader 和 runtime bridge
  继续拥有 pre-model validation；20-branch evidence ledger 继续拥有 denominator。
- **Disposition**: `delete`。
- **迁移条件**: 先加入缺失 `capability_ref` 在 request construction/render 前失败的 red test；确认
  20 catalog cases 与 17 construction expressions 全部显式提供 ref；更新 NAC/NOA/NPC evidence。
- **删除条件**: 生产、tests 和 current specs 不再读取/写入 `capability_binding`；main spec 不再包含
  临时 legacy set 或 cohort 时态；focused tests、20-row joins、strict OpenSpec 和 governance 通过。
- **保留负向护栏**: invalid/missing/package-mismatched capability 在 model/tool work 前失败；禁止
  capability inference、generic fallback、arbitrary system prompt override 和 capability-owned route/state。
- **OpenSpec change slice**: `close-node-capability-migration`，建议作为本计划第一个实施 change。

### NC-C02 - Converge node cognition language vertically

- **证据**: `resources/node_agent/runtime_policy.md`; `agents/phase_prompt.py`;
  `agents/factory.py`; `agents/middleware.py`; `runtime/node_agent_bridge.py`;
  `tests/unit/test_phase_prompt.py`; NOA/NPC specs 与 registry。
- **当前 owner**: retired `Phase Agent` identity 分散在 model policy、Python symbols、tests 和 specs。
- **目标 owner**: product identity 使用 `LLM-Bearing Node`；model-visible/local cognition 使用
  `Node Cognitive Control Program`；runtime/governance mechanism 使用 `node-agent`。
- **Disposition**: `rename`。
- **迁移条件**: 先批准一张 bounded term table；逐个区分 product text、model-facing text、private
  symbol 和 requirement prose；确认没有外部 Python import promise。
- **删除条件**: current code/model policy/tests/main specs/registry 不再把 `Phase Agent` 当 current
  identity；residual 只允许 archive、明确的 retired-term guard 或逻辑 phase 的非 identity 用法。
- **保留负向护栏**: full-takeover、no checkpointer、bounded budgets、closed tools、redaction、
  cancellation、no clarification、deterministic admission 与 graph-owned lifecycle 均保持原测试强度。
- **OpenSpec change slice**: `converge-node-cognition-language`；应在 NC-C01 后独立实施，避免把
  contract subtraction 与 AI-facing rename 混成一个不可诊断 change。

### NC-C03 - Restore CONTEXT to glossary-only ownership

- **证据**: `deep_research_harness/CONTEXT.md` glossary 后六个设计章节；ADR 0011、0022-0026；
  cognitive evaluation specs；`openspec/policies/local-context.md`。
- **当前 owner**: `CONTEXT.md` 非词典尾部与 ADR/spec/policy 重复承担设计陈述。
- **目标 owner**: `CONTEXT.md` 只拥有 current terms 和 `_Avoid_`；durable decision 留在 ADR；
  required behavior 留在 owning specs；edit routing 留在 charter policy。
- **Disposition**: `migrate then delete`。
- **迁移条件**: 为六段逐段建立语义对照；任何独有 current rule 先写入正确 owner；确认 docs/charter
  入口可到达该 owner。
- **删除条件**: 非词典段落没有独有 current requirement，删除后 glossary definitions 完整且引用不坏。
- **保留负向护栏**: 不删除任何 canonical term、状态标签或 `_Avoid_`；不把 glossary 迁移成另一份
  永久术语 registry；ADR 历史保持不改写。
- **OpenSpec change slice**: 随 `converge-node-cognition-language` 同批做 documentation ownership
  closure，不单独创建纯格式 change。
