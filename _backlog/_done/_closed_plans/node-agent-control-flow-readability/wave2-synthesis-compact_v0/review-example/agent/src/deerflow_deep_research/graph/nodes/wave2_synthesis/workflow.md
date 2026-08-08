<!-- node-workflow-card: {"schema_version":1,"workflow_id":"node-workflow/wave2_synthesis","logical_node":"wave2_synthesis","classification":"node-agent","prototype":true} -->
# Wave2 Synthesis: Coding Agent 维修入口

> **SUPERSEDED BY v1 FINAL。** 这是 v0 的全景/checker 对照，不是新 node package 的 reader
> interface 模板。最终版本见上级计划中的 `wave2-synthesis-compact_v1`。

> **NODE TYPE: LLM-BEARING NODE AGENT（智力节点）**
>
> 它的认知工作是：只根据 graph 已接纳的 evidence，形成跨主题 findings、relations 和
> evidence gaps。模型交回的是 candidate；确定性代码负责接纳、写 artifact 和选 route。
>
> **这是 `_backlog/.../review-example` 中的隔离 documentation prototype，不是 runtime authority。**
> 相邻 Python 与 capability 文件是当前 Wave2 implementation 的 review snapshot；生产 runtime、
> prompt renderer 和 graph builder 都不会发现或读取这个目录。
>
> 对修问题的人或 Coding Agent 来说，这一份 MD 是本样例唯一的 reader-facing prose interface；
> 不要求先读另一份 Python/JSON schema。获批前不得把它或相邻快照复制进正式 `agent/`。

## 先按症状找修改点

| 观察到的症状 | 先检查什么 | 精确 owner（repo-relative `file::symbol`） | 为什么从这里开始 | 最低责任测试 / eval |
| --- | --- | --- | --- | --- |
| 模型不理解自己的角色、试图检索、接纳 evidence 或决定 route | model-visible capability policy | `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/capabilities/wave2-evidence-synthesis.md`；repair 分支看相邻 repair MD | metadata 后的 Markdown body 会进入 system policy | `agent/tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding`；行为质量仍需 live eval |
| findings 很浅、没有跨主题关系、遗漏重要 gap | 初始 objective、实际分配的 evidence、质量 eval | `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/prompts.py::build_synthesis_prompt`；`agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py::build_real` | objective 和 accepted evidence 是模型本次真正看到的动态任务 | `agent/tests/live/test_canaries.py::test_live_prefix_canary[live-wave2-synthesis]`；**MISSING: 没有专门衡量跨主题综合深度的 eval** |
| 模型反复漏字段、返回 Markdown、混淆 finding/gap 的 `search_required` | request output contract | `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/prompts.py::_expected_synthesis_output` 和 `::build_synthesis_prompt` | 两者进入 model-visible user message | `agent/tests/graph/test_wave2_synthesis_real.py::test_wave2_prompts_distinguish_finding_and_gap_search_flags` |
| 首次 candidate 失败后，repair 又犯同一个语义错误 | repair 是否收到具体失败原因 | `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py::build_real`；`agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/prompts.py::build_synthesis_repair_prompt` | **当前错误被丢弃**；repair 只收到 draft + accepted evidence | 扩展 `::test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists`，断言第二个 request 含稳定 validation code |
| 合法 candidate 被拒绝，或非法 backing ref 被接纳 | result contract、parser、semantic admission | `agent/src/deerflow_deep_research/domain/synthesis.py::SynthesisResult`；`.../wave2_synthesis/prompts.py::parse_synthesis_output`；`.../wave2_synthesis/node.py::_validate_synthesis_semantics` | 这是确定性接纳问题，不是模型质量或 graph route 问题 | `agent/tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_maps_source_aliases_to_accepted_record_refs` 及相邻 invalid-output tests |
| `search_required` 正确但走错 `evidence_needed/pass/exhausted` | preview 与 gate | `agent/src/deerflow_deep_research/domain/synthesis.py::build_wave2_gate_preview`；`agent/src/deerflow_deep_research/engine/gate_fixtures.py::build_wave2_real_gate_def`；`agent/src/deerflow_deep_research/graph/nodes/gate_adapter.py::evaluate_gate_for_node` | 模型只建议 gap；这些确定性 owner 才把它变成 route | `agent/tests/graph/test_gate_integration.py::TestRealWave2GateOutcomes` |
| 模型未配置、capability admission 失败、零工具策略失效 | runtime bridge 与 Wave2 execution policy | `agent/src/deerflow_deep_research/runtime/research.py::_wave2_synthesis_node_agent_policy`；`.../runtime/node_agent_bridge.py::RuntimeNodeAgentBridge.run_agent` | model/tool resolution 和实际 admission 在 runtime，不在 capability body | Wave2 policy 看 `agent/tests/unit/test_research_runtime_capabilities.py::test_wave2_synthesis_uses_its_dedicated_zero_tool_policy`；bridge enforcement 看 `agent/tests/unit/test_node_agent_bridge.py::test_zero_tool_repair_request_does_not_resolve_or_expose_policy_tools` 和 `::test_capability_posture_disagreement_fails_before_model_resolution` |
| route label 正确但进入了错误 node | executable graph wiring | `agent/src/deerflow_deep_research/graph/builder.py::build_research_graph` 和 `::_route`；semantic inventory 看 `agent/src/deerflow_deep_research/graph/topology.py::NORMALIZED_EDGES` | topology inventory 与 LangGraph wiring 是两个不同表面 | `agent/tests/graph/test_topology_and_implementation.py::test_wave2_topology_includes_bounded_exhausted_terminal` |

