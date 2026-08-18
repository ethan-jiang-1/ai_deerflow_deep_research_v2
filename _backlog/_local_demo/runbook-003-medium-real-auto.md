---
title: "003 - Medium Real-Auto End-to-End"
runbook_id: "003"
difficulty: "medium"
mode: "real-auto"
cost: "medium"
automation: "full-auto"
fixed_question: "What is one bounded fact about China's EV battery market in 2024?"
prerequisites:
  - "DEEPSEEK_API_KEY"
  - "TAVILY_API_KEY"
  - "DEERFLOW_DEMO_MODEL"
purpose: "Run the real model + real web tools path fully automatically at the lowest practical scale (declared minimal intent) and verify a real final report."
how_to_run: |
  cd deep_research_harness
  ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 003-demo --mode 003" | sed -n 's/^soft_bundle_root=//p')
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 003"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="status $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="phases $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="verify $ROOT"
expected_result: "RESULT: PASS + final/report.md with real content + one wave0 + one wave1 work unit; a non-converging honest gap degrades to a completed run whose report discloses the gap under Uncertainties"
non_goals:
  - "Not a Gateway observer path claim (validates the non-interactive operator path only)."
  - "No custom research question."
  - "No manual HITL input."
  - "No bridge hang-hardening (out of scope; Ctrl-C + retry when hung)."
---

# 003 Runbook：中等 Real-Auto 端到端

> **003 是什么**：真实 DeepSeek 模型 + 真实 Tavily 网页工具，全自动跑完整 Deep
> Research，不等人。入口通过 `soft-bundle run <root> --mode 003`，内部委托
> `make demo-real-scripted --question "<固定问题>"`。
>
> **003 的最低规模机制**：入口声明 `profile_intent=minimal`（非交互自动 run 的
> 产品机制），真实链路按 minimal 意图跑：planner `single_topic` 强制 1 个 topic、
> wave0/wave1 各 1 个 work unit、wave2 gate 预算 2 轮补证。产品默认行为不变。
>
> **003 不是什么**：不是测试分支——它测的就是 minimal 意图下的真实产品路径；
> 不开放自定义问题；不需要人工 HITL。
>
> **003 固定问题**：`What is one bounded fact about China's EV battery market in 2024?`

---

## 0. 前置

- `.env`（`deep_research_harness/.env`，gitignored）需要：
  - `DEEPSEEK_API_KEY`（真实模型）
  - `TAVILY_API_KEY`（真实网页搜索）
  - `DEERFLOW_DEMO_MODEL=deepseek-v4-flash`（演示用模型名）
- 需要网络（模型 + Tavily）。
- 全程自动：HITL1/HITL2 都由系统自动回答（auto 建档 + auto proceed）。
- 每次 `run` 都会先自动清理之前的 run bundle。

## 1. 创建 soft bundle 并跑 003

```bash
cd deep_research_harness

ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 003-demo --mode 003" | sed -n 's/^soft_bundle_root=//p')
echo "ROOT=$ROOT"

UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 003"
```

预期控制台结尾（真实 run 用时不定，几分钟到十几分钟）：

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

关键检查（真实内容验收，区别于 002 的脚本模板）：

- `final/report.md` 必须存在。
- 报告是**真实内容**：由真实来源支撑的事实性陈述，不是脚本模板句子
  （002 的 `# Deep Research Report` 模板句不算）。
- 有 claim-citation 映射（结论 → 来源引用）。
- 证据提交引用**真实 source URL**（`bundle` 内 evidence/submissions 或 report
  的引用列表）。

### 5.1 honest gap 不收敛时的诚实交付（BUG-035/044/046/050/053/054 修复后的验收语义）

真实模型留 honest gap（如"两个来源数字为什么不同"、"精确全年总量是多少"）
且补证不收敛是**常态**，不再判负：

- wave2 gate 预算耗尽时**首次**降级为 degraded pass，run 继续走
  hitl2 → readiness → final_delivery，终态 `completed`，`RESULT: PASS`
  （readiness 在降级后不再把流程送回补证循环——BUG-044 修复；即便
  readiness critic 调用失败也走降级交付）。
