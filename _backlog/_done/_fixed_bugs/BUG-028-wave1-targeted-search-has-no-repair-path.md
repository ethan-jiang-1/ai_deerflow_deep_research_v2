# BUG-028: Wave1 `targeted_search` 没有真正的修复路径

> 严重级别: P1 | 发现: 2026-08-15 | 状态: 已修复（2026-08-16，change `wave1-question-handoff-and-critic-observability`）

## 症状

真实 Wave1 gate 对 28 个开放问题给出 `targeted_search`。原路由把它送入 `repair`，再返回
Wave1；但 Wave1 没有把这些开放问题转化为新的、受预算约束的 targeted retrieval WorkSpec。
结果是重复访问已有证据，最终触发 fatigue 或 terminal block，而不是补齐缺口。

## 根因

图拓扑存在 `wave1 -> repair -> wave1`，而数据所有权不连通：Wave1 的开放问题不会成为
`targeted_evidence` 所消费的 `unresolved_gaps`。后者只由 Wave2 synthesis 投影。因此 route
名字承诺了“targeted search”，实际没有任何新的检索工作被创建。

## 复现

创建带 `targeted_search` disposition 的 Wave1 review。验证路由回到 repair/Wave1，并检查没有
新增 targeted-evidence WorkSpec 或等价的 Wave2 unresolved gap。2026-08-15 的真实运行提供了
28 个此类开放问题。

## 修复关联

当前工作树暂时移除了 Wave1 的该 gate rule，使问题被延后到 synthesis；这只是防止错误循环，
尚未证明开放问题会变成可检索缺口。本卡应由新的 OpenSpec change 决定并测试以下其一：
Wave1 到 targeted-evidence 的受控转换，或明确交给 Wave2 并保证可追踪的 handoff。

2026-08-16 现状同步：`engine/real_gates.py` 的 wave1 gate 现在只有 `work_unit_completion` /
`new_source_floor` / `review_presence` 三条规则，question-floor（`targeted_search` → repair）
规则已移除，因此 `tests/integration/test_wave1_work_units.py::test_real_wave1_review_gate_enforces_
question_floor_and_review_integrity`（@impl WON-004）保持红色（期望 repair、实际 pass）。scripted-real
基线（已归档 change）也实测：wave1 submission 不进入 accepted refs（延后到 synthesis 的现状），且
synthesis 一旦投影可检索 gap，路由进 targeted_evidence 会抛 `work_unit_gate_view_inconsistent`。
本卡是这两条红线的唯一 owner，修复 change 落地前不要关闭。

---

**关闭记录（2026-08-16）**：经 change `wave1-question-handoff-and-critic-observability` 修复。
