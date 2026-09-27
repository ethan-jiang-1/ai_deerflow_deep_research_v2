# Plan: Deep Research Harness 的 Agent 支持与证据反馈提升

> 类型: 分阶段设计 / 待准入 | 状态: 仅计划，未批准任何产品语义或代码变更
> 基线: 本次只读调查；执行前重核代码、主规格、现有证据与活跃工作项
> 入口: 本计划服务于 `deep_research_harness/`；后续契约/行为变更各走独立 OpenSpec change

## 目标与读法

使两种 agent 都能独立走通各自的最短路径，并准确知道证据的边界：

1. **维护本应用的 Coding Agent**：从问题找到唯一 owner、适用契约和最低验证 seam；遇到失败时从受限事实定位原因，不靠解析 TUI 或凭空猜测部署状态。
2. **使用本应用的 DeerFlow 专用 Agent**：把用户意图映射到合法的 `deep_research` 动作，诚实呈现类型化结果；研究节点在限定预算/工具内提出候选，质量主张有相称的实际模型证据。

这两种 agent 不是一个新 controller。本文的“提升”不是增加 agent 自治权，也不是把现有图节点改造成通用 coding agent。先证明确有失败，再选最小 owner；每个阶段可独立停止。

## 基线：哪些已经有了

| 事实 | 现行 owner / 证据 | 本计划不重复建设 |
| --- | --- | --- |
| 应用是 DeerFlow 之上的独立运行时；Run Bundle-local State 管生命周期，StateGraph 管路由，ledger/gate 管证据接纳；节点 agent 只提候选 | [运行时架构](../../deep_research_harness/docs/runtime-architecture.md)、[运行旅程](../../deep_research_harness/docs/run-lifecycle-walkthrough.md)、[节点工厂](../../deep_research_harness/src/deerflow_deep_research/agents/factory.py) | 新持久 agent controller、第二 checkpoint/registry、把候选当接受事实 |
| 公共工具已有 `infra_probe/start/resume/status/cancel/refine`，生命周期调用独占且经 trusted runtime；结果已有 `code/status/phase/terminal_incident/legal_next_action` | [工具](../../deep_research_harness/src/deerflow_deep_research/tool.py)、[结果契约](../../deep_research_harness/src/deerflow_deep_research/domain/lifecycle.py)、[公共技能](../../deep_research_harness/config/public-skill/deep-research-controller/SKILL.md) | 第二套动作入口、从会话文本推断 Bundle 权威 |
| 节点执行已有预算、工具 allowlist、路径约束、取消/失败分类和受限结果；Run Event Journal 是可丢失/不完整的诊断，不是恢复依据 | [执行策略](../../deep_research_harness/src/deerflow_deep_research/agents/policies.py)、[观测契约](../../deep_research_harness/src/deerflow_deep_research/domain/run_observation.py) | DSH 式工具总线、通用审批/沙箱/日志体系 |
| Coding Agent 已有入口、node-local `workflow.md`、ADR、OpenSpec、结构/测试门禁和脚本化真实工作流 | [应用指南](../../deep_research_harness/AGENTS.md)、[ADR 索引](../../deep_research_harness/docs/adr/README.md)、[测试与评估](../../deep_research_harness/docs/testing-and-evaluation.md) | 重写 AGENTS.md、再造知识目录或批量增设 Skills |

外部材料的可借鉴原则是“事实有 owner、正确路径可发现、机器反馈能证明会红、按需披露”；它的 Phase 顺序是 FAQ 对钉版 DSH 的归纳，不是本项目的授权设计。对照本仓时，以本仓规范和可观察失效优先。FAQ 本地输入在仓库外，**不得成为计划执行时的唯一证据依赖**。

## 可证 GAP 与待证假设

