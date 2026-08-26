# 020 TUI 交互战役（= 原 010 手动 TUI）· OpenSpec 落地进度计划

> ⚠️ **编号更新（2026-08-21）**：按 01x/02x 命名轴，本战役是 **020 手动 TUI**
> （runbook-020-tui-manual.md）；**010 = 自动 TUI 孪生**（runbook-010-tui-auto.md，
> BUG-061，入口 `make demo-tui-real-auto`）。下文"010"均指本战役的 020 内容。
>
> 生成: 2026-08-21 | 最近同步: 2026-08-25 | 状态: **进行中——Phase 0/1/3/4 完成
> （含 BUG-061 change 闭环归档）；战役主体 Stage B1 未跑**
> 用途: 以最少 openspec change 落地 [`tui-interactive-campaign.md`](tui-interactive-campaign.md)（v4）
> 与 [`../bugs/BUG-060-demo-tui-choice-option-unprojected.md`](../bugs/BUG-060-demo-tui-choice-option-unprojected.md)，
> 并全程 track 战役进展。
>
> **怎么用本文件**：完成一项就勾一项；每个 Phase 收尾在 §4 进展记录表加一行；
> Phase 状态改 §3 表头。证据细节进 handoff-020 / runbook 附录，本文件只记进度与判定。
>
> **2026-08-25 同步说明**：本文件原停在 08-21（Phase 3 闭环），漏记了此后
> 发生的 **010/020 拆分与双轨落地**（010 自动 TUI 代码/入口、020 手动 TUI 交互层
> 大扩展、01x/02x 交互原则）。本次同步折叠进 Phase 4，并把 §1「只 1 个预规划
> change」的结论修订为「2 个 change」，并已于 2026-08-25 全部闭环归档
> （BUG-060 `fix-demo-tui-choice-option`、BUG-061 `add-demo-tui-auto-entry`）。

## 1. 落地策略：从「1 个预规划 change」到「2 个」（08-25 修订）

| 工作项 | 性质 | 落地载体 | 要不要 openspec change |
| --- | --- | --- | --- |
| Stage 0 文档校准（plan v4 / runbook / launcher / 阶梯表 / BUG-060 登记） | 文档/账本 | `_backlog/` | ❌ 无产品契约变化（已完成） |
| Stage A fixture smoke | 操作跑次 | runbook §2 + 战役记录 | ❌ |
| Stage B1 真人 HITL1 真实跑 | 操作跑次 | runbook §3 + handoff-020 | ❌ |
| **BUG-060 修复**（TUI typed OPTION 投影） | **代码 + 契约** | **openspec change（已归档）** | ✅ `fix-demo-tui-choice-option` |
| **010/020 拆分 + 010 自动 TUI 入口**（BUG-061） | **代码 + 契约** | **openspec change（已归档）** | ✅ `add-demo-tui-auto-entry` |
| 020 手动 TUI 交互层扩展（侦察/流式/NLU/按钮/回显） | 代码 | 随各 feat commit（无独立 change） | ❌ 交互层呈现，无 route/profile 契约变化 |
| Stage B2 CHOICE 专项 | 操作跑次（条件式） | runbook §4 | ❌（但前置 = BUG-060 change，已满足） |
| Stage C Gateway observer | 操作跑次（可选） | runbook §5 | ❌ |
| 战役中撞出的新 bug | 不可预规划 | `_backlog/bugs/` → 各自独立 change（004 先例） | ⚠️ 条件性，按需追加 |
| capability 精确归因（closed observation fact） | 已明确推迟 | 无（plan v4 收窄 #1） | ❌ 不在本落地范围 |

**结论（08-25 修订）：预规划 change 从 1 个扩为 2 个，均已在 2026-08-25 闭环归档
——BUG-060（`fix-demo-tui-choice-option`）与 BUG-061（`add-demo-tui-auto-entry`）。**

## 2. 预规划 change 设计要点（供 propose 时用）

### 2.1 `fix-demo-tui-choice-option`（BUG-060，✅ 已闭环）

- **触发**: BUG-060——`demo_tui.py::on_input_submitted()` 把 composer 输入一律
  构造为 text `AnswerRun`，而 hitl1 language CHOICE 轮要求
  `response_kind=option` + `option_id`（`run_experience.py:357-358`）；且该轮
  无 `accept_current_proposal` control，"Start proposal" 按钮不显示——CHOICE
  轮在 TUI 里是死路。
