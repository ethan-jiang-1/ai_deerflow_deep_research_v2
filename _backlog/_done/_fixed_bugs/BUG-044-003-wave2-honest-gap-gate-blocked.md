# BUG-044: 003 real-auto 在 wave2 honest gap 上 `research.blocked`（gate_blocked），未按 runbook 5.1 降级为 completed

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 活跃

## 症状

`soft-bundle run <root> --mode 003`（真实 DeepSeek + 真实 Tavily，固定问题
`What is one bounded fact about China's EV battery market in 2024?`）：
8/9 节点 completed（`final_delivery` 缺失），终态 `blocked`，
`RESULT: FAIL`（exit 2），`final/report.md` 未生成。

- 终端结果：`结果类别: research.blocked`，`已知阶段: wave2_synthesis`，
  `可重试: 否`，诊断引用 `diag_a59e8e299eb6555c27709b24`。
- `diagnostics/run-summary.json`：`status=blocked`、`phase=wave2_synthesis`、
  `failure_category=research.blocked`、`terminal_outcome=blocked`、
  `terminal_reason=gate_blocked`、`journal_availability=complete`、
  `dropped_event_count=0`、`execution_profile=deepseek-v4-flash`。
- 这是 handoff-003 首次 run 的同签名复现（首次 run 也是 wave2 honest gap
  收敛失败 → `research.blocked`）；**已连续 2/2 次真实 003 run 触发 blocked**，
  runbook 5.1"单次 003 run 预期不会触发"的预期被证伪。

完整证据 bundle 已保全：`_backlog/_done/_evidence/003-blocked-20260818-b_8iYx4hy/bundle/`
（events.jsonl 133 事件、state.json、profile.json、findings.json、work/、graph.sqlite）。

## 复现

```bash
cd deep_research_harness   # 需 .env（DEEPSEEK_API_KEY/TAVILY_API_KEY/DEERFLOW_DEMO_MODEL）+ 网络
ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 003-demo --mode 003" | sed -n 's/^soft_bundle_root=//p')
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 003"
# → 结果类别: research.blocked / 已知阶段: wave2_synthesis / 可重试: 否
```

执行流（events.jsonl 序号）：bootstrap → hitl1 → topic_planning → wave0(w0000)
→ wave1(w0000, 重跑 w0001) → wave2_synthesis#1 → targeted(w0000..w0002)→exhaustion
→ synthesis#2 → targeted→exhaustion → synthesis#3 → hitl2 → readiness
（readiness model_tool **failed**，seq 106）→ targeted(retry)→exhaustion →
synthesis#4 → terminal blocked。

## 根因（已定位到机制层）

产品机制全部按设计生效，问题集中在 wave2 收敛路径的**降级判定**：

1. **minimal 意图机制正确**：`request/profile.json` =
   `cost_tolerance=minimal`、`depth=quick_overview`、`time_budget=very_quick`、
   `must_answer=[固定问题]`、`degraded_profile=true`——意图声明 → 自动建档
   构造 minimal profile 的链路 OK。
2. **single_topic 正确**：topic_planning 产出 1 个 scope
   `2024-china-ev-battery-market-volume-and-share`；wave0 恰好 1 个 work unit
   （`g0_wave0_w0000`）。
3. **wave2 gate 2 轮补证预算生效**：targeted_evidence 每轮 w0000..w0002
   （初始 + 2 补证）后 exhaustion。
4. **降级路径未生效（本 bug 核心）**：runbook 5.1 说"预算**首次**耗尽 →
   degraded pass → hitl2 → readiness → final_delivery → completed"，实测
   readiness 在 critic 模型失败（seq 106 model_tool failed → 保守回退
   `blocked_repair_required`）后路由 `repair_targeted`（REA-004 旧逻辑：
   任何 blocked_repair_required 都送 repair）→ 送回 targeted_evidence →
   wave2 gate 在 budget=0 + 降级 marker 已存在时二次耗尽 → `gate_blocked`。
   sqlite 铁证：gate#3 `verdict=pass` + `degraded_decisions=
   wave2_synthesis:exhaustion_degraded` → readiness `route=repair_targeted`
   → gate#4 `verdict=blocked` + `repair_budget_exhausted` →
   `terminal=gate_blocked`。**降级后 repair 是必死回路**（gate kernel 每次
   budget seeding 至多降级一次是有界设计，见 `tests/engine/test_gate_kernel.py`
   580-621），readiness 必须改为降级 run 直接 pass 交付。
5. **honest gap 本体**：`synthesis/findings.json` 的 `gaps` 明确披露——
   "Accepted evidence does not provide the total EV battery installation volume
   in China's domestic market for 2024"（只有份额 45.08%/24.74% 与全球总量，
   缺中国国内总量）。

**重要关联**：本 run 的 wave2 不收敛并非单纯模型波动——targeted 补证循环
9/9 attempts 全部 `work.failed`（零产出），根因是 **BUG-045**（targeted
worker 未排序 source_refs → 候选校验必败）。修 BUG-044 只保证"降级后能
completed 交付（披露 gap）"；修 BUG-045 才让补证循环有收敛可能。两个 bug
相互独立、都需修。

次要观察（同一 run，登记备用）：
- **wave1 出现第二个 work unit**（`g0_wave1_w0001`，10:33:49 node 重跑），
  但 scope 与 w0000 相同（同一 topic 的 repair 重跑，不同 spec_hash）——
  single_topic 未失效，但 runbook 第 6 节"wave0/wave1 各恰好 1 个 work
  unit，若出现多个说明 single_topic 没生效"的验收措辞与实际 gate 重跑机制
  不符，需改措辞（区分"planner 多 topic"与"同 topic 重跑"）。
- **gap id 轮间不稳定**：round 2 的 `unresolved_gaps` 为 `gap_q1..q3`，
  round 1/3/4 为 `gap_1..3`（gap id 是模型自由生成的）。软问题：补证证据
  仍会进 ledger，但"resolved"状态跨轮不累积。
- **runbook 5.1 预期被证伪**："单次 003 run 预期不会触发 blocked"——连续
  2/2 次触发，措辞需改为"可能触发"。

## 修复关联

✅ 已修复（2026-08-18，代码已落地）：OpenSpec change
`openspec/changes/fix-readiness-degraded-route/`（`readiness-node` REA-004
delta，已 polish → apply）。修复 = readiness 路由判定新增 `wave2_degraded`
条件（`exhaustion_degradation_marker("wave2_synthesis") in
state["degraded_decisions"]`）：降级 run 中 `blocked_repair_required` 路由
`pass`（降级交付，report plan 继续披露 unresolved gaps）；结构性失败仍
`exhausted`；非降级 run 行为不变。验证：`tests/unit/test_readiness_real.py`
新增 4 用例（critic 失败/候选被拒/结构失败/ready 四象限），全量
`make verify` 通过，ruff 干净，`openspec validate --strict` 通过。
真实 003 验证 run 待 BUG-045 修复后一并跑（一次 run 验两个 change）。
