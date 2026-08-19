# Plan: Mode 004 hard real-auto 默认意图跑通（比较题找茬，不污染产品逻辑）

> 类型: 设计 | 更新: 2026-08-19 | 状态: 最终共识（v2，决策点 D1-D4 已收敛）

## 背景

- 004 = README 阶梯的最后一格：`runbook-004-hard-real-auto.md`（待建）、花（多）、
  真机全自动、固定问题 `Compare China and US EV battery market in 2024.`、
  定位"最难：真机全自动跑，专门用来找茬"。
- 003 战役（minimal 意图跑通）已完结：`profile_intent` 声明机制、gate 预算解析、
  must_answer 修复、wave2/targeted 归一化、honest degraded delivery
  （BUG-044..057）全部落地归档。004 全部继承，无需重建。
- 003 刻意回避的部分——多 topic planner、多 work unit wave、wave2 默认预算、
  真实 final layout（多结论）——正是 004 要压的路径。**004 与 003 构成对照：
  003 测 minimal 意图下的真实链路；004 测默认意图（None）下的真实链路。**

## 现实约束（调研结论，2026-08-19，全部代码证据）

1. **意图类型是闭合的**：`runtime/non_interactive.py` 的
   `profile_intent: Literal["minimal"] | None`。003 plan 已决策不做空洞的
   `standard` 值（欠考虑 #2：与 absent 等价）。→ **004 = None（不声明）即产品
   默认路径，无需动产品类型。**
2. **入口硬编码了 minimal**：`scripts/demo_real.py:493` 的 embedded smoke 分支
   `profile_intent="minimal" if scripted else None`。004 要 scripted + None →
   入口需要参数化（operator 面，非产品逻辑）。
3. **Gateway 自动路线不存在**：`demo_real.py:410-412` Gateway 分支显式拒绝
   `--scripted`（"自动策略仅属于 embedded smoke"）。→ 004 入口定为
   embedded smoke（`make demo-real-scripted`，同 003）；Gateway 非交互自动化
   是独立产品特性，不在本 plan 范围。README 004 行的"入口待定"就此收口。
4. **比较题 seed 提取能过 fail-closed 门，但结果跛脚**（沙盘实测，
   2026-08-19）：`derive_comparison_intake_seed("Compare China and US EV
   battery market in 2024.")` → `comparison_required=True`、
   `subjects=('China', 'US EV battery market in 2024.')`、`output_language=en`。
   auto 分支不会 blocked（subjects 非空），但懒惰正则
   （`profile.py:121-124`：lazy first + greedy second）让第一个 subject 只有
   "China"，第二个吞掉整个半句（含句号）。这个跛脚对会流入 planner 上下文
   （`topic_planning/prompts.py:89,242`）。**这是 004 尚未开跑就找到的第一根茬**
   （处置见决策点 D2）。
5. **None 意图下的规模**：auto profile 为 degraded 空字段（depth/cost/time 缺）
   → `single_topic=False` → planner 自由拆 1-8 topics（`MAX_TOPICS=8`，
   `topics.py:19`；prompt 要求 `1-{MAX_TOPICS} entries`，每个 topic 绑定
   must_answer，全题只有 1 条=比较题本身）。比较题大概率拆 2-5 topics
   （China 市场 / US 市场 / 对比维度…），最坏 8。
6. **wave2 gate 预算是 1 轮**：`real_gates.py:203-210` 预算解析器只在
   `cost_tolerance==minimal and time_budget==very_quick` 时给 2；004（None →
   字段空）得 default 1。比较题天然多 gap → 大概率 1 轮耗尽 → **首次降级
   degraded pass + Uncertainties 披露**（BUG-050/053/054 机制，预期路径而非
   失败）。
7. **readiness/final 预算从未被真实负载压过**：003 按"实证驱动"保持现状
   （欠考虑 #3：只放宽了有实测 exhausted 证据的 wave2）。004 多 topic 多结论
   会第一次真实压 final_delivery 的模型 layout 路径（003 的 ≤1 结论确定性
   layout 免模型捷径不会触发）和 readiness critic 的负载。撞 exhausted 按
   bug 流程实证放宽——这正是找茬的产出。
8. **模型挂起风险继承**（003 已知：DeepSeek SDK 偶发阻塞 ainvoke，asyncio.timeout
   无法中断）：Ctrl-C 重试，bridge 加固仍是独立事项。
