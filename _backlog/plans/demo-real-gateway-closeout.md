# Plan: demo-real Gateway 路线收尾（v2.1.0 demo 阶梯最后一格）

> 类型: 执行计划（ongoing，长期打磨） | 更新: 2026-09-26
> 前序: `/tmp/handoff-deerflow-v210-demo-real.md`（易失）。本文是其仓库内持久化 + 2026-09-26 诊断增量。

## 背景 / 现状

v2.1.0 同步后 demo 阶梯仅剩一格：`make demo-real`（Gateway observer 路线）及其依赖项
（`demo-tui-real-auto` / `demo-tui` / `tests/live/test_gateway_forwarding_proof.py`），
全部卡在 wave2_synthesis 的候选验证（handoff §3）。

**2026-09-26 本会话新增证据**（上会话遗留 run：bundle
`b_d0ecD8y4VA4bQ0A1BwUVBoJrPiH52SVs2oDrlDmpvbE`，Gateway 日志 `/tmp/gateway7.log`）：

- 三轮修复全部被拒，category **全部 = `candidate_invalid`**，`detail=None`，
  chars = 10047 / 7148 / 7148（后两轮字节数完全相同 → 修复轮在原样复刻同一坏形状）。
- 离线代码复现（`deep_research_harness` venv）：
  `parse_synthesis_output` 的 JSON 语法错误已包进封闭词表
  （`synthesis_output_json_invalid` → 会得 `parser_invalid`）；
  但 `SynthesisResult.model_validate(payload)` 的 **pydantic `ValidationError` 裸逃逸**
  ——它是 `ValueError` 子类、消息形如 `1 validation error for SynthesisResult...`、
  不匹配 `synthesis_*` 前缀、且无 `.detail` 属性 →
  `_synthesis_validation_category` 落入 `candidate_invalid` 桶、`detail=None`。
- **根因判定（高置信）**：真实 run 的失败 = JSON 合法但 schema 不合；
  修复提示词（`build_synthesis_repair_prompt`）在此类别下只给模型
  `candidate_invalid` + `validation_detail: null`，零具体反馈 → 模型复刻同一坏形状。
- **对 handoff §3 决策菜单的修正**：菜单 2/3/4（ID 别名 / 语义放宽 / 问题瘦身）
  针对的 `synthesis_question_coverage_invalid` **从未出现** → 暂不进入；
  菜单 1（重试派）的"概率性失败"判断被系统性证据削弱（同类三连败 + 同尺寸复刻）。

## 目标（拟定）

- **G1 诊断闭环（无准入语义变更）**：把 pydantic `ValidationError` 折进封闭词表——
  `parse_synthesis_output` 捕获后 raise `synthesis_output_schema_invalid` 并携带
  bounded `.detail`（前 N 条 pydantic 错误的 loc/type/msg 投影）。
  效果：category 变为 `parser_invalid`、日志 detail 非空、修复提示词拿到具体反馈。
  可选加码：被拒候选 bounded 落盘 bundle diagnostics（现未持久化，离线无法取证）。
  **→ 2026-09-26 已实现（tdd 红→绿）**：`SynthesisValidationFailure` 上移至
  `prompts.py` 供 parser 与语义校验共用；`parse_synthesis_output` 捕获
  `ValidationError` → `synthesis_output_schema_invalid` + `_schema_detail`
  （前 3 条错误、msg 截 120 字符）；`_synthesis_validation_category` 自动映射
  `parser_invalid`，修复提示词经既有 `validation_detail` 通道拿到结构化反馈。
  owning spec 无需 delta：WSN 只强制 pre-model ValidationError 不落
  candidate_invalid 桶（现满足且更优），model-candidate 路径未被枚举。
  可选加码（候选落盘）未做，保持最小改动。
- **G2 修复**：按 G1 重跑后的取证决定——
  schema 反馈闭环大概率足以让既有 3 轮修复成功（模型有能力，见 handoff §3 重放实验）；
  若仍失败 → 评估模型侧结构化输出绑定；
  只有证据指向覆盖语义才回到 handoff 决策菜单 2/3/4。
- **G3 验收**：handoff §5 清单原样执行
  （`UV_OFFLINE=1 make verify` + `make test-live` 50/50 + `demo-tui-real-auto` /
  `demo-tui` / `session-workbench` + `test_gateway_forwarding_proof.py` + 全部提交）。

## 次序

1. G1 实现 + 单测（tdd：构造 schema 违例候选，断言 category=parser_invalid、detail 非空）。
   动手前检查 owning spec 是否枚举 wave2 拒绝 category；如枚举，同 change 同步 spec。
   **→ 2026-09-26 完成（c43fd49）**：owning spec WSN 只强制 pre-model 路径，
   model-candidate 路径未被枚举 → 纯代码改，无 spec delta。
