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
2. 重算指纹（handoff §2）→ 起 Gateway → `make demo-real`（管道 stdin，行序见 handoff §2）。
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
