# Plan: Mode 003 real-auto 最低规模跑通（Profile 驱动意图，不污染产品逻辑）

> 类型: 设计 | 更新: 2026-08-18 | 状态: 最终共识

## 背景

- 003 = 真实模型 + 真实网页全自动跑通（soft-bundle 入口，固定 bounded 问题）。
- 诉求：wave 深度/宽度/交叉降到非常低，只要能跑通；不要"搜太多网页"。
- **v1 教训（废弃）**：v1 直接改产品默认（worker 预算、wave2 gate budget、节点预算、
  domain 归一化、hitl1 auto 分支）来适配真实 run——等于"测的和真实跑的不是一个东西"，
  用测试需求污染了产品逻辑。**全部回退。**
- **v2 原则**：规模/花费/时长的**意图**由 **ResearchProfile（研究档案）** 表达——
  profile 由 HITL1 确认后写入 Bundle（全局可见），各节点按 profile 意图调整；
  **产品默认（标准 profile）行为一律不变**。测试想快、想窄，就把意图写进 profile，
  而不是改默认代码。

## 现实约束（调研结论，2026-08-18）

1. **Profile 是全局可见的**：`ResearchProfile` 由 HITL1 写入 Bundle request store；
   `topic_planning/prompts.py::planner_assignment_from_state` 通过
   `request_bundle.read_profile(profile_ref)` 读取，`single_topic` 已从
   `research_depth==quick_overview and cost_tolerance==minimal and time_budget==very_quick`
   推导并强制 1 个 topic。**这就是"profile 意图传递到节点"的既有范式**。
2. **但只有 topic_planning 消费意图**：wave0/wave1 worker 预算
   （`runtime/research.py::_worker_policy`）、wave2 gate 预算
   （`engine/real_gates.py::build_wave2_real_gate_def`）、readiness/final_delivery
   （内容节点预算）**都不读 profile**。要把意图传到每个节点，需要一个
   **profile 意图投影**（新机制）。
3. **非交互 auto 路径**（`hitl1/node.py` auto 分支，= demo-real `--scripted`）当前只填
   comparison/language，`depth/cost/time` 留空（degraded）→ `single_topic=False` →
   planner 自由拆 1-8 个 topic。**这是"搜太多网页"的直接来源**，且它本来就该把意图写进
   profile（auto = 自动建档，填 minimal 三字段是 profile 的正确用法，不是产品默认变化）。
4. **真实 run 撞出的产品缺陷**（与规模无关，任何真实 run 都会遇到）：
   - wave2：真实模型输出 `priority:"high"`（字符串）vs 契约 int 1-5；gaps 的
     `source_questions` 写自然语言 vs 契约 `q:w1_*` id；**wave2 修复路径二次解析无保护**
     → ValidationError 逃逸崩图（`bundle.unavailable`）。
   - targeted_evidence：worker 输出 `sources[].url/observed_relevance` vs 契约
     `source_id/canonical_url`。
   - wave0/wave1：模型输出形状波动大，repair 循环多。
   - **auto 建档缺 `must_answer`**（v1 实测 `state.must_answer_questions=[]`）→
     readiness 无 per-question verdict → `final/report.md` 空壳（v1 实测证据）。
     这是任何 auto run 的 bug（与 minimal 无关）。
   - **wave2 预算按脚本模板校准，真实输出会 `budget.exhausted`**（v1 实测事件证据）。
     readiness/final 预算同理偏紧，但**无实测失败证据**（v1 从未在旧预算下跑到那）；
     按"实证驱动"原则：只放宽 wave2，readiness/final 保持现状，遇 exhausted 再按证据放宽。
5. **运行前置**：`.env` 需 `DEEPSEEK_API_KEY` + `TAVILY_API_KEY` +
   `DEERFLOW_DEMO_MODEL=deepseek-v4-flash`。
6. **模型挂起风险**：DeepSeek SDK 偶发阻塞调用，bridge 的 `asyncio.timeout` 对阻塞
   ainvoke 无法中断 → run 卡死（实测多轮）。这是框架/桥接层健壮性问题，**不在本 plan
   范围内**（需要独立评估），runbook 先注明"卡死可 Ctrl-C 重试"。

## 系统性复审发现的欠考虑点（2026-08-18，已修正）

