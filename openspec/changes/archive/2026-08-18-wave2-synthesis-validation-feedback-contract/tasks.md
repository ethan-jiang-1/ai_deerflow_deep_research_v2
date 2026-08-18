# Tasks: Wave2 Synthesis Validation-Feedback Contract Fidelity

## 1. 治理登记

- [x] 1.1 更新 `openspec/governance/req-registry.yaml`：MODIFIED `WSN-001`（有界终态对语义失败投影具体验证类别、parse 失败保留 `output.structured_invalid`），新增 `WSN-010`（repair 携带完整 open-question 处置契约 + 具体覆盖细节）与 `WSN-011`（输出契约含具体示例与负面对照），owner 均为 `wave2-synthesis-node`；不新增 WSN-012（终态投影属 WSN-001 行为变更，不是新 requirement）。
- [x] 1.2 跑 `python3 openspec/governance/check_project_reqs.py` 与 `check_project_architecture.py`，确保治理检查通过；如 req-registry 或 project-structure 需要更新路径/条目，按 `architecture-policy.md` 协议补上。

## 2. 验证失败携带类型化 detail（BUG-040/041 的承载体）

- [x] 2.1 `graph/nodes/wave2_synthesis/node.py`：引入携带具体类别 + 有界 detail 的失败载体（`SynthesisValidationFailure(ValueError)` 子类或等价 dataclass），`_validate_synthesis_semantics` 的覆盖面检查在抛错时附带缺失/重复/外键问题 id 明细；`_synthesis_validation_category` 仍产出粗粒度 parse/semantic 桶用于 repair 路由。

## 3. Repair prompt 携带完整 open-question 契约 + 具体 detail（BUG-040）

- [x] 3.1 `graph/nodes/wave2_synthesis/prompts.py`：`build_synthesis_repair_prompt` 增 `open_questions: Iterable[tuple[str, str]]` 与 `validation_detail: object | None` 关键字参数，objective 复用初始 prompt 的 closed disposition contract 措辞并加入可信 detail。
- [x] 3.2 `graph/nodes/wave2_synthesis/node.py`：把初始 prompt 的 `open_question_pairs` 与首个验证失败携带的 detail 传入 repair 请求；repair 保持 `tools_enabled=False`、同一 capability ref，无新增 authority。

## 4. 输出契约具体化 + 负面对照（BUG-043）

- [x] 4.1 `graph/nodes/wave2_synthesis/prompts.py`：`_expected_synthesis_output()` 增 `"example"` 键（一个最小合法 findings/relations/gaps 对象）与 `"instruction"` 负面对照（"return findings/relations/gaps, NOT a wave1 claims verdict list (`claims[]` …)"）；初始与 repair 共用同一 builder。

## 5. 有界终态投影具体验证类别（BUG-041）

- [x] 5.1 `domain/run_experience.py`：`NodeProblem` 与 `TerminalIncidentProjection` 增可选有界 `validation_category: str | None`（`max_length` 约束、小写/点/下划线类别字符串，如 `synthesis_question_coverage_invalid`），构造校验与现有 provider 校验不冲突；checkpoint 兼容由 `exclude_none=True` 持久化保证（字段缺省时不写入，旧 checkpoint 可读）。该字段只携带类别字符串，不含缺失 id 明细（id 明细在 `SynthesisValidationFailure`（task 2.1）上，不进投影）。
- [x] 5.2 `graph/nodes/wave2_synthesis/node.py`：二次验证 `except ValueError:` 改为绑定错误变量，把具体类别传入 `NodeProblem`；纯 parse 失败保留 `OUTPUT_STRUCTURED_INVALID`、`validation_category=None`；`_exhausted_update` 无需改动即透传。
- [x] 5.3 `runtime/run_experience.py` `_publish_observation`：`failure_category` 投影改为 `incident.validation_category or incident.code.value`，让 journal 事件与 `run-summary.json` 显示 `synthesis_question_coverage_invalid`（`RecordBearingLifecycleFact.failure_category` 的 pattern `^[a-z]+(?:[._][a-z]+)*$` 已接受该字符串，无需枚举扩展）。
- [x] 5.4 `runtime/run_experience.py` `_failure_for_terminal` + `scripts/demo_real.py`：`RunFailure` 增可选 `validation_category` 字段并透传（`_failure(...)` 加关键字）；`demo_real.py` 通用 `_failure_lines`（非 provider 分支）在 `failure.code` 后渲染一行 `failure.validation_category`（像 `worker_failure_category` 那样 if-not-None 追加）。**注意**：wave2 终态是通用分支，不走 `_terminal_failure_presentation.py`（其 `is_provider_diagnostic` 要求 provider 字段）；RunFailure 是运行时派生投影、不进 checkpoint，加字段无迁移。
- [x] 5.5 确认没有任何 route/gate/lifecycle/recovery 读者消费 `validation_category`（现有 provider/budget 分支按 code 比较，不受影响）。

## 6. 确定性测试（red-before-green）

- [x] 6.1 `tests/graph/test_wave2_synthesis_real.py`：prompt-objective 断言覆盖 repair 请求现携带 `open_questions` 契约与可信 detail、输出契约含 example + 负面对照。
- [x] 6.2 新增覆盖类失败 → repair 收到完整 question 契约 + 缺失 id detail → 非盲修复通过；修复后仍漏覆盖 → 有界终态投影具体 `synthesis_question_coverage_invalid` 而非泛化 code。
- [x] 6.3 新增纯 parse 失败终态保留 `output.structured_invalid` 且 `validation_category=None`；无 open questions 时行为不变（回归）。
- [x] 6.4 跑窄测试：`cd deep_research_harness && .venv/bin/python -m pytest tests/graph/test_wave2_synthesis_real.py` 与相关 prompts 单测，确保红变绿且既有用例不回归。

## 7. 文档与收尾

- [x] 7.1 `_backlog/bugs/`：BUG-040/041/043 标记修复并 `git mv` 到 `_backlog/_done/_fixed_bugs/`；更新 `_fixed_bugs/README.md` 表格 + Next available bug ID、`_backlog/bugs/README.md` 活跃列表、`_backlog/_done/README.md` 计数。
- [x] 7.2 全量验证：`cd deep_research_harness && UV_OFFLINE=1 make verify`、`openspec validate wave2-synthesis-validation-feedback-contract --strict`、`git diff HEAD --check` 均通过；`git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status --porcelain=v1 --untracked-files=all` 与 `git diff --submodule=short` 记录为归档证据；`deerflow/` gitlink 不修改。

## 8. Operator 确认（非 CI gate，如需）

- [ ] 8.1 （可选，需真机凭据）修复后跑一次 runbook-003 `soft-bundle run … --mode 003`，确认 wave2 覆盖类失败时 repair 非盲修复、终态投影具体类别，并把证据写入对应 BUG 卡。
