## Why

真实 003 run（BUG-044，连续两次同签名复现）在 wave2 honest gap 上
`research.blocked`：wave2 gate 首次预算耗尽已按 BUG-035 降级为 pass
（`degraded_decisions` 写入 `wave2_synthesis:exhaustion_degraded` marker）→
hitl2 → readiness，但 readiness 在 critic 模型调用失败时走保守回退
（`blocked_repair_required`），把流程路由回 `repair_targeted` →
targeted_evidence → wave2_synthesis → gate 再次求值发现 budget=0 且 marker
已存在 → BLOCKED。降级后 repair 是必死回路：runbook 5.1 "降级 → hitl2 →
readiness → final_delivery → completed（带披露）"的契约被违背。

> 关联（独立 bug，不在本 change 范围）：同一 run 的 wave2 不收敛根因另在
> BUG-045——targeted worker 未排序 source_refs 导致补证候选校验必败
> （9/9 零产出）。本 change 只保证"降级后能 completed 交付并披露 gap"；
> 补证循环的收敛能力由 BUG-045 的独立 change 恢复。

## What Changes

- readiness 路由判定新增一条优先级：当 wave2 gate 已降级
  （`degraded_decisions` 含 `wave2_synthesis:exhaustion_degraded` marker）时，
  `blocked_repair_required` 不再路由 `repair_targeted`，改路由 `pass`
  （降级交付：report plan 继续把 gate 记录的 unresolved gaps 披露为
  mandatory uncertainties）。
- 结构性 hard-rule 失败仍优先路由 `exhausted`（BLOCKED），不受此改动影响。
- 非降级 run 行为完全不变（`blocked_repair_required` 仍路由
  `repair_targeted`，即现有收敛循环）。
- 不改 wave2 gate 的降级语义（每次 budget seeding 至多降级一次），也不放宽
  任何预算。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `readiness-node`: REA-004 路由优先级新增"wave2 已降级 → `blocked_repair_required`
  路由 `pass`（降级交付）而非 `repair_targeted`"的契约。REA-006 的保守回退
  本身不变（仍投影 `blocked_repair_required`），去向由 REA-004 的降级分支决定。

## Impact

- 代码：`src/deerflow_deep_research/graph/nodes/readiness/node.py`（路由判定，
  读 `state["degraded_decisions"]`）；无 engine/domain 改动。
- 测试：`tests/unit/test_readiness_real.py` 新增降级 run 下 bridge 失败/候选
  拒绝路由 `pass` 的用例；`tests/unit/test_honest_delivery_disclosure.py` 的
  降级披露链不受影响。
- 行为：真实 003 run 在 wave2 honest gap 不收敛 + readiness critic 失败时，
  终态从 blocked 变为 completed（report 带 Uncertainties 披露），与
  runbook-003 5.1 的契约一致。注：BUG-045 未修前，补证循环仍零产出，
  report 以 gap 披露为主（诚实降级交付）；补证收敛待 BUG-045 修复。
