# Plan: TUI Workflow Debugger 递进执行计划

> 类型: 递进执行计划 | 创建: 2026-08-31 | 重写: 2026-08-31 | UX/一致性审计: 2026-09-01
> 状态: 当前唯一活跃 plan；D6-D8 已定；**Cpre/C0/C3/C4a 已归档**（均 2026-09-02；C4a=`2026-09-02-add-local-workflow-debug-driving`，矩阵 7/7+全链路 terminal 证明）；**C4b apply 进行中**（propose+plan gate 绿；launcher/alias/attach-replay intents/入口测试 5/5 已落地；剩余：Node Context pane 接线、Pilot 三尺寸旅程、README/COMMANDS 按 DRC-006 重做、sync/archive）；终线未开始（需网络/凭证）
> 当前决策与执行权威: 本文件
> 前置证据与原计划纠错: [tui-step-debugger-grounding-review.md](tui-step-debugger-grounding-review.md)
> 目标体验与计划追踪: [tui-workflow-debugger-target-ux.md](tui-workflow-debugger-target-ux.md)
> 历史材料: `_archive/tui-interactive-campaign*-digested.md` 只作 provenance，不再定义当前 TUI debugger
> 编号说明: 历史 C1 `close-provider-timeout-budget-handback` 与 C2 `add-suspended-run-recovery` 已归档；
> Cpre/C0 是后续审阅新增的纠错闸门，不是漏掉 C1/C2，也不表示它们无效。
> 当前用法: 严格按 `Cpre -> C0 -> C3 -> C4a -> C4b -> real validation` 推进；每个 change 归档且 gate 全绿后才进入下一阶段。

任何人 propose、review 或 apply Cpre/C0/C3/C4a/C4b 前，必须完整阅读本文件；当工作涉及原计划纠错、
Journal/Bundle/checkpoint 权威、E4 实验、被拒方案或延后项时，还必须完整阅读 grounding review。
进入 C3、C4a、C4b 或 real validation 前，还必须完整走读 target UX 中的主旅程、文件边界、负路径和
traceability matrix。
supporting 文档与本文件冲突时，以本文件为当前决策权威。主 specs 和应用 runtime/domain 代码共同
约束当前已实现事实；二者或多个主 specs 彼此冲突时，必须先通过 Cpre 或新的 corrective change
明确 owner、目标 contract 和同步范围，不能由 proposal、adapter 或单份旧 spec 私自选边。

## 文档控制与解释顺序

| 文档 | 当前角色 | 可以决定什么 | 不可以决定什么 |
| --- | --- | --- | --- |
| 本文件 | 唯一活跃 plan | 阶段顺序、owner、contract 边界、gate、no-go、OpenSpec 任务来源 | 覆盖已经归档的 OpenSpec 历史或把目标体验冒充当前能力 |
| [target UX](tui-workflow-debugger-target-ux.md) | 受控的目标体验与验收地图 | 完成后的 operator 旅程、负路径、可见状态及 plan 追踪 | 新增 runtime authority、改变阶段顺序或直接充当 implementation backlog |
| [grounding review](tui-step-debugger-grounding-review.md) | 冻结到 2026-08-31 的前置证据 | 解释旧方案为何失效、记录 dated evidence 和被拒方案 | 覆盖 2026-09-01 后的 Node Context/Files/launcher 决策或继续追加实施结论 |
| `_archive/tui-interactive-campaign*-digested.md` | 冻结历史 provenance（已消化） | 解释 010/020 战役来源和旧决策形成过程 | 提供当前 debugger task、interface、阶段状态或验收权威 |
| 主 specs + `deep_research_harness/` 代码 | 当前已实现事实 | 说明已经存在的 contract 与行为 | 不经 OpenSpec 自动改变本 plan 的目标或未来 ownership |

无上下文执行者按“本 plan -> 当前阶段对应 grounding -> target UX 对应旅程/负路径 -> 主 specs 与
应用代码 -> 当期 OpenSpec change”阅读。`_archive/` 路径本身不赋予文档权威；不得从三份 campaign
历史中复制 unchecked task、类名或接口建议进入 proposal。

## 起点：原始意图与阶段因果链（先读）

本节保留这项工作的“为什么”，防止后续 Agent 只看到 interface、checkbox 和 change slug，却不
知道它们在阻止什么失败。它不把历史材料重新提升为当前 authority，也不替代后文任务；它只把
原始意图、历史证据、目标原则和执行顺序连成一条可复核的因果链。

### 原始意图

最初的诉求是：**“像传统软件开发 debug，一步一步把 agentic workflow 调对，也能串起来跑。”**
这里的“像 debugger”不是给现有 TUI 多加几个按钮，而是让 contributor/operator 能够：

1. 在**同一张真实 StateGraph、同一套 Bundle lifecycle、同一个 checkpoint thread**上，既逐边界
   Step，也能 Continue/Run；调试路径不能成为另一张只在 demo 中成立的 graph。
2. 看懂一次 logical node 真正收到的初始 context、执行约束、内部活动、安全产物和失败原因，并
   区分 captured runtime fact、当前源码/文件投影与未被保留的历史。
3. 只在可信的 node boundary 或正式 HITL request 上暂停和输入；进程退出后仍能凭 exact Bundle/
   cursor attach、replay，而不是靠“最近一个 run”猜测现场。
4. 调整运行节奏、breakpoint 和观察深度。发现 prompt、代码或配置问题后，在正常开发工具中修改
   并创建新 Bundle 重跑；v1 不原地篡改旧 checkpoint/State。

成功标准因此不是“界面能走完 happy path”，而是 operator 可以相信：屏幕所说的 run、边界、
context、等待输入和恢复位置都对应同一份 canonical execution。即使移除 Textual，headless
interface 仍应能证明相同的 trace、drive、并发拒绝和恢复语义。

### 为什么不能直接扩建旧 TUI

旧 TUI 曾先后承担 Primary User UI、demo visualizer、recon/workbench、live progress 和 orphan
attach。这些尝试留下了有用的交互经验，也让 presentation script 逐渐知道过多 runtime 细节。
debugger 需要的可信事实实际分布在不同 owner：StateGraph/checkpoint 决定 durable boundary，Bundle
lifecycle 决定 exact identity、pending input 和 recovery admission，Journal 记录有界活动事实，
runtime bridge 才知道 node-agent invocation 当时真正生效的初始 context。

TUI 无法从文件时间、phase、当前源码或若干事件自行重建这些事实。若继续在 adapter 内猜测并叠加
卡片/按钮，会得到一个看起来完整、实际可能说谎的 debugger：

| 历史压力或失败 | 容易产生的假结论 | 当前必须坚持的纠正 |
| --- | --- | --- |
| live progress 选择 latest active/suspended Bundle | 最近更新的 run 就是本次 run | admission/attach 起绑定 exact Bundle；拿不到 handle 就 fail closed |
| Journal `completed` 先于 checkpoint commit，且 `suspended` 曾被真实 model 拒绝 | 有事件就等于 durable boundary 已完成 | checkpoint 是 commit authority；Journal 缺口显式 degraded |
| 用相邻 checkpoint 时间戳计算耗时 | 两帧间隔就是 node 执行时间 | wrapper 只测实际 invocation；operator/HITL 等待不计入 node duration |
| 用当前 resource/source 事后重建 prompt | 当前文件就是历史模型当时看到的内容 | invocation 前 capture immutable context；current source 只作 MATCH/DRIFT 对照 |
| walkthrough 与主 specs 保留旧 HITL2 人工菜单 | TUI 应显示第二个 Answer/Resume | 先由 Cpre 收敛 authority；当前 real HITL2 autonomous，只有正式 pending request 才能输入 |
| orphan `ContinueRun` 已能恢复到终态 | 它也可以充当 debugger continue | 保留既有 recovery intent；debug driving 使用独立 local command 与 stop policy |

### 历史证据教会了什么，又没有证明什么

010/020 campaign 与 digested 文档只作 provenance：它们解释问题如何暴露，不再产生当前 task。从中
保留的教训是：fixture UI smoke 能证明 adapter 接线，却不能证明真实 cognition、report quality 或
exact attribution；网络/进程失败会留下 suspended/orphan run；latest 证据会造成 false positive；
typed option 不一致会让人工选择成为死路；非空 output/profile 不能证明变化来自某次 human decision；
有界 Journal 也不能独自承担完整能力归因。

E4 证明同一 recipe/compile path/saver/thread 可以完成 bootstrap boundary pause -> HITL1 typed
resume -> 继续或运行到 completion，因此不需要 step 专用拓扑。E4 **没有**证明 restart、双进程竞争、
refinement、stale lease、long-node pause、mid-node crash 或未来并行拓扑；这些必须由 C4a 的
deterministic matrix 关闭，不能由 UI happy path 或旧 campaign 截图代替。

### 从教训导出的设计原则

1. **一个执行事实源**：run、step 和 replay 共享真实 graph、Bundle lifecycle 与 canonical
   checkpoint；debugger 不创建第二份 State 或隐藏拓扑。
2. **边界级控制**：v1 只在顶层 logical-node committed/suspended/failed boundary 停止；模型和工具
   内部活动是只读 narration，不承诺任意指令级中断。
3. **runtime 拥有语义**：capture、projection、drive、lease 和 recovery 由 runtime/domain deep
   module 负责；Textual 只展示 typed view、提交 closed command。
4. **live/replay 同构**：两者消费同一 versioned schema/projector；live 曾显示但未 durable-retain
   的事实，replay 不得继续冒充存在。
5. **exact identity、fail closed**：Bundle、cursor、request、context 和 command 必须精确关联；
   missing、stale、gap、busy 或 uncertain 必须显式呈现，不能回退猜测。
6. **权威与投影分离**：checkpoint、lifecycle、Journal、captured context、current workspace/source
   各自说明自己知道的事实；一个投影不能因“看起来合理”取代另一个 owner。
7. **只响应正式 HITL**：operator 只能回答现有 typed pending request；TUI 不创造 prompt、route 或
   human subject。当前 HITL1 是人工边界，HITL2 是 autonomous graph phase。
8. **原 run 不被随意改写**：v1 无 route/profile/arbitrary State mutation；未来 fork 必须新建有
   lineage 的 Bundle，不能把历史 replay 变成可变现场。

### 为什么必须按 Cpre -> C0 -> C3 -> C4a -> C4b 推进

| 原始压力 | 必须先关闭的 contract 缺口 | 阶段 | 该阶段不拥有 |
| --- | --- | --- | --- |
| HITL2 owner/代码与依赖主 specs 冲突 | 原子收敛 autonomous HITL2，保留内部 route/topology | Cpre | debugger runtime、UI 或 graph 行为变更 |
| persisted observation 会丢/误述 suspended，live trace 会串 Bundle | 修好 event truth 与 exact correlation | C0 | 卡片 UX、step/continue driving |
| 没有可信的 boundary/context/files 投影 | 建立可回放的 observation deep modules 和只读 presentation | C3 | 启动、推进、恢复 graph |
| 没有合法的 step/pause/attach owner 与并发 fence | 建立 headless driver、control lease、恢复/幂等 contract | C4a | Textual 私有执行语义 |
| operator 需要可用入口和控制面 | 把 typed views/commands 接入同一 TUI 与 launcher | C4b | 新增 runtime authority 或绕过前阶段 denial |
| deterministic tests 不能单独证明真实使用感 | 用固定问题做 bounded real validation | 终线 | 用真实模型替代 contract tests |

顺序本身是正确性约束，不只是项目管理偏好。上游 authority/truth 未闭合时，后续 UI 越完整，错误
事实越容易被包装成可信体验。任何阶段发现必须增加 owner、persisted/public surface、第二张 graph、
远端控制或任意 State mutation，都先回到本 plan 修订，而不是在当期 change 或 adapter 中顺手实现。

### 无上下文 Agent 的判断规则

| 信息类别 | 位置/例子 | 使用规则 |
| --- | --- | --- |
| 原始动机与历史证据 | 本节、grounding review、campaign provenance | 解释“为何”，不直接生成任务；dated evidence 在 propose/apply 前重验 |
| 已验证的当前事实 | §0.3、§9、主 specs 与应用代码 | 描述“现在是什么”；spec/代码冲突先 corrective change，不私自选边 |
| 已批准的目标决策 | §0-§3、target UX 的受控目标 | 约束“最终必须是什么”；不得把目标写成当前已有能力 |
| 执行任务与状态 | §4-§8、checkbox、§L 最新记录、当期 OpenSpec change | 决定“现在做什么”；只做当前 gate，完成后更新本文件 |

若历史文档、旧 plan 记录、target UX、当前 spec/代码或 active change 冲突，先按“文档控制与解释
顺序”定位事实与 owner，不能挑选最顺手的一份材料继续实施。尤其不能为了让界面更顺滑而弱化
exact binding、typed pending input、degraded/unavailable 表达、lease/fence 或 no-State-mutation 原则。

## 0. 执行摘要与已定决策

### 0.1 目标

建设一个本地 contributor/operator **agentic workflow debugger**：用同一张真实 StateGraph
完成自动运行、节点边界步进、正式 HITL 交互、运行观察、进程恢复和历史回放。Textual TUI 是
主要 presentation adapter；未来其他本地 adapter 可复用同一 trace/drive modules。

