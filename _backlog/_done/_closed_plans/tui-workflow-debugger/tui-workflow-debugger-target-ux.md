# TUI Workflow Debugger Target UX

> 类型: 受控的目标体验、主旅程与计划追踪
> 日期: 2026-09-01
> 目标状态: C0、C3、C4a、C4b 全部归档后的 local contributor/operator experience
> 当前决策与执行权威: [`tui-workflow-debugger-progressive-plan.md`](tui-workflow-debugger-progressive-plan.md)
> 前置技术证据: [`tui-step-debugger-grounding-review.md`](tui-step-debugger-grounding-review.md)，冻结到 2026-08-31
> UX 专项依据: 本文 §8-§12 与当前 plan 中 2026-09-01 后的 Node Context、Files、launcher 决策
> 状态: 已收口（2026-09-02）— 目标体验经 C0/C3/C4a/C4b 归档落地；E5 三尺寸 Pilot 调参为唯一尾差。

## 文档控制

本文与当前 plan 同层存放，是当前 plan 的受控 supporting baseline，不是历史 campaign，也不是
独立 backlog。它只能说明“完成后应该怎样体验、怎样验收”，不能自行增加 runtime owner、persisted
schema、权限或阶段。

implementation discovery 若改变本文承诺，必须先回到当前 plan 记录事实、影响阶段和处置，再同步
本文 traceability；不得让 TUI 实现或某个 OpenSpec change 静默偏离。已经归档的 OpenSpec change
保持不可变，后发现的 contract 缺口通过 plan 中新的 corrective change 前进。任何 UX 条目若无法
映射到 plan task 和 falsifiable acceptance，就不能作为已批准需求进入 proposal。

## 1. 最终体验的一句话定义

operator 启动一个本地 TUI workbench，在其中创建或接管一个 exact Run Bundle，看着同一张真实
StateGraph 按节点边界产生可信 timeline；需要细调时逐步 Step，需要快速穿过已验证区域时
Continue/Run，需要看现场时 Inspect，需要人工输入时回答正式 HITL。进程退出后可以从同一
checkpoint Attach，调好代码或 prompt 后再创建新 Bundle 重跑，最后用同一 TUI 完成一次全速运行。

它也是 node 级研发调试器：选中一张卡后，可以继续打开该 node 的 captured
node-agent invocation context，查看当次 `RuntimeNodeAgentBridge.run_agent` 开始时真正生效的 runtime MD、
初始 system/human messages、request、tool/budget policy、虚拟 mount/read/write roots、
输入 refs 和对应 workspace 内容。研发用 `workflow.md` 与源码导航也在旁边可见，但明确标为
`DEVELOPER GUIDE - NOT MODEL VISIBLE`，不冒充模型当时看到的上下文。

这不是三套 CLI，也不是 step graph 和 run graph 两套系统。外部只有一个 TUI workbench；New Run、
Attach、Replay 是其中三类动作。按钮、快捷键、command palette 和手敲 slash command 都只是在调用
同一个 typed adapter action。

所有 workflow 执行与调速都在 TUI 内完成。源码、prompt 或配置的编辑仍由 operator 在正常开发工具
中完成；v1 不把 TUI 伪装成代码编辑器，也不允许原地修改 checkpoint State。

## 2. Operator 的心智模型

进入 TUI 后，operator 始终能回答七个问题：

1. 我现在看的是哪个 exact Bundle？
2. 这次 session 是 Run、Step、paused、HITL、terminal，还是只读 Replay？
3. 已经 committed 到哪个 boundary，下一 logical node 是谁？
4. 当前是谁拥有控制权，第二个进程能不能推进？
5. trace 是 complete、degraded，还是 unavailable？
6. 我此刻能安全执行哪些动作？
7. 这个 node 的初始输入、cognitive program、runtime enforcement、内层活动与最终 handoff
   分别是什么，哪一层出了问题，它与当前源码是否一致？

对应的 UX 不变量：

| 不变量 | 用户能观察到的结果 |
| --- | --- |
| exact identity | header 从拿到 verified handle 起固定显示 Bundle id；不会悄悄切到最近 run |
| one graph, two speeds | Step 与 Run 产生同一种 TraceFrame、route 和 terminal，只改变停止策略 |
| boundary honesty | running、pause requested、committing、paused、failed 分开显示，不把进行中说成完成 |
| explicit mutation | 只有明确 control/slash command 能推进、应答、detach 或 cancel；普通文本不被猜成命令 |
| inspect is read-only | 浏览 timeline、文件和诊断不改变 cursor、lease、route 或 State |
| captured context is historical truth | Replay 展示 node-agent 进入 fresh agent 前保存的 exact initial context；当前源码只能标 current/match/drift，不能重建历史事实 |
| context coverage is honest | initial context、enforcement、bounded activity、outcome 和 current files 分别标 provenance/quality；未保留的内层消息明确显示 `NOT RETAINED` |
| recoverable ownership | live owner、busy observer、stale takeover 与 orphan recovery 明确区分 |
| failure is visible state | blocked、degraded、uncertain、unavailable 都有独立姿态，不埋在聊天文本里 |
| old runs stay immutable | 调整代码后创建新 Bundle；旧 Bundle 继续可 Replay，不被覆盖或续写成另一次实验 |

## 3. 两层入口，而不是三个程序

### 3.1 外层：一个准备好的 `.sh` 入口