9. **soft_bundle 004 接线点**（全部照抄 003 模式，operator 面）：
   `MODE_QUESTIONS` 加 004 固定问题、`cmd_run` 加 004 分支（委托
   `make demo-real-scripted` + 显式 `--profile-intent none`）、verify 的
   report 必需集合 `{002,003}` → 加 004、inspect 委托集合（`soft_bundle.py:568`）
   → 加 004。REQUIRED_TRACE（9 阶段）不变。
10. **成本/时长**：003（单 topic）实测几分钟到十几分钟；004 若 2-5 topics，
    每 wave 相应 work unit 数 ×（含 repair 重跑），预期显著高于 003（数倍），
    README 阶梯已标注花（多）。护栏：MAX_TOPICS=8 是产品界；跑飞 Ctrl-C 重来。

## 方案（v1：入口传参 + operator 接线，产品逻辑零预改）

### 原则（继承 003 的铁律）

- **产品逻辑零预改**：004 不为跑通预改任何产品默认。撞出的问题按
  `_backlog` bug 流程实证驱动修（这是 004 的产出，不是前置条件）。
- **004 只是传参（不传）**：入口显式声明"不声明意图"（`--profile-intent none`
   → policy 不含 `profile_intent` 键 = 产品默认路径）。测的就是默认意图下的
  真实链路：planner 自由拆题、真实 worker 预算、wave2 gate 默认 1 轮、
  真实 final layout。
- **范围诚实**：004 验证非交互 operator 路径（embedded smoke）在默认意图 +
  比较题下的真实性；不声称覆盖 Gateway 交互路径（那是未来 010 的事）。

### A. 入口参数化（operator 面）

- `demo_real.py` 加 `--profile-intent {minimal,none}`（默认 `minimal`）：
  - `minimal` → 现行为（`profile_intent="minimal"`），**003 路径字节级不变**；
  - `none` → 不设（None），policy 不含该键。
- embedded smoke 的硬编码改为读该参数。命名与 `non_interactive_policy.profile_intent`
  字段名对齐；与 Gateway 的 `--profile`（运行 profile 名）语义不同，runbook
  注明区别。
- 命名备选：`--research-intent`。倾向前者（与字段名一致）。

### B. soft-bundle mode 004（operator 面，003 模式复制）

- `MODE_QUESTIONS["004"] = "Compare China and US EV battery market in 2024."`
- `cmd_run` 004 分支：`make demo-real-scripted DEMO_ARGS='--question "<固定问题>" --profile-intent none'`，
  绑定/退出码语义照抄 003（解析 bundle id、非零退出但 bundle 可解析仍绑定）。
- verify：`{002,003}` → `{002,003,004}` 要求 `final/report.md`；inspect 委托
  集合同步加 004。

### C. runbook-004 + README 阶梯收口

- `_backlog/_local_demo/runbook-004-hard-real-auto.md`：前置（同 003 的 .env
  三变量 + 网络）、步骤（create/run/status/inspect/phases/verify）、验收语义
  （见下）、模型挂起处理、bug 流程指引。
- README 004 行更新：入口定为 embedded smoke（`soft-bundle run --mode 004`），
  删"入口待定"；"可能是 Gateway 自动路线"改为"Gateway 非交互自动化是独立
  产品特性，不在 001~004 内"。

### 产品逻辑：零改动（实证驱动例外）

真实跑撞出的缺陷（预期见风险表）按 bug 流程：BUG 登记 → 定位 → 实证修复
→ 回归。004 的成功标准包含"把茬找出来并记录"，不包含"零茬跑过"。

## 验收语义（004 与 003 的对照）

| 维度 | 003（minimal） | 004（默认 None） |
| --- | --- | --- |
| 意图 | 声明 minimal → 单 topic、gate 2 轮 | 不声明 → planner 自由 1-8 topics、gate 1 轮 |
| work unit | 每 wave 初始恰 1 个 | 每 topic 每 wave ≥1 个（观察并记录实际数，不硬断言） |
| 报告 | 单事实 + claim-citation | **真实比较内容：China 与 US 两市场都必须覆盖** + claim-citation + 真实 URL |
| honest gap | 降级 pass + 披露 | 同（大概率 1 轮即耗尽降级——预期路径） |
| RESULT | PASS | PASS（含降级 pass）；blocked/崩图 → bug 流程记录 |

补充验收点：

- `final/report.md` 必须存在且为真实比较内容（两个市场都有事实性陈述与引用，
  不是只写一边）。