- **节点级预算失败同样交还 gate**（BUG-050 修复）：wave2 synthesis 的
  模型调用被策略预算拒绝/截停时，节点不再直写 terminal blocked，而是写
  `wave2_budget_exhausted` 信号非终止返回；wave2 gate 把它投影为规则失败，
  走与 gap 耗尽**同一套**预算/marker/降级分支——同一 seeding 至多降级一次。
- **高置信 finding 必须交付**（BUG-054 修复）：`confidence=high`、引用完备、
  无检索需求的 synthesis finding 直接成为可写结论（statement 原文），
  readiness critic 的非实质性判定只能**追加**强制不确定项（披露），不能清空
  结论——"部分结论 + 披露并存"取代"insufficient → 零交付"。
- **layout 回显失败不再阻塞**（BUG-055 修复）：非退化 plan 的排版候选被拒
  （fence/散文包裹在归一化后仍不可 admit）或 composer 调用失败时，
  final_delivery **同 visit 降级为 plan-order layout 并正常发布**——排版是
  advisory，不消耗 gate repair、不再可能因此 blocked；拒绝的 canonical code
  （闭合 `final_layout_*`）进 journal `initial` validation fact，模型原文按
  REJ 契约不落盘。
- **退化 plan 免模型**（BUG-053 修复）：结论数与不确定项数均 ≤1 时排序数学
  唯一，final_delivery 确定性构造 layout，不再赌模型回显合成 id。
- `final/report.md` 的 `## Uncertainties` 段必须**披露**未收敛的 gap
  （描述来自 `synthesis/findings.json`；正文找不到描述时至少披露 gap id）。
- blocked 只在两种情形出现：结构性失败（plan/evidence 读取、render、publish、
  readback/verify——BUG-055 修复后 layout 回显失败已降级为带发布的 completed，
  不在此列）；或"降级后再次耗尽"
  （wave2 gate 每次预算 seeding 至多降级一次）——均带 typed incident 与
  诊断引用（wave2 输入条件失败也走有界终止，不再裸崩溃——BUG-046）。
  历史上"单次 003 run 预期不会触发 blocked"的表述已被 2/2 次真实 run
  证伪，现按"可能触发、按第 8 节记录证据"处理。
- 终端若出现 blocked（其他原因），journal 可用性行应如实显示
  `Event Journal: 已创建`（诊断 ref 已发布时），不再误报"不可用"。

## 6. 单 work unit 验收

003 声明 minimal 意图 → planner `single_topic` → wave0/wave1 初始各恰好 1 个
work unit：

```bash
BUNDLE=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="path $ROOT" | tail -1)
ls "$BUNDLE/work"
```

验收规则（BUG-045 修复后的准确口径）：

- **初始 work unit**：`g0_wave0_w0000` 与 `g0_wave1_w0000` 各一个
  （没有 w0001 等由 planner 多 topic 产生的多余初始 unit）。
- **同 topic repair 重跑不计**：wave1 gate 有界 repair 会以**相同 scope**
  重跑该 wave（`g0_wave1_w0001`，spec_hash 不同）——这是 repair 循环正常
  工作，不是 single_topic 失效。判定 single_topic 是否生效看 **scope**：
  所有 wave1 work unit 的 scope 相同（1 个 topic）即为正确；出现**不同
  scope** 的额外 work unit 才说明 single_topic 没生效，按第 8 节走 bug
  流程。

## 7. 模型挂起 / 卡死怎么办

- DeepSeek SDK 偶发阻塞 `ainvoke`，bridge 的 `asyncio.timeout` 无法中断
  （已知问题，实测多轮）。
- **处理：Ctrl-C 中断，然后重跑**（`run $ROOT --mode 003` 会先清理再跑）。
- 多次重试仍挂起 → 按第 8 节走 bug 流程；bridge 加固是独立事项，不在
  003 范围内。

## 8. 发现不对怎么办

1. 把现象、复现步骤、日志贴到 `_backlog/bugs/BUG-xxx-<slug>.md`
2. 在 `_backlog/bugs/README.md` 活跃列表登记
3. 不要直接去改 Harness 核心；先按 `_backlog` 规矩走 bug 流程
4. 真实模型波动（repair 循环多、wave2 留 honest gap、final_delivery 多次
   attempt）是实测常态：gate 2 轮 + must_answer + 归一化覆盖收敛路径；wave2
   honest gap 不收敛时按 5.1 节降级为带披露的 completed 交付（不再阻塞），
   其余失败按 bug 流程记录证据。