| 分类 | 具体证据与边界 | 初步判断 |
| --- | --- | --- |
| 已证的可消费性缺口 | [本地诊断命令](../../deep_research_harness/scripts/demo_sessions.py) 只将已有 `WorkbenchDiagnosisView` 经[人类文本 renderer](../../deep_research_harness/scripts/_inspect_view.py) 输出；该 view 本身已有有界、脱敏的 availability/summary/events/incomplete 标记，见[投影契约](../../deep_research_harness/src/deerflow_deep_research/domain/session_workbench.py)。 | **仅本地操作/维护路径**缺稳定机器可读的受限诊断出口。不是“没有日志”或“需要再建一套 journal”。先验证 Coding Agent 是否真的卡在文本解析上。 |
| 已证的产品接口差异，是否要改仍未定 | 公共[工具](../../deep_research_harness/src/deerflow_deep_research/tool.py)没有选中 Bundle 的细粒度 journal-inspect 动作；[生命周期结果](../../deep_research_harness/src/deerflow_deep_research/domain/lifecycle.py)不承载 journal 内容。 | 专用 Agent 不能经现有公共工具直接读细粒度诊断，但这可能是刻意的安全/上下文边界，**不能直接判为 bug**；须有真实用户旅程再决定是否对模型公开。 |
| 已证的证据边界 | [测试与评估](../../deep_research_harness/docs/testing-and-evaluation.md)明确脚本化 controller handoff 只证明加载与接线，不证明模型自己选对意图；六项 live canary 不证明全链。[认知评测](../../deep_research_harness/docs/cognitive-evaluation-suite.md)已有 controller/planning selected-live 案例，但 Wave0/1/2 cognitive-program 仍为 deterministic-only，评审非日常 CI。 | 欠缺对**新鲜重复的真实语义选择与研究质量**足够强的结论；不是“没有 live 评测”。先用已有评测途径取证，不将绿色 pytest 写成质量通过。 |
| 需样本证明的假设 | 一次新 Coding Agent 走查可能暴露 owner 路由、失败定位或负知识检索成本；现有[入口](../../deep_research_harness/AGENTS.md)及[节点 reader contract](../../openspec/specs/node-agent-reader-interface/spec.md)已经覆盖大部分结构。 | 无具体卡点前不改入口、ADR、Skill 或目录预算。 |

历史[agent-native 渐进计划](../_done/_closed_plans/deep-research-harness-agent-native/deep-research-harness-agent-native-progressive-plan.md)已经完成 Bundle/direction loop 及 HITL1/Wave0/Wave1/Wave2 的认知 owner 迁移，不能把其旧诊断当成现行缺口；[历史测试资产审计](../_done/_closed_plans/deep-research-harness-agent-native/deep-research-harness-test-asset-audit.md)同理只用于解释取舍，不用其旧计数宣称现状。

## 分阶段路线

### 0. 两条真实路径走查（优先，不改产品）

- **Coding Agent 路径**：选最近一笔已完成且可重放的小变更/故障；从任务意图独立定位 owner、主规格、最窄可变红测试、验证命令与现行 ADR；记录每次“靠猜”“找不到证据”“命令输出无法安全解析”的实际卡点。不要仅用十维自评取代实操。
- **专用 Agent 路径**：在现有已注册案例中选一个意图有歧义或方向变更的短旅程；分别记录实际模型选择（与测试预写 tool call 区分）、加载的 controller skill、typed result、诚实呈现和禁止动作；遇到研究质量问题再选对应节点案例。
- **产出/验收**：一页证据表：输入、绑定的 Bundle/案例与版本、期望/实际、权威结果、证明强度、缺口 owner 和最低红灯 seam。发现无实质可消费性/语义失败时，停止相关分支，关闭或修订本计划；不为追求“全十维”制造工作。
- **权限/成本**：本阶段以只读、离线、已有记录与脚本案例为先；真实模型/网络/凭证只在人工选定预算和明确同意的评测条件下执行，不默默重跑全链或输出密钥。

### 1. 本地诊断的受限机器可读投影（只有阶段 0 证实需求才做）

