# 当前 Node Agent Invocation 全量盘点

> 类型：事实调研 / 架构 baseline
> 更新：2026-07-27
> 口径：只统计生产 graph 中实际可到达 `NodeExecutionCapabilities.run_agent()` 的 branch；测试 helper 单独列为迁移影响，不算产品能力。

## 结论摘要

当前 Deep Research 的 agent 不是“每个 node 一个 agent”，而是：

```text
16 个 branch 的动态 Objective / Expected output
                    │
                    v
    同一个 runtime_policy.md system prompt
                    │
                    v
    RuntimeNodeAgentBridge -> build_node_agent()
```

`NodeExecutionRequest` 只有 `objective`、`expected_output`、source artifact refs 和工具
数值字段；它没有 capability ID、node-local policy reference 或工具姿态。`RuntimeNodeAgentBridge`
默认从同一包资源读取 system policy，并允许 `system_prompt` 字段整体覆盖它。

因此“这个 agent 是谁、应如何思考”当前不是可验证的系统事实，而是散落在每个 Python
字符串中的约定。

## 图级范围

| 注册 node | 当前模型状态 | 理由 / 证据 | 本计划处理 |
| --- | --- | --- | --- |
| `bootstrap` | 无模型 | `node.py` 明确写“performs no research model call”。 | 显式 no-agent；不加 prompt。 |
| `hitl1` | 有模型 | profile brief、semantic intake 通过 `run_agent`。 | 4 个 branch 全部迁移到 local capability。 |
| `topic_planning` | 有模型 | planner 及 validation repair 通过 `run_agent`。 | 2 个 branch 迁移。 |
| `wave0` | 有模型 | work-unit source intake worker 及 repair 通过 `run_agent`。 | 2 个 branch 迁移。 |
| `wave1` | 有模型 | work-unit evidence worker 及 repair 通过 `run_agent`。 | 2 个 branch 迁移。 |
| `wave2_synthesis` | 有模型 | synthesis 及 repair 通过 `run_agent`。 | 2 个 branch 迁移并纠正工具矛盾。 |
| `targeted_evidence` | 有模型 | targeted worker、repair、source diagnostic、claim verifier 均调用 `run_agent`。 | 4 个 branch 迁移并纠正 critic 工具矛盾。 |
| `hitl2` | 无模型 | `recommend_hitl2_route()` 为 graph-owned deterministic recommendation。 | 保持 no-agent；不能因名字像 HITL 而加 prompt。 |
| `rerun` | 无模型 | `planner.py` 是 deterministic scope/routing logic。 | 保持 no-agent。 |
| `readiness` | 无模型（deferred） | `critic.py` 明确是 deterministic fallback，真实 agent loop deferred。 | 先记录 future admission，当前不创建假 capability。 |
| `final_delivery` | 无模型（deferred） | `writer.py` 明确是 deterministic formatter，LLM writer deferred。 | 先记录 future admission，当前不创建假 capability。 |

## 共同运行链与当前缺口

| 环节 | 当前 owner | 当前行为 | 缺口 |
| --- | --- | --- | --- |
| 角色 policy | `agents/resources/node_agent/runtime_policy.md` | 所有 branch 读同一份“bounded node agent”文字。 | 没有 node 独有角色、方法、成功标准或工具策略。 |
| 动态任务 | `graph/nodes/**/prompts.py` | 将角色、任务、数据、修复规则和 schema 组合为长 `objective` 字符串。 | 静态 policy 与动态 assignment 混合，审查和重用都困难。 |
| request contract | `domain/context.py::NodeExecutionRequest` | 仅含字符串和工具数值，无 capability。 | runtime 无法验证“此请求应是什么 agent”。 |
| 执行 | `runtime/node_agent_bridge.py` | 按 `tools_enabled` 解析工具，调用共享 renderer / node agent。 | `system_prompt` 可替换整个 policy；默认 `tools_enabled=True` 会掩盖 node 的意图。 |
| 审计 | `agent/node_prompts/` | 正确 dump 所有 case 的最终 system/human message。 | 它证明 system 层相同，却还不能证明 branch 有独立 capability。 |

## 实际模型调用 branch

下表把每一行都当作未来一个明确 capability。`当前工具`是 request 字段的实际值，
不是 prompt 文字的愿望；`已确认问题`只记录源码已能证明的事实。

