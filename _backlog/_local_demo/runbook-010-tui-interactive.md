---
title: "010 - TUI Interactive Real Run (Human HITL1)"
runbook_id: "010"
difficulty: "medium-hard"
mode: "real-interactive"
cost: "medium"
automation: "human-in-the-loop"
fixed_question: "What is one bounded fact about China's EV battery market in 2024?"
prerequisites:
  - "DEERFLOW_DEMO_MODEL（非空模型 selector）"
  - "与 selector 匹配的模型凭证（如 DEEPSEEK_API_KEY）"
  - "TAVILY_API_KEY"
  - "demo-tui extra 已安装（make install）"
purpose: "以真人在 TUI 里做 HITL1 交互（profile proposal 修订 + 显式确认，semantic intake 真模型分类自由文本）跑通一次真实 Deep Research；HITL2 是被观察的自主 continuation，无人工决策。压 001-004 从未触达的交互认知面。"
how_to_run: |
  # Stage A（零凭证，已知形状 UI smoke）
  cd deep_research_harness && make demo-tui-fixture
  # Stage B1（本地凭证，真交互真实跑——用户本人操作 TUI）
  make demo-tui-embedded-smoke
expected_result: "exact bundle（启动前记录目录集合、退出后唯一新增）+ 四步证据链（初始 proposal → 真人必然不同的修订 → 修订后 proposal → 显式确认）+ request/profile.json 与 State 匹配修订后 proposal 且 degraded_profile=false + terminal_status=completed + final/report.md 真实内容。HITL2 作为自主 phase 经过、无人工 prompt。"
non_goals:
  - "不做 language CHOICE 覆盖（英文固定问题确定性 en，不触发 CHOICE；CHOICE 专项是条件性 B2，前置 BUG-060 修复）。"
  - "不做 HITL2 人工决策（真实 HITL2 是自主 continuation，不产生 prompt，不输入 continue）。"
  - "不是 Gateway observer 路径（Stage C 可选，另见）。"
  - "不修改研究问题（control environment：固定问题 + 条件式应答脚本）。"
  - "不做 capability 精确归因（Journal model_tool fact 无 capability 字段，见 §4.3 证据限制）。"
---

# 010 Runbook：TUI 真人交互跑（HITL1 专项）

> **一键启动**：Finder 双击仓库根的 **`RUN-010-TUI.command`**（或终端里
> `bash RUN-010-TUI.command`）——选 Stage A/B1、显示应答脚本提示卡、在眼前
> 的终端窗口起 TUI，退出后按 exact-bundle 绑定规则展示证据位置。
>
> **010 是什么**：`_backlog/_local_demo` 前四格全是 CLI 全自动；010 换轴——
> **真人坐在 TUI 里做 HITL1 决策**。入口 `make demo-tui-embedded-smoke`
> 起本地全真实图（真实模型 + 真实 Tavily），问题由 composer 输入，hitl1
> 提 profile proposal、你用自由文本修订（真实模型 semantic intake 分类你的
> 话）、修订后显式确认。**HITL2 不需要你**：它是自主 continuation，作为
> 被观察的 phase 自动经过。001-004 的 auto 短路（scripted）全部不触发。
>
> **本 runbook 是"给用户的操作单"**：agent 负责环境与 bundle 侧证据收集，
> TUI 里的按键由你本人完成。

## 1. 前置检查（agent 侧）

```bash
cd deep_research_harness
make install   # uv sync --locked --extra operations --extra demo-tui --extra demo-real
```

凭证**不做**终端检查（不打 secret）。embedded-smoke 需要三要素：
非空 `DEERFLOW_DEMO_MODEL` selector + 与 selector 匹配的模型凭证（如
`DEEPSEEK_API_KEY`）+ `TAVILY_API_KEY`（`_demo_core.py::
validate_real_demo_prerequisites`）。TUI 启动时自带 safe preflight，只报告
闭合的 missing category，不显示凭证内容——缺什么它会告诉你。

## 2. Stage A：fixture TUI 已知形状 smoke（零凭证，分钟级）

```bash
make demo-tui-fixture
```

fixture 图**已知**发出一个 `mode=TEXT` 的 hitl1 interrupt（集成测试
`test_tui_fixture_route_completes_through_shared_experience` 确定性证明），
所以这是已知形状的 UI smoke，不是考古：

- 验证形状：banner（fixture-graph demo）→ pipeline → composer 可用 →
  按 §3.1 轮 1 方式回答 → 到达 completed terminal → 退出（Ctrl-C 或 q）
  无异常；
