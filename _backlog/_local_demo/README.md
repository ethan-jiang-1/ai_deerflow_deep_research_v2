# 本地跑法（从简单到难）

> **001~004 是同一个端到端 Deep Research 流程的四种跑法**，不是四个分开的功能模块。
> 都是从图的第一个节点一路跑到最后一个节点；区别只在于：是否用真实模型/网页工具、是否要人介入、环境前置有多少。
>
> 原则：先跑 001，能过再 002，再 003，最后 004。一步一步来，每一步都能暴露不同层面的 bug。
>
> **所有操作都写在 runbook 里，不单独放 `.sh` 脚本。**

| 编号 | 手册 | 花不花钱 | 需要什么 | 这个例子是什么意思 | 默认示例问题 |
| --- | --- | --- | --- | --- | --- |
| 001 | [`runbook-001-最简单-fixture图端到端.md`](runbook-001-最简单-fixture图端到端.md) | 免费 | 无 | 最简单：只用假数据把图从第一节点跑到最后节点，验证“路通不通” | `What is the capital of France?` |
| 002 | `runbook-002-稍难-scripted真实链路.md`（待建） | 免费 | 无 | 稍难：用脚本化的真实控制链路跑一遍，验证“真适配器+门+持久化通不通” | 固定为 `What is one bounded fact about grid energy storage?` |
| 003 | `runbook-003-更难-真机全自动.md`（待建） | 花 API | 本地模型/Tavily 凭据 | 更难：接真实模型和网页工具，全自动跑完，不等人 | `Compare China and US EV battery market in 2024.` |
| 004 | `runbook-004-最难-真机交互找茬.md`（待建） | 花 API | 先起 Gateway + 人 | 最难：真机交互跑，HITL 环节要人参与，专门用来找茬 | `Compare China and US EV battery market in 2024.` |

> 📐 手册命名规则固定为 `runbook-00X-难度-用途.md`，以后按这个补。

## 每天固定怎么跑

1. 打开 [`runbook-001-最简单-fixture图端到端.md`](runbook-001-最简单-fixture图端到端.md)
2. 按里面的顺序执行：
   - 跑 001
   - 认 bundle
   - 看节点日志
   - 看每个环节内容
   - 验收最终结果

如果 001 都跑不过，先别碰 002/003/004，把 001 的问题修好。

## 前置

- 001 / 002：零前置，不联网、不花 API。
- 003：需要本地有真实模型/Tavily 凭据（不需要 Gateway）。
- 004：需要先启动本地 Gateway：

```bash
cd deep_research_harness
make profile-dev PROFILE=demo
```

## 避坑

所有命令都带 `UV_NO_CACHE=1`，用来绕过 uv 全局缓存权限/沙箱导致的
`Operation not permitted` 问题，避免一上来就被环境卡住。
