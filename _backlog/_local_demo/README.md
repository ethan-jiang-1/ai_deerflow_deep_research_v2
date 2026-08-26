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
> **TUI 轴分两格：010 = 自动 TUI（同一例子可全跑，真人零操作，✅ 已落地，
> 入口 `make demo-tui-real-auto` / `RUN-010.command`）、020 = 手动 TUI（与 010
> 完全同一例子，真人操作 HITL1，入口 `make demo-tui-embedded-smoke` /
> `RUN-020.command`）。**
> 拆分规则记在本文 §[TUI 轴线：010 与 020 的分割](#tui-010-020)，别忘。
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
| 010 | [`runbook-010-tui-auto.md`](runbook-010-tui-auto.md) + `RUN-010.command` | 花（中） | 同 003 的 `.env` 三变量 + `make install`（含 demo-tui extra）+ 网络（**真人零操作**） | **同一例子的 TUI 自动全跑**——真人只看不动手，hitl1/hitl2 全自动（scripted 默认产品路径），验证"TUI 一层真实图能自主到终态"。入口 `make demo-tui-real-auto`（BUG-061 → change `add-demo-tui-auto-entry`，2026-08-25 归档） | 同 003：`What is one bounded fact about China's EV battery market in 2024?` |
| 020 | [`runbook-020-tui-manual.md`](runbook-020-tui-manual.md) + `RUN-020.command` | 花（中） | 同 003 的 `.env` 三变量 + `make install`（含 demo-tui extra）+ 网络 + **真人坐镇** | 手动 TUI：**与 010 同一例子**，真人 HITL1 交互——**启动后先进侦察模式**（看环境/闲聊，不触发研究），点「Start Deep Research」或说触发语才启动；hitl1 里有快捷修订按钮/输入回显/修订确认，修订 profile proposal 并显式确认（semantic intake 真模型分类你的自由文本）；HITL2 是自主 continuation 不需要人。启动器不再提供 Stage A 选择（010 已覆盖通路）。language CHOICE 不在本 run（条件性 B2，前置 BUG-060） | 同 003：`What is one bounded fact about China's EV battery market in 2024?` |

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
> **落地现状（2026-08-21 完成）**：两半都已落地——
> - **010（自动 TUI）**：入口 `make demo-tui-real-auto`（= `demo_tui.py
>   --embedded-smoke --auto` → `StartRun(scripted=True, profile_intent=None)`，
>   默认产品路径同 004），runbook-010-tui-auto.md + RUN-010.command；落地载体
>   BUG-061（openspec change `add-demo-tui-auto-entry`，2026-08-25 已归档
>   `archive/2026-08-25-add-demo-tui-auto-entry/`）；
> - **020（手动 TUI）**：= 原 runbook-010 交互战役，已更名
>   `runbook-020-tui-manual.md` + RUN-020.command，入口
>   `make demo-tui-embedded-smoke`。

| | 010（自动 TUI，✅ 已落地） | 020（手动 TUI，✅ 已落地） |
| --- | --- | --- |
| 用途 | 人只看，验证真实图在 TUI 一层能自主跑到终态 | 人操作 hitl1，压交互认知面（semantic intake / 修订 / 确认） |
| 提交 | `StartRun(scripted=True, profile_intent=None)`（`auto_profile`+`auto_proceed` → hitl1/hitl2 全短路） | `StartRun(scripted=False)`（非 scripted → hitl1 interrupt 真人回答） |
| 按键 | 零 | hitl1 至少一轮修订 + 显式确认 |
| 验收 | exact bundle + `terminal_status=completed` + 真实 report（**无**四步证据链——无真人修订） | runbook-020 §3.4 七条（含四步证据链） |
| 现状 | ✅ 入口 `make demo-tui-real-auto`（demo_tui.py `--auto`，仅 embedded-smoke）+ `RUN-010.command` | ✅ 入口 `make demo-tui-embedded-smoke` + `RUN-020.command` |

**后续约定**：

1. **对照**：010（auto profile 默认路径）vs 020（真人确认后 profile）同一问题下可对照，
   逻辑同现状 003 vs 020 对照。
2. **新增 01x/02x 对**：按本文顶部"通用命名轴"规则补 runbook + `.command`（`01x`
   自动、`02x` 手动、同 `x` 同例子）。
3. **harness 变更纪律**：凡动 `deep_research_harness/` 的入口/行为，先登记
   `_backlog/bugs/`（如 BUG-061），修复走独立 openspec change。

> 红线照旧：010 自动跑 ends-to-end 成功或明确失败类别才算数，能调出 TUI 不算 PASS；
> 撞茬按 `_backlog/bugs/` 流程，修复走独立 openspec change。

## 01x（自动跑法）怎么做更合理：自带进度播报

> **原则（2026-08-21 定）**：凡是 `01x` 这类"真人零操作、坐等跑完"的自动跑法，
> **必须自带进度播报**——run 进行中要持续告诉人"当前在哪个阶段、已完成哪些、
> 最近在干什么"，**不能只显示一个等待秒数**。否则人无法区分"在跑"与"死了"，
> 体感就是"等个没完、以为它死了"（010 首跑实测教训）。

**播报的合理形态**（对应 010 现状，已落地）：

```text
进度: bootstrap → hitl1 → wave0 → wave1（进行中）
最近: 18:54:33 · wave2_synthesis model_tool started
模型调用: 11 次完成 · 55.9k tokens
journal 事件: 56
```

- **实时**：每 1 秒随 Working 心跳刷新（不是固定文案）；
- **来自 run 现场**：读当前 active bundle 的 `diagnostics/events.jsonl` +
  `run-summary.json`（被忽略的本地 retained-run 文件），聚合出阶段链/最近事件/
  模型调用数——实现是 `demo_tui.py::live_progress_lines()` 纯函数（TUI 层只读，
  不碰运行时，读不到就退化静态文案）；
- **判别标准**：进度行 / journal 事件数在变 = 活着（模型调用一次几十秒很正常）；
  只有等待秒数在涨、其余全不动且持续数分钟 = 卡死，才需要 Ctrl-C 重跑。

**自动跑法的另外两条体感底线（2026-08-21 定，010 已落地）**：

1. **报告必须给路径**：run 完成时明确显示
   `Report: <bundle>/final/report.md`，人不用翻目录找产出；
2. **运行中必须能拷贝**：**中间对话区（RichLog）保证可拷**——双击复制全文、
   Copy details 按钮复制全文、Option+拖拽选中一段、且每次渲染详情落盘
   `logs/tui-<pid>.log`（出问题时打开文件拷全量，不依赖屏幕选择）。

**以后新增 01x 跑法时照此办理**：任何自动全跑入口（TUI 或 CLI）都要有等价播报 +
报告路径 + 可拷贝，runbook 里写明"怎么看它在动、什么才算卡死"。没有这些的自动
跑法不算合格体验。

## 01x 与 02x 的交互差异（定稿，2026-08-22）

> **根源一句话：01x 人只看（观察者），02x 人坐镇（操作者）——所有交互差异
> 都由这一条推出。** 理解了这个，01x/02x 的每个交互设计都有出处。

| 维度 | 01x（自动跑法） | 02x（手动跑法） |
|---|---|---|
| 人的角色 | **观察者**：零操作、坐等跑完 | **操作者**：输入、决策、检查 |
| 交互方向 | 单向观察（系统→人） | 双向对话（人⇄系统） |
| 输出形态 | **同步（sync）**：后台图自动跑，心跳播报"在动" | **流式（Streaming）**：TUI↔模型对话逐段显示（`astream`） |
| 反馈要求 | 播报"在动"：进度链 / 模型调用数 / journal 计数 | **有活动就有反馈**：收到→处理中（计时）→结果，研究推进中模型调用也实时可见 |
| 输入理解 | N/A（scripted 自动，人无输入） | **真 NLU**：自然语言→结构化，模型主导（本地短语只是零成本捷径） |
| inspect | 不需要（操作者事后看现场） | **必须**（`/ls` `/cat` `/inspect` + 自然语言工具） |
| 可拷贝 | 必须（观察记录留证） | 必须（交互记录留证） |
| **API 依赖** | 底层 graph/runtime/journal 心跳 + 同步轮询 | **同一套底层共用**；交互层额外依赖流式（`astream`）、只读文件系统工具、斜杠命令 |

**API 依赖原则（2026-08-22 定）**：01x/02x 因行为差异，交互层依赖的 API
可以不同（01x 同步轮询足够，02x 需要流式 + 工具 + 文件读取）；但**底层
（graph / runtime / journal 心跳）尽量共用同一套**——现状即如此（同一个
TUI、同一个 `ResearchRunExperience`），差异只在 02x 交互层做加法，不为
两条轴线各造一套底层。

**01x 的三条体感底线**：① 进度播报（能区分"在跑/死了"）；② 报告给路径；
③ 可拷贝。缺任一 = 不合格。

**02x 的三条体感底线**：① 流式（有活动就有反馈，无"卡住无反应"）；
② 必须能 inspect workspace；③ 反馈闭环完整（输入回显→处理中→结果，失败
也明确回显"你输入的是 X"+给路）。缺任一 = 不合格。

**规则**：02x 任何 TUI↔模型直接对话必须流式；02x 任何输入必须有三阶段反馈
（收到/处理中/结果）；02x 必须给用户亲手 inspect 的手段；01x 自动研究保持
同步心跳。新增 01x/02x 对时按此表区分。

## 02x（手动跑法）怎么做更合理：必须支持 inspect workspace

> **铁律（2026-08-21 定）**：**02x 是"真人坐镇 TUI 手动跑"，那就必须给用户
> 亲手 inspect workspace 的手段——否则 inspect 毫无意义。** 用户不是来当
> 观众的，他要能随时看到"现在 workspace 里有什么、刚才跑出来的东西在哪"。
> 任何 02x 跑法，**没有可用的 inspect 手段 = 不合格**。
>
> 除 inspect 外，02x 还要求**流式 + 反馈闭环 + 真 NLU**（差异见
> 「01x 与 02x 的交互差异」表）：输入必有三阶段反馈、模型对话必流式、
> 自然语言输入由模型理解（本地短语只是零成本捷径）。

**020 已落地的 inspect 手段（后来的 02x 照此办理）**：

1. **侦察循环**：启动先进侦察模式、每轮研究结束后自动回到侦察——研究前后
   都有 inspection 机会（用户随时可以停下来看现场）；
2. **`环境` / `env` / `workspace` / `工作区` 命令**：直接在 TUI 里输出
   workspace 结构视图——workspace 绝对路径、`deep-research/`（N scopes ·
   M bundles）、`soft-bundles/`、`archive/` 概况、最近 3 个 run bundle 的
   终态与是否有报告、TUI 日志路径；
3. **全局斜杠命令（研究中也能用，2026-08-21 起）**：`/ls [路径]` 列目录、
   `/cat <文件>` 看文件内容（state.json 格式化 / events.jsonl 尾部 /
   report.md 开头）、`/inspect <bundle_id>` 单 bundle 摘要、`/clear` 清空
   查看面板——斜杠开头一律作为 inspect 命令处理，**不会**被当成研究答案或
   聊天；输出到独立查看面板，不被心跳渲染清掉；
4. **单 bundle 检查**：`make demo-sessions DEMO_ARGS="inspect <bundle_id>"`
   （TUI 内提示给出该命令，用户复制即可跑）；
5. **日志落盘**：每次渲染详情写 `logs/tui-<pid>.log`，出问题打开文件拷全量；
6. **可拷贝**：中间对话区双击复制全文、Copy details 按钮、Option+拖拽选一段；
7. **自然对话也能 inspect（2026-08-21 起）**：侦察聊天模型挂 3 个只读
   workspace 工具（`list_workspace` / `read_workspace_file` / `inspect_bundle`），
   直接问"workspace 里有什么 / 刚才的 run 在哪 / 某个文件内容"会真实查文件
   系统回答——用户以自然语言就能 inspect，与 `/ls` `/cat` 命令等价。

**以后新增 02x 跑法时照此办理**：任何手动跑法（TUI 或 CLI）都必须提供等价
inspect 手段（看 workspace 结构 / 查 bundle / 拿日志），runbook 里写明
"用户怎么 inspect"。**没有 inspect 手段的 02x 不算合格体验。**

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
