# Policy Gate Injection Layer — 配套审查证据

> 主计划：[`../policy-gate-injection-layer.md`](../policy-gate-injection-layer.md)
> 状态：详细依据；不定义 runtime 行为，也不替代 OpenSpec proposal / spec / tasks。

主计划是当前进度、下一步和 contract 的唯一追踪页。这里保存较长的原案、审查、外部借鉴和
probe 证据，使首页不必混入“为什么这样判断”的完整论证。

## 阅读顺序

1. 先读主计划的“进度与下一步”，确认当前 change 与下一个关口。
2. 需要完整复核原始主张、逐项 disposition 和建议演变时读
   [`00-program-architecture-review.md`](00-program-architecture-review.md)。
3. 需要复核“这个问题不是无中生有”时读
   [`01-bug-boundary-evidence.md`](01-bug-boundary-evidence.md)。
4. 需要复核“跨 session guardrail 为什么不是再造一个 checker”时读
   [`02-session-drift-borrowing.md`](02-session-drift-borrowing.md)。
5. 需要复核“OpenSpec 1.7 的两个 operation 时机怎样和 tasks/guardrails 组成反馈环”时读
   [`03-openspec-1.7-operation-guidance.md`](03-openspec-1.7-operation-guidance.md)。
6. 需要确认三个 change 的分期和已收敛的 Change 3 contract 时读
   [`04-three-change-system-program.md`](04-three-change-system-program.md)。

## 证据纪律

- Bug 卡、Git commit、已接受 spec 和当前可执行 contract 是不同等级的证据；每份文档都标明
  它能证明和不能证明什么。
- 反复出现的案例可以支持**架构诊断**，不能自动变成“全部 regression 的统计比例”或
  “所有逻辑都应移动到 prompt”的结论。
- 任何新的发现必须回到 change 的正常 `tasks.md`；聊天总结、本文档或单次模型判断都不是
  runtime authority，也不是 archive proof。

## 文档

| 文件 | 回答的问题 |
| --- | --- |
| [`00-program-architecture-review.md`](00-program-architecture-review.md) | 原案快照、审查台账和经审查的架构建议；当前状态以主计划为准 |
| [`01-bug-boundary-evidence.md`](01-bug-boundary-evidence.md) | BUG-001～016 为什么支持“先问边界/authority，再叠加实现”的判断，以及它的反例和适用边界 |
| [`02-session-drift-borrowing.md`](02-session-drift-borrowing.md) | 对 `ai_tool_deepresearch` 的 session-drift feedback loop 做了什么选择性借鉴、哪些机制不迁移、未来 guardrail 的本地验证条件 |
| [`03-openspec-1.7-operation-guidance.md`](03-openspec-1.7-operation-guidance.md) | OpenSpec 1.7.0 的 `operations.apply/archive.guidance` 各自解决什么时机、如何与 `rules.tasks` 和未来 guardrail 配合，以及 advisory 的真实边界 |
| [`04-three-change-system-program.md`](04-three-change-system-program.md) | 已确认的三项连续 change 系统目标、分期 authority 边界和 Change 3 proposal contract |
| [`05-operation-guidance-probe-evidence.md`](05-operation-guidance-probe-evidence.md) | Change 2 的六项 local probe、archive side effects、`missing-boundary` 与 `unclosed` replay 事实 |