最终仓库直接交付：

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh
```

无参数时，脚本打开 TUI 的 composition chooser，随后进入 lifecycle-backed Bundle chooser。用户不需要
先知道 Bundle 目录，也不需要记住 Python script。常用的 direct forms 是：

```bash
./run/tui-workflow-debugger.sh --fixture
./run/tui-workflow-debugger.sh --embedded
./run/tui-workflow-debugger.sh --embedded --attach b_xxx
./run/tui-workflow-debugger.sh --fixture --replay b_xxx
./run/tui-workflow-debugger.sh --help
```

`--attach` 和 `--replay` 只是 explicit intent；TUI/lifecycle 仍验证 Bundle、scope 和 posture。脚本不能
扫描 workspace、按 mtime 选 latest、解析 State/checkpoint 或直接取得 lease。Attach 成功后不自动
推进，Replay 永远只读。

Bundle chooser 本身保持简单：支持方向键选择和按 exact id 过滤，每行只显示 bounded id、
composition、status@phase、generation、更新时间与 lifecycle 给出的 legal action。选中一行是纯读；
只有明确选择 Attach Control 或 Replay 才提交 action。terminal 只显示 Replay，live-owned 只显示
Read-only，可接管 posture 才显示 Attach Control。不会出现一个含糊的“继续最近任务”按钮。

脚本的 `--help` 同时给出可手敲的等价入口：

| 目的 | 启动命令 | 最终能力 |
| --- | --- | --- |
| 无凭证练习与回归 | `make demo-tui-fixture` | 完整 trace、Step、Run、HITL、Attach、Replay |
| 本地 all-real 调试 | `make demo-tui-embedded-smoke` | readiness 通过后具备同一套完整 debugger 能力 |
| profile Gateway | `make demo-tui PROFILE=<name>` | observer-only；v1 不提供远程 debug driving |

C4b 同步 README、COMMANDS、local operations 和可选 `make tui-debugger` alias。launcher 必须可从
任意 cwd 调用、自己定位 harness root、不做 dependency sync/install，并由 entry tests 证明目标文件
实际 executable。这个脚本由 C4b 的实现者创建并提交，不要求 operator 自己手写；在 C4b 归档前，
仓库当前没有这条目标入口，不能用一个只会启动旧 visualizer 的占位 wrapper 冒充已交付 debugger。
它是 local adapter-private entry，不是 lifecycle owner 或 public API。

### 3.2 内层：同一个 TUI/REPL 的显式动作

首屏的三入口都可以点，也可以手敲：

| 屏幕动作 | 手敲等价形式 | 语义 |
| --- | --- | --- |
| New Run / Step | `/new --step` | 新 Bundle，绑定后执行 bootstrap 一步并暂停 |
| New Run / Run | `/new --run` | 新 Bundle，绑定后按自动 stop policy 推进 |
| Attach | `/attach <bundle_id>` | 对可接管的 exact Bundle 取得 debug control；不自动推进 |
| Replay | `/replay <bundle_id>` | exact Bundle 的只读历史；永不取得 control lease |

进入 session 后，同一 composer/command palette 还接受 `/step`、`/continue`、`/run`、`/pause`、
`/break after <node>`、`/break clear`、`/inspect`、`/context`、`/ls`、`/cat`、`/detach` 和 `/cancel`。
WORKBENCH 中保留独立 question draft；`/new --step` 或 `/new --run` 消费当前已经校验的 draft，
不得把任意自然语言自动猜成 start。实现可以提供带 question 参数的显式等价语法，但只能有一条
typed Start action。

这些不是 shell escape。parser 只构造 closed typed actions；它不直接 compile graph、打开 checkpoint、
操作 lease 或实现 lifecycle 分支。按钮和命令必须在 adapter boundary 前归一，返回相同 update 或
typed denial。

slash command spelling 属于 local Textual adapter-private surface，可以随 C4b 的同步文档演进；跨模块
承诺是 closed `DebugCommand`/session action，持久化承诺是 versioned TraceFrame/RunEvent。命令语法
不进入 Gateway/public reflected tool，也不成为第三个 lifecycle owner。

## 4. 工作台长什么样

宽终端的稳定布局可以是：

```text
Deep Research Debugger | EMBEDDED | b_a81f... | gen 3 | STEP | PAUSED -> wave1 | TRACE COMPLETE | OWNED
-------------------------------------------------------------------------------------------------------
TIMELINE                                      CURRENT BOUNDARY
01  bootstrap          completed   0.18s      node: wave0 / visit 4 / frame 5
02  hitl1              suspended   1.42s      outcome: completed
03  hitl1              completed   0.63s      route: pass -> wave1
04  topic_planning     completed   2.10s      changed fields: topic_registry, phase
05  wave0              completed  18.34s  >   work 6 / attempts 7 / model calls 8
06  wave1              next                   quality: complete
                                               refs: evidence/...  diagnostics/...