这不是“把日志画成卡片”，也不是 dormant 的 Primary User TUI 复活。solid 的判据是：即使删除
Textual，headless tests 仍能通过相同 interface 可信地 trace、step、resume 和拒绝并发冲突。

### 0.2 D6-D8 决策

| 决策 | 结论 | 含义 |
| --- | --- | --- |
| D6 形态 | **通过** | 一个真实 graph + runtime-owned debug driving；放弃每 Node 独立 CLI |
| D7 顺序 | **修订后通过** | 已归档 C1/C2 不重开；当前链为 Cpre authority -> C0 truth -> C3 observation -> C4a headless driving -> C4b TUI adapter |
| D8 定位 | **通过并收窄** | 本地 operator workflow debugger；不是 Primary User product UI，不给 reflected public tool 扩权 |

### 0.3 关键纠错

1. owning `hitl2-node` spec 与当前代码规定 real HITL2 autonomous，但五份依赖主 specs 仍要求人工
   HITL2；Cpre 必须先原子收敛这组 authority，不能只修 walkthrough 或由 TUI 选边。
2. `suspended` outcome 当前被真实 `RunEvent` 拒绝，C0 必须先修复；fake-recorder 绿测不足以
   证明 Journal truth。
3. live trace 必须从 admission/attach 起绑定 exact `bundle_id`；没有 exact handle 时 fail closed，
   不回退 latest-active 扫描。
4. 现有 `ContinueRun` 只表示 orphan natural resume，保持不变；debugger continue 使用独立
   local `DebugCommand`。
5. checkpoint `created_at` 相邻差不能叫 node duration；duration 由 wrapper 对实际 invocation
   显式测量。
6. C3 只做 observation capture/projection 与只读 trace/context/workspace inspection；它可以在正式
   invocation seam 写 Bundle-private debugger snapshot，但不启动、推进或恢复 graph。`run`、`step`、
   `continue`、`pause`、`answer`、`attach` 的 runtime 驱动属于 C4a，Textual mutation-command 接线属于 C4b。
7. 同一 compiled graph 可逐次使用 `interrupt_after`，fixture E4 已证明 step -> HITL -> run
   核心路径；正式不变量是同一 recipe/compile path/checkpoint thread，不维护 step 专用拓扑。

## 1. 目标体验与操作语义

### 1.1 两层观察，一个控制粒度

- **L2 顶层边界卡片**：每次 logical-node invocation segment 在 completed/suspended/failed boundary
  形成一张卡，是 v1 唯一可 step 的粒度。普通 node visit 通常一张；HITL resume 会复用 visit id，
  因而同一 visit 可先有 suspended card，再有 completed card。当前 happy path 最短约 9 个 completed
  boundaries，真实 run 通常 10-20 个；C4a 用 topology guard 保证当前每个顶层 superstep 只执行
  一个 logical node。
- **L3/L4 内层叙述**：work unit、attempt、模型和工具调用以只读行跟随。v1 可展示安全计数、
  budget/failure facts，并为每次 bridge/node-agent invocation 展示 exact captured initial context，
  但不在模型或工具调用内部暂停。一次 node-agent invocation 可包含多次内部
  provider model call/tool loop；v1 保留其计数和安全事实，不保留每次 provider call 的完整
  raw message history。

node 执行期间显示一条 provisional running row：exact node/visit、wall elapsed、最新安全内层 fact
和 pause-requested 状态。wall elapsed 明确不是最终 node duration；只有 boundary commit 或正式
HITL/failure 后才固化 TraceFrame，避免把“仍在跑”叙述成“已完成”。

composer、Files/Inspect 视图、`/ls`、`/cat`、`/inspect` 可以继续作为 operator workbench 能力。
树视图与手敲命令必须复用同一个 bounded read interface，只浏览明确挂载且授权的 workspace、
exact Bundle artifacts、evidence 和 report；不得越出 root 读取任意 host path，也不得把 raw
checkpoint/State/secret 绕过 typed projection 与 redaction 展示，更不得获得 graph mutation 权。

Node Context 是独立的 typed inspection surface：对 LLM-bearing bridge/node-agent invocation 显示
runtime bridge 在 fresh agent 运行前捕获的 exact runtime MD、initial system/human messages、request、
enforced tool/budget policy、virtual mounts/roots 和 artifact refs；对内部 provider/tool 活动只显示
bounded counts/safe facts 和明确的 retention quality。对 deterministic node 明确显示无
node-agent invocation，但仍展示 boundary/route/artifacts/files/developer guide。当前
`workflow.md` 和源码导航可作为 developer guide 展示，但必须标为 non-runtime/current source，不能与
captured context 合并，也不能通过 package/repository 任意路径读取。

### 1.2 操作闭集

| 操作 | 精确定义 | 停止条件 / 约束 |
| --- | --- | --- |
| `start` | 以稳定 `start_request_id` 创建或重放 exact debug session/Bundle admission；返回 verified handle 后，按 Start Step 或 Start Run 策略开始 | same-id/same-fingerprint 返回同一 handle；same-id/different-fingerprint conflict；不靠 workspace 扫描，首个 running row 前已显示 exact id |
| `step` | 调用当前顶层 logical node 一次 | completed/suspended/failed boundary；不执行第二个顶层 node |
| `continue` | 从当前 boundary 按 stop policy 连续推进 | 指定 node 提交后的 breakpoint、HITL、failure、terminal 或 pause request |
| `run` | 新 run 的自动挡，或无自定义 breakpoint 的连续推进 | 仍逐 boundary commit/emit，可请求 pause |
| `pause` | 请求自动 drive 在下一个 committed boundary 停住 | 不声称能中断正在进行的模型/工具调用 |
| `inspect` | 查看当前/历史 TraceFrame、captured node-agent context、mounted workspace 和授权 content refs | 纯读，不改 cursor、State、route 或 lease |
| `answer` | 对当前正式 HITL request 提交 existing typed response | request id/cursor 必须匹配；HITL2 不发明 prompt |
| `cancel` | 走现有 lifecycle cancel 语义 | TUI 不把本地退出冒充 durable cancel |
| `attach` | 选择 exact recoverable Bundle 并重建 debug session | 不自动推进；现有 orphan `ContinueRun` 仍是另一操作 |
| `detach` | 在 committed boundary 释放 debug control lease 并离开 session | 不改 cursor/State/lifecycle；node 运行中先 pause，不冒充已 detach |

UI label 可以使用 `continue`，domain 内部必须使用独立 `DebugCommand.drive_until` 或等价闭集值，
避免与现有 `RunIntent.ContinueRun(kind="continue")` 冲突。

### 1.3 Operator 能调什么

v1 允许 operator 调整运行节奏、breakpoint、观察深度，并在正式 HITL 上回答。调试发现问题后，
修改代码、prompt/capability/config，再创建新 Bundle 重跑和比较。

v1 不允许原地改 route、profile、checkpoint 或任意 State value。未来若需要 checkpoint fork，必须
创建新 Bundle，记录 parent bundle/cursor 和 debug lineage；原 Bundle 保持可重放。

### 1.4 TUI 可用性验收

TUI 至少稳定呈现：exact bundle/mode/cursor 状态、按 sequence 排列的 timeline、当前卡片、Node Context、
Files/Inspect pane 和常驻 composer。卡片默认只显示闭集安全事实；captured prompt、runtime MD、developer
guide 和 workspace 内容按 typed ref 主动展开。使用 Textual
Pilot/截图在至少 80x24、120x40、160x50 三种终端尺寸验证无重叠、关键状态不被截断、动态内容
不导致控制区跳位。fixture 全流程不需要凭证或网络。

最终首屏是工作台而不是聊天式 onboarding：提供 New Run、Attach、Replay 三个明确入口，且不自动
选择 latest Bundle。New Run 显式选择 Start Step 或 Start Run；Attach 只列 lifecycle 验证过的 exact
candidate，并区分 busy/read-only 与可 takeover；Replay 永远只读。terminal 后可从同一 TUI 新建
Bundle 或重放旧 Bundle，旧 Bundle 不被改写。

New Run、Attach、Replay 不是三个外部 CLI。C4b 必须交付一个 repo-owned executable launcher
`run/tui-workflow-debugger.sh`；无参数进入 composition + Bundle chooser，`--fixture`/`--embedded` 可
直接选 composition，`--attach <bundle_id>`/`--replay <bundle_id>` 可带入 explicit intent。进入后仍是
同一个 TUI/REPL；operator 可以点选 control，也可以手敲 `/new --step`、`/new --run`、
`/attach <bundle_id>`、`/replay <bundle_id>`。所有入口必须归一成同一个 typed adapter action，不能
各自实现 lifecycle 或 filesystem 逻辑；现有 Make targets 作为可手敲的明确等价入口保留或原子迁移。

composer 的含义随 typed UI state 闭合：setup 时只接收新问题，正式 HITL 时只接收 correlated
answer，全局 slash inspect 保持只读；普通自由文本不能被静默解释为 step/run/cancel/route mutation。
debug mutation 只来自明确按钮、key binding 或 closed command palette action。

## 2. 权威、modules 与 interface

### 2.1 Authority map

| 事实 / 动作 | 唯一 authority | TUI 的权限 |
| --- | --- | --- |
| route、ResearchState、node commit | StateGraph + Bundle lifecycle | 只消费投影 |
| durable boundary | exact Bundle checkpoint | 只显示 projected cursor |
| lifecycle status、pending input、cancel/recovery admission | 现有 lifecycle/domain contracts | 提交 typed command，不推断 |
| intentional debug-boundary ownership | runtime-owned expiring debug control lease | 展示 lease posture；不能自行续租/接管 |
| redacted node/model facts | runtime Journal writers | 只显示 TraceFrame |
| node-agent invocation 的 initial effective prompt/runtime MD/request | shared renderer + runtime bridge inputs；Bundle-private `NodeContextSnapshot` 只作 immutable observation | 只按 opaque context ref 显示 captured bytes；不能用 current source 重建，不冒充内部 provider-call history |
| enforced model/tool/budget/root posture | runtime bridge + `ExecutionPolicy` + trusted virtual-path projection | 只显示闭集安全投影；不能显示 AppConfig、handle、credential 或 host path |
| 当前 runtime resource / `workflow.md` | canonical package resource + node registry；`workflow.md` 是 non-runtime reader | 只按 validated node/capability identity 打开并标 current/non-runtime |
| mounted workspace 的 operator-visible listing/preview | composition-injected `OperatorWorkspaceReader` policy | 只提交 relative path；不能把 path 变成 Bundle/control identity |
| exact Bundle content/artifact inspection | lifecycle-validated Bundle ref + contained content owner | 只打开授权 projection/ref；不能 raw-read State/checkpoint |
| card/layout/selection | Textual adapter | presentation owner，不成为 runtime authority |

### 2.2 `RunTraceProjector` deep module

工作名 `RunTraceProjector` 表示一个 module，不预先锁死类名或文件名。按本仓现有 pattern，
adapter-facing contract models 归 domain，I/O 与投影 implementation 归 runtime；两者都不在 TUI
script。其小 interface：接收 lifecycle 已验证的 Bundle ref 与可选 opaque `TraceReadCursor`，
返回 versioned、分页、redacted `TracePage`。implementation 隐藏 checkpoint serde、Journal
对齐、sequence/gap 检测、field whitelist、live/replay 合并和 observation quality。

`scripts/experiments/tui_trace.py` 只是一枚接受任意路径、直接打开 SQLite 并 compile graph 的
read-only spike。C3 完成时应由正式 module 和 interface tests 取代；脚本随后删除，或降为只调用
正式 interface 的薄诊断 adapter。

### 2.3 `OperatorWorkspaceReader` read module

工作名 `OperatorWorkspaceReader` 是 local operator-only 的 bounded read module，不是 generic product
filesystem browser。composition 在构造时私下注入 trusted mounted root 和 access policy；调用者只给
relative path 或 lifecycle 已验证的 Bundle/content ref。小 interface 返回 typed `WorkspacePage`、
`FilePreview` 或 restricted/unavailable denial，隐藏 host path、symlink resolution、file type/size limit、
redaction 和 Bundle-contained content resolution。

它允许浏览 access policy 明确标成 operator-visible 的挂载内容，包括跨 run 的公开 artifacts；但
path selection 永远不能绑定 Bundle、推断 lifecycle、恢复 State 或授予 drive。Bundle-private State、
checkpoint、secret 和未授权 payload 只能拒绝或走既有 typed projection/content ref。该 local surface
不扩张 Gateway/public tool，也不改变 `research-local-session-workbench` 的 no-generic-browser 边界。

C3 用该 module 取代 `demo_tui.py` 中重复的 `_safe_workspace_path`、`_resolve_inspect_path`、
`_list_directory`、`_cat_file` 和 recon-tool direct reads；Files view、slash commands 和任何只读 chat
tool 都降为同一 interface 的薄 adapter。新增 module 因此退休现有重复权限实现，而不是增加并行 owner。

### 2.4 `NodeContextSnapshot` 与 context inspector

