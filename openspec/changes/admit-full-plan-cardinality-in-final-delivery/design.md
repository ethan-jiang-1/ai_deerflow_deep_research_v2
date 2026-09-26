# Design

## Context

2026-09-26 上午 demo-real 首次抵达 final_delivery 后确定性 gate_blocked；
离线复现（真实 bundle 的 `review/report-plan.json`：7 conclusions + 9 uncertainties）
钉死根因：`FinalDeliveryLayoutCandidate` 两个 order 的 `max_length=8` 与
`ReadinessReportPlan` 无界 tuple 不匹配，composer 路径与确定性降级路径在同一点
双杀，且兜底 `except Exception` 静默。取证过程与判据见
`_backlog/plans/demo-real-gateway-closeout.md`。

## Goals / Non-Goals

**Goals:**

- 任意合法基数的 admitted plan 都能走完 layout → render → publish → read-back。
- 被拒投递带封闭具体类别 + bounded detail；终态失败留 journal 事实。

**Non-Goals:**

- 不改准入语义（complete、duplicate-free 全排列仍强制）。
- 不给 plan 侧加基数截断（违反 readiness spec"blocked judgment 不得消失"）。
- 不动 composer 提示词与 wave2/readiness。

## Decisions

1. **移除 order 的 `max_length=8`（对齐 plan 契约的无界 tuple），而非抬高到某个
   新常数。** 备选"双方统一到 32"被否：plan 侧截断会隐藏 uncertainty（spec 禁止），
   只抬布局侧则留下下一次撞界的机会；无界 tuple 的真实安全网已存在（wave1 开放
   问题上限 64、REG-008 checkpoint 字节界、条目内字段界）。这与
   `ReadinessReportPlan.writable_conclusions` 现状同形，契约两侧一致。
2. **pydantic 折叠复用 wave2 G1 的形状而非代码**：composer 内新增局部
   `_schema_detail`（前 3 条 loc/type/msg，msg 截 120 字符）+
   `ValueError("final_layout_schema_invalid", detail=…)`；`_LAYOUT_LITERAL_CODES`
   加入该码。不抽公共 helper——两个消费者形状相近但域不同，第三个消费者出现时
   再上提（避免过早抽象）。
3. **read-back 失败留痕用最小闭合映射**：except 分支把异常 str 在既有封闭码集合
   （`final_report_shape_invalid` / `final_citation_map_shape_invalid` /
   `final_publication_refs_invalid`）内直记，否则记
   `final_delivery_readback_failed`；经 `_record_layout_validation_fact` 落
   journal，持久化失败不扰动 visit（沿用 BUG-055 语义）。
4. **测试用真实事故规模**：单测直接构造 7+9 的 plan（与真实 bundle 同规模），
   断言 plan_order_layout → render → `_validate_final_artifacts` 全链通过——
   这正是昨晚死掉的那条链的红→绿。

## Risks / Trade-offs

- [无界 tuple 削弱域模型自证] → 由上游问题集上限（64）与 REG-008 字节界兜底；
  delta 的 full-cardinality scenario 把这个不变量锁进 spec。
- [schema detail 进入修复反馈，可能被模型投喂放大] → detail bounded（3 条×120 字符），
  且只进受信验证通道，不进 untrusted 数据块。
- [回滚] → 单 commit 还原三处 + spec 归档可检索。

## Migration Plan

无数据迁移。旧 bundle 的 plan 读回不受影响（plan 契约未变）；已 blocked 的旧
bundle 不复活（一次性 run 语义不变）。

## Open Questions

（无。）