这张表就是维护 interface。报告一个具体问题时，Coding Agent 应先选中一行，再打开该行的
owner 和最低责任测试；不要先在 1700 多个测试或整个 graph 中漫游。

现有 `live-wave2-synthesis` 也不是完整 production-policy proof：
`agent/tests/scenarios/canaries.py::_execute_focused_wave2_core` 当前调用
`_build_hitl1_capabilities`，而生产 `_context` 使用 `_build_wave2_synthesis_capabilities`。
它能观察真实 Wave2 prompt/model candidate/admission 的一部分行为，但不能证明专用 Wave2
execution policy 的 authenticity。

## 一眼看懂这个智力回路

```text
ResearchState: topic_registry + accepted_submission_refs
                         |
                         v
          synthesis_bundle reads accepted evidence
                         |
                         v
              initial synthesis LLM
                         |
                     candidate
                         v
          parse + semantic/backing-ref admission
                  |                     |
                  | valid               | invalid: trigger repair once
                  |                     v
                  |          repair LLM gets draft + evidence
                  |          (current code does NOT send failure code)
                  |                     |
                  +<------ repaired candidate
                  |
                  v
       write synthesis/findings.json + gate preview
                  |
                  v
             wrapper-invoked gate
          pass / evidence_needed / exhausted
                  |
        evidence_needed -> targeted_evidence
                  |
          newly accepted evidence re-enters Wave2
```

两个容易误读的事实：

1. local validation 当前只是 **repair trigger**，不是送给模型的具体 feedback；
   `node.py::build_real` 捕获 `ValueError` 后没有保留 exception。
2. Wave2 gate 也不直接把 feedback 交给 Wave2 模型。它把 searchable gap IDs 交给
   `targeted_evidence` 路径；新 evidence 被接纳后，Wave2 从更新后的 evidence 重新综合。

## 模型到底看见了什么

不要把一个 Python/JSON record 里所有字段都叫“提示词”。下面按真实 reader 分类。