`NodeContextSnapshot` 是 local debugger composition 下，每次已 admission 的
`RuntimeNodeAgentBridge.run_agent` 调用（以下简称 bridge/node-agent invocation）的 versioned、
immutable、Bundle-private observation；它不是 checkpoint、ResearchState、runtime configuration 或第二份
prompt authority。唯一写入点在正式 `render_node_cognitive_control_program()` 结果与
model/tool/policy enforcement 已解析，但 fresh agent 的 `ainvoke` 尚未开始的 seam；因此 snapshot
在首次 provider call 前完成。snapshot 至少关联 exact Bundle、node、attempt、node-agent ordinal
和不会碰撞的 invocation/context identity；多 worker、critic、repair `run_agent` 调用分别写入，
不能按顶层 node 覆盖。

一次 node-agent invocation 内的 fresh agent 可以进行多次 provider model calls 与 tool loops。
snapshot 捕获的是进入 agent 时的 exact initial execution envelope，不是每次 provider request
随 assistant/tool messages 演化后的完整 payload。内部 provider calls 通过 bridge/middleware 的 bounded
model/tool counters、budget stop 和已批准 safe outcome facts 观察；当前 counters 尚未持久投影，
C3 必须补足这条 correlation。v1 不新增完整 raw message-history retention，TUI 必须显式标为
`BOUNDED_OBSERVATION` / `RAW_HISTORY_NOT_RETAINED`。

bridge 不能为此获得 Bundle root 或任意 filesystem writer。composition 只在 local debugger 下给它注入
一个已经绑定 exact `RunBundleRef` 的 write-only `NodeContextRecorderProtocol`（工作名）；bridge 只提交
typed snapshot candidate 与既有降权 identity。recorder/store 独占 containment、relative layout、atomicity、
idempotency、retention 和 opaque ref publication，拒绝 caller root/path/bundle override。该新 surface 退休
“TUI/bridge 事后重 render 或直读 package/workspace”的需求，不成为 lifecycle 或 content-selection owner。

top-level wrapper/worker controller 必须把 runtime-only、不会碰撞的 parent visit/segment correlation 显式
传给 recorder；不得从 node name、phase、path 或 current State 事后推断。context store 在 Bundle 内维护
bounded immutable collection index，把 parent segment -> ordered node-agent context refs 固定下来；
RunTraceProjector 通过同一 committed/failure segment correlation 取得 collection ref。Journal 可以复制
bounded join fact，但不能成为唯一索引，否则 event eviction 会让仍存在的 snapshot 无法 Replay。

snapshot 的字段闭集至少包括：exact rendered initial system policy/human message；base
`runtime_policy.md` 与 selected capability ref/metadata/body 的 captured bytes 和 content hashes；bounded
`NodeExecutionRequest`；safe model/profile label；requested 与最终 enforced tool names/posture；完整
`ExecutionBudget`；safe structured-output schema identity/version；virtual workspace/attempt/read/write roots
与 mount manifest；source artifact refs；capture quality/schema。exact prompt 可能包含研究问题或其他用户输入，因此 snapshot 按 Bundle-private sensitive
content 管理、随 Bundle retention/deletion，不进入默认卡片、日志、Gateway 或 public result。它不得额外
捕获 AppConfig、outer identity、host path、sandbox/model/tool/file handle、runtime credential/secret、
chain-of-thought、任意 raw checkpoint/State 或内部 provider calls 的完整/无限 model/tool message history。

`NodeContextView` 必须逐字段标 provenance/visibility：base policy 与 capability body 是 MODEL_VISIBLE；
capability header metadata、requested/enforced tools、budget 和 roots 是 RUNTIME_ENFORCED；current
`workflow.md` 是 DEVELOPER_ONLY。不得因为它们出现在同一个调试 view 就声称全部进入了 prompt。
它还必须返回固定 coverage/quality projection：initial context = CAPTURED，runtime posture =
ENFORCED，inner activity = BOUNDED/DEGRADED，outcome = OBSERVED/UNAVAILABLE，workspace files = CURRENT。
实现不得用空白、current source 或 initial snapshot 掩盖某层未保留的事实。

snapshot bytes 由 bounded Bundle-contained context store 持有；定义单条/单 Bundle size 与 count limit、
atomic publication、idempotent same-id/same-hash replay 和 same-id/different-hash conflict。
Journal/TraceFrame 只保留 opaque context ref、node-agent invocation identity/count、hash/quality 等
bounded join facts；provider/model/tool call counts 是另一类 bounded activity facts，不能当 context count。
debug Bundle 可用期间不得静默 eviction/overwrite 已捕获 context；下一条 snapshot 超 size/count capacity 时
在首次 provider call 前返回 typed `context_capacity_exhausted`（最终 reason 可在 C3 spec 定名），
保留旧 snapshots。
local fixture/embedded debugger 必须启用
required capture：fixture 的 node-agent-context case 走正式 writer/reader contract，embedded 的实际
bridge/node-agent invocation 在 `agent.ainvoke`/首次 provider call 前捕获；snapshot 写入或 correlation
失败时，在首次 provider call 前 fail closed，避免产生一个事后无法解释的 debug
node-agent invocation。非-debug composition 默认不新增 raw-context retention；
Gateway/public tool 不获得读取 surface。

context inspector 先接收 lifecycle 已验证的 Bundle ref + opaque context-collection ref/cursor，返回分页
`NodeContextPage` 与 bounded node-agent invocation summaries；再以其中 exact context ref 返回 typed
`NodeContextView`。另以 node registry/validated capability ref 返回 curated `NodeSourceView`。后者可以展示
current `runtime_policy.md`、exact capability resource、node `workflow.md` 和源码导航，但 package source
仍不挂入 research sandbox，且不存在 caller-selected source path。inspector 比较 captured/current hashes，
只返回 MATCH/DRIFT/CURRENT_SOURCE_UNAVAILABLE；DRIFT 默认仍读 captured bytes。legacy Bundle 无 snapshot
时返回 CONTEXT_NOT_CAPTURED，绝不使用 current source 冒充历史输入。

Node Context 的 Inner Activity/Outcome/Handoff 由 inspector 只读关联 TraceFrame/Journal 与既有
authorized content refs，展示内部 provider/model/tool counts 与安全 facts、final structured
candidate/ref、validation/repair feedback、deterministic
admission owner/result、changed field names 和 route；它不把这些 outcome 反写 snapshot，也不发明未被
runtime 保留的 raw provider response/message history。后者必须显示 NOT_RETAINED，不能从
initial snapshot、candidate 或 State 逆推。

workspace reader 展示 `CURRENT` 文件；context snapshot 展示
`CAPTURED_AT_NODE_AGENT_INVOCATION`。artifact ref 有
immutable hash 时可验证两者；没有时只并列显示，不承诺整棵 workspace 的 point-in-time snapshot。
这一区分既满足研发现场观察，也避免为了“完整上下文”复制整个 mount 或扩大任意文件权限。

### 2.5 `DebugRunDriver` deep module

工作名 `DebugRunDriver` 同样不锁死最终类名；contract models 归 domain，graph/lifecycle driving
implementation 归 runtime。它可以在 `BundleGraphExecutor` 背后或相邻 module 实现，但必须提供
独立于现有 `ContinueRun` 的 debug interface。外部 interface 保持为三个小动作：

```text
open_start(DebugStartRequest) -> DebugSessionSnapshot
open_attach(DebugAttachRequest) -> DebugSessionSnapshot
execute(DebugCommand) -> DebugSessionUpdate
```

`DebugStartRequest` 在 Bundle 出现前携带 adapter 在 WORKBENCH -> BINDING 转换时创建的稳定
`start_request_id`，以及 composition、validated question 和 initial Step/Run mode 的 immutable
fingerprint。same-id/same-fingerprint 的并发或重放返回同一 exact handle；same-id/different-fingerprint
返回 typed conflict。若相同 scope 已有不同 start request 的 active Bundle，则复用现有 lifecycle
admission 返回 typed active-bundle denial，不创建第二个 Bundle。实现应复用或扩展现有
`start_message_id + start_request_digest + scope_exclusion` 语义，不再造平行 Bundle authority。

adapter 在一次 BINDING 期间复用同一 `start_request_id`，重复按钮/命令只 coalesce 或重放该请求；
拿到 handle 后，再用稳定 `command_id + expected_cursor` 提交首次 `advance_one` 或 `drive_until`。
因此“创建一个 Bundle”和“最多推进一次 bootstrap”是两层幂等，任何一层都不能借另一层的 key
冒充已经闭合。其余 mutation command 必须携带 exact bundle、`expected_cursor` 和 `command_id`。implementation 隐藏
graph compile/config、per-boundary `execution_exclusion`、checkpoint reopen、interrupt handling、
stop policy、duplicate detection 和 stale-cursor denial。

它不成为第二 lifecycle owner，也不扩写 `BundleGraphExecutor.continue_run`。step/run 使用同一
recipe、compile path 和 durable saver/thread；进程内可复用 compiled object，attach/restart 可从同一
recipe 重新 compile。每次 boundary commit 后释放本次 `execution_exclusion`；debug session 仍按下述
规则持有 control lease，不维护 step 专用 topology/recipe。

`interrupt_after` 产生的边界没有 human pending input；现有 lifecycle 会把它看作 active/no-pending，
即 recoverable orphan。C4a 因此需要一个 Bundle-local、runtime-owned、可过期的 debug control lease：
debug session 在 pause 间持有/heartbeat 该轻量控制租约，每次执行另取 `execution_exclusion`。它不把
Bundle 伪装成 suspended，不写 ResearchState；正常 detach 释放，进程死亡后过期并允许 exact attach。
现有 natural resume 和第二 debugger 必须尊重 live control lease，observer inspect 仍可用。

control lease 与现有短期 `execution_exclusion` 是两个语义不同的 fact；可以复用 coordinator 的实现
模式，但不能把同一执行锁跨 operator pause 长期持有。takeover 必须同时满足 control lease 已 stale、
不存在 live execution exclusion，并以 exact generation/cursor 做 CAS。一次 node invocation 的
execution exclusion/fence 必须持续到 checkpoint commit 或明确放弃，并能覆盖长模型调用；TTL 到期
本身绝不能授权第二 writer。若 in-flight 状态仍有歧义，只允许 read-only/uncertain，待恢复规则收敛。

### 2.6 `BoundaryCursor`、`TraceFrame` 与 active visit

`BoundaryCursor` 至少关联：schema version、bundle id、checkpoint identity/sequence、generation、
committed visit sequence、next logical node(s) 和 lifecycle posture。它由 checkpoint/lifecycle 投影，
不是第二份持久化 State。

每个 committed/suspended boundary 或 non-committed failure segment 投影为一张 immutable
`TraceFrame`。有 commit 的 frame identity 来自 checkpoint identity；没有 checkpoint 的 failure
使用失败 event sequence。`visit_id` 只作关联，不能当唯一键；HITL suspend/resume 可对同一 visit id
产生多张顺序卡。

`TracePage` 另带至多一个 `ActiveVisitProjection`，状态闭集为 running、committing、uncertain。
started 且无 outcome 是 running；node completed/suspended fact 已出现但对应 checkpoint 尚不可见时是
committing；进程/lease 消失且 commit 仍不确定时是 uncertain。只有 checkpoint commit 或确定的
non-committed failure 才产生 frame。active projection 可携带已 atomic-published 的 opaque context-collection
ref/count，使 node-agent 内部 provider 长调用期间也能 Inspect exact initial inputs；TUI 不自行
配对 snapshot、Journal 和 checkpoint。

增量读取使用 versioned opaque `TraceReadCursor`，内部同时覆盖 checkpoint position/identity 与
Journal high watermark；它与 mutation 用的 `BoundaryCursor` 是两个不同 contract。单独一个
`after_sequence` 不足以发现 Journal 写失败但 checkpoint 已提交的 boundary。

`pause_requested` 属于 C4a `DebugSessionSnapshot`，不是 Journal/TraceFrame 事实；TUI 可并列渲染两个
typed projections，但不得把 session control state 写回 trace。

边界存在、顺序、route/next 的 authority 是 checkpoint；Journal 提供 duration、attempt、failure 和
内层 causal facts。现有 Journal 最多保留 256 条，并会在容量压力下淘汰普通事件。C3 必须优先保留
finalized node facts，并在丢失后仍从 checkpoint 显示边界，但把 duration/inner detail 标为 unavailable
且 quality=degraded。L3/L4 内层叙述是 bounded observation，不承诺无限历史回放。

TraceFrame v1 自动展示的字段闭集：

- `bundle_id`, `frame_sequence`, `visit_id`, `generation`, `node`, `outcome`；
- `route`, `next_nodes`, `changed_field_names`；
- work/attempt/model/tool counts 与已存在的安全 budget facts；
- `node_agent_context_count`、opaque `node_context_collection_ref` 和 `context_quality`，只作分页
  context inspector 入口；它与 `model_call_count`/`tool_call_count` 分开；
- wrapper 显式测得的 `duration_ms`；
- `failure_category`, terminal disposition, pending-input projection；
- `observation_quality = complete | degraded | unavailable` 及 bounded gap reason。

禁止自动包含任意 State value、泛化 `input_summary/output_delta`、raw model/tool content 或 host path。
node-specific whitelist/content refs 必须复用现有访问和 redaction contract。capability id、prompt、request
和 policy attribution 只可由 `NodeExecutionRequest.capability_ref` 所在正式 renderer/bridge seam 写入
`NodeContextSnapshot`，不能从 node/phase 或当前源码推断。TraceFrame 不内嵌 snapshot bytes/refs list；
一张 frame 通过 bounded collection ref 分页关联零到多个 node-agent invocation context，
deterministic node 的零必须保真。一份 context 可关联多次内部 provider model calls，不因
model-call count 增加而伪造多份 initial snapshot。

