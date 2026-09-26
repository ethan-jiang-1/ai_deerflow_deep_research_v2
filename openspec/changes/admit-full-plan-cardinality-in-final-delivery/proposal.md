# Proposal

## Why

demo-real Gateway 路线首次抵达 `final_delivery` 后确定性死亡：真实 run 的 readiness
plan 含 9 个 mandatory uncertainties，而 `FinalDeliveryLayoutCandidate` 的两个 order
字段带 `max_length=8`（spec 从未背书的早期假设）——composer 候选与确定性降级路径
`plan_order_layout` **双双**在同一个 pydantic 上限上抛错，被兜底 `except Exception`
静默吞掉 → WORK_FAILED×3 → `gate_blocked`。这直接违反 final-delivery spec 明文
"no visit SHALL fail, block, or lose its delivery solely because the composer's
ordering was unavailable or inadmissible"。同族缺口还有两个：
`parse_layout_candidate` 的裸 pydantic ValidationError 被折叠成
`final_layout_shape_invalid`（composer 修复轮零反馈，wave2 同款病灶），
以及 render/publish/read-back 失败不留任何 journal 事实（本次取证被迫全离线复现）。

## What Changes

- `FinalDeliveryLayoutCandidate.conclusion_order/uncertainty_order` 移除
  `max_length=8`，与 plan 契约（`ReadinessReportPlan` 的无界 tuple）对齐；自然上界
  由既有机制承担（wave1 开放问题上限 64、REG-008 checkpoint 字节界、plan 条目字段界）。
- `parse_layout_candidate` 捕获 pydantic `ValidationError` → 封闭类别
  `final_layout_schema_invalid` + bounded detail（loc/type/msg 投影，与 wave2 G1
  的 `_schema_detail` 同构）；该类别加入 `_LAYOUT_LITERAL_CODES`，journal 记录具体
  类别而非折叠码。
- final_delivery 的 render/publish/read-back `except Exception` 在返回 WORK_FAILED
  前记录一条封闭码验证事实（closed 集内的原码直记，其余记
  `final_delivery_readback_failed`），终结静默失败。
- MODIFIED `final-delivery-node` FID-001：requirement 增补两句（order 字段 SHALL
  容纳 admitted plan 的全部条目；schema-invalid 但 JSON 合法的投递 SHALL 记具体
  封闭类别而非折叠码），新增两个 scenario（9-uncertainty plan 全链通过；
  read-back 失败留封闭码事实），全部既有文本与 scenario 原样保留。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `final-delivery-node`: FID-001 增补基数对齐与封闭类别反馈两句 + 两个新 scenario；
  其余四个 requirement 不变。

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/publication.py`
  （order 字段约束）、`graph/nodes/final_delivery/composer.py`（parser 折叠 +
  detail）、`graph/nodes/final_delivery/node.py`（字面码集合 + read-back 留痕）。
- 测试：新单测（真实规模 plan 的 plan_order_layout/render/validate 全链、
  schema-invalid 投递的封闭类别与 detail、read-back 失败的事实记录）。
- 验收面：`UV_OFFLINE=1 make verify` + `check_project_gate.py --phase closeout` +
  strict validate；随后真机重跑 `make demo-real` 验证 final_delivery 通过
  （配方与 stdin 脚本见 `_backlog/plans/demo-real-gateway-closeout.md`）。
- 无准入语义放宽：布局仍须 complete、duplicate-free 的全排列；只是不再用任意常数
  拒绝合法 plan。

## Change Focus

- **Primary module / causal owner:** `domain/publication.py` 的 `FinalDeliveryLayoutCandidate` order 字段约束——"一个 admitted plan 的布局候选能否构造"的语义决定点。
- **Seam classification:** deterministic-guardrail —— 修复确定性契约之间的不匹配（plan 契约 vs 布局契约），不新增任何认知面；composer 的模型角色、准入 owner、渲染/发布路径全部不变（选 guardrail：纯确定性边界修正，无认知/人决/接线语义）。
- **Question:** 布局候选的 order 字段应容纳多大的 admitted plan，以及被拒投递/read-back 失败在 journal 里留下什么？
- **Necessary adjacent/external contracts:** `final-delivery-node` spec FID-001（降级路径 SHALL 交付的明文，本 change 把它落为代码事实）；`readiness-node` spec 的 plan 物化契约（uncertainties 无基数上限、blocked judgment 不得消失——否决砍 plan 侧的备选）；wave2 G1 的 `_schema_detail` 先例（反馈投影同构）；REG-008 checkpoint 字节界（无界 tuple 的真实安全网）。
- **Evidence seam:** 节点级确定性单测（真实规模 plan 全链构造、封闭类别断言、journal 事实断言）+ `UV_OFFLINE=1 make verify` + `check_project_gate.py --phase closeout`。
- **Not in scope:** composer 提示词、readiness 物化逻辑、wave2/其他节点、嵌入式/Gateway 驱动差异、报告内容质量。
- **Triggered review policies:** none: 纯确定性契约对齐与封闭词表反馈，无认知面、无 workflow outcome 变化、无 node-agent 参与面变化。

边界声明：本 change 不修改 `deerflow/` gitlink，不触碰框架源码。
