## 1. 信封对齐（readiness / final_delivery，BUG-047）

- [x] 1.1 确认 `runtime/research.py` readiness 策略 `total_token_budget=16_384`、
      final_delivery `total_token_budget=24_576`，其余字段（calls/output cap/wall
      time/tools）零变化；docstring 注明与构建器投影上限的推导关系（BUG-047）
- [x] 1.2 确认 `tests/unit/test_research_runtime_capabilities.py` 的
      `test_evidence_embedding_requests_stay_within_admission_envelope`：以
      builder-maximal 证据（各 `MAX_*_EVIDENCE_BYTES` 满额 + plan 投影）构建请求，
      断言 payload + system prompt（`load_policy_prompt()` 实测字节）+
      per_call_output_token_cap ≤ total_token_budget（readiness 与 final_delivery
      两侧）

## 2. wave2 有界投影（BUG-049）

- [x] 2.1 确认 `graph/nodes/wave2_synthesis/prompts.py`：synthesis 与 repair
      builder 均走确定性拟合投影——共享字节预算 32,768 起步，objective 超
      16,384 字符或 44,800 UTF-8 字节则预算 ×¾（下限 1,024）重投；截断条目
      `truncated=true`；不可拟合抛 `ValueError("synthesis_evidence_projection_overflow")`
- [x] 2.2 确认 `tests/graph/test_wave2_synthesis_real.py` 的
      `test_synthesis_prompts_bound_evidence_projection_within_request_limits`：
      4 条 20k 字符 CJK+ASCII 混合证据下，synthesis 与 repair 两个请求的
      objective 同时满足字符与字节双上限

## 3. pre-model 类别保真（BUG-048 第 5 项，纵深防御）

- [x] 3.1 测试先行：`tests/graph/test_wave2_synthesis_real.py` 新增单测——直接以
      pydantic `ValidationError`（模拟未来 builder 新增字段约束触发）驱动
      `_pre_model_problem`，断言归一类别为 `synthesis_request_shape_invalid`
      （pattern-safe），且 `!= "candidate_invalid"`；再以
      `synthesis_evidence_projection_overflow`（拟合下限仍超限的闭式消息）驱动，
      断言类别原样保留
- [x] 3.2 实现：`wave2_synthesis/node.py` 的 `_pre_model_problem` 对非闭式消息的
      ValueError/pydantic ValidationError 归一为
      `synthesis_request_shape_invalid`；闭式 raise 消息保留原类别；ruff + 新用例绿。
      注：拟合投影（任务 2.1）落地后 objective 溢出已走 typed 闭式消息，本任务为
      纵深防御，防未来 builder 演进重新引入类别失真

## 4. 回归与验证

- [x] 4.1 全量测试：`UV_NO_CACHE=1 .venv/bin/python -m pytest tests/unit
      tests/graph tests/contract` 全绿；`.venv/bin/python -m ruff check src tests`
      通过
- [x] 4.2 `openspec validate fix-request-envelope-coherence --strict` 通过
- [x] 4.3 更新 BUG-047/049 卡片（修复关联指向本 change）；真实 003 复跑验证随
      honest-degraded-delivery change 的验证 run 一并执行（本 change 单独复跑
      只能验证到 final_delivery 前不再算术暴毙）
