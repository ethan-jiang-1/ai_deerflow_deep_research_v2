# BUG-023: HITL1 brief prompt 要求 schema 禁止的语言字段

> 严重级别: P1 | 发现: 2026-08-02 | 状态: 已修复，已归档

## 症状

历史上的 HITL1 prompt 曾要求 `brief_summary_language`；模型照此输出时，严格
`StructuredBrief` 解析会拒绝额外字段，从而不能进入用户确认或后续检索。保留的真实
`research.blocked` 终态不能单独证明正是该字段导致阻断。

## 根因

战术修复已从 `graph/nodes/hitl1/prompts.py::build_brief_prompt` 的 model-visible output
contract 移除 `brief_summary_language`。语言约束继续由 `brief_summary` 指令和解析后的
语言校验承载。剩余风险是 prompt descriptor 日后再次与 strict parser 漂移，因此
`HIN-013` 要求初始和 structural-repair descriptor 都经由 parser-compatibility fixture
验证，并保留既有两次 brief invocation / repair-exhausted 路径。

## 复现

1. 从 `deerflow_research/` 执行 `bash run/real-research.sh`。
2. 对返回的 HITL1 summary 调用
   `parse_brief_output(summary, expected_output_language=SupportedLanguage.EN)`。
3. 为初始与 repair request 解析 `expected_output`；构造所有 advertised required field 的
   canonical payload 应被 parser 接受，而添加 `brief_summary_language: "en"` 必须仍得到
   strict extra-field 拒绝，且不得写入部分 profile/checkpoint authority。

## 修复关联

本 bug 的收口由 OpenSpec change `harden-real-research-external-io` 管理；parser 仍是唯一
admission owner，CLI 只投影既有 typed terminal，而不推断或重写类别。

验收条件：

- 初始与 repair 模型 expected output 均覆盖 parser-required fields，只声明 parser 接受的
  fields，且 advertised enum/bounds/schema version 能被 strict parser 接受。
- `brief_summary_language` 继续被拒绝；已有 `brief_summary` 语言约束和解析后的语言验证保留。
- output-contract failure 只走既有 repair/exhausted path，不写入部分 profile/checkpoint，且
  terminal CLI 保留 `output.structured_invalid` 等安全类别。
- 在确定性证据通过后，单条有界真实 canary 至少记录是否到达首次 HITL1 suspension 或更后阶段；
  外部失败不自动宣称为 schema bug 已复现或已关闭。

## 本次实施证据（2026-08-03）

- `HIN-013` 的初始/repair prompt-parser compatibility fixture、两次 invocation 的 no-profile lifecycle replay，以及 CLI typed-terminal projection 已纳入合并确定性 lane；该 lane 为 `125 passed`，测试资产、需求注册和需求覆盖检查均通过。fixture 明确拒绝 `brief_summary_language`，并证明该 extra field 不会发布 profile 或 checkpoint authority。
- preflight 通过后仅运行一次 `bash run/real-research.sh`：run `r_YFc9zaYkbQmoU2wU5O0YyNavljOE8I4wc_HiirXlSFE` 返回 `research.blocked`，阶段 `hitl1`，诊断 `diag_YZ_PWs_cyMwf5j5Pr-ke8pVv`。未到达首次 HITL1 suspension 或后续阶段，也没有执行手工重试。

该终态不是 `output.structured_invalid`，不能归因为已移除的语言字段。它记录的是独立的 HITL1 阻断，不能覆盖或推翻 prompt/parser 直接契约的确定性结论。

## 关闭证据（2026-08-03）

- 以历史实际 prompt `5888c6b:deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/prompts.py` 做无模型差分回放：旧 `build_brief_prompt(..., output_language="en")` 在 model-visible descriptor 中要求 `brief_summary_language: "en"`；按该 descriptor 构造的完整 candidate 被同一严格 `StructuredBrief(extra="forbid")` parser 拒绝。当前 descriptor 不再声明该字段，同一合法 candidate 被 `parse_brief_output(..., expected_output_language="en")` 接受。
- 当前回归验证初始与 repair descriptor 都只声明 parser-accepted fields，显式拒绝该 extra field，且 double-invalid lifecycle 只走现有两次 repair/blocked 路径、不发布 profile 或 checkpoint authority；与 BUG-022/CLI 邻接边界的选择集为 `24 passed in 1.45s`。

因此本 bug 的 prompt/schema 冲突已由可重复的红绿差分和 lifecycle 回归证据关闭。该结论不把无关的 `research.blocked@hitl1` 误报为 schema 故障，也不承诺所有模型输出均合法。
