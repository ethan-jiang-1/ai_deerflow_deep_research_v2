# BUG-055: 非退化 plan 的 final_delivery layout 回显 3/3 拒绝致 run blocked——admission 失败码被吞、模型原文无观测

> 严重级别: P1 | 发现: 2026-08-19 | 状态: 已修复（2026-08-19）

## 症状

第五次真实 003 run（bundle `b_hCdqf6hMon6v6VExodcf1GpmSg_MIWqRLtaCi-qT1mI`，诊断引用
`diag_289dd512ee28ffefbdae111d`）：

- 前序全部打通：hitl2 → readiness 一次通过，wave2 走降级
  （`state.degraded_profile=true`），`synthesis/findings.json` 有 2 条真实
  findings（548.4 GWh / CATL 246.01 / BYD 135.02 等）+ 3 个 honest gap。
- `final_delivery` 3 次尝试、**模型调用 3 次全部 completed**（事件 112-123，
  18:37:48→18:37:58 共约 10 秒，非挂起；每次 usage 约 4600 in / 344-440 out），
  但 `final/report.md` 未发布，`final/` 目录为空，终态
  `terminal_status=blocked`、`terminal_reason=gate_blocked`、
  `latest_incident=research.blocked @ final_delivery`，`RESULT: FAIL`。
- `review/report-plan.json` 实况：`writable_conclusions: 2` +
  `mandatory_uncertainties: 3`——**非退化 plan**（BUG-053 的确定性渲染分支
  不覆盖：两计数均 >1，排序不唯一，走模型路径）。

## 根因

`final_delivery/node.py` + `composer.py` 的 layout 合同残余缺陷（BUG-053 只修了
退化分支）：

- 非退化 plan 要求模型精确回显合成 id
  `{"schema_version":1,"conclusion_order":["conclusion:0","conclusion:1"],"uncertainty_order":["uncertainty:0","uncertainty:1","uncertainty:2"]}`；
  `parse_layout_candidate`/`admit_layout_candidate` 对 fence 包裹、散文前后缀、
  id 形状偏差一律抛 ValueError。
- `node.py` 的 `except Exception` 把具体错误码（`final_layout_json_invalid` /
  `final_layout_conclusions_invalid` / …）**吞成泛化 WORK_FAILED** gate view；
  gate `default_budget=3` + `WORK_FAILED → repair`，3 次耗尽 → `exhausted` →
  `research.blocked`。此前全部真实研究产出（wave0/wave1/wave2 真实证据与
  findings）随之不交付。
- **观测缺口**（BUG-053 卡已点名、BUG-048 修复未覆盖此路径）：journal 里
  final_delivery 3 次尝试没有任何 validation 类事件，错误码不可见；模型实际
  返回文本不落盘，无法区分"fence/散文包裹"还是"id 回显错误"。旁证：3 次输出
  均 344-440 tokens，而合法 layout 回显约 60 tokens 即可，指向模型返回了
  prose/包裹物。
- 对照证据（波动性）：2026-08-19 早间 PASS 的 run（bundle
  `b__sZxRIhwTO19O0lHNM-EZGVr6L4P9UUKC-AVabSCUQw`，3 conclusions + 1
  uncertainty，同样非退化、同样模型路径）一次回显成功——说明是模型波动触发
  的契约脆弱点，不是必现。
- 追加对照（同日复跑）：立即重跑 PASS（bundle
  `b_q6s6QMeBYnXGVanvW-JvQfBB7p4Vu1EwwzHAjRpKdcA`，事件 68-75：final_delivery
  a1 admission 失败一次、a2 成功发布，`RESULT: PASS`）。同一 build 内"a1 拒、
  a2 过"直接证实逐次波动，且 gate repair 预算（3 轮）通常能吸收单次失败——
  BUG-055 触发条件是连续 3 次都失败。

## 复现

任一 readiness 产出非退化 plan（结论数或不确定项数 >1）的真实 003 run，模型
只要 3 次都不精确回显合成 id 即复现（本次 3/3 失败；同日早间 1 次成功）。

## 证据

- bundle: `.deep-research-demo-runs/workspace/deep-research/scopes/s_4ir6xpt2TBI3rRvjHEiSW8iR9hOVB1sRoRbo0clI_1Y/b_hCdqf6hMon6v6VExodcf1GpmSg_MIWqRLtaCi-qT1mI`
  （rerun 前会被移入 `workspace/archive/`，BUG-052 修复保证不销毁）
- `diagnostics/events.jsonl` 序列 112-124；`diagnostics/run-summary.json`
  （status=blocked, failure_category=research.blocked, policy envelope
  final-delivery-composer 24576/2048/1）；`review/report-plan.json`（2+3）；
  `synthesis/findings.json`（2 findings + 3 gaps）；`state.json`
  （degraded_profile=true, terminal blocked）。

## 修复关联

已由 change `fix-final-delivery-layout-fragility` 修复（2026-08-19，已归档，主 specs
已同步）：
- parser 归一化（fenced/embedded 投递形状）；admission 失败码以闭合
  `final_layout_*`（含新增坍缩码 `final_layout_shape_invalid`）进 journal
  `initial` validation fact（REJ-007 名单扩展）；
- composer 调用/候选失败 → 同 visit plan-order 降级发布，排版不再拥有 run 级
  否决权；结构性失败（读取/render/publish/verify）仍走既有 repair；
- 验证：单元/集成/一致性套件 + 002 回归 + 真实 003 复跑 `RESULT: PASS`。

（原"待讨论"方向 1/2/3 采纳；方向 4"彻底移除模型回显"被降级语义等效覆盖——
composer 保留为 advisory 排版建议，见 change 的 design D1。）

## 补充证据（已含于正文）


1. **admission 失败码透出**（最低成本）：node 捕获时区分
   parse/admission/render/publication 失败码写入 gate view 或 journal validation
   事件，先消灭观测缺口；
2. **候选规范化**：parser 剥离 code fence / 前后 prose 后再 `json.loads`（仓库
   其他 structured 输出路径的既有惯例）；
3. **admission 放宽**：集合相同但顺序/形状不严格时接受或规范化（排序本身对
   渲染只有排版意义）；
4. 或把 layout 选择也做成确定性（如按 priority 排序），彻底移除"run 生死押在
   模型回显合成 token 上"的设计。
