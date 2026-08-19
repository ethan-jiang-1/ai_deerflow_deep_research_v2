# BUG-058: 004 wave1 source-diagnostic critic 用字符串标签填 bool 字段，真实 run 必然 blocked

> 严重级别: P0（阻断——004 首跑 wave1 6 次尝试全部 `wave1_review_output_invalid` 后 `research.blocked`） | 发现: 2026-08-19 | 状态: 已修复（change `fix-wave1-critic-label-shapes`；真实模型复验：prompt bounds 后模型直接返回 bool，归一化兜底就位；待 004 复跑确认后归档）

## 症状

真实 mode-004 run（bundle `b_8bfIc_sJr53K0o5MJfK8fOPP0MOVvL5A3XxJvHNvW4A`，默认意图、
比较题）在 wave1 阻断：

- `g0_wave1_w0000_a00`：worker 初始验证通过（2 新源 / 6 claims），post-candidate
  `source_diagnostic` critic 判 `wave1_review_output_invalid`；
- gate repair 循环：`w0001`（`wave1_new_source_floor_not_met` ×2 → structured_output
  耗尽）→ `w0001_a01`（初始过、critic 再次 `wave1_review_output_invalid`）→
  `w0002`（worker unknown 失败 ×3）；
- 终态 `terminal_reason="gate_blocked"`、`latest_incident research.blocked @wave1`，
  事件序列 74。

**关键模式**：每当 wave1 worker 产出通过初始验证的候选（3/3 次），source_diagnostic
critic 的输出必然解析失败——这是确定性缺陷，不是模型波动。

## 根因

两层：

1. **契约/提示不匹配（主因）**：`domain/critics.py::CriticSourceAssessment` 要求
   `marketing_risk: bool` / `cross_verification_need: bool`，但
   `wave1/prompts.py::build_wave1_source_diagnostic_prompt` 的 objective 只说
   "marketing-risk flag"、expected 块只列 key 名**从未声明 boolean 类型**。真实模型
   （deepseek-v4-flash，2026-08-19 复现实测）返回：
   `"marketing_risk": "low"`、`"cross_verification_need": "low"`——把"flag"理解成
   严重度标签，语义上完全合理。
2. **错误掩码（放大器）**：`wave1/review.py::_canonical_critic_code` 把所有非
   `wave1_*` 前缀的 ValueError（含 pydantic ValidationError——它是 ValueError
   子类）折叠成笼统的 `wave1_review_output_invalid`，事件里看不到真实失败类型
   （bool_parsing），只能靠 bundle 外复现定位。

与 003 战役修复的 wave2 `priority:"high"`（字符串 vs int 1-5）、targeted
`url`→`canonical_url` 属**同一缺陷类**：真实模型输出形状 vs 确定性契约边界。
003 单 topic 问题未触发本字段纯属运气（模型恰好返回 bool）。

## 复现

```bash
cd deep_research_harness
# 用 blocked bundle 的 w0000 真实 assignment（carnegie_endowment + kleinman_energy）
# 构建 build_wave1_source_diagnostic_prompt → 调真实 DeepSeek → parse_wave1_source_diagnostic
```

实测输出（2026-08-19，temperature 0.2，json_object）：

```json
{"schema_version":1,"sources":[
  {"source_id":"carnegie_endowment","trust_tier":"high","materiality":"primary",
   "marketing_risk":"low","cross_verification_need":"low"},
  {"source_id":"kleinman_energy","trust_tier":"high","materiality":"primary",
   "marketing_risk":"low","cross_verification_need":"low"}],
 "source_ids":["carnegie_endowment","kleinman_energy"]}
```

`parse_wave1_source_diagnostic` → 4 × ValidationError `bool_parsing`（每源 2 个
bool 字段）→ 折叠为 `wave1_review_output_invalid`。

## 修复关联

待修（按 003 先例——确定性契约边界归一化 + 提示显式化）：

1. 归一化：critic 结果解析处把有限字符串标签确定性映射为 bool
   （`"low"/"none"/"no"/"false"/"minor"/"unlikely" → false`；
   `"high"/"yes"/"true"/"elevated"/"needed"/"required" → true`），带闭合映射表
   与越界拒绝；
2. 提示：expected 块显式声明两个 bool 字段的取值（`true/false`），objective
   去掉歧义的 "flag" 措辞；
3. （诊断性，评估顺手修）`_canonical_critic_code` 对 pydantic ValidationError
   透出字段级类型（如 `wave1_review_output_type_invalid`），不再全部掩码；
4. 横切排查（README 约定"契约探针"）：`ClaimAssessment`（verdict 枚举/refs）与
   readiness critic 是否存在同类 bool/enum 标签字段——同一次真实 run 的
   claim_verifier 从未跑到（source_diagnostic 先挡），需在修复后观察。

修复落地后 004 复跑（`run --mode 004`）验证 wave1 通过。
