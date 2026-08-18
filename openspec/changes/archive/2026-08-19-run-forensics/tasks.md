## 1. 预算操作数（BUG-048.1）

- [x] 1.1 测试先行：`tests/unit/test_budget_middleware*.py`（就近）——
      token_admission/per_call_output_cap/total_token_budget 三类停止的
      `AgentBudgetError.operands` 键集与值为计算值
- [x] 1.2 实现：`agents/middleware.py` 在三个 raise 点装配 `operands`
      （闭集整数码：projected_request_bytes/total_token_budget/
      per_call_output_token_cap/observed_output_tokens/cumulative_tokens/cap）

## 2. model_tool 事件：操作数 + usage + 序号（BUG-048.4/6）

- [x] 2.1 测试先行：bridge 就近测试——同一 attempt 三次调用的事件序号
      1/2/3 且 started/completed 同序号；completed 带 usage_tokens（usage
      可得）；预算失败事件带 operands；无 usage 的 completed 不带
      usage_tokens 字段
- [x] 2.2 实现：`runtime/node_agent_bridge.py` `_record` 增 per-attempt
      序号（实例内计数器，started 分配/completed 复用）、usage_tokens
      透传（completed 且可得）、operands 并入（预算失败时）

## 3. 策略信封快照（BUG-048.2）

- [x] 3.1 测试先行：run_observation 就近测试——summary 含已执行 phase 的
      `{phase, policy_name, total_token_budget, per_call_output_token_cap,
      max_model_calls}`；未执行 phase 不出现
- [x] 3.2 实现：RunSummary 增 `policy_envelopes` 字段；demo 运行组装
      summary 处从装配策略对象采集（运行时值）

## 4. critic 兜底事件（BUG-048.3）

- [x] 4.1 测试先行：readiness 就近测试——invocation 失败与 candidate
      不合格两条路径各发一条 `readiness_critic_fallback`（reason 正确）、
      成功路径零事件；保守投影与 route 不变
- [x] 4.2 实现：`graph/nodes/readiness/node.py` 两个 except 块发节点级
      事件（事件失败吞掉，不改行为）

## 5. 回归与验证

- [x] 5.1 全量测试 + ruff 全绿
- [x] 5.2 `openspec validate run-forensics --strict` 通过
- [x] 5.3 更新 BUG-048 卡片（1/2/3/4/6 项修复关联；第 5 项并入
      fix-request-envelope-coherence；state.json 投影 follow-up 如实标注）
- [x] 5.4 下一次真实 003 run 的事件流抽查：admission/budget 事件带操作数、
      model_tool 带 usage+序号、summary 带信封、（若触发）兜底事件可见
