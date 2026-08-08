# Plan: Real Research Reliability

> 类型: 跨层设计 / 长程可靠性计划 | 状态: 已关闭，实施、验证与 OpenSpec 归档完成；BUG-022/023 已由后续确定性差分关闭 | 更新: 2026-08-03

## 进度总览

本计划用一个有边界的 OpenSpec change 收敛真实 Deep Research CLI 的外部 I/O 与结构化输出可靠性问题。它不承诺第三方服务永不失败；目标是让每一种可预期失败都有唯一事实 owner、有限恢复和可验证的安全结局。

| 阶段 | 状态 | 产物 / 退出条件 |
| --- | --- | --- |
| 1. 证据与遏制 | 已完成 | 已记录 [BUG-022](../_fixed_bugs/BUG-022-real-demo-external-read-reliability.md) 和 [BUG-023](../_fixed_bugs/BUG-023-hitl1-brief-language-schema-conflict.md)；战术修复已进入 `deerflow_research` 当前提交；仍保留一次真实 `blocked@hitl1` 的反例，不能声称端到端通过。 |
| 2. Change 设计 | 已完成，已打磨 | `openspec/changes/archive/2026-08-03-harden-real-research-external-io/` 已定义外部调用分类、恢复归属、prompt/schema 契约检查和验证边界；4/4 artifacts 已完成且通过 `openspec validate --strict`。 |
| 3. 实施与确定性证据 | 已完成 | 已登记 `DPL-009`/`HIN-013` 并通过资产、需求注册与覆盖检查；Tavily 分类/次数/退避/取消、HITL1 prompt-parser 兼容性及 CLI typed-terminal 投影的聚焦 lane 为 `125 passed`。 |
| 4. 有界真实 canary 与收尾 | 已完成并已归档（22/22） | preflight 后唯一 canary `r_YFc9zaYkbQmoU2wU5O0YyNavljOE8I4wc_HiirXlSFE` 于 `hitl1` 返回 `research.blocked`，诊断 `diag_YZ_PWs_cyMwf5j5Pr-ke8pVv`，未到达首次 HITL1 suspension；没有手工重试。完整 `make verify`、严格 OpenSpec 校验和 diff 检查均通过。比较输入契约升级遗留的三条 lifecycle fixture 已修复并以 `3 passed` 回归验证。本计划的 change 已归档；后续历史红绿差分已关闭两项直接边界 bug。 |

## 最终证据与未决限制

- 2026-08-03 完整确定性 gate：`UV_OFFLINE=1 make verify` 通过，包含 fast `2310 passed`、integration `188 passed, 4 skipped` 和 workflow `21 passed`；治理、lock、lint、format、测试资产及需求覆盖检查均通过。`openspec validate harden-real-research-external-io --strict` 和 `git diff HEAD --check` 也通过，且 `backend/`、`frontend/` 保持干净。
- 唯一 credentialed canary 仍是 `r_YFc9zaYkbQmoU2wU5O0YyNavljOE8I4wc_HiirXlSFE`，安全事实仅为 `research.blocked@hitl1` 与 `diag_YZ_PWs_cyMwf5j5Pr-ke8pVv`。它没有到达 Tavily 读取或首个 HITL1 suspension，故不能证明外部读取可用性、prompt/schema 复现，或任何特定 provider 根因；不会因本计划再运行一次。
- 初始 canary 只证明 `research.blocked@hitl1`，并不识别两项 bug 的直接根因。随后以历史实现和当前实现的同输入红绿差分重放直接 Tavily adapter 与 prompt/parser 契约，且针对选择集 `24 passed in 1.45s`；两项 bug 已移至 `_fixed_bugs/`。不得将 generic blocked 重新解释为任一已关闭 bug。
- 归档前审查已复核 Control Placement Review、战术提交范围 `ef84e59^..ef84e59`、当前工作树范围、未决任务和全部确定性/canary 事实；未发现需要新增的 action item。`harden-real-research-external-io` 已完成主规范同步并归档；本计划作为实施与复盘记录以 `CLS-028` 关闭。后续的差分回放提供两项独立关闭证据，且不改变 canary 的已记录事实。

## 背景 / 现状

`bash deerflow_research/run/real-research.sh` 是用于检查真实模型和网页读取接线的 standalone CLI，不是生产恢复客户端。2026-08-02 的真实运行曾在 `hitl1` 返回安全投影 `research.blocked`；保留的 run `r_I1j6YtWqBkeMHRWiuDqUD7jz4a2YNPMXqU7uwSp28cc` 与诊断 `diag_XTCS3_3qanyrC1PQVziGg5-X` 证明“本地配置可通过”不足以证明运行链路可走通。

该调查已暴露两个独立但相关的问题：

1. BUG-022：零工具 HITL1 的 model bridge 预算曾短于同类阶段；demo Tavily `search` / `extract` 是幂等读取，却曾把所有异常压成一次性不可用结果，缺少单次 deadline、瞬态分类和有限重试。
2. BUG-023：HITL1 prompt 曾要求 `StructuredBrief` 禁止的 `brief_summary_language` 字段，使模型按 prompt 返回时必然触发 extra-field schema failure。

当前提交已经将 HITL1 单调用 wall-time 对齐至 60 秒、为 Tavily 读取加入三次以内的短退避，以及移除冲突字段。这些是正确的遏制措施，但不是 change 的结束证据：仍须确认分类没有被 CLI 的通用 `research.blocked` 投影抹掉，也须证明“模型 prompt 所列 JSON”持续与严格 parser schema 同步。

