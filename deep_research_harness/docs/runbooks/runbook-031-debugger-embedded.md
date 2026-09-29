# Runbook 031 — 调试工作台（embedded 真实图，逐边界 step + Node Context）

> **状态（2026-09-27）：已落地。** 调试驱动是组合无关的：`--embedded-smoke` 现在起的是
> **全真实图（ALL_REAL）上的调试工作台**——launcher 会为该组合注入 `--debug`，driver 以
> `ImplementationMode.ALL_REAL` 建 bundle，step/continue、`/context`、`/files`、`/attach`、
> `/replay` 与 fixture 路线完全一致；`/context` 此时能看到 LLM-bearing node 的捕获上下文，
> 且可用 `/context <node>#<n>` **下钻**到某一次调用：initial system policy / human message、
> base policy 与 capability 分层的内容摘录与哈希、enforced tools（requested→enforced）与
> budget、output schema、virtual roots 与 mounts、activity 与 coverage strip。
>
> 前置：同 003 的 `.env` 三变量（`DEEPSEEK_API_KEY`、`TAVILY_API_KEY`、
> `DEERFLOW_DEMO_MODEL`）+ `make install` + 网络——真实节点真的要调模型与网页工具。
> **诚实边界**：本路线的*接线*（组合、实现模式、入口旗标）已由无头测试与 harness 断言
> 锁住；真实模型下的逐边界实跑需要凭证与网络窗口，我无法在无头环境验证，需在你的真机
> 或一次 live 窗口确认。
>
> 入口：`./run/tui-workflow-debugger.sh --embedded-smoke`（等价：
> `DEBUGGER_COMPOSITION=embedded-smoke ./run/tui-workflow-debugger.sh`）。
> 本质：与 030 相同的 DebugRunDriver 逐边界推进，但跑在**真实模型和网页工具**上。wave0 等 LLM-bearing node 会捕获 Node Context Snapshot（initial prompt、runtime MD、enforced tools/budget、mount roots）。

## 1. 启动

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh --embedded-smoke
```

TUI 打开后 preflight 检查 `.env` 三变量和网络。失败会在创建 Bundle 前明确报错。

## 2. 提交问题（Start Step）

在 composer 输入研究问题，按 Enter。debug session 开启，bootstrap 提交。

## 3. Step 到 HITL1 → 回答

与 030 相同：Enter advance → hitl1 interrupt → composer 输入回答 → Enter resume。

2026-09-29（RED-015）起，HITL 停点是**类型化对话卡片**而非原始 JSON：
- `→ 等待 hitl1 输入（text）` 下是 goal（配置提案摘要）、proposed_scope（各维度取值）、
  缺少字段、剩余可接受轮次——不再是 `{"accepted_rounds_remaining":…}` 机器载荷；
- 你上一条回答被消费但未被接受时，明示 `↩ 回答已消费 · 未被接受 · 剩余 N 轮`
  和 `hitl1 回复: <节点对你说的原话>`（含建议输入短语，如「确认」「深度: 快速概览」）；
- 卡片与 `/help` 明示最快通关输入：`确认` / `confirm`；修订单项：`字段: 值`；
- 提交后 composer 清空——重复 Enter 不会再把同一段文字当第二条答案消费（BUG-078）。

## 4. 逐步穿过 LLM-bearing nodes

Enter advance 到 wave0。wave0 会调用真实模型和 Tavily 搜索，可能耗时较长。

wave0 完成后，输入 `/context` 查看 Node Context：

预期：
- 至少一条 bridge/node-agent invocation 记录
- `INITIAL CAPTURED` — exact initial system/human message
- `RUNTIME ENFORCED` — enforced tool names、budget、mount roots
- `ACTIVITY BOUNDED` — model_calls/tool_calls 计数
- raw provider message histories 标 `NOT RETAINED`

## 5. 到 terminal / Detach

继续推进到 terminal，或随时 `/detach` 干净退出。detach 后可用 `--attach <bundle_id>` 恢复。
terminal 姿态下直接输入新问题 = 结束当前会话并开新跑（2026-09-29 起兑现文档承诺）。

## 5b. 重跑节点与 auto-hitl（LDD-007/008，RED-016）

- **`/rerun`**：重跑刚提交的节点（重抽该节点结果），落到下一个停点（新提案或终态）。
  embedded 组合下**真实模型调用再次计费**——命令前有黄色成本提示。
- **`/run` 默认 auto-hitl**：连续推进撞上 hitl1 提案确认时，以操作者策略自动代答
  「确认」继续跑（日志明示 `⚙ drive 策略代答: 确认 ×N（auto-hitl · 操作者策略）`）。
  **`/run --no-auto-hitl`** 关闭代答；单步 Enter 永不代答；HITL2 方向决策永远停下等
  人；同一提案连续 2 次代答未被接受即停回人工并渲染节点回复。
- 经典 debugger 概念对照：断点=`/pause`+停点、单步=Enter、继续=`/run`、跑到指定节点
  =`/run <节点>`、观察窗=`/context` `/files` `/inspect`、回放=`/replay`、重执行帧=
  `/rerun`、断点处对话=HITL 卡片 + `?` 侧聊。

## 6. 与 030 的区别

| 维度 | 030 fixture | 031 embedded |
|------|------------|--------------|
| 模型 | 无（deterministic） | 真实 LLM + Tavily |
| 耗时 | 秒级 | 分钟级（wave0 可达数分钟） |
| Node Context | `/context` 显示空属预期 | 有真实 captured snapshot |
| 凭证 | 零 | `.env` 三变量 + 网络 |
| 费用 | 免费 | 消耗 API 额度 |

## 7. Live 验证清单（只有操作者能做：凭证 + 网络窗口）

无头门禁已锁住接线与渲染（`make tui-journey`、`make debugger-proof`、
`UV_OFFLINE=1 make verify` 全绿），以下是**必须在真机 live 窗口确认**的项，
过了之后本 runbook 顶部的诚实边界注记应更新：

1. **Start Step 到 hitl1 卡片**：真实问题（例：`Compare renewable energy storage
   technologies`）+ Enter → 停点应显示 goal/proposed_scope/剩余轮次，无原始 JSON。
2. **对话往返**：故意输入一句闲聊（如 `你都能干什么`）→ 应看到
   `↩ 回答已消费 · 未被接受 · 剩余 N 轮` + `hitl1 回复: …`（节点会解释并给建议短语）；
   再输入 `确认`（或 `confirm`）→ hitl1 接受、flow 进入 topic_planning。
3. **wave0 真跑**：`/run`（或逐步 Enter）到 wave0，分钟级等待后 `/context` 应有
   真实捕获（exact prompt / enforced tools / budget / mounts）。
4. **`/files`、`/targets`、`/inspect`** 在真实 bundle 上的表现；推进到 terminal 后
   `/detach` → `--attach <id>` 恢复。
5. **卡住会话的恢复**：上次 live 遗留的 paused bundle 可 `--attach b_EHlhgNio-gZLv82ZpzTd9MvGzlPca4if8__w-AvDfHI`
   接回，直接输 `确认` 让它继续（RED-015 后你能看清它还在问什么）；不需要就 `/cancel`。

观察到的任何缺陷：截图/复制日志窗（Copy details）+ bundle id，现场立卡。
