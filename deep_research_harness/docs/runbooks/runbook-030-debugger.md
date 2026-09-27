# Runbook 030 — 调试工作台（节点边界 step/continue）

> 前置：`make install` 已跑（含 demo-tui extra）；零凭证、零网络。
> 入口：`./run/tui-workflow-debugger.sh --fixture`（或 `make tui-debugger DEBUGGER_ARGS="--fixture"`）
> 本质：用 `DebugRunDriver` 逐边界推进同一张 fixture StateGraph，实时看 timeline 和 Node Context。
>
> **本手册的步骤由 `scripts/tui_journey_probe.py` 在真机等价环境下逐条断言**
> （`make tui-journey`）：它执行真实脚本、驱动下面整条流程并在每步校验姿态与提交。
> 手册与代码不一致时，以该 harness 的断言为准并同 PR 修手册。

## 1. 启动

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh --fixture
```

TUI 打开后看到 Ready 状态（fixture composition，无凭证要求）。

## 2. 提交问题（Start Step）→ 落在 HITL1 提问处

在 composer 输入一个研究问题（如 `Compare renewable energy storage technologies`），按 Enter。

预期：
- 日志区出现 `调试会话: b_XXXX… (Start Step)`
- 然后 `✓ bootstrap 提交（帧 N）`
- 面板显示 `姿态: awaiting_hitl · 等待输入（直接输入回答）`

说明：**Start Step 在全新 bundle 上会一路跑到第一个 interrupt**（driver 在
fresh 状态下没有已知的下一个节点，故 `interrupt_after` 为空），所以第一步就停在
hitl1 的提问处，而不是停在 hitl1 之前的边界。

## 3. 回答 HITL1

在 composer 输入一个 profile 描述（如 `depth: standard` 或 `Use the default profile.`），按 Enter。

预期：
- `✓ hitl1 提交（帧 N）`
- 面板变为 `姿态: paused_at_boundary`

## 4. 逐步推进（step）

**composer 留空按 Enter** 即推进一个节点边界（也可输入任意非斜杠文本，效果相同）。
每次 Enter 提交恰好一个逻辑节点，日志逐行给出 `✓ <node> 提交（帧 N）`：

```
topic_planning → wave0 → wave1 → wave2_synthesis → hitl2 → readiness → final_delivery
```

预期：
- 最终 `姿态: terminal`（此时 `下一节点` 显示 `—`）
- 每个 paused 帧的面板给出下一个节点名，例如 `姿态: paused_at_boundary · 下一节点: wave0`；
  harness 对整条 ladder 逐步断言该投影非空。
- 再次处于 `awaiting_hitl` 时，空 Enter 不会推进，而是提示"等待 HITL 输入"——
  此时必须直接输入回答。

## 5. 查看 Node Context

输入 `/context` 并按 Enter。

预期：
- fixture 模式下，deterministic node（bootstrap、hitl1、topic_planning 等）没有 LLM 调用，所以 `/context` 显示 `尚无已捕获的调用上下文` 属预期
- embedded 模式下，LLM-bearing node（wave0 等）会有 captured context snapshot

## 6. 干净退出

输入 `/detach` 并按 Enter。

预期：
- `调试会话` 引用被清除
- **Bundle 保留在原 boundary（仍是 active），不触发 cancel**

## 7. 中途退出后的恢复（重要）

因为 `/detach` 不 cancel，而生命周期每个 scope 只允许一个 active bundle，
**中途 detach 后再提交新问题会被拒为 `busy`**（日志给出可操作提示）。两条出路：

- `/cancel` —— 放弃该活跃 bundle，之后可重新 Start Step（推荐用于调试脚手架）；
- 或走完整个 ladder 到 `terminal`（bundle 完成，scope 自然释放）。

```text
调试会话开启失败: 本 scope 已有活跃 bundle（可能是上次未走完的会话）。
输入 /cancel 放弃它后再 Start Step；已开启的会话请直接继续步进。
```

## 8. Attach / Replay（三入口：按钮、slash、启动参数等价）

工作台的三个入口各自可等价触发同一组动作（RED-014）：

| 入口 | 按钮 | slash | 启动参数 |
|------|------|-------|----------|
| 新会话 | `New Run`（用 composer 里的问题） | 直接在 composer 输入问题按 Enter | `--fixture --debug` |
| 附加保留 bundle | `Attach`（用 composer 里的 bundle id） | `/attach <bundle_id>` | `--attach <bundle_id>` |
| 只读回放 | `Replay`（用 composer 里的 bundle id） | `/replay <bundle_id>` | `--replay <bundle_id>` |

- **Attach**：经生命周期校验后把工作台接到该 bundle 的 durable checkpoint，**不自动推进**；
  之后 composer Enter 即可继续 step/answer。
- **Replay**：只读渲染该 bundle 的 trace（帧序列、route、next、terminal 处置），
  **不取 lease、不建调试会话、不写任何东西**。
- `--attach` / `--replay` 隐含 fixture 调试工作台组合；launcher 会按需补
  `--fixture --debug`，所以下面两条可直接用：

```bash
./run/tui-workflow-debugger.sh --attach <bundle_id>
./run/tui-workflow-debugger.sh --replay <bundle_id>
```

> 备注：命令面板（command palette）归一与专门的 Node Context/Files 分栏属 RED-014
> 的后续 UI 面，见 `_backlog/bugs/` 的历史卡片（BUG-069 已交付按钮/slash/参数三入口
> 与 attach/replay 消费）。
