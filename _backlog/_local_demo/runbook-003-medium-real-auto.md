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
expected_result: "RESULT: PASS + final/report.md with real content + one wave0 + one wave1 work unit"
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

## 6. 单 work unit 验收

003 声明 minimal 意图 → planner `single_topic` → wave0/wave1 各恰好 1 个
work unit：

```bash
BUNDLE=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="path $ROOT" | tail -1)
ls "$BUNDLE/work"
```

预期：`g0_wave0_w0000` 与 `g0_wave1_w0000` 各一个（没有 w0001 等多余 work
unit）。若出现多个 work unit，说明 single_topic 推导没生效，按第 8 节走 bug
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
   attempt）是实测常态：gate 2 轮 + must_answer + 归一化覆盖收敛路径，失败时
   按 bug 流程记录证据。
