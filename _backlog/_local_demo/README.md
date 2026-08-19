# 本地跑法（从简单到难）

> **001~004 是同一个端到端 Deep Research 流程的四种跑法**，不是四个分开的功能模块。
> 都是从图的第一个节点一路跑到最后一个节点；区别只在于：是否用真实模型/网页工具、是否要人介入、环境前置有多少。
>
> **Control Environment 原则：所有 001~004 都使用固定研究问题，不开放自定义问题。**
> 固定问题 = 受控环境，跑出来的结果可对照、可复现，找 bug 容易很多。难度从 001 到 004 递增。
>
> **自动化原则：因为问题固定，HITL1/HITL2 的答案也是确定的，系统自动回答，不需要人工输入。**
> **001~004 全部走全自动。** 真机交互/人工 HITL 专项留给未来的 010 等 runbook，不在 001~004 内。
>
> 原则：先跑 001，能过再 002，再 003，最后 004。一步一步来，每一步都能暴露不同层面的 bug。
>
> **所有操作都写在 runbook 里，不单独放 `.sh` 脚本。**

| 编号 | 手册 | 花费 | 需要什么 | 这个例子是什么意思 | 固定问题 |
| --- | --- | --- | --- | --- | --- |
| 001 | [`runbook-001-easiest-fixture-graph.md`](runbook-001-easiest-fixture-graph.md) | 花（少） | 无 | 最简单：只用假数据把图从第一节点跑到最后节点，验证“路通不通” | `What is the capital of France?` |
| 002 | [`runbook-002-easy-scripted-real.md`](runbook-002-easy-scripted-real.md) | 花（少） | 无 | 稍难：用脚本化的真实控制链路跑一遍，验证“真适配器+门+持久化通不通”，且会产出 Markdown report | `What is one bounded fact about grid energy storage?` |
| 003 | [`runbook-003-medium-real-auto.md`](runbook-003-medium-real-auto.md) | 花（中） | `.env` 三个变量（`DEEPSEEK_API_KEY`、`TAVILY_API_KEY`、`DEERFLOW_DEMO_MODEL`）+ 网络 | 更难：接真实模型和网页工具，全自动跑完，不等人（声明 minimal 意图 → 单 topic / 每 wave 1 work unit） | `What is one bounded fact about China's EV battery market in 2024?` |
| 004 | [`runbook-004-hard-real-auto.md`](runbook-004-hard-real-auto.md) | 花（多） | 同 003 的 `.env` 三变量 + 网络 | 最难：真机全自动跑**默认意图**（不声明 minimal），固定比较题压多 topic 链路，专门用来找茬 | `Compare China and US EV battery market in 2024.` |
| 010 | [`runbook-010-tui-interactive.md`](runbook-010-tui-interactive.md) | 花（中） | 同 003 的 `.env` 两变量（DEEPSEEK/TAVILY）+ demo-tui extra + 网络 + **真人坐镇** | 换轴：**真人交互**——TUI 里做 hitl1/hitl2 决策（semantic intake 真模型分类你的回答），压 001-004 从未触达的交互认知面 | `What is one bounded fact about China's EV battery market in 2024?` |

> 📐 手册命名规则固定为 `runbook-00X-难度-用途.md`，以后按这个补。

## 每天固定怎么跑

1. 打开 [`runbook-001-easiest-fixture-graph.md`](runbook-001-easiest-fixture-graph.md)
2. 按里面的顺序执行：
   - 跑 001
   - 认 bundle
   - 看节点日志
   - 看每个环节内容
   - 验收最终结果

如果 001 都跑不过，先别碰 002/003/004，把 001 的问题修好。

## 前置

- 001 / 002：零前置，不联网，花费少。
- 003：需要本地有真实模型/Tavily 凭据（不需要 Gateway）。
- 004：同 003 的凭据前置（`.env` 三变量 + 网络）。入口已定为 embedded
  smoke（`soft-bundle run <root> --mode 004`，显式 `--profile-intent none`
  走默认产品路径）；Gateway 非交互自动化是独立产品关切，不在 001~004 内：

```bash
cd deep_research_harness
make profile-dev PROFILE=demo
```

## 避坑

所有命令都带 `UV_NO_CACHE=1`，用来绕过 uv 全局缓存权限/沙箱导致的
`Operation not permitted` 问题，避免一上来就被环境卡住。
