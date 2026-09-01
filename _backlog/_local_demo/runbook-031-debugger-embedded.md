# Runbook 031 — 调试工作台（embedded 真实图，逐边界 step + Node Context）

> 前置：同 003 的 `.env` 三变量（`DEEPSEEK_API_KEY`、`TAVILY_API_KEY`、`DEERFLOW_DEMO_MODEL`）+ `make install` + 网络
> 入口：`./run/tui-workflow-debugger.sh --embedded`
> 本质：与 030 相同的 DebugRunDriver 逐边界推进，但跑在**真实模型和网页工具**上。wave0 等 LLM-bearing node 会捕获 Node Context Snapshot（initial prompt、runtime MD、enforced tools/budget、mount roots）。

## 1. 启动

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh --embedded
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
