---
title: "001 - Easiest Fixture Graph End-to-End"
runbook_id: "001"
difficulty: "easiest"
mode: "fixture-graph"
cost: "low"
automation: "full-auto"
fixed_question: "What is the capital of France?"
prerequisites: []
purpose: "Verify the Deep Research graph runs from first node to last node using a fixed simple question and a clean controlled environment."
how_to_run: |
  cd deep_research_harness
  ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 001-demo" | sed -n 's/^soft_bundle_root=//p')
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 001"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="status $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"
  UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="phases $ROOT"
expected_result: "terminal: completed + Fixture graph composition verified."
non_goals:
  - "Not a real research report validation."
  - "No custom research question."
  - "No manual HITL input."
---

# 001 Runbook：最简单 fixture 图端到端

> **001 是什么**：用最简单、确定性的方式，从图的第一个节点一路跑到最后一个节点，确认整条 Deep Research 流程能通。
>
> **001 不是什么**：不是真实研究报告验证。fixture 图不生成真实 report，只验证 graph 通断。
>
> **本文件是 001 的唯一操作手册**：所有命令都写在下面，不需要额外 `.sh` 脚本。
>
> **001 现在统一走 soft bundle CLI**：先 create 一个 soft bundle root，再 run，之后 status/path/inspect/phases 都用同一个 root。

---

## 0. 前置

- 零前置：不联网、不需要 Gateway，花费少。
- 只需在 `deep_research_harness/` 下执行。
- 全程自动：固定问题下 HITL1/HITL2 都由系统自动回答，不需要人工输入。

## 1. 创建 soft bundle 并跑 001

> 每次 `run` 都会先自动清理之前的 run bundle 内容，保证从干净状态开始。
> 也可以手动执行：`UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="clean"`。

```bash
cd deep_research_harness

# 创建 soft bundle（不指定 --root 会自动生成；研究问题固定为极简单问题）
ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name 001-demo" | sed -n 's/^soft_bundle_root=//p')
echo "ROOT=$ROOT"

# 跑 001
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 001"
```

预期控制台结尾：

```text
bound_bundle_id=b_xxx
bundle_local_path=.deep-research-demo-runs/workspace/deep-research/scopes/<scope>/<bundle_id>
```

## 2. 认 root 和 bundle

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="status $ROOT"
```

检查点：

- `soft_bundle_root` 与第 1 步一致
- `current_bundle_id` 已绑定为 `b_xxx`
- `mode=001`

也可以看当前真实 bundle 的 repository-relative 位置：

```bash
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="path $ROOT"
```

## 3. 看节点跑得对不对（看 log）

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"
```

检查点：

- `Observed summary: completed@final_delivery generation 0`
- `Journal health: complete`
- 执行轨迹应包含且最终走到：
  `bootstrap -> hitl1 -> topic_planning -> wave0 -> wave1 -> wave2_synthesis -> hitl2 -> readiness -> final_delivery`
- 最后一条事件应该是 `final_delivery` 的 `completed` / `terminal completed`

## 4. 看每个环节的内容

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="phases $ROOT"
```

它会一次打印：

- `state.json`：执行轨迹、最终状态
- 每个 `work/.../outputs/fixture.json`：Wave0/Wave1 各环节产出的内容
- `final/report.md`：是否存在（001 预期不存在）

也可以直接看 Bundle 目录（用 `path $ROOT` 拿到相对路径）：

```text
deep_research_harness/.deep-research-demo-runs/workspace/deep-research/scopes/<scope>/<bundle_id>/
```

逐项检查：

| 检查项 | 路径 | 预期内容 |
| --- | --- | --- |
| 状态总览 | `state.json` | `phase=final_delivery`、`phase_status=terminal`、`terminal_status=completed` |
| 节点执行轨迹 | `state.json` 的 `execution_trace` | 包含上面 9 个阶段 |
| Wave0 内容 | `work/g0_wave0_w0000/.../outputs/fixture.json` | 有 `fixture_marker: non_research_fixture` |
| Wave1 内容 | `work/g0_wave1_w0000/.../outputs/fixture.json` | 有 `fixture_marker: non_research_fixture` |
| 最终报告 | `final/report.md` | **001 不应存在**。fixture 图不生成真实报告，只验证通断 |

如果 001 出现了 `final/report.md`，说明行为不符合 001 预期，需要记录 bug。

## 5. 验收最终结果

- `make soft-bundle DEMO_ARGS="status $ROOT"` 显示 `current_bundle_id` 已绑定。
- `make soft-bundle DEMO_ARGS="phases $ROOT"` 显示执行轨迹完整、最终 `completed`。
- `diagnostics/run-summary.json`：
  - `status: completed`
  - `terminal_outcome: completed`
  - `latest_event_sequence` 与事件日志一致
- `diagnostics/events.jsonl` 最后一条：`terminal` / `completed` / `final_delivery`

全部符合 → 001 通过。

## 6. 发现不对怎么办

1. 把现象、复现步骤、日志贴到 `_backlog/bugs/BUG-xxx-<slug>.md`
2. 在 `_backlog/bugs/README.md` 活跃列表登记
3. 不要直接去改 Harness 核心；先按 `_backlog` 规矩走 bug 流程