| 来源 | 分类 | 谁读取 / 怎样使用 | Wave2 模型可见？ |
| --- | --- | --- | --- |
| `agent/src/deerflow_deep_research/resources/node_agent/runtime_policy.md` | model-visible system policy | `agents/prompts.py::load_policy_prompt` 读取，作为 shared base system policy | **是，system** |
| capability MD 第一行 `<!-- node-agent-capability: ... -->` | deterministic admission metadata | `agents/capabilities.py::load_node_agent_capability` 校验 ID/schema；`tool_posture` 参与 runtime admission；整行随后被剥离 | **否** |
| capability MD 第一行后的 body | model-visible system policy | 同一 loader 返回 `policy`；`agents/phase_prompt.py::render_phase_agent_prompt` 追加到 base system policy | **是，system** |
| `NodeExecutionRequest.objective` | model-visible request content | `wave2_synthesis/prompts.py` 构造；renderer 放进 `Objective:` user message | **是，user** |
| `NodeExecutionRequest.expected_output` | model-visible request content | `_expected_synthesis_output` 构造；renderer 放进 `Expected output:` user message | **是，user** |
| accepted evidence JSON | model-visible untrusted data | `build_synthesis_prompt` / repair builder 放进 delimited untrusted block，作为 objective 的一部分 | **是，user/untrusted** |
| `tools_enabled=False` + capability `tool_posture=forbidden` + Wave2 `ExecutionPolicy` | runtime enforcement | request validation、capability admission、bridge policy 三层共同限制实际工具 | **不是 prompt；模型最终看到零工具** |
| `agent/node_prompts/wave2-synthesis/*.md` | generated review-only projection | synthetic catalog 调用同一 prompt builder/renderer；runtime 从不加载这些文件 | **否** |
| 本 `workflow.md` | authored review-only maintenance map | 人和 Coding Agent 读取；runtime、prompt renderer、graph builder 都不读取 | **否** |

关键区别：capability metadata 中的 `role/method/authority_limit/...` 目前只是经过校验的
review/configuration metadata；它们不会自动变成模型文字。真正进入 system prompt 的是 metadata
下面的 body。若模型不理解某条规则，要确认那条规则是否真的出现在 body 或动态 request 中。

## 真实装配与加载链

下面的每一跳都是当前代码里的 exact symbol。陌生 Agent 不需要猜 capability 是怎么找到、
prompt 是怎么拼、candidate 又在哪里被接纳。

```text
runtime/research.py::ResearchActionHandler._context
  -> _build_wave2_synthesis_capabilities
  -> RuntimeNodeAgentBridge(policy=_wave2_synthesis_node_agent_policy, tools=())
  -> RuntimeNodeDependencyResolver(capabilities_by_node["wave2_synthesis"])

graph/builder.py::build_research_graph
  -> graph/nodes/gate_adapter.py::real_wave2_gate_def
  -> engine/gate_fixtures.py::build_wave2_real_gate_def
  -> _node_wrapper(..., gate_defs)

graph/builder.py::_node_wrapper
  -> RuntimeNodeDependencyResolver.resolve
  -> attach synthesis_bundle
  -> wave2_synthesis.__init__.py::NODE_SPEC.real_factory
  -> wave2_synthesis.node::build_real
  -> synthesis_bundle.read_synthesis_evidence
  -> wave2_synthesis.prompts::build_synthesis_prompt
  -> NodeExecutionRequest(capability_ref=WAVE2_EVIDENCE_SYNTHESIS)
  -> dependencies.capabilities.run_agent
  -> runtime/node_agent_bridge.py::RuntimeNodeAgentBridge.run_agent
  -> agents/phase_prompt.py::render_phase_agent_prompt
  -> agents/capabilities.py::load_node_agent_capability
  -> importlib.resources reads capabilities/wave2-evidence-synthesis.md
  -> capability body appended to shared system policy
  -> objective + expected_output rendered as user message
  -> bridge resolves zero tools + model
  -> agents/factory.py::build_phase_agent
  -> agent.ainvoke
  -> RuntimeNodeAgentBridge._project_result
  -> NodeExecutionResult.summary
  -> wave2_synthesis.prompts::parse_synthesis_output
  -> wave2_synthesis.node::_validate_synthesis_semantics
  -> optional one-shot repair request (same bridge, repair capability)
  -> synthesis_bundle.write_synthesis
  -> domain/synthesis.py::build_wave2_gate_preview
  -> graph/builder.py::_node_wrapper
  -> graph/nodes/gate_adapter.py::evaluate_gate_for_node
  -> engine/gate_kernel.py::evaluate_gate (using the prebuilt gate definition)
  -> state["route"]
  -> graph/builder.py::_route
  -> conditional executable edge
```

