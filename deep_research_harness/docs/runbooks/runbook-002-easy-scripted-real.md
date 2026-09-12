---
title: "002 - Easy Scripted-Real End-to-End"
runbook_id: "002"
difficulty: "easy"
mode: "scripted-real"
cost: "low"
automation: "full-auto"
fixed_question: "What is one bounded fact about grid energy storage?"
prerequisites: []
purpose: "Run the full production control path with scripted model/tools and verify a final Markdown report is produced."
how_to_run: |
  cd deep_research_harness
  ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 002-demo --mode 002" | sed -n 's/^soft_bundle_root=//p')
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 002"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="status $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="phases $ROOT"
expected_result: "RESULT: PASS + final/report.md exists"
non_goals:
  - "Not a live model or web research run."
  - "No custom research question."
  - "No manual HITL input."
---

# 002 Runbook：稍难 Scripted-Real 端到端

> **002 是什么**：用脚本化的真实控制链路跑完整 Deep Research，验证真实适配器、门、持久化，并且最终会生成一个 Markdown report。
>
> **002 不是什么**：不是真实模型 + 真实网页搜索；不开放自定义问题；不需要人工 HITL。
>
> **002 固定问题**：`What is one bounded fact about grid energy storage?`

---

## 0. 前置

- 零前置：不联网、不调用真实模型，花费少。
- 全程自动：HITL1/HITL2 都由系统自动回答。
- 每次 `run` 都会先自动清理之前的 run bundle。

## 1. 创建 soft bundle 并跑 002

```bash
cd deep_research_harness

ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 002-demo --mode 002" | sed -n 's/^soft_bundle_root=//p')
echo "ROOT=$ROOT"

UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 002"
```

预期控制台结尾：

```text
bound_bundle_id=b_xxx
bundle_local_path=.deep-research-demo-runs/workspace/scripted-real/.../b_xxx
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
Work outputs: ...
```

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

预期：

```text
RESULT: PASS
```

关键检查：

- `final/report.md` 必须存在（002 与 001 的核心区别）
- 报告内容至少是一个 Markdown 结构（`# Deep Research Report` 等）
- 9 个节点全部 completed
- 终态 completed

## 6. 发现不对怎么办

1. 把现象、复现步骤、日志贴到 `_backlog/bugs/BUG-xxx-<slug>.md`
2. 在 `_backlog/bugs/README.md` 活跃列表登记
3. 不要直接去改 Harness 核心；先按 `_backlog` 规矩走 bug 流程
