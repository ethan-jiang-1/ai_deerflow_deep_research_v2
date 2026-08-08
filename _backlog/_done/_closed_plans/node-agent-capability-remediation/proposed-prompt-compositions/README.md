# 拟议最终 Prompt 组合

> 状态：设计原文草案，待逐 node 审定；不是当前运行时 prompt，也不授权代码实现。
> 更新：2026-07-27
> 上游：[目标能力映射](../target-capability-map.md)

## 为什么这里要写出完整形状

过去的问题正是“代码里有很多 Objective 字符串，但没有人能说清最终 agent 到底收到
什么”。因此这里不只列 capability 名称，而是把每一个 branch 的运行时消息分为可检查
的三个部分：

```text
Final system prompt
  = shared-base-safety.md（逐字共享）
  + 本 node 文件中的 capability policy（逐字独有）

Final human message
  = trusted assignment（本次已验证任务）
  + output contract（本次结构化结果）
  + zero or more <untrusted-source-data> blocks（外部内容）
```

没有隐藏的第四段 generic role prompt。运行时实际可用的模型、工具名、预算、路径和
identity 不写进这些 prompt；它们由 bridge/middleware 注入并强制执行。

## 文件

| Node | 拟议组合原文 |
| --- | --- |
| 所有 branch | [shared-base-safety.md](shared-base-safety.md) |
| `hitl1` | [hitl1.md](hitl1.md) |
| `topic_planning` | [topic-planning.md](topic-planning.md) |
| `wave0` | [wave0.md](wave0.md) |
| `wave1` | [wave1.md](wave1.md) |
| `wave2_synthesis` | [wave2-synthesis.md](wave2-synthesis.md) |
| `targeted_evidence` | [targeted-evidence.md](targeted-evidence.md) |

## 如何审阅每一页

对每一个 branch，请先判断四件事：

1. 这真的是该 node 应承担的认知工作吗？若不是，应改 capability，不是先调措辞。
2. 它是否拿到了不该有的工具或 authority？工具是 runtime 权限，policy 只表达必须/禁止。
3. 所有外部数据是否都被当作数据，而不是指令？
4. 这个输出契约是否足以让后续 deterministic node 验证，而不是让模型代替 graph 决定 route/state？

页面中的 `PROMPT_FIXTURE` 是建议未来 catalog 和 scripted tests 使用的合成数据标记，
绝不应变成真实用户、来源或 provider 数据。