### 2.7 Adapter capability matrix

| Adapter / mode | Trace replay | Exact initial node-agent context | Debug driving |
| --- | --- | --- | --- |
| fixture local | 是 | 是，required capture | 是，C4a 首要验收面 |
| embedded-smoke local | 是 | 是，fixture 全绿后接线 | 是，fixture 全绿后接线 |
| Gateway/public tool | 有 exact contract 时才可 | 否；不新增 raw-context surface | 否；保持 observer-only |

Gateway 远程 step 需要另行批准认证、授权、租约、断线和 public versioning，不得隐藏在 C4a/C4b 中。

## 3. 并发、失败与恢复不变量

1. **Exact correlation**：一个 session 从第一条 admission/attach fact 起绑定一个 Bundle；缺 id 时
   不读取其他 Bundle，不显示伪 live trace。
2. **Control ownership**：intentional boundary pause 有 live debug control lease；第二 debugger 或
   natural `ContinueRun` 得到 typed busy/status，而不是接管。observer 不被控制租约挡住。只有 control
   lease 已 stale 且不存在 live execution exclusion 时才可广告 takeover。
3. **At-most-once boundary advance**：`expected_cursor + command_id + execution_exclusion` 共同防止
   双击、重放和双进程顺序多走一步；旧 cursor 返回 typed stale denial。execution fence 覆盖完整
   invocation/commit，长 node 不以 TTL 到期作为并发接管许可。
4. **Boundary recovery**：进程在 boundary 后死亡，control lease 过期且确认没有 live execution
   exclusion 后，attach 才可从 durable checkpoint CAS 重建同一 cursor，且不自动推进。
5. **Mid-node uncertainty**：只有 started、没有 matching outcome 时显示 interrupted/uncertain；恢复
   依现有 lifecycle/work-unit 幂等语义收敛，不伪造 completed。
6. **Observation degradation**：Journal 写失败或 sequence gap 不改变 graph authority，但 TraceFrame
   必须标 degraded；projector 不从 checkpoint 猜一个成功事件填洞。
7. **Pause honesty**：模型/工具调用进行中只记录 pause requested；下一个 committed boundary 才是
   paused。Ctrl-C/本地退出不冒充 durable cancel。
8. **Read failure**：checkpoint/Bundle invalid 或 unavailable 时 inspect/drive fail closed，不执行 graph。
9. **Breakpoint ownership**：v1 breakpoint 是 debug session 配置，不写 ResearchState。进程死亡后可
   丢失 breakpoint 设置，但 Bundle/cursor 必须可 attach；operator 重新设置 breakpoint。
10. **Context provenance**：每次已 admission 的 debug bridge/node-agent invocation 必须在
    `agent.ainvoke`/首次 provider call 前 durable-capture exact initial context；写入或 correlation
    失败则不调用 provider。Replay 只认 captured snapshot，current source 只作 MATCH/DRIFT
    对照；内部 provider raw history 未保留就显示 NOT_RETAINED；legacy absence 显式 unavailable。
11. **Workspace time axis**：mount manifest/roots 是 invocation-time projection；Files tree 是 current
    content。没有 immutable ref/hash 时不声称 workspace bytes 是 invocation-time snapshot。

对应 falsifiable guards：双 Bundle 并发不得串帧；同 command id 重放只 commit 一次；两个 driver
竞争时一个成功、另一个 stale/locked；node 执行时间跨过 control TTL 也不得出现第二 writer；人为
删一条 Journal event 必须出现 degraded；植入任意 checkpoint value 不得自动出现在 TraceFrame。
让 context-store 写入失败必须证明 provider spy 零调用；一次 node-agent invocation 内安排多次
provider calls，必须证明只有一份 initial snapshot、model/tool counts 独立增长且 raw history 标
NOT_RETAINED；修改 capability resource 后旧 snapshot bytes 不变且 source status=DRIFT；在 current
workspace 替换文件不得改变 captured ref/hash。

## 4. OpenSpec change 阶梯

所有 accepted contract、代码、persisted schema 或 cross-module interface 变更都走独立 OpenSpec
change。下面的表列出**当前尚未完成的链**；创建 planning draft 不等于 apply 或完成。C1/C2 已经
完成并归档，所以不会再次出现在待办顺序中：
**propose -> polish/apply-readiness -> TDD apply -> `UV_OFFLINE=1 make verify` -> sync/archive**。
propose 时声明 requirement impact；确需新增 requirement 时才登记新 ID，并核对当前没有会修改同一
authority 的 overlapping active change。

| 顺序 | change slug | 唯一载荷 | 当前状态 | 前置 |
| --- | --- | --- | --- | --- |
| Cpre | `reconcile-hitl2-autonomous-contracts` | 原子收敛 autonomous HITL2 的主 specs、registry、walkthrough 与受影响 fixtures/tests；零 runtime/topology 变更 | 已归档（2026-09-02）；五 specs/registry/walkthrough/fixtures 原子同步，plan/closeout 门全绿 | 已完成 |
| C0 | `repair-run-observation-truth` | suspended Journal truth + fail-closed exact live correlation | 已归档（2026-09-02）；RunEvent v3 值集扩展、投影不再改标、live 旁听 exact-bind，红/绿与门禁证据在归档 evidence.md | Cpre 归档 |
| C3 | `add-local-workflow-debug-observation` | runtime TraceFrame/projector + required node-agent-context capture/inspect + bounded workspace reader + replay/live presentation | 已归档（2026-09-02）；新主 spec `local-workflow-debug-observation`（LDO-001..008）；trace/context/workspace fixtures 全绿；spike 退役 | C0 归档 |
| C4a | `add-local-workflow-debug-driving` | DebugRunDriver + control lease + 全部 headless drive/recovery contracts | 已归档（2026-09-02）；新主 spec `local-workflow-debug-driving`（LDD-001..005）；driver 矩阵 7/7 + lease 冒烟 3/3 + 全链路到 terminal 证明 | C3 归档 |
| C4b | `connect-tui-workflow-debugger` | Textual command adapter + executable launcher + fixture/embedded 接线；零新增 runtime 语义 | **apply 进行中**（propose 完成；launcher/入口测试落地；Node Context pane 待接线） | C4a 归档 |
| 终线 | 无 change | 一次固定问题的真实模型体验/一致性验收 | 未开始 | C4b 归档 + 网络可用 |

编号保留 C3 与 C4a/C4b 中的“4”是为了延续 020 战役账本：历史 C1
`close-provider-timeout-budget-handback` 与 C2
`add-suspended-run-recovery` 已归档。C0 是本次审阅插入的前置修复，不表示回改历史 C2；它通过
新的 corrective change 前进，并保留 C2 的 orphan recovery 行为。C4a/C4b 是同一 driving 阶段的
headless authority 与 presentation adapter 两个独立 cut，不增加新的轴编号。

### 4.1 Cpre 当前状态、范围与出口

Cpre 已于 2026-09-02 完成 apply、delta sync 与 archive
（`openspec/changes/archive/2026-09-02-reconcile-hitl2-autonomous-contracts/`）。
其出口条件全部满足并留有证据（见该归档 `evidence.md`）：五份 main specs、`REN-001`/`REN-006`
registry 摘要、lifecycle walkthrough §4 与受影响 fixtures/tests 原子同步；HITL1 typed-choice
与 autonomous HITL2 的 deterministic 证据经真实测试面跑通（最低 seam 35 passed、集成 86
passed、契约 36 passed）；diff 无 runtime/public API/checkpoint schema/topology/dependency/
`deerflow/` 变更；`UV_OFFLINE=1 make verify`、plan/closeout 门、strict validation 全绿。
顺带修复的干净树 closeout 门回归登记为 BUG-067（零契约面变更，不属于 Cpre 载荷）。

Cpre 的唯一目标是让所有 current authority 一致表达：HITL1 是当前唯一 human pending-input
producer；real HITL2 校验 predecessor 后自主产生内部 graph route，不创建第二个 human prompt、
Answer/Resume 或 retained HITL2 session。它必须保留仍有效的 HITL2 internal routes、rerun/readiness
control facts、topology 和宽泛 decoder compatibility，不把“删除错误的人机投影”扩大为 runtime rewrite。

Cpre 归档放行 C0：propose C0 前须重新运行 `openspec list --json` 核对无 overlapping active
change，并按 §10 重验 dated evidence（`RunEvent` suspended 拒绝须先用当前代码重现并记录到
change evidence）。Cpre 的详细 apply checklist 已随归档保留，scope、顺序和放行条件仍由本 plan
约束。

每个 change 在 `openspec propose` 前必须建立一张可审阅的 source mapping，并放入 proposal/design/tasks
之一（具体载体由当期 OpenSpec 模板决定）：

- 每个 proposal task 映射到本文件中同阶段的 exact task、acceptance 或 no-go；Cpre 映射本节的
  authority scope/gate；不得从 campaign
  历史直接导入 task。
- C3/C4a/C4b 逐项映射 target UX 的相关主旅程、负路径、traceability row 和验收剧本；C0 也要
  映射其中依赖 observation truth/exact identity 的条目。
- 对 grounding review 中引用的 dated code/spec 事实重新核验；若已漂移，在本文件 §L 记录新证据，
  不把冻结审阅当成永真前提。
- proposal 若发现 plan task 与 target UX 无法双向对应，或需要新增 owner、persisted surface、权限、
  graph 变体、远端控制能力，立即停止 propose，先同步修订本文件与 target UX。
- 已归档 change 与后来发现冲突时，保留归档不可变，通过本文件登记 corrective change；不得静默
  改写 archive、target UX 或 UI 文案来掩盖 contract 漂移。

统一门规则：

- 每个 change 只有“验收全绿并 archive”或“停止后续阶段并回本 plan 收缩范围”两种出口。
- C0/C3/C4a 的 correctness 均由无凭证 fixture/headless tests 证明；C4b 再证明 adapter 接线；真实模型只验证体验和接线，
  不能替代 deterministic contract tests。
- 实验推翻计划时，只修订尚未 propose/apply 的阶段；已归档 change 通过新的 corrective change
  前进，不改历史归档。
- Cpre 未归档，禁止开始 C0；C0 未通过，禁止开始 C3；C3 无法 exact-bind 或无法显式报告 degraded，禁止开始 C4a；C4a
  未归档，禁止开始 C4b。
- 若 C4a 只能靠第二张 graph、TUI 私有 State mutation 或 public tool 扩权实现，立即 no-go。

## 5. C0 - `repair-run-observation-truth` [x]

目标：在设计卡片之前先修复 observation 事实，并使无法关联的 live narration 宁可缺失也不串包。

### 5.1 Contract tasks

- [x] 在 propose 前用当前代码重现 `RunEvent(outcome="suspended")` 拒绝，并记录到 change evidence。
- [x] 扩展 persisted RunEvent outcome 闭集，使 `suspended` 在主 spec 要求的 schema/version 策略下
  可读写；枚举所有 readers/writers 并同步切换。新代码须读取旧 events 且无需数据迁移；旧代码
  会拒绝新 suspended event，proposal 必须声明本地 coordinated cutover 和 rollback 限制。
- [x] `_record_node_event` 的所有 observation paths 都保留 suspended，不映成 `failed`；unexpected
  exception 继续是 `failed + internal.unexpected` 并传播。
- [x] 建立 wrapper -> real Bundle recorder/store -> serialized `events.jsonl` -> reader 集成测试；
  fake recorder test 只保留为局部行为测试，不再作为 REJ-011 唯一证据。
- [x] 移除 `_latest_active_bundle` 对当前 dispatch live narration 的因果角色。exact id 未知时显示
  unbound/static working，不读最近 Bundle；attach candidate 排序可保留，但选择后必须 exact-bind。
- [x] 修正与本变更直接相关的 REJ-011 主 spec/test/doc 漂移；不把历史 walkthrough 提升为
  authority，也不把无关文档清理混入 C0。

### 5.2 Falsifiable acceptance

- [x] 真实 store 中存在 `started -> suspended`，且没有 `internal.unexpected`；reader 返回 suspended。
- [x] 真 unexpected exception 仍持久化 failed/internal.unexpected，graph 行为不因 observation 改变。
- [x] 同 workspace 放置两个 active/suspended Bundle，TUI 未拿 exact id 时不显示任一方事件；绑定
  A 后永不出现 B 的 sequence/phase。
- [x] 植入 observation persistence failure 后，graph/lifecycle 继续按原 authority 工作，诊断明确
  表示 degraded/unavailable，而不是错误 completed。
- [x] 相关 targeted tests、integration tests、`make verify` 全绿；change 同步主 spec 并归档。

### 5.3 No-go

真实 store 仍丢 suspended、TUI 仍需要 latest 才能显示“实时进度”，或修复要求改变 graph route，
则停止 C3。允许的收缩结果是暂时只显示静态 working 和 exact historical replay。

## 6. C3 - `add-local-workflow-debug-observation` [x]

目标：建立 runtime-owned、versioned、redacted、可分页且 live/replay 同构的 trace module，required
debug node-agent invocation-context capture/inspect，以及 local operator-only 的 bounded workspace read module；
本阶段不启动、不推进、不恢复 graph。

### 6.1 Contract tasks

