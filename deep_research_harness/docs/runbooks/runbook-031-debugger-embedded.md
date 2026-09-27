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

## 6. 与 030 的区别

| 维度 | 030 fixture | 031 embedded |
|------|------------|--------------|
| 模型 | 无（deterministic） | 真实 LLM + Tavily |
| 耗时 | 秒级 | 分钟级（wave0 可达数分钟） |
| Node Context | `/context` 显示空属预期 | 有真实 captured snapshot |
| 凭证 | 零 | `.env` 三变量 + 网络 |
| 费用 | 免费 | 消耗 API 额度 |