2026-08-03 的合并确定性 lane 已获 `125 passed`，资产、需求注册和需求覆盖检查也已通过。随后唯一一次真实 canary（`r_YFc9zaYkbQmoU2wU5O0YyNavljOE8I4wc_HiirXlSFE`）仍在 `hitl1` 以 `research.blocked` 结束，诊断为 `diag_YZ_PWs_cyMwf5j5Pr-ke8pVv`，未产生首次 HITL1 suspension 或后续阶段证据。该事实不证明 Tavily 读取、prompt schema 或任一 provider 为根因；不进行手工重试。

## 决策 / 方案

### Change 边界

拟议 change：`harden-real-research-external-io`。

Primary causal owners 是 `deerflow_research/scripts/_demo_core.py` 的直接 Tavily 读取边界，及
`deerflow_research/src/deerflow_deep_research/graph/nodes/hitl1/` 的 model-visible brief
contract 与 strict admission compatibility。`RuntimeNodeAgentBridge` 仍是相邻、既有的
admitted model-service classification contract；CLI 只消费 shared typed outcome，不能自行猜测
或重写失败类别。

该 change 要建立四个相互配合、但不形成第二个全局 controller 的保证：

1. **外部 I/O 的闭合分类和恢复归属。** 每个 provider/model 或只读 web call 先在直接边界确定 timeout、暂态网络、429/5xx、认证/输入、结构化输出和未知失败。只有其既有的 graph/controller 或幂等工具 adapter 可执行有限恢复；不让 CLI、prompt 或 worker 通过捕获泛化异常另造 retry。
2. **明确且有总上限的重试。** 每次尝试有 deadline；只对已证明幂等且可恢复的类别重试；退避可取消；重试总次数、wall time 和现有 node/worker 预算共同形成上限。认证、输入、非可恢复 4xx、未知异常和取消不会被“再试一次”掩盖。
3. **模型输出契约的同源验证。** 模型可见 expected JSON 与 `StructuredBrief` 等 strict parser 的 accepted key/value/bound 由确定性检查覆盖。语言等系统约束留在 instruction 或 parser validation，不伪造未持久化的模型字段。
4. **从确定性复现到有限 live evidence 的验证梯子。** fake/provider seam 覆盖分类、次数、backoff、取消、schema 不兼容与 typed terminal projection；只有这些通过后，才运行一条限时真实 CLI canary。真实检查补充接线证据，永远不能替代确定性回归测试。

### 事实与投影

| 事实 | 唯一 owner | 允许的下游投影 |
| --- | --- | --- |
| 单次 provider/model 调用的直接失败分类与安全 observation | `RuntimeNodeAgentBridge` | `NodeProblem`、现有 graph recovery/terminal incident |
| 每个 graph phase 是否及如何重试 | 该 phase 的既有 graph node/controller | 有界 lifecycle result 和 recovery facts |
| Tavily 只读读取的尝试、deadline 和 retry eligibility | demo tool adapter | 有字节边界且脱敏的 tool result；worker 决定后续工作 |
| brief JSON 是否符合接受 schema 与语言约束 | HITL1 prompt/parser 与 domain validator | checkpointed advisory proposal 或既有 schema-invalid outcome |
| 人可见的 terminal 类别、诊断引用与 legal next action | `ResearchRunExperience` / shared `Terminal` | standalone CLI 的安全文本和只读 inspect 指引 |

## 风险 / 取舍

| 风险 | 缓解 |
| --- | --- |
| 把“外部不可靠”误修为无限重试，消耗研究预算或掩盖认证错误 | 将 retry eligibility、attempt cap、per-attempt deadline 和 cancellation 写为需求与测试；live canary 也有显式次数/时间界限。 |
| 每个 node 或 CLI 复制 provider 分类，随后再次发生投影漂移 | 分类只在直接 I/O owner；graph 仅决定既有 route/recovery，CLI 只渲染 shared typed result。 |
| prompt 新增字段再次领先于 Pydantic schema | 对每个 real structured prompt 加 parser-compatibility fixture；系统约束不要求模型输出无对应持久化字段。 |
| 真实服务偶发失败导致错误宣告完成 | live run 只作为补充 evidence；未越过 HITL1 时保持 bug/plan 活跃，记录安全 reference 和下一步。 |
| 将 standalone demo 扩大为 upstream 产品可靠性承诺 | 不修改 `backend/`、`frontend/` 或 DeerFlow public interfaces；不宣称跨进程 resume、生产 SLA 或第三方可用性。 |

## 落地关联

- OpenSpec change：`openspec/changes/archive/2026-08-03-harden-real-research-external-io/`（本计划阶段 2）。
- 相关既有能力：`node-agent-runtime`、`hitl1-node`、`demo-pipeline`、`workflow-failure-outcomes`、`research-cli-onboarding`。
- 后续顺序：本计划的变更与复盘均已完成，计划本身移至 `_backlog/_done/_closed_plans/` 并登记 `CLS-028`。后续历史红绿差分已为 `BUG-022` 和 `BUG-023` 提供各自独立关闭证据；generic `research.blocked` 不能被用于推断或重新打开任一 bug。

## 非范围

- `backend/`、`frontend/`、生产 Gateway/Web/IM 的 provider policy。
- 任意第三方 provider 的无限可用性、跨进程执行恢复、自动切换供应商或无限 fallback 链。
- 在没有新的证据前，扩大 Wave0/Wave1 的总研究预算；现有 900 秒/200 tool-call worker limits 不是本次已证实的根因。
