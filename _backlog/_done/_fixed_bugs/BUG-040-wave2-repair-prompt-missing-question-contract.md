# BUG-040: wave2 修复提示词缺少 open-question 处置契约，覆盖类语义错误只能盲修

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 已修复 ✅

## 症状

修复后真机 003 run（bundle `b_SOh4RFrtWOtfW0ARw5NKyb3DX296NBynqUD5tEHsqAo`，
diag `diag_2faa0d34b8413df5e361faf3`）wave2 首轮输出形状错误（wave1 的 claims
形状，见 BUG-043）触发一次 repair；repair 输出**形状正确**（11 findings /
3 gaps，parse 通过），但漏处置 wave1 遗留 open question 之一
`q:w1_oq_china_full_year_installed_capacity_2024` →
`synthesis_question_coverage_invalid` → 有界 blocked 终态。

checkpoint 解码证据：wave1 遗留 4 个 open questions，repair 输出的 3 个 gap
的 source_questions 共覆盖其中 3 个，第 4 个既不在任何 gap 也不在
resolved_questions。模型被告知了失败"类别"（一个 terse 字符串），但**没有任何
地方告诉它必须处置的完整问题清单**——这轮 repair 对覆盖错误是盲修。

## 根因

`graph/nodes/wave2_synthesis/prompts.py` 的
`build_synthesis_repair_prompt(draft, evidence, *, validation_category)` 签名
**没有 open_questions 参数**（全文 0 处提及）；初始 prompt
`build_synthesis_prompt(..., open_questions=open_question_pairs)` 有。
语义验证失败的根因信息（哪些问题未处置）在 `_validate_synthesis_semantics`
抛出的 ValueError 里，但 `_synthesis_validation_category()` 把它压成一个类别
字符串就丢了。

## 复现

解码 `graph.sqlite` writes：`wave1_open_questions` 末值（4 问）× `messages`
末条（repair 输出）→ 手工复算
`(gap_covered | resolved) != expected` → 复现 `synthesis_question_coverage_invalid`。

## 修复关联

Change `wave2-synthesis-validation-feedback-contract`（WSN-010）：`build_synthesis_repair_prompt`
新增 `open_questions: Iterable[tuple[str, str]]` 与 `validation_detail: object | None`
关键字参数，objective 复用初始 prompt 的 closed disposition contract 措辞并把
具体缺失 id 明细作为可信 detail 传入；`_validate_synthesis_semantics` 的覆盖面
检查在抛错时附带缺失/重复/外键 id 明细（`SynthesisValidationFailure` 载体）。
确定性测试：`test_repair_prompt_carries_open_question_contract_and_trusted_detail`、
`test_repair_is_non_blind_for_coverage_with_open_question_contract`（新增）。

