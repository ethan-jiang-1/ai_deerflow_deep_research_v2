# BUG-041: wave2 有界终态吞掉具体验证类别，诊断只剩笼统的 output.structured_invalid

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 已修复 ✅

## 症状

同 BUG-040 的 run：终态 incident、`run-summary.json`、journal records 里失败
类别都只有 `output.structured_invalid`。真实失败是
`synthesis_question_coverage_invalid`（语义覆盖错误）——与本轮"JSON 形状错误"
（首轮才是 parse 失败）是两类问题，但对外投影完全无法区分。要定位真实类别必须
解码 checkpoint messages 手工复算验证（本次排查即如此）。

## 根因

`graph/nodes/wave2_synthesis/node.py` 二次验证的 `except ValueError:` 分支构造
`NodeProblem(code=RunFailureCode.OUTPUT_STRUCTURED_INVALID)` 时丢弃了第二个
ValueError 携带的类别；首轮的 `validation_category` 有计算但只进了 repair
prompt，不进终态投影。与 BUG-036"journal 可用性如实投影"是同一精神的缺口：
**投影层字段与真实失败原因不同源**。

## 复现

同 BUG-040；对照 `run-summary.json` 的 `failure_category`（笼统）与 checkpoint
解码复算出的 `synthesis_question_coverage_invalid`（真实）。

## 修复关联

Change `wave2-synthesis-validation-feedback-contract`（WSN-001 行为变更）：
二次验证 `except ValueError:` 绑定错误变量，把具体语义类别传入 `NodeProblem`；
`NodeProblem`/`TerminalIncidentProjection`/`RunFailure` 增可选有界
`validation_category` 字段；`runtime/run_experience.py` 的 `_publish_observation`
投影 `failure_category = incident.validation_category or incident.code.value`
（journal/run-summary 显示 `synthesis_question_coverage_invalid`），
`_failure_for_terminal` 透传，`demo_real.py` 通用 `_failure_lines` 渲染验证类别行。
纯 parse 失败保留 `output.structured_invalid`。确定性测试：
`test_still_invalid_semantic_repair_projects_concrete_validation_category`、
`test_parse_terminal_keeps_generic_code_without_validation_category`（新增）。

