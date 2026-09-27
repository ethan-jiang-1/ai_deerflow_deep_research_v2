# Runbook 030 — 调试工作台（节点边界 step/continue）

> 前置：`make install` 已跑（含 demo-tui extra）；零凭证、零网络。
> 入口：`./run/tui-workflow-debugger.sh --fixture`（或 `make tui-debugger DEBUGGER_ARGS="--fixture"`）。
> 裸跑 `./run/tui-workflow-debugger.sh` 会给组合选择器（fixture / embedded / gateway）。
> 本质：用 `DebugRunDriver` 逐边界推进同一张 fixture StateGraph，实时看 timeline 与 Node Context。
>
> **支持的终端尺寸：100×30**。更小的终端（例如 80×24）不会静默裁切或挤压：工作台在
> 提示行说明"当前尺寸小于建议尺寸"、折叠两个按需分栏，并保持三入口、composer 与日志可用。
>
> **同一张工作台也跑在真实图上**：`./run/tui-workflow-debugger.sh --embedded-smoke` 起的是
> ALL_REAL 组合（driver 以 `ImplementationMode.ALL_REAL` 建 bundle），step/continue、
> `/context`、`/files`、`/attach`、`/replay` 与本文一致——差别只在真实节点会调模型与网页
> 工具（需要 `.env` 三变量 + 网络），且 `/context` 能看到捕获的调用上下文。见
> [runbook-031](runbook-031-debugger-embedded.md)。
>
> **本手册的每条步骤都由 `scripts/tui_journey_probe.py`（`make tui-journey`）在真机等价
> 环境下断言**：它执行真实脚本、逐步驱动下面整条流程，并在每个检查点做 ≥1.3s 真实停留后
> 校验姿态、分栏与提交；布局与尺寸档位由
> `tests/integration/test_demo_tui.py` 断言。手册与代码不一致时，以断言为准并同 PR 修手册。

## 1. 启动与首屏

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh --fixture
```

TUI 打开后即为可操作的首屏（fixture composition，无凭证要求）：

- 面板：`姿态: 无调试会话 · 输入研究问题开始调试（或 /attach <id>、/replay <id>）`
- 提示行：`输入研究问题开始调试会话 · /attach <id> 附加保留 bundle · /replay <id> 只读回放`
- 按钮行（调试专用）：`[New Run] [Attach] [Replay]`；共享入口按钮在调试器里**隐藏**
  （它们在调试器中无作用，隐藏而非移除——共享渲染路径仍会查询它们）
- composer 已聚焦，可直接输入

## 2. 提交问题（Start Step）→ 落在 HITL1 提问处

在 composer 输入研究问题（如 `Compare renewable energy storage technologies`）后按 Enter
（或把问题写进 composer 点 `New Run`）。

预期：
- 日志区出现 `你: <问题>`、`调试会话: b_XXXX… (Start Step)`，随后 `✓ bootstrap 提交（帧 N）`
- 面板显示 `姿态: awaiting_hitl · 下一节点: hitl1 · 等待输入（直接输入回答）`
- **提示行变为 `HITL 等待输入：直接输入回答后按 Enter`**

说明：Start Step 在全新 bundle 上会一路跑到第一个 interrupt（driver 在 fresh 状态下没有
已知的下一个节点，故 `interrupt_after` 为空），所以第一步就停在 hitl1 的提问处。

## 3. 回答 HITL1

在 composer 输入 profile 描述（如 `depth: standard` 或 `Use the default profile.`）后按 Enter。

预期：
- `✓ hitl1 提交（帧 N）`
- 面板变为 `姿态: paused_at_boundary · 下一节点: topic_planning`
- 提示行变为 `Enter（可留空）推进一个边界 · /context · /files · /detach · /cancel`

## 4. 逐步推进（step）

**composer 留空按 Enter** 即推进一个节点边界（输入任意非斜杠文本效果相同）。每次 Enter 恰好
提交一个逻辑节点，日志逐行给出 `✓ <node> 提交（帧 N）`：

```
topic_planning → wave0 → wave1 → wave2_synthesis → hitl2 → readiness → final_delivery
```

预期：
- 每个 paused 帧的面板给出下一节点名，例如 `姿态: paused_at_boundary · 下一节点: wave0`；
  harness 对整条 ladder 逐步断言该投影非空
- 最终 `姿态: terminal`（此时 `下一节点` 为 `—`，提示行变为 `会话已终态 · 输入新问题开始，或 /attach <id> 回看该 bundle`）
- 再次处于 `awaiting_hitl` 时，空 Enter **不推进**，而是提示"等待 HITL 输入"——此时必须直接输入回答

## 5. 查看 Node Context（按需分栏）

输入 `/context` 并按 Enter。

预期：
- 下方出现 **Node Context 分栏**（不再往日志里倒内容），分栏高度有上限
- fixture 模式下 deterministic node 没有 LLM 调用，分栏显示
  `Node Context: 尚无已捕获的调用上下文（deterministic node 没有模型调用，属预期覆盖）。`
- embedded/真实模式下，每次调用列出 `⌨ <node>#<n> model=<次数>`、固定 coverage strip
  （`INITIAL CAPTURED · RUNTIME ENFORCED · ACTIVITY BOUNDED · OUTCOME OBSERVED/UNAVAILABLE ·
  FILES CURRENT · RAW PROVIDER HISTORIES NOT RETAINED`）与 Objective 摘要