- 可选另跑一次，中途用 Cancel 验证取消分支；
- **不声称**：本阶段不证明 real semantic intake、language CHOICE 或真实
  报告质量。

## 3. Stage B1：embedded-smoke TUI 真交互真实跑（战役主体，你操作）

### 3.0 启动前：记录 bundle 目录集合（exact-bundle 绑定，agent 侧）

```bash
cd deep_research_harness
BROOT=.deep-research-demo-runs/workspace/deep-research/scopes
ls -d $BROOT/*/b_* 2>/dev/null | sort > /tmp/bundles_before_010.txt
make demo-tui-embedded-smoke
```

### 3.1 应答脚本（control environment：固定问题 + 条件式修订）

**问题（composer 首次输入，原样粘贴）**：

```
What is one bounded fact about China's EV battery market in 2024?
```

**hitl1 应答（条件式修订——必然不同于初始值，可复现且可证明
human-caused change）**：

| 轮次 | TUI 上你看到什么 | 你做什么 |
| --- | --- | --- |
| 1（profile proposal） | 初始 proposal（记下 `depth` 字段值） | 若 depth **不是** `quick_overview` → 输入 `depth: quick overview.` 回车；若**已是** `quick_overview` → 输入 `depth: deep dive.` 回车 |
| 2（refinement，如出现） | 修订后的 proposal（记下 depth 值） | 目标达成 → 点 **Start proposal** 按钮显式确认；未达成 → 再一句短修订，直到 depth = 目标值后确认 |

- **记录三值**（战役证据，抄进记录）：初始 proposal 的 depth / 你的修订
  语句 / 修订后 proposal 的 depth。三者构成 human-caused change 的前两步。
- **没有 CHOICE 轮**：英文固定问题确定性推导 `en`（`derive_comparison_intake_seed`），
  语言 CHOICE interrupt 不会出现。若真的出现语言选项——这是偏离预期的
  发现，照实记录（该轮现为可作答：选项按钮或 composer 精确输入 `zh`/`en`
  ——BUG-060 已修复，见 §6）。
- **没有 hitl2 人工轮**：HITL2 是自主 continuation，不产生 prompt；若 TUI
  停在一个 hitl2 决策输入上等待——同样是偏离预期，照实记录。
- Cancel 按钮在 embedded 模式真实可用——本战役不用（除非要中止）。

### 3.2 等待与观察

- 起 run 后 pipeline 依次走 bootstrap → hitl1 → topic_planning → wave0 →
  wave1 → wave2_synthesis →（targeted_evidence）→ **hitl2（自主经过，无需
  输入）** → readiness → final_delivery；RichLog 滚动日志；
- 观察点（找茬面）：hitl1 semantic intake 对你自由文本的分类形状、多轮
  refinement 与 Start proposal 按钮联动、hitl2 自主 phase 的渲染与耗时
  叙事、provider 失败呈现、长 run 下 RichLog 行为；
- 全程分钟级到十数分钟（真实模型 + 真实 web）；**不要合盖/断网**（004 教训）。

### 3.3 结束后验收（agent 侧）

**第一步：exact bundle 绑定**（不回退 mtime-latest）：

```bash
cd deep_research_harness
BROOT=.deep-research-demo-runs/workspace/deep-research/scopes
ls -d $BROOT/*/b_* 2>/dev/null | sort > /tmp/bundles_after_010.txt
NEW=$(comm -13 /tmp/bundles_before_010.txt /tmp/bundles_after_010.txt)
COUNT=$(echo "$NEW" | grep -c . || true)
if [ "$COUNT" -ne 1 ]; then
  echo "证据未绑定：新增 bundle 数 = $COUNT（启动前失败或并发写入）——不得使用历史 bundle"
else
  B=$(echo "$NEW")
  echo "本次 bundle: $B"
fi
```

**第二步：bundle 内容检查**：

```bash
python3 -c "
import json; s=json.load(open('$B/state.json'))
print('terminal:', s.get('terminal_status'))
print('profile:', {k:s.get(k) for k in ('research_depth','cost_tolerance','time_budget','output_language','degraded_profile')})
"
ls "$B/request/profile.json" 2>/dev/null && echo PROFILE_ARTIFACT_OK
ls "$B/final/report.md" 2>/dev/null && echo REPORT_OK
```

### 3.4 PASS 判据（全部满足才算过）

1. exact bundle 绑定唯一且来自本次 run（§3.3 第一步）；
2. 四步证据链完整：初始 proposal 值 / 真人修订语句 / 修订后 proposal 值 /
   显式确认（Start proposal）都有记录；
