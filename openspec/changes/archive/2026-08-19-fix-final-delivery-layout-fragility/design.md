# Design — fix-final-delivery-layout-fragility

## Context

BUG-055 的三层根因与既有代码事实（引用当前实现，apply 时以代码为准）：

- `graph/nodes/final_delivery/composer.py`：`parse_layout_candidate` 裸
  `json.loads`；`admit_layout_candidate` 做闭合集合校验
  （`schema_version==1` + conclusion/uncertainty id 集合恰好完整）。既有
  canonical ValueError 码：`final_layout_empty` / `final_layout_json_invalid` /
  `final_layout_not_object` / `final_layout_schema_unsupported` /
  `final_layout_conclusions_invalid` / `final_layout_uncertainties_invalid`。
- `graph/nodes/final_delivery/node.py`：退化分支（两计数 ≤1）已确定性构造
  plan-order layout（BUG-053）；非退化分支一次 composer 调用，任何异常被
  `except Exception` 折叠成 `WORK_FAILED` gate view。
- `engine/real_gates.py`：final gate `default_budget=3`，`WORK_FAILED → repair`，
  耗尽 → `exhausted` → blocked。本 change 不改 gate。
- 观测缝已存在：`domain/run_observation.py` 的
  `classify_final_response_shape`（`empty/prose/fenced/embedded_json/json_object`
  ，只分类不提取）；wave0/wave1 subgraph 经
  `NodeBuildDependencies.observation_projection`（builder 统一注入）发
  `initial`/`repair` validation fact。REJ-007 名单未含 final_delivery。
- Journal 纪律（REJ-002/007，RTO）：validation fact 只带闭合 code/stage；
  invocation 失败只留 invocation fact；任何面不保留 raw 模型输出。

## Goals / Non-Goals

**Goals**

1. layout 级失败（composer invocation / parse / admission）不再可能使 run
   blocked——同 visit 确定性降级发布。
2. final_delivery 的 admission 失败码以闭合 validation fact 进入 journal，
   消灭"失败码被吞"。
3. parser 接受 fenced / embedded-json 投递形状（与 journal 既有形状分类学对齐）。

**Non-Goals**（proposal Not in scope 之外的设计边界）

- 不移除非退化 plan 的 composer 调用（见决策 D1 的备选讨论）。
- 不引入节点内模型 repair 循环（workflow.md 明确"no invented repair branch"；
  降级路径取代 repair，而不是模拟 wave0 的 repair）。
- 不给 journal 增加新字段/新 stage/新 category——只扩 REJ-007 的边界名单。
- 不动 `FinalDeliveryGateView` 形状与 gate 规则——降级后的 pass view 与正常
  pass view 同形，gate 无感知。

## Decisions

### D1：降级而非移除 composer（advisory 排版）

**决策**：非退化 visit 仍调用 composer；其候选失败时降级为 plan-order layout
（与退化分支同一构造函数产出、同一条 admission→render→publish→readback-verify
路径），不产生 `WORK_FAILED`。

**理由**：layout 排列是纯排版决定，plan-order 本身就是 readiness 认可的优先序
——降级不损失任何实质内容。而移除 composer（备选）会推翻 BUG-053 刚确立的
"composer SHALL remain the path for every non-degenerate plan"（FID-001 现行文），
且 003 的验收价值含"真实链路每个环节真实模型角色"；把它降为 advisory 既消灭
run 级否决权，又保留架构演示价值。blocked 从此只剩结构性失败一类，与
runbook-003 §5.1 既有口径对齐。

**备选否决**：
- 移除全部 composer 调用：推翻一天前刚定的 FID-001 条文，收益仅省一次调用。
- 只做归一化不做降级：失败概率降一个量级，但 run 生死仍押在排版回显上
  （BUG-055 的 P1 本质未除）。
- gate 侧放宽（budget↑或 route 改）：治标，且把排版问题抬到 gate 层不合职责。

### D2：降级触发条件 = "composer 未产出 admitted 候选"，覆盖两类失败