- [x] 在 delta spec 定义 `TraceFrame`/`TracePage`/`ActiveVisitProjection` 的字段闭集、version、
  ordering、opaque `TraceReadCursor`、pagination/upsert、gap/degraded semantics、redaction 和未知
  版本行为；started 或 pre-checkpoint completed 都不能冒充 committed frame。
- [x] 在 node wrapper 对每次实际 invocation segment 使用 monotonic clock，随
  completed/suspended/failed fact 写入 bounded `duration_ms`；HITL resume 的多段 active duration
  分别记录，human wait 不在任一段内。checkpoint 间隔只可另名展示，不冒充 node duration。
- [x] 审核现有 `MAX_EVENT_RECORDS=256` retention：finalized node fact 的优先级高于普通
  start/model-tool success，admission/terminal/failure 等现有 anchors 继续受保护；容量仍不足时
  manifest/TracePage 必须披露 dropped interval/count。
- [x] 实现 `RunTraceProjector`：只接受 verified Bundle ref；从 checkpoint 投影 boundary cursor，
  从 Journal 读取 causal facts；检测重复、缺口、out-of-order、corrupt 和 unavailable。
- [x] 同一 projector 支持 historical replay 与 caller-supplied verified Bundle 的 exact live
  incremental read；live 断线后用 opaque TraceReadCursor 重接，输出与完整 replay 一致。C3
  不为获得 handle 而启动 graph；当前 TUI 若尚无 early handle，只展示 replay/static working。
- [x] 卡片只显示 §2.6 闭集；changed fields 只给名称。内容通过 node-specific whitelist 或现有
  authorized refs inspect，不输出 raw State/model/tool payload。
- [x] 在 delta spec 定义 §2.4 versioned `NodeContextSnapshot`、opaque context/collection refs、分页
  `NodeContextPage`/cursor、typed `NodeContextView`/`NodeSourceView`、capture quality、retention、unknown-version
  和 legacy-absence 行为；
  一张 TraceFrame 可关联零到多个 node-agent context，不能假设每个顶层 node 只有一次
  `run_agent` 调用，也不能把一次 `run_agent` 内的多次 provider calls 当成多份 context。
- [x] 扩展 shared capability loader/renderer 的 typed result，使同一次正式 package-resource read 返回
  base/capability layer identity、captured bytes/metadata/hash 和 rendered initial messages；recorder 直接消费
  该 result。不得为 snapshot 再读一次 resource，也不得让 TUI/catalog 复制组合模板。
- [x] 在正式 renderer/`RuntimeNodeAgentBridge` seam，model/tool/policy admission 后、`agent.ainvoke`/首次
  provider call 前为 fixture/embedded debugger 写入 exact Bundle-private snapshot：captured
  base/capability MD bytes+hash、initial system/human messages、bounded
  request、safe model/profile label、requested/enforced tools、budget、virtual mount/read/write/attempt roots、
  artifact refs 和 exact node-agent invocation correlation。atomic snapshot + active-trace join 都完成后才可
  进入 agent；写入/correlation/join 失败必须 provider 零调用。
- [x] recorder 是 composition-injected、exact-Bundle-bound 的 write-only protocol；bridge/TUI 不能接收
  Bundle root、从 bundle id 拼 path 或拥有 generic content writer。store 独占 bounded layout、containment、
  atomic publication、same-id/hash idempotency、conflict 和 retention/deletion。
- [x] wrapper/worker controller 显式提供 runtime-only parent visit/segment correlation；context store 维护
  bounded immutable segment->ordered-node-agent-invocations collection index，projector 据此给 active/frame collection
  ref。禁止依赖 node/phase/path 推断或只靠可 eviction Journal 关联。
- [x] snapshot store 不写 checkpoint/ResearchState，不接受 caller root/path，不记录 AppConfig、outer
  identity、host path、handle、credential/secret、chain-of-thought 或内部 provider calls 的完整/无限
  raw messages。Journal/TraceFrame 只写 opaque ref/node-agent-context count/hash/quality；model/tool call
  counts 保持独立。production/Gateway composition 默认不启用 raw-context retention。
- [x] 将 `BudgetMiddleware.model_calls` 与 `ToolPolicyMiddleware.tool_calls` 作为 bounded aggregate activity
  facts 关联到 exact node-agent context，至少在 completed/failed outcome 持久最终计数、budget stop
  和已批准的 safe tool/outcome facts。mid-call crash 或 observation failure 时显示 DEGRADED/UNAVAILABLE，
  不从 budget limit、result 或 initial snapshot 猜测实际调用数；不持久 raw request/response/messages。
- [x] context inspector 只接受 verified Bundle + opaque context collection/ref/cursor，分页返回 bounded
  summaries/view；curated source reader 只接受 node registry identity/validated capability ref，展示 current
  runtime resources 与 `workflow.md` 导航并返回
  MATCH/DRIFT/CURRENT_SOURCE_UNAVAILABLE。`workflow.md` 始终 non-runtime；legacy 无 snapshot 不重建。
- [x] 定义并实现 §2.3 `OperatorWorkspaceReader`：trusted root/policy 只由 composition 注入；list/preview
  只接收 relative path 或 verified Bundle/content ref，返回 bounded typed page/preview/denial，绝不返回
  absolute host path，也不把 path 解释为 lifecycle identity。
- [x] workspace projection 枚举 composition 注入的全部 virtual mounts、alias/readiness、effective
  read/write/attempt roots；Files 标 CURRENT，snapshot 标 CAPTURED_AT_NODE_AGENT_INVOCATION。
  有 immutable ref/hash
  时校验，没有时不宣称完整 filesystem snapshot。每个 root/entry 区分 MODEL_READ、MODEL_WRITE、
  OPERATOR_ONLY、RESTRICTED；TUI 可见不等于模型可见。package source 不挂入 research sandbox。
- [ ] 用该 reader 取代 TUI/recon 中所有 direct path resolution/list/cat helpers；树视图、slash command  ← 剩余：TUI direct helpers 迁移随 C4b workbench 接线落地
  和可保留的只读 chat tool 只做 adapter。同步列出 operator-visible path policy、private/secret deny
  policy、text/binary/size/truncation behavior，且不扩大 standalone workbench 或 Gateway surface。
- [x] 把 `scripts/experiments/tui_trace.py` 替换为正式 interface tests；脚本删除，或改为不认识
  SQLite/recipe/serde 的薄 adapter。
- [ ] Textual trace pane 只消费 TracePage，Context pane 只消费 NodeContextPage/NodeContextView/NodeSourceView，  ← 剩余：pane 接线归 C4b（C4b tasks 已列）
  Files pane 只消费 WorkspacePage/FilePreview；adapter 不 render/rebuild prompt、不 load package resource、不
  compile graph、不打开 `graph.sqlite`、不 direct-read path、不扫描 latest。将 trace/context/files
  rendering/transport 从 1817 行 `demo_tui.py` 中拆出，避免继续堆 runtime semantics。
- [ ] 用 fixture 完成 E5：卡片密度、timeline/inspect/composer 和三种终端尺寸调试；结论写 §L。  ← 剩余：E5 三尺寸调参随 C4b Pilot 旅程执行

### 6.2 Required fixtures and acceptance

- [x] replay：fixture completed、real-sample completed、BUG-062 blocked、HITL suspended。
- [x] truth：Journal complete 时，同一 Bundle 的 live incremental 最终 frames 与 full replay 等价；
  active projection 只在 commit/failure 确定后消失。一次多轮 HITL visit 保留每个 suspended segment
  和最后 completed segment，不因 visit id 相同而覆盖。Journal incomplete 时只保证 checkpoint
  boundary identity/order，并明确缺失的 duration/inner facts。
- [x] commit truth：注入“node body 返回 completed，随后 wrapper/gate 失败且无 checkpoint”；只生成
  failed frame，可保留 node-body-completed 子事实，但不得生成 completed boundary frame。
- [x] isolation：两个 Bundle 交错写入不串 frame；TraceReadCursor 只消费指定 Bundle。
- [x] degradation：缺 event、坏 JSON、checkpoint unreadable、started-without-outcome 都得到显式
  quality/uncertain 结果，不推断完成。
- [x] capacity：用超过 256 条的 fixture 触发 eviction；admission/terminal/failure/finalized-node
  retention 符合 spec，dropped interval 可见，旧卡片不被冒充为完整 causal trace。
- [x] privacy：向 checkpoint 植入 sentinel question/profile/evidence/message/path，默认 TraceFrame
  和默认卡片均不出现 sentinel；显式 local debug context 只从 exact snapshot ref 打开，并证明 host
  path/AppConfig/identity/runtime-credential/chain-of-thought sentinel 不能进入 snapshot 或 UI。
- [x] context fidelity：用 renderer/bridge/provider spy 证明 snapshot 在 `agent.ainvoke`/首次 provider
  call 前已 durable commit，initial system/human bytes、request、capability、tools/budget/roots typed-value
  等价；initial/repair/critic/worker 多次 bridge/node-agent invocation 各有唯一 ref，live 与 replay 返回
  相同 snapshot bytes/order。同一 node-agent invocation 内多次 provider calls 仍只有一份 initial
  snapshot，model/tool counts 独立增长，完整 raw histories 显示 NOT_RETAINED。触发 Journal eviction 后，
  durable collection index 仍能把所有 retained contexts 关联回 exact segment；HITL 多 segment 不串联。
- [x] context negative：capture/store/correlation 失败时 provider 零调用；deterministic node
  `node_agent_context_count=0`；capability/tool/model pre-capture admission failure 显示 NODE_AGENT_NOT_STARTED
  而不伪造 snapshot；
  legacy Bundle 返回 CONTEXT_NOT_CAPTURED；未知 schema/corrupt/missing ref fail closed，不从 node/phase/current
  source 猜 capability 或 prompt。单条/Bundle capacity 超限在首次 provider call 前 typed fail，
  旧 contexts 不 eviction/
  overwrite，same-id/different-hash conflict 不污染 index。
- [x] source drift：capture 后改变 fixture capability/runtime resource，旧 snapshot bytes/hash 不变，current
  source 标 DRIFT；`workflow.md` 只出现在 NOT MODEL VISIBLE developer view。任意 source path/`..`/absolute
  path 被拒，且 research sandbox mount manifest 不包含 package source。
- [x] filesystem：同一 trusted mount 下，Files view、`/ls`、`/cat` 对 operator-visible 内容返回等价
  relative results；absolute/`..`/symlink escape、blocked private State/checkpoint/secret、foreign
  trusted scope 均 typed deny。浏览另一 run 的 policy-public artifact 不绑定该 Bundle，也不改变当前
  trace/cursor/control。替换 current workspace 文件不改变 captured immutable ref/hash；无 hash 时 UI
  明确只显示 current content。
- [x] timing：模拟长时间 operator pause，node `duration_ms` 不包含 pause；boundary timestamps
  可以保留但标签不同。
- [x] UI：80x24、120x40、160x50 无重叠/关键状态截断；fixture composer 与 inspect 可用。
- [x] module interface tests、TUI Pilot tests、`make verify` 全绿；spec 同步并归档。（Pilot 三尺寸随 C4b 收尾；interface tests 与 make verify 已绿）

### 6.3 Required node-context closure

capability attribution、initial effective prompt、enforced policy 和 mount roots 已因 debugger 的核心研发体验
升级为 C3 必需项，不再延后为 optional `add-model-invocation-trace-attribution`。仍不得把
raw context 塞进 node frame 或 Journal；C3 必须通过 opaque ref 连接 Bundle-private snapshot。
若无法在 `agent.ainvoke`/首次 provider call 前可靠捕获并在 replay 中保持 exact bytes，
C3 不得归档，C4a/C4b 不开始。这一 gate 只对 node-agent 的 initial execution envelope 作
exact 承诺；内部 provider raw message histories 必须明示 NOT_RETAINED，不可借“完整上下文”扩张。
未来若要逐 provider-call payload replay，必须另立 change，重新闭合 capture seam、bounded schema、
sensitive-content access、retention/deletion、capacity failure 和 unknown-version cutover；不能当作当前
`NodeContextSnapshot` 的字段扩展偷渡。

### 6.4 No-go / 收缩

若安全且有用的叙述流无法收敛，保留 headless projector 与历史 replay，撤回自动内容卡片；不要
用 raw checkpoint dump 换取“可见性”。若 workspace browsing 只能靠 TUI direct path access、调用者
传 root、raw State/checkpoint 或扩张 generic product/Gateway browser，则 Files 目标未成立，C3 不得
以旧脚本 helper 假绿。若 exact initial node-agent context 只能事后重新 render、扫描当前
runtime MD、持久化 secret/host authority，或把 package source 挂进 research sandbox，则 Node Context
目标未成立。若 UI 把 initial snapshot 冒充为内部 provider calls 的完整消息历史，也不得
归档。C3 未归档，C4a 不开始。

## 7. C4a/C4b - Local workflow debug driving [ ]

目标：先在 C4a 建立独立、可 headless 验收的 local debug drive interface，再由 C4b 把 Textual
接成纯 adapter。现有 shared `RunIntent`、`ContinueRun`、route/profile/HITL admission 保持原义。

### 7.1 C4a `add-local-workflow-debug-driving` tasks

- [x] 定义 `DebugSessionSnapshot`、`BoundaryCursor`、closed `DebugCommand`、typed update/denial 和
  stop policy；surface 明确 local-only，不进入 reflected public tool。