- `/context` 执行后 composer 被清空（下一次 Enter 不会重复该命令）

## 6. 查看工作区（按需分栏）

输入 `/files` 查看工作区根页；输入 `/files <相对路径>` **进入子目录**或**预览文件**。

预期：
- `/files` → `Files: workspace:. · 根: outputs[OPERATOR_ONLY], uploads[MODEL_READ], workspace[MODEL_READ]`
  以及每项 `[dir|file][策略标签] 相对路径 [字节数]`
- `/files notes` → 进入该目录并列目录内条目
- `/files notes/inner.md` → 预览：`Files: workspace:notes/inner.md · <字节>B · [MODEL_READ] · CURRENT`
  加内容（超长会标"已截断"）
- `/files ../../etc/passwd` → `不可读（path_escape）`；不存在的路径 → `不可读（not_found）`
- 分栏只渲染 alias 与相对路径，**绝不出现 host 绝对路径**

## 7. 干净退出

输入 `/detach` 并按 Enter。

预期：
- `调试会话` 引用被清除
- 面板回到 `姿态: 无调试会话 · 输入研究问题开始调试（或 /attach <id>、/replay <id>）`，
  提示行回到首屏文案——**不会残留上一会话的姿态**
- **Bundle 保留在原 boundary（仍是 active），不触发 cancel**

## 8. 中途退出后的恢复（重要）

因为 `/detach` 不 cancel，而生命周期每个 scope 只允许一个 active bundle，**中途 detach 后
再提交新问题会被拒为 `busy`**（日志给出可操作提示，面板仍是诚实的"无调试会话"）。两条出路：

- `/cancel` —— 放弃该活跃 bundle，之后可重新 Start Step（推荐用于调试脚手架）；本机会先用
  driver 的闭命令 `cancel` 再 `detach`（后者释放控制 lease）
- 或走完整个 ladder 到 `terminal`（bundle 完成，scope 自然释放）

```text
调试会话开启失败: 本 scope 已有活跃 bundle（可能是上次未走完的会话）。
输入 /cancel 放弃它后再 Start Step；已开启的会话请直接继续步进。
```

## 9. 三个动作与四条等价入口

工作台的新会话 / 附加 / 只读回放各有**四条已交付**的等价路径（按钮、slash、启动参数、
命令面板）：

| 动作 | 按钮 | slash | 启动参数 | 命令面板 |
|------|------|-------|----------|----------|
| 新会话 | `New Run`（用 composer 里的问题） | 问题 + Enter | `--fixture --debug` | `New Run` |
| 附加保留 bundle | `Attach`（用 composer 里的 bundle id） | `/attach <bundle_id>` | `--attach <bundle_id>` | `Attach` |
| 只读回放 | `Replay`（用 composer 里的 bundle id） | `/replay <bundle_id>` | `--replay <bundle_id>` | `Replay` |

- **Attach**：经生命周期校验后接到该 bundle 的 durable checkpoint，**不自动推进**；之后
  composer Enter 即可继续 step/answer。`/attach`（不带 id）列出**有界候选**（最近 5 个 run
  bundle 目录，operator view 而非生命周期权威）及各自姿态 `[takeover|rebind|busy]`；未知 id
  得到闭合拒绝 `not_found`。
- **Replay**：只读渲染该 bundle 的 trace（帧序列、route、next、terminal 处置），
  **不取 lease、不建调试会话、不写任何东西**。
- `--attach` / `--replay` 隐含 fixture 调试工作台组合；launcher 会按需补 `--fixture --debug`：

```bash
./run/tui-workflow-debugger.sh --attach <bundle_id>
./run/tui-workflow-debugger.sh --replay <bundle_id>
```

- **命令面板**（`Ctrl+P`）里 `New Run` / `Attach` / `Replay` 与按钮走同一组 typed 方法；
  带 id 的两个动作读取 composer 里的 bundle id。
