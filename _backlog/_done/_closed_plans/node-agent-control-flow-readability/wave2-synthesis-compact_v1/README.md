# Wave2 Synthesis — Final Reader Interface (v1)

> **FINAL DESIGN / REVIEW ONLY。** 这是已选定的 reader-interface 方案，不是运行时代码或已批准的实现。
> [v0](../wave2-synthesis-compact_v0/README.md) 仅保留为被取代的全景对照。

**Final 决定：v1 是最终选定的方法示例，不是要求所有 node 复刻 Wave2。** 后续实现与评审
应采用它的最小、症状驱动 reader interface，并根据各 node 的实际职责、authority 与控制流
编写内容；它不是两个候选方案中的一个。

v0 证明了“每个 LLM-bearing node 可以有一份 reader-facing `workflow.md`”。v1 只保留
这份 interface 对人和 Coding Agent 真正有杠杆的部分：跨文件因果、症状到修改 owner 的入口，
以及最低责任测试。

## Final interface scope

当前 Wave2 的局部循环已经在 `node.py::build_real` 中清楚表达：读 evidence、建 request、
调用模型、接纳 candidate、至多一次 repair、写 artifact/preview。把这段代码完整翻译成文档，
不会增加多少维修 leverage，反而会造成第二份会过期的实现说明。

真正需要 reader interface 的，是不在同一个模块里的事实：

- capability **body**、不是 metadata，怎样进入模型的 system prompt；
- local validation 怎样触发 repair，以及 validation code 当前没有传给 repair model；
- node、wrapper gate 和 executable builder 各自拥有什么 route authority。

因此 v1 的 [workflow.md](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md)
是短维修地图，而不是完整控制流复述。

## v0 与 v1 的差别

| 项目 | v0 | v1 |
| --- | --- | --- |
| `workflow.md` | 267 行的全景解释 | 小型、症状驱动的维修 interface |
| 主循环 | 再画一遍完整 flow | 链接回 `node.py::build_real` |
| runtime prompt 装配 | 列出每一跳 | 只保留 Wave2 容易误改的可见性事实 |
| failure / repair | 完整分类和 worked example | 一条关键 feedback 事实 + owner/test |
| branch inventory | generated region + checker proposal | 暂不引入；prompt catalog/topology 仍是 authority |
| checker / metadata | 已展开 review prototype | 暂缓，等至少多个 node 证明有同一稳定 seam |

## v1 目录刻意很小

```text
review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/
├── node.py, prompts.py, capabilities.py, capabilities/  # 当前实现快照
└── workflow.md                                          # 唯一新增 reader interface
```

没有 `workflow_review.py`，也没有 checker、generated inventory 或第二份语义 schema。代码、
spec 与测试仍是唯一 authority；`workflow.md` 只帮助读者更快到达它们。

## Final regression task

给两个版本同一个问题：

> initial candidate 因 `synthesis_findings_required` 失败，repair 又犯同样错误。应改哪里、如何证明？

陌生 Coding Agent 应能直接打开 `node.py::build_real`、
`prompts.py::build_synthesis_repair_prompt` 和相应测试，就说明小 interface 足够。若仍要先读
完整 runtime chain 或 checker，应只把缺失的那一条事实补回此 interface，而不是恢复 v0 的整张说明书。
