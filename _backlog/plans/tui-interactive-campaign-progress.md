# 010 TUI 交互战役 · OpenSpec 落地进度计划

> 生成: 2026-08-21 | 状态: **进行中（Phase 0 已完成）**
> 用途: 以最少 openspec change 落地 [`tui-interactive-campaign.md`](tui-interactive-campaign.md)（v4）
> 与 [`../bugs/BUG-060-demo-tui-choice-option-unprojected.md`](../bugs/BUG-060-demo-tui-choice-option-unprojected.md)，
> 并全程 track 战役进展。
>
> **怎么用本文件**：完成一项就勾一项；每个 Phase 收尾在 §4 进展记录表加一行；
> Phase 状态改 §3 表头。证据细节进 handoff-010 / runbook 附录，本文件只记进度与判定。

## 1. 落地策略：为什么只需 1 个预规划 change

| 工作项 | 性质 | 落地载体 | 要不要 openspec change |
| --- | --- | --- | --- |
| Stage 0 文档校准（plan v4 / runbook / launcher / 阶梯表 / BUG-060 登记） | 文档/账本 | `_backlog/` | ❌ 无产品契约变化（已完成） |
| Stage A fixture smoke | 操作跑次 | runbook §2 + 战役记录 | ❌ |
| Stage B1 真人 HITL1 真实跑 | 操作跑次 | runbook §3 + handoff-010 | ❌ |
| **BUG-060 修复**（TUI typed OPTION 投影） | **代码 + 契约** | **openspec change（本计划唯一预规划）** | ✅ |
| Stage B2 CHOICE 专项 | 操作跑次（条件式） | runbook §4 | ❌（但前置 = BUG-060 change） |
| Stage C Gateway observer | 操作跑次（可选） | runbook §5 | ❌ |
| 战役中撞出的新 bug | 不可预规划 | `_backlog/bugs/` → 各自独立 change（004 先例） | ⚠️ 条件性，按需追加 |
| capability 精确归因（closed observation fact） | 已明确推迟 | 无（plan v4 收窄 #1） | ❌ 不在本落地范围 |

**结论：预规划 change = 1 个；战役执行本身 0 个 change。**

## 2. 唯一预规划 change 的设计要点（供 propose 时用）

- **change 名**: `fix-demo-tui-choice-option`（文件夹日期前缀按 propose 当天，
  惯例 `YYYY-MM-DD-<slug>`，见 `openspec/changes/archive/`）
- **触发**: BUG-060——`demo_tui.py::on_input_submitted()` 把 composer 输入一律
  构造为 text `AnswerRun`，而 hitl1 language CHOICE 轮要求
  `response_kind=option` + `option_id`（`run_experience.py:357-358`）；且该轮
  无 `accept_current_proposal` control，"Start proposal" 按钮不显示——CHOICE
  轮在 TUI 里是死路。
- **spec delta 目标**: 仅 `openspec/specs/research-demo-tui/spec.md`——现有
  文本已要求展示 "graph-owned advertised choices"（RED-001 区块），但缺
  "把当前广告 CHOICE 选项的选择派发为 typed OPTION `AnswerRun`" 的要求。
  新增/修改该 requirement（fixture 与 embedded-smoke 模式：CHOICE 轮渲染
  选项、选择派发为 `response_kind=option` + 该轮合法 `option_id`；TEXT 轮
  保持自由文本；不引入 route/profile admission 决策）。
- **不动的 spec**: `human-interaction-contract`——typed option 契约与
  `_prepare_intent` 校验已正常工作，问题纯在 presentation adapter 投影层
  （BUG-060 根因分析）。
- **primary causal owner**: demo TUI presentation adapter
  （`scripts/demo_tui.py`）；不下放 route/profile admission 给 TUI。
- **确定性回归**: fixture CHOICE 路径经 shared experience 的 TUI 测试
  （选项渲染 + typed OPTION 派发 + admission 接受），不依赖真实模型。
- **验证门**: `UV_OFFLINE=1 make verify`（应用完整门）。
- **技能路线**: `openspec-propose` 建 → `polish-openspec-change` 硬化 →
  `openspec-apply-change` 实施 → `openspec-archive-change` 归档。

## 3. Todolist（按序执行；Phase 3 与 Phase 1/2 无依赖可提前）

### Phase 0 — Stage 0 校准 ✅ 完成（2026-08-21）

- [x] plan v4 重写（消化 review，9 采纳 / 2 收窄）
- [x] runbook-010 重写（条件式修订脚本 / exact bundle / 证据限制）
- [x] RUN-010-TUI.command 同步重写（合法应答卡 + 唯一新增 bundle 绑定）
- [x] BUG-060 登记（P1）+ bugs/README + _fixed_bugs 编号权威 → BUG-061
- [x] _local_demo/README.md 阶梯表 010 行修正

### Phase 1 — Stage A：fixture TUI 已知形状 smoke ⬜ 未开始

- [x] 建 handoff-010（战役进行中记录，完结收口删除——004 先例）——`_backlog/_local_demo/handoff-010-tui-interactive.md`；agent 侧前置已过（textual 8.2.8 + entry-preflight EXIT=0）
- [ ] 用户跑 `make demo-tui-fixture`：Ready → StartRun → AwaitingInput(hitl1/text) → 回答 → Terminal completed → 退出无异常
- [ ] （可选）再跑一次验证 Cancel 分支
- [ ] 记录 UI 形状结论进 handoff-010（不声称 real cognition / CHOICE / 报告质量）