-------------------------------------------------------------------------------------------------------
NODE CONTEXT / FILES
node-agent na_07 | initial CAPTURED | model calls 3 | runtime MD MATCH | read /mnt/user-data/workspace | write <virtual-attempt-root>
[Initial Prompt] [Runtime MD] [Request] [Tools & Budget] [Activity] [Workspace] [Outcome & Handoff] [Developer Guide]
workspace/   bundle/b_a81f.../work/   evidence/   final/           selected: evidence/source_003.md
-------------------------------------------------------------------------------------------------------
[Continue] [Step] [Breakpoint: after wave1] [Inspect] [Detach] [Cancel]
> /inspect current
```

这不是最终像素稿，但布局责任固定：

- **Header**：composition、exact Bundle、generation/cursor、drive mode、session posture、next node、
  trace quality、control ownership。
- **Timeline**：按 frame sequence 排列，支持选择；同名 node 的 repair loop 和 HITL 多段不会互相覆盖。
- **Current Boundary / Detail**：当前 frame 或 active visit 的安全事实；内容通过 refs 主动展开。
- **Node Context**：列出该 frame 下 exact bridge/node-agent invocations；每一行展示 captured
  initial prompt/runtime MD/`NodeExecutionRequest`、实际 tool/budget posture、virtual mount manifest、输入/输出
  refs，以及该 invocation 内部 provider/tool calls 的 bounded counts 和 safe outcomes。没有
  node-agent invocation 的 deterministic node 明确显示 `NON-MODEL NODE / NO NODE-AGENT INVOCATION`，
  仍可看 boundary、route、artifacts、Files 和 Developer Guide，但不虚构 prompt。
- **Files / Inspect**：通过 `OperatorWorkspaceReader` 查看挂载 workspace 和 exact Bundle 的授权内容；
  与 `/ls`、`/cat`、`/inspect` 同权，不直接拿 host path。
- **Developer Guide**：通过 node/capability 的 curated source identity 打开当前 `workflow.md` 和源码导航；
  它与 captured runtime context 分栏，始终标明 non-runtime、current source 和 source drift 状态。
- **Control Bar + Composer**：只显示当前 posture 合法的动作；尺寸稳定，不因长卡片上下跳动。

在 80x24 下，Timeline、Detail、Context、Files 变成可切换 views，header 和 control/composer 固定；在
120x40、160x50 下可以并排。无论尺寸如何，Bundle id、posture、trace quality 和主动作不能被挤掉。

## 5. UI posture，不是第二生命周期

下表是 adapter 对 typed runtime projections 的呈现，不新增 persisted workflow state：

| TUI posture | 屏幕重点 | 可用动作 | 禁止的假象 |
| --- | --- | --- | --- |
| WORKBENCH | New Run、validated Attach candidates、Replay history | new/attach/replay/files | 不自动选择 latest |
| BINDING | preflight、正在创建或验证 exact handle | cancel local setup、等待 | 无 Bundle id 时不显示别人的 live trace |
| RUNNING | active node、wall elapsed、最新安全 fact | pause、inspect、files | 不显示 completed，不允许 detach 成功 |
| PAUSE_REQUESTED | running + pause requested | inspect、files、等待 boundary | 不声称 node 内部已中断 |
| PAUSED_BOUNDARY | committed cursor、next node、control owned | step/continue/run/break/inspect/detach/cancel | 不偷偷推进 |
| AWAITING_HITL | exact request、允许的 typed response | answer/inspect/detach/cancel（按 lifecycle） | 普通 debug command 不变成人工回答 |
| BUSY_READ_ONLY | live owner 与 lease posture | inspect/replay/refresh | 不广告 takeover |
| UNCERTAIN | last committed cursor、unmatched active visit | inspect/refresh/recovery status | 不允许 drive，不伪造 failure/completion |
| TERMINAL | completed/blocked/stopped/cancelled、report/diagnostic refs | replay/new run/files | 不把 blocked 叫 completed |
| REPLAY | immutable timeline、quality/gap | select/inspect/files/return | 不显示 mutation controls |

## 6. 一次完整的调试旅程

### 6.1 启动

operator 第一次使用：

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh
```

operator 在第一个 TUI view 选择 Fixture，再进入 Bundle workbench。之后 TUI 显示 composition 和
readiness。fixture 不需要凭证或网络。embedded 模式若缺 model/web
凭证，应在创建 Bundle 前给出明确 preflight failure；失败后仍可返回 workbench，不制造半个 run。

首屏直接是工作台，不先进行泛化聊天。左侧是 New Run，旁边是经过 lifecycle 验证的 Attach 和
Replay 列表。每个 candidate 显示 exact id、phase/posture、更新时间和可用动作；排序只帮助寻找，
不代表选择或接管。

### 6.2 用 Step 开一个新 run

operator 输入研究问题，选择 Start Step，或者敲 `/new --step`。

内部顺序必须是：

1. `open(start)` 创建并验证 Bundle。
2. TUI header 先显示 exact `bundle_id`、generation 和初始 cursor。
3. adapter 再提交一次 `advance_one`。
4. bootstrap 运行时出现 provisional row。
5. bootstrap checkpoint commit 后，row 固化为第一张 TraceFrame，TUI 停在下一 boundary。

若按钮被双击或命令重发，`command_id + expected_cursor` 保证 bootstrap 只提交一次。用户看到的不是
两条重复卡，也不是两个 Bundle。

### 6.3 看第一张卡，并查看 node context 与文件

bootstrap 卡默认只显示 node、outcome、duration、route、next node、changed field names、计数和
observation quality。operator 选择这张卡后，Detail 展开允许公开的 safe facts。

Files 视图能浏览本次 composition 明确挂载且 policy-public 的 workspace 内容，也能通过 validated
Bundle/content ref 进入当前 exact Bundle 的安全 artifacts、evidence 和 report。operator 可以点目录，
也可以输入：

```text
/ls
/ls evidence
/cat evidence/source_003.md
/inspect b_a81f...
```

树视图和命令返回同一内容与同一 denial。Inspect 期间 cursor、next node 和 control lease 都不变。

当选中一个 LLM-bearing frame 时，Node Context 先列出该 frame 内的 bridge/node-agent
invocation rows，包括 worker、critic 和 repair 等分开的 `run_agent` 调用。一张顶层 node 卡可能
关联多个 node-agent invocation，每个 invocation 内部又可能有多次 provider model call 与 tool loop；
这两层不能混成一个“model invocation”，也不能把整个 node 压成一份“node prompt”。选择
exact node-agent invocation 后可以点 tab，也可以手敲。invocation list 使用 bounded
pagination/virtual scrolling，数量增长不能把
所有 refs 塞进 TraceFrame 或撑爆布局：

```text
/context current
/context invocation na_07
/context runtime-md
/context workspace
```

一个完整的 node-agent invocation context 至少呈现：

1. **Identity**：exact Bundle、generation、frame/visit、node、attempt、node-agent ordinal 和 immutable
   context id。
2. **Initial Effective Prompt**：同一个正式 renderer 生成、用于创建 fresh agent 和 seed child
   state 的 exact system policy 与 initial human message；不是 TUI 事后拼接。它精确描述
   node-agent invocation 的初始模型上下文，不声称等于内部每一次 provider call 随 tool result
   演化后的完整消息载荷。
3. **Runtime MD**：实际加载的 base `runtime_policy.md` 与 exact capability `capabilities/*.md`，包括
   capability id/resource、metadata/tool posture、内容 hash 和 captured bytes。base policy 与 capability
   body 进入 system message；capability header metadata 被 runtime 解析/校验，其中 tool posture 被强制
   执行，但 header 不冒充 model-visible text。
4. **Request**：`NodeExecutionRequest.objective`、`expected_output`、source artifact refs、requested tool
   window，以及每项 trusted/untrusted 标识。
