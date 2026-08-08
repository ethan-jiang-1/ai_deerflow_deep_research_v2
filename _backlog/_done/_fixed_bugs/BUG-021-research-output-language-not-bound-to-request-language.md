# BUG-021: 研究语言未绑定到用户请求语言

> 严重级别: P2 | 发现: 2026-08-02 | 状态: 活跃

## 症状

中文问题“比较两种储能路线的成本、风险与适用场景”得到中文 CLI 外壳，但 HITL1 的
保存 profile 写明“问题是中文但输出将为英文”，并生成英文 `must_answer` 与范围文本。
用户在确认范围时需要阅读与原始请求语言不一致的关键决策内容。

## 根因

`ResearchProfile` 和 topic-planning inputs 没有输出/交互语言字段；HITL1 brief prompt
也没有将请求语言作为持久化的用户意图。语言选择因此完全留给模型默认行为，后续节点
不能区分用户明确要求英文与模型自行切换到英文。

## 影响

- 用户难以核对 scope、比较对象和 `must_answer` 是否符合中文请求。
- 语言切换放大 BUG-019 的隐式范围问题，也增加自然确认被误解的风险。
- 最终报告语言无法作为可测试、可追踪的用户授权事实。

## 复现

运行：

```bash
cd deerflow_research
make demo-real DEMO_ARGS='--question "比较两种储能路线的成本、风险与适用场景"'
```

检查 HITL1 proposal 与 `request/profile.json`：交互壳为中文，但 scope/must-answer 和
output-language 说明为英文。

## 修复关联

尚未创建 OpenSpec change。应在 profile/HITL contract 中决定语言策略：默认继承请求语言，
或以显式可见选择覆盖；选择须进入 typed profile/state，并约束 proposal、topic plan 和
最终交付的语言。补充中文与英文请求的端到端校准测试。
