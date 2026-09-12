# TODO: CI correctness + entry-env trigger + governance claim merge

> 状态: 暂停（未排期） | 优先级: 低 | 更新: 2026-09-12
> 上游: CLS-053（test-regression-speedup）| 下游: 无

## Why

CLS-053 第三轮提速收尾时，三项被显式搁置/远期化，只在关闭摘要留字，无独立条目：

- **L3 · CI checkout `submodules: recursive`**：存量 CI 问题（CLS-052 T20 已定位），
  当前 CI `make install` 必挂。用户"CI 以后再说"，搁置。
- **L4 · entry-env 工作流触发收窄**：去掉 `src/**` / `src_fake/**` 触发（或改
  cron+dispatch），多数 PR 省 2-3min 第二 job；需改契约
  `test_entry_environment_regression_workflow.py::EXPECTED_PATHS`，CI 相关，非本轮痛点。
- **R3-12 · 治理层 claim 合并**：L-C 实测证明用例数大头被 425-claims 逐 row 绑定钉死，
  **只有合并 claims 才能实质减数**；动 traceability，需单独立项，远期。

## 现状对齐

三项都不是"提速路径"（L3 是 CI 正确性，L4 是触发范围，R3-12 是治理层），因此被
排除在 CLS-053 的收益目标外；排除理由均有实测，不是遗漏。

## Current Direction（重启时）

- L3：CI checkout 加 `submodules: recursive`，重开 PR #1 验证（与 R1 缓存确认同批）。
- L4：先改契约 `EXPECTED_PATHS`，再收窄触发。
- R3-12：单独立项，先设计 claim 合并的有界 policy 与 traceability 影响面。

## Non-Goals

- 不把 L3 当作 CLS-053 提速 KPI 的一部分（它是正确性修复）。
- R3-12 未立项前不动 traceability 结构。

## Next Step

无（暂停）。重启条件：用户重开 CI 话题（L3/L4），或出现需要实质减少用例数的
高风险改动（R3-12）。
