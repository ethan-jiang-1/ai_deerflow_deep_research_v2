---
title: "010 - TUI Interactive Real Run (Human HITL)"
runbook_id: "010"
difficulty: "medium-hard"
mode: "real-interactive"
cost: "medium"
automation: "human-in-the-loop"
fixed_question: "What is one bounded fact about China's EV battery market in 2024?"
prerequisites:
  - "DEEPSEEK_API_KEY"
  - "TAVILY_API_KEY"
  - "demo-tui extra 已安装（uv sync --extra demo-tui）"
purpose: "以真人在 TUI 里交互（hitl1 多轮 profile 对话 + hitl2 自主决策）跑通一次真实 Deep Research；压 001-004 从未触达的交互认知面（semantic intake / CHOICE / TUI 渲染）并找茬。"
how_to_run: |
  # Stage A（零凭证，先决环境）
  cd deep_research_harness && make demo-tui-fixture
  # Stage B（本地凭证，真交互真实跑——用户本人操作 TUI）
  make demo-tui-embedded-smoke
expected_result: "final_delivery -> completed + bundle profile 字段来自真人回答（非 degraded）+ final/report.md 真实内容；hitl1 交互轮数与 semantic intake 调用记录在 events.jsonl"
non_goals:
  - "不是 Gateway observer 路径（Stage C 推迟为可选）。"
  - "不修改研究问题（control environment：固定问题 + 固定应答脚本）。"
  - "不做 bridge 挂起加固（Ctrl-C 重试，同 003/004 经验）。"
---

# 010 Runbook：TUI 真人交互跑（HITL 专项）

> **一键启动**：Finder 双击仓库根的 **`RUN-010-TUI.command`**（或终端里
> `bash RUN-010-TUI.command`）——自动开菜单选 Stage A/B、显示应答脚本提示卡、
> 在你眼前的终端窗口里起 TUI，退出后自动展示 bundle 位置 + 报告开头。
>
> **010 是什么**：`_backlog/_local_demo` 前四格全是 CLI 全自动；010 换轴——
> **真人坐在 TUI 里做 hitl1/hitl2 决策**。入口 `make demo-tui-embedded-smoke`
> 起本地全真实图（真实 DeepSeek + 真实 Tavily），问题由 composer 输入，
> hitl1 提 profile proposal、你用自然语言回答（真实模型 semantic intake
> 分类你的话）、hitl2 交互决策。001-004 的 auto 短路（scripted）全部不触发。
>
> **本 runbook 是"给用户的操作单"**：agent 负责环境与 bundle 侧证据收集，
> TUI 里的按键由你本人完成。

## 1. 前置检查（agent 侧）

```bash
cd deep_research_harness
uv sync --locked --extra operations --extra demo-real --extra demo-tui   # TUI 依赖
grep -E "DEEPSEEK_API_KEY|TAVILY_API_KEY" ../.env                         # 凭证在位
```

## 2. Stage A：fixture TUI 交互面验证（零凭证，分钟级）

```bash
make demo-tui-fixture
```

- TUI 起来后：看 banner（fixture-graph demo）、pipeline、composer；
- fixture 图若带交互步（composer 变可用/出现提示）→ 按提示走完；
  若全程无交互步 → 记录"fixture 无真交互"（考古结论，也算产出）；
- 退出（Ctrl-C 或 q）无异常即过。

**考古项（跑完记录）**：fixture 路径到底有没有 AwaitingInput；有则记下
交互轮数与内容来源（fixture 数据 vs 模型）。

## 3. Stage B：embedded-smoke TUI 真交互真实跑（战役主体，你操作）

```bash
cd deep_research_harness
make demo-tui-embedded-smoke
```

### 3.1 应答脚本（control environment：固定问题 + 固定应答）

**问题（composer 首次输入，原样粘贴）**：

```
What is one bounded fact about China's EV battery market in 2024?
```

**hitl1 各轮应答（最小轮数策略，D3）**——按 proposal 实际问的轮次依次用：

