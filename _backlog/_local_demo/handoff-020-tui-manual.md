# Handoff: Mode 020 TUI 真人交互战役（= 原 010 手动 TUI）+ change `fix-demo-tui-choice-option`

> 生成: 2026-08-21 | 用途: 战役进行中新会话 pick up 后继续（Stage A/B1 跑次 / 茬处置 / 收口）
> 位置: 本文件在 `_backlog/_local_demo/`；设计文档在 `_backlog/plans/tui-interactive-campaign.md`（v4 消化版）；
> 进度追踪在 `_backlog/plans/tui-interactive-campaign-progress.md`；实施载体已归档 `openspec/changes/archive/2026-08-21-fix-demo-tui-choice-option/`
>
> **状态: 🟡 进行中**。已完成：Stage 0 校准（review 全消化）→ 唯一预规划 change
> `fix-demo-tui-choice-option` 闭环（BUG-060 修复 + RED-009 注册 + 归档）。
> 待办：**Stage A（你操作 fixture smoke）→ Stage B1（你操作 embedded 真跑，战役主体）**
> →（条件 B2 / 可选 C）→ 收口。

## 目标（一句话）

**在 TUI 里以真人 HITL1 交互跑通一次真实 Deep Research（真实 DeepSeek + 真实
Tavily），并找茬交互认知面**：固定 003 短问题 + 条件式修订应答（初始 depth 是
X 就改 Y）→ 四步证据链（初始 proposal / 修订语句 / 修订后 proposal / 显式确认）
→ exact bundle `terminal_status=completed` + `degraded_profile=false` + 真实
report。HITL2 是自主 continuation **不需要人**。PASS 判据 7 条见 runbook §3.4。

## 实施摘要（已完成部分，均有 commit/归档证据）

- **Stage 0 校准（2026-08-21，commit 前史）**：独立 review 九项事实主张全部
  代码核验成立并消化——plan v4 重写（hitl2 自主性 / CHOICE 拆 B2 / 条件式修订
  证据链 / exact bundle 绑定 / Journal 归因限制 / preflight 三要素）；runbook-010
  与 `RUN-020.command` 重写（合法应答卡 + 启动前后 bundle 目录集合 diff）；
  阶梯表 010 行修正。
- **BUG-060 修复（2026-08-21，commit `cd053d6`）**：change
  `fix-demo-tui-choice-option` 全流程（propose → polish 三 pass → apply TDD →
  归档）。要点：
  - `demo_tui.py`：选项按钮组（`SupportedLanguageOption` 闭集静态生成、按当前
    hitl1 CHOICE 广告切可见性）；按钮点击与 composer **exact-match**（精确等于
    广告 id 如 `zh`）都派发 typed OPTION
    `AnswerRun(value=option_id, response_kind="option", option_id=option_id)`；
    非匹配文本不派发；TEXT 轮与 hitl2 CHOICE 文本转发不变（受保护行为）。
  - 回归：集成 4 用例 + contract 回放 2 用例（派发 seam：typed OPTION → resume；
    text → `input.invalid_response` Fault）。verify 全绿（fast 2641 +
    integration 261 + workflow 35）。
  - RED-009 进主 spec；BUG-060 → `_done/_fixed_bugs/`。
  - **apply 中固化的事实**（后续跑次注意）：hitl2 CHOICE 轮自由文本转发是
    graph 侧校验的既有契约；hitl1 CHOICE 轮的 text 拒绝投影为闭合 Fault
    （`input.invalid_response`），不是 raise。

## 战役跑次战况（append-only，跑了就填）

| 尝试 | 阶段 | bundle / 证据 | 结果 | 判定 |
| --- | --- | --- | --- | --- |
| Stage A（2026-08-21 15:40-16:17，`RUN-020.command` 选 1） | A | fixture scope `s_At5E33X…` 6 个 bundle（15:40/15:55×2/15:59×2/16:17） | 全部 `terminal_status: completed`、`implementation_mode: fixture`；每次 hitl1 完整往返（4 事件）；图走完 final_delivery | ✅ PASS（交互面/启动/退出均正常；Cancel 分支未跑，可选项） |
| （待填：Stage B1 第 1 跑） | B1 | — | — | — |

> Stage A 观察备注：①"没跑出什么"= 预期形态——fixture 图 `final/` 为空
> （不产 report.md），终态只有 "Research complete" + bundle 信息，真实内容
> 属 B1；②每次 run 的 hitl1 首个 attempt 记 `failed` 后 retry completed——
> 这是 journal 对 interrupt 挂起-恢复的记账形态，非故障；③launcher fixture
> 分支提示"不产出真实 run bundle"措辞偏严（fixture bundle 实际写入同一
> demo workspace 的 fixture scope，只是非真实模型 run），不影响绑定逻辑
> （exact-bundle 绑定仅用于 real 模式）。

## 你要做的事（Stage A，现在就可以）

```bash
cd deep_research_harness && make demo-tui-fixture
```

（或仓库根双击 `RUN-020.command` 选 1。）预期形状：banner（fixture-graph
demo）→ composer 出示例问题 → 回车起 run → hitl1 TEXT 提示 → 随便答一句回车
→ Terminal completed → Ctrl-C/q 退出无异常。把"看到什么、有没有卡"报给我，
我记进战况表。（可选加跑一次中途 Cancel。）

## 撞茬处置

- 任何异常：保留现场描述 → 报我登记 `_backlog/bugs/`（下一号 BUG-061）；
- semantic intake 形状缺陷是预期高危（BUG-058/059 同类：真实模型 vs 确定性
  契约边界）——撞上算产出；
- 收尾纪律同 004：bug 修复走独立 change，战役记录折进 runbook 附录后本文件
  删除。
