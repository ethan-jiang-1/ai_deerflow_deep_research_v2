# Handoff: Mode 003 real-auto 跑通 + change `low-scale-real-auto`

> 生成: 2026-08-18 | 用途: 新会话 pick up 后继续（003 runbook 落地 + low-scale-real-auto change 实施）
> 位置: 本文件在 `_backlog/_local_demo/`；设计文档在 `_backlog/plans/low-scale-real-auto-runs.md`；实施载体在 `openspec/changes/low-scale-real-auto/`
>
> **状态: ✅ 已完成（2026-08-18）**。change 已实施、测试通过、归档为
> `openspec/changes/archive/2026-08-18-low-scale-real-auto/`，主 specs 已同步
> （新增 `execution-intent` / `low-scale-real-auto` capability），提交
> `eab00c4`。003 首次真实 run 验证了全部机制（意图声明 → single_topic、
> 每 wave 1 work unit、wave2 gate 2 轮补证、形状归一化、有界终止），最终在
> wave2 honest gap 收敛失败（`research.blocked`，typed incident）——这是
> runbook-003 第 8 节文档化的模型波动失败路径，不阻塞交付；后续复现按 bug
> 流程处理。

## 目标（一句话）

**把 mode 003（真实 DeepSeek + 真实 Tavily、全自动）端到端跑通**：`soft-bundle run --mode 003` → `RESULT: PASS` + `final/report.md` 真实内容 + 每 wave 1 个 work unit。为支持它，先把 change `low-scale-real-auto` 实施完。

## 当前状态（pick up 时的起点）

- **plan 已定稿**：`_backlog/plans/low-scale-real-auto-runs.md`（v5，最终共识）——含背景、7 项"系统性复审欠考虑点"清单、方案 A/B/C/D、落地评估、实施顺序。**先读它**，它是设计权威。
- **change 已 ready**：`openspec/changes/low-scale-real-auto/`（proposal + specs×7 + design + tasks，`openspec validate --strict` 通过，两轮 polish 完成，结论 ready for apply）。
- **代码零改动**：工作区只剩 plan + change 两个目录（git status 干净）。所有 v1 试验代码已回退。
- 下一步 = **`/openspec-apply-change low-scale-real-auto`**，按 tasks 1→6 顺序实施，最后做真实 003 跑通验证。

## 方案核心（引用 plan，别凭记忆）

产品只新增**一个机制**：非交互 run 声明研究意图（`non_interactive_policy.profile_intent: "minimal" | None`）→ hitl1 auto 分支按声明构造 profile（minimal 三字段 → `single_topic` 既有推导）→ wave2 gate 预算由 **resolver 读 state 的 profile 意图字段**派生（minimal 对 → 2 轮补证，否则默认 1）。003 只是传参（声明 minimal），测的是真实链路。C 部分（must_answer 修复、wave2 预算放宽、wave2/targeted 形状归一化、修复路径有界化）是**产品 bug 修复**（脚本模板掩盖的真实缺陷）。

## 必须知道的坑（全部有代码证据，plan 欠考虑表 + design 已记录，别重踩）

1. **`repair_budget_by_phase` 是 GATE-owned**（`state.py` FieldOwnership）——HITL1 写它会被拒。gate 预算只能 **resolver 只读** HITL 已写的 `cost_tolerance`/`time_budget` state 字段。
2. **`MAX_QUESTION_CHARS = 256`**——`must_answer=(request_text,)` 超 256 会抛 `must_answer_invalid`；auto 分支对长 request **fail-closed blocked**（与 typed-fact 缺失同一路径），不截断。
3. **capability 构造时序**——recipe/capability 在 profile 写入前构造，意图不能走 capability；只能走 profile（planner）和 state（gate resolver）。
4. **模型挂起**——DeepSeek SDK 偶发阻塞 ainvoke，bridge 的 `asyncio.timeout` 无法中断（实测多轮；v1 试过线程隔离但 pytest 兼容性差，已放弃）。处理：runbook 注明 Ctrl-C 重试；bridge 加固是**独立事项**，不在本 change。
5. **真实模型波动**——wave0/wave1 repair 循环多、wave2 留 honest gap、final_delivery 多次 attempt 都是实测常态；gate 2 轮 + must_answer + 归一化覆盖收敛路径，但失败时按 runbook 第 6 节 bug 流程走。
6. **`non_interactive_policy` 是 closed 结构**（tool.py 严格键校验）——加 `profile_intent` 时保留"unknown 键拒绝"，`tests/unit/test_non_interactive.py` 的断言要同步更新（tasks 1.4）。

## 环境事实

- 工作区：`/Users/bowhead/ai_deerflow_deep_research_v2`；应用在 `deep_research_harness/`。
- `.env`（gitignored）已有：`DEEPSEEK_API_KEY`、`TAVILY_API_KEY`、`DEERFLOW_DEMO_MODEL`（值不外泄）。
- 常用命令（均在 `deep_research_harness/` 下）：
  - 002 零成本回归：`UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 002"`
  - 003 真实 run：`UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 003"`（需 .env + 网络；run 输出可能因管道缓冲延迟显示，用 `events.jsonl` mtime 判断进度）
  - 验证：`openspec validate low-scale-real-auto --strict`；全量测试 `UV_NO_CACHE=1 .venv/bin/python -m pytest tests/unit tests/graph tests/contract`
- 真实 003 跑通的历史证据（v1 时代）：run5 曾完整 PASS；wave2 各问题已分别定位过（priority 字符串、gap source_questions 自然语言、targeted source 形状、must_answer 缺失、gate budget 1 轮卡 honest gap）——**证据都在 plan 的现实约束节**。

## 下一步建议（新会话开场）

1. `/openspec-apply-change low-scale-real-auto`（实施；tasks 1→6 有顺序）。
2. 实施中先验证两个关键机制再往下写（避免 v1 式返工）：
   - `GateDefinition.budget_resolver` 接线（evaluate_gate → _resolve_budget，tasks 2.1/2.2）；
   - auto 分支 must_answer + 256 fail-closed（tasks 1.3/1.4）。
3. 全量测试 + ruff + 002 回归（tasks 6.1/6.2）。
4. 真实 003 跑通（tasks 6.3）——失败按 runbook bug 流程；模型挂起就 Ctrl-C 重试。
5. 收尾：runbook-003 落地（tasks 5.4）、`openspec validate --strict`、归档 change（closeout evidence 齐后）。

## 会话语境（简短历史）

002 跑通并修复 BUG-034 → 用户要求按 README 阶梯建 003（真实模型+网页全自动）→ 首次直接实施（v1）发现"为测试改了一堆产品默认"被用户叫停并全部回退 → 用户提出"测试要测真实的东西，特殊情况用 profile 传达意图" → 多轮收敛到 v5（意图声明机制 + gate resolver + 真实适配）→ plan 定稿、change ready、两轮 polish 完成。

## Suggested skills（新会话按需调用）

- `openspec-apply-change`：实施本 change（首要）。
- `openspec-archive-change`：实施+验证完成后归档。
- `tdd`：tasks 1-4 的测试先行实施。
- `grilling`：实施前如对方案仍有疑虑可先质疑一轮。
- `writing-for-agents`：写 runbook-003（面向 agent 的执行文档）。
- `openspec-explore` / `openspec-update-change`：实施中发现设计问题时回到探索/修订。
