---
title: "010 - TUI Auto Full Run (Zero Human Keys)"
runbook_id: "010"
difficulty: "medium"
mode: "real-auto-tui"
cost: "medium"
automation: "full-auto"
fixed_question: "What is one bounded fact about China's EV battery market in 2024?"
prerequisites:
  - "DEERFLOW_DEMO_MODEL（非空模型 selector）"
  - "与 selector 匹配的模型凭证（如 DEEPSEEK_API_KEY）"
  - "TAVILY_API_KEY"
  - "demo-tui extra 已安装（make install）"
purpose: "在同一固定例子（003 短问题）下，用 TUI 自动全跑一次真实 Deep Research：真人零按键，hitl1/hitl2 由 graph 拥有的 scripted 策略自动补（auto_profile + auto_proceed，默认产品路径无 profile_intent）。验证'TUI 一层真实图能自主到终态'。020 是同一例子的手动孪生（交互由真人补）。"
how_to_run: |
  cd deep_research_harness && make demo-tui-real-auto
  # 或双击 RUN-010.command（自动起 TUI，什么都不用按）
expected_result: "exact bundle（启动前记录目录集合、退出后唯一新增）+ terminal_status=completed + request/profile.json 存在 + final/report.md 真实内容。全程零人工输入；若出现 AwaitingInput（hitl1/hitl2 interrupt）= 偏离契约，照实记录。"
non_goals:
  - "不做真人 HITL1 交互（那是 020：runbook-020-tui-manual.md，同一例子由真人补交互）。"
  - "不做 language CHOICE 覆盖（英文固定问题确定性 en，不触发 CHOICE）。"
  - "不做 HITL2 人工决策（scripted 自动 proceed；真实 HITL2 本就自主）。"
  - "不是 Gateway observer 路径（Stage C 可选，另见 020 runbook）。"
  - "不修改研究问题（control environment：固定问题，TUI 自动提交）。"
  - "不做 capability 精确归因（Journal model_tool fact 无 capability 字段，证据限制同 020）。"
---

# 010 Runbook：TUI 自动全跑（真人零按键）

> **一键启动**：Finder 双击仓库根的 **`RUN-010.command`**（或终端里
> `bash RUN-010.command`）——起 TUI、自动提交固定问题、自动跑完，你只看。
>
> **010 是什么**：`_backlog/_local_demo` 前四格（001-004）是 CLI 全自动；
> 010 是 **TUI 一层的自动全跑**——入口 `make demo-tui-real-auto`
> （= `demo_tui.py --embedded-smoke --auto`）起本地全真实图（真实模型 +
> 真实 Tavily），preflight 通过后自动派发
> `StartRun(question=<固定问题>, scripted=True, profile_intent=None)`：
> graph 拥有的策略自动回答 HITL1（auto_profile）与 HITL2（auto_proceed），
> **真人零按键**，TUI 自主走到 `terminal_status=completed`。
>
> **010 与 020 是同一例子**（同一固定问题、同一真实图、同一测试内容）：
> 唯一差别是交互点——010 由自动化补（本 runbook），020 由真人补
> （`runbook-020-tui-manual.md`）。先跑 010 自动验证通路，再跑 020 手动压
> 交互认知面。
>
> **本 runbook 是"给 agent 的操作单"**：010 不需要用户按键；agent 负责
> 环境、启动、bundle 侧证据收集与验收。

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

## 2. 启动前：记录 bundle 目录集合（exact-bundle 绑定，agent 侧）

```bash
cd deep_research_harness
BROOT=.deep-research-demo-runs/workspace/deep-research/scopes
ls -d $BROOT/*/b_* 2>/dev/null | sort > /tmp/bundles_before_010.txt
make demo-tui-real-auto
```

> **010 不需要你按键**：TUI 自动提交固定问题并全跑。你只观察：banner
> 标注 `embedded smoke · auto`，pipeline 滚动，RichLog 记录等待与进度，
> 直到 `Research complete`（Terminal）。Ctrl-C 可随时退出（bundle 侧状态
> 由 checkpoint 决定，不猜）。

## 3. 等待与观察

- 起 run 后 pipeline 依次走 bootstrap → hitl1（**自动**，auto_profile
  短路，无 AwaitingInput）→ topic_planning → wave0 → wave1 →
  wave2_synthesis →（targeted_evidence）→ hitl2（**自动**，auto_proceed
  短路，无人工 prompt）→ readiness → final_delivery；RichLog 滚动日志；
