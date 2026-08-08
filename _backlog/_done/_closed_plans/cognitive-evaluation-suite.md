# Plan: Cognitive Evaluation Suite

> 类型: 设计 / 分析 | 完成: 2026-08-04

## 背景 / 现状

Deep Research 的节点 MD/prompt 是认知控制程序，不能只用传统 pytest 或一次真实
CLI 结果判断。现有 `tests/eval/` 和 live calibration 继续负责确定性/既有 live 证据；
本计划跟踪一套独立、Local-First、由人显式编排的认知评估系统。

## Progressive Plan

| 阶段 | 状态 | 交付 |
|---|---|---|
| V1 澄清与 proposal | 已完成 | `CONTEXT.md`、ADR 0020-0026、`add-cognitive-evaluation-suite` 的 proposal/specs/design/tasks |
| V1 apply | 已完成 | Runner 一次性执行、隔离 Bundle、`evals/control` 与 `evals/runs` 分离、HITL1/Wave0 node smoke |
| V1 archive/commit | 已完成 | 严格验证、边界检查、同步主规格、归档 change 并提交 |
| V2 | 明确延后 | Flow lane、更多节点覆盖、可选导出/脱敏；不自动触发评审，除非另有明确决策 |

## 决策 / 方案

- `deerflow_research/evals/control/` 只放慢变化、版本化的 Case、Rubric、Review Protocol、schema 和 registry。
- `deerflow_research/evals/runs/` 只放被忽略的快速变化 workspace、immutable Bundle 和独立 Review Record。
- Runner 实现在受治理的 `src/deerflow_deep_research/runtime/evaluation/`，不与上述两个 content/data 子目录混放。
- Runner 每次只执行一个注册 Case；失败后不自动重试、恢复或启动评审。再次尝试必须是新的显式调用。
- Review 由人显式发起；Review Record 引用但不修改 Bundle，执行状态与四态认知结论分离。

## 风险 / 取舍

- [Provider 不稳定导致 smoke 失败] → 保留完整观察和 typed failure，不能把失败伪装成质量结论；修复后新建 Run。
- [运行记录污染控制文件] → 结构 checker、`.gitignore` 和独立 `control/` / `runs/` 路径共同约束。
- [节点 smoke 被误认为完整研究证明] → V1 只做 HITL1 brief 和 Wave0 worker，Bundle 明确 subject，Flow lane 留到 V2。

## 落地关联

归档 change：`openspec/changes/archive/2026-08-04-add-cognitive-evaluation-suite/`。
V1 已完成；本 plan 归档于 `_backlog/_done/_closed_plans/`。V2 只有在另一个明确 change 中启动。
