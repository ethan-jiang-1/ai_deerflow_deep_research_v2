---
title: "004 - Hard Real-Auto End-to-End"
runbook_id: "004"
difficulty: "hard"
mode: "real-auto"
cost: "high"
automation: "full-auto"
fixed_question: "Compare China and US EV battery market in 2024."
prerequisites:
  - "DEEPSEEK_API_KEY"
  - "TAVILY_API_KEY"
  - "DEERFLOW_DEMO_MODEL"
purpose: "Run the default product path (no declared research intent) fully automatically on the fixed comparison question and verify a real comparative final report; this rung deliberately stresses the never-exercised multi-topic real chain to surface defects."
how_to_run: |
  cd deep_research_harness
  ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 004-demo --mode 004" | sed -n 's/^soft_bundle_root=//p')
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 004"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="status $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="phases $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="verify $ROOT"
expected_result: "RESULT: PASS + final/report.md with real comparative content covering BOTH the China and US EV battery market + observed (not asserted) multi-topic decomposition; a non-converging honest gap degrades to a completed run whose report discloses the gap under Uncertainties"
non_goals:
  - "Not a Gateway observer path claim (validates the non-interactive operator embedded-smoke path only)."
  - "No custom research question."
  - "No manual HITL input."
  - "No bridge hang-hardening (out of scope; Ctrl-C + retry when hung)."
  - "No product default changes: 004 runs the default product path precisely so its defects surface (bug flow), not so they get pre-fixed."
---

# 004 Runbook：最难 Real-Auto 端到端（默认意图找茬）

> **004 是什么**：真实 DeepSeek 模型 + 真实 Tavily 网页工具，全自动跑完整 Deep
> Research，不等人。入口通过 `soft-bundle run <root> --mode 004`，内部委托
> `make demo-real-scripted --question "<固定比较题>" --profile-intent none`。
>
> **004 的机制定位**：入口显式**不声明**研究意图（`--profile-intent none`）——
> 走**产品默认路径**：planner 自由拆 1–8 个 topic、每 topic 每 wave 至少 1 个
> work unit、wave2 gate 默认 1 轮补证、真实多结论 final layout。003（minimal
> 意图）刻意回避的链路正是 004 要压的链路。**这一格的用途就是找茬**：撞出的
> 缺陷按第 8 节 bug 流程处理，这是产出，不是失败。
>
> **004 不是什么**：不是测试分支——它测的就是默认意图下的真实产品路径；
> 不开放自定义问题；不需要人工 HITL；不为跑通预改任何产品默认。
>
> **004 固定问题**：`Compare China and US EV battery market in 2024.`

---

## 0. 前置

- `.env`（`deep_research_harness/.env`，gitignored）需要：
  - `DEEPSEEK_API_KEY`（真实模型）
  - `TAVILY_API_KEY`（真实网页搜索）
  - `DEERFLOW_DEMO_MODEL=deepseek-v4-flash`（演示用模型名）
- 需要网络（模型 + Tavily）。
- 全程自动：HITL1/HITL2 都由系统自动回答（auto 建档 + auto proceed）。
- 每次 `run` 都会先自动清理之前的 run bundle。
- **花费预期（花多）**：多 topic × 每 topic 每 wave work unit ×（含 repair 重跑）
  ——常态 2–5 个 topic，最坏 8（产品界 `MAX_TOPICS=8`）；显著高于 003（单
  topic 数分钟到十几分钟）。跑飞就 Ctrl-C 重来。

## 1. 创建 soft bundle 并跑 004

```bash
cd deep_research_harness

ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 004-demo --mode 004" | sed -n 's/^soft_bundle_root=//p')
echo "ROOT=$ROOT"

UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 004"
```

预期控制台结尾（真实 run 用时不定，视 topic 数显著长于 003）：

```text
bound_bundle_id=b_xxx
bundle_local_path=.deep-research-demo-runs/workspace/deep-research/scopes/.../b_xxx
RESULT: PASS

=== Run Summary ===
Nodes passed:
  1. bootstrap (completed: ...)
  ...
  9. final_delivery (completed: ...)
Terminal: final_delivery -> completed
Final result:
  final/report.md: exists
# Deep Research Report
...
```

> 提示：`make` 输出可能因管道缓冲延迟显示，可用 bundle 内
> `diagnostics/events.jsonl` 的 mtime 判断进度（`ls -l .../diagnostics/events.jsonl`）。

## 2. 认 root 和 bundle

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="status $ROOT"
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="path $ROOT"
```

## 3. 看节点日志

```bash
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"
```

检查点：

- `Observed summary: completed@final_delivery generation 0`
- `Journal health: complete`
- 执行轨迹应包含：
  `bootstrap -> hitl1 -> topic_planning -> wave0 -> wave1 -> wave2_synthesis -> hitl2 -> readiness -> final_delivery`

## 4. 看每个环节内容

```bash
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="phases $ROOT"
```

## 5. 验收最终结果

```bash
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="verify $ROOT"
```

预期：`RESULT: PASS`。

关键检查（真实比较内容验收，区别于 003 的单事实）：

- `final/report.md` 必须存在。
- 报告是**真实比较内容**：**China 与 US 两个市场都必须有事实性陈述与引用**，
  只写一边不算过（见 6.2 观察点）。
- 有 claim-citation 映射（结论 → 来源引用）。
- 证据提交引用**真实 source URL**。

### 5.1 honest gap 不收敛时的诚实交付（继承 003 全部语义）

与 runbook-003 第 5.1 节完全相同的验收语义（BUG-035/044/046/050/053/054/055/057
修复后）：wave2 gate 预算**首次**耗尽降级为 degraded pass、run 继续 completed、
`RESULT: PASS`、`## Uncertainties` 披露未收敛 gap。004 的默认 gate 预算是
**1 轮**（无 minimal 意图对），比较题天然多 gap——**大概率首耗尽即降级 pass
+ 披露，这是预期路径不是失败**。blocked 只出现在结构性失败或"降级后再次
耗尽"，出现即按第 8 节走 bug 流程记录证据。

