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

待定。修复 = model 前阶段整体包 try/except ValueError → typed exhausted
（`_exhausted_update` + `NodeProblem(code=OUTPUT_STRUCTURED_INVALID,
validation_category=<具体类别>)`），与 BUG-041 的 journal/demo 渲染衔接；
run 以 research.blocked + 诊断收尾而非崩溃。需 OpenSpec change
（`wave2-synthesis-node` 契约：节点任何输入条件失败必须 bounded，不得
crash 图）。修复后 003 即使 coverage 失败也有诊断可查、可重试。