5. **Enforced Runtime**：安全的 model/profile label、`policy_name`、最终 eligible tool names、budget、
   structured-output schema identity/version、virtual read roots、write roots 和 exact attempt root。这些是
   deterministic enforcement context，不等于 prompt 里出现了同样的文字；不显示 AppConfig、credential、
   host path 或 handle。
6. **Workspace & Refs**：该 invocation 收到的 virtual mount manifest、输入 refs，以及当前仍可访问的
   artifact/workspace 内容。若 ref 带 hash，显示并校验；当前文件视图明确标 `CURRENT`，不冒充时间点快照。
7. **Inner Activity**：列出该 node-agent invocation 内部的 model-call/tool-call 计数、budget stops、
   tool names/posture 和已批准的 safe outcome facts。v1 不保存每次 provider request/response 的
   完整 raw message history；该部分明确标 `BOUNDED OBSERVATION` 和缺失字段。
8. **Observed Outcome & Handoff**：来自 TraceFrame/Journal/authorized refs 的安全 model/tool facts、final
   structured candidate/ref、validation/repair feedback、deterministic admission owner/result、changed field
   names 和 route。未被 runtime 保留的 raw provider response 或内部消息载荷明确标
   `NOT RETAINED`，不事后重建。
9. **Developer Guide**：当前 node 的 `workflow.md`、prompt builder 和 deterministic owners 导航，明确
   标 `NOT MODEL VISIBLE`。`workflow.md` 是研发 reader projection，不是 runtime-loaded MD。

每个 Context view 顶部还有固定 coverage strip：`INITIAL CAPTURED`、`RUNTIME ENFORCED`、
`ACTIVITY BOUNDED|DEGRADED`、`OUTCOME OBSERVED|UNAVAILABLE`、`FILES CURRENT`。“理解整个 node
上下文”的含义是这些声明过的层次都有类型化来源与完整性状态，不是展示进程内存、
raw State 或一条无边界的消息 dump。任何一层缺失都是可见调试事实，不用空白或
当前源码补齐。

fixture/embedded debugger 中每次已通过 renderer、policy、tool 和 model admission、将进入
fresh agent 的 bridge/node-agent invocation，都必须在 `agent.ainvoke` 之前（因而在第一次 provider
call 之前）成功写入 Bundle-private、versioned `NodeContextSnapshot`，随后才允许进入 agent。
这样 active node 一开始就能 Inspect 初始 context，进程重启后的 Replay 也能看到相同
bytes。capture 或 correlation 失败时，debug run 在第一次 provider call 前明确失败；不能
为了继续跑而退化成事后猜 prompt。如果 capability/tool/model admission 在 snapshot seam 之前
已失败，TUI 显示 `NODE-AGENT NOT STARTED` 和安全的 failure stage/reason，而不伪造 snapshot。

一个 `run_agent` invocation 内的 fresh agent 可以发起多次 provider model calls。v1 的
`NodeContextSnapshot` 只精确保留该 invocation 的初始执行 envelope；内部 provider calls 仅保留
已有计数、budget 和安全 tool/outcome facts，不保留完整 raw message histories。屏幕上必须用
`NODE-AGENT INVOCATION` 与 `INTERNAL PROVIDER CALLS` 两个名称分开它们。

snapshot 中的 exact prompt 可能包含研究问题或其他用户输入，因此它是 Bundle-private sensitive content，
只在 local debugger 对 exact Bundle 主动 Inspect 时打开，并随 Bundle 一起 retention/deletion；默认卡片、
日志、Gateway 和 public result 都不携带这些 bytes。这里排除的是额外混入的 runtime credential、host
identity/path、AppConfig/handle 和 chain-of-thought，不是把模型真实看到的研究输入脱敏后还宣称 exact。

TUI 同时计算 captured runtime MD 与当前 canonical package resource 的 hash：相同显示 `MATCH`，不同显示
`DRIFT`，源文件缺失显示 `CURRENT SOURCE UNAVAILABLE`。DRIFT 时默认仍打开 captured 版本；当前文件只能
作为对照，绝不能替换历史上下文。旧 Bundle 若没有 snapshot，显示 `LEGACY - CONTEXT NOT CAPTURED`，
可以看当前 developer guide，但不能声称还原了当次 prompt。

### 6.4 Step 进入 HITL

operator 按 Step，hitl1 开始。若 node 请求人工确认：

- active row 先显示 running；
- GraphInterrupt/checkpoint 确认后形成 suspended segment；
- TUI posture 变为 AWAITING_HITL；
- composer placeholder 和 typed options 来自正式 pending request，而不是 TUI 自己编 prompt。

operator 输入修订或选择 typed option。Answer 携带 request id 和 expected cursor。hitl1 resume 后，同一
visit id 可以形成 completed segment；原 suspended card 仍保留，human wait 不计入任一 node duration。

当前 real HITL2 是 autonomous continuation，因此 TUI 不显示第二个人工 Answer 控件。未来 runtime
contract 若改变，必须先改主 spec 和 C4a contract，不能由 UI 猜测。

### 6.5 一步一步穿过节点与回环

随后每次 Step 最多提交一个当前拓扑下的 logical node。比如：

```text
topic_planning -> wave0 -> wave0(repair) -> wave1 -> wave2_synthesis
```

第二次 wave0 是新的 frame，不覆盖第一次。operator 能看到 route 从 repair 再到 pass、两次 attempt
数量、各自 duration 和变化字段。卡片默认不倾倒 prompt 或模型输出；operator 主动打开 Node Context
时，可以查看该 node-agent invocation 已捕获的 exact initial effective prompt、内部调用的安全
计数/结果与最终 handoff，但仍不能 raw-dump State、credential、chain-of-thought 或未授权的
完整 model/tool payload。

如果需要内容，operator 通过白名单 detail 或 content ref 打开；如果该内容不允许展示，UI 明确显示
restricted/unavailable，而不是绕过 runtime 去读 checkpoint。

### 6.6 从 Step 切到 Continue 或 Run

