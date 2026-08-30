# 020 TUI 交互战役（= 原 010 手动 TUI）· OpenSpec 落地进度计划

> ⚠️ **编号更新（2026-08-21）**：按 01x/02x 命名轴，本战役是 **020 手动 TUI**
> （runbook-020-tui-manual.md）；**010 = 自动 TUI 孪生**（runbook-010-tui-auto.md，
> BUG-061，入口 `make demo-tui-real-auto`）。下文"010"均指本战役的 020 内容。
>
> 生成: 2026-08-21 | 最近同步: 2026-08-29 | 状态: **进行中——Phase 0/1/3/4 完成
> （含 BUG-061 change 闭环归档）；Stage B1 环境就绪、待真人实跑**
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
>
> **三文件分工（2026-08-30 定盘）**：本文件 = **战役核心推进账本**（唯一活文件：
> 勾项 + §4 append-only 记录）；[`tui-interactive-campaign.md`](tui-interactive-campaign.md)
> = 计划 v4（战略权威，仅大决策点更新）；[`tui-interactive-campaign-review.md`](tui-interactive-campaign-review.md)
> = 已被 v4 全量消化的独立审阅（历史产物，**冻结**，不再更新）。

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

### Phase 2 — Stage B1：embedded 真人 HITL1 真实跑（战役主体）🟡 进行中

> **这是整个 020 战役存在的意义。环境已就绪，等待真人实跑一次。**

- [x] agent 侧环境就绪：三要素非空（`DEERFLOW_DEMO_MODEL`/`DEEPSEEK_API_KEY`/`TAVILY_API_KEY`，仅验非空不打值）+ `entry-preflight` EXIT=0 + textual 可导入
- [x] agent 侧：启动前 bundle 目录集合快照（runbook §3.0）——65 bundles，存 `/tmp/bundles_before_020.txt` + `_local_demo/.evidence/`
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
| 2026-08-29 | 2 | Stage B1 环境就绪：三要素非空 + `entry-preflight` EXIT=0 + textual 可导入；before 快照落盘（65 bundles → `/tmp/bundles_before_020.txt` + `.evidence/`） | 🟡 待真人实跑 |
| 2026-08-29 | 2 | B1 证据工具就绪：摸清 real bundle 证据形状（state.json schema5 `research_depth/degraded_profile/terminal_status`、request/profile.json schema2 `depth/audience/format`、events.jsonl hitl1 `model_tool` 无 capability / hitl2 自主 node 无 interrupt）；写 `verify_b1_pass.py`（7 条 PASS 的机械判据 1/3/4/5 + 2/6 支持证据），对历史 all_real bundle dry-run 通过，并捕获其 degenerate report 标记 | ✅ 工具可战 |
| 2026-08-30 | 2 | B1 推进前复核：三要素非空 + `entry-preflight` EXIT=0 + textual 8.2.8 可导入；before 快照仍有效（/tmp 与 .evidence 双份 65 = 当前 65，期间无新增）——环境就绪未漂移，直接进入真人实跑；三文件分工定盘（本文件 = 核心推进账本，review 冻结） | 🟡 待用户实跑（本会话即跑） |
| 2026-08-30 | 2 | B1 第 1 跑（`b_l_W3Z6…`）：hitl1 交互链路完整、planning+wave0+wave1 过、证据 2 条入库，wave2_synthesis 唯一模型调用挂 16m22s 被 bridge_wall_time 掐死（provider.timeout）**零重试** → readiness `synthesis_findings_unavailable` 终局 blocked；hitl2 自主经过✅。登记 **BUG-062**（P1）+ **BUG-063**（P2 挂起记账 mislabel） | ❌ blocked，三值待用户回报 |
| 2026-08-30 | 2 | B1 第 2 跑（`b_yFAvXIr8…`）：14:18 confirm 后跑到 wave1，14:23:45 网络断 → **TUI 进程树死亡**，bundle 遗弃 suspended（journal complete 53 事件）无恢复入口、safe-inspect 拒绝 → 登记 **BUG-064**（P1 UX：无 attach/resume）。两跑三 bug，B1 尚无 completed run；用户 hitl1 交互本身两跑均无障碍 | ❌ 孤儿，战况记录在 handoff-020 |
| 2026-08-30 | — | 老数据清理（用户指令，按 todo 纪律手工执行）：67 → **3 bundles**（23M→4.1M）。保留 = B1 两跑证据（BUG-062/063/064）+ 最新 003 时代 completed all_real（§3.6 对照 / verify_b1_pass.py 可测）+ `tui-78024.log`（BUG-064 现场）；删除 = 58-bundle fixture scope + 6 老 all_real scope + 08-30 前日志；**基线快照重建**（/tmp + .evidence 双份，=3），第 3 跑验收以此为新基线 | ✅ 清理完毕，B1 可续跑 |
| 2026-08-30 | 5 | **C1 `close-provider-timeout-budget-handback` 闭环**（BUG-062）：propose 四件套 → polish 三 pass（Focus Card 格式 + `_timeout_origin` 公开化 + R1/R3 预算执法当场取证：middleware.py:121-128 `AgentBudgetError(BUDGET_EXHAUSTED, MODEL_CALL_LIMIT)`）→ apply TDD（红 5 → 绿 49：`_is_provider_transient` 谓词 + 主/repair 调用点 `_invoke_with_provider_retry`；发现 domain 契约已禁"PROVIDER_TIMEOUT 观察无 origin"形态）→ closeout 六项全绿（含 @impl/@bug 标注行规修正）→ WSN-012 同步主 spec → 归档 `archive/2026-08-30-close-provider-timeout-budget-handback/`；verify 全绿 fast **2656** + integration 301[4 skipped] + workflow 35 | ✅ C1 完全闭环，BUG-062 → `_done/_fixed_bugs/`（编号权威 → BUG-065） |
| 2026-08-30 | 5 | **C2 `add-suspended-run-recovery` 闭环**（BUG-064+063）：propose 四件套 + polish（posture 闭集值修正 + human-interaction-integrity 补列）→ apply：journal 挂起分类（`observed_run` 认 GraphInterrupt，outcome=suspended）、orphan `legal_next_action=RESUME` + `BundleGraphExecutor.continue_run`（lease+checkpoint `ainvoke(None)` 无伪造应答）+ `BundleControl._resume` 孤儿分支 + TUI attach 卡片（扫描/卡片/继续/查看/新跑，`ContinueRun` intent）；**apply 取证两项**：诊断对非 terminal 本已可用（15:05 拒绝=活持有者锁，RWB-009 定性契约锁）；run 2 实为冻结 69 分钟后自愈完成（BUG-064 证据注记已修）→ closeout 六项全绿 → REG-023/REJ-011/RWB-009/RED-011 同步四主 spec → 归档 `archive/2026-08-30-add-suspended-run-recovery/`；verify 全绿 exit 0 | ✅ C2 完全闭环，BUG-063/064 → `_done/_fixed_bugs/`（编号权威 → BUG-066） |