- **进度播报（010 的必备体验，2026-08-21 起）**：run 进行中 TUI 的
  Working 心跳会**实时读当前 active bundle 的 journal（events.jsonl）**，
  每 1 秒刷新并播报四行——`进度: bootstrap → hitl1 → wave0 → wave1（进行中）`、
  `最近: HH:MM:SS · <phase> <category> <outcome>`、`模型调用: N 次完成 · X.Xk tokens`、
  `journal 事件: N`。看到进度行在变 = run 活着；只看到等待秒数在涨 = 卡住
  （见 §6 判别法）。播报实现：`demo_tui.py::live_progress_lines()`（纯函数，
  只读被忽略的本地 retained-run 文件，读不到就退化为静态文案，不影响 run）。
- **报告路径（2026-08-21 起）**：run 完成（Research complete）时，TUI 在
  详情末尾显示 **`Report: <路径>/final/report.md`**，直接照路径打开即可。
- **可拷贝（2026-08-21 起）**：**中间对话区（RichLog，LLM 对话/日志那
  一块）保证能拷**——**双击该区域 = 复制对话全文**到剪贴板；底部
  **Copy details** 按钮同样复制中间对话全文；要选一段则 **Option+拖拽**
  选中屏幕文本（Textual 内置文本选择）；每次渲染的详情还落盘到
  **`logs/tui-<pid>.log`**（路径在 Copy 后提示），出问题打开文件即可拷全量。
- 观察点：TUI 对 scripted 全跑的渲染（hitl1/hitl2 以 phase 形式经过而非
  interrupt）、provider 失败呈现、长 run 下 RichLog 行为、耗时叙事；
- 全程分钟级到十数分钟（真实模型 + 真实 web）；**不要合盖/断网**（004 教训）。

## 4. 结束后验收（agent 侧）

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

## 5. PASS 判据（全部满足才算过）

1. exact bundle 绑定唯一且来自本次 run（§4 第一步）；
2. **全程零人工输入**：TUI 没有出现等待真人输入的 AwaitingInput；
   若出现（hitl1/hitl2 interrupt）= 偏离 scripted 契约，照实记录并报 bug
   （不替代 PASS）；
3. `request/profile.json` 存在，与 `state.json` 的 profile 字段一致，
   `terminal_status=completed`；
4. `final/report.md` 真实内容（非模板句，与 003/020 同层级内容检查）；
5. Journal 证据只声明实际能证明的事实（§7 证据限制，同 020）。

## 6. 撞上问题怎么办

- **TUI 卡死/模型挂起**：先看 §3 进度播报——**进度行/journal 事件数在动 = 活着
  （模型调用本来就要几十秒，别急）**；只有"等待秒数在涨、其余全不动"持续数分钟
  才算卡死。Ctrl-C 退出 TUI（bundle 侧状态由 checkpoint 决定，不猜）；重跑 §2
  起（新 bundle；旧 bundle 不会被自动清理或归档——real DemoAdapter 每进程独立
  scope 但不删历史）。
- **出现 AwaitingInput（不应发生）**：scripted 策略短路了 hitl1/hitl2，
  出现 interrupt = 偏离契约。截图/抄录 TUI 日志行 + 保留 bundle → 按
  `_backlog/bugs/` 流程登记。
- **language CHOICE 意外出现**：同 020——该轮现为可作答（BUG-060 已由
  change `fix-demo-tui-choice-option` 修复）：点选项按钮，或 composer 精确
  输入广告 id（`zh`/`en`）回车。若行为与此不符，截图/抄录 → 报新 bug。
- **semantic intake 报错/形状怪异**：抄录 TUI 日志行 + 保留 bundle → 按
  `_backlog/bugs/` 流程登记（预期高危：分类输出形状、TUI 长跑渲染）。
- **profile 不符预期**（字段丢失/意外降级）：保留 bundle + events.jsonl
  相关行，报 bug。

## 7. Journal 证据限制（不得伪归因，同 020）

model_tool fact 只含 phase/outcome/attempt_id/call_ordinal，**没有
capability 字段**——不能靠字符串搜索证明 semantic intake 被调用。010 自动
跑可用的证据：exact bundle、终态 State、`request/profile.json`、
report/citation artifacts、HITL1/HITL2 以 phase 经过的 trace。对"具体是
哪一种认知调用"保留限制说明。

## 8. 证据归档

- exact bundle id + `state.json` profile 片段 + `request/profile.json` +
  report.md 开头 → 战役记录（handoff-020 或 runbook 附录）；
- 与 020 的对照：同一例子下，010（scripted auto）vs 020（真人确认后
  profile）的 profile 来源差异可对照——逻辑同现状 003 vs 020 对照；
- bug 按 `_backlog/bugs/` 流程；修复走 openspec change（BUG-061 先例：
  `add-demo-tui-auto-entry`，2026-08-25 已归档）。