3. `request/profile.json` 与 `state.json` 匹配修订后 proposal，且
   `degraded_profile=false`；
4. `terminal_status=completed`，HITL2 作为自主 phase 经过、无人工 prompt；
5. `final/report.md` 真实内容（非模板句，与 003 同层级内容检查）；
6. Journal 证据只声明实际能证明的事实（§3.5）；
7. 撞上 blocked/fault：保留 exact bundle 与闭合 failure category，按
   `_backlog/bugs/` 流程处理——**发现 bug 不替代端到端成功作为 PASS**。

### 3.5 Journal 证据限制（不得伪归因）

model_tool fact 只含 phase/outcome/attempt_id/call_ordinal，**没有
capability 字段**——`grep semantic_intake events.jsonl` 不能证明 semantic
intake 被调用。可用证据：修订前后 proposal（TUI 侧记录）、HITL1
visit/resume 事件、HITL1 model-tool ordinal（辅助）、最终
`request/profile.json`、终态 State、report/citation artifacts。对"具体
是哪一种认知调用（brief/intake/repair）"保留限制说明。

### 3.6 与 003 的对照观察（战役观察点）

| 维度 | 003（auto minimal） | 010（真人交互） |
| --- | --- | --- |
| profile 来源 | scripted 三字段硬编码 | 真人修订 + semantic intake 分类 + 显式确认 |
| degraded_profile | True | 期望 False（真人确认过） |
| hitl1 轮数 | 0（短路） | ≥1（interrupt 往返） |
| hitl2 | auto_proceed 标记短路 | 自主 `recommend_hitl2_route` 决策（被观察） |
| 时间 | ~2-3 分钟 | 更长（交互往返 + 模型分类调用） |

## 4. Stage B2：language CHOICE 专项（条件式，不在 010 PASS 范围）

仅当 (a) ~~BUG-060（Demo TUI typed OPTION 缺失，已登记）修复并有确定性
回归~~（✅ 已满足：change `fix-demo-tui-choice-option`，2026-08-21，RED-009
+ verify 全绿），且 (b) B1 收官后仍决定覆盖 CHOICE，才执行。用独立的
unspecified-language 问题（不含 ASCII 字母与汉字），验证 TUI 只显示
`zh`/`en`、提交 typed OPTION、HITL1 admission 写入选定 output language。
该 run 不与 003 profile 对照混同。此处只留占位。

## 5. Stage C：Gateway observer 体验（可选，推迟）

`make profile-dev PROFILE=demo` + `make demo-tui PROFILE=demo`。定位：
**Demo TUI 的 default real Gateway observer 路线观察**（transport/
presentation 差异），明确无本地 cancel、无 embedded bundle 发现假设、
**无 Primary User 产品验收声明**（Demo TUI 是 contributor/operator
visualizer，不是当前产品入口）。执行前预写有限观察问题清单；否则不保留
占位。此处只留占位。

## 6. 撞上问题怎么办

- **TUI 卡死/模型挂起**：Ctrl-C 退出 TUI（bundle 侧状态由 checkpoint
  决定，不猜）；重跑 §3.0 起（新 bundle；**旧 bundle 不会被自动清理或
  归档**——real DemoAdapter 每进程独立 scope 但不删历史）。
- **语言 CHOICE 意外出现**：该轮现在可作答（BUG-060 已由 change
  `fix-demo-tui-choice-option` 修复，2026-08-21）：点选项按钮，或 composer
  精确输入广告 id（`zh`/`en`）回车；不匹配的文本不会被派发。若行为与此
  不符，截图/抄录 → 报新 bug。
- **semantic intake 报错/形状怪异**：抄录 TUI 日志行 + 保留 bundle → 按
  `_backlog/bugs/` 流程登记（预期高危：分类输出形状、TUI 长跑渲染）。
- **hitl2 出现人工 prompt**：偏离契约（应为自主 continuation），保留
  bundle 报 bug。
- **profile 不符预期**（字段丢失/意外降级）：保留 bundle + events.jsonl
  相关行，报 bug。

## 7. 证据归档

- exact bundle id + 四步证据链记录（三值 + 确认方式）+ `state.json`
  profile 片段 + `request/profile.json` + report.md 开头 → 战役记录
  （handoff-010 或 runbook 附录）；
- hitl1 交互轮数 / 各轮耗时 / hitl2 自主经过的观察 → 观察点数据；
- bug 按 `_backlog/bugs/` 流程；修复走 openspec change（004 先例），
  primary causal owner 从 presentation adapter 与 shared typed
  interaction boundary 的实际问题中选定。