| # | 欠考虑点 | 代码证据 | 修正 |
| --- | --- | --- | --- |
| 1 | **"hitl1 写 `repair_budget_by_phase`"不可行** | `state.py`：`repair_budget_by_phase` 的 WriterRole=**GATE**（含 FieldOwnership），HITL 写会被所有权校验拒绝 | gate 预算改为 **gate 只读 state 派生**：`cost_tolerance`/`time_budget` 已是 HITL-owned state 字段（`profile_state_fields` 写入）；wave2 gate 定义加预算解析（读这两个字段 → minimal 对 → 2，否则 default 1） |
| 2 | `profile_intent=standard` 与 absent 语义空洞（等价） | 无 standard 的独立行为定义 | 简化为 `profile_intent: "minimal" \| None`（无空洞值）；未来需要 standard 再扩 |
| 3 | readiness/final 预算放宽**缺实证**（只有 wave2 实测 exhausted） | v1 事件证据仅 wave2 | 只放宽 wave2（实证驱动）；readiness/final 保持现状，遇 exhausted 再按证据改 |
| 4 | **auto 建档缺 `must_answer` → report 空壳**（plan 漏了） | v1 实测 `must_answer_questions=[]` → readiness per_question 空 → `writable_conclusions=[]` | 纳入 C（产品 bug 修复）：auto 分支构造 profile 时补 `must_answer=(request_text,)`（任何 auto run 都受益，与意图无关） |
| 5 | `non_interactive_policy` 加字段的改动面未列全 | `tool.py::_admitted_start_action_input` 严格键校验（`set(candidate) != required_keys`）；`NonInteractivePolicy`/`graph_value`/`StartActionInput` 序列化；`tests/unit/test_non_interactive.py` 等形状断言 | plan/tasks 列出完整改动面 |
| 6 | 003 验证范围未诚实界定 | embedded smoke 是 demo/operator 路径 | 明确：003 验证**非交互 operator 路径**的真实性（minimal 意图下），不声称覆盖 Gateway 交互路径 |
| 7 | **`must_answer=(request_text,)` 有 256 字符上限风险**（polish 复审发现） | `domain/profile.py`：`MAX_QUESTION_CHARS = 256`，validator 超限抛 `must_answer_invalid`；非交互 request 上限 16K | auto 分支：request_text > 256 → **fail-closed blocked**（与 typed-fact 缺失同一路径，不静默截断）；已补进 design D1 / tasks 1.3 / hitl1 spec 场景 |

## 方案（v5：意图声明机制——产品只留机制，003 只传参）

### 原则（回应"测试应测真实的东西"）

- **产品代码只新增一个机制**：非交互 run 可以声明研究意图
  （`non_interactive_policy.profile_intent: "minimal" | None`，默认 None = 现状）。
  HITL1 auto 分支**按声明**构造 profile（minimal → 三字段；None → 现状
  degraded 空字段）。这是产品能力（非交互自动 run 本就该能表达意图），不是测试逻辑。
- **003 只是传参**：入口（demo_real --scripted / soft_bundle mode 003）声明
  `profile_intent=minimal`——模拟一个"选了 minimal 意图的自动化用户"，走的全是真实
  链路（planner single_topic、真实 worker 预算、真实 gate）。
- **不埋坑**：auto 分支不硬编码 minimal；未来 operator 不声明（现状兼容），产品零改动。
  003 测的就是 minimal 意图下的真实产品行为（**范围诚实**：非交互 operator 路径，
  不声称覆盖 Gateway 交互路径）。
- **改动面完整列出**（欠考虑 #5）：`tool.py::_admitted_start_action_input`（严格键
  校验）、`runtime/non_interactive.py`（NonInteractivePolicy/graph_value/StartActionInput
  序列化）、`hitl1/node.py`（auto 分支）、`tests/unit/test_non_interactive.py` 等形状断言。

### A. 意图声明 → profile（机制 + 传参）

- `non_interactive_policy` 加可选 `profile_intent`（minimal/None——不做 standard 空洞值，
  欠考虑 #2）。
- hitl1 auto 分支：`profile_intent=minimal` → 构造 minimal 三字段 profile（degraded，
  无模型调用）→ `single_topic` 既有推导成立；None → 保持现状（degraded 空字段）。
- 003 入口声明 minimal。

### B. 意图消费（gate 只读 state 派生，无权限冲突）

- **gate 预算解析（修正欠考虑 #1）**：`cost_tolerance`/`time_budget` 已是 HITL-owned
  state 字段（`profile_state_fields` 写入）——wave2 gate 定义加**预算解析器**
  （`GateDefinition` 加可选 budget resolver：读 state 的这两个字段 → minimal 对 →
  2，否则 None → 用 default 1）。gate **只读** state（不写 `repair_budget_by_phase`，
  避免 WriterRole=GATE 的权限冲突）。`_resolve_budget` 优先用 resolver 结果。
- **worker 预算不分档**（真实上限 50/200/900s，bounded run 实际 1-3 次调用不 bind）
  ——003 用的就是真实 worker 预算，进一步"测真实"。
- **宽度**：minimal 三字段 → planner `single_topic`（既有推导）。

### C. 真实模型适配（产品 bug 修复，与规模无关——已决策：纳入本 change）

- **auto 建档补 `must_answer=(request_text,)`**（修正欠考虑 #4，v1 实测 report 空壳
  根因——任何 auto run 都受益）。
- **wave2 预算放宽**（实证驱动，欠考虑 #3）：wave2 ≈ 4 calls / 64K / 16K 输出 / 300s
  （v1 实测 `budget.exhausted`）；**readiness/final 保持现状**，遇 exhausted 再按证据改。
- wave2 priority/source_questions 归一化 + targeted 形状归一化 + wave2 修复路径有界化。
- **这些不是测试改动，是脚本模板掩盖的真实缺陷。**