- topics 观察：记录 planner 实际拆题数与 scope（验收"每个 must-answer 被覆盖"
  的产品契约，不断言具体数量）。
- 跛脚 comparison_subjects 的实际影响：观察 planner 拆题是否被
  `('China', 'US EV battery market in 2024.')` 带偏（如只研究 China）——
  带偏即 D2 决策的实证输入。

## 风险 / 取舍

- [R1 跛脚 comparison_subjects 带偏 planner] → 首跑观察；带偏按 bug 流程修
  正则（对称提取，如两个市场短语各自成对）。不预修：无下游伤害证据，且
  任意自然语言的对称提取是开放问题，预修易过度工程。
- [R2 规模/费用失控（最坏 8 topics × 多轮 repair）] → README 已标注花（多）；
  runbook 给预期区间（常态 2-5 topics）；Ctrl-C 重来；usage_tokens/
  budget_operands 观测（003 已就位）用于事后核对。
- [R3 wave2 预算 1 轮即耗尽] → 首次降级 pass + Uncertainties 披露是预期
  路径（非失败）；"降级后再次耗尽"才 blocked（继承 003 语义）。
- [R4 final_delivery 模型 layout 首次真实受压] → BUG-055 的降级路径
  （plan-order layout 带发布 completed）是护栏；撞出新形状按 bug 流程。
- [R5 模型挂起] → Ctrl-C 重试（继承 003）。
- [R6 readiness/final 预算 exhausted 首现] → 按 bug 流程实证放宽（003 留的
  口子，004 正好补实证）。

## 决策点（已收敛，2026-08-19）

- **D1 意图 = None（不声明，默认产品路径）** ✅ 用户确认。备选（新增
  `comparison` 意图值）否决：003 已决策不做空洞 standard 值；为 004 造意图值
  重蹈 v1"为测试改产品"覆辙；默认路径才是找茬对象。
- **D2 跛脚 subjects = 先跑观察** ✅ 用户确认。首跑观察 planner 是否被
  `('China', 'US EV battery market in 2024.')` 带偏；带偏按 bug 流程修正则
  （实证驱动，无下游伤害证据不预修）。
- **D3 入口 flag = `--profile-intent {minimal,none}`** ✅ 用户确认。与
  `non_interactive_policy.profile_intent` 字段名对齐；默认 minimal（003 行为
  不变），004 传 none；runbook 注明与 Gateway `--profile` 的语义区别。
- **D4 003 回归口径 = 双保险** ✅ 默认接受。contract 测试钉死"默认=minimal"
  （003 路径不变）+ 收尾阶段真实 003 复跑一次确认。

## 实施顺序

1. **A**：`demo_real.py` `--profile-intent` 参数（默认 minimal）+ embedded
   smoke 硬编码改读参数；测试：默认=minimal（003 不变）、`none`=不设。
2. **B**：soft-bundle mode 004 接线 + `tests/contract/test_soft_bundle_cli.py`
   004 用例（绑定/verify/inspect）。
3. **C**：runbook-004 + README 阶梯行。
4. **回归**：全量测试 + ruff；002 零成本回归；003 contract 回归。
5. **真实 004 首跑**：跑通或按 bug 流程记录茬（含 R1 观察点）。
6. **茬的处置**：实证修复（走 bug 流程）→ 复跑至 PASS。
7. **收尾**：真实 003 复跑确认入口参数化无回归（D4）→ 归档 change →
   handoff-004 → plan 关闭。

## 验证方式

- 确定性：`tests/contract/test_demo_commands.py`（profile-intent 参数两档）、
  `tests/contract/test_soft_bundle_cli.py`（mode 004 绑定/verify/inspect）、
  既有 non_interactive 形状测试不回归（None 路径本就存在）。
- 端到端：002 零成本回归；003 contract + 真实复跑；真实 004（PASS + 双市场
  真实比较内容 + gap 披露）。

## 与 OpenSpec 的关系

- 本 plan 是思考文档，收敛定稿后实施走 `openspec/changes/hard-real-auto/`
  （proposal/specs/design/tasks 按本 plan 对齐）。改动面预计集中在
  demo-pipeline / soft-bundle-session-cli 两个 capability 的 delta +
  runbook/README 文档；产品 src 改动仅 `scripts/demo_real.py` 与
  `scripts/soft_bundle.py`（operator 面）。
