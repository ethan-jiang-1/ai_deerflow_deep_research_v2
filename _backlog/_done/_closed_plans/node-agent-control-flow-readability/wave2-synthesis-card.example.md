# Example Workflow Card: `wave2_synthesis`

> **历史审计卡，不是 final template。** 它不是 runtime authority，也不声称证明 spec conformance。
>
> 这是“普通 gated Node Agent”的 v0 样例。标有 **derived** 的内容属于已搁置的 inventory
> 方案；标有 **reviewed** 的内容需要人核对 owner 后维护。
>
> 维修入口、模型可见内容和真实加载链以
> [隔离 review example 的 v1 workflow.md](wave2-synthesis-compact_v1/review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md) 为准。本卡保留较完整的
> outcome/exit 对照。

## 一眼答案

```text
accepted evidence
    -> synthesis model candidate (zero tool)
    -> parse + assigned-reference validation
       -> invalid first candidate: one zero-tool repair
       -> invalid repaired candidate: exception propagates today
    -> write canonical synthesis artifact
    -> create typed Wave2 gate preview
    -> graph wrapper invokes deterministic gate
    -> gate writes evidence_needed | pass | exhausted
    -> builder consumes route through conditional edges
```

模型只负责提出 synthesis candidate。node 决定它是否满足结构和 backing-reference 约束，
synthesis bundle 写入 canonical artifact，gate preview 只携带 bounded searchable gap IDs，
最后由 wrapper gate 写 route。

## Scope

| 项目 | 内容 |
| --- | --- |
| Logical node | `wave2_synthesis` |
| Real factory | `graph.nodes.wave2_synthesis.node::build_real` |
| Model branches | `wave2-synthesis/synthesis`、`wave2-synthesis/repair` (**derived**) |
| Non-model control | evidence read/write、parse、semantic validation、gate preview、wrapper gate、conditional routing (**reviewed**) |

## Entry

| 输入 | 事实 owner | 这里如何使用 |
| --- | --- | --- |
| `accepted_submission_refs` | validated submission ledger + checkpoint projection | 限定哪些 refs 可以支撑 finding。 |
| synthesis evidence content | synthesis bundle adapter | 作为分配给模型的只读 evidence。 |
| topic registry | planner-owned checkpoint state | 给 synthesis 提供 topic context。 |
| repair/gate budgets | node invocation policy / gate state | 分别约束 structured repair 与 phase convergence。 |

## Candidate Paths

这是已搁置的 v0 方案：该表应由 prompt catalog join 生成。最终 v1 不在 `workflow.md`
中维护或生成 branch inventory。

| Branch (**derived**) | Candidate | Requested tools | Capability source |
| --- | --- | --- | --- |
| [`wave2-synthesis/synthesis`](../../../agent/node_prompts/wave2-synthesis/synthesis.md) | structured findings + gaps candidate | forbidden | [`wave2-evidence-synthesis.md`](../../../agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/capabilities/wave2-evidence-synthesis.md) |
| [`wave2-synthesis/repair`](../../../agent/node_prompts/wave2-synthesis/repair.md) | repaired candidate constrained to assigned evidence | forbidden | [`wave2-evidence-synthesis-repair.md`](../../../agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/capabilities/wave2-evidence-synthesis-repair.md) |

## Admission

```text
model summary
    -> parse_synthesis_output
    -> _validate_synthesis_semantics
       - at least one finding when accepted evidence exists
       - every backing ref resolves to an accepted submission
    -> synthesis_bundle.write_synthesis
    -> build_wave2_gate_preview
```

模型输出不能直接写 artifact、`unresolved_gaps` 或 route。相关 owner：

- Parser/semantic owner: [`wave2_synthesis/node.py`](../../../agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py)
- Artifact adapter: `NodeBuildDependencies.synthesis_bundle`
- Gap projection/route owner: [`gate_adapter.py`](../../../agent/src/deerflow_deep_research/graph/nodes/gate_adapter.py)

## Outcome Review

| Failure class (**reviewed**) | Recovery owner and bound | Current disposition | Legal next action |
| --- | --- | --- | --- |
| Initial invocation returns a classified non-success | Wave2 node; no provider retry here | typed `route="exhausted"`, terminal blocked; no synthesis publication | graph terminates through the declared exhausted edge |
| Initial candidate fails parse/backing-ref validation | Wave2 node; exactly one structured repair | run zero-tool repair with original draft + assigned evidence；当前不传具体 validation failure | admit repaired candidate or follow the next row |
| Repair invocation returns a classified non-success | Wave2 node; no further repair | typed `route="exhausted"`, terminal blocked | graph terminates through exhausted edge |
| Repaired candidate is still invalid | no current conversion owner | exception propagates; no artifact or gate preview | runtime failure handling; a typed outcome needs a separate owning change |
| Evidence read or artifact write fails | synthesis bundle adapter; no node-local retry | exception propagates | runtime/infrastructure handling |
| Valid candidate still contains searchable gaps | gate kernel; bounded phase repair/fatigue budget | `evidence_needed` while budget remains, otherwise `exhausted` | targeted evidence or blocked terminal |

这里最重要的是：structured repair 和 phase-gate repair 是两个不同 owner 的预算，不能合并
写成“失败会 retry”。还要注意，当前 `except ValueError` 只触发 repair，却丢弃 exception；
不能把它描述成 repair model 已收到 local validation feedback。

## Exit Semantics

| Semantic route (**derived**) | Route writer (**reviewed**) | Executable edge | Route consumer | Target |
| --- | --- | --- | --- | --- |
| `evidence_needed` | wrapper-invoked Wave2 gate | conditional | `builder::_route` | `targeted_evidence` |
| `pass` | wrapper-invoked Wave2 gate | conditional | `builder::_route` | `hitl2` |
| `exhausted` | node for direct terminal failure, or wrapper gate for gate exhaustion | conditional | `builder::_route` | blocked terminal / LangGraph `END` |

Semantic edge inventory 来自
[`topology.py`](../../../agent/src/deerflow_deep_research/graph/topology.py)，实际 wiring 来自
[`builder.py`](../../../agent/src/deerflow_deep_research/graph/builder.py)。当前两者是两份不同的
surface，所以 card 必须同时指出它们，不能把 topology 称为 executable wiring。

## Evidence

- Owning spec: [`wave2-synthesis-node`](../../../openspec/specs/wave2-synthesis-node/spec.md)
- Wrapper/gate proof: [`test_gate_integration.py`](../../../agent/tests/graph/test_gate_integration.py)
- Real node proof: [`test_wave2_synthesis_real.py`](../../../agent/tests/graph/test_wave2_synthesis_real.py)
- Topology/builder proof: [`test_topology_and_implementation.py`](../../../agent/tests/graph/test_topology_and_implementation.py)

## 读完应能回答

1. 模型能不能直接决定 `evidence_needed`？不能。
2. 谁接纳 backing refs？node-local deterministic validation。
3. 谁写成功 route？wrapper 调用的 gate。
4. repair 后仍无效会怎样？当前传播 exception，不是统一 `exhausted`。
