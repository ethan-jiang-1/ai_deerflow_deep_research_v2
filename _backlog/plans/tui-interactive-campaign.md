# Plan: TUI 交互战役（v2 定稿）

> 生成: 2026-08-20 | 状态: **v2 定稿（D1-D4 已收敛）**
> 收敛记录: D1=010（README 交互专项语义）；D2=003 短问题（与 003 minimal
> 自动 profile 可直接对照）；D3=最小轮数应答脚本（先保跑通）；D4=Stage C
> 推迟为可选（视 A/B 战况）。
> 前置: 001-004 战役完结（全 CLI、全自动）；本战役换轴——**交互性**

## 1. 考古结论（TUI 现状）

### 1.1 三个入口（`make` 目标，`scripts/demo_tui.py` 单文件 Textual 应用）

| 入口 | 凭证 | 跑什么 | 现状 |
| --- | --- | --- | --- |
| `demo-tui-fixture` | 零凭证 | fixture 图（确定性 composition proof） | 可跑，无战役记录 |
| `demo-tui-embedded-smoke` | 本地 `DEEPSEEK_API_KEY`+`TAVILY_API_KEY` | **直接本地全真实图**（`DemoAdapter.for_real()`） | 可跑，无战役记录；docs 标注 "explicit smoke work only" |
| `demo-tui PROFILE=<name>` | Gateway 侧（需先 `profile-dev`） | Gateway **观察者**（无取消按钮，只渲染 predecessor-approved 进度） | 产品默认真实路由，但依赖 profile/Gateway 体系 |

辅助面：`session-workbench`（本地 Bundle 观察投影，只读）；`demo-sessions`（bundle 检查）。

### 1.2 关键机制差异（vs CLI 001-004）

TUI 提交 `StartRun(question)` 时 **`scripted=False`**（composer 输入问题）：

- **hitl1 走真交互 interrupt 路径**：提出 profile proposal → 用户在 composer
  自由文本回答 → `_classify_proposal_reply`（**真实模型** semantic-intake
  调用）分类答复 → 多轮 refinement → CHOICE 选输出语言（TUI "Start
  proposal" 按钮 = `accept_current_proposal`）。auto_profile 短路只在
  `scripted=True` 时触发——001-004 全走 auto，**这条交互认知面从未被战役压过**。
- **hitl2 走真交互自主决策**（auto_proceed 同样只在 scripted 时触发）。
- Cancel 按钮在 embedded 模式真实可用（Gateway 模式明确不提供）。
- TUI 的 `StartRun` 不带 `profile_intent` → 默认产品路径（同 004 的 None 意图）。

### 1.3 与既有战役的关系

README 阶梯表明确："001~004 全部走全自动。真机交互/人工 HITL 专项留给
未来的 **010** 等 runbook"。TUI 战役 = **010 的探路与主体**。

## 2. 战役定位

**在 TUI 里以真人交互（hitl1 多轮 profile 对话 + hitl2 自主决策）跑通一次
真实 Deep Research（真实模型 + 真实 web 工具），并找茬交互认知面的缺陷。**

新找茬面（001-004 全没压过）：

1. hitl1 **semantic intake**（真实模型分类用户自由文本 → profile 字段）
   ——真模型 + 真人输入的组合，形状缺陷高危区（对照 BUG-058/059 教训）；
2. hitl1 **CHOICE 模式**（output_language 选项）与 TUI 按钮（accept/cancel）联动；
3. hitl2 交互决策内容与后续路由；
4. TUI 渲染层本身：provider 失败呈现（`_terminal_failure_presentation`）、
   进度 pipeline、长 run 下的 RichLog 行为。

## 3. 阶梯设计（提案主体："第一做啥，第二做啥"）

### Stage A — fixture TUI 交互面验证（零凭证，先决环境）

`make demo-tui-fixture`，人工在 TUI 里走完 fixture 图的 HITL 交互（若有）。

- **目的**：环境 OK（demo-tui extra 装好）、TUI 基本交互面（composer/按钮/
  进度条/日志）能用；确认 fixture 图是否真有交互 HITL（考古项，跑了才知道）。
