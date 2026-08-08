# Wave2 Synthesis — 维修地图

> **REVIEW ONLY。** 这是 reader interface，不进入 runtime。代码、spec 和测试仍是事实 source。

> **节点性质：LLM-bearing node agent（智力节点）。** Wave2 只根据已接纳的 evidence 提出
> findings、relations 和 gaps 的 candidate。模型不接纳 evidence、不写 artifact、不决定 route；
> 这些都是确定性代码的 authority。

## 从症状进入

| 观察到的症状 | 先打开的 owner | 最低责任测试 / proof |
| --- | --- | --- |
| 模型误解角色、想检索、想接纳 evidence 或决定 route | `capabilities/wave2-evidence-synthesis.md`（repair 看相邻文件） | `test_node_agent_capability_cohort.py::test_cohort_branch_binding`；模型质量另做 live eval |
| 输出字段错误、Markdown、`search_required` 混淆，或 findings/gaps 质量差 | `prompts.py::_expected_synthesis_output`、`::build_synthesis_prompt` | `test_wave2_synthesis_real.py::test_wave2_prompts_distinguish_finding_and_gap_search_flags` |
| initial candidate 无效后，repair 又犯同一个语义错误 | `node.py::build_real`、`prompts.py::build_synthesis_repair_prompt` | 扩展 `test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists`，断言第二个 request |
| 合法 candidate 被拒绝，或非法 backing ref 被接纳 | `domain/synthesis.py::SynthesisResult`、`prompts.py::parse_synthesis_output`、`node.py::_validate_synthesis_semantics` | `test_wave2_synthesis_real.py` 的 source-alias 和 invalid-output tests |
| gap 正确却走错 `evidence_needed` / `pass` / `exhausted` | `domain/synthesis.py::build_wave2_gate_preview`、`gate_adapter.py::evaluate_gate_for_node`、`graph/builder.py::_route` | `test_gate_integration.py::TestRealWave2GateOutcomes`；`test_topology_and_implementation.py` |
| 模型未配置、capability admission 失败，或零工具策略失效 | `runtime/research.py::_wave2_synthesis_node_agent_policy`、`runtime/node_agent_bridge.py::RuntimeNodeAgentBridge.run_agent` | `test_research_runtime_capabilities.py::test_wave2_synthesis_uses_its_dedicated_zero_tool_policy`；`test_node_agent_bridge.py::test_zero_tool_repair_request_does_not_resolve_or_expose_policy_tools`、`::test_capability_posture_disagreement_fails_before_model_resolution` |

局部执行顺序以 `node.py::build_real` 为准：它已经直接表达 read evidence → initial request →
admission → optional repair → write synthesis/preview。不要在这里维护第二份逐行流程图。

## 三个跨模块事实

1. **模型实际看见的内容**：shared runtime policy 和 capability Markdown 的 **body** 进入
   system prompt；`objective`、`expected_output` 和 accepted evidence 进入 user request，其中
   evidence 是 untrusted data。capability 第一行 metadata 与 tool posture 是 deterministic
   admission / enforcement，不是自动可见的 prompt 文本。
2. **repair feedback 的真实语义**：`node.py::build_real` 的 `except ValueError` 只触发一次
   repair。当前 exception/code 没有传进 `build_synthesis_repair_prompt`，所以 repair 只有 draft、
   accepted evidence 和静态 contract；它并不知道例如 `synthesis_findings_required`。
3. **route authority 不在模型或 node 内**：node 只写 Wave2 gate preview；graph wrapper 调用
   gate 写 `state["route"]`；`graph/builder.py::_route` 和 conditional edges 决定 executable target。
   `evidence_needed` 到 targeted evidence 后，新增 evidence 被接纳才会重新进入一次 Wave2 synthesis。

## Route 事实

| Route | writer | consumer | executable target |
| --- | --- | --- | --- |
| `evidence_needed` | wrapper-invoked Wave2 gate | `graph/builder.py::_route` | `targeted_evidence` |
| `pass` | wrapper-invoked Wave2 gate | `graph/builder.py::_route` | `hitl2` |
| `exhausted` | direct invocation failure 时由 node；gate budget 耗尽时由 gate | `graph/builder.py::_route` | blocked `END` |

## 修改后的验证顺序

1. 先扩展症状行所列的最低责任测试，证明 request、admission 或 route 的确定性事实。
2. 如果改的是 prompt/capability 的认知质量，再用 `live-wave2-synthesis` 观察行为；它不能代替
   上述确定性断言。
3. 只有问题跨过 runtime bridge 或 executable wiring 时，才向外打开共享 runtime 或 graph builder。

相关行为 source：`node.py`、`prompts.py`、`capabilities/*.md`；相关 specs：
`openspec/specs/wave2-synthesis-node/spec.md` 与 `openspec/specs/research-graph-lifecycle/spec.md`。
