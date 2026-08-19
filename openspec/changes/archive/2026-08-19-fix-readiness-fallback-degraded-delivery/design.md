# Design — fix-readiness-fallback-degraded-delivery

## Context

readiness 是 non-gated 节点（自写 route，见 `graph/nodes/readiness/node.py`）。当前路由优先级：
结构性失败 → `exhausted`/`BLOCKED`；`blocked_count > 0` 且 wave2 未降级 → `repair_targeted`；
否则 `pass`。保守回退（`conservative_readiness_output`）产出全量 `blocked_repair_required`，
因此**观察失败（含 per-call cap 截停）与认知判定走同一条 repair 路由**。而 targeted-evidence
只对 `unresolved_gaps` 派工，gapless 时是确定性 no-op（`route=next` 空视图）→ 形成无界自旋
`readiness → targeted(空转) → wave2 → hitl2 → readiness`，直到某次预算/结构性死亡写 blocked
terminal，全部产出零交付（BUG-057 真实 run + 确定性探针双重证明；探针 8 轮自旋、26 次模型调用
后 blocked，journal 完整保留循环模式）。

对照家族先例：wave2 gate 有 `degraded_pass_on_exhaustion`（BUG-035/044）、wave2 节点预算失败
交还 gate 走同一降级分支（BUG-050）、final_delivery 排版失败同 visit 降级（BUG-055）。readiness
是同家族中唯一缺降级通路的阶段；wave2 降级借用（BUG-044）只覆盖"wave2 已降级"的窄情形。

## Goals / Non-Goals

**Goals**
- 观察失败（critic 执行失败/候选不可采纳）从"伪装修复需求"改为"披露的未验证判断"，永不路由
  repair、永不 spin、永不单独导致 blocked。
- 堵住同类第二入口：admitted blocked 判定在 gapless run 中不再路由 no-op repair，降级为披露交付。
- pass 投向下 blocked 判定必须留在 report plan 里（披露），不再消失。
- 三条观测事实入 journal（readiness 路由决策、targeted no-op、terminal 结构归因），修复
  RER-009 已规定但实现缺失的 journal 可用性行真实性。

**Non-Goals**
- 不改结构性失败 → `exhausted`/`BLOCKED` 语义；不改 wave2 降级借用分支；不改图拓扑与 hard rules。
- 不做 critic 同 visit 重试（预算内二次调用）——模型方差重试是独立预算决策，另行立项。
- 不做 host 侧（DeerFlow Gateway）trace 增强——独立 run 不经 Gateway HTTP，host trace 体系在该
  路径不生效；本次只补 bundle-local journal 决策事实层。host trace 与 bundle journal 的关联键
  登记为后续观察。
- BUG-056 无产品改动（已由 94c8087 修复，根因是测试 fake store 滞后于 dd4c39d 的结构性读取扩展）。

## Decisions

### D1: 保守回退改投影 `ready_insufficient_judgment`（而非保留 blocked + 特判路由）

`conservative_readiness_output` 从 `blocked_repair_required` 改为 `ready_insufficient_judgment` +
固定闭合 limitation note（文案保留现有 "Readiness critic did not produce an admissible
answerability verdict."）。

- 为什么：一步到位——`blocked_count` 自然为 0 → 路由自然 `pass`；materializer 现有的
  insufficient→强制不确定项通路自动完成披露；无需新增路由特判分支；语义诚实（"无法判断"≠"需要补证"）。
- 备选（拒）：保留 `blocked_repair_required` 并在 fallback 时特判路由 `pass`——需要在路由和
  materializer 两处穿透 fallback 状态，分支更多、更难测试；且 checkpoint 的
  `readiness_critic_summary` 会继续携带误导性的 blocked 投影。
- 影响面已核对：`conservative_readiness_output`/`readiness_blocked_count`/`readiness_critic_summary`
  的消费方全部在 readiness 包内（node/critic/materializer）+ state checkpoint 字段，seam 干净。

### D2: gapless 守卫按"修复循环有无申报工作"判定，与 wave2 降级借用同一优先级平面

路由判定改为：结构性失败 → `exhausted`；admitted `blocked_count > 0`：
- `unresolved_gaps` 非空 且 wave2 未降级 → `repair_targeted`（现状保留）；
- 否则（gapless 或 wave2 已降级）→ `pass` + 披露。

- 为什么 gaps 非空是正确的"有工作"判据：targeted_evidence 的派工**只**来自
  `unresolved_gaps`（`materialize_gap_intents(gap_ids)`，0 intents 即 no-op）——路由进一个
  定义上无事可做的循环是不诚实路由。
- 备选（拒）：给 readiness 加自旋计数/疲劳上限——引入新 state 字段与计数语义，且只是把无界
  自旋变成有界自旋，每轮仍烧 wave2/hitl2/readiness 三个节点的真实调用；gapless 守卫直接消除
  自旋类别。

### D3: pass 投向下 blocked→uncertainty 由 materializer 统一完成，传入"交付姿态"