- **Primary owner**：`deep_research_harness/scripts/demo_sessions.py` 的本地检查出口；复用 `runtime` 现有已授权的 `WorkbenchDiagnosisView`，必要时在相邻 presentation 模块做纯投影。该脚本不是产品公共工具或新的生命周期 writer。
- **候选变更**：现有 `inspect <bundle-id>` 默认文本保持兼容，可选 `--format json` 输出固定版本、脱敏、限定字段/数量的诊断摘要；明确 `available/incomplete/unavailable`，不把 exit 0、空事件或 journal 丢失写成“无失败”。不直接 `model_dump` 整个 view，也不让外部路径/manifest 成为 Bundle locator。
- **最低证据**：对现有 Bundle、损坏/丢失 Bundle、缺失或不完整 journal、越界 id 的脚本入口测试；JSON 可解析且字段闭集、无原始 prompt/网页正文/凭证/主机路径；默认文本和原退出码语义保持不变。引入故意越界/泄露的负例，确认守卫变红。即便本地 JSON 成功，也不能宣称产品专用 Agent 获得了 inspect 能力。
- **准入**：若只是本地展示便利且不改契约语义，按已有 owner 的最小维护路径处理；如改了观察或退出码承诺，则先开以该投影为唯一 primary owner 的 OpenSpec change。

### 2. 用现有评测路线验证 Agent 自主判断（可与阶段 1 独立）

- **Primary owner**：现有 controller 及节点的 `evals/control/` 案例、`tests/live/` 入口和 review protocol；选择一条因阶段 0 失败而需要提高证据等级的路径，不同时重写 prompt、gate 和评测系统。
- **先做 controller**：复用 `public-controller-direction-loop@v1` 和 `topic-planning-direction-loop@v1` 的真实 loader/受控模型重复评审。覆盖新请求、相关 pending 答复、同 Run direction、status、明确 cancel、歧义停手，以及 blocked/unavailable 时诚实告知合法下一步；核对“模型自己选择”而不是测试预写动作。
- **再看研究节点**：若阶段 0 指向来源选择或证据合成质量，针对那个节点选已有案例/最短真实前缀；缺少选定 live 案例的 Wave0/1/2 先由人批准 case、成本和对外来源边界，再提认知评测 change。保留来源质量与内部 hash/URL 规范校验的区别；不以一个来源摘要自称原文真实性。
- **验收/停止**：每次执行记录案例/控制 digest、模型/配置版本、样本数、预算、实际动作、误选/拒绝/澄清、失败与未知，评审使用现有 `pass/limited/inconclusive/failed`；基线不充分就报 `limited`，不能以样本少强设 PR 质量阈值。可复现失效才下沉到最窄 deterministic regression，再对照改动前后同一案例。selected-live 仍不等于 full-real release 证明。

### 3. 是否让专用 Agent 读取诊断（有明确受益和人批准才开启）

- **触发**：阶段 0/2 明确观察到用户或专用 Agent 需要解释某个可用 Bundle 的失败，而当前 typed result + `legal_next_action` 不足；确认现有人类查看命令不是充分替代，并评估模型看到诊断的隐私/提示注入风险。
- **决定权**：这是公共 tool/AI-facing 语义扩面，需人批准产品用途和披露范围，再单列 OpenSpec change；默认方案仍是保持现有六动作和人类诊断路径。
- **如获批准的最小边界**：`domain/` 定义受限只读投影及兼容策略；`runtime/` 只消费选中 Bundle 已授权、受限且可能不完整的 journal；`tool.py` 经现有 trusted scope/Bundle 校验提供入口；controller skill 只解释事实，不调用任何新恢复路由。设计需列清旧消费者、字段红线、超限/丢失/取消、失败时合法动作及已发生读取的不可逆性。
- **必需红灯**：跨用户/跨 Bundle/丢失 Bundle 不回退读取、旧结果兼容、注入内容不能授予权限或触发新的 lifecycle 动作、journal 不完整不被报成功、内容脱敏/大小上限、产品端到端专用 Agent 只读旅程。任何一个无法闭合就不扩公共接口。

