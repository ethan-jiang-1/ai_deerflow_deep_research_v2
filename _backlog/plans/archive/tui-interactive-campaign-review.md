# TUI 交互战役计划审阅

> 类型: 审阅 / 分析 | 更新: 2026-08-20
> 审阅对象: [`tui-interactive-campaign.md`](tui-interactive-campaign.md)
> 结论: 010 的 HITL1 真人交互主线值得执行，但当前计划、runbook 与 launcher
> 对真实 HITL2、语言 CHOICE、证据归因和本次 Bundle 绑定存在事实偏差；在真实
> API 战役前应先校正。

## 1. 总体判断

010 的正确价值不是“给现有自动流程套一个 TUI”，而是首次用真人回答压测
非 scripted 的 HITL1 proposal 交互：真实 brief、自然语言 semantic intake、
修订后的 proposal 再展示、显式确认、最终 profile 发布，以及 TUI 对等待、失败、
取消和终态的呈现。

当前计划把几个相邻但不同的行为合并成了一条人工交互链：HITL1 proposal、
HITL1 language CHOICE、HITL2 route 和 TUI presentation。实际代码与 main specs
并不支持这种合并叙述。若不先拆开，Stage B 可能等待一个不会出现的 HITL2
prompt、完全绕过 CHOICE，却仍被误记为覆盖成功；启动或 preflight 失败时，
launcher 还可能把历史 Bundle 当成本次证据。

## 2. 必须纠正的事实

### 2.1 真实 HITL2 是自主 continuation，不是人工决策点

`openspec/specs/hitl2-node/spec.md` 明确规定：real HITL2 不使用
interrupt/resume，验证 Wave2 predecessor 后自主写 `proceed`；普通 route 名不得
呈现为用户决策。`graph/nodes/hitl2/node.py` 的非 scripted 分支同样直接调用
`recommend_hitl2_route()`，不会产生 `PendingResearchInterrupt`。

因此计划中的以下表述不成立：

- “hitl2 走真交互自主决策”；
- “hitl2 按预设选 continue”；
- 把 hitl2 交互内容与后续路由列为本战役的新找茬面。

010 应改成：真人只参与 HITL1；HITL2 是被观察的自主 continuation。非 scripted
只表示不会写 `hitl2_auto_proceed` 标记，不表示 HITL2 恢复为人工 interrupt。

### 2.2 固定英文问题不会触发 language CHOICE

`derive_comparison_intake_seed()` 对含 ASCII 字母的问题确定性选择
`request_language=en` 与 `output_language=en`。D2 的固定问题因此不会进入
HITL1 language CHOICE。

这与“010 覆盖 CHOICE 按钮联动”的目标冲突。二者应明确拆分：

- Stage B1 保留 003 英文短问题，验证真实 semantic revision 与 proposal
  confirmation；
- Stage B2 如确实需要覆盖 CHOICE，使用独立的 unspecified-language probe，
  不把它冒充为 003 对照 run。

### 2.3 当前 Demo TUI 不能提交 HITL1 所要求的 typed OPTION

`scripts/demo_tui.py::on_input_submitted()` 对 composer 的所有输入都构造默认
`AnswerRun(value=...)`，即 `response_kind=text`。但
`runtime/run_experience.py::_prepare_intent()` 对当前 HITL1 CHOICE 明确要求
`response_kind=option` 且 `option_id` 是当前广告的 `zh` 或 `en`；text 会以
`hitl1_language_answer_requires_option` 被拒绝。

同时，`Start proposal` 只在当前 prompt 暴露
`accept_current_proposal` visible control 时显示。language CHOICE 没有这个
control，所以按钮不会显示，也不能用它选择 English。runbook/launcher 中“点
Start proposal 或输入 English”的说明均不合法。

这是独立 bug 候选。若 Stage B2 仍在 010 范围内，应先登记 bug，并通过
OpenSpec change 修复 adapter 对当前 typed option 的投影与确定性测试，再进行
真人 CHOICE probe。

