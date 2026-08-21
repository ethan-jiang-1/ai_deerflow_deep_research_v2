# Plan: TUI 交互战役（v4 消化版）

> ⚠️ **编号更新（2026-08-21）**：本战役的"手动交互"主线按新命名轴
> **010/020 拆分**后成为 **020**（runbook-020-tui-manual.md，入口
> `make demo-tui-embedded-smoke`）；**010 = 自动 TUI 孪生**（runbook-010-tui-auto.md，
> 入口 `make demo-tui-real-auto`，BUG-061）。本文件描述的 010 即现在的 020 内容。
>
> 生成: 2026-08-20 | 更新: 2026-08-20 | 状态: **v4——已消化独立审阅并逐条核验代码，尚未执行**
> 前置: 001-004 战役完结（全 CLI、全自动）；本战役换轴——**HITL1 真人交互与 TUI 观察性**。
> v4 变更: 全量消化 `tui-interactive-campaign-review.md`（另一 agent 的独立审阅）——
> 其事实主张已逐条回到当前代码核验，**全部成立**；修复 v3 的内部矛盾，
> 范围收窄为 B1 主线，CHOICE 移出 PASS 范围。

## 0. 审阅采纳记录（v4）

| # | 审阅主张 | 核验证据（当前代码） | 处置 |
| --- | --- | --- | --- |
| 1 | 真实 HITL2 是自主 continuation，不是人工决策点，无 interrupt/prompt | `graph/nodes/hitl2/node.py` 非 scripted 分支直接 `recommend_hitl2_route(state)`，不产生 `PendingResearchInterrupt` | **采纳**。删除 v3 的 hitl2 人工找茬面与 "hitl2 输 continue" 应答步骤 |
| 2 | 003 英文固定问题不会触发 language CHOICE | `domain/profile.py::derive_comparison_intake_seed`：含 ASCII 字母 → 确定性 `en`/`en` | **采纳**。CHOICE 拆为条件性 B2，B1 主线无 CHOICE 轮 |
| 3 | Demo TUI 当前无法提交 CHOICE 所需的 typed OPTION（真 bug） | `demo_tui.py:577` 所有 composer 输入构造 text `AnswerRun`；`run_experience.py:357-358` 对 hitl1 CHOICE 强制 `response_kind=option` 否则抛 `hitl1_language_answer_requires_option`；"Start proposal" 按钮只在 `accept_current_proposal` visible control 存在时显示，language CHOICE 无此 control | **采纳**。Stage 0 登记 bug；B2 以修复为前置 |
| 4 | fixture 是否交互是已知事实，不是考古项 | `tests/integration/test_demo_tui.py` 确定性证明 fixture 路径 `AwaitingInput`(hitl1/text) → 回答 → completed terminal | **采纳**。Stage A 改为已知形状的 UI smoke |
| 5 | 非空 profile 不足以证明"真人改变了结果"（初始 proposal 本就是模型生成） | 逻辑成立 | **采纳**。改条件式修订脚本 + 四步证据链（§5） |
| 6 | Journal 不能精确归因 semantic-intake capability | `run_observation.py` 的 model_tool fact 只含 `phase/outcome/attempt_id/call_ordinal`，契约明示不携带 capability | **采纳证据限制，收窄范围**：010 不新建 closed observation fact（确有产品需求另立 change），只收窄证据声明，弃用 `grep semantic_intake` 式伪归因 |
| 7 | 必须绑定本次 exact bundle，不能用 mtime-latest | runbook/launcher 现取 mtime 最新 bundle，启动前失败或并发写入时会把历史 bundle 当本次证据 | **采纳**（§5.2） |
| 8 | embedded smoke 前置不止两个 key | `_demo_core.py::validate_real_demo_prerequisites` = `DEERFLOW_DEMO_MODEL` selector + 匹配模型凭证（如 `DEEPSEEK_API_KEY`）+ `TAVILY_API_KEY` | **采纳**。runbook 弃用 `grep ../.env`（错位 + 泄漏 secret），改 `make install` + 现有 safe readiness/preflight |
| 9 | Demo TUI 不是当前 Primary User 产品入口 | `deep_research_harness/README.md`：contributor/operator visualizer；当前产品路线是 Dedicated Agent + reflected tool | **采纳**。Stage C 更名为 Gateway observer 路线观察，不做产品验收声明 |

**无事实性忽略项**；仅两处范围收窄（见 #6 与下节）。

**范围收窄（不照单全收）**：

1. 审阅 §3.2 建议的"另行设计 closed observation fact 做 capability 精确归因"——
   推迟。010 只做证据声明收窄；若产品确需精确归因，另立 openspec change。
