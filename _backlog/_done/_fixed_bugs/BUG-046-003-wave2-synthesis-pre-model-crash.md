# BUG-046: wave2_synthesis model 前阶段裸 ValueError 崩溃整个 run（internal.unexpected → bundle.unavailable）

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 活跃

## 症状

真实 003 验证 run（BUG-044/045 修复后）在 wave2 补证循环首次**成功提交证据**
后崩溃：`node | wave2_synthesis | failed | internal.unexpected |
worker_failure_category=unknown`（attempt a2，11:39:42，无 model_tool 事件 =
崩溃在模型调用**之前**）→ 图死亡 → demo_real 返回 `bundle.unavailable`、
无 report、无 typed incident、`可重试: 否`——整个 run 被毁，连诊断都没有。

代码级复现（同一签名）：`wave2_synthesis/node.py:213` 的 model 前 coverage
检查 `raise ValueError("synthesis_question_coverage_invalid")` 未捕获 →
节点 wrapper（`graph/builder.py` observed_run）记录 internal.unexpected 后
re-raise → 图崩溃。复现脚本：state 带 uncovered 的 wave1 open question id →
同签名崩溃。

## 根因

`wave2_synthesis/node.py` 的 `run()` 分两段：
- **model 后**（parse/validate/repair）：有完整 typed 处理（BUG-040/041/043：
  `SynthesisValidationFailure` → repair → 最终 typed exhausted，journal 渲染
  `validation_category`）；
- **model 前**（topic_registry/refs/`read_wave1_open_questions`/coverage 检查/
  `read_synthesis_evidence`/`build_synthesis_prompt`）：**零防护**——任何
  ValueError（`synthesis_question_coverage_invalid`、
  `synthesis_accepted_record_missing`、`wave1_open_question_read_invalid`、
  `wave1_open_question_projection_invalid`）直接冒泡 → 图崩溃。

触发条件（数据相关）：wave1_open_questions 投影（gate review 的模型输出）与
accepted wave1 记录的 open_questions 文本（worker 的模型输出）是**两次独立
模型调用**，id 可能不一致；wave1 repair 轮（w0001）加剧漂移。本次 run 命中
coverage 失败；此前 run 未命中（模型波动）。BUG-044/045 修复后补证能提交、
run 能走到 wave2 第二访，此雷才暴露。

## 复现

1. 代码级：`wave2_synthesis/node.py:212-213`——state 的
   `wave1_open_questions` 含记录中不存在的 question id →
   `ValueError("synthesis_question_coverage_invalid")` 未捕获。
2. 运行级：003 真实 run 在 wave2 第二访崩溃（模型 id 漂移时偶发），
   events.jsonl 末条 `node wave2_synthesis failed internal.unexpected`。

## 修复关联

✅ 已修复（2026-08-18，代码已落地）：OpenSpec change
`openspec/changes/fix-wave2-synthesis-bounded-input/`（`wave2-synthesis-node`
WSN-001 delta，propose → polish → apply）。

修复 = `wave2_synthesis/node.py` 的 model 前输入推导段（topic_registry →
build_synthesis_prompt）整体包 `try/except ValueError` →
`_pre_model_problem(error)` → typed exhausted（`_exhausted_update` +
`NodeProblem(code=OUTPUT_STRUCTURED_INVALID, validation_category=...)`）：
- `validation_category` 取 raise 点闭式消息串（`synthesis_question_coverage_
  invalid` 等，pattern 校验通过则直接用；`wave1_*` 首段含数字的加
  `input.` 前缀使其满足 NodeProblem pattern；其余回退泛化桶）；
- 不吞 CancelledError/非 ValueError；模型调用路径逻辑不变；
- run 以 `research.blocked`（带具体类别诊断）收尾，不再
  `bundle.unavailable` 静默死亡。

验证：`tests/graph/test_wave2_synthesis_real.py` 新增 2 用例（uncovered
question id → exhausted + `synthesis_question_coverage_invalid`；非法投影 →
`input.wave1_open_question_projection_invalid`）+ 更新既有
`test_real_synthesis_fails_closed_when_projected_text_is_unresolvable`（旧断言
即崩溃行为）；全量 `make verify` 通过、ruff 干净、`openspec validate
--strict` 通过。真实 003 验证 run 待跑（三个修复齐后验证）。