## 5. 条件性 change 追踪（战役撞出的 bug，按需追加行）

| bug | change 名 | 状态 |
| --- | --- | --- |
| BUG-060 | `fix-demo-tui-choice-option`（Phase 3） | ✅ 已修复并归档（2026-08-21） |
| BUG-061 | `add-demo-tui-auto-entry`（Phase 4） | ✅ 已修复并归档（2026-08-25） |
| BUG-062 | **C1 `close-provider-timeout-budget-handback`** | ✅ 已修复并归档（2026-08-30：propose → polish 三 pass → apply TDD 6 用例 → verify 全绿 fast 2656 + integration 301[4 skipped] + workflow 35；WSN-012 进主 spec；BUG-062 → `_done/_fixed_bugs/`） |
| BUG-063 | **并入 C2** `add-suspended-run-recovery` | ✅ 已修复并归档（2026-08-30） |
| BUG-064 | **C2 `add-suspended-run-recovery`**（含 063） | ✅ 已修复并归档（2026-08-30） |
| （新 bug 填行） | | |

> **分组决议（2026-08-30）**：三 bug 收敛为 **2 个 change**（用户要求少量）。
> C1 = 062（engine/graph：wall-time 超时补进 BUG-050 budget-handback 机制，战役
> 关键路径先行）；C2 = 064+063（domain/runtime/TUI："suspension 是一等可恢复状态"
> ——attach/resume + safe-inspect 放宽 + journal 挂起标签，同一契约同一 writer 族）。
> 详见 handoff-020 与当日讨论记录。