2. 审阅 §5 的 B2（CHOICE 覆盖）——改纯条件式：typed OPTION bug 修复且仍决定
   覆盖时才执行；**不阻塞 010、不在 010 PASS 范围内**。

## 1. 战役定位

010 的目标不是给自动流程套一层 TUI，而是首次在 embedded-smoke TUI 中用真人回答压测当前已经存在的 HITL1 交互契约：

1. 初始 profile brief 与 proposal 展示；
2. 真人非确认自由文本进入 zero-tool semantic intake；
3. semantic candidate 被 graph/domain admission 为新的 advisory proposal；
4. 真人通过当前 proposal 的显式 control 确认；
5. profile 由 graph owner 发布，真实研究继续执行；
6. TUI 对等待、失败、取消、**自主 HITL2 continuation** 和终态的呈现。

**范围边界：**

- 真人只参与 HITL1；HITL2 是被观察的自主 continuation（`recommend_hitl2_route`），不产生人工 prompt，不输入 `continue`；
- language CHOICE 不属于 B1 的 003 对照 run，另列为条件性 B2（前置：bug 修复）；
- TUI 是 contributor/operator visualizer，不是当前 Primary User 产品入口；
- 本战役的 live model 结果是观察证据，不把真实模型语义质量伪装成 deterministic pass。

### 1.1 三个入口（`make` 目标，`scripts/demo_tui.py` 单文件 Textual 应用）

| 入口 | 凭证 | 跑什么 | 现状 |
| --- | --- | --- | --- |
| `demo-tui-fixture` | 零凭证 | fixture 图（确定性 composition proof） | 可跑，无战役记录 |
| `demo-tui-embedded-smoke` | `DEERFLOW_DEMO_MODEL` + 匹配凭证 + `TAVILY_API_KEY` | **直接本地全真实图**（`DemoAdapter.for_real()`） | 可跑，无战役记录；docs 标注 "explicit smoke work only" |
| `demo-tui PROFILE=<name>` | Gateway 侧（需先 `profile-dev`） | Gateway **观察者**（无取消按钮，只渲染 predecessor-approved 进度） | 默认真实路由，但依赖 profile/Gateway 体系 |

辅助面：`session-workbench`（本地 Bundle 观察投影，只读）；`demo-sessions`（bundle 检查）。

### 1.2 关键机制差异（vs CLI 001-004）

TUI 提交 `StartRun(question)` 时 **`scripted=False`**（composer 输入问题）：

- **hitl1 走真交互 interrupt 路径**：提出 profile proposal → 用户在 composer
  自由文本回答 → `_classify_proposal_reply`（**真实模型** semantic-intake
  调用）分类答复 → 多轮 refinement → 显式确认（TUI "Start proposal" 按钮 =
  `accept_current_proposal`）。auto_profile 短路只在 `scripted=True` 时触发
  ——001-004 全走 auto，**这条交互认知面从未被战役压过**。
- **hitl2 走自主 continuation**（同 scripted 一样不 interrupt；区别仅是非
  scripted 不写 `hitl2_auto_proceed` 标记，由 `recommend_hitl2_route` 决策）。
- Cancel 按钮在 embedded 模式真实可用（Gateway 模式明确不提供）。
- TUI 的 `StartRun` 不带 `profile_intent` → 默认产品路径（同 004 的 None 意图）。

### 1.3 与既有战役的关系

README 阶梯表明确："001~004 全部走全自动。真机交互/人工 HITL 专项留给
未来的 **010** 等 runbook"。TUI 战役 = **010 的探路与主体**。

## 2. 战役目标与找茬面（v4 修正）

**在 TUI 里以真人 HITL1 交互跑通一次真实 Deep Research（真实模型 + 真实
web 工具），并找茬交互认知面的缺陷。**

新找茬面（001-004 全没压过）：

1. hitl1 **semantic intake**（真实模型分类用户自由文本 → profile 字段）
   ——真模型 + 真人输入的组合，形状缺陷高危区（对照 BUG-058/059 教训）；
2. hitl1 **多轮 refinement 与显式确认 control** 的 TUI 联动（composer /
   "Start proposal" 按钮在 visible control 存在时的可用性）；
3. TUI 对**自主 HITL2 continuation 的呈现**（作为被观察 phase 经过，无人工
   prompt——观察其渲染与耗时叙事，不是人工决策点）；
4. TUI 渲染层本身：provider 失败呈现（`_terminal_failure_presentation`）、
   进度 pipeline、长 run 下的 RichLog 行为。