**决策**：invocation failure（`invoke_and_normalize` 返回
`InvocationFailure`）与 parse/admission failure 都触发降级。区别仅在观测：
- parse/admission 失败 → 发一条 `initial`-stage validation fact（闭合
  `final_layout_*` code），因为候选已到达 parser 边界（REJ-002 规则）。
- invocation 失败 → 不发 validation fact（既有 model_tool invocation fact 已
  由 bridge 记录；REJ-007"invocation failure before the boundary remains the
  existing invocation fact"）。

**理由**：两类失败的共同点是"排版建议不可得"；既然内容不依赖模型，恢复动作
相同（plan-order）。观测差异遵循既有 journal 纪律，零新增字段。

### D3：归一化只做"投递形状"，不做"内容宽容"

**决策**：`parse_layout_candidate` 归一化顺序——strip → 裸 `json.loads` →
fenced code block 内容提取 → 首个平衡 JSON 对象扫描（`raw_decode`，与
`classify_final_response_shape` 的 embedded-json 判定同算法族）。归一化产物
仍必须通过**原样**的 `FinalDeliveryLayoutCandidate` 校验 +
`admit_layout_candidate` 闭合集合校验：不猜 id、不修 schema、不补缺项。

**canonical code 坍缩**（镜像 wave0 `_canonical_validation_code` 惯例）：
composer/admission 抛出的 ValueError 中，六个字面码
（`final_layout_empty/json_invalid/not_object/schema_unsupported/
conclusions_invalid/uncertainties_invalid`）原样透出；其余一切类型化校验
细节——Pydantic `ValidationError`（如非 int 的 schema_version、非 str 的
entry id）、模型内 `conclusion_order_duplicate`/`uncertainty_order_duplicate`
——坍缩为第七个闭合码 `final_layout_shape_invalid`（"JSON 对象解析成功但
未通过类型化 layout 形状"）。journal fact 只携带这七个闭合码。

**理由**：宽容投递形状（模型把 JSON 包进 fence/散文是分布常态）但严守内容
（admission 语义是 FID-003 的引用完整性基础）。提取逻辑放
`final_delivery/composer.py` 本地（trusted parser 边界），**不**改
`domain/run_observation.py` 的 classifier——那个模块的合同是"只分类不提取"
（观测安全），混入提取函数会破坏其单一职责；两处算法相似是可接受的重复
（各 ~15 行，语义不同：分类 vs 提取）。

### D4：validation fact 走既有 event_recorder 缝（journal），live 投影可选

**决策**：journal validation fact 经
`NodeBuildDependencies.event_recorder`（builder 统一注入，可能为 None），镜像
topic_planning 的 `_record_validation_observation` 形状：
`record(category=VALIDATION, phase="final_delivery", validation_stage="initial",
validation_codes=(canonical,))`——不带 response_shape（RunEvent 合同已把
shape 限定在 wave0/wave1，`domain/run_observation.py` 的
phase-scoping 校验对 final_delivery 本就要求无 shape），不带 attempt_id（与
topic_planning 的 validation fact 同形；attempt 相关性由节点 attempt 事件序
列承载）。包 `try/except: return`（观测失败不得扰动执行，与既有节点一致）。
可选加发 observation_projection 的 live/log 字段（同 topic_planning：
`operation=validation, outcome=rejected, code=validation_rejected`）——RTO 面
闭合谓词里 `validation` 只允许 `rejected`，恰好匹配。

**理由**：零新缝、零新字段；`event_recorder` 已在 builder 对所有 real 节点注入。
先例同构：readiness 的 critic 失败已有"保守替换 +
`readiness_critic_fallback.{reason}` 观测"模式（BUG-047/050 时代修复）——
本 change 的 layout 降级是该模式在 final_delivery 的对应物。

### D5：结构级失败路径原样保留 + 目标控制流

