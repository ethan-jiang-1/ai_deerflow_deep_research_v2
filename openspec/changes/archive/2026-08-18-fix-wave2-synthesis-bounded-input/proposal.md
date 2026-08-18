## Why

真实 003 验证 run（BUG-046）在 wave2 补证循环首次成功提交证据后崩溃：
`wave2_synthesis` 节点的**模型前阶段**（topic/refs/open-question coverage
检查/证据读取/prompt 构建）对数据条件错误零防护——coverage 检查
（`node.py:213`）对投影与记录不一致时抛裸 `ValueError`，未被捕获 → 节点
wrapper 记 `internal.unexpected` 后 re-raise → 整个图崩溃 →
`bundle.unavailable`，无 report、无 typed incident、不可重试。模型后阶段
（BUG-040/041）已有完整 typed 处理，模型前阶段缺失同样的有界失败承诺。

## What Changes

- `wave2_synthesis/node.py` 的模型前阶段（registry/refs/read_wave1_open_
  questions/coverage/read_synthesis_evidence/build_synthesis_prompt）整体包
  try/except ValueError → typed exhausted（`_exhausted_update` +
  `NodeProblem`），`validation_category` 携带具体类别
  （`synthesis_question_coverage_invalid`、`synthesis_accepted_record_missing`、
  `wave1_open_question_read_invalid`、`wave1_open_question_projection_invalid`
  等，经既有 `_synthesis_validation_category` 提取），journal/demo 沿用
  BUG-041 的渲染。
- 非 ValueError 异常（含 CancelledError）不吞；模型调用路径逻辑不变。
- run 以 `research.blocked`（带诊断）收尾而非崩溃；可诊断、可重试。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `wave2-synthesis-node`: WSN-001 增补——模型前输入条件失败（coverage 不一致、
  记录缺失/不可读、投影非法）SHALL 以 typed incident 有界终止，绝不作为未捕获
  异常逃逸。

## Impact

- 代码：`graph/nodes/wave2_synthesis/node.py`（model 前阶段 + typed 出口）；
  无 engine/domain/gate 改动。
- 测试：`tests/graph/test_wave2_synthesis_real.py` 新增——uncovered open
  question id → `route=exhausted`、`terminal_status=blocked`、incident 带
  `validation_category=synthesis_question_coverage_invalid`、不抛异常。
- 行为：真实 003 即使触发 coverage/读取不一致，run 也有诊断地 blocked
  （而非 bundle.unavailable 静默死亡），可按诊断重试。
