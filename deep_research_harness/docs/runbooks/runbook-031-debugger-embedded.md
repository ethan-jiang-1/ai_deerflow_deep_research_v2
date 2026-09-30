# Runbook 031 — 调试工作台（embedded 真实图，逐边界 step + Node Context）

> **状态（2026-09-29）：已落地，且真图全流程已由 live 自证探针验证。** 调试驱动是组合无关的：`--embedded-smoke` 现在起的是
> **全真实图（ALL_REAL）上的调试工作台**——launcher 会为该组合注入 `--debug`，driver 以
> `ImplementationMode.ALL_REAL` 建 bundle，step/continue、`/context`、`/files`、`/attach`、
> `/replay` 与 fixture 路线完全一致；`/context` 此时能看到 LLM-bearing node 的捕获上下文，
> 且可用 `/context <node>#<n>` **下钻**到某一次调用：initial system policy / human message、
> base policy 与 capability 分层的内容摘录与哈希、enforced tools（requested→enforced）与
> budget、output schema、virtual roots 与 mounts、activity 与 coverage strip。
>
> 前置：同 003 的 `.env` 三变量（`DEEPSEEK_API_KEY`、`TAVILY_API_KEY`、
> `DEERFLOW_DEMO_MODEL`）+ `make install` + 网络——真实节点真的要调模型与网页工具。
> **诚实边界（2026-09-29 更新）**：真图全流程（真问题驱动 → 真提案卡片 → `/rerun` 再生 →
> auto-hitl 代答 → wave0 真实捕获 → terminal）已由
> `tests/live/test_debugger_embedded_live.py` 在本机真凭证下自证通过（并顺带暴露并修复
> BUG-079/080）；**人眼层面的体验**（排版、节奏、你自己的研究问题）仍属操作者窗口。
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

## 5c. 条件断点（LDD-010，RED-018）

- **`/run [节点] if <条件>`**：条件是 `字段 运算符 值` 的 **and 合取**（最多 8 个
  子句），字段取类型化 State 的**标量可比较字段**（int/str/bool 及可空变体；StrEnum
  如 `phase` 按其字符串值比较），运算符闭集 `== != >= <= > <`，字面值
  `true/false/none/整数/无空格字符串`。
- 语义：带节点目标时，**节点已访问且条件满足**的边界才停（目标边界条件不满足就
  越过它继续）；不带目标时任一**条件满足的边界**即停。条件永不满足 = 驱动跑到底
  （terminal / 既有 64 步上界是安全网），不会报错。
- 坏条件在**解析期即拒绝**（未知字段、不可比较字段、闭集外运算符、字面值类型与
  字段不符、含空格字面值），点名问题并列出可用字段，**绝不带病开车**。
- 例：`/run wave2_synthesis if generation >= 1`、`/run if phase == wave0 and
  degraded_profile == true`。

## 6. 与 030 的区别

| 维度 | 030 fixture | 031 embedded |
|------|------------|--------------|
| 模型 | 无（deterministic） | 真实 LLM + Tavily |
| 耗时 | 秒级 | 分钟级（wave0 可达数分钟） |
| Node Context | `/context` 显示空属预期 | 有真实 captured snapshot |
| 凭证 | 零 | `.env` 三变量 + 网络 |
| 费用 | 免费 | 消耗 API 额度 |

## 7. Live 验证（自证探针 + 操作者窗口）

无头门禁已锁住接线与渲染（`make tui-journey`、`make debugger-proof`、
`UV_OFFLINE=1 make verify` 全绿）。live 自证探针（真凭证 + 真图 + 真工作台渲染，
单次全流程，**会消耗真实 API 额度**）：

```bash
cd deep_research_harness
UV_OFFLINE=1 .venv/bin/python -m pytest tests/live/test_debugger_embedded_live.py --no-header -q
```

探针覆盖：真实提案卡片（无机器 JSON）→ `/rerun` 真重跑再生提案 → `/run` 默认
auto-hitl 代答（日志明示）→ 真实 wave0 捕获（Node Context）→ terminal（真图若有
HITL2 由探针按人答 `proceed`）。人眼层面的体验（排版、节奏、自己的研究问题）仍属
操作者窗口；观察到的缺陷带日志（Copy details）+ bundle id 回来立卡。

## 8. 经典 debugger 概念对照与已知边界

| 经典概念 | 工作台对应 | 状态 |
|---|---|---|
| 断点 | `/pause` + HITL 天然停点 | ✅ |
| 单步 | Enter（空 composer = advance_one） | ✅ |
| 继续 | `/run`（默认 auto-hitl 代答，`--no-auto-hitl` 关） | ✅ |
| 跑到指定节点 | `/run <节点>`（11 个逻辑节点全部可作目标；含中断型节点=停在其请求处） | ✅ |
| 重执行帧 | `/rerun`（重跑最后已提交节点，落到下一停点） | ✅ |
| 观察窗 | `/context`（真实快照+下钻）· `/files` · `/inspect` · `/harness` · `/targets` | ✅ |
| 断点处对话 | HITL 类型化卡片 + `?` 侧聊 | ✅ |
| 回放 | `/replay` 只读帧回放 | ✅ |
| 恢复 | `--attach <id>` 接回暂停 bundle · 失败渲染真实姿态与恢复动作 | ✅ |
| 长操作不装死 | 所有调试命令执行期间姿态栏脉搏（已耗时 + journal 进度行） | ✅ |
| 条件断点 | `/run [节点] if <字段><op><值>`（and 合取；字段为类型化 State 标量字段） | ✅ 2026-09-29（LDD-010/RED-018） |
| 改输入重跑（edit-and-continue） | — | ❌ Stage 3（明确缓办） |
| 注入/状态手术 | — | ❌ Stage 3（明确缓办） |

**已知粒度边界**：单步/断点的粒度是**逻辑节点**（wave0 内部多个并行 work unit 作为
一个边界一次提交；其内部进度由执行期脉搏行与提交后的 `/inspect` work-unit 记录呈现）。
按 work-unit 逐步进需要引擎级改动，属 Stage 3，未立项。