当 bootstrap、HITL 和 planning 已经验证过，operator 不必继续逐节点点击：

1. 设置 `/break after wave1`。
2. 按 Continue。
3. driver 用同一 graph、same saver/thread 连续推进。
4. 每个 boundary 仍逐张进入同一 timeline。
5. wave1 commit 后停住，header 显示 PAUSED、next node 和 breakpoint reason。

Continue 尊重当前 stop policy。active session 的 Run 表示没有自定义 breakpoint 的 drive-until，通常
跑到 HITL、failure 或 terminal；Start Run 则是在新 Bundle 上直接使用这一策略。Run 不是另一个
执行循环。

### 6.7 长 node 中请求 Pause

wave1 或 synthesis 可能运行很久。active row 持续显示 exact node、wall elapsed、work/attempt/model-tool
计数和最近安全 fact。operator 按 Pause 后：

- header 立即显示 PAUSE REQUESTED；
- 正在进行的模型或工具调用继续完成；
- 下一 committed boundary 才变成 PAUSED；
- 最终 duration 只计算 invocation active time，不包含 operator 在边界阅读的时间。

这样用户不会因为按钮有响应就误以为底层调用已经被中断。

### 6.8 发现失败时

三种情况必须视觉上不同：

1. **node failed/Bundle blocked**：timeline 固化 failed frame，显示 failure category、last committed
   cursor 和 lifecycle 允许的下一步。
2. **observation degraded**：checkpoint boundary 仍可信，卡片骨架继续出现；缺失的 duration/inner
   facts 标 unavailable，运行控制不被 Journal 缺口重新定义。
3. **uncertain commit**：只有 started 或进程在 node 中死亡，UI 停止 drive，显示 last committed
   boundary 和 uncertain active visit，等待 lifecycle recovery 收敛。

错误不会只作为一行红色日志滚走。operator 可以保持在当前现场 Inspect、看文件、复制安全诊断，
再决定 Detach、Cancel 或 New Run。

### 6.9 Detach、关闭与重新 Attach

正常离开调试现场时，operator 在 committed boundary 选择 Detach：

- debug control lease 释放；
- cursor、checkpoint、ResearchState 和 lifecycle status 不变；
- Bundle 留在原 boundary，下一次 Attach 不自动前进一步。

node 运行中 Detach 不得假成功。正常操作是先 Pause，等 boundary 后 Detach。Ctrl-C 或强制关闭只
代表 presentation/process 消失，不产生 cancel fact；若发生在 node 中，重启后可能先看到 UNCERTAIN。

重新启动 TUI 后：

- live-owned session 只显示 Busy / Read-only；
- control stale 但仍有 live execution exclusion 时仍不可 takeover；
- control stale 且没有 live execution exclusion 时才出现 Attach Control；
- Attach 用 exact generation/cursor CAS，成功后仍停在原 boundary。

### 6.10 到达终态

completed 时，终屏显示 terminal outcome、final frame、report ref、trace quality 和 Bundle id。blocked、
stopped、cancelled 使用各自真实名称。可用动作是 Replay、Files/Inspect、New Run；旧 Bundle 不再被
写成下一次调试实验。

Cancel 与 Detach 明确分开。Cancel 只有 lifecycle 当前允许时出现，确认框显示 exact Bundle；本地
退出和关闭窗口绝不静默 dispatch Cancel。

## 7. 真正把系统调出来的循环

一个典型调试循环是：

1. 用 Start Step 建立第一轮 Bundle。
2. Step 过 bootstrap/HITL，Inspect 每个 boundary，定位第一个错误或高耗时 node。
3. 对已经可信的前段设置 breakpoint，用 Continue 快速穿过，不再机械逐步点击。
4. 在问题 node 前后停住，打开 captured node-agent context，对照 initial runtime MD/prompt、
   request、tool/budget、mount roots、attempt workspace、bounded inner activity、输入 refs、route 和 failure；
   coverage strip 直接告诉你哪一层缺失或 degraded。
5. 查看 Developer Guide，确认 cognitive program 与 deterministic owner 的分界；如果 source status 是
   DRIFT，以 captured context 解释旧 run，以 current source 作为即将修改的对象。
6. 在 boundary Detach；到编辑器里修改代码、prompt、capability 或配置，并跑相应 tests。
7. 回到同一个 TUI，New Run 创建第二个 Bundle，使用同一问题和相同 breakpoint 重新验证。
8. 在 Replay 中切回旧 Bundle，人工对照 frame sequence、captured contexts 和安全事实；v1 不假装已有
   自动 cross-run semantic diff。
9. 局部问题稳定后，以 Start Run 创建最终 Bundle，全速跑到 HITL/failure/terminal。
10. 最终全速 run 仍产生同一种 timeline 和 NodeContextSnapshot，因此验证的不是另一套执行路径。

这里不能从旧 Bundle 任意跳到某 node，也不能改 checkpoint route 来节省时间。要快速到达目标，使用
同一图从头 Run/Continue 到 post-node breakpoint。这个限制换来结果可重放、可比较和不污染。

## 8. 文件系统与 Node Context 的准确边界

“能看到整个挂上的文件系统”在 v1 中精确定义为：TUI 能列出本次 composition 注入的全部 virtual
mount roots 和每个 root 的有效 read/write/none posture，并能遍历其中明确授权给 local operator 的
内容。至少包括当前 runtime 投影的 workspace、uploads、outputs、exact Bundle root 和 active attempt
root；屏幕只显示 sandbox-visible virtual path，不泄露它们对应的 host absolute path。

对研发者而言，以下四个视图必须同时存在，但它们不是同一种 authority：

1. **Mounted Runtime Workspace**：显示 runtime 提供的 virtual mount manifest、alias/readiness 状态、
   `ExecutionPolicy.read_roots`、`write_roots` 和 exact attempt root。Files tree 覆盖 operator-visible 的
   request、work/attempt、evidence、synthesis、review、diagnostics、final、uploads/outputs 等实际内容；
   每个 root/entry 标出 `MODEL READ`、`MODEL WRITE`、`OPERATOR ONLY` 或 `RESTRICTED`，避免“能在 TUI
   看见”被误解为“当时模型也能读写”。最终精确子目录由 store contract 封装，UI 不把示例目录名变成
   写入 API。