## OpenSpec 消化映射（2026-09-27 补记）

本计划的阶段不塞进一个 change：每个阶段一个 owner、可独立停止（计划自身的准入原则）。
另有一次同期的独立发现（证据纪律）先于阶段 0 落地，因为它在本次会话里已被实测三次。

| 来源 | 消化载体 | 状态 |
| --- | --- | --- |
| 同期实测发现：证据缺乏载体（演示 CLI 套件骑环境现场 → 假红；`git commit` 与 verify 串联 → 红着提交；runbook 承诺无断言 → 漂移） | change `add-evidence-receipts-and-proof-lanes`（lane 登记表 + 回执 runner + 变异 lane，纯工具，skip_specs） | 已建，plan 门绿，待 apply |
| 同上：让回执在关账时有牙齿 | change `bind-closeout-to-proof-receipts`（PRS-009 delta：注册第七个组件 checker + 关账要求 runner 回执） | 已建，plan 门绿，**待人拍板规范语义** |
| 阶段 0（两条路径只读走查 → 一页证据表） | 后续 change `run-agent-support-evidence-walkthroughs`（skip_specs；交付物=证据表 + 每分支 go/no-go） | 建议在 A1 落地后执行：走查结论本身要带新鲜回执 |
| 阶段 1（本地诊断 JSON） | 仅当阶段 0 证实：单独 change，primary owner = `scripts/demo_sessions.py` 的只读投影 | 待证 |
| 阶段 2（controller/节点认知评测） | 单独 change，owner = 现有 controller 与节点评测路径；与 [`todo-adopt-framework-engineering-protocols.md`](../todos/todo-adopt-framework-engineering-protocols.md) 的"评测可复现协议"相交时先定 owner 与去重 | 待证 |
| 阶段 3（公共 tool 读诊断） | 需人先批准产品用途与披露范围，再单列 change | 待裁决 |

阶段 0 的走查工具已就位（同期的调试器探索面）：`/harness`（组合/节点类型/可读投影）、
`/targets`（可调试对象清单）、`/inspect <id>`（帧与类型化工作单元）、`/context <node>#<n>`
（某次调用收到的指令与被允许的工具/预算）。用它们记录"靠猜/找不到证据"的卡点，而不是解析
TUI 文本。

## 明确不做

- 不修改、翻查或重设计 `deerflow/`；它提供 LangGraph、模型/工具/宿主能力，应用通过已核对的公共接口接入。需要框架能力时先界定 public-interface/兼容问题再单独决策。
- 不照搬 DSH 的插件图、pre/post-execute waterfall、approval、session 注入、compaction、subagent 继承规则或 `CLAUDE.md` symlink；这属于另一种宿主的控制面。本仓 `CLAUDE.md` 的薄导入已被现行契约接受。
- 不批量增加手写 catalog/ADR/Skills/测试元数据；不把 journal、诊断 JSON、TUI 或留存观察升格为 State、证据 ledger 或恢复权威；不把 deterministic green 当模型认知质量。
- 不把本计划本身当 OpenSpec proposal、spec、任务或对现行行为的批准；每个后续 change 只设一个 primary causal owner，按相应 policy、红绿测试、负例和独立验证闭环。已有[机制待办](../todos/todo-adopt-framework-engineering-protocols.md)的 `stop_reason`/评测复现/waiver 属另一条线，若实际相交先明确 owner 和去重。

## 关闭与回看

本计划的完成条件是阶段 0 的两份证据走查有结论，阶段 1/2 分别被证实并通过相应独立 change 交付或有证据地停止，阶段 3 获明确“保持现状”或单独批准并验收。每阶段结尾记录哪一个判断改变了、哪个能力仍是未知；没有 live 凭证时标 `UNVERIFIED`。完成后按[_backlog 搬迁规矩](../README.md)归档本 plan，并同步三处索引/计数；不能因为本文写完就标完成。
