# Runbook 030 — 调试工作台（节点边界 step/continue）

> 前置：`make install` 已跑（含 demo-tui extra）；零凭证、零网络。
> 入口：`./run/tui-workflow-debugger.sh --fixture`（或 `make tui-debugger DEBUGGER_ARGS="--fixture"`）
> 本质：用 `DebugRunDriver` 逐边界推进同一张 fixture StateGraph，实时看 timeline 和 Node Context。

## 1. 启动

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh --fixture
```

TUI 打开后看到 Ready 状态（fixture composition，无凭证要求）。

## 2. 提交问题（Start Step）

在 composer 输入一个研究问题（如 `Compare renewable energy storage technologies`），按 Enter。

预期：
- 日志区出现 `调试会话: b_XXXX… (Start Step)`
- 然后 `✓ bootstrap 提交（帧 1）`
- 面板显示 `姿态: paused_at_boundary · 下一节点: hitl1`

## 3. Step 到 HITL1

按 Enter（composer 留空或输入任意文本——paused 态下 Enter 就是 advance_one）。

预期：
- hitl1 开始执行并触发 interrupt
- 面板显示 `姿态: awaiting_hitl · 等待输入`
- hitl1 的 suspended 卡出现在 timeline

## 4. 回答 HITL1

在 composer 输入一个 profile 描述（如 `depth: standard` 或 `Use the default profile.`），按 Enter。

预期：
- hitl1 完成并提交
- 面板更新为下一边界

## 5. 逐步推进 / Continue

继续按 Enter 逐步穿过 `topic_planning → wave0 → wave1 → wave2 → hitl2 → readiness → final_delivery`。每次 Enter 提交恰好一个逻辑节点。

## 6. 查看 Node Context

输入 `/context` 并按 Enter。

预期：
- fixture 模式下，deterministic node（bootstrap、hitl1、topic_planning 等）没有 LLM 调用，所以 `/context` 显示 `尚无已捕获的调用上下文` 属预期
- embedded 模式下，LLM-bearing node（wave0 等）会有 captured context snapshot

## 7. 干净退出

输入 `/detach` 并按 Enter。

预期：
- `调试会话` 引用被清除
- Bundle 保留在原 boundary，不触发 cancel
- 下次 `--attach <bundle_id>` 可恢复到同一位置

## 8. Attach / Replay

```bash
./run/tui-workflow-debugger.sh --attach <bundle_id>
./run/tui-workflow-debugger.sh --replay <bundle_id>
```

Attach 恢复到 durable checkpoint 且不自动推进；Replay 只读。
