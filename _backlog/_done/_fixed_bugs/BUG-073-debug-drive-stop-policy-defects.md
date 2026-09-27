# BUG-073: 调试驱动的 stop policy 三处缺陷（HITL 重入 / 暂停崩溃 / 并发暂停被丢弃）

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 已修复（2026-09-27）

## 症状（均在我为"暴露全部能力"而测试 `/run`、`/pause` 时暴露）

1. **`drive_until` 无视 `stop_on_hitl`**：从 HITL 停顿处执行一次 `drive_until`，会一路
   重入正在等待的节点直到循环上限——实测 **一次命令调用 `_advance` 64 次**（循环上限），
   姿态看似"停在 hitl1"只是假象。规范 LDD-003 早已要求"停在正式 HITL 请求"。
2. **pending pause 让 `_drive_until` 返回 `None`**：先 `/pause` 再 `/run` 时，循环在
   `if session["pause_requested"]: break` 处**未推进就退出**，`last` 仍为 `None` →
   `_with_observation` 访问 `update.denied` → `AttributeError`（应用级崩溃）。
3. **并发 pause 被静默丢弃**：`_invoke_once` 在每次提交后无条件
   `session["pause_requested"] = False`，于是"运行中请求暂停"（LDD-001 明确支持的
   `pause_request` 用法）会被刚提交的边界清掉，永远不生效。

## 根因

`_drive_until` 的循环把暂停判断放在**推进之前**（且缺 HITL/终态之外的停点判断），并且
允许在没有推进的情况下返回 `None`；`pause_requested` 的所有权分散在 `_invoke_once`
与循环两处，导致"谁负责清除"没有单一答案。

## 修复（2026-09-27，change `expose-debugger-pending-request-and-capabilities`）

- 循环改为**先推进一次**，再按 `stop_on_hitl` / 终态 / 断点 / "本轮之前或期间请求过暂停"
  决定停点；暂停在**下一个已提交边界**生效（符合 LDD-001 的 pause honesty），并在此处
  清除标志；循环**永不返回 None**。
- 移除 `_invoke_once` 对 `pause_requested` 的无条件清除（并发暂停得以保留）。
- 工作台侧：终态会话上 `/pause` 明确回答"没有下一个节点边界可暂停"，不再承诺停点。

## 证据

- `tests/integration/test_debug_driver_matrix.py`：
  `test_drive_until_stops_at_the_hitl_boundary_once`（断言 `_advance` 调用次数 == 1、
  姿态 `awaiting_hitl`、下一节点 `hitl1`）；`test_a_pending_pause_makes_the_next_drive_advance_one_boundary`
  （恰好提交一个节点、姿态 `paused_at_boundary`、标志已清）；既有 pause honesty 测试继续绿。
- harness `make tui-journey` 新增 `[12]`-`[14]`（Start Run 停在 HITL、`/run` 到终态、
  终态 `/pause` 诚实回答），共 23 个检查点全绿。
- 规范面：LDD-003/LDD-001 的既有语义即为正确行为，因此这两个缺陷是**实现追平规范**；
  本次 change 只把快照的 pending-request 投影作为**加法式**规范字段。

## 修复关联

- change: `openspec/changes/archive/2026-09-27-expose-debugger-pending-request-and-capabilities`
- 回归：上述两条驱动测试（红→绿）；`/pause` 终态守卫由 TUI 测试与 harness 断言钉住。
