# Targeted Evidence 路由诊断示例

> **诊断参考，不是 final reader-interface 模板。** 这份 discussion prototype 只用于说明
> handler 写 route 与 executable graph 是否消费 route 是两回事；它不是 runtime authority，也不
> 声称当前 real journey 已通过 compiled graph conformance。
>
> 这是“特殊出口 + 两条内部路径”的样例，专门验证 card 能否避免把 route 写错。

## 一眼答案

```text
Wave2 gate-owned gap IDs
    -> gap worker candidates
    -> same-gap parse/validation
    -> shared work-unit validator/controller/ledger

optional critic_work_items
    -> source diagnostic / claim verifier candidates
    -> critic materializer validates assigned refs
    -> critic artifacts

handler writes route="next"
    -> builder ignores that route
    -> unconditional edge returns to wave2_synthesis
```

这里有两个必须分开的事实：handler 确实写了 `route="next"`；但是 graph 返回 Wave2 的原因
不是这个 route，而是 builder 注册了 unconditional edge。

## 当前实现提醒

| 状态 | 说明 |
| --- | --- |
| Known gap | `critic_work_items` 在 production source 中没有 writer，因此两个 critic branches 不能描述为已证明的正常 graph journey。 |
| Known bug | `NODE_SPEC` 声明 `WORK_UNIT_CONTROLLER`，wrapper 因此要求 `WORK_UNIT_GATE_VIEW_KEY`；当前 real node 丢弃 component `gate_view`，compiled journey 到这里会在 wrapper validation 失败。 |

正式 card 可以显示这些 implemented limitations，但不能用 card 代替对应的 owning bug/change。

## Scope

| 项目 | 内容 |
| --- | --- |
| Logical node | `targeted_evidence` |
| Real factory | `graph.nodes.targeted_evidence.node::build_real` |
| Model branches | worker、repair、source diagnostic、claim verifier 四个 direct cases (**derived**) |
| Internal paths | gap work-unit path；可选 critic dispatch path (**reviewed**) |
| Return wiring | semantic `next`；executable unconditional edge to `wave2_synthesis` |

## Entry

| 输入 | 事实 owner | 这里如何使用 |
| --- | --- | --- |
| `unresolved_gaps` | current Wave2 gate projection | 每个 validated gap ID materialize 一个 `WorkIntent`。 |
| `critic_work_items` | 当前没有 production writer | 若被提供，选择 source/claim critic assignment。 |
| work-unit controller/ledger | runtime-injected controller dependencies | 分配 attempts、验证 candidates、提交 accepted evidence。 |
| assigned source/evidence refs | critic work item | 限定 critic candidate 可以引用的集合。 |

## Candidate Paths

| Branch (**derived**) | Candidate | Requested tools | Admission path |
| --- | --- | --- | --- |
| [`targeted-evidence/worker`](../../../agent/node_prompts/targeted-evidence/worker.md) | one-gap evidence candidate | exactly one permitted retrieval | same-gap parser -> work-unit validator/controller/ledger |
| [`targeted-evidence/repair`](../../../agent/node_prompts/targeted-evidence/repair.md) | repaired same-gap candidate | forbidden | same-gap parser -> work-unit validator/controller/ledger |
| [`targeted-evidence/source-diagnostic`](../../../agent/node_prompts/targeted-evidence/source-diagnostic.md) | assigned-source diagnostic | forbidden | typed parser -> assigned-ref materializer |
| [`targeted-evidence/claim-verifier`](../../../agent/node_prompts/targeted-evidence/claim-verifier.md) | assigned-evidence claim verdicts | forbidden | typed parser -> assigned-ref materializer |

## Admission

### Gap worker path

```text
gate-owned gap ID
    -> worker candidate
    -> parse_targeted_worker_output
    -> exact assigned gap-id check
    -> candidate artifact
    -> shared submit validation
    -> accepted submission ledger
```

### Critic path

```text
assigned refs + untrusted material
    -> typed critic candidate
    -> Pydantic validation
    -> materializer rejects any unassigned ref
    -> critic JSON artifact
```

Critic artifact 不等于 accepted evidence ledger record；两条 admission path 不应混画成一个
“validator”。代码 owner：

- Dispatch/workers: [`subgraph.py`](../../../agent/src/deerflow_deep_research/graph/nodes/targeted_evidence/subgraph.py)
- Critic materialization: [`materializer.py`](../../../agent/src/deerflow_deep_research/graph/nodes/targeted_evidence/materializer.py)
- Node composition: [`node.py`](../../../agent/src/deerflow_deep_research/graph/nodes/targeted_evidence/node.py)

## Outcome Review

| Failure class (**reviewed**) | Recovery owner and bound | Current disposition | Legal next action |
| --- | --- | --- | --- |
| Worker invocation failure | shared work-unit controller after typed worker classification | terminal attempt; controller may allocate its bounded retry | retry work or finish the batch |
| Initial worker candidate invalid/wrong gap | targeted worker; exactly one zero-tool repair | repaired candidate re-enters same-gap admission | admit or record failed attempt |
| Repair invalid/non-success | shared worker failure path; no second structured repair | no source/result artifact or ledger admission | controller retry/gate handling |
| Critic malformed/out-of-scope candidate | critic parser/materializer; no recovery in current node | exception propagates before critic artifact write | runtime failure handling |
| Storage/ledger infrastructure failure | owning adapter; not relabeled as model failure | exception propagates | infrastructure recovery |
| Missing wrapper gate view | wrapper contract validation | `work_unit_gate_view_inconsistent` | separate conformance fix; route is not reached |

## Exit Semantics

| Semantic route (**derived**) | Route writer (**reviewed**) | Executable edge | Route consumer | Target |
| --- | --- | --- | --- | --- |
| `next` | `targeted_evidence` handler | unconditional | **none** | `wave2_synthesis` |

这张表是整个示例的关键。错误写法是“handler writes `next`, so graph routes to Wave2”。
正确写法是“handler writes `next`, but builder does not consume it; unconditional wiring returns
to Wave2”。

## Evidence

- Owning spec: [`targeted-evidence-loop`](../../../openspec/specs/targeted-evidence-loop/spec.md)
- Shared controller spec: [`work-unit-kernel`](../../../openspec/specs/work-unit-kernel/spec.md)
- Direct real-node tests: [`test_targeted_evidence_real.py`](../../../agent/tests/graph/test_targeted_evidence_real.py)
- Wrapper contract: [`builder.py`](../../../agent/src/deerflow_deep_research/graph/builder.py)
- Missing compiled-path proof is itself part of the known gap.

## 读完应能回答

1. `next` 是谁写的？targeted handler。
2. 谁读取 `next`？没有人。
3. 为什么仍回 Wave2？builder 的 unconditional edge。
4. critic 为什么不能算正常主链已覆盖？当前没有 production work-item writer。
5. 为什么 direct node tests 通过仍不够？它们绕过了 graph wrapper 的 gate-view seam。
