# BUG-035: wave2 honest gap 两轮补证不收敛导致 003 真实 run 必死于 gate blocked

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 已修复（openspec/changes/honest-delivery-and-real-run-diagnostics）

## 症状

两次真实 003 run（`soft-bundle run <root> --mode 003`）**同型失败**：最终都停在
`wave2_synthesis` gate blocked（`research.blocked`，typed incident），执行轨迹
完全相同：

```
bootstrap -> hitl1 -> hitl1_auto_profile -> topic_planning -> wave0 -> wave1
-> wave2_synthesis -> targeted_evidence -> wave2_synthesis -> targeted_evidence -> wave2_synthesis
```

- 第 1 次（bundle `b_iW_7JGji_X2dVMRp8d00x5dcIVaTKnZ-LZnmKl1_b3s`，
  `diag_101a8eefdd125d581350007c`）：gap = "No accepted evidence provides a
  precise full-year 2024 total for China's installed capacity…"（精确数字缺失）。
- 第 2 次（bundle `b_C7H5yIqdf_EgWxSjGeBR1SoGzfWE2NkmUixu1v1z7v4`，
  `diag_e243a4df6c5f0594cffd721a`）：gap = `gap:g_q_w1_oq_1`（wave1 遗留 open
  question 投影）："The accepted evidence does not explain whether the differing
  2024 China power battery market share figures (CATL 45.2% vs 45.08%; BYD 25.1%
  vs 24.74%)…"。

两次都是 wave2 产出真实 findings（4 条，含整数 priority）+ 1 个 honest
searchable gap，两轮 targeted 补证后 gap 仍 `search_required=true` → 第三轮
评估预算耗尽 → 整个 run BLOCKED，无 report、无降级产物。

## 根因

wave2 gate 的"预算耗尽即整体终止"语义对真实模型无收敛保证：

1. wave1 遗留 open question 投影为 wave2 searchable gap（既有机制，正常）；
2. minimal 意图下 gate 预算 = 2 轮补证（`low-scale-real-auto` 新增的
   budget_resolver，机制本身按设计生效并已实测）；
3. 但 honest gap（"两个来源数字为什么不同"、"精确全年总量是多少"）本质是
   证据间矛盾/缺失，**不保证 N 轮 targeted 搜索内收敛**；
4. 预算耗尽 → `REPAIR_BUDGET_EXHAUSTED` → BLOCKED，**没有"带 honest gap 降级
   到 readiness/final_delivery、报告如实披露 gap"的路径**。

对"最低规模跑通"（003 验收 = RESULT: PASS + 真实 report）这是机制性障碍：
只要 wave1 留 1 个 open question 且补证不收敛，run 必死。修复方向不是"再加
预算"，而是给 wave2 增加**诚实交付降级语义**（gap 不收敛时进入带 gap 的
readiness/final，报告披露 gap + 引用），或在 gate 语义上区分"可补证的 gap"与
"证据矛盾型 gap"。

## 复现

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 003"
```

连续 2/2 次复现（2026-08-18，固定问题 "What is one bounded fact about China's
EV battery market in 2024?"，真实 DeepSeek + Tavily）。run 输出结尾：
`结果类别: research.blocked / 已知阶段: wave2_synthesis / 可重试: 否`。

## 修复关联

已修复：`openspec/changes/honest-delivery-and-real-run-diagnostics/`（gate-kernel
增加 opt-in `degraded_pass_on_exhaustion`：首次预算耗尽且无 hard failure 时
降级为 degraded pass，经 `degraded_decisions` 标记限一次/预算播种期，rerun
重置同步清标记；readiness 将 `unresolved_gaps` 投影为报告 Uncertainties，
gap 描述读自 canonical `synthesis/findings.json`；runbook-003 验收同步）。
确定性证据：`tests/engine/test_gate_kernel.py`（TestExhaustionDegradation）、
`tests/graph/test_gate_integration.py`（TestRealWave2GateOutcomes）、
`tests/unit/test_honest_delivery_disclosure.py`、
`tests/unit/test_readiness_real.py`（TestHonestGapDisclosure）。原修复建议段落
（历史记录）：

`openspec/changes/archive/2026-08-18-low-scale-real-auto/`（已归档；本 bug 是
其验证暴露的 follow-up）。修复建议走独立 change：wave2 诚实交付降级语义 +
runbook-003 验收标准同步（或显式把"wave2 honest gap 收敛失败"列为已知验收
例外）。与 BUG-036（journal 显示矛盾）同源观测。

## 修复后真机验证（2026-08-18，tasks.md 6.1）

`soft-bundle run … --mode 003`（bundle `b_T0PuZxnG4jibqyHqAaVEP8kjB-uq-zDwnY_TXDaZiWc`，
真实 DeepSeek + Tavily）。checkpoint 时序（graph.sqlite writes 解码）：

```
wave2 gate: repair/evidence_needed (budget 1) -> repair (budget 0)
         -> pass (checkpoint 1f19aac0, degraded_decisions=[wave2_synthesis:exhaustion_degraded])
         -> hitl2 -> readiness -> targeted_evidence -> wave2 gate: blocked/exhausted (二次耗尽, marker 已在)
```

- **首次耗尽降级为 pass**：图继续走到 hitl2/readiness（修复前此处即死）；
  `review/report-plan.json` 的 mandatory_uncertainties 如实披露了 gap——
  `Unresolved research gap gap:g1: "Accepted evidence does not state China's
  total power battery installed capacity for the full year 2024…"`。
- **降级后再次耗尽合规 blocked**：第二轮补证后 gap 仍在，按设计止步
  `research.blocked`——单次降级机会（每预算播种期）语义与 spec 一致。
- 结论：降级/披露/一次性边界三个行为在真机全部如预期；本 run 的 blocked 是
  诚实 gap 两轮均未收敛的合规结果，非缺陷。
