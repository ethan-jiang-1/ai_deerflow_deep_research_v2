## Why

真实 003 run 4：九节点全完成、3 次模型调用成功、**零出版物**，`research.blocked`
收场。四个缺陷构成一条语义链——"证据不完美"被放大成"零交付"，而系统本该
诚实降级：交付真实部分结论 + 披露未收敛项。

- **BUG-054（源头）**：`materialize_report_plan` 的可写结论**唯一**来源是
  readiness critic 的 `ready_substantive` 判定。run 4 中 critic 对高置信、
  引用完备的 finding（548.4 GWh，CAPBIIA/Gasgoo 双源）判 insufficient →
  `writable_conclusions: []`。synthesis artifact 里已被 wave2 admission 放行的
  findings 在交付层被单点否决——"insufficient → 零结论"放大。
- **BUG-053（终端）**：零结论 + 1 不确定项的退化 plan 仍要求模型回显合成 id
  `"uncertainty:0"`。单元素集合的"排序"数学上唯一，模型调用是纯粹的失败面：
  run 4 三次全拒 → exhausted → blocked。
- **BUG-050（兜底）**：节点级 `_exhausted_update` 直接写 terminal blocked，
  绕过 gate kernel 的 `degraded_pass_on_exhaustion` 降级路径（runbook-003
  §5.1 的承诺两次落空）。降级决定权按 FieldOwnership 属 GATE，节点不能自判。
- **BUG-051（数据合同）**：wave1 修复重跑让不同 work unit 产出同 id
  `q:w1_q1`；`read_wave1_open_questions` 返回的重复 `(id, text)` 对在 wave2
  端被 `dict()` 静默折叠——问题文本丢失且无任何信号。

## What Changes

- **Decision A（054）**：可写结论增加**确定性第二来源**——synthesis artifact 中
  `confidence=high`、`backing_refs` 非空且 ⊆ accepted ledger、`search_required=
  false` 的每条 finding 直接成为可写结论（`conclusion_text=finding.statement`
  verbatim，`backing_claim_ids=backing_refs` 截 16）。critic 的 insufficient/
  blocked 判定**只能添加强制不确定项（披露）与触发修复路由**，不能删除
  finding 派生结论——"部分结论 + 强制不确定项并存"取代"insufficient → 零交付"。
- **Decision B（050）**：wave2_synthesis 的**预算类** exhausted（middleware
  budget/admission 拒绝类）不再直写 terminal：节点写入有界状态信号
  （新 FieldOwnership：wave2_synthesis 写、gate 读），以非终止更新交还 phase
  gate；gate 以既有 kernel 降级分支（预算耗尽 + marker 一次 + degraded_pass）
  决定诚实降级或终止。marker 仍由 GATE 写——一次降界的边界不放松。
- **053**：final_delivery 退化 plan（结论数 ≤1 且不确定项数 ≤1）走**确定性
  渲染分支**：单元素集合的完整排序唯一，node 直接构造 layout candidate，
  跳过 composer 模型调用；admission/renderer/publisher 管线不变。
- **051**：`read_wave1_open_questions` 对跨 work unit 同 id **不同文本**抛
  typed `wave1_open_question_id_collision`（经 BUG-046 pre-model guard 有界
  终止）；同 id 同文本静默去重（无害幂等）。不做 id 改名——gap
  `source_questions` 引用模型铸造的 id，改名破坏 wave2 coverage 合同。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `readiness-node`：REA-003 增补——report plan 的可写结论 SHALL 有 finding
  派生的确定性第二来源（高置信 + 引用完备 + 无检索需求），critic 非实质性
  判定 SHALL 只增披露与修复路由，SHALL NOT 清空 finding 派生结论。
- `final-delivery-node`：FID-001 增补——退化 plan（两类条目均 ≤1）SHALL 走
  确定性 layout 构造，不调用 composer。
- `wave2-synthesis-node`：解析 seam 增补——wave1 open-question id 跨 work
  unit 冲突（同 id 不同文本）SHALL typed 有界终止；预算类 exhausted SHALL
  非终止交还 gate。
- `gate-kernel`：增补——节点预算类失败经状态信号进入 gate 规则后，SHALL 沿
  既有降级分支（一次 marker）决定，不新增降级路径。

## Impact

- 代码：`readiness/materializer.py` + `readiness/node.py`（findings 读取与
  映射）、`work_unit_store.py`（`read_synthesis_findings` + 冲突检测）、
  `final_delivery/node.py`（退化分支）、`wave2_synthesis/node.py`（预算类
  hand-back）、`engine/real_gates.py` + `domain/state.py`（状态信号 +
  FieldOwnership）。
- 测试：readiness materializer 单测（finding 派生结论 + critic 否决边界）、
  final_delivery 退化分支 graph 测试、store 冲突单测、wave2 预算 hand-back
  graph 测试。
- 行为：003 在 honest gap 不收敛时以"真实部分结论 + Uncertainties 披露"
  completed 收尾；runbook-003 §5.1 措辞与实现对齐。