- **primary causal owner**: demo TUI presentation adapter（`scripts/demo_tui.py`）。
- **落地**: 选项按钮组（`SupportedLanguageOption` 闭集静态生成）+ composer
  exact-match 派发 typed OPTION `AnswerRun(value=option_id, response_kind="option",
  option_id=option_id)`；TEXT 轮与 hitl2 CHOICE 文本转发不变。
- **结果**: 集成 4 + contract 回放 2 全绿；verify 全绿；RED-009 进主 spec；
  归档 `archive/2026-08-21-fix-demo-tui-choice-option/`；BUG-060 → `_done/_fixed_bugs/`。

### 2.2 `add-demo-tui-auto-entry`（BUG-061，✅ 已闭环 2026-08-25）

- **触发**: BUG-061——`scripts/demo_tui.py` 的 composer 提交永远构造
  `StartRun(question=value)`（`scripted=False`），无 `--auto`/`--scripted` 开关，
  TUI 一层无法复现 010 自动形态。
- **落地代码（已实现 + 测试 20 passed）**:
  - `scripts/demo_tui.py`: 新增 `--auto`（仅限 `--embedded-smoke`）；`_initialize`
    就绪后若 `mode == "embedded_smoke" and auto`，自动
    `_dispatch(StartRun(question=AUTO_QUESTION, scripted=True, profile_intent=None))`；
    固定问题 = 003 同款；banner 标注 `· auto`。
  - `Makefile`: 新增 `demo-tui-real-auto` target（010 自动入口）。
  - `tests/integration/test_demo_tui.py`: 新增 2 用例（auto 派发 scripted
    StartRun 且直达 Terminal；fixture+auto 仍保持交互）。
- **✅ 闭环（2026-08-25）**: propose（四件套）→ polish（两遍 pass + plan gate
  全绿，reservation RED-010）→ apply（核对已落地代码；补 argparse 拒绝路径
  测试 `test_tui_auto_flag_is_rejected_outside_embedded_smoke`；RED-010 登记
  `openspec/governance/req-registry.yaml`；`UV_OFFLINE=1 make verify` 全绿
  fast 2650 + integration 301[4 skipped] + workflow 35）→ archive（delta 同步
  进主 spec RED-010；closeout gate 通过；归档为
  `archive/2026-08-25-add-demo-tui-auto-entry/`）；BUG-061 →
  `_done/_fixed_bugs/`（编号权威 → BUG-062）。

## 3. Todolist（按序执行；Phase 3 与 Phase 1/2 无依赖可提前）

### Phase 0 — Stage 0 校准 ✅ 完成（2026-08-21）

- [x] plan v4 重写（消化 review，9 采纳 / 2 收窄）
- [x] runbook-010 重写（条件式修订脚本 / exact bundle / 证据限制）
- [x] RUN-010-TUI.command 同步重写（合法应答卡 + 唯一新增 bundle 绑定）
- [x] BUG-060 登记（P1）+ bugs/README + _fixed_bugs 编号权威 → BUG-061
- [x] _local_demo/README.md 阶梯表 010 行修正

### Phase 1 — Stage A：fixture TUI 已知形状 smoke ✅ 完成（2026-08-21）

- [x] 建 handoff-020（战役进行中记录，完结收口删除——004 先例）——`_backlog/_local_demo/handoff-020-tui-manual.md`；agent 侧前置已过（textual 8.2.8 + entry-preflight EXIT=0）
- [x] 用户跑 `make demo-tui-fixture`：Ready → StartRun → AwaitingInput(hitl1/text) → 回答 → Terminal completed → 退出无异常——经 `RUN-020.command` 选 1，6 个 bundle 全部 completed（详见 handoff-020 战况表）
- [ ] （可选）再跑一次验证 Cancel 分支（未跑，可选项，不阻塞）
- [x] 记录 UI 形状结论进 handoff-020（不声称 real cognition / CHOICE / 报告质量）

### Phase 2 — Stage B1：embedded 真人 HITL1 真实跑（战役主体）⬜ 未开始

> **这是整个 020 战役存在的意义，目前一个字都没跑。**