| Node / branch | 当前 builder 与调用位置 | 当前模型工作 | 当前工具 | 当前静态 policy | 已确认问题 |
| --- | --- | --- | --- | --- | --- |
| `hitl1/profile-brief` | `hitl1/prompts.py::build_brief_prompt`; `hitl1/node.py` | 从原始研究问题提出 advisory structured profile。 | 禁用。 | 通用 runtime policy。 | profile 建议的角色/保守性/不确定性只在 Objective。 |
| `hitl1/profile-brief-repair` | 同 builder 的 `repair_error` branch。 | 修复不合法 brief JSON。 | 禁用。 | 同上。 | repair 与首次生成拥有不同任务，却没有独立 policy。 |
| `hitl1/semantic-intake` | `build_semantic_intake_prompt`; `hitl1/node.py` | 将完整 proposal 上的自然语言回复归为封闭候选 intent。 | 禁用。 | 同上。 | 这是 UX 主路径，却没有“对话理解但无 graph authority”的系统级能力。 |
| `hitl1/semantic-intake-repair` | 同 builder 的 `repair_error` branch。 | 修复不合法 semantic candidate。 | 禁用。 | 同上。 | repair 指令仍混在动态 Objective；失效时难审查其不越权边界。 |
| `topic_planning/plan` | `topic_planning/prompts.py::build_planner_prompt`; `node.py` | 将 confirmed profile 分解为有覆盖、互斥的研究 topic。 | 默认启用，无最小/最大限制。 | 通用 runtime policy。 | 当前没有声明 planner 是否应该使用工具；角色和 topic 方法只在 Objective。 |
| `topic_planning/plan-repair` | 同 builder 的 `repair_error` branch。 | 修复 validation failed 的 topic plan。 | 默认启用，无最小/最大限制。 | 同上。 | repair 与常规 planner 的工具/方法没有区分。 |
| `wave0/source-intake` | `wave0/prompts.py::build_wave0_worker_prompt`; `subgraph.py` | 广度优先找权威来源并记录元数据。 | 启用；至少 1、最多 3。 | 通用 runtime policy。 | 最重要的 source strategy 在 Objective；capability 无独立可审查定义。 |
| `wave0/output-repair` | `build_wave0_repair_prompt`; `subgraph.py` | 从 untrusted draft/tool result 仅恢复符合 schema 的 source intake 输出。 | 禁用。 | 同上。 | “不得补造来源/事实”的 repair 原则没有独立 policy。 |
| `wave1/evidence-extraction` | `wave1/prompts.py::build_wave1_worker_prompt`; `subgraph.py` | 在 Wave0 baseline 外作一次检索、抽取 claims 和 open questions。 | 启用；至少 1、最多 1。 | 通用 runtime policy。 | 新来源/claim/counter-evidence 方法只有动态文字。 |
| `wave1/output-repair` | `build_wave1_repair_prompt`; `subgraph.py` | 从已有 untrusted draft/tool result 仅修复 Wave1 schema。 | 禁用。 | 同上。 | repair 无独立认知/证据限制 policy。 |
| `wave2_synthesis/synthesis` | `wave2_synthesis/prompts.py::build_synthesis_prompt`; `node.py` | 只用 accepted evidence 形成 findings、relations、gaps。 | **实际默认启用**，无 call limit。 | 通用 runtime policy。 | Objective 写“NO web tools”，与实际工具请求矛盾。 |
| `wave2_synthesis/output-repair` | `build_synthesis_repair_prompt`; `node.py` | 从 draft 和 accepted evidence 修复 synthesis JSON，禁止编造。 | 禁用。 | 同上。 | repair policy 未独立；文字甚至需依赖 human message 才能限制工具。 |
| `targeted_evidence/gap-intake` | `targeted_evidence/prompts.py::build_targeted_worker_prompt`; `subgraph.py` | 为一个 synthesis gap 做一次目标检索，记录来源与限制。 | 启用；至少 1、最多 1。 | 通用 runtime policy。 | gap 的研究策略、resolved/deferred/unresolved 的诚实标准不在 capability 层。 |
| `targeted_evidence/output-repair` | `build_targeted_worker_repair_prompt`; `subgraph.py` | 不搜索、不加事实，只将已有 draft 改成目标 schema。 | 禁用。 | 同上。 | repair 角色没有独立 prompt asset。 |
| `targeted_evidence/source-diagnostic` | `build_source_diagnostic_prompt`; `subgraph.py::run_source_diagnostic` | 评估每个来源的信任层级、materiality、marketing risk、交叉验证需要。 | **实际默认启用**，无 call limit。 | 通用 runtime policy。 | 模块注释称两个 critic 都 read-only/no tools，request 却允许工具。 |
| `targeted_evidence/claim-verifier` | `build_claim_verifier_prompt`; `subgraph.py::run_claim_verifier` | 对 assigned evidence 给每个 claim supported/weakened/contradicted/uncertain verdict。 | **实际默认启用**，无 call limit。 | 通用 runtime policy。 | 同样与 read-only/no-tools 文字矛盾，且证据归因方法未系统化。 |

## 现有生成目录与源码的对应

`agent/node_prompts/` 当前已经有上述 16 个 case。它们按下列 ID 生成：

```text
hitl1/{brief,brief-repair,semantic-intake,semantic-intake-repair}
topic-planning/{plan,plan-repair}
wave0/{worker,repair}
wave1/{worker,repair}
wave2-synthesis/{synthesis,repair}
targeted-evidence/{worker,repair,source-diagnostic,claim-verifier}
```

这份命名是有价值的 inventory baseline，但它不是能力定义：其中 `worker`、`repair`
过于泛化，不能仅凭目录名告诉读者 agent 的实际职责。目标映射会给每个 branch 更明确的
capability ID 和本地 Markdown 名称。

## 迁移影响：非产品 builder

除了上述 13 个产品 builder，测试和 eval 中存在直接构造 `NodeExecutionRequest` 的 helper。
它们不代表新的产品能力，但 foundation change 会要求它们改用明确的测试 capability
fixture，或使用受限 test-only factory。否则“production request 不得 generic”会被测试
绕开，未来又无法判断一个真实调用是否遗漏 capability。

## 尚未验证的事

本盘点没有宣称任一模型当前一定实际调用了其允许工具，也没有根据一次 live run 判断
prompt 质量。下一步必须分别建立：

1. 静态 posture/request/runtime 一致性证据；
2. scripted invocation 对角色和结构化结果的 evidence；
3. 需要时的真实 provider 补充评估。

这些都在目标映射和总计划中被列为 future change 的验收，而不是当前事实。