plan 引用缺失/发散、evidence 读取、render、publish、readback/hash/shape
verify 失败 → 维持现行为：该 attempt 无发布 + `WORK_FAILED`（或
evidence 缺失 → `EVIDENCE_INSUFFICIENT`）gate view → 既有 repair/blocked。
实现上 `except Exception` 只包裹结构级操作段；layout 获取段独立成函数，
其失败走 D2 降级分支，不再落入同一个吞码的 try。

重构后的 visit 控制流（伪码，apply 以此为准）：

```
plan_ref 缺失 / plan 读失败        → WORK_FAILED view（不变）
accepted evidence 缺失             → EVIDENCE_INSUFFICIENT view（不变）
try:                                 # 结构级保护段（不变）
  evidence = read_synthesis_evidence(...)
  if 退化 plan:
      layout = plan_order_layout(plan)            # 不变（免模型）
  else:
      outcome = invoke_and_normalize(composer)    # CancelledError 自然传播
      if isinstance(outcome, InvocationFailure):
          layout = plan_order_layout(plan)        # 降级，无 validation fact
      else:
          try:
              layout = admit(parse(outcome.text), plan)
          except ValueError as exc:
              await record_validation_fact(canonical(exc))  # D4，失败静默
              layout = plan_order_layout(plan)    # 降级
  report, cmap = render(plan, layout)             # 以下全部不变
  refs = publish(report, cmap)
  readback + hash/shape verify
except Exception: → WORK_FAILED view（不变）
→ published view（pass）
```

`canonical(exc)`：六个字面码原样；其余 ValueError（含 Pydantic
ValidationError、duplicate-order）坍缩 `final_layout_shape_invalid`。
降级构造与渲染/发布/校验共用同一路径；gate view 形状不变。

## Risks / Trade-offs

- **排版降级不可见于报告正文**：报告内容与成功路径逐字节同构（renderer 只消费
  plan 文本 + 引用），故不在 `final/report.md` 披露；可见性在 journal
  validation fact。若未来产品认为"排版由模型决定"是用户可感知承诺，需另立
  change——本 design 记录为已知边界。
- **composer 变成永不失败的 advisory 调用**：模型质量漂移不再有 run 级信号，
  只有 journal 信号。评估面（tests/eval）若要跟踪 composer 回显质量，读
  validation fact 即可。
- **归一化的 embedded-json 扫描接受"散文里恰好有合法 JSON"**：这是刻意宽容
  （与 wave 分类学一致）；内容仍被 admission 闭合校验兜底，不存在把散文当
  layout 的路径。
- **测试面**：`test_rejected_layout_and_readback_failure_never_publish_a_pass_view`
  的"rejected layout"半边语义反转，需拆分改写（见 tasks）。

## Migration / Compatibility

- 无状态/存储迁移：gate view、journal schema（v3）、run-summary（v2）均不变。
  RunEvent 的 response_shape phase-scoping（wave0/wave1 专属）已存在于
  `domain/run_observation.py`——final_delivery 无 shape 的 validation fact
  当前类型合同即合法，零 domain 改动。
- 旧 bundle 的 journal（无 final_delivery validation fact）依旧合法——REJ-007
  名单扩展只约束新写入。
- 002 scripted / full-fake 路径的 final_delivery 是 fixture adapter
  （`src_fake/.../final_delivery/adapter.py` 直接返回 state update），不经过
  real composer 分支，行为不变。
- `tests/scenarios/final_composition_calibration.py`（live-only 校准语料）直接
  调 composer 的 parse/admit/render 面：归一化只放宽可接受的投递形状，语料的
  request/projection/rubric 断言不受影响。
- 已知既有漂移（本 change 不处理、不扩大）：`gate-kernel` 主 spec 写
  "final_delivery self-repair SHALL default to 1"，而 `real_gates.py` 为
  `default_budget=3`（今日真实 run 亦为 3 次尝试）。属 spec 与实现的既有
  不一致，另行处理，不进本 change 范围。

## Open Questions

（无——两个 spec delta 与本 design 已消解 BUG-055 卡中"待讨论方向"的 1/2/3/4
取舍：采纳 1+2+3，4 的彻底确定性由 1 的降级语义等效覆盖而保留 composer。）