- [ ] agent 侧：启动前 bundle 目录集合快照（runbook §3.0）
- [ ] 用户跑 `make demo-tui-embedded-smoke`：侦察模式 → 触发研究 → 固定问题 + 条件式修订应答（runbook §3.0.5/§3.1）
- [ ] 四步证据链记录：初始 proposal depth / 修订语句 / 修订后 depth / 显式确认
- [ ] agent 侧：exact bundle 绑定（唯一新增，否则记"证据未绑定"）
- [ ] PASS 判据 7 条逐条核对（runbook §3.4），结果记 handoff-020
- [ ] 撞茬按 `_backlog/bugs/` 登记（新 bug → 列入 §5 条件性 change 追踪）
- [ ] 与 003 对照观察表填写（runbook §3.6）

### Phase 3 — OpenSpec change：fix-demo-tui-choice-option（BUG-060）✅ 完成（2026-08-21）

- [x] `openspec-propose`：建 change（按 §2.1 设计要点；delta 只打 research-demo-tui）——`fix-demo-tui-choice-option`，validate 通过
- [x] `polish-openspec-change`：apply readiness 硬化（含确定性回归方案审定）——三 pass 完成，plan gate 全绿（RED-009 预留 + Focus Card + 三 seam 证据链）
- [x] `openspec-apply-change`：实施修复 + fixture CHOICE 路径确定性测试——TDD 红（3 集成 + 2 contract）→ 绿（18/18）；实现中固化两事实：hitl2 CHOICE 文本转发是受保护行为、Textual mount 异步 → 按钮组静态生成
- [x] `UV_OFFLINE=1 make verify` 全绿（fast 2641 + integration 261 + workflow 35；strict validate 通过；RED-009 已注册 req-registry）
- [x] BUG-060 状态更新（修复 change 关联）；`openspec-archive-change` 归档——delta 同步进主 spec（RED-009），closeout 六项检查全绿，归档为 `archive/2026-08-21-fix-demo-tui-choice-option`
- [x] BUG-060 归档（git mv → `_done/_fixed_bugs/`，三个 README 同步）

### Phase 4 — 010/020 拆分与双轨落地（新增，非原计划 Stage）✅ 代码/入口落地（2026-08-21 ~ 08-22）

> 战役中途拆分：TUI 轴一分为二——**010 自动全跑**（真人零操作）与 **020 手动跑**
> （真人坐镇 HITL1）。以下是双轨的落地成果（代码/runbook/launcher/测试），
> 其中 **BUG-061 的 openspec change 已闭环**（见 §2.2）。

- [x] **拆分定名**：runbook-010-tui-auto.md + runbook-020-tui-manual.md +
  RUN-010.command + RUN-020.command；阶梯表 010/020 两行 + `#tui-010-020` 分割规则
- [x] **010 自动 TUI 入口（BUG-061 代码）**：`demo_tui.py --auto`（仅 embedded-smoke）
  + `Makefile demo-tui-real-auto` + 2 集成测试（20 passed）；runbook-010 + launcher
- [x] **010 体验底线**：实时进度播报（`live_progress_lines()` 读 events.jsonl）、
  Report 路径显示、中间 RichLog 可拷贝（双击全文 / Copy details / Option+拖拽 /
  `logs/tui-<pid>.log` 落盘）
- [x] **020 侦察循环**：启动进侦察模式、每轮研究结束自动回侦察；
  `环境`/`env`/`workspace`/`工作区` 输出 workspace 结构视图
- [x] **020 workspace inspect**：全局斜杠命令 `/ls` `/cat` `/inspect` `/clear`（研究中也可用，
  输出到独立查看面板）+ 自然语言只读工具（`list_workspace` / `read_workspace_file` /
  `inspect_bundle`）
- [x] **020 自然语言 HITL1**：短语映射（"深度: 快速概览" 等）+ 快捷修订按钮
  （深度/受众 4 按钮）+ 输入回显「你: …」+「已按你的输入修订…」确认 + 拒绝时具体指引
- [x] **020 流式交互**：聊天流式 + 滚动事件流 + 语义反馈（三阶段：收到/处理中/结果）
- [x] **01x/02x 交互原则定稿**：交互差异表 + API 依赖原则（01x 同步轮询 / 02x 流式+工具+文件读取，
  底层 graph/runtime/journal 共用同一套）
- [x] **BUG-061 openspec change `add-demo-tui-auto-entry`**：propose → polish →
  apply → archive 闭环（2026-08-25；见 §2.2）

