# BUG-019: 未指定两条比较路线的研究仍可被确认并启动

> 严重级别: P1 | 发现: 2026-08-02 | 状态: 活跃

## 症状

用户提出“比较两种储能路线的成本、风险与适用场景”，但没有给出两条路线名称。HITL1
生成的保存 profile 明确写着“用户必须提供具体路线；否则仅以常见路线作为 placeholder”，
同时把 “What are the two energy storage routes being compared?” 放入 `must_answer`。

界面却只提供“Start with the current proposal”。用户输入“可以，我觉得你说的挺好”后，
profile 被接受，系统进入 topic planning，迫使 planner 在用户从未授权的路线之间猜测。

## 根因

`ResearchProfile` 的完整性只要求通用的深度、受众、格式、成本、时间和非空
`must_answer`。它没有 `comparison_subjects`、`route_pair` 或等价的 typed decision。
因此“尚待用户决定哪两条路线”被编码为自由文本 `custom_notes` 和一个问题，
`missing_dimensions()` 仍判定 profile 完整，HITL1 允许 `accept_suggestion`。

## 影响

- 用户的“确认”被误解释为对未展示默认路线的授权。
- 后续 topic plan、检索和结论可能比较错误对象，即使执行技术上成功也不满足请求。
- 关键决策隐藏在模型生成的提示文本中，用户必须猜测该补充什么，形成反复确认和修正。

## 复现

1. 运行 real demo，并输入“比较两种储能路线的成本、风险与适用场景”。
2. 在 proposal 中不指定路线，选择“Start with the current proposal”或输入自然确认语。
3. 观察 profile 被接受且进入 `topic_planning`，没有一个明确的两路线选择或补充输入。

确定性回归测试应构造一个包含“尚未指定比较对象”信息的 advisory brief；断言 proposal
不能出现接受动作，必须先发出专门的 comparison-subject decision。明确选择默认路线时，
该选择必须作为 typed profile/state 数据被保留。

## 修复关联

尚未创建 OpenSpec change。应建立一个 HITL/profile domain change：为比较型研究引入
显式的比较对象决策和完整性门槛；未选对象时显示可理解的补充问题或显式默认组合，
而不是允许泛化的“开始研究”。