- [x] `open(start)` 在任何 live narration 前返回 exact Bundle handle；`open(attach)` 只重建 cursor，
  不等同现有 natural resume，也不自动推进。
- [x] 固定 start 组合语义：Start Step = `open(start)` 后恰好一次 `advance_one`，首张 committed frame
  是 bootstrap；Start Run = `open(start)` 后走同一 `drive_until`。两者必须先向 adapter 交付 exact
  handle，再出现首条 provisional row；重试不得重复创建 Bundle 或重复提交 bootstrap。
- [x] 定义/实现独立的 expiring debug control lease：open 原子取得，live session heartbeat，
  detach/terminal/cancel 释放。明确 owner、generation、TTL、heartbeat、stale detection 和 fencing；
  lease 是 private control fact，不写 ResearchState，也不复用 suspended/pending-input posture。
- [x] natural `ContinueRun`、第二 debugger 和其他 mutation path 在 live debug lease 存在时 typed
  deny/busy；status/inspect observer 仍可读。takeover 只在 control lease stale 且无 live
  `execution_exclusion` 时开放，并必须 CAS exact lease generation/cursor；歧义状态保持 read-only。
- [x] attach candidate projection 区分 live-owned debug pause 与 stale/dead owner：前者只允许
  status/inspect，后者才广告 takeover/attach；候选列表排序不授予控制权。
- [x] 实现 `advance_one`：同一 recipe/compile path、per-invocation `interrupt_after`、同一 durable
  saver/thread；每步获取并释放 `execution_exclusion`，提交最多一个当前 topology 下的 logical node。
  execution fence 必须覆盖 node body、gate 和 checkpoint commit，长调用期间保持 live/renewed；
  restart 可重新 compile，但不得存在 step 专用 topology/recipe。
- [x] 实现 `drive_until`：到 breakpoint/HITL/failure/terminal/pause 停止；`run` 是 start 时的自动
  stop policy，不复制一套执行逻辑。
- [x] pause 仅在下一个 committed boundary 生效；正在执行的模型/工具调用显示 running +
  pause-requested，不宣称已中断。
- [x] answer 复用 existing typed human response/request correlation；HITL1 可多轮，HITL2 保持
  autonomous continuation。
- [x] detach 是 closed local control action：只在 committed boundary 释放 control lease，不改
  checkpoint cursor、ResearchState 或 lifecycle status；in-flight detach 返回 typed busy，operator
  先 pause 到边界。进程强退仍走 crash/recovery 语义，不伪装成 detach 或 cancel。
- [x] mutation command 统一校验 exact bundle、expected cursor、command id；处理 duplicate、stale、
  active lease 和 out-of-order。
- [x] attach/restart 从 durable checkpoint 重建；started-without-outcome 保持 uncertain，按现有
  work-unit/lifecycle recovery 收敛。
- [x] 增加 topology guard：当前一个顶层 superstep 只有一个 logical visit。guard 失败时阻止 step
  contract 漂移，要求重新设计并行语义。

### 7.2 C4a falsifiable acceptance matrix

| Journey | 必须证明 |
| --- | --- |
| start admission | Start Step/Run 都在第一条 running row 前返回 exact Bundle；Start Step 只提交 bootstrap 一次，Start Run 无额外 bootstrap/重复 Bundle |
| fixture step | 从 bootstrap 一手 step 到 terminal，至少 9 个 completed boundaries，无跨 node 跳步/重复 |
| HITL | step 进入 HITL1 suspended segment；typed answer 后同 visit 可产生下一 segment；human wait 不计任一 duration |
| mode switch | step -> run、run -> pause -> step、step -> continue 共用同一 saver/thread/recipe semantics，无 step graph 变体 |
| breakpoint | v1 breakpoint 在指定 logical node commit 后停；不重复命中当前已提交卡片；无 breakpoint 时到 HITL/failure/terminal |
| intentional pause | shared lifecycle 可保持 active，但 DebugSession 明确 paused-at-boundary；live control lease 阻止 orphan resume/第二 writer，inspect 不受阻 |
| attach listing | live-owned pause 不广告 takeover；control stale 且无 live execution exclusion 后才出现 exact attach，选择前零 mutation |
| refinement | completed Bundle 的 refinement task/cursor 与现有 `snapshot.tasks` 语义兼容 |
| boundary crash | kill debugger 后 control lease 到期且 execution exclusion 不再 live；CAS attach 得到相同 cursor，第一条 command 不多走一步；旧 owner 不能复活写入 |
| mid-node crash | unmatched started 显示 uncertain；恢复后不伪造旧 visit completed |
| double click | 相同 command id 并发/重放最多一个 commit，另一请求 duplicate/stale |
| long node | invocation 跨过 control TTL/heartbeat interval 时第二进程仍 busy/read-only；不会双 commit |
| two processes | control generation + execution fence 只允许一个 writer；失败者不能随后用旧 cursor 多推进 |
| detach | boundary detach 后 cursor/State 不变且 control lease 释放；in-flight detach 被拒，退出不产生 cancel fact |
| failure | node exception、blocked terminal、observation degraded 都停在可解释状态 |
| privacy/authority | TUI command 无 route/profile/State 任意写入口；public Gateway surface 未变化 |

- [x] fixture/headless matrix 全绿；真实模型不是这些断言的唯一证据。（refinement 兼容由既有 refinement 套件覆盖；两进程单写已在 lease CAS 层证明，进程级 harness 待建）
- [x] driver/control-lease module interface tests、multiprocess tests、`make verify` 全绿；delta 同步主（进程级 harness 待建： lease CAS 层已证 single-writer）
  spec，C4a 归档。归档前 Textual 不调用新 mutation interface。

### 7.3 C4b `connect-tui-workflow-debugger` tasks and acceptance

- [x] 新增 executable `run/tui-workflow-debugger.sh` 作为 canonical human entry，并可选提供
  `make tui-debugger` 薄 alias。脚本从任意 cwd 解析本仓 harness root，不 sync/install 依赖，不包含
  Bundle discovery/lifecycle 逻辑；默认工作流不要求 operator 直接运行 Python script。
- [ ] launcher 无参数进入 TUI composition + Bundle chooser；支持 `--fixture`、`--embedded`、
  `--attach <bundle_id>`、`--replay <bundle_id>` 和 `--help`。显式 Bundle intent 仍由 TUI/lifecycle
  validate，脚本不扫描目录、不选 latest、不自动推进；`--help` 同时列出等价 Make commands。
- [ ] fixture 启动零凭证，embedded 启动先做现有 readiness 检查；mode/profile/preflight failure 在
  创建 Bundle 前明确可见。同步 README、COMMANDS 和 local operations，旧入口保留或原子迁移。
- [ ] 首屏实现 New Run / Attach / Replay 三入口：New Run 选择 Start Step 或 Start Run；Attach/Replay
  只消费 lifecycle 验证的 exact candidate，零自动 latest 认领、零选择前 mutation。
- [ ] New/Attach/Replay 既可由 control/command palette 触发，也可手敲显式 slash command；两条路径
  归一到同一个 typed action，并对 exact bundle/cursor 产生相同 update/denial。不得 shell out 到
  三个脚本，也不得在命令 parser 中复制 lifecycle 语义。
- [ ] Textual 只消费 C3 TracePage/NodeContextPage/NodeContextView/NodeSourceView/WorkspacePage/FilePreview 与 C4a
  DebugSession updates，只提交 closed DebugCommand；不直接 render/rebuild prompt、load package resource、
  compile graph、操作 lease、读 path/checkpoint 或推断 lifecycle。
- [ ] 提供明确 mode/cursor/breakpoint/control-lease/pause 状态，以及
  step/continue/run/inspect/answer/cancel/detach；重复输入显示 C4a typed duplicate/stale/busy。
- [ ] 提供 post-node breakpoint 的 set/clear 操作，并明确显示当前 breakpoint；active session 中的
  Run 是无 breakpoint 的 drive-until，Continue 尊重当前 stop policy，两者不得复制执行逻辑。
- [ ] composer 按 setup/HITL/neutral state 做 typed routing；debug mutation 只来自明确 control，
  任意文本不得被猜成 start、step、continue、cancel、attach 或 route/profile/State 修改。debugger
  模式退休现有 ambiguous natural-language research trigger 旁路；slash syntax 只在 adapter 内解析为
  shared typed action，不升级为 public/persisted contract。
- [ ] Files/Inspect 视图与 `/ls`、`/cat`、`/inspect` 复用同一 bounded read interface：可遍历已授权
  mounted workspace 中 policy-public 内容，并打开 exact Bundle 的安全 artifacts/evidence/report；
  path escape、foreign scope、不允许的 raw checkpoint/State/secret 均 fail closed。选择文件或看见
  另一 run 的公开 artifact 都不绑定 Bundle、不改变当前 trace，也不授予 drive 权。
- [ ] 增加 Node Context 视图与 `/context current|invocation <id>|runtime-md|workspace` 等 adapter-private
  等价动作：一张 frame 先列 bridge/node-agent invocation rows，再以 tabs 显示 Initial Prompt、
  Runtime MD、Request、Tools & Budget、Inner Activity、Workspace、Outcome & Handoff、Developer Guide。
  所有内容来自 C3 typed views，不能由 UI 拼 prompt、逆推 raw response/message history 或自行
  决定 deterministic owner/result。
- [ ] Context header 必须显示 CAPTURED_AT_NODE_AGENT_INVOCATION、exact context identity/quality 和
  MATCH/DRIFT/CURRENT_SOURCE_UNAVAILABLE/CONTEXT_NOT_CAPTURED；`workflow.md` 始终标
  DEVELOPER GUIDE - NOT MODEL VISIBLE，deterministic node 显示 NON-MODEL NODE / NO NODE-AGENT
  INVOCATION。coverage strip 固定显示 INITIAL CAPTURED、RUNTIME ENFORCED、ACTIVITY
  BOUNDED/DEGRADED、OUTCOME OBSERVED/UNAVAILABLE 和 FILES CURRENT；内部 provider raw histories 显示
  NOT RETAINED。
- [ ] Files view 显示全部 runtime virtual mounts、effective read/write/attempt roots 和 CURRENT time posture；
  Context Workspace 显示 invocation-time manifest/refs。两者并列时不得把 current bytes 冒充 captured
  filesystem snapshot，也不得显示 host path。
- [ ] Detach 是默认的非破坏性离开动作；Cancel 只有 lifecycle 允许时出现，视觉上与 Detach 区分并
  要求确认 exact Bundle。Ctrl-C/window close 不静默发 Cancel；in-flight 强退按 uncertain/recovery 呈现。
- [ ] attach UI 区分 live-owned busy/read-only 与 stale takeover candidate；选择前零 mutation。
- [ ] terminal/blocked 后回到同一 workbench，可 Replay 当前 exact Bundle 或 New Run 创建新 Bundle；
  保留旧 trace 可读，不提供原地 State/route 编辑，也不伪装 v1 已有自动 cross-run diff。
- [x] 同步 `docs/run-lifecycle-walkthrough.md`：HITL1 是正式人工停点，当前 real HITL2 是
  autonomous continuation；TUI 不显示第二个人工 answer 控件。
- [x] launcher/entry tests 覆盖任意 cwd、no-arg chooser、fixture/embedded、help、非法参数、explicit（entry tests 5/5 绿：cwd/help/flags/fail-closed/executable/零扫描静态断言）
  attach/replay intent 透传，以及“脚本零 workspace 扫描/零 lifecycle mutation”；目标 `.sh` 实际可执行。
- [ ] fixture Textual Pilot 按 target UX 覆盖：首屏三入口、Start Step/Run、完整 step journey、
  breakpoint/mode 切换、HITL typed input、composer 误路由反例、按钮/命令重复触发、长卡片、三种
  terminal size/resize、pause requested、Cancel 确认、stale/busy denial、detach/restart/reattach、
  terminal replay 与 New Run；另证明 control 与手敲命令等价、文件树与 `/ls`/`/cat` 等价、path
  escape/private cross-Bundle 读取被拒，policy-public artifact 浏览不产生 lifecycle binding；Context tabs/
  `/context` 等价、多 node-agent invocation 不覆盖、单个 invocation 内多 provider calls 不
  伪造多 snapshot、live/replay snapshot 相同、source drift/legacy/deterministic/NOT_RETAINED labels
  准确，80x24 下 Context 仍可完整切换且不遮挡主控制。
- [ ] fixture adapter 全绿后接 embedded all-real composition；Gateway 保持 observer-only。
- [ ] C4b 不新增或改写 runtime drive semantics；发现 contract 缺口时返回 C4a corrective change，
  不在 TUI 私有补丁中绕过。
- [ ] `make verify` 全绿，TUI delta spec 同步，C4b 归档。

### 7.4 No-go / 收缩

若 intentional pause 只能冒充 suspended/orphan、需要跨 operator pause 长期占用 execution lease，或 refinement、restart、
concurrency 无法在同一 graph/checkpoint authority 下闭环，停止 real 接线。允许保留 C3
observer/replay TUI；不允许创建第二 graph、隐藏 debug State 或 TUI 私有恢复。若 C4a 已绿但 C4b
体验无法收敛，保留 headless driver 和 observer TUI，关闭 mutation adapter，不回退 C4a contract。