2. 重算指纹（handoff §2）→ 起 Gateway → `make demo-real`（管道 stdin，行序见 handoff §2）。
   **→ 2026-09-26 实跑记录**：指纹已重算（`v1:ed9ad508…`）；三次点火均**未到 wave2**，
   卡在更早的外层 Gateway agent 路由层：
   - 裸 `confirm` → run 侧"未识别"（新 thread 上 confirm 的合法性以 demo 自述为准，
     实测被拒；与 handoff §2 "有提案时 confirm 合法"存在张力，待复核）；
   - 完整 JSON → 外层 agent 说教不路由 → `protocol.invalid_result`（不可重试）；
   - question+JSON+confirm 三行 → 期间两次 provider 流式断流（`stream_chunk_timeout`，
     240s×N，VPN 链路抖动），自动重试后部分推进，结局待本 run 收尾。
   **每 run 独立 scope，重试无需 soft_bundle clean；唯一一次僵尸 bundle 已归档。**
   **2026-09-26 深夜诊断定论（六次点火后的机制链）**：
   - 交互路线的 HITL1 文本回答解析是**认知面**：profile 细节与提案确认都走
     `hitl1/_classify_proposal_reply` → `build_semantic_intake_prompt` → 真模型调用；
     仅"短语修订"有确定性捷径（`_local_phrase_revision`）。
   - 今晚 provider 流式反复断流（`stream_chunk_timeout` 240s×4+）→ 语义解析调用
     失败/无法完成 → 所有 stdin 答案（裸 confirm、精确匹配建议值的 JSON）一律
     "未识别" → stdin 耗尽 → `input.invalid_response`。**非代码 bug、非契约错配。**
   - 提案阶段 `visible_controls` 为空（`allow_acceptance=False`）→ 控件选择这条
     零模型调用通路也不可用；`allow_acceptance = interaction.controls` 非空才开启，
     而 interaction.controls 由语义解析结果驱动——与上条同因。
   - **改进候选（修正版，2026-09-26 深夜复核）**：~~确定性确认捷径~~ **已存在**——
     `domain/profile.py::normalize_clear_confirmation`（封闭集含 confirm/确认/yes…）
     + `test_local_clear_confirmations_bypass_the_semantic_bridge` 全绿；据此撤回了
     冗余的 `deterministic-explicit-confirmation-shortcut` 提案（ca13563）。
   - **真正的缺陷定位（下一步诊断）**：节点直连路径上捷径工作正常，但 Gateway 路线的
     六次实跑中答案从未被节点接受——`profile_rejection_round=0`、
     `interaction_feedback=None`、`hitl1_visit_count=4`（四次访问全裸挂）。结论：
     驱动 `AnswerRun` 携带的逐字答案（含 `human_input_response` 结构化负载）在
     Gateway 会话运输层被外层 agent 转述/丢弃，未以原值到达节点，精确匹配的封闭集
     永远打不中。**下一步 = 追踪答案在 gateway transport（threads/runs API → 外层
     agent → deep_research resume 调用）中的保存/变形点**，修好后 HITL1 无需任何
     代码改动即可稳定通过（捷径已在）。备选修复面：驱动对 Gateway 路线改用确定性
     resume 通道（绕过外层 agent），或 transport 保结构化负载。
   - **G1 判据取数仍被阻塞**：wave2 要先过 HITL1（运输层修复）+ 一次稳定链路窗口。
   教训：交互 observer 路线的瓶颈是外层 agent 的路由随机性 + 今晚的 provider 抖动，
   不是 wave2。G1 判据（category=parser_invalid、detail 非空）要等 wave2 真正被执行
   才能取数；若 agent 路由持续不稳，备选是先在嵌入式路线（demo-real-scripted 同一
   wave2 代码路径）上验证 G1，再回 Gateway 路线。
3. 通过 → 直接 G3；再挂 → 用新 detail 细分：
   `parser_invalid` 反复 → 结构化输出绑定方向；
   `coverage_invalid` 出现 → 决策菜单 2/3/4（走 openspec）。
4. 收尾按 G3；`.env`/指纹/密钥不落盘；`.agents/skills/` 6 个用户本地文件永远不碰。

## 风险 / 取舍

- [ValidationError 折词表改变分类表面] → 该分类是 repair-safe 反馈通道，不是准入语义；
  封闭词表契约用测试锁住。→ 缓解：tdd + 契约测试。
- [落盘被拒候选含研究内容] → 放 diagnostics 子树、bounded 截断、随 Bundle 生命周期删除。
- [G2 若最终需动覆盖语义] → 先 `openspec-propose` 写 spec 再动手（handoff §7 同款约束）。

## 落地关联

- G1：node 内部反馈通道修复，无生命周期契约变化 → 直接小 PR。
- G2 若选语义放宽/瘦身 → 动 WSN 契约 → 走 `openspec/changes/`。
