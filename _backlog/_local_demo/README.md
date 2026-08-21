# 本地跑法（从简单到难）

> **001~004 是同一个端到端 Deep Research 流程的四种跑法**，不是四个分开的功能模块。
> 都是从图的第一个节点一路跑到最后一个节点；区别只在于：是否用真实模型/网页工具、是否要人介入、环境前置有多少。
>
> **Control Environment 原则：所有 001~004 都使用固定研究问题，不开放自定义问题。**
> 固定问题 = 受控环境，跑出来的结果可对照、可复现，找 bug 容易很多。难度从 001 到 004 递增。
>
> **自动化原则：因为问题固定，HITL1/HITL2 的答案也是确定的，系统自动回答，不需要人工输入。**
> **001~004 全部走全自动（CLI 轴）。** 真机交互/人工 HITL 专项留给未来的 010 等 runbook，不在 001~004 内。
>
> **TUI 轴分两格：010 = 自动 TUI（同一例子可全跑，真人零操作，⚠️ 未落地）、
> 020 = 手动 TUI（与 010 完全同一例子，真人操作 HITL1，= 现行 runbook-010 的主体）。**
> 拆分计划记在本文 §[TUI 轴线：010 与 020 的分割](#tui-010-020)，别忘。
>
> **通用命名轴（从 01x/02x 起）：`01x` = 自动简化跑法、`02x` = 手动跑法，都从
> `.command` 启动；相同 `x` = 测试内容尽量相同，唯一差别是交互点：`01x` 自动补、
> `02x` 由真人补。** 例如 010/020 同一例子，区别只在 HITL1 是否自动化。
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
| 010(规划：自动 TUI) | —（待建 `runbook-010-tui-auto.md`） | 花（中） | 同 003 的 `.env` 三变量 + `make install`（含 demo-tui extra）+ 网络（**真人零操作**） | **计划中：同一例子的 TUI 自动全跑**——真人只看不动手，hitl1/hitl2 全自动（scripted），验证"TUI 一层真实图能自主到终态"。**尚未落地**：缺 auto 入口（`demo_tui.py` 无 scripted 开关）。详见 §[010 与 020 的分割](#tui-010-020) | 同 003：`What is one bounded fact about China's EV battery market in 2024?` |
| 020 | [`runbook-010-tui-interactive.md`](runbook-010-tui-interactive.md)（= 020 主体，未更名） | 花（中） | 同 003 的 `.env` 三变量 + `make install`（含 demo-tui extra）+ 网络 + **真人坐镇** | 手动 TUI：**与 010 同一例子**，真人 HITL1 交互——TUI 里修订 profile proposal 并显式确认（semantic intake 真模型分类你的自由文本）；HITL2 是自主 continuation 不需要人。压 001-004 从未触达的交互认知面。language CHOICE 不在本 run（条件性 B2，前置 BUG-060） | 同 003：`What is one bounded fact about China's EV battery market in 2024?` |

> 📐 手册命名规则固定为 `runbook-00X-难度-用途.md`，以后按这个补。

## TUI 轴线：010 与 020 的分割（记忆点，别忘） {#tui-010-020}

> **原意**：TUI 拆成两个 runbook——**010 = 可自动全跑**（同一个固定例子的 TUI 形态，
> 真人零操作，TUI 把真实研究自主全跑完）；**020 = 同一例子但手动跑**（真人坐 TUI
> 前操作 HITL1）。
>
> **通用规则（01x/02x 轴）**：
>
> - `01x` = **自动简化跑法**，`02x` = **手动跑法**，都通过 `.command` 启动；
> - 相同 `x` ⇒ 同一测试内容（尽量一样），唯一的差别是交互点：
>   `01x` 的交互由自动化补上（真人零操作），`02x` 的同一交互由真人补上；
> - 这条规则从 010/020 开始，之后若加 011/021、012/022 等也照此命名。
>
> **落地现状**：只落了"手动"这一半——现行 `runbook-010-tui-interactive.md` 的
> Stage B1 交互战役**就是 020 的主体**；**"自动 TUI"（010）至今没建**，这就是
> "感觉没落地"的那一半。

| | 010（自动 TUI，**未落地**） | 020（手动 TUI，= 现行 runbook-010 B1） |
| --- | --- | --- |
| 用途 | 人只看，验证真实图在 TUI 一层能自主跑到终态 | 人操作 hitl1，压交互认知面（semantic intake / 修订 / 确认） |
| 提交 | `StartRun(scripted=True, profile_intent=None)`（默认产品路径同 004；`auto_profile`+`auto_proceed` → hitl1/hitl2 全短路） | `StartRun(scripted=False)`（非 scripted → hitl1 interrupt 真人回答） |
| 按键 | 零 | hitl1 至少一轮修订 + 显式确认 |
| 验收 | exact bundle + `terminal_status=completed` + 真实 report（**无**四步证据链——无真人修订） | runbook-010 §3.4 七条（含四步证据链） |
| 现状 | **缺入口**：`scripts/demo_tui.py` composer 提交永远是 `StartRun(scripted=False)`（demo_tui.py:605），没有任何 `--auto/--scripted` 开关；全自动机制现在只在 CLI 侧（`make demo-real-scripted` = `demo_real.py --embedded-smoke --scripted`） | ✅ 已落地（入口 `make demo-tui-embedded-smoke`） |

**落地 010 需要的最小工作**（按规程走，不隐式改契约）：

1. **入口**：`demo_tui.py` 给 embedded-smoke 加 auto 开关（或独立 `make demo-tui-real-auto`：
   `demo_tui.py --embedded-smoke --auto` → `StartRun(scripted=True, profile_intent=None)`）。
   presentation adapter 层小 change → openspec change + 确定性测试（fixture 同理可让
   Stage A 真正零按键）。
2. **runbook-010-auto**：自动 TUI 操作单（应答脚本 = "什么都不按"；验收复用 exact-bundle +
   terminal completed + 真实 report；无四步证据链要求）。固定问题沿用 003 的 China EV 2024
   （与 020 同一例子）。
3. **更名/拆分**：010(auto) 建好后，把现行 `runbook-010-tui-interactive.md` 更名为
   `runbook-020-tui-manual.md`，并同步 handoff-010 / `RUN-010-TUI.command` / 战役计划与进度。
4. **对照**：010（auto profile 默认路径）vs 020（真人确认后 profile）同一问题下可对照，
   逻辑同现状 003 vs 010 对照。

> 红线照旧：010 自动跑 ends-to-end 成功或明确失败类别才算数，能调出 TUI 不算 PASS；
> 撞茬按 `_backlog/bugs/` 流程，修复走独立 openspec change。

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