### 2.4 Fixture 是否交互已经是已知事实

fixture HITL1 adapter 始终发出一个 `mode=TEXT` interrupt；
`tests/integration/test_demo_tui.py::test_tui_fixture_route_completes_through_shared_experience`
也确定性证明 TUI 收到 `AwaitingInput`，回答后到达 completed terminal。

Stage A 不再是“跑了才知道是否交互”的考古项。它应被定义为已知形状的 UI
smoke：Ready -> StartRun -> AwaitingInput(hitl1/text) -> AnswerRun -> Terminal，
并可选验证 CancelRun 分支。它不证明 real semantic intake、language CHOICE 或
真实报告质量。

## 3. 验收证据需要重写

### 3.1 非空 profile 不能证明真人改变了结果

初始 proposal 是模型生成的。终态 profile 非空、非 degraded，只能证明一个
profile 被发布，不能证明真人回答改变了它。可靠证据链应为：

```text
初始可见 proposal
    -> 真人提出至少一个与初始值不同的修订
    -> 修订后的可见 proposal
    -> 真人选择当前 proposal 的显式确认 control
    -> request/profile.json 与 state.json 匹配该 proposal
```

固定应答可改为确定性的条件脚本：若初始 `depth` 不是 `quick_overview`，就要求
改为 `quick_overview`；否则改为 `deep_dive`。同时记录初始值、修订语句和修订后
值。这样既保留可复现性，也能证明 human-caused change。

“profile 字段来自真人回答”应收窄为：最终 proposal 经真人确认；指定字段由
真人提出的修订改变并经 graph admission 后进入最终 profile。其他未修改字段仍
可能来自初始模型 proposal。

### 3.2 Event Journal 不能精确归因 semantic-intake capability

当前 Journal 的 `model_tool` 事实保留 `phase=hitl1`、outcome、attempt 与
`call_ordinal`，但不保留 capability/builder ID。因而：

- `grep semantic_intake diagnostics/events.jsonl` 不能证明调用发生；
- HITL1 model-call 数只能作为辅助证据，不能单独区分 brief、brief repair、
  semantic intake 或 semantic repair；
- 若产品确实需要精确归因，应另行设计 closed observation fact，不能靠 runbook
  字符串推断。

010 本轮可用的证据是：修订前后 proposal、相关 HITL1 visit/resume、HITL1
model-tool ordinal、最终 `request/profile.json`、终态 State、report 与 citation
artifacts。对“具体是哪一种认知调用”保留证据限制说明。

### 3.3 必须绑定本次 exact Bundle

runbook 和 `RUN-010-TUI.command` 当前使用整个 demo workspace 中 mtime 最新的
Bundle。若 Stage B 在 Bundle 创建前失败，或另一个进程同时写入，它可能展示
历史 fixture/real Bundle，制造假阳性。

应优先使用本次 `AwaitingInput`/`Terminal` 返回的 exact `bundle_id`。若 launcher
暂时拿不到 typed result，应至少在启动前记录目录集合，退出后只接受本次新增且
唯一的 Bundle；零个或多个新增都必须报“证据未绑定”，不得退回历史 latest。

real DemoAdapter 为每次进程创建独立 trusted scope，但不会自动删除或归档旧
Bundle。“重跑后旧 bundle 自动归档”应从 runbook 和 launcher 删除。

## 4. 环境与产品边界校正

### 4.1 Embedded smoke 前置不是两个 key

`DemoAdapter.for_real()` 的安全 preflight 需要：

- 非空 `DEERFLOW_DEMO_MODEL` selector；
- 与 selector 匹配的模型 credential，例如 `DEEPSEEK_API_KEY`；
- `TAVILY_API_KEY`。

Makefile 从 `deep_research_harness/.env` 注入 embedded-smoke 环境。runbook 当前
`grep ../.env` 检查了不同位置，并会把 secret 值直接打印到终端。应删除这条
命令，使用 `make install` 准备依赖，并让现有 safe readiness/preflight 只报告
闭合的 missing category，不显示凭证内容。