## 落地可行性评估（2026-08-18，代码核对 + 坑探索 + 系统性复审）

| 模块 | 难度 | 依据 |
| --- | --- | --- |
| A. 意图声明机制（`profile_intent` 扩展） | ★ 容易 | closed 结构扩展（tool.py 严格键校验 + NonInteractivePolicy 序列化），向后兼容（None = 现状）；改动面已列全（欠考虑 #5） |
| B. 意图消费（gate 预算解析） | ★★ 中等 | `repair_budget_by_phase` WriterRole=GATE 写不了（欠考虑 #1）→ 改 **GateDefinition 加预算解析器**（gate 只读 state 的 `cost_tolerance`/`time_budget`——HITL-owned 字段，无权限冲突）；`_resolve_budget` 优先 resolver；涉及 gate 契约 + kernel + real_gates + 测试 |
| C. 真实模型适配 | ★ 容易 | v1 已实施+测试通过（wave2 37 passed / targeted 62 passed）。**只放宽 wave2**（实证驱动，欠考虑 #3）+ must_answer 修复（欠考虑 #4）+ 形状归一化 + 修复路径有界化 |
| D. mode 003 + runbook | ★ 容易 | v1 已实施+测试通过（19 passed）。003 入口声明 `profile_intent=minimal`（传参，无产品逻辑） |
| 风险项 | — | ① 模型挂起 → runbook 注明 Ctrl-C 重试，bridge 加固独立评估；② 真实 run 波动 → gate 2 轮解析覆盖收敛路径；③ 未声明意图的行为必须与今天一致 → 测试钉死 |

**总体判断（v5）**：产品只加"意图声明"一个机制 + gate 预算解析（gate 契约小扩展），
003 只传参，C 是真实缺陷修复（must_answer 是 v1 实测 report 空壳根因）。
**产品里没有测试专用逻辑；003 测的就是 minimal 意图下的真实链路**。落地总体
**容易-中等**（B 的 gate 契约扩展是唯一中等项），无阻塞性障碍。

### D. operator 入口与文档

- `soft_bundle.py` mode 003（委托 `make demo-real-scripted`，record-based
  inspect/verify）；runbook-003；`_backlog/_local_demo/README.md` 003 行；
  `.env` 前置文档。**无产品推理逻辑**，纯 operator 面；003 入口声明 minimal 意图。

## 已决策（决策点定稿）

1. **C（真实模型适配）纳入本 change**：真实 run 的硬需求（不修永远跑不通），语义是
   "让契约接受真实模型形状"，与规模意图正交；归一化是确定性契约边界适配，不是放宽
   admission。若未来需要单独评审，archive 前可拆出。
2. **意图传递形态**：`non_interactive_policy.profile_intent`（`minimal` | None——
   无 standard 空洞值，欠考虑 #2）是唯一入口；hitl1 auto 按声明构造 profile（minimal
   → 三字段；None → 现状）；gate 预算走 **预算解析器**（gate 只读 state profile 字段，
   无 WriterRole 冲突，欠考虑 #1）。无 envelope/recipe capability 改动。
3. **003 传参**：demo_real --scripted / soft-bundle mode 003 声明 `profile_intent=minimal`
   ——测的就是真实链路，不是测试分支。

## 实施顺序（先机制后适配）

1. **A**：`profile_intent` 声明机制（tool.py 校验 + NonInteractivePolicy + hitl1 auto
   按声明构造 profile）；测试：minimal → 三字段、None → 现状。
2. **B**：`GateDefinition` 预算解析器（wave2 gate 读 state profile 意图 → minimal 对
   → 2，否则 default 1；`_resolve_budget` 优先 resolver）；测试：两档 + absent 零变化。
3. **C**：must_answer 修复（auto 建档）+ wave2 预算放宽（实证驱动，readiness/final
   不动）+ wave2 / targeted 输出适配 + 修复路径有界化 + 测试。
4. **D**：soft-bundle mode 003（声明 minimal）+ runbook + README。
5. **验证**：全量测试 + ruff；002 零成本回归；真实 003 跑通（RESULT: PASS +
   真实 report + 每 wave 1 work unit）。模型挂起时按 runbook 注明 Ctrl-C 重试
   （bridge 加固为独立事项，不阻塞本 change）。

## 验证方式

- 确定性：`tests/graph/test_hitl1_node.py`（minimal → 三字段 + must_answer；None →
  现状 + must_answer 修复）、gate 预算解析两档测试（default 1 / minimal 2）、
  wave2/targeted 适配测试、`tests/contract/test_soft_bundle_cli.py`（mode 003）、
  `tests/unit/test_non_interactive.py`（形状扩展）。
- 端到端：002 回归；真实 003（PASS + 真实内容 + 单 work unit）。

## 与 OpenSpec 的关系

- 本 plan 是思考文档，已定稿（最终共识，v5）。实施走
  `openspec/changes/low-scale-real-auto/`（proposal/specs/design/tasks 按 v5 对齐，
  `validate --strict` 通过）。**代码已全部回退，工作区只剩本 plan
  与 change 目录。**