2. **Exact Bundle Content**：Bundle/private content 必须先经 lifecycle 验证，再通过 typed projection 或
   content ref 打开；workspace 中看见一个目录名不等于绑定、恢复或取得该 Bundle 控制权。
3. **Captured Node Context**：它不是随便扫描出来的文件。runtime 在 exact
   bridge/node-agent invocation seam 写入不可变、Bundle-private 的 `NodeContextSnapshot`，TUI 通过
   opaque context ref 读取。它回答“该 fresh agent 开始时实际拿到什么”，并保留 exact
   runtime MD/initial messages/request/policy/mount refs 的历史事实；它不声称保留内部每次
   provider call 逐步演化的完整消息历史。
4. **Current Developer Sources**：只允许通过 node registry 和 validated capability ref 打开明确枚举的
   `runtime_policy.md`、exact capability Markdown、该 node 的 `workflow.md` 和源码导航。package source
   仍不挂入 research sandbox；TUI 的 curated source projection 不扩大 node/model 的文件权限，也不是
   arbitrary repository browser。

这一区分来自当前代码和主 spec，而不是 UI 自创概念：

- [`agents/prompts.py`](../../deep_research_harness/src/deerflow_deep_research/agents/prompts.py) 只从 package
  resource 加载 base `resources/node_agent/runtime_policy.md`；
- [`agents/capabilities.py`](../../deep_research_harness/src/deerflow_deep_research/agents/capabilities.py) 按
  validated `NodeAgentCapabilityRef` 加载 exact `capabilities/*.md`；
- [`node_cognitive_control_program.py`](../../deep_research_harness/src/deerflow_deep_research/agents/node_cognitive_control_program.py)
  是正式 initial system policy/human message renderer，runtime bridge 也使用它；
- [`runtime/node_agent_bridge.py`](../../deep_research_harness/src/deerflow_deep_research/runtime/node_agent_bridge.py)
  为每次 `run_agent` 调用构造 fresh agent，以一份 rendered system policy 和 initial human message
  seed child state，再调用 `agent.ainvoke`；该 agent 内部可发生多次 model/tool loop；
- [`domain/context.py`](../../deep_research_harness/src/deerflow_deep_research/domain/context.py) 已定义
  objective/output/capability/artifact refs 与 virtual workspace/attempt roots，
  [`agents/policies.py`](../../deep_research_harness/src/deerflow_deep_research/agents/policies.py) 已定义实际
  tool、budget、read/write roots；
- [`agents/middleware.py`](../../deep_research_harness/src/deerflow_deep_research/agents/middleware.py) 已在运行中维护
  `model_calls`/`tool_calls` bounded counters，但当前 bridge 尚未把它们持久成可 replay 的
  node-agent-context activity facts；
- [`runtime_adapter.py`](../../deep_research_harness/src/deerflow_deep_research/runtime/runtime_adapter.py) 区分
  host paths 与 `/mnt/user-data/workspace|uploads|outputs` virtual roots，host paths 不应进入 UI；
- [`node-agent-reader-interface`](../../openspec/specs/node-agent-reader-interface/spec.md) 明确规定
  `workflow.md` 是 non-runtime reader projection；[`deployment-configuration`](../../openspec/specs/deployment-configuration/spec.md)
  明确禁止把 host package source mount 进 research sandbox。

当前 bridge 只在内存中 render 后构造 fresh agent 并调用 `agent.ainvoke`，尚未持久化
exact initial node-agent invocation context。该 agent 内部可能发起多次 provider call，当前也没有可
支撑“每次 provider call 完整 raw messages 可重放”的持久化 contract。这正是 C3
新增 `NodeContextSnapshot` 的理由；在它落地以前，旧 TUI 或事后 prompt dump 都不能声称已提供历史
node context。

前两种 filesystem scope 由 C3 `OperatorWorkspaceReader` 提供 typed `WorkspacePage`/`FilePreview`/denial；
后两种由 runtime-owned context capture/read interface 提供 typed `NodeContextView`/`NodeSourceView`/denial。
Textual、slash parser 和只读 chat tool 只消费这些 interface，不再各自 `Path.resolve()`、`read_text()`、
load package resource 或重建 prompt。

当前 workspace 与历史 context 的时间语义必须诚实：Files 显示 `CURRENT` 内容；snapshot 显示
`CAPTURED AT NODE-AGENT INVOCATION` 内容。若输入 artifact 有 immutable ref/hash，TUI 可以验证；
若没有，就只显示当时引用与当前文件，不声称保存了整棵 filesystem 的时间点快照。
源码改变后显示 MATCH/DRIFT，历史
snapshot 永远不被当前 resource 覆盖。

以下内容不能因为 TUI 方便就变成 raw file access 或 context capture：

- workspace root 之外的 host filesystem；
- 通过 `..`、absolute path 或 symlink 逃逸得到的路径；
- foreign trusted scope 或其他 run 未标为 operator-visible 的私有内容；
- raw checkpoint database、任意 ResearchState dump；
- AppConfig、sandbox/model/tool handles、外层 identity、secrets、环境凭证和 provider credential；
- chain-of-thought、未通过 redaction/whitelist 的 model/tool payload，以及无限制原始消息历史；
- 未经 registry/ref 枚举的任意 repo/package source 或超出 contract 的二进制/不安全内容。

这类请求返回 typed restricted/unavailable，不返回猜测内容。Files view、slash command、TraceFrame
content ref 和 Node Context 必须经过各自声明的 access/redaction boundary，不能出现“树里看不到但
`/cat` 能绕过”或“snapshot 没有却用当前 prompt 冒充”的差异。浏览另一 run 的 policy-public artifact
仍然只是文件观察，不切换 header Bundle、不改变 TraceReadCursor/BoundaryCursor，也不使
Attach/Continue 变合法。

## 9. 负路径体验