### 4.2 Demo TUI 不是当前 Primary User 产品入口

`deep_research_harness/README.md` 把 Demo TUI 定义为 contributor/operator
visualizer，并明确不是 current Primary User TUI。当前产品路线是 Dedicated Agent
+ reflected `deep_research` tool。

Stage C 应称为“Demo TUI 的 default real Gateway observer route”，而不是“产品
默认真实形态”。它可观察 Gateway transport/presentation 差异，但不证明当前
Primary User 产品体验。

## 5. 建议的新阶梯

### Stage 0 - 战役校准

1. 校正 plan、runbook、launcher 的 HITL2、CHOICE、credential 与 Bundle 叙述。
2. 登记 Demo TUI typed OPTION 缺失 bug。
3. 若 010 必须覆盖 CHOICE，先完成对应 OpenSpec change 与确定性回归；否则把
   CHOICE 明确移出 010 PASS 范围。

### Stage A - Fixture TUI 确定性 smoke

按已知契约验证一次 HITL1 text interrupt 的开始、回答、完成和退出；可选另跑
Cancel。记录 UI 形状，不声称真实 cognition 或 report quality。

### Stage B1 - Embedded real HITL1 semantic campaign

使用 003 固定英文短问题：记录初始 proposal，提出一个必然不同的 bounded
revision，记录修订 proposal，显式确认，等待自主 HITL2 与后续图完成。验收 exact
Bundle 的 profile、State、report/citation artifacts 和受限 Journal 证据。

### Stage B2 - Language CHOICE 专项（条件式）

仅在 typed OPTION bug 修复且仍决定覆盖时执行。使用独立
unspecified-language 输入，验证 TUI 只显示 `zh`/`en`、提交 typed OPTION、HITL1
admission 写入选定 output language。该 run 不与 003 profile 对照混为一谈。

### Stage C - Gateway observer 体验（可选）

保留为 Demo TUI transport/presentation 观察，明确无本地 cancel、无 embedded
Bundle 发现假设、无 Primary User 产品验收声明。若执行，应预先写出有限的观察
问题；否则从本轮交付物删除占位。

## 6. 建议的 PASS 定义

Stage B1 只有同时满足以下条件才算通过：

1. exact Bundle 绑定唯一且来自本次 run；
2. 初始 proposal、真人 revision、修订 proposal、显式 confirmation 四步有记录；
3. 最终 `request/profile.json` 与 State 匹配修订后 proposal，且
   `degraded_profile=false`；
4. lifecycle 到达 `terminal_status=completed`，HITL2 作为自主 phase 经过而没有
   人工 prompt；
5. `final/report.md`、citation map 及必要 artifact 存在并通过与 003 相同层级的
   内容检查；
6. Journal/visit 证据只声明它实际能证明的事实，不用字符串搜索伪造 capability
   归因；
7. 任何 blocked/fault 都保留 exact Bundle 与闭合 failure category，并按 backlog
   bug 流程处理，不以“找到了 bug”为 PASS 替代端到端成功。

## 7. 落地关联

- 文档校正目标：`tui-interactive-campaign.md`、
  `_backlog/_local_demo/runbook-010-tui-interactive.md`、
  `RUN-010-TUI.command`、`_backlog/plans/README.md`。
- code bug 候选：Demo TUI CHOICE 输入未投影为当前 typed `AnswerRun` OPTION。
- 若修改 TUI/共享 interaction 行为：建立 OpenSpec change，primary causal owner
  应从 presentation adapter 与 shared typed interaction boundary 的实际问题中选定，
  不把 route 或 profile admission 下放给 TUI。
- 战役完成后：把真实 bundle id、有限证据、发现的 bugs 和未覆盖边界写入
  handoff/复盘；change 独立修复并验证，不在 runbook 中隐式改变产品契约。