若问题发生在链的前半段，通常是模型装配、context 或 cognitive policy；发生在
`parse_synthesis_output` 之后，才通常是 admission、artifact、gate 或 graph control。

## 输入、feedback 与 authority

| Signal | 实际 recipient | 当前传递内容 | Effect / bound |
| --- | --- | --- | --- |
| 首次进入 | synthesis model | topic registry、accepted refs、accepted evidence | 产生一个 candidate；零工具 |
| initial parse/semantic failure | node-local controller | `ValueError` 只用于进入 `except` | 恰好触发一次 repair；**failure code 未交给 repair model** |
| repair request | repair model | original draft、accepted evidence、静态 schema/capability | 产生 replacement candidate；无第二次 repair |
| repaired candidate 再次无效 | runtime failure handling | exception 传播 | 不写 artifact/preview；当前不是 typed `exhausted` |
| Wave2 gate searchable gaps | `targeted_evidence` graph path | bounded searchable gap IDs | gate budget 内检索；不是给 Wave2 model 的直接 feedback |
| targeted evidence 被接纳后 re-entry | 新一次 synthesis model | 更新后的 accepted evidence 集合 | 从头重做 synthesis，不是 patch 旧 artifact |

模型只拥有 candidate authority。确定性 owner 分工如下：

| 决定 | 唯一 owner |
| --- | --- |
| output schema / provider-shape normalization | `domain/synthesis.py::SynthesisResult` |
| backing refs 是否属于 assigned accepted refs | `wave2_synthesis.node::_validate_synthesis_semantics` |
| canonical synthesis artifact | `synthesis_bundle.write_synthesis` |
| searchable gap projection | `domain/synthesis.py::build_wave2_gate_preview` |
| `pass/evidence_needed/exhausted` verdict | Wave2 gate definition + gate kernel |
| executable target | `graph/builder.py::build_research_graph` conditional edges |

## 失败时当前怎样结束

| Failure class | Recovery owner / bound | Implemented disposition |
| --- | --- | --- |
| initial model invocation 返回 classified failure | Wave2 node；这里没有 provider retry | `_exhausted_update` 写 typed blocked + `route="exhausted"`；不发布 synthesis |
| initial candidate parse/semantic failure | Wave2 node；恰好一次 zero-tool repair | failure 只触发 repair；具体 validation code 当前丢失 |
| repair invocation 返回 classified failure | Wave2 node；不再 repair | `_exhausted_update` 写 typed blocked + `route="exhausted"` |
| repaired candidate 仍 invalid | 当前没有 conversion owner | exception 传播；不写 artifact/preview，不是 typed exhausted |
| evidence read / synthesis write I/O failure | synthesis bundle adapter；无 node-local retry | exception 传播给 runtime/infrastructure handling |
| valid candidate 仍有 searchable gaps | Wave2 gate；phase budget 为 1 | budget 内 `evidence_needed`，耗尽后 `exhausted` |

## 一个完整的修复例子

### 报告的症状

> accepted evidence 非空。initial model 只返回 gaps，repair model 仍然只返回 gaps，最后抛出
> `synthesis_findings_required`。为什么 repair 不知道必须补一个 finding？

### 当前因果链

```text
node.py::_validate_synthesis_semantics
  -> raises ValueError("synthesis_findings_required")
node.py::build_real
  -> except ValueError:                       # exception 被丢弃
  -> build_synthesis_repair_prompt(result.summary, evidence)
prompts.py::build_synthesis_repair_prompt
  -> repair request contains draft + evidence + generic schema
  -> no "synthesis_findings_required" signal
```

因此这不是先去放宽 parser/gate 的问题，也不是先改 capability role。具体修复面是：