（v3 的 "hitl2 交互决策内容" 找茬面已按采纳记录 #1 删除。）

## 3. 阶梯设计（v4：0 → A → B1 →（条件 B2）→（可选 C））

### Stage 0 — 战役校准（本 plan v4 已完成其一）

1. ~~校正 plan~~ ✅ 本文件 v4。
2. **重写 `runbook-010-tui-interactive.md`**：应答脚本去 CHOICE/hitl2 人工轮、
   改条件式修订脚本；验收改 exact bundle + 四步证据链；前置改
   `make install` + safe preflight（弃 `grep ../.env`）；删除"旧 bundle
   自动归档"表述。
3. **同步或下线 `RUN-010-TUI.command`**：提示卡同样含非法操作与 latest-bundle
   逻辑，未同步前不得作为战役入口。
4. **登记 bug**（`_backlog/bugs/`，下一号 BUG-060）：Demo TUI 对当前 typed
   OPTION（hitl1 language CHOICE）不投影为 typed `AnswerRun`。
5. `_backlog/_local_demo/README.md` 阶梯表 010 行去掉 "hitl1/hitl2 决策" 中
   的 hitl2 人工表述。

### Stage A — fixture TUI 已知形状 smoke（零凭证，分钟级）

`make demo-tui-fixture`。fixture 图**已知**发出一个 `mode=TEXT` 的 hitl1
interrupt（集成测试确定性证明），故本阶段是 UI smoke 不是考古：

- **验证形状**：Ready → StartRun → `AwaitingInput`(hitl1/text) → composer
  回答 → Terminal completed → 退出无异常；可选另跑一次验证 Cancel 分支。
- **不声称**：不证明 real semantic intake、language CHOICE 或真实报告质量。

### Stage B1 — embedded real HITL1 semantic 战役主体

`make demo-tui-embedded-smoke`，本地 `.env`（三要素，见 §1.1）。

- **固定问题**（003 原题，可对照）：`What is one bounded fact about China's EV battery market in 2024?`
- **条件式修订应答脚本**（可复现且必证 human-caused change）：
  - 轮 1（profile proposal）：看初始 proposal 的 `depth`——若非
    `quick_overview`，输入 `depth: quick overview.`；若已是
    `quick_overview`，输入 `depth: deep dive.`（必然不同于初始值）；
  - 轮 2（refinement，如出现）：看修订后 proposal 符合上述目标 → 点
    **Start proposal**（= `accept_current_proposal`）显式确认；
  - **无 CHOICE 轮**（英文问题确定性 en，见采纳记录 #2）、**无 hitl2 人工轮**
    （自主 continuation，见采纳记录 #1）；
  - 记录三值：初始 proposal 值 / 修订语句 / 修订后值。
- **等待**：hitl2 作为自主 phase 经过（无 prompt），后续图自动到终态。
- **验收**：按 §6 PASS 定义。

### Stage B2 — language CHOICE 专项（条件式，不在 010 PASS 范围）

仅在 **同时**满足时执行：(a) BUG-060（typed OPTION 缺失）已通过 openspec
change 修复并有确定性回归；(b) 战后仍决定覆盖 CHOICE。执行时用独立的
unspecified-language 输入（不含 ASCII 字母与汉字的问题），验证 TUI 只显示
`zh`/`en`、提交 typed OPTION、HITL1 admission 写入选定 output language。
该 run 不与 003 profile 对照混同。

### Stage C — Gateway observer 体验（可选）

`make profile-dev PROFILE=demo` + `make demo-tui PROFILE=demo`。定位：
**Demo TUI 的 default real Gateway observer 路线观察**（transport/presentation
差异），明确：无本地 cancel、无 embedded bundle 发现假设、**无 Primary User
产品验收声明**。若执行，预先写出有限观察问题清单；否则从交付物删除占位。

## 4. 决策点（已收敛）

- ~~D1 战役编号~~ → **010**（与"001-004=全自动阶梯"语义一致，005-009 留给自动轴）。
- ~~D2 Stage B 固定问题~~ → **003 短问题**（交互轮次少；同问题下 minimal
  自动 vs 真人交互的 profile 差异可直接对照）。其推论：B1 无 CHOICE 轮。
- ~~D3 应答脚本策略~~ → **条件式修订**（若初始 depth=X 则改 Y，保证必然
  不同的修订可复现且可证明 human-caused change；自然应答找茬留给后续加跑）。
- ~~D4 Stage C 取舍~~ → **可选**，且需预写观察问题才保留占位。
- **D5（v4 新增）CHOICE 范围** → 移出 010 PASS 范围；B2 纯条件式（bug 修复
  + 仍决定覆盖），不阻塞战役。

