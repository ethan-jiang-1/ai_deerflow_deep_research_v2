# BUG-070: 调试工作台"下一节点"投影始终为空

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 已修复（2026-09-27）

## 症状

runbook-030 的调试工作台在 fixture 流程中，面板的 `下一节点` 始终显示 `—`，
即使图确实还有后续节点。实测（`make tui-journey` 的 11 步 transcript）：从
`paused_at_boundary` 到 `terminal`，每一帧的 `下一节点` 都是 `—`；推进本身正常
（日志逐行给出 `✓ bootstrap 提交（帧 2）` … `✓ final_delivery 提交（帧 10）`）。

## 根因

`DebugRunDriver._boundary_cursor`（`runtime/debug_driver.py:364`）把
`next_nodes` 取自 `RunTraceProjector.project_full(...)` 最后一帧的
`frame.next_nodes`：

```python
page = await RunTraceProjector(self._lifecycle).project_full(bundle, live=True)
last = page.frames[-1] if page.frames else None
next_nodes=last.next_nodes if last else (),
```

即 trace projector 产出的 frame 没有填充 `next_nodes`（或投影时未从图状态读取
`snapshot.next`）。驱动侧的 step 逻辑本身用 `graph.aget_state(config).next` 决定
`interrupt_after`，所以推进不受影响——缺的只是面向操作者的投影。

## 复现

```bash
cd deep_research_harness
make tui-journey            # 观察每步的 inspect 行：下一节点恒为 —
# 或人工：./run/tui-workflow-debugger.sh --fixture → 提交问题 → 观察面板
```

## 修复关联

已修复（2026-09-27）：`_invoke_once` 在 invoke 后本就持有
`post = graph.aget_state(config)`，现将 `post.next` 线程化进
`_snapshot(next_nodes=...)` → `_boundary_cursor(next_nodes=...)`，游标由此携带
**真实的下一个节点**（`_terminal_update` 传空）；trace frame 的回退保留给没有图
状态的调用方。

同时修掉一个被该字段掩盖的设计缺陷：`BoundaryCursor.token()`（driver 的写许可）
原本把 `next_nodes` 也序列化进 token，导致"投影字段"参与边界身份——命令校验路径
用回退游标（空 next）重算时必然与快照 token 不一致，`execute` 判定 `stale`。
现在 token 只含 durable boundary 身份（bundle/generation/frame/checkpoint），
投影字段不参与 write permit。

回归锁：
- `tests/integration/test_debug_driver_matrix.py::test_cursor_reports_the_next_node_after_a_step`
  （step 后游标命名 `hitl1`；token 对 next_nodes 不变）；
- `make tui-journey` 逐步断言：Start Step 后 `下一节点: hitl1`，ladder 每个 paused 帧
  的下一节点非空（terminal 时为 `—`），显示为逗号连接的节点名而非 tuple repr。
