# BUG-079: 调试器启动的真图研究一直跑在回退问题 "Research" 上——操作者的真问题从未进入图

> 严重级别: P1 | 发现: 2026-09-29（live 自证探针） | 状态: 已修复（2026-09-29，live 自证阶段发现）

## 症状

live 自证探针（tests/live，真凭证全流程）失败现场：图值里
`'request_text': 'Research'`——操作者在 composer 输入的真问题
（"Compare renewable energy storage technologies…"）**没有驱动研究**。
hitl1 反复追问 "What specific topic…should the research address?" 的真正原因：
图只知道 "Research"。操作者按提示补主题后 flow 才能走，表象是"调试器听不懂人话"。

## 根因

`runtime/debug_driver.py::open_start` 构建 session dict 时**不存
`request.question`**；`_invoke_once` 的 fresh 分支构造
`SelectedStartMessage(text=session.get("question", "Research"))`，
而 `BundleGraphExecutor._initial_graph_state` 用 `"request_text": start_message.text`
作为图的 request_text。链路结果：`lifecycle.start(request_text=真问题)` 只把真问题
写进 durable state（request_digest/request_text），图的初始载荷却拿到回退串。
fixture 图对问题内容无感 → 矩阵测试全绿；ALL_REAL 图的 hitl1 语义依赖 request_text
→ 只有 live 才暴露。

## 复现

无头红环：`tests/integration/test_debug_driver_matrix.py` 的
`test_open_start_carries_the_operator_question_into_the_graph`——open_start(唯一标记
问题) + advance，直读 checkpoint values 的 `request_text` 必须等于该标记；修复前是
"Research"（红）。

## 修复关联

`open_start` 的 session dict 补 `"question": request.question`（一行，会话自己的
载体）。发现于 change `debugger-node-rerun-and-auto-hitl` 的 live 自证阶段。