### Phase 5 — Stage B2：language CHOICE 专项（条件式，不在 020 PASS 范围）⬜ 未开始

> 前置 (a) 已满足（BUG-060 修复 `fix-demo-tui-choice-option` 归档）；仍卡在
> (b)「B1 跑完 + 战后仍决定覆盖」。

- [ ] 前置判定：执行 / 放弃（放弃则注明理由，Phase 直接关闭）
- [ ] unspecified-language 问题跑 `make demo-tui-embedded-smoke`，验证 TUI 只显示 `zh`/`en`
- [ ] typed OPTION 提交 + HITL1 admission 写入选定 output_language（bundle 证据）
- [ ] 不与 003 profile 对照混同的独立记录进 handoff-020

### Phase 6 — Stage C：Gateway observer 体验（可选）⬜ 未开始

> 前置：预写有限观察问题清单（不预写 = 不保留占位，直接关闭）。

- [ ] 预写观察问题清单（transport/presentation 差异；无本地 cancel；无 Primary User 产品验收声明）
- [ ] `make profile-dev PROFILE=demo` + `make demo-tui PROFILE=demo`，体验记录进 handoff-020
- [ ] Gateway/profile 侧坑单独报 bug（如有）

### Phase 7 — 战役收口 ⬜ 未开始

- [x] BUG-061 change 闭环归档（`add-demo-tui-auto-entry` →
  `archive/2026-08-25-add-demo-tui-auto-entry/`），BUG-061 →
  `_done/_fixed_bugs/`（已做，2026-08-25）
- [ ] 全部证据（exact bundle id / 四步链 / 对照表 / 观察点）折叠进 runbook-020 附录
- [ ] `_local_demo/README.md` 阶梯表 010/020 行补状态结论
- [ ] plan v4 标记"已执行"并注日期
- [ ] handoff-020 收口删除（004 先例）
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
| 2026-08-21 | 1 | Stage A PASS：用户经 launcher 选 1 跑 fixture TUI，6 bundle 全 completed，hitl1 往返完整；"无输出"= fixture 无 report 的预期形态 | ✅ Phase 1 主体完成（Cancel 可选项未跑） |
| 2026-08-21 | 4 | 010/020 拆分：TUI 轴一分为二，runbook-010-tui-auto + runbook-020-tui-manual + RUN-010/020.command + 阶梯表两行 | ✅ 双轨定名落地 |
| 2026-08-21 | 4 | 010 自动 TUI 落地：`demo_tui.py --auto` + `make demo-tui-real-auto`（BUG-061 代码）+ 进度播报/报告路径/可拷贝 | ✅ 代码+入口+体验落地，change 待走 |
| 2026-08-21 | 4 | 020 手动 TUI 交互层：侦察循环 + workspace inspect（斜杠命令 + NLU 只读工具） | ✅ 落地 |
| 2026-08-22 | 4 | 020 交互层加强：自然语言 HITL1（短语映射/回显/intake）+ 快捷修订按钮 + 流式聊天/滚动事件流/语义反馈 | ✅ 落地 |
| 2026-08-22 | 4 | 01x/02x 交互差异表 + API 依赖原则定稿（观察者 vs 操作者，同步 vs 流式） | ✅ 原则定稿 |
| 2026-08-25 | — | 进度文件同步：折叠 010/020 拆分与双轨落地进 Phase 4；§1 change 结论 1→2 修订 | 📋 本版 |
| 2026-08-25 | 4 | BUG-061 change `add-demo-tui-auto-entry` 闭环：propose/polish/apply/archive；RED-010 登记 + 同步主 spec；`UV_OFFLINE=1 make verify` 全绿（fast 2650 + integration 301[4 skipped] + workflow 35）；BUG-061 → `_done/_fixed_bugs/`（编号权威 → BUG-062） | ✅ Phase 4 完全闭环 |

## 5. 条件性 change 追踪（战役撞出的 bug，按需追加行）

| bug | change 名 | 状态 |
| --- | --- | --- |
| BUG-060 | `fix-demo-tui-choice-option`（Phase 3） | ✅ 已修复并归档（2026-08-21） |
| BUG-061 | `add-demo-tui-auto-entry`（Phase 4） | ✅ 已修复并归档（2026-08-25） |
| （新 bug 填行） | | |