1. 在 `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py::build_real`
   保留一个**闭集、无原始 payload 的 validation code**，传给 repair builder；不要把任意 raw
   exception text 直接送进 prompt。
2. 在 `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/prompts.py::build_synthesis_repair_prompt`
   增加该参数，并把可信 validation code 放在 repair assignment 中；draft/evidence 仍留在
   untrusted block。
3. 更新 `agent/src/deerflow_deep_research/graph/prompt_catalog.py` 的
   `wave2-synthesis/repair` synthetic case，使新 builder signature 仍可生成审阅 prompt。
4. 扩展
   `agent/tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists`，
   断言第二个 request 明确含 `synthesis_findings_required`；再给 prompt builder 加一个纯函数断言。
5. 用 `live-wave2-synthesis` 观察模型质量，但不要用 live test 替代上述确定性 request 断言；
   在 canary 改用专用 Wave2 bridge 前，也不要把它称为 production-policy authenticity proof。

这也是当前 spec/code conformance 缺口：`openspec/specs/wave2-synthesis-node/spec.md` 的
`WSN-005` 要求 repair 收到 validation facts，而 implemented request 尚未做到。它应由独立
Wave2 conformance change 修复；本 MD 只能如实导航，不能替运行代码补上行为。

## 分支与出口

下面两个表的 inventory 可从现有 owner 机械派生；未来 checker 只更新这个有界区块，
不生成或覆盖上面的维修语义。

<!-- BEGIN GENERATED: NODE-WORKFLOW-INVENTORY -->
| Direct branch | Request builder | Capability | Requested tools |
| --- | --- | --- | --- |
| `wave2-synthesis/repair` | `graph/nodes/wave2_synthesis/prompts.py::build_synthesis_repair_prompt` | `wave2-evidence-synthesis-repair` | forbidden |
| `wave2-synthesis/synthesis` | `graph/nodes/wave2_synthesis/prompts.py::build_synthesis_prompt` | `wave2-evidence-synthesis` | forbidden |

| Semantic edge | Normalized target |
| --- | --- |
| `wave2_synthesis:evidence_needed` | `targeted_evidence` |
| `wave2_synthesis:exhausted` | `blocked` |
| `wave2_synthesis:pass` | `hitl2` |
<!-- END GENERATED: NODE-WORKFLOW-INVENTORY -->

Executable control 仍需明确写出，因为 `NORMALIZED_EDGES` 不拥有 LangGraph wiring：

| Route | Route writer | Consumer | Executable target |
| --- | --- | --- | --- |
| `evidence_needed` | wrapper-invoked Wave2 gate | `builder.py::_route` | `targeted_evidence` |
| `pass` | wrapper-invoked Wave2 gate | `builder.py::_route` | `hitl2` |
| `exhausted` | direct invocation failure 时由 node；gate budget exhaustion 时由 gate | `builder.py::_route` | blocked `END` |

## 文档本身怎样维护

- 人和 Coding Agent 直接读、直接审阅同一份 `workflow.md`；没有隐藏的 Python/JSON
  semantics source。
- 第一行 metadata 只用于 identity/coverage check，不是 runtime config。
- 未来 `agent/scripts/node_workflow_docs.py`（拟议名称）只读取第一行和明确的
  `BEGIN/END GENERATED` 区块，用 `prompt_catalog_cases()` + `NORMALIZED_EDGES` 检查或刷新
  branch/semantic-edge inventory；它不解释、重写或执行其余 prose。
- runtime、capability loader、prompt renderer、node factory 和 graph builder 永远不读取本文件。
- 人工 source refs 必须指向 exact `file::symbol`；checker 可做 existence/link check，但
  semantic 正确性仍由 code review 与负责测试证明。

Owning specs: `openspec/specs/wave2-synthesis-node/spec.md`、
`openspec/specs/research-graph-lifecycle/spec.md`。

主要行为测试: `agent/tests/graph/test_wave2_synthesis_real.py`、
`agent/tests/graph/test_gate_integration.py`、
`agent/tests/graph/test_topology_and_implementation.py`。
