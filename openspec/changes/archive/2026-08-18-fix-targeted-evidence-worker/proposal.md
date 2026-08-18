## Why

真实 003 run（BUG-045）中 wave2 补证循环 9/9 attempts 全部 `work.failed`：
targeted worker 按模型输出顺序构建 `source_refs`，而
`CandidateResult.source_refs` 校验器要求 `(source_id, canonical_url)`
字典序（`source_refs_not_canonical`）——候选提交前必败，补证零产出，
gap 永不收敛（wave1 worker 显式排序、是正确的范式；wave0 同缺陷类、本次
侥幸）。同一 run 中模型 9/9 次诚实报告：assigned gap 只有裸 id
`gap:gap_1`、无描述无上下文，单次搜索只能搜出方法论文章——即便排序修复，
worker 也无法有效定位 gap 内容。两个问题叠加使 wave2 honest gap 结构性
不可收敛。

## What Changes

- targeted_evidence worker（`graph/nodes/targeted_evidence/subgraph.py`
  `run_gap_workers.worker`）：构建 `source_refs` 前按
  `(source_id, canonical_url)` 排序（与 `wave1/subgraph.py` 一致），使候选
  通过既有校验器，补证证据真正进入 ledger。
- wave0 worker（`graph/nodes/wave0/subgraph.py`）：同类缺陷防御性修复
  （同样排序；模型输出本就有序时行为不变）。
- targeted worker 请求（`prompts.py build_targeted_worker_prompt` + node）：
  携带 assigned gap 的**有界描述**作为检索上下文。描述只来自 canonical
  synthesis artifact（`store.read_synthesis_gaps()`，与 readiness 同一
  bounded 读），按 gate 投影的 gap id 联接；**不参与路由/调度**（TEL-001
  的 id-only 路由权威不变）。
- 不改 wave2 gate、不改预算、不改收敛门。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `targeted-evidence-loop`: TEL-002 增补——worker 输出 source refs 必须
  canonical 有序才可提交；worker 请求必须携带 assigned gap 的有界描述
  （来自 canonical artifact、仅作上下文、不参与路由）。
- （无 `work-unit-kernel` delta：source_refs canonical 序已由既有提交校验器
  强制，本 change 只是让 worker 遵守契约。）

## Impact

- 代码：`graph/nodes/targeted_evidence/subgraph.py`、`prompts.py`、
  `graph/nodes/wave0/subgraph.py`（排序防御）；无 engine/domain 核心改动。
- 测试：`tests/graph/test_targeted_evidence_real.py` 增补排序与描述上下文
  用例；wave0 worker 用例防御性覆盖。
- 行为：真实 003 的 wave2 补证循环可产出并提交证据（gap 描述到位后单次
  搜索可命中主题），honest gap 有真实收敛路径；不收敛时仍走 BUG-044 的
  降级交付。