## 5. 证据规范（v4 新增，runbook 必须遵守）

### 5.1 human-caused change 的四步证据链

```text
初始可见 proposal（记录字段值）
  -> 真人提出必然不同的修订（记录语句）
  -> 修订后的可见 proposal（记录字段值）
  -> 真人选择显式确认 control（Start proposal）
  -> request/profile.json 与 state.json 匹配修订后 proposal
```

"profile 字段来自真人回答"只能声明为：最终 proposal 经真人确认；指定字段
由真人修订并经 graph admission 进入最终 profile。其他未修改字段仍可能来自
初始模型 proposal。

### 5.2 exact bundle 绑定

优先使用本次 run 返回的 exact `bundle_id`。launcher/runbook 暂拿不到 typed
result 时，至少：启动前记录 bundle 目录集合，退出后只接受本次**新增且唯一**
的 bundle；零个或多个新增都报"证据未绑定"，**不得回退 mtime-latest**。
旧 bundle 不会被自动归档（real DemoAdapter 每进程独立 scope 但不清理）。

### 5.3 Journal 证据限制

model_tool fact 只有 phase/outcome/attempt/ordinal，无 capability 归因。
可用证据：修订前后 proposal、相关 HITL1 visit/resume、HITL1 model-tool
ordinal、最终 `request/profile.json`、终态 State、report/citation artifacts。
对"具体是哪一种认知调用（brief/intake/repair）"保留限制说明，不做字符串
搜索伪归因。

## 6. PASS 定义（Stage B1，全部满足才算过）

1. exact bundle 绑定唯一且来自本次 run（§5.2）；
2. 四步证据链完整记录（§5.1）：初始 proposal、真人修订、修订 proposal、
   显式 confirmation；
3. 最终 `request/profile.json` 与 State 匹配修订后 proposal，且
   `degraded_profile=false`；
4. lifecycle 到达 `terminal_status=completed`，HITL2 作为自主 phase 经过而
   无人工 prompt；
5. `final/report.md`、citation map 及必要 artifact 存在并通过与 003 相同
   层级的内容检查；
6. Journal/visit 证据只声明实际能证明的事实（§5.3）；
7. 任何 blocked/fault 保留 exact bundle 与闭合 failure category，按
   `_backlog/bugs/` 流程处理——**发现 bug 不替代端到端成功作为 PASS**。

## 7. 交付物

- `runbook-010-tui-interactive.md` **重写**（0/A/B1 操作单 + 条件式应答脚本
  + §5 证据规范 + §6 PASS 定义；B2/C 仅条件占位）
- `RUN-010-TUI.command` 同步重写（或修复前先下线）
- `_backlog/_local_demo/README.md` 阶梯表 010 行修正
- `_backlog/bugs/BUG-060`（Demo TUI typed OPTION 缺失）
- openspec change（仅当修 TUI/共享交互行为时；primary causal owner 从
  presentation adapter 与 shared typed interaction boundary 的实际问题中
  选定，不把 route/profile admission 下放给 TUI）
- handoff-010（战役进行中使用，完结后按 004 先例收口删除）

## 8. 风险与坑（预判）

1. **TUI 在工具会话里怎么跑**：Textual 全屏交互，agent 无法替用户按键——
   战役本质是**人机协作**：agent 起环境/收 bundle 侧证据，用户坐 TUI 前按
   应答脚本操作。runbook 写成"给用户的操作单"。
2. **semantic intake 形状缺陷概率高**：001-004 从未真跑，参照 BUG-058/059
   经验，真实模型 + 契约边界的第一晚大概率有茬——这是产出不是失败。
3. **Ctrl-C/挂起**：embedded 真实图同 004（runbook §7 经验全继承）；TUI 里
   Ctrl-C = 退出 TUI 进程（bundle 侧状态由 checkpoint 决定，不猜）；重跑
   产生新 bundle，旧 bundle 不清理不归档（§5.2）。
4. **验收假阳性三源**（v4 新增，均已封堵）：mtime-latest 冒充本次证据（§5.2）、
   非空 profile 冒充真人改变（§5.1）、`grep semantic_intake` 冒充 capability
   归因（§5.3）。

## 9. 下一步

1. Stage 0 收口：重写 runbook-010 → 同步/下线 launcher → 登记 BUG-060 →
   修 README 阶梯表行。
2. Stage A → B1 按序执行（人工 TUI 操作 + agent 侧证据收集），bug 流程随行。
3. B2/C 事后按 D4/D5 决定。