`materialize_report_plan` 增加一个确定性的交付姿态输入（`blocked_as_uncertainties: bool`，由
node 用与路由完全相同的输入计算：fallback 激活 ∨ gapless ∨ wave2_degraded）。姿态为真时，
每个 blocked 判定产出一条强制不确定项：admitted 判定携带其 bounded limitation note；保守回退
投影自然是 insufficient（D1），无需特殊文案分支。

- 为什么在 materializer 而非 node 拼装：plan 是披露的唯一权威产物；集中一处可测
  （现有 `test_readiness_real.py` materializer 组测试直接扩展）。
- 现有语义保留：`repair_targeted` 时 blocked 只计数不进 plan（不变）。

### D4: 三条观测事实走现有 node-level 事件通道，闭合枚举字段

- readiness visit fact：category=node、phase=readiness，新增闭合字段（route、blocked_count、
  可选单一 pass-guard 旗标、exhausted 时的结构失败码集合）。结构性失败码本就是闭合的
  `HardRuleFailure.code` 枚举，直接复用。
- targeted no-op fact：category=node、phase=targeted_evidence，闭合 reason=`drained_no_op` +
  gap 计数 0；仅 0-intent visit 记录。
- 事实记录沿用 `dependencies.event_recorder` 既有通道（readiness 的 fallback 事件已经这么走），
  不新增事件类别、不碰 journal schema 版本。
- 失败安全：事实记录 try/except 吞掉（与 fallback 事件同款），观察失败不得影响路由。

### D5: RER-009 合规修复走"发布链补全"方向，先以单元 seam 定位

BUG-057 观察到的误报（terminal 已有诊断引用仍报 journal 不可用）在代码上的候选断点：
readiness 自写 terminal（非 gate kernel）不产 `latest_incident`，`run_experience` 走
`RESEARCH_BLOCKED`/`certainty=UNKNOWN` 回退分支，`_terminal_diagnostic_reference` 派生的引用
可能从未被 observation publisher 发布到 journal → `_incident_diagnostic_location` 校验失败 →
如实报 unavailable。实现任务先在 `run_experience` 单元 seam 上复现（构造 blocked@readiness 的
BundleControlResult + 未发布/已发布两种 observation view），确认断点后补发布链，使
RER-009 的 gate-blocked 场景对 readiness terminal 同样成立。若调查发现语义分歧（例如该类
terminal 按契约就不该有引用），回到 change 更新结论而不是硬改。

### D6: 回归证明用 scripted-real conformance 新场景，探针转正为测试资产

诊断探针（cap 截停模型 + scripted-real 全图基建）转成确定性测试场景：readiness critic 全部
visit 越 cap → 断言终态 `completed`、`final/report.md` 发布、journal 含
`readiness_critic_fallback.execution_failed` + readiness visit fact（`route=pass`，
guard=`fallback_projection`）、trace 无 targeted_evidence。这正是 BUG-057 真实 run 的确定性
投影。模板机制：scripted model 对 readiness 模板报 over-cap usage（探针已验证的
`TemplateScriptedModel` 子类手法），fixture 放 `src_fake/.../scripted_real/`。

## Risks / Trade-offs

- [交付质量下限] fallback/gapless 交付的报告可能只有 finding 结论 + "answerability 未验证"
  披露、零结论极端情形下只有披露 → 缓解：这正是诚实交付契约（BUG-054 "部分结论 + 披露并存"）；
  结构性防线（hard rules、findings 高置信门槛、gap 披露）全部保留；runbook §5.1 语义按此更新。
- [critic 真blocked 但 gaps 空的 run 少了一轮修复尝试] → 缓解：targeted 对该判定本就无事可做
  （no-op 已被探针证明）；把"想要修复"变成披露不会比空转更差；runbook 明示该语义。
- [D1 改保守投影语义可能影响既有消费方] → 缓解：消费方已全量核对（包内 + state 字段）；
  `test_readiness_real.py` 相关断言（`test_bridge_failure_projects_repair_without_all_ready` 等）
  随语义改写。
- [观测字段扩 journal 事件可能触碰契约边界（REJ 闭合码规则）] → 缓解：全部字段闭合枚举/非负
  整数，无原文；delta spec 已在 run-event-journal 侧同步约束；journal 契约测试扩展守护。
- [D5 断点定位可能 uncover 更深的发布链问题] → 缓解：任务以单元 seam 复现为先，分歧时回 change
  更新（D5 明确回退条款）。

## Migration Plan

单仓原子落地，无部署迁移。回滚 = revert 单个 change commit。已归档 run bundle 的旧 journal 无
新字段（字段缺席即语义缺席，向后兼容读取）。

## Open Questions

- pass-guard 旗标与 fallback 事件的 journal 呈现是否需要在 demo CLI 的 fault/blocked 渲染里
  同步露出（目前只要求 journal 事实与 runbook 检查口径）——可在 apply 中按现有渲染测试的自然
  边界决定，不改变 spec。