## 6. 多 topic 观察验收（004 专属）

### 6.1 topic 分解与 work unit

```bash
BUNDLE=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="path $ROOT" | tail -1)
ls "$BUNDLE/work"
```

验收规则：

- **观察并记录** planner 实际拆题数与各 topic 的 scope（写入 handoff）；
  **不断言固定数量**（产品契约只承诺 1–8 与"每个 must-answer 被覆盖"）。
- 每个 topic 在每个 wave 至少产生 1 个 work unit（scope 判定同 003 第 6 节：
  同 topic repair 重跑不计，看 scope 不看序号）。
- 证据提交引用真实 source URL。

### 6.2 观察点：comparison subjects 提取不对称（已知，先跑不预修）

`derive_comparison_intake_seed` 对 004 固定问题的提取结果是
`('China', 'US EV battery market in 2024.')`——第一个 subject 只有 "China"，
第二个吞掉整个半句（含句号）。这个跛脚对会进入 planner 上下文。**观察**：
topic 分解是否因此被带偏（如只拆出 China 侧 topic、US 侧无人覆盖、或 scope
切分怪异）。带偏成立 → 按第 8 节 bug 流程登记（修复方向：对称提取/去尾部
句号），以真实 run 的 journal 为证据。未带偏 → 记录"观察无伤害"即可。

### 6.3 观察点：final layout 与 readiness/final 预算首次真实受压

003 的 ≤1 结论确定性 layout 免模型捷径在 004 **不会触发**（多结论）——
final_delivery 的模型排版路径（BUG-055 的降级护栏：plan-order layout 带发布
completed）与 readiness critic 首次承受多 topic 负载。撞出新形状失败 →
bug 流程；readiness/final 预算 exhausted 首现 → bug 流程实证放宽（003 留的
口子，004 正好补实证）。

### 6.4 已收口观察（2026-08-19 首跑战役，PASS bundle `b_cuTRGqwJysx...`）

- **6.1 结论**：planner 在自由 1–8 topic 下实际产出 **1 个 wave0 + 1 个
  wave1 work unit**（`g0_wave0_w0000`/`g0_wave1_w0000`），topic_registry
  空——广度按契约"观察不断言"记录；证据提交引用 10+ 真实 source URL。
- **6.2 结论**：subjects 跛脚对（`['China', 'US EV battery market in
  2024.']`）依旧进入 planner 上下文，但 findings/gaps **双市场覆盖无实际
  伤害**（China 侧 LFP/BYD/CATL 与 US 侧 IRA/产能/价格均有覆盖）——按 D2
  决策记录"观察无伤害"，不预修。
- **6.3 结论**：多结论真实排版路径走通（final_delivery a1 一次过），
  readiness critic 无可采信 verdict → 诚实披露降级交付（3 个 unresolved
  gaps 进 Uncertainties），未撞出新形状失败。
- **战役副产出**：5 次尝试连破 2 个 P0（BUG-058 wave1 critic bool 标签、
  BUG-059 claim ref 别名盲区，均为 003 minimal 路径踩不到的盲区），经
  `fix-wave1-critic-label-shapes` / `fix-synthesis-claim-ref-aliases` 修复
  归档；环境性失败（进程回收/合盖断网/SDK 挂起）见 §7 与 git 历史。

## 7. 模型挂起 / 卡死怎么办

- DeepSeek SDK 偶发阻塞 `ainvoke`，bridge 的 `asyncio.timeout` 无法中断
  （已知问题，实测多轮；004 的多 topic 长跑暴露面更大）。
- **处理：Ctrl-C 中断，然后重跑**（`run $ROOT --mode 004` 会先清理再跑）。
- 多次重试仍挂起 → 按第 8 节走 bug 流程；bridge 加固是独立事项，不在
  004 范围内。

## 8. 发现不对怎么办

1. 把现象、复现步骤、日志贴到 `_backlog/bugs/BUG-xxx-<slug>.md`
2. 在 `_backlog/bugs/README.md` 活跃列表登记
3. 不要直接去改 Harness 核心；先按 `_backlog` 规矩走 bug 流程
4. **004 的产出包括茬本身**：真实模型波动（repair 循环多、wave2 留 honest
   gap、final_delivery 多次 attempt）、subjects 不对称带偏、多结论 layout
   新形状、预算首现 exhausted——逐项按证据登记；wave2 honest gap 不收敛时
   按 5.1 节降级为带披露的 completed 交付（不再阻塞）。