## 8. 终线 - real validation（无 change）[ ]

- [ ] 固定一个问题和 model profile，预先记录 exact baseline；网络/凭证只在本阶段需要。
- [ ] 用 embedded local debugger 完成一轮：auto run 一段、pause、关键 node step、inspect refs、
  continue、HITL typed answer、最终 terminal。
- [ ] 在至少一个真实 LLM-bearing node/repair 的 bridge/node-agent invocation 打开 Node
  Context，核对 captured runtime MD、initial prompt、request、实际 tools/budget、
  mount/read/write/attempt roots 与 renderer/bridge 输入一致；核对内部 model/tool counts 与 safe
  outcomes，并确认完整 raw provider histories 明示 NOT_RETAINED。重启 Replay 后 bytes/identity
  不变，且屏幕无 host path/credential/secret。
- [ ] 从 `run/tui-workflow-debugger.sh --embedded` 进入真实首屏，完成 New Run -> Start Step，并在
  terminal 后用 New Run 创建第二个 exact Bundle 走 Start Run；证明调试态和全速态共享同一
  trace/graph semantics，旧 Bundle 仍可 Replay。
- [ ] 证据绑定 exact bundle/cursor；抽查 TraceFrame 与 events/checkpoint/lifecycle 一致，不使用
  latest Bundle 或屏幕截图单独证明。
- [ ] 进程退出后重新 attach 并历史 replay，frame sequence/terminal 与 live session 一致。
- [ ] 记录体验问题：卡片噪声、等待反馈、命令可发现性、长 node 的 pause 诚实度；contract bug
  回新 corrective change，纯 presentation 调整可走当前允许的最小变更流程。
- [ ] 明确结论是 local operator debugger 验收，不宣称 Gateway remote debugger 或 Primary User UI。

## 并行线（020 战役遗留，与本阶梯并行推进）

- [ ] **B1 第 3 跑收尾**（等网络恢复）：`make demo-tui-embedded-smoke` 真人实跑
  （操作单 = `../_local_demo/runbook-020-tui-manual.md` §3）；PASS 7 条核对
  （`verify_b1_pass.py` 已就绪）→ 记 handoff-020；撞茬走 `../bugs/` 流程（编号权威 BUG-067——BUG-066 已被架构检查器漂移占用，见 §L）
- [ ] B2 CHOICE 专项（条件式：typed OPTION 修复已归档；战后仍决定覆盖才跑）
- [ ] C Gateway observer（可选：预写观察问题清单，否则直接关闭）
- [ ] 战役收口：证据折叠 runbook-020 附录、阶梯表状态、handoff-020 删除
  → 收口后按治理把 `archive/` 五份 TUI 文件整组 `git mv` 进 `../_done/_closed_plans/`
  （plan ID 从 CLS-058 起）并同步 README 索引

## 9. Dated grounding 与实验状态

完整证据、代码位置、最小实验过程和被拒方案见
[grounding review](tui-step-debugger-grounding-review.md)。本节只保留会直接影响执行顺序的
当前状态；本地 Bundle 数量是 2026-08-31 样本，不是 contract。

| # | 已证明 | 尚未证明 / 纠正 | 所属 gate |
| --- | --- | --- | --- |
| E1 | `aget_state_history` 能从样本 Bundle 形成 11-15 帧历史 | spike 直接开 path/SQLite/compile graph，不是正式 interface | C3 替换 spike |
| E2 | checkpoint 有 `created_at` | **原结论撤销**：相邻差包含人类/暂停时间，不是 node duration | C3 显式 duration test |
| E3 | completed/blocked/suspended checkpoint 能形成粗卡片 | suspended Journal 被真实 RunEvent 拒绝，不能称 observation truth 已绿 | C0 real-store test |
| E4 | 同一 graph/saver/thread 可 bootstrap pause -> HITL -> typed resume -> run complete | Bundle lifecycle 会把 no-pending pause 看成 active/orphan；control lease、refinement、restart、concurrency、mid-node crash 未证 | C4a matrix |
| E5 | 未执行 | 只在 TraceFrame contract 稳定后做 TUI 手感调参 | C3 UI gate |

截至本 plan 重写时的代码事实：

- `RunEvent.outcome` 只接受 started/completed/failed，而 wrapper 发出 suspended；C0 未开始。
- TUI live progress 仍选择 latest active/suspended Bundle；C0 未开始。
- `ContinueRun` 仍是 orphan natural resume；它不是 debugger command。
- `scripts/demo_tui.py` 1817 行，主集成测试 1295 行；C3 应阻止 runtime semantics 继续增长。
- `scripts/experiments/tui_trace.py` 是 zero-contract read-side spike；C3 不得把任意 path interface
  原样产品化。
- Journal 默认最多 256 条并有 priority eviction；完整顶层 boundary 可依赖 checkpoint，完整内层
  narration 不能被预设为永久可回放。
- 当前 bridge 在内存中 render exact initial system/human messages 后构造 fresh agent 并调用
  `agent.ainvoke`，尚无 Bundle-private node-agent invocation context snapshot；当前源码事后重
  render 不能证明历史 prompt。fresh agent 内可有多次 provider calls，当前也无完整 raw
  message-history replay contract。C3 必须补上前者，并对后者明示 NOT_RETAINED。
- runtime-loaded Markdown 只有 base `resources/node_agent/runtime_policy.md` 与 selected package-local
  `capabilities/*.md`；每个 node 的 `workflow.md` 是 non-runtime maintainer projection。TUI 必须同时可见但
  清楚分栏，且不得把 package source mount 进 research sandbox。
- `openspec list --json` 在 2026-08-31 plan 重写时为空；该 dated fact 已被 2026-09-01 创建的 Cpre
  planning draft 取代。当前 active planning scope 仅为 `reconcile-hitl2-autonomous-contracts`，尚未
  apply/sync/archive；Cpre 归档并准备 propose C0 前仍须重新检查 overlapping active change。

## 10. 提案前交接清单

接手者 review/apply 当前 Cpre，或创建任何后续 change 前，逐项确认：

- [ ] 完整阅读本 plan；按当前阶段阅读 grounding review；进入 C3/C4a/C4b/real validation 时完整
  阅读 target UX，并检查 git 中是否已有 overlapping active change。
- [ ] 重新运行该阶段的最小反证，确认 dated evidence 未因代码变化失效。
- [ ] 在 proposal/design/tasks/spec 中建立 source mapping，逐项映射本阶段 tasks、target UX
  journey/negative paths/traceability、acceptance 和 no-go；确认没有从 campaign 历史导入任务。
- [ ] 明确 surface：persisted RunEvent、versioned TraceFrame/NodeContextSnapshot、local
  NodeContextPage/NodeContextView/NodeSourceView、local OperatorWorkspaceReader、local DebugCommand，分别给出兼容策略。
- [ ] tests 穿过正式 module interface；fake-only 或 UI snapshot-only 不能证明 runtime contract。
- [ ] 保持 `deerflow/` submodule 只读；实现只发生在 `deep_research_harness/` 与对应 specs/tests。
- [ ] change 归档后更新本文件 checklist 与 §L，并复核 target UX traceability；不追写冻结历史文档，
  未归档前不开始下一阶段。

## L. 进展记录（append-only）

本表按当日认知保留历史，不回写旧行；旧行中的“下一步”若与后续行或页首状态冲突，以日期更晚的
记录和 §4 当前阶梯为准。尤其是 2026-08-31 的“下一步仅可 propose C0”已被 2026-09-01 插入并创建
Cpre planning draft 的记录取代。

