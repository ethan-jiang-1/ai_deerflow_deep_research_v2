# Node Workflow 可读性对齐样例

> 状态: final reader-interface direction，2026-07-29
>
> 这些文件只用于对齐未来 Coding Agent 的维修 interface，不是 runtime authority、OpenSpec
> 或实现任务。主计划是
> [node-agent-control-flow-readability.md](../node-agent-control-flow-readability.md)。
> 落地顺序见 [progressive plan](../node-agent-control-flow-readability-progressive-plan.md)。

## Final 决议

**`wave2-synthesis-compact_v1/` 是本目录唯一的 final reader-interface 示例。** 最终决定是
采用它展示的“小型、症状驱动、node-local `workflow.md`”方法，而不是要求所有 node 复制
Wave2 的章节、症状或控制流。每个 node 应按自身的认知工作、deterministic authority 和实际
跨模块边界，提供等价的最小维修接口。`v0`、旧 Wave2 card、Targeted Evidence card 及
checker/generated-inventory 示例只保留为历史取舍或局部诊断参考，不构成可选实现方案，也不得
覆盖或扩展 v1 方法的最终边界。

## 现在的核心决定

每个 LLM-bearing node 只 colocate 一份面向读者的 `workflow.md`。人和 Coding Agent
读、审阅同一份 Markdown；不再用 `workflow_review.py` 大 literal 保存另一份人工语义。

每份 `workflow.md` 的最小 interface 必须独立回答：

- 这个 node 的 LLM 在思考什么，哪些部分仍是确定性外壳；
- 一个具体症状首先对应哪个 exact `file::symbol` 和测试/eval；
- 对该 node 容易误改的跨模块事实：例如 initial/re-entry input 与 feedback 实际交给了谁、
  模型实际看见什么、candidate 由谁接纳，或 route 由谁写和消费。

若未来多个 node 证明同一份 branch/semantic-edge inventory 值得自动维护，机器只允许刷新
Markdown 内明确标记、可从现有 owner 推导的区块；它不能生成或覆盖人工维修语义。这个
checker 方向当前不属于最终方案，除非新的跨节点证据重新提出它。

## 先用人话说明

| 词 | 在这些样例里是什么意思 |
| --- | --- |
| cognitive job | 这个 node 交给模型的有界思考任务，也是认知质量调优首先看的地方。 |
| model-visible system policy | shared runtime policy 加 capability Markdown body；模型真的会看到。 |
| model-visible request content | prompt builder 产生的 objective、expected output 与 delimited evidence。 |
| deterministic admission | parser/validator/materializer 对 candidate 的接纳；模型不拥有这项 authority。 |
| feedback | 必须说明 source、recipient、实际 signal 和 bound；“触发 repair”不等于“错误已送给 repair model”。 |
| tuning map | 从 observable symptom 直接指到 exact owner 和最低责任测试/eval。 |
| review-only | 给人和 Coding Agent 的地图；runtime、loader、builder 不读取。 |

## 阅读顺序

1. 先看 [Wave2 最终紧凑样例（v1）](wave2-synthesis-compact_v1/README.md)，再直接读它的
   [隔离 review example 内的 workflow.md](wave2-synthesis-compact_v1/review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md)。
   这是已选定的“小维修 interface”，尚未进入正式 `agent/`。
2. 仅在需要理解被拒绝的取舍时，才看保留的 [Wave2 v0 全景样例](wave2-synthesis-compact_v0/README.md)。
   v0 的完整装配链、generated inventory 和 checker 不属于最终 node-local interface。
3. 看 [Targeted Evidence 示例](targeted-evidence-card.example.md)，理解 handler 写 route 与
   executable graph 是否消费 route 是两回事。
4. 按需看 [人工内容与派生区块](source-vs-derived.example.md)，了解已搁置 checker 方案的边界；
   它不是实现 final interface 的前置工作。
5. [旧版 Wave2 审计卡](wave2-synthesis-card.example.md) 只保留较完整的 outcome/exit 对照，
   不是 final template；维修入口和 prompt 加载事实以 v1 紧凑样例为准。

## 直接用维修任务验收

不要只问“是否容易读”，而是把一份 card 交给陌生 Coding Agent，要求它解决一个具体问题。
Wave2 样例使用：

> initial candidate 因 `synthesis_findings_required` 失败，repair 又犯同样错误。
> repair 模型是否真的收到了这个 validation code？应改哪里？

合格答案必须一跳找到 `node.py::build_real`、
`prompts.py::build_synthesis_repair_prompt` 和负责测试，并明确当前 error 被丢弃。只有修改
prompt builder signature 时，才进一步打开 prompt catalog synthetic case。若 Agent 仍先去改
parser、gate 或 builder，这个 interface 就没有解决问题。

## 不由这些样例决定

- 是否先修 Wave1/Targeted/Wave2 已发现的 conformance 缺口；
- 是否有足够跨节点证据重新考虑 checker/script 和 Make target；
- 是否为 no-agent controller 增加不同类型的操作卡；
- 是否让 `NORMALIZED_EDGES` 未来直接驱动 executable builder wiring。

这些决定应进入后续 owning OpenSpec change；样例只先固定读者最终拿到的维修 interface。