- **验收**：TUI 启动 → 走完（或确认无交互步）→ 退出无异常；记录 fixture
  交互面的真实形状。
- **耗时预期**：分钟级。

### Stage B — embedded-smoke TUI 真交互真实跑（战役主体）

`make demo-tui-embedded-smoke`，本地 `.env` 凭证（同 003/004）。

- **操作脚本（control-environment 的交互版）**：固定研究问题（建议沿用
  003 的 `What is one bounded fact about China's EV battery market in 2024?`
  ——短问题交互轮次少）+ **固定应答脚本**：hitl1 每轮proposal 按预设回答
  （如第一轮 "depth: quick overview; output in Chinese"、CHOICE 轮选
  English），hitl2 按预设选 continue。应答脚本写进 runbook，保证可复现。
- **验收**：`final_delivery -> completed` + bundle `state.json` 的
  `profile` 字段**来自真人回答**（对照 003 的 minimal 三字段：交互路径应
  产出真实 depth/cost/language 而非 degraded）+ `final/report.md` 真实内容。
- **验收命令**：`demo-sessions inspect`（bundle 观察）+ events.jsonl 检查
  hitl1 交互轮数/semantic intake 调用。
- **找茬收集**：撞上啥按 `_backlog/bugs/` 流程报（预期高危：semantic
  intake 形状、CHOICE 校验、TUI 长跑渲染）。

### Stage C —（可选收尾）Gateway observer TUI 走一遍产品默认路由

`make profile-dev PROFILE=demo` + `make demo-tui PROFILE=demo`。

- **目的**：看产品默认真实形态（Gateway 侧凭证、TUI 纯观察者、无取消）；
  不做验收主体，只记录体验与差异（观察者模式进度渲染质量）。
- **定位**：体验记录，不设 PASS/FAIL；Gateway/profile 体系如有坑单独报 bug。

### 交付物

- `runbook-010-tui-interactive.md`（A/B/C 操作 + 应答脚本 + 验收）
- `_local_demo/README.md` 阶梯表加 010 行（交互轴）
- openspec change（若需改代码；纯跑通则只出 runbook + 观察记录）
- handoff-010（战役进行中使用，完结后按 004 先例收口删除）

## 4. 决策点（已收敛，v2）

- ~~D1 战役编号~~ → **010**（与"001-004=全自动阶梯"语义一致，005-009 留给自动轴）。
- ~~D2 Stage B 固定问题~~ → **003 短问题** `What is one bounded fact about
  China's EV battery market in 2024?`（交互轮次少；与 003 同问题下 minimal
  自动 vs 真人交互的 profile 差异可直接对照）。
- ~~D3 应答脚本策略~~ → **最小轮数**（每轮一个短句直取目标字段，可控可
  复现先保跑通；自然应答找茬作为后续加跑，不阻塞本战役）。
- ~~D4 Stage C 取舍~~ → **推迟为可选**（A/B 是主体，C 视战况另行决定）。

## 5. 风险与坑（预判）

1. **TUI 在工具会话里怎么跑**：Textual 是全屏交互应用，agent 无法替用户
   按键——战役本质是**人机协作**：agent 起环境/收 bundle 侧证据，用户坐
   TUI 前按应答脚本操作。runbook 要写成"给用户的操作单"。
2. **semantic intake 形状缺陷概率高**：001-004 从未真跑，参照 BUG-058/059
   经验，真实模型 + 契约边界的第一晚大概率有茬——这是产出不是失败。
3. **Ctrl-C/挂起**：embedded 真实图同 004（runbook §7 经验全继承）；TUI
   里 Ctrl-C 语义 = 退出 TUI 进程（bundle 侧状态由 checkpoint 决定，不猜）。
4. **fixture 图可能没有真交互**（Stage A 考古项，跑了才确认）。

## 6. 下一步

1. 用户收敛 D1-D4 → plan v2 定稿。
2. 建 openspec change（如需）+ 写 runbook-010。
3. Stage A → B（→ C 视 D4）按序执行，bug 流程随行。
