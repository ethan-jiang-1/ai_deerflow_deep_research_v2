## 1. BUG-051：open-question id 冲突显式化（最小、先行）

- [x] 1.1 测试先行：`tests/unit/test_work_unit_store*.py`（或就近 store 测试）
      新增——两个 accepted wave1 记录含同 `q:w1_q1` 不同文本 →
      `read_wave1_open_questions` 抛 `ValueError("wave1_open_question_id_collision")`；
      同 id 同文本 → 单条目返回
- [x] 1.2 实现：`work_unit_store.read_wave1_open_questions` 在 `entries` 上做
      冲突检测（同 id 不同文本 raise；同 id 同文本去重），保持排序语义
- [x] 1.3 graph 测试：wave2_synthesis 节点遇冲突 state → pre-model 有界终止，
      incident `validation_category == "wave1_open_question_id_collision"`

## 2. BUG-054（Decision A）：finding 派生可写结论

- [x] 2.1 `work_unit_store` 新增 `read_synthesis_findings()`（镜像
      `read_synthesis_gaps`：bounded contained read，返回 `SynthesisResult.findings`）
      + 单测
- [x] 2.2 测试先行：`tests/unit`（materializer 就近）——高置信+引用完备+
      `search_required=false` 的 finding → plan 含其 conclusion（statement
      verbatim、refs 截 16）；低置信/空 refs/越界 ref/`search_required=true`
      的 finding → 不产生结论；critic insufficient 判定**不删除** finding 结论、
      照常产生 uncertainty
- [x] 2.3 实现：`materialize_report_plan` 增 `findings` 与 `accepted_refs`
      参数按 D1 规则映射；`readiness/node.py` 读 findings 并传入（读失败按
      `readiness_hard_failures` 既有模式处理，不静默）
- [x] 2.4 回归：既有 materializer/readiness 测试全绿（question 派生结论、gap
      不确定项、provenance 投影零变化）

## 3. BUG-053：退化 plan 确定性渲染

- [x] 3.1 测试先行：`tests/graph/test_final_delivery_real*.py`（就近）——
      0 结论+1 不确定项 与 1+0 两类退化 plan → 节点**零 composer 调用**
      （capabilities spy 断言）→ admission/renderer/publisher 正常产出两个
      终稿工件，内容与 composer 路径等价
- [x] 3.2 实现：`final_delivery/node.py` 退化分支（两类条目均 ≤1）直接构造
      `FinalDeliveryLayoutCandidate`（plan 顺序 entry ids），走同一
      admit/render/publish 管线；非退化路径零变化
- [x] 3.3 回归：既有 final_delivery 测试全绿（非退化 plan 仍走 composer、
      拒绝路径不变）

## 4. BUG-050（Decision B）：wave2 预算类失败交还 gate

- [x] 4.1 `domain/state.py`：新字段 `wave2_budget_exhausted: bool = False` +
      FieldOwnership 注册（wave2_synthesis writer、GATE reader 合法）；
      ownership 契约测试更新
- [x] 4.2 测试先行：graph 测试——wave2 invocation 以 budget-class
      `NodeProblem` 失败（伪造 capabilities 返回 admission/预算拒绝）→ 节点
      返回**非终止**更新（无 terminal_status/terminal_reason）+ 信号置位；
      非 budget 失败（provider/candidate）仍走既有 terminal/disposition 路径
- [x] 4.3 实现：`wave2_synthesis/node.py` `_exhausted_update` 预算类分支
      （判定：`NodeFinishReason.BUDGET_EXHAUSTED` 或 problem code 属预算/admission
      拒绝闭集）→ 写信号 + 非终止 `node_state_update`；节点在**每次进入时先
      复位** `wave2_budget_exhausted=False`（任何非预算类结局——成功/其他失败
      ——都不留下旧信号，防 gate 规则投影过期失败导致无限修复）
- [x] 4.4 `engine/real_gates.py`：wave2 gate def 注册规则——
      `wave2_budget_exhausted` 置位 → repairable Failure（评估后信号由节点在
      下次进入时复位）；gate 测试：预算递减→REPAIR→耗尽+marker 缺席→degraded
      pass（marker 追加）；marker 在场→blocked
- [x] 4.5 全链覆盖由三个 seam 测试组合承担：节点 hand-back 非终止
      （test_budget_exhausted_invocation_hands_route_authority_to_the_gate）、
      gate 机制（test_wave2_budget_handback_rides_the_gate_machinery_without_a_preview
      ：REPAIR→降级 pass→marker 封顶）、既有链路（disclosure 首测：降级 pass →
      readiness 披露 → 终稿渲染）：budget 失败 → gate 降级 pass → readiness/final
      delivery 继续到 completed（以 002 fake 链或 003 缩件驱动）

## 5. 回归、runbook 与真实 003 验证

- [x] 5.1 全量测试：`UV_NO_CACHE=1 .venv/bin/python -m pytest tests/unit
      tests/graph tests/contract` 全绿；ruff 通过
- [x] 5.2 `openspec validate honest-degraded-delivery --strict` 通过
- [x] 5.3 runbook-003 §5.1 按实现边界改写（D2/D3 语义、PASS 判据）
- [x] 5.4 更新 BUG-050/051/053/054 卡片（修复关联指向本 change）
- [x] 5.5 真实 003 复跑（runbook §7 重试纪律）至 `RESULT: PASS`，报告含真实
      结论 + claim-citation 映射 + Uncertainties 披露；失败 bundle 由
      `preserve-failed-run-bundles` 归档可查
