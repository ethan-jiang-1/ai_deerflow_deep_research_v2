# Wave2 Synthesis 隔离 Review Example

> **SUPERSEDED BY v1 FINAL。** 此目录只保留 v0 的全景/checker 对照；不要将它当成新 node
> package 的 reader-interface 模板。最终方向见 [v1](../wave2-synthesis-compact_v1/README.md)。

> **REVIEW ONLY - 全部内容位于 `_backlog`，正式 `agent/` 保持不变。**
>
> `review-example/` 下面实际创建了一棵未来形状的 `agent/` 目录。里面的真实代码快照、
> capability Markdown、`workflow.md`、checker、index 和 tests 可以一起打开 review；它们不会被 runtime 导入。

## 先看最终读物

[隔离样例的 Wave2 workflow.md](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md)
是此 example 唯一需要交给读者的 maintenance interface。它现在包含：

- 症状到 exact owner/test/eval 的维修表；
- capability、objective、expected output、evidence 各自怎样进入模型的分类；
- 从 graph wrapper 到 capability loader、model invocation、admission、gate 和 route 的真实链；
- local validation、repair 和 targeted-evidence re-entry 的真实 feedback 语义；
- 一个 `synthesis_findings_required` 的完整修复例子。

这个 example 不保留 `workflow_review.py`，也不保留第二份 `workflow.md` 内容。之前的大 literal 让维护者先学习另一套 schema，
却没有回答 runtime 谁读取它、字段怎样进入模型、发生问题应改哪里。它没有为调用者隐藏
复杂度，因此不值得成为新的 module interface。

## Review Example 中真实存在的位置

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

上面每个路径都已经在 `_backlog` 中创建，不再把“未来可能有的文件”混进现状图。更完整的
snapshot/proposal 分类和 review 顺序见 [review-example/README.md](review-example/README.md)。
正式 repo 中的同名 checker/index/workflow 仍然不存在，除非这个设计 review 后另行获批。

## 同一个真实目录里各文件怎样配合

| 真实文件 | 在这个示范中的职责 | Coding Agent 什么时候打开 |
| --- | --- | --- |
| [`workflow.md`](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md) | reader-facing 维修 interface；把症状、模型输入、feedback、authority、route 和 tests join 在一起 | **先打开**，按症状选 owner |
| [`node.py`](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py) | 当前真实 controller 的 review snapshot：取 evidence、调用模型、接纳 candidate、触发一次 repair、写 artifact | workflow 指向 `build_real` 或 `_validate_synthesis_semantics` 时 |
| [`prompts.py`](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/prompts.py) | 当前真实 prompt builder/parser 的 review snapshot | 模型任务、输出格式或 repair request 有问题时 |
| [`capabilities.py`](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/capabilities.py) | capability ID 到 package resource 的确定性引用快照 | capability 加载或 branch binding 有问题时 |
| [`wave2-evidence-synthesis.md`](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/capabilities/wave2-evidence-synthesis.md) | metadata 后的 body 进入 system policy | 模型误解角色或越权时 |
| [`wave2-evidence-synthesis-repair.md`](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/capabilities/wave2-evidence-synthesis-repair.md) | repair 分支的 model-visible cognitive policy | repair 模型误解任务时 |
| [`__init__.py`](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/__init__.py) | `NODE_SPEC` 与 real factory binding 的快照 | node 注册或 factory binding 有问题时 |
| [`node_workflow_docs.py`](review-example/agent/scripts/node_workflow_docs.py) | 只检查/替换 generated inventory 的 proposed adapter | 文档 identity、coverage 或 freshness 有问题时 |
| [`test_node_workflow_docs.py`](review-example/agent/tests/graph/test_node_workflow_docs.py) | checker 的 focused proof | 怀疑 generator 会覆盖 prose 或接受坏 marker 时 |

这就是供 review 的实际放法：Python 和 capability MD 展示 future package 的 implementation，
`workflow.md` 提供小的维修 interface，checker 只是受限 adapter。样例 `node.py` 顶部示范一行
reader-facing locator，但正式代码没有这项修改，是否保留也属于本次 review。

## 谁读取什么

| Surface | Reader | 作用 | 不做什么 |
| --- | --- | --- | --- |
| `graph/nodes/wave2_synthesis/workflow.md` prose | 人与 Coding Agent | 维修导航、智力回路、真实 source trace | 不进入 prompt，不驱动 runtime |
| 第一行 metadata | proposed checker | 校验 logical node、classification、coverage | 不定义模型、route 或权限 |
| `BEGIN/END GENERATED` 区块 | proposed checker/renderer | join `prompt_catalog_cases()` 与 `NORMALIZED_EDGES` | 不生成或覆盖人工维修语义 |
| capability Markdown body | runtime prompt renderer | 追加到模型 system policy | 不读取 `workflow.md` |
| `prompts.py` 产生的 request | runtime bridge | 形成模型 user message 与请求级工具窗口 | 不读取 review metadata |

因此不存在“AI 要先猜谁加载 `workflow_review.py`”的问题。修 runtime 问题时，Coding Agent
只把 `workflow.md` 当地图，再打开它指向的当前 authority。

## 有界生成关系

```text
prompt_catalog_cases() -----> direct branch/capability facts --+
                                                              +--> workflow.md generated region
NORMALIZED_EDGES -----------> semantic route/target facts -----+

node.py + prompts.py + loader + bridge + tests
          --human-reviewed exact refs--> workflow.md authored sections
```

机器能推导的 inventory 才生成。模型看见什么、feedback 是否真的送达、异常由谁转换、某个
症状应从哪里修，都必须由 reviewer 对照 source/test 写在同一份 MD 中；checker 只能验证链接
和 freshness，不能假装证明语义。

## 用什么问题验收

不要问“这份文档读起来顺不顺”，直接给一个维修任务：

> Wave2 initial candidate 因 `synthesis_findings_required` 失败，repair 又犯同样错误。
> repair 模型实际收到了这个 validation code 吗？若没有，改哪些 symbol 和测试？

陌生 Agent 只读 [隔离 workflow.md 的完整修复例子](review-example/agent/src/deerflow_deep_research/graph/nodes/wave2_synthesis/workflow.md#一个完整的修复例子)，应能回答：

1. 当前没有收到；`except ValueError` 丢弃了错误。
2. 首要修改 `node.py::build_real` 与 `prompts.py::build_synthesis_repair_prompt`。
3. prompt catalog synthetic case 也要适配 builder signature。
4. 应扩展 real-node request assertion，再用 live canary 观察质量。
5. 当前 canary 使用 HITL1 bridge，不能充当专用 Wave2 execution-policy authenticity proof。
6. 不应先放宽 parser、修改 gate 或重接 graph edge。
