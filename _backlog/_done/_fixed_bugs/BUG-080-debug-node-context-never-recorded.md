# BUG-080: embedded 调试工作台的 Node Context 恒空——build_demo_runtime 从未接到 recorder holder

> 严重级别: P1 | 发现: 2026-09-29（live 自证探针） | 状态: 已修复（2026-09-29，live 自证阶段发现）

## 症状

live 全流程探针跑通真管线到 terminal 后，NodeContextStore `page.total == 0`——
wave0/wave1 等真模型的调用上下文**一条都没被捕获**，runbook-031 承诺的
`/context` 真实快照（exact prompt / enforced tools / budget / mounts）在
embedded 调试模式下从未存在过。这正是交接单里"尚未验证"的那一项；live 首次
验证即证伪。

## 根因

`scripts/demo_tui.py::_initialize` 的两处 `build_demo_runtime(...)` 调用
（real 与 fixture_graph）**都没有传 `node_context_recorder_holder`**。real 路线：
`_make_recorder_bridge_factory(None)` 返回 None → `build_real_demo_recipe` 落回
无 recorder 的默认 bridge → 任何节点上下文都不会被记录。TUI 明明在
`debug_mode` 下建了 `self._node_context_holder` 并在会话开始时绑好
`NodeContextRecorder`（`_bind_node_context`），但那个 dict 和运行时之间**断线**。
fixture 路线的 E15 之所以绿，是 fixture recipe 的内部缺省另有通路，掩盖了同一处
调用点缺陷。

## 复现

无头红环：`tests/integration/test_demo_tui.py` 的
`test_debugger_wiring_hands_the_node_context_holder_to_the_runtime`——spy
`build_demo_runtime`，断言 real/fixture 两次构建都收到 TUI 的 holder dict；
修复前收到 None（红）。端到端由 live 探针
`tests/live/test_debugger_embedded_live.py` 断言 `page.total >= 1` 锁定。

## 修复关联

change `debugger-node-rerun-and-auto-hitl` 的 live 自证阶段发现；修复 =
两处 build 调用补传 holder（c4b 提交 9006057 线程化了 `_demo_core` 侧，
但 demo_tui 调用点从一开始就漏传）。
