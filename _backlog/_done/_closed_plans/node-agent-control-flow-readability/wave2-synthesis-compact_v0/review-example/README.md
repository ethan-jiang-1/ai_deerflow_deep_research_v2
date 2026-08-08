# Wave2 Node Workflow 隔离 Review Example

> **SUPERSEDED BY v1 FINAL。** 此 review example 仅记录 v0 的全景/checker 备选方案；最终
> reader interface 见 [v1](../../wave2-synthesis-compact_v1/README.md)。

> **REVIEW ONLY。这个目录不参与 runtime，也不是已批准实现。**

这里把提案中的未来目录真实展开一次，让 reviewer 可以同时打开 Python、capability Markdown、
`workflow.md`、checker、derived index 和 checker tests，判断这种维护方式是否值得进入正式 change。

`review-example/` 模拟未来 repo root；因此它下面仍从 `agent/` 开始：

```text
review-example/
└── agent/
    ├── src/deerflow_deep_research/graph/nodes/wave2_synthesis/
    │   ├── __init__.py
    │   ├── node.py
    │   ├── prompts.py
    │   ├── capabilities.py
    │   ├── capabilities/
    │   │   ├── wave2-evidence-synthesis.md
    │   │   └── wave2-evidence-synthesis-repair.md
    │   └── workflow.md
    ├── scripts/node_workflow_docs.py
    ├── node_workflows/README.md
    └── tests/graph/test_node_workflow_docs.py
```

## 哪些是快照，哪些是提案

| Surface | 此样例中的来源 | Review 目的 |
| --- | --- | --- |
| `__init__.py`、`node.py`、`prompts.py`、`capabilities.py`、`capabilities/*.md` | 从当前真实 Wave2 package 复制的 review snapshot | 看 `workflow.md` 是否能正确解释并导航现有 implementation |
| `workflow.md` | 本计划人工维护的 reader interface | 看陌生 Coding Agent 能否从症状定位 owner、模型输入和测试 |
| `scripts/node_workflow_docs.py` | 本目录内的可运行 proposal | 看 checker 是否只处理 metadata 和 generated inventory |
| `node_workflows/README.md` | 仅导航的 derived-index 示例 | 看全局入口能否不成为第二 prose owner |
| `test_node_workflow_docs.py` | checker 的 focused example tests | 看人工 prose 是否不会被 generator 覆盖 |

快照不是新的代码 authority。真实实现仍在 repo 的 `agent/`；review 期间两边可能不同，整个
`review-example/` 最终应删除或由获批实现取代，不能长期同步维护。

## 建议 Review 顺序

1. 打开 `agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md`，只给自己症状：
   initial candidate 因 `synthesis_findings_required` 失败，repair 又犯同样错误。
2. 按 workflow 的 maintenance map 打开相邻 `node.py::build_real` 和
   `prompts.py::build_synthesis_repair_prompt`，验证因果链是否属实。
3. 对照两份 capability MD，确认 metadata 与 model-visible body 没有被混称为 prompt。
4. 最后读 checker 和 tests，确认机器只维护 `BEGIN/END GENERATED` 区块。

## 运行样例检查

从真实 `agent/` 环境执行，checker 只读取真实 prompt catalog/topology，再检查本 review 目录：

```bash
cd agent
uv run pytest -q \
  ../_backlog/_done/_closed_plans/node-agent-control-flow-readability/wave2-synthesis-compact_v0/\
review-example/agent/tests/graph/test_node_workflow_docs.py
```

这条命令不会写生产 package。手工刷新本样例的 generated region 也只能显式运行 review 目录下
的 `node_workflow_docs.py`，默认 `--check` 不写文件。