| 场景 | 用户看到什么 | 用户能做什么 | 系统绝不能做什么 |
| --- | --- | --- | --- |
| preflight 失败 | composition/profile 和明确原因；尚无 Bundle | 修配置、返回、退出 | 创建半个 Bundle |
| exact handle 尚未返回 | BINDING/static working | 等待或取消 setup | 扫描 latest 冒充当前 run |
| 双击 Step | 一次成功，另一次 duplicate/stale | 继续使用新 cursor | 多走一个 node |
| 第二个 debugger 打开 | Busy / Read-only + exact owner posture | inspect/replay/refresh | 自动抢 control |
| stale control、live execution | Still busy / in-flight | inspect/等待 | 只看 TTL 就 takeover |
| boundary 后 owner 死亡 | Attach Control candidate | CAS attach | attach 时自动推进 |
| node 中 owner 死亡 | UNCERTAIN + last committed frame | inspect/等待 recovery | 伪造 completed 或允许并发 drive |
| Journal 缺口/eviction | trace degraded、缺失字段显式标记 | 继续看 checkpoint frames | 猜 duration 或补造事件 |
| capability/tool/model admission 失败 | NODE-AGENT NOT STARTED + safe stage/reason | 看 request/guide，修复后新 run | 伪造一份已运行 snapshot |
| debugger context capture 失败 | provider 尚未调用、context capture failed | inspect denial、修复后新 run | 继续调用模型并在事后猜 prompt |
| node-agent 内部 provider 消息未保留 | BOUNDED OBSERVATION / RAW HISTORY NOT RETAINED | 看计数、budget、safe tool/outcome facts | 把 initial snapshot 冒充为每次 provider payload |
| legacy Bundle 无 context snapshot | LEGACY / CONTEXT NOT CAPTURED | 看 trace、current guide、新建 run | 把当前 runtime MD 冒充历史输入 |
| captured MD 与当前源码不同 | SOURCE DRIFT + 两个明确版本 | 默认看 captured，切换 current 对照 | 静默用 current 覆盖 captured bytes |
| workspace 文件在 invocation 后改变 | CURRENT + captured ref/hash（若有） | 查看两者及校验状态 | 声称当前树是完整历史 filesystem snapshot |
| workspace path escape/private file | restricted/unavailable + relative requested path | 返回 Files root | 暴露 host path、secret 或借路径绑定 Bundle |
| checkpoint 损坏/Bundle loss | unavailable | 返回 workbench、新建 run（若合法） | 从 observation 重建 State |
| Cancel | exact Bundle confirmation 与真实 terminal | 确认或返回 | 把 Ctrl-C 当 Cancel |
| Gateway 模式请求 Step | Observer-only denial | replay/observe | 暗中启用本地 drive |

## 10. v1 刻意不提供的体验

- 不在模型调用或 tool call 内部单步，只在顶层 logical-node boundary 停。
- 不原地编辑 State、route、profile、checkpoint 或 evidence ledger。
- 不从历史 Bundle 中间 fork；未来若做，必须创建有 lineage 的新 Bundle。
- 不自动做 cross-run semantic diff；v1 通过 Replay 切换人工比较。
- 不把 TUI 做成源码/prompt 编辑器；编辑发生在正常开发工具中。
- 不捕获或展示模型 chain-of-thought，也不保存无限 raw message/tool-result history。
- 不声称 `NodeContextSnapshot` 是每次内部 provider call 的完整消息快照；它是每次
  bridge/node-agent invocation 的 exact initial execution envelope。
- 若将来确实需要逐 provider-call payload replay，必须另立 change 定义 capture seam、bounded
  schema、sensitive-content access、retention/deletion 和未知版本行为；不能在 C3/C4b 中暗中扩张。
- 不承诺整棵 workspace 的 point-in-time copy；精确历史只覆盖 snapshot 与 immutable/hash refs 声明的内容。
- 不把当前 `workflow.md` 当 runtime prompt，也不把 package source mount 进 research sandbox。
- 不承诺无限 L3/L4 历史；Journal bounded 时明确 degraded。
- 不给 Gateway/public reflected tool 增加远程 debug mutation。
- 不制造 HITL2 人工输入；当前 real HITL2 保持 autonomous continuation。

## 11. 体验承诺与计划追踪

| 目标体验 | 支撑 contract / plan 任务 | Gate | 是否闭环 |
| --- | --- | --- | --- |
| 一个 executable `.sh` 进入 chooser/fixture/embedded | C4b launcher + entry tests + readiness + docs | C4b | 是 |
| New/Attach/Replay 可点也可手敲且语义相同 | C4b typed action normalization + Pilot equivalence | C4b | 是 |
| 首条 live row 前出现 exact Bundle | C0 exact correlation；C4a start admission | C0 + C4a | 是 |
| Start Step 首次只提交 bootstrap | C4a fixed start composition + duplicate guard | C4a | 是 |
| timeline live/replay 同构 | versioned TracePage、TraceReadCursor、checkpoint/Journal projector | C3 | 是 |
| Step/Continue/Run 同一 graph | DebugRunDriver、interrupt_after、drive_until、topology guard | C4a | 是 |
| post-node breakpoint 与 pause | DebugSession stop policy、next-boundary pause | C4a + C4b | 是 |
| running/committing/uncertain 诚实区分 | ActiveVisitProjection + recovery matrix | C3 + C4a | 是 |
| HITL 多段、typed answer、不覆盖卡片 | TraceFrame identity + existing response correlation | C3 + C4a + C4b | 是 |
| 每次 bridge/node-agent invocation 的 exact initial context 可 live/replay | C3 versioned `NodeContextSnapshot` + bridge-seam capture + opaque context ref | C3 | 是 |
| node-agent 内部 provider/tool 活动可见且不冒充完整历史 | C3 bounded counts/safe facts + explicit NOT_RETAINED quality | C3 + C4b | 是，按 v1 边界收窄 |
| runtime MD、initial messages、request、tool/budget/mount posture 可审查 | C3 `NodeContextView` field contract + C4b Context tabs/commands | C3 + C4b | 是 |
| captured runtime MD 与 current source 不混淆 | C3 captured hashes/bytes + curated source projection + MATCH/DRIFT/UNAVAILABLE tests | C3 + C4b | 是 |
| `workflow.md` 可见但明确 non-runtime | C3 `NodeSourceView` registry + C4b Developer Guide label | C3 + C4b | 是 |
| Files view 与 `/ls`/`/cat` 同权 | C3 `OperatorWorkspaceReader` + C4b thin adapters + path/privacy negative tests | C3 + C4b | 是 |
| 全部 runtime virtual mounts 与 effective roots 可见 | C3 mount manifest projection + host-path/secret negative tests | C3 | 是 |
| Detach 不等于 Cancel 或进程退出 | C4a detach contract + C4b confirmation/exit UX | C4a + C4b | 是 |
| busy/stale/attach 不并发推进 | control lease + execution exclusion/fence + CAS cursor | C4a | 是 |
| terminal 后 Replay 或 New Run | C3 replay + C4b terminal workbench | C3 + C4b | 是 |
| 调试后用新 Bundle 全速复验 | real validation 的 Step run + second Start Run | 终线 | 是 |
| 小中大终端不重叠 | C3/C4b Textual Pilot at 80x24、120x40、160x50 | C3 + C4b | 是 |
| Gateway 明确 observer-only | adapter capability matrix + typed denial | C4b | 是，按边界收窄 |

