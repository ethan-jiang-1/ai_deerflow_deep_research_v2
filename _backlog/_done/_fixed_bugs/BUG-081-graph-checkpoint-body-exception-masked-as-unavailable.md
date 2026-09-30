# BUG-081: open_graph_checkpoint 把调用方 body 的图执行异常包装成 bundle_unavailable——图节点守卫错误被掩蔽成"存储不可用"

> 严重级别: P2 | 发现: 2026-09-29（live journey 探针 hitl2 现场观察） | 状态: 已修复（2026-09-29，主动立卡收窄）

## 症状

live journey 探针某轮（BUG-079 修复前）在 hitl2 抛 `hitl2_state_invalid`
（`graph/nodes/hitl2/prompts.py:50-57` 的状态守卫），但操作者/调试器看到的却是
`BundleLifecycleError("bundle_unavailable")`——**图逻辑错误被错误归类为存储可用性故障**，
恢复动作被导向"Bundle 丢了"的错误分支，真正的状态问题被掩蔽。

## 根因

`runtime/bundle_lifecycle.py::open_graph_checkpoint` 的
`except (OSError, RuntimeError, ValueError)` 包住**整个** `async with` 体，包括
`yield` 之后调用方 body 里跑的图执行（`bundle_graph` 各 invocation、`debug_driver`
的 advance/rerun 都在 body 内 `graph.ainvoke`）。节点守卫抛的
`ValueError("hitl2_state_invalid")` 穿过 yield 落进该 except，被统一重新包装。
语义混淆点：**setup 阶段**（开连接、serde 装配、准入检查）的这三类异常确实是
"Bundle 存储不可用"的事实；**body 阶段**的异常是图执行的因果，不是可用性事实。

## 复现

无头红环：`tests/unit/test_checkpoint_error_boundary.py::
test_open_graph_checkpoint_does_not_mask_a_caller_body_failure`——
已发布 Bundle 上 `async with lifecycle.open_graph_checkpoint(BUNDLE)` body 内
抛 `ValueError("hitl2_state_invalid")`，断言其原样穿透（`pytest.raises(ValueError)`）。
修复前该异常变成 `BundleLifecycleError("bundle_unavailable")`（红）。

## 修复关联

`open_graph_checkpoint` 以 `body_entered` 标志区分阶段：yield 开始前（setup）的
`OSError/RuntimeError/ValueError` 仍包装为 `bundle_unavailable`；yield 后（调用方
body）的异常原样穿透，不再改写归属。`CheckpointStateBoundExceeded →
bundle_graph_over_bound` 的映射保持不变（存储越界是 store 事实，REG-008 语义）。
setup 侧可用性行为由既有 `tests/unit/test_state_persistence.py::test_bundle_graph_
checkpoint_is_contained_and_cannot_reopen_after_bundle_loss` 继续锁定（修复后保持绿）。