### Phase 2 — Stage B1：embedded 真人 HITL1 真实跑（战役主体）⬜ 未开始

- [ ] agent 侧：启动前 bundle 目录集合快照（runbook §3.0）
- [ ] 用户跑 `make demo-tui-embedded-smoke`：固定问题 + 条件式修订应答（runbook §3.1）
- [ ] 四步证据链记录：初始 proposal depth / 修订语句 / 修订后 depth / 显式确认
- [ ] agent 侧：exact bundle 绑定（唯一新增，否则记"证据未绑定"）
- [ ] PASS 判据 7 条逐条核对（runbook §3.4），结果记 handoff-010
- [ ] 撞茬按 `_backlog/bugs/` 登记（新 bug → 列入 §4 条件性 change 追踪）
- [ ] 与 003 对照观察表填写（runbook §3.6）

### Phase 3 — OpenSpec change：fix-demo-tui-choice-option（BUG-060）✅ 完成（2026-08-21）

- [x] `openspec-propose`：建 change（按 §2 设计要点；delta 只打 research-demo-tui）——`fix-demo-tui-choice-option`，validate 通过
- [x] `polish-openspec-change`：apply readiness 硬化（含确定性回归方案审定）——三 pass 完成，plan gate 全绿（RED-009 预留 + Focus Card + 三 seam 证据链）
- [x] `openspec-apply-change`：实施修复 + fixture CHOICE 路径确定性测试——TDD 红（3 集成 + 2 contract）→ 绿（18/18）；实现中固化两事实：hitl2 CHOICE 文本转发是受保护行为、Textual mount 异步 → 按钮组静态生成
- [x] `UV_OFFLINE=1 make verify` 全绿（fast 2641 + integration 261 + workflow 35；strict validate 通过；RED-009 已注册 req-registry）
- [x] BUG-060 状态更新（修复 change 关联）；`openspec-archive-change` 归档——delta 同步进主 spec（RED-009），closeout 六项检查全绿，归档为 `archive/2026-08-21-fix-demo-tui-choice-option`
- [x] BUG-060 归档（git mv → `_done/_fixed_bugs/`，三个 README 同步）

### Phase 4 — Stage B2：language CHOICE 专项（条件式，不在 010 PASS 范围）⬜ 未开始

> 前置：Phase 3 完成 **且** 战后仍决定覆盖（plan D5）。任一不满足 → 勾掉下面退出项收尾。

- [ ] 前置判定：执行 / 放弃（放弃则注明理由，Phase 直接关闭）
- [ ] unspecified-language 问题跑 `make demo-tui-embedded-smoke`，验证 TUI 只显示 `zh`/`en`
- [ ] typed OPTION 提交 + HITL1 admission 写入选定 output_language（bundle 证据）
- [ ] 不与 003 profile 对照混同的独立记录进 handoff-010

### Phase 5 — Stage C：Gateway observer 体验（可选）⬜ 未开始

> 前置：预写有限观察问题清单（不预写 = 不保留占位，直接关闭）。

- [ ] 预写观察问题清单（transport/presentation 差异；无本地 cancel；无 Primary User 产品验收声明）
- [ ] `make profile-dev PROFILE=demo` + `make demo-tui PROFILE=demo`，体验记录进 handoff-010
- [ ] Gateway/profile 侧坑单独报 bug（如有）

### Phase 6 — 战役收口 ⬜ 未开始

- [ ] 全部证据（exact bundle id / 四步链 / 对照表 / 观察点）折叠进 runbook-010 附录
- [ ] `_local_demo/README.md` 阶梯表 010 行补状态结论
- [ ] plan v4 标记"已执行"并注日期
- [ ] handoff-010 收口删除（004 先例）
- [ ] 本文件终检：全部 Phase 状态落定，§4 记录完整，标记 **完成**

## 4. 进展记录（append-only）

| 日期 | Phase | 事项 | 结果 |
| --- | --- | --- | --- |
| 2026-08-21 | 0 | Stage 0 五项校准（plan v4 / runbook / launcher / BUG-060 / 阶梯表） | ✅ 完成，复查无残留 |
| 2026-08-21 | — | 本进度计划创建；change 集收敛为 1 个预规划 + 条件性追加 | 📋 定稿 |
| 2026-08-21 | 3 | propose 完成：`fix-demo-tui-choice-option`（proposal/specs delta/design/tasks 4/4，validate ✅） | 📐 待 polish |
| 2026-08-21 | 3 | polish 完成：三 pass（RED-009 注册修正 + value==option_id 契约修正 + ReplayTransport 接受证据 + Focus Card）；plan gate 全绿 | ✅ ready for apply |
| 2026-08-21 | 3 | apply 完成：TDD 红→绿（集成 18/18 + contract 回放 2）；verify 全绿（fast 2641 + integration 261 + workflow 35） | ✅ 实施完毕 |
| 2026-08-21 | 3 | 归档完成：delta 同步主 spec（RED-009）、closeout 六项全绿、change → `archive/2026-08-21-fix-demo-tui-choice-option`、BUG-060 → `_done/_fixed_bugs/` | ✅ Phase 3 闭环 |

## 5. 条件性 change 追踪（战役撞出的 bug，按需追加行）

| bug | change 名 | 状态 |
| --- | --- | --- |
| BUG-060 | `fix-demo-tui-choice-option`（Phase 3） | ✅ 已修复并归档（2026-08-21） |
| （新 bug 填行） | | |
