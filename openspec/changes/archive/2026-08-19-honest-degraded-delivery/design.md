# Design: honest-degraded-delivery

## Context

003 run 4 链条：synthesis 产出高置信 finding（548.4 GWh，双源引用）→ readiness
critic 判 insufficient → `writable_conclusions: []` → 退化 plan 仍要模型回显
`"uncertainty:0"` → 3 拒 → exhausted → blocked。九节点全绿、零出版物。

## Goals / Non-Goals

- **Goal**：honest gap 不收敛时，run 以"真实部分结论 + Uncertainties 披露"
  completed 收尾；003 拿到 PASS。预算类节点失败经 gate 一次性诚实降级。
- **Non-Goal**：不改变 wave2 admission/gap 语义（findings/gaps 的产生侧不动）；
  不给 final_delivery 增加降级路径（FID-004 exhausted=blocked 保持，退化分支
  已消灭其最常见的模型失败面）；不改 critic prompt（否决权语义不变）。

## Decisions

### D1（054，Decision A）finding 派生结论：规则为主，critic 只增披露

可写结论的确定性第二来源：synthesis artifact（canonical `synthesis/findings.json`，
wave2 admission 已放行）中每条 `confidence=high ∧ backing_refs≠∅ ∧
backing_refs⊆accepted_refs ∧ search_required=false` 的 finding →
`ReportPlanConclusion(question=f"Finding {finding_id}", conclusion_text=statement
verbatim, backing_claim_ids=backing_refs[:16])`。

- 为什么 finding 可以越过 critic：findings 已过 wave2 的 evidence-grounded
  admission（引用必须指向 accepted 证据是 admission 规则）；critic 只看 8 KiB
  截断投影，证据视野严格更小。两者冲突时交付层选视野更大、已被 admission
  约束的一侧，同时把 critic 的判断作为强制不确定项**原样披露**——不隐瞒
  分歧。
- `question` 字段用 `Finding {finding_id}`：renderer 以 question 为标题、
  conclusion_text 为正文；finding_id 稳定、有界、可回链 synthesis artifact。
- 截 16：`ReportPlanConclusion.backing_claim_ids` 域上限 16（finding 侧 32），
  确定性取前 16；多引用 finding 的完整引用留在 claim-citation-map（由 plan
  驱动，同 16 上限）——与现有 question 派生结论同界。

### D2（053）退化 plan 确定性渲染：单元素集合的排序唯一

`len(conclusions) ≤ 1 ∧ len(uncertainties) ≤ 1` 时完整合法排序唯一，node 直接
构造 layout candidate（plan 顺序），零模型调用。admission（exact-set 匹配）、
renderer、publisher 管线不变——candidate 的来源从"模型回显"变为"确定性构造"，
后续验证全同。非退化 plan 照旧走 composer。

### D3（050，Decision B）预算类失败交还 gate：不新增降级路径

- 节点侧：`_exhausted_update` 的预算类分支（`NodeFinishReason.BUDGET_EXHAUSTED`
  / admission 拒绝类 `NodeProblem`）不写 terminal，改写有界状态信号
  `wave2_budget_exhausted: bool`（FieldOwnership：wave2_synthesis 节点写、
  gate 读），返回非终止更新。
- gate 侧：wave2 gate def 注册规则把该信号投影为 repairable Failure；此后走
  kernel **既有**分支——budget 递减 → REPAIR（targeted evidence 重试）→
  预算耗尽 + marker 缺席 + degraded_pass_on_exhaustion → 一次诚实降级 pass；
  marker 在场 → blocked。疲劳指纹照常累计（同指纹 3 连击提前 blocked）。
- 为什么不改 kernel：`degraded_decisions` 写权属 GATE（FieldOwnership 硬约
  束）；节点自判降级必违反所有权。把失败交给 gate 是唯一所有权干净的路径，
  且 kernel 的预算/marker/疲劳机制已经完备。
- 为什么只做 wave2：final_delivery 的 exhausted=blocked 是 FID-004 契约，且
  D2 已消灭其主失败面；readiness 的 budget 失败走 conservative 投影（REA-006
  契约）。范围最小化。

### D4（051）冲突显式化，不改名

`read_wave1_open_questions` 在返回前检测同 id 跨文档不同文本 → 抛
`ValueError("wave1_open_question_id_collision")`（进 BUG-046 pre-model guard →
typed 有界终止）；同 id 同文本静默去重。**不做** work 前缀改名：gap
`source_questions` 与 `resolved_questions` 引用模型铸造的 id，投影改名会让
wave2 coverage 合同两边（prompt 指派 vs 模型输出）id 体系分裂。碰撞是数据
事实，显式失败优于静默改写。

### D5 Spec delta 范围收窄（4 个，原计划 7 个）

计划列了 7 个 delta；实施设计后收窄到 `readiness-node`、
`final-delivery-node`、`wave2-synthesis-node`、`gate-kernel`：051 修在 store
解析 seam（wave2 spec 的 coverage requirement 已覆盖该读合同），wave1 节点
零改动；050 不新增终态语义（复用既有非终止路由 + gate 分支），
`research-graph-lifecycle` 无合同变化；003 验收语义（PASS = completed + 报告
工件）不变，`low-scale-real-auto` 无需 delta。少改 spec 即少一份未来漂移面。

## Risks / Trade-offs

- [finding 派生结论可能与 critic 判断矛盾] → 不隐瞒：critic 判定同版披露为
  mandatory uncertainty；报告读者同时看到结论与限制。
- [D3 的 hand-back 引入 targeted evidence 重试放大成本] → kernel 预算上限
  （resolver 2）+ 疲劳 3 连击封锁；降级 marker 一次。有界。
- [D2 退化分支与 composer 路径行为漂移] → 退化 candidate 走**同一**
  admission/renderer/publisher；graph 测试断言两条路径产物一致。
- [051 显式失败把此前"碰巧能跑"的 run 变成 blocked] → 那些 run 的问题文本
  本来就被静默丢弃（结论建立在残缺指派上）；typed 失败可诊断、可修复，
  诚实优于静默。

## Migration Plan

- `wave2_budget_exhausted` 新 state 字段：FieldOwnership 注册（wave2_synthesis
  writer）+ 默认 False；旧 checkpoint 无此字段按缺省读——无迁移。
- report plan / synthesis artifact 格式零变化（D1 读既有 findings，不写新工
  件）。
- runbook-003 §5.1 按实现边界改写：wave2 预算类失败经 gate 一次降级；
  final_delivery 退化 plan 确定性渲染；critic 分歧以披露共存。