本次 UX 审阅发现的原计划缺口已经回填到当前 plan：executable `.sh` launcher、首屏三入口、Start Step/Run
首步语义、breakpoint set/clear、composer typed routing、button/command equivalence、C3
`OperatorWorkspaceReader`、bounded Files view、required `NodeContextSnapshot`、Runtime MD/Workspace/Developer
Guide 分层、源码漂移、Detach/Cancel 区分，以及 terminal 后 Replay/New Run。

## 12. 必须跑通的 UX 验收剧本

C4b 归档和 real validation 不能只看静态截图。至少跑通以下一条 fixture 自动旅程：

1. 从任意 cwd 运行 canonical `.sh`，选择 Fixture 并进入 WORKBENCH；`--help` 显示等价手敲命令，
   launcher 没有扫描 workspace 或执行 lifecycle mutation。
2. Files view 列出 composition 注入的全部 virtual mounts、effective read/write roots 和 active attempt root，
   并正确标 MODEL READ/WRITE、OPERATOR ONLY、RESTRICTED；`/ls` 返回同一授权根，`/cat` 与选择 preview
   等价。屏幕和 snapshot 均不出现 host path/runtime credential。
3. 用 `/new --step` 开 run；首条 running row 前 header 已有 exact Bundle。
4. bootstrap 只形成一张 committed frame。
5. Step 到 HITL1 suspended，提交 typed answer，保留 suspended/completed 两段。
6. fixture 载入一组经正式 writer/reader contract 生成的 LLM-bearing context cases；另由 focused
   renderer/bridge/provider-spy test 证明 `NodeContextSnapshot` 在 `agent.ainvoke`/首次 provider call 前已提交。
   Context view 中 exact initial system/human messages、base/capability MD、request、tool/budget、mount roots
   与正式 inputs byte-for-byte 或 typed-value 等价；一个多 node-agent-invocation node 不发生覆盖。
   再用一个内部多 provider-call 用例证明只产生一份 initial snapshot，而调用计数/安全事实
   正确更新，屏幕明示 raw histories `NOT RETAINED`。
7. Context 的 Developer Guide 能打开当前 `workflow.md`，且始终显示 NOT MODEL VISIBLE。修改当前
   capability fixture 后旧 snapshot 仍不变并显示 DRIFT；legacy/no-snapshot 显示 unavailable，不重建。
8. Inspect frame、context、workspace 和 content ref 不改变 cursor；path escape/private file 被拒，浏览
   另一 run 的 policy-public artifact 不改变当前 Bundle/cursor/control。
9. 设置 post-node breakpoint，Continue 命中；随后 Run -> Pause -> Step。
10. 在 running 状态尝试 Detach 得到 busy；到 boundary 后 Detach 成功且无 cancel fact。
11. 重启 TUI，Attach 同一 exact Bundle，不自动推进；旧 owner generation 被 fenced。
12. 继续到 terminal，Replay 得到与 live 相同的 frame sequence 和 captured context bytes。
13. New Run 创建第二个 Bundle，以 Start Run 到 terminal；第一个 Bundle 仍只读可 Replay。
14. 同一路径在 80x24、120x40、160x50 下无重叠、主状态、Context tabs 和控制不丢失。

真实验收再用 embedded composition 完成同样的关键动作，并抽查 TraceFrame、NodeContextSnapshot、
checkpoint、Journal、lifecycle、runtime renderer/bridge inputs 与屏幕叙述一致。任何一项只能靠 UI
推断、latest Bundle、current-source prompt reconstruction、raw State dump 或人工脑补成立，都不能宣布
目标 UX 已落地。

## 13. 支撑结论

按当前 plan 完成 C0 -> C3 -> C4a -> C4b -> real validation 后，本文描述的 local fixture/embedded
体验有逐项 contract 和 falsifiable acceptance 支撑：研发者能从 exact boundary 下钻到 captured
node-agent context，把 initial inputs/cognitive program、runtime enforcement、bounded inner activity、outcome/handoff、
current workspace/developer guide 串成一条可诊断链路，并清楚知道每条信息的时间、可见性
和完整性。内部 provider raw message history 未保留时会明示缺口，不会用 initial snapshot 冒充。
它没有要求第二张 graph、TUI 私有 lifecycle、arbitrary State
mutation、research sandbox source mount 或 Gateway 扩权。

结论中的“支撑”是实施门，不是对当前代码的能力声明。C0-C4b 任一 gate 未归档，或上述验收剧本
有一步失败，最终体验就仍未成立。允许收缩成 observer/replay TUI，但不允许用 presentation 假装
debugger 已经完成。
