# BUG-070: 调试工作台"下一节点"投影始终为空

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 活跃

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

在 trace projector 的 frame 投影处填充 `next_nodes`（来源：该帧对应 checkpoint 的
`snapshot.next`），或在 `_boundary_cursor` 直接读取图状态而不经 frame 投影——
前者更正确（投影本就是"可观察事实"的唯一来源，避免第二权威）。修复后
runbook-030 的 harness 断言可加一条"paused 帧的下一节点非空且等于预期节点"，
把这条可见性锁进 `make tui-journey`。当前 runbook-030 已诚实标注该显示可能为
`—`，并以提交日志为推进权威。