| 轮次 | TUI 上你看到什么 | 你做什么 |
| --- | --- | --- |
| 1（profile proposal） | proposal 概要 + composer 可用 | 输入：`depth: quick overview. cost: minimal. time: very quick.` 回车 |
| 2（如再问 refinement） | 更新后的 proposal | 输入：`looks good, confirm.` 回车；或直接点 **Start proposal** 按钮 |
| CHOICE（输出语言） | 选项列表（如 English/Chinese） | 点 **Start proposal**（= `accept_current_proposal`）选 English；或按提示输入选项 |
| hitl2（自主决策） | continue/stop 类决策 | 输入：`continue` 回车（按实际选项最小确认） |

- 原则：**每轮一个短句直取目标字段**；proposal 已含目标字段时优先用按钮确认。
- Cancel 按钮在 embedded 模式真实可用——本战役不用（除非要中止）。

### 3.2 等待与观察

- 起 run 后 pipeline 依次走 bootstrap → hitl1 → topic_planning → wave0 →
  wave1 → wave2_synthesis →（targeted_evidence）→ hitl2 → readiness →
  final_delivery；RichLog 滚动日志；
- 全程分钟级到十数分钟（真实模型 + 真实 web）；**不要合盖/断网**（004 教训）。

### 3.3 结束后验收（agent 侧）

```bash
cd deep_research_harness
# 最新 bundle 定位（demo scope）
B=$(ls -td .deep-research-demo-runs/workspace/deep-research/scopes/*/b_* | head -1)
python3 -c "
import json; s=json.load(open('$B/state.json'))
print('terminal:', s.get('terminal_status'))
print('profile:', {k:s.get(k) for k in ('research_depth','cost_tolerance','time_budget','output_language','degraded_profile')})
"
grep -c semantic_intake "$B/diagnostics/events.jsonl" 2>/dev/null || true
ls "$B/final/report.md" 2>/dev/null && echo REPORT_OK
```

**PASS 判据**：
1. `terminal_status: completed`；
2. profile 三字段（depth/cost/time）**非空且非 degraded**——这是与 003
   （auto minimal）的核心对照点：同样字段这次来自你的回答 + semantic
   intake 分类；
3. `final/report.md` 真实内容（非模板句）；
4. hitl1 交互轮数 ≥1（events 有 interrupt/resume 痕迹）。

### 3.4 与 003 的对照观察（战役观察点）

| 维度 | 003（auto minimal） | 010（真人交互） |
| --- | --- | --- |
| profile 来源 | scripted 三字段硬编码 | 你的回答 → semantic intake 分类 |
| degraded_profile | True | 期望 False（真人确认过） |
| hitl1 轮数 | 0（短路） | ≥1（interrupt 往返） |
| wave2 gate | 2 轮（minimal pair） | 看 profile 实际字段决定 |
| 时间 | ~2-3 分钟 | 更长（交互往返 + 模型分类调用） |

## 4. Stage C（可选，推迟——视 A/B 战况另行决定）

Gateway observer 路由（`profile-dev` + `make demo-tui PROFILE=demo`），
纯体验记录，不设 PASS/FAIL。此处只留占位，不展开。

## 5. 撞上问题怎么办

- **TUI 卡死/模型挂起**：Ctrl-C 退出 TUI（bundle 侧状态由 checkpoint 决定，
  不猜）；重跑 `make demo-tui-embedded-smoke`（新 bundle，旧的自动归档）。
- **semantic intake 报错/形状怪异**：截图或抄录 TUI 日志行 → 按
  `_backlog/bugs/` 流程登记（预期高危区：分类输出形状、CHOICE 校验、
  TUI 渲染 provider 失败）。
- **profile 不符预期**（如字段丢失/降级 unexpectedly）：保留 bundle + 记
  events.jsonl 相关行，报 bug。

## 6. 证据归档

- bundle id + `state.json` profile 片段 + report.md 首页 → 战役记录
  （handoff-010 或直接 runbook 附录）；
- hitl1 交互轮数 / semantic intake 调用数 / 各轮耗时 → 观察点数据；
- bug 按 `_backlog/bugs/` 流程，修复走 openspec change（004 先例）。
