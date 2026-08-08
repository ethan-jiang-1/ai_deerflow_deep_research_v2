# BUG-001: HITL1 无法识别中文偏好，且没有明确确认步骤

> 严重级别: P1 | 发现: 2026-07-22 | 状态: 已修复

## 症状

真实 CLI 在研究范围确认页展示中文文案，但解析器只识别英文短语。用户输入“标准深度”后，系统没有告诉用户该值是否被接受，也没有显示已识别的字段；下一轮仍把 `depth, audience, format, cost_tolerance, time_budget` 全部列为缺失，并把目标退化为英文兜底文案 `Additional profile details are required before research can proceed.`。

现场 run：`r_SnrIKUGQhUwUIAWyht4dq_zJLGNftutorg24_bhX62E`。其 retained profile 最终为 degraded，所有偏好字段为空，说明输入没有进入 profile progress。

## 根因

`domain/profile.py` 的自由文本解析只维护英文 `_TEXT_SYNONYMS`；`hitl1/node.py` 又把任何解析错误或零字段结果静默降级成空 `PartialResearchProfile`。CLI 只是原样发送文字，既没有“接受全部建议”的显式动作，也没有在发送前/发送后投影出字段级解析结果。因此这是 Python 域契约与 CLI 展示层的组合问题，不是模型节点自己在解释用户输入。

## 复现

```bash
cd /Users/bowhead/ai_deerflow_deep_research/agent
uv run --extra operations python -c 'from deerflow_deep_research.domain.profile import parse_profile_response, missing_dimensions; p = parse_profile_response("标准深度"); print(p.model_dump(mode="json")); print(missing_dimensions(p))'
```

当前结果中 `depth` 为 `null`，并仍列为缺失。

## 修复关联

新建 focused OpenSpec change，范围应包括：中文/机器值/结构化输入的确定性解析、已识别字段和待补字段的回显、明确的“接受建议”操作，以及无法解析时不消耗一轮 HITL 的反馈。不得把自然语言解析权交给模型，也不得扩大到 `backend/` 或 `frontend/`。
