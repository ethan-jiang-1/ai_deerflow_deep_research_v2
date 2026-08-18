# BUG-047: readiness/final_delivery critic 信封与构建器上限算术矛盾——真实 003 run 确定性 blocked

> 严重级别: P0 | 发现: 2026-08-18 | 状态: 活跃（本地修复已落地并经 run 4 验证：readiness critic 首次真正运行且一次通过，事件 84 前无任何 token_admission）

## 症状

真实 003 run（`run --mode 003`，bundle `b_fTetY-LjEppmlUk1L7K2ynXi8bMdcfgLDPvKsArrAWQ`，
诊断引用 `diag_c4c702505025f413a28821be`）：

- `RESULT: FAIL`，终态 `blocked`，`failure_category: budget.exhausted`，阶段 `wave2_synthesis`。
- `readiness` critic 的模型调用 **4 次全部** `budget_stop_reason: token_admission` 拒绝
  （事件序列 37/49/61/73，attempt a1–a4），从未真正到达网络。
- 之后空转循环 `wave2 → hitl2 → readiness → targeted_evidence` 4 轮（gate 每轮 pass，
  降级标记从未出现），最终 `wave2_synthesis` a5 被 `per_call_output_cap` 打断 → 终止。
- 研究内容本身是好的：`synthesis/findings.json` 有真实结论（2024 中国动力电池装机
  548.4 GWh，+41.5%，CAPBIIA/Gasgoo 来源）——被机制杀死，不是模型能力问题。

## 根因

**确定性算术矛盾，与模型行为无关（调用发出前即被拒）：**

1. `readiness/critic.py`: `MAX_READINESS_EVIDENCE_BYTES = 8_192` 允许 critic 请求装入
   8 KiB 证据；
2. `runtime/research.py`: readiness 策略 `total_token_budget=8_192`、
   `per_call_output_token_cap=2_048`；
3. `agents/middleware.py` admission：`请求 UTF-8 字节上界 + 2048 ≤ 8192`
   ⇒ **整个请求（脚手架+问题+证据投影+system message）必须 ≤ 6144 字节**。

实测（本次 run 真实数据复算）：证据 6255 字节（两个 work result）→ 请求 payload
7907 字节（objective 7473 + expected_output 434，尚未计 system message）——
**超出上限 ≥1763 字节**。证据一旦攒到 ~4.5 KiB 以上，readiness critic 永久不可运行。

放大器（循环无界）：critic 被拒 → `conservative_readiness_output` 把所有 must_answer
判为 `blocked_repair_required` → readiness 路由 `repair_targeted`（此时 wave2 gate
每轮都 pass，`exhaustion_degradation_marker` 从未写入，runbook 5.1 的"critic 失败也走
降级交付"只在 gate 已降级后生效）→ 补证 → wave2 → … 无独立边界，直到某个预算事故
（本次是 wave2 a5 的 `per_call_output_cap`）才终止。

**同形潜伏缺陷**：`final_delivery/composer.py` `MAX_FINAL_DELIVERY_EVIDENCE_BYTES = 8_192`
配同样的 8192/2048 信封——本次未走到，但算术上同样必然拒绝。

`research.py` wave2 策略注释明确写着 readiness/final_delivery 预算
"stay unchanged until real runs demonstrate a need (evidence-driven)"——本次 run
即该证据。

## 复现

```bash
cd deep_research_harness
ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 003-demo --mode 003" | sed -n 's/^soft_bundle_root=//p')
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 003"
# 预期（bug 存在时）: RESULT: FAIL / blocked / budget.exhausted @ wave2_synthesis
# events.jsonl 中 readiness 的 model_tool 事件全部 token_admission
```

确定性复算（无需真实模型，静态算术即可证）：

```bash
PYTHONPATH=src .venv/bin/python -c "
from deerflow_deep_research.graph.nodes.readiness.critic import build_readiness_critic_request
# 用 ≥4.5KiB 的 SynthesisEvidence 构建请求，objective+expected_output > 6144
# ⇒ BudgetMiddleware TOKEN_ADMISSION 必拒"
```

## 修复关联

已由 change `fix-request-envelope-coherence` 落地（2026-08-18）：信封对齐
（readiness 16,384 / final_delivery 24,576）与 wave2 拟合投影（44,800 字节上限）
均有不变量测试锁死；类别保真（synthesis_request_shape_invalid）纵深防御就位。
待 honest-degraded-delivery 的 003 复跑一并做终验后归档。