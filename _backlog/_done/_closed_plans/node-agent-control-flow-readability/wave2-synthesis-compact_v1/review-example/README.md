# Wave2 Final v1 隔离 Review Example

> **FINAL DESIGN / REVIEW ONLY。** 此目录模拟已选定的最小 reader interface；它不参与 runtime。

相邻 Python 与 capability Markdown 是当前真实 Wave2 package 的 review snapshot。唯一的提案
文件是同目录的 [`workflow.md`](agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md)。

## Review 顺序

1. 只读 `workflow.md` 的“从症状进入”表，选择报告问题对应的一行。
2. 打开它指向的 `file::symbol`，以实现为事实源核对因果。
3. 运行表中对应的最低责任测试；需要时再扩展到 runtime 或 graph。

## 此样例刻意没有的东西

- 不复制 `node.py` 的完整控制流；源码已是该事实的 owner。
- 不逐跳解释 shared runtime prompt assembly；只有本 node 容易误读的差异留在地图中。
- 不含 `workflow_review.py`、JSON semantics schema 或 generated inventory。
- 不含 checker。一个 node 尚不足以证明这是一条值得维护的通用 seam；未来若多个 node 都有
  同样的机械 inventory，再让代码 owner 提供稳定字段并引入 adapter。

这使 `workflow.md` 成为一个小而深的 interface：读者用很少的内容定位实现、测试和跨模块
authority，而不是学习第二套 implementation。
