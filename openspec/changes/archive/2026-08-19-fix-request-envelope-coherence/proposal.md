## Why

真实 003 run（2026-08-18 晚四次）暴露同一类病的两处发作：**必须成对推导的上限各改各的**。

- **BUG-047**（run 2）：readiness critic 构建器允许 8 KiB 证据投影，但节点 admission
  信封只许请求共 6 KiB（8192 total − 2048 output cap）——证据攒到 ~4.5 KiB 后 critic
  被确定性 `token_admission` 拒绝，4 次全拒驱动无界补证循环至 blocked。
  `final_delivery` composer 是同形缺陷（8 KiB 投影 + plan 投影配同一 8192/2048 信封）。
- **BUG-049**（run 3）：wave2 synthesis/repair prompt 把**全部** accepted 证据无界嵌入
  objective（无任何投影上限），第 6 条 accepted ref 时序列化超
  `NodeExecutionRequest.objective` 的 16,384 字符域上限 → pydantic ValidationError
  被兜底成 `candidate_invalid`（类别失真，BUG-048 第 5 项）→ 20ms 内 blocked。

两处共同教训：上限（admission 信封 / 域契约 / 构建器投影）不是孤立的魔法数字，
**任何一方的最大合法输入必须在其余各方的容纳范围内**。run 4 已验证本 change 的
主体修复有效（readiness critic 首次真正运行且一次通过；wave2 六条证据下不再溢出）。

## What Changes

- `runtime/research.py`：readiness critic 信封 `total_token_budget` 8192→16384、
  final-delivery composer 8192→24576（覆盖各自构建器最大投影 + 脚手架 + system
  prompt + 2048 output cap）；其余字段不动。
- `graph/nodes/wave2_synthesis/prompts.py`：synthesis 与 repair 两个 builder 改用
  **确定性有界证据投影**——32 KiB 预算起步、不满足 objective 双上限（≤16,384 字符
  且 ≤44,800 UTF-8 字节，由 wave2 64K 信封推导）时按 3/4 几何收缩；投影截断置
  `truncated` 标记；降到下限仍不满足时抛 typed
  `synthesis_evidence_projection_overflow`（可分类），不再让 pydantic ValidationError
  逃逸成 `candidate_invalid`。
- `graph/nodes/wave2_synthesis/node.py`：pre-model 类别保真——请求构造失败的
  ValidationError SHALL 归一为 pattern-safe 的具体类别（如
  `synthesis_request_shape_invalid`），不得落入与模型输出失败同义的
  `candidate_invalid` 泛化桶。
- 两个不变量测试锁死"构建器最大输入 ≤ 信封"：
  `test_evidence_embedding_requests_stay_within_admission_envelope`（readiness/
  final_delivery）与 `test_synthesis_prompts_bound_evidence_projection_within_request_limits`
  （wave2 双上限）。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `readiness-node`：critic 有界策略增补——构建器最大证据投影 + trusted system
  prompt + per-call output cap SHALL ≤ 节点信封 total_token_budget（admission 前
  可判定，测试锁死）。
- `final-delivery-node`：composer 请求有界性增补——同形信封一致性要求（plan 投影 +
  证据投影 + 脚手架 + system prompt + output cap ≤ 信封）。
- `wave2-synthesis-node`：WSN-008 增补——synthesis/repair 请求的证据投影 SHALL
  确定性有界并拟合 objective 域上限与 wave2 admission 信封；不可拟合时 SHALL 以
  typed 具体类别有界终止；pre-model 请求构造失败 SHALL 携带 pattern-safe 具体类别，
  SHALL NOT 折叠为 `candidate_invalid`。

## Impact

- 代码：`runtime/research.py`（两处预算）、`graph/nodes/wave2_synthesis/prompts.py`
  （有界投影拟合）、`graph/nodes/wave2_synthesis/node.py`（类别保真）。
  主体已在工作区实现并经 run 4 验证；本 change 收编并补类别保真。
- 测试：`tests/unit/test_research_runtime_capabilities.py`（信封不变量，已有）、
  `tests/graph/test_wave2_synthesis_real.py`（投影双上限不变量，已有；类别保真，
  新增）。
- 行为：真实 003 run 不再于 readiness/wave2 因确定性算术拒绝而 blocked；模型
  行为零变化（上限只放宽到覆盖设计输入，投影截断是确定性操作）。