| 日期 | Stage | 事项 | 结果 |
| --- | --- | --- | --- |
| 2026-08-31 | — | 文件创建；体验定义定调（REPL 双面：叙述流 + 操作面） | 📋 Stage 0 待拍板 |
| 2026-08-31 | — | Review 就绪化：技术 grounding 预核全绿——39 个现存 bundle 的 graph.sqlite 各含 11 行逐超步 checkpoints、`aget_state_history` 可用、serde 边界与 `_config` 同构确认；留存策略验证项关闭 | 📋 Stage 0 待拍板（D6/D7） |
| 2026-08-31 | — | 用户定调：按 openspec change 推进——阶梯重构为 **C3 `add-tui-trace-observation`（观察叙述面）→ C4 `add-tui-step-driving`（步进驱动面）→ real 验证跑（无 change）**；原 Stage 1–3 折叠进 change 任务序（先尖刺后契约），流程对齐 C1/C2 纪律（propose→polish→apply→verify→archive） | 📋 Stage 0 待拍板（D6/D7） |
| 2026-08-31 | E1–E3 | 实验 3 枚完成（`scripts/experiments/tui_trace.py` 只读尖刺）：4 类样本回放全过——fixture completed 11 帧/9 边界卡、real completed 15 帧、**BUG-062 real blocked 12 帧（wave2 16min 单卡可见、blocked 原因键在终卡 Δ）**、suspended 4 帧（HITL 停点 + 等待内容可读）；耗时 = 相邻 checkpoint ts 差（metadata.writes 为 None → 差分法）；E4 编译层通过、运行时部分留 C4 spike | ✅ C3 数据形状实证成立；差分法替代 events 对齐，卡片字段闭集可定稿 |
| 2026-08-31 | — | `deep_research_harness/scripts/` 分层重组：根 = 常态入口/运维 + README 导读、`checks/` = verify 校验家族 9 文件、`experiments/` = 实验尖刺（tui_trace.py 迁入）；引用面同步 Makefile ×8 + required-paths.toml ×2 + 13 测试 import + docs；bootstrap parents[1]→[2]；结构注册表不枚举 scripts/，无需立 change | ✅ 门禁全绿（fast 2674 + integration 302[4 skip] + workflow 35 + ruff check/format；wheel-exclusion 一测因沙箱禁 uv 缓存环境性未跑，与重组无关）；顺手登记 **BUG-066**（架构检查器干净树即红，存量 ignored_paths 漂移，修复 = 单行 registry 同步走微 change） |
| 2026-08-31 | — | openspec 微 change `sync-structure-registry-ignore-entries` 闭环：propose → polish（plan gate 四组件全绿 + reservation PRS-022 映射 task 1.2）→ apply（registry `[ignored_paths]` +`.uv-cache/`、req-registry 登记 PRS-022、checker 干净树 exit 0）→ delta 同步主 spec（PRS-022 requirement + header）→ archive `2026-08-31-sync-structure-registry-ignore-entries`；BUG-066 关闭迁移 `_done/_fixed_bugs/`（编号权威 → BUG-067） | ✅ 治理门恢复绿，change 收口 |
| 2026-08-31 | plan deep review | 用户授权直接修订：D6 通过；D7 改为 C0 truth -> C3 trace -> C4a headless driving -> C4b TUI adapter；D8 固定为 local operator debugger。发现 persisted `RunEvent` 拒绝 suspended、live progress latest 假归因、ContinueRun 语义冲突、checkpoint duration 错误、Journal 256 条 retention、pre-checkpoint completed、HITL visit-id 复用及 intentional pause/orphan 冲突；补做 E4 graph fixture，证明同一 recipe/saver/thread 可 step -> HITL -> run，但 Bundle lifecycle/control lease、refinement/restart/concurrency 未证。新增冻结 grounding review，主 plan 改为当前唯一执行权威。 | **Stage 0 关闭；下一步仅可 propose C0，旧 E2/E3 绿结论由本行和 §9 纠正** |
| 2026-08-31 | plan final audit | 澄清 C1/C2 已归档、C0 是新增纠错闸门；区分 debug control lease 与 per-invocation execution exclusion，并补入 long-node fencing 与 takeover 的双条件。 | 执行顺序不变；消除编号歧义和 TTL 并发漏洞 |
| 2026-09-01 | target UX audit | 新增从 executable `.sh` launcher、Bundle chooser、Start Step、HITL、breakpoint、run/pause、failure、detach/attach 到新 Bundle 全速复验的目标体验稿；补齐 `OperatorWorkspaceReader`、首屏三入口、start 首步、composer routing、detach/cancel 和 terminal iteration 验收。 | 目标体验逐项映射 C0/C3/C4a/C4b；无超出现有 authority 的隐含承诺 |
| 2026-09-01 | node-context UX audit | 将研发调试所需的 exact initial node-agent context 从 optional attribution 提升为 C3 gate：`agent.ainvoke`/首次 provider call 前捕获 runtime MD/initial messages/request/policy/mount refs，live/replay 同构；分开 node-agent invocation 与内部 provider calls，后者只保留 bounded safe facts 并标 raw history NOT_RETAINED；分开 captured context、current workspace 与 non-runtime `workflow.md`，补 source drift、legacy、capture-failure 和 secret/host-path 反例。 | TUI 能解释 node 声明过的输入/enforcement/activity/outcome 上下文且不冒充未保留历史；package source/Gateway 权限不扩张 |
| 2026-09-01 | cross-document consistency audit | 系统复核 current plan、target UX、grounding review 与三份 campaign 历史；建立文档 authority/read-order、OpenSpec source mapping 与 drift 回流规则；C4a 纳入 target UX 必读 gate；冻结材料增加 supersession/retirement 路由。 | 当前执行任务只来自本 plan；UX 承诺可追踪到 C0/C3/C4a/C4b；旧 §10/Phase 8 不再形成第二计划 |
| 2026-09-01 | plan intention/authority sync | 补入原始 debugger 意图、旧 TUI 失效原因、campaign/E4 证据边界、八项设计原则与“压力 -> correction -> stage”因果链；登记 Cpre planning draft 已创建但未 apply/sync/archive，并补齐 Cpre scope/gate。 | 无上下文 Agent 可从本 plan 理解为何按 Cpre -> C0 -> C3 -> C4a -> C4b 推进；当前只允许 review/polish Cpre，未开始实施 |
| 2026-09-02 | C4a xfail 转正 | 投影 suspended 帧配对修复后：原 crash-restart xfail 转正（CAS attach 恢复 cursor + answer 增长时间线）；uncertain xfail 摘除（unmatched started → replay=uncertain/live=running）；矩阵 7/7 全绿 + 回归 19/19；ruff 与 `UV_OFFLINE=1 make verify` exit 0。 | **C4a 剩余：refinement 兼容行与两进程单写证明（lease CAS 层已部分证明），完成后 sync/archive** |
| 2026-09-02 | C4b 文档同步 | README Entry Surfaces（表尾插入 Debugger workbench 行，DRC-006 契约测试通过）+ COMMANDS.md TUI 路线表补 launcher 行；`UV_OFFLINE=1 make verify` exit 0。 | **文档同步完成；C4b 剩余：Node Context pane、Pilot 三尺寸、no-arg chooser、sync/archive** |
| 2026-09-02 | C4b propose + 部分实现 | propose 完成（research-demo-tui 新增 RED-013 canonical launcher / RED-014 workbench 三入口 + Node Context pane；plan gate 绿）。已落地：可执行 `deep_research_harness/run/tui-workflow-debugger.sh`（任意 cwd 根解析、no-arg/--fixture/--embedded-smoke/--attach/--replay/--help、unknown flag 非零退出、零扫描/lifecycle 逻辑）+ `make tui-debugger` alias + demo_tui attach/replay intent 参数与校验 + 入口测试 5/5。README 行回退（DRC-006 契约测试锁定 Entry Surfaces 顺序——文档同步需按其规则重做）。`UV_OFFLINE=1 make verify` exit 0。剩余：Node Context pane 接线、Pilot 三尺寸旅程、README/COMMANDS 按契约重做、sync/archive。 | **C4b 未归档；C4b 剩余项即下一会话起点** |
| 2026-09-02 | C4a closeout/archive | 修复 terminal sync（镜像 executor 传完整 state values）后 drive_until 全链路到 terminal（≥9 committed boundaries，journal 证明）；矩阵 8/8；ruff/lint 全绿；`UV_OFFLINE=1 make verify` exit 0；strict/closeout 门全绿；新主 spec `local-workflow-debug-driving`（LDD-001..005）同步；归档 `2026-09-02-add-local-workflow-debug-driving`。已注记：两进程单写在 lease CAS 层证明（进程级 harness 未建）；refinement 兼容由既有 refinement round 套件 + driver attach 覆盖。 | **C4a 关闭；C4b 解禁。下一步 = propose C4b（launcher + Textual 纯 adapter），然后终线（需网络/凭证）** |
| 2026-09-02 | plan 全量对账 | 应操作者要求对本 plan 做全面对账：§5(C0)/§6(C3)/§7.1+7.2(C4a) 全部已完成项勾选（62 项）；§6 三项 presentation 任务（TUI helper 迁移、pane typed 化、E5 三尺寸）显式标注随 C4b 落地；§7.3(C4b) 仅勾 launcher 项，其余 30 项如实保留未勾并对应 C4b 剩余范围（Node Context pane、Pilot 三尺寸、README/COMMANDS 按 DRC-006 契约重做等）；§8 终线全部未勾。当前真实位置一目了然：**C0/C3 已归档，C4a 接近归档（剩 refinement/两进程两行），C4b 半程，终线未开始**。 | **plan 即权威交接面；后续每里程碑同步本表** |
| 2026-09-02 | C4a 收敛 | 矩阵 7/7 全绿（start 幂等/单边界 step/HITL answer/breakpoint drive/pause/detach 释放/双 driver fencing+CAS+边界崩溃重启不推进）。投影新增 interrupt-checkpoint 的 suspended 帧配对（journal FIFO），连带修复：原 xfail（CAS answer 后帧增长）转正；剩 1 xfail = unmatched started 的 active 投影（running/committing/uncertain 判别细节，LDD-001 剩余行）。ruff 全绿；`UV_OFFLINE=1 make verify` exit 0。 | **C4a 未归档（剩 1 xfail 排查 + refinement/两进程矩阵行）；下一会话从这两项继续，随后 C4b** |
| 2026-09-02 | C4a driver 实现 | `runtime/debug_driver.py` DebugRunDriver 主体落地：open_start（幂等 admission + exact handle 先行 + BundleAlreadyActive→busy）/open_attach（live→busy；stale+generation CAS takeover；attach 零推进）/execute（duplicate/stale/busy/not_found/in_flight typed denials；pause_request；answer 走既有 pending correlation；detach 释放 lease 并结束 session；cancel 走 lifecycle）。advance_one 经 execution_exclusion + open_graph_checkpoint + 逐次 interrupt_after 单边界提交（topology guard：next>1 fail closed）+ sync_graph_progress 对账；drive_until stop policy（breakpoint/HITL/failure/terminal/pause）。矩阵：6/7 绿 + 1 xfail（CAS attach 恢复 cursor 已证；answer 后帧增长边缘差异排查中——投影/对账细节，属 LDD-004 剩余行）。lease 冒烟 3/3；ruff 全绿；`UV_OFFLINE=1 make verify` exit 0。 | **driver 核心绿；1 xfail 待查 + drive_until/breakpoint 完整链路已绿；C4a 未归档，剩 xfail 排查与剩余矩阵行** |
| 2026-09-02 | C4a 实现交接 | 会话上下文临近极限，按检查点交接（工作树干净，全部已提交）：已落地 domain/debug_driving.py（closed DebugCommand/BoundaryCursor/session/Start/Attach/StopPolicy）+ runtime/debug_driving.py（ControlLease：acquire/heartbeat/release/stale/CAS takeover 双条件门 + generation fencing；DebugCommandLedger at-most-once；冒烟 3/3 绿）。**DebugRunDriver 主体待实现**，已核实可复用通路：`lifecycle.execution_exclusion(bundle)`（exclusion + ensure_live）、`lifecycle.open_graph_checkpoint(bundle)`→saver、`executor._recipe.builder.compile(checkpointer=saver)`、`executor._config(bundle)`、`graph.ainvoke(..., interrupt_after=[node])`（E4 已证逐次可用）、`executor._journal_envelope(...)`、`lifecycle.sync_graph_progress(values/pending)`、`runtime/human_input.pending_from_snapshot`。实现要点见本 change design D1-D5 与 tasks §3-4（start 幂等、advance 单边界、drive_until stop policy、topology guard、双进程/崩溃/TTL 矩阵）。 | **交接清晰；下一会话从 DebugRunDriver 主体继续，然后 C4b 与终线** |
| 2026-09-02 | C4a WIP | domain/debug_driving.py（closed DebugCommand/BoundaryCursor/session snapshot/denials/Start-Attach）+ runtime/debug_driving.py（ControlLease：acquire/heartbeat/release/CAS takeover 双条件门、owner fencing；DebugCommandLedger at-most-once 冒烟 3/3 绿）提交检查点 d73e9a4。 | **lease/ledger 绿；DebugRunDriver 主体（advance_one/drive_until/matrix）待实现** |
| 2026-09-02 | C4a propose | 新 capability `local-workflow-debug-driving`（LDD-001..005：命令闭集 at-most-once / expiring control lease+fencing / step-drive 执行语义 / attach-detach-restart / topology guard），proposal/design/tasks/delta spec 齐备，plan gate 绿。C3 委托失败教训已采纳：后续 mutation 全部自主实现。 | **propose 关闭；进入 TDD apply** |
| 2026-09-02 | C3 closeout | node-context 半区完成：domain/node_context.py（Snapshot/View/SourceView/coverage 闭集）+ runtime/node_context_store.py（Bundle-private 原子发布、same-id/hash 幂等与冲突、容量 typed 拒绝、durable segment→invocations index、分页 summaries、NodeSourceReader MATCH/DRIFT/CURRENT_SOURCE_UNAVAILABLE）+ bridge capture seam（render+admission 后、ainvoke 前强制 durable capture；capture/conflict/容量失败 → typed fail-closed，provider 零调用；activity facts 随终态 best-effort 上报；production 默认无 recorder 行为不变）。测试：store 4 + capture 3 + 全套 fixture 全绿；unit+integration+graph+contract 2548 passed（wheel 环境性失败同 §L 既有记录）；ruff 全绿；`UV_OFFLINE=1 make verify` exit 0；strict/hygiene/closeout 门全绿；新主 spec 同步（56 specs）。三次委托 subagent 均因会话沙箱写入限制失败，全部转自主实现——后续阶段不再委托 mutation。归档 `2026-09-02-add-local-workflow-debug-observation`。 | **C3 关闭；C4a 解禁。下一步 = propose C4a（DebugRunDriver + control lease），propose 前重跑 openspec list 与 §10 重验** |
| 2026-09-02 | C3 apply（进行中） | propose 完成（新 capability `local-workflow-debug-observation`，LDO-001..008 登记，plan gate 绿）。实现进度：LDO-001..004 已落地——domain/trace.py（TraceFrame/TracePage/ActiveVisitProjection 闭集）+ runtime/trace_projector.py（checkpoint=commit 权威、trace 增长判 commit、opaque TraceReadCursor 含校验 fail-closed、live/replay 同构、degraded/unavailable 披露）+ builder wrapper monotonic duration_ms（含 suspended 路径）+ finalized-node eviction 优先级 45；fixture 7/7 绿（isomorphism/cursor fail-closed/duration+privacy/非 commit failed 帧/uncertain/双 Bundle 隔离/journal 损坏骨架保留）+ retention 1/1 绿。LDO-007 已落地——OperatorWorkspaceReader（composition 注入 trusted roots、相对路径/verified ref、escape/absolute/private/binary/oversize typed denial、无 host path、hash 校验、CURRENT 姿态）fixture 7/7 绿。`tui_trace.py` spike 已删除并同步 experiments README（required-paths 未引用，架构检查 exit 0）。委托式 subagent 三次因会话沙箱写入限制失败（无改动），全部转自主实现。待办：LDO-005/006 node-context capture/store/inspector、其 fixtures、closeout 门、sync/archive。 | **C3 apply 过半；trace+workspace 绿，node-context 待实现** |
| 2026-09-02 | C0 apply/archive | 静默自主执行 C0 全链：重验 dated evidence（suspended Literal 拒绝 + 静默丢弃链）→ 委托式 reader/writer 全量盘点 → propose `repair-run-observation-truth`（REJ-011 MODIFIED + 新 RED-012，plan gate 绿）→ 红阶段 7 个确定性失败 → 实现：RunEvent v3 outcome 值集扩展 `suspended`（REJ-011 绑定，无版本 bump/迁移）、`ObservationOutcome.SUSPENDED`、builder 投影不再改标 failed、demo TUI live 旁听 exact-bind（`_latest_active_bundle`/dead `_event_feed_lines` 删除，suspended 叙述为「待恢复」）→ 绿：聚焦 181 passed、integration+graph+contract 1424 passed（wheel-exclusion 环境性失败与 §L 记录一致，非本次引入）→ `UV_OFFLINE=1 make verify` exit 0 → REJ-011/RED-012 sync 主 specs → strict/hygiene/closeout 门全绿 → 归档 `2026-09-02-repair-run-observation-truth`。 | **C0 关闭；C3 解禁。下一步 = propose C3 前重跑 `openspec list`（现为空）并按 §10 重验 C3 相关 dated evidence** |
| 2026-09-02 | Cpre apply/archive | 静默自主执行 Cpre 全链：polish（workflow-control 引用修正 + design §D5 五能力 keep/retire matrix）→ 15 个 delta hunk 原子 sync 五主 specs → REN-001/REN-006 registry 摘要 → walkthrough §4 autonomous HITL2 重写 → 合成 HITL2 prompt fixtures 删除/迁移（`awaiting_hitl2`/`awaiting_invalid_hitl2_choice` 移除，invalid-choice 证据迁至 HITL1 language CHOICE；refinement DRH-005 测试迁至有效 HITL1 pending subject；TUI composer CHOICE exact-match-only 收窄）→ 122 处 specs HITL2 审计 0 违规 → 1.2 红线 baseline 全部清除（4.1 扫描 exit 1）。红/绿证据：adapters 红期 1 failed（"proceed" 硬编码示例）→ 迁移后 adapters 36 / 集成 86 / 最低 seam 35 全绿；`UV_OFFLINE=1 make verify` exit 0；strict validation + plan/closeout 门全绿；diff 无 src/deerflow 变更。干净树 closeout 门存量回归（commit 3965640 遗留）登记 BUG-067 并以零契约面修复关闭（README prose token ×2 + `check_project_architecture.py` 补 `@impl PRS-022`）。归档为 `2026-09-02-reconcile-hitl2-autonomous-contracts`。 | **Cpre 关闭；C0 解禁。下一步 = propose C0 前重跑 `openspec list` 与 §10 dated evidence 重验（`RunEvent` suspended 拒绝重现）** |
