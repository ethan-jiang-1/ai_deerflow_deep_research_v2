# TUI Workflow Debugger Grounding Review

> 类型: 冻结的设计审阅与证据底稿
> 日期: 2026-08-31
> 当前执行权威: [`../tui_step_progressive_plan.md`](../tui_step_progressive_plan.md)
> 作用: 给没有历史上下文的实现者解释当前 plan 的事实来源、纠错理由和边界选择。
> 状态: 冻结。新的实施结论进入当前 plan 的进展记录或对应 OpenSpec change，本文不追写。

## 1. 审阅结论

需要建设的是一个本地 contributor/operator workflow debugger，而不是继续扩张一个展示型
Textual demo。它应当用同一张真实 StateGraph 完成运行、单步和恢复，并把运行事实投影成可回放
的安全 trace。Textual TUI 是主要 presentation adapter，但不是执行、路由、生命周期或事实权威。

原 progressive plan 的方向有价值，但不能按原稿直接实施，原因如下：

1. `RunEvent` 的持久化模型拒绝 wrapper 已经产生的 `suspended` outcome，归档 change
   `add-suspended-run-recovery` 的 REJ-011 没有穿过真实 store 得到验证。
2. TUI live progress 仍扫描 workspace 并选择最近更新的 active/suspended Bundle，可能把别的 run
   当成本次 run。
3. 现有 `ContinueRun` 是孤儿 Bundle 的跨进程接管并运行到自然终态，不能承载 debugger
   `continue` 的 breakpoint 语义。
4. 原计划把 `step` 和 `continue` 都定义成“下一个边界”，两个操作没有行为差异。
5. 相邻 checkpoint 时间差会包含 operator/HITL 停留时间，不能作为 node duration。
6. 泛化的 `input_summary` / `output_delta` 会泄露或误述 checkpoint 内的 profile、evidence、
   messages 和其他状态值。
7. capability 事实存在于模型调用请求，不存在于通用 node boundary；由 checkpoint 或 phase 推断
   capability 会制造伪因果。
8. TUI 的历史身份在 Primary User UI、非产品 visualizer、recon chat 和 debugger 之间漂移；
   继续把 runtime 逻辑堆进单文件会扩大漂移。

因此当前 plan 改为：`C0 observation truth -> C3 trace projection -> C4a headless debug driving ->
C4b TUI command adapter -> real validation`。C3 拥有观察 contract 和只读 trace/replay 呈现，C4a
拥有运行控制，C4b 只把 mutation commands 接入 Textual，不新增 runtime 语义。

## 2. 审阅范围与约束

审阅了以下范围：

- `_backlog/plans/tui_step_progressive_plan.md`
- `_backlog/plans/archive/tui-interactive-campaign*.md`
- `deep_research_harness/scripts/demo_tui.py`
- `deep_research_harness/scripts/experiments/tui_trace.py`
- `deep_research_harness/src/deerflow_deep_research/{domain,runtime,graph,agents}` 中与 run、
  observation、checkpoint、node wrapper、capability 有关的模块
- `deep_research_harness/tests/` 中对应的 unit/integration/graph tests
- `deep_research_harness/docs/` 中 TUI ADR、run lifecycle walkthrough、README
- `openspec/specs/` 中 run event、demo TUI、HITL、Bundle lifecycle 等当前主 spec
- 相关 git 历史：TUI live progress、recon loop、streaming interaction、suspended recovery、
  progressive plan 的提交链

遵守仓库边界：没有阅读或修改 `deerflow/` 源码；只使用本应用已经依赖的框架接口和本仓证据。
本轮没有修改 runtime 代码或 OpenSpec spec。

## 3. 用户目标的精确定义

用户所说“像传统软件开发 debug，一步一步把 agentic workflow 调对，也能串起来跑”，在本应用
中应解释为：

- 同一真实 StateGraph 和 Bundle lifecycle 同时支持自动运行与边界步进。
- 每个顶层 logical-node visit 有一张可信卡片；work unit、attempt、模型和工具调用作为更细的
  只读叙述。
- operator 能在边界 step、continue、inspect、请求 pause，并在正式 HITL interrupt 上 answer。
- 进程死亡后从 exact Bundle 的 durable checkpoint 恢复，不猜测当前 run。
- live narration 和 historical replay 使用相同的 trace schema 与 projector。
- 调试改变运行节奏和观察深度，不授予 TUI route/profile admission 或任意 State 写权限。

第一版不支持原地编辑 checkpoint。未来如确需“改 State 后继续”，必须创建带 parent cursor 和
lineage 的新 debug Bundle；原 Bundle 保持不可变，以便重放和比较。

## 4. 历史重建

### 4.1 身份漂移

`docs/adr/0002-tui-is-the-primary-user-interface.md` 最初把 dedicated TUI 定义成 Primary User
界面；其 2026-08-13 postscript 又明确该路线 dormant，当前产品入口转为 Dedicated Agent 与
reflected tool。`docs/adr/0008-start-with-a-local-first-tui.md` 对 local-first product TUI 也作了
相同 dormant 标注。

当前 `deep_research_harness/README.md` 把 `Demo TUI visualizer` 定位为 contributor/operator，
并明确“Not a current Primary User TUI”。`openspec/specs/research-demo-tui/spec.md` 同时规定它是
bounded、non-product demo。

之后 TUI 经历了以下扩张：

1. live progress 和报告路径；
2. recon loop、workspace inspect、natural-language chat tools；
3. streaming chat、rolling event feed、semantic feedback；
4. orphan attach 和 suspended recovery；
5. proposed node-boundary step debugger。

结果是 `scripts/demo_tui.py` 已有 1817 行，`tests/integration/test_demo_tui.py` 已有 1295 行。
一个文件同时承载 demo、recon workbench 和 debugger，会让 presentation 继续拥有不属于它的
runtime 知识。当前 plan 因此把长期身份固定为本地 operator debugger，并要求 runtime-owned
deep modules 隐藏复杂度。

### 4.2 战役真正暴露的问题

020 战役的困难主要不是 Textual layout，而是运行身份、事实相关性和恢复：

- 旧 launcher/runbook 曾用 mtime-latest Bundle 作为本次证据，审阅后已明确禁止。
- 真实运行发生网络中断和进程死亡，留下 suspended/orphan Bundle，推动 C2 recovery change。
- TUI 在 graph dispatch 期间拿不到一个可直接消费的 exact live handle，于是重新出现
  “最近 active Bundle”扫描。
- attach 已能把 operator 选择路由到生命周期恢复，但现有恢复命令会自动跑向终态，并不是
  debugger pause/continue。

这说明 solid TUI 的前置条件是 debugger protocol，而不是更多卡片或更多聊天能力。

## 5. 代码与契约发现

### 5.1 `suspended` Journal 契约没有落到真实持久化

证据链：

1. `graph/builder.py::_node_wrapper` 捕获 `GraphInterrupt` 后调用 `_record_node_event(...,
   outcome="suspended")`。
2. `domain/run_observation.py::RunEvent.outcome` 仅接受 `started | completed | failed`。
3. `runtime/run_observation.py::_bundle_record_event_sync` 使用该模型构造真实事件，因此
   `suspended` 触发 Pydantic `ValidationError`。
4. `RunObservationStore.record_event` 为了保证 observation 不影响 graph，会捕获该错误、记录
   persistence failure 并返回，所以 run 不一定失败，但 `suspended` 事件没有持久化。
5. `_record_node_event` 的另一条 observation projection 只认三种 outcome，其他值映成
   `failed`，因此 suspension 还可能被错误叙述为 failure。
6. `tests/graph/test_node_wrapper.py::_JournalRecorder` 只把任意 kwargs 放入 dict；REJ-011 测试
   没有穿过 `RunEvent` 或真实 store，所以产生假绿。

直接构造真实 `RunEvent(outcome="suspended")` 的最小校验得到 ValidationError，错误含义为
outcome 必须是 `started`、`completed` 或 `failed`。

影响：checkpoint/lifecycle 仍可能正确识别 suspended，不能据此声称整个 recovery 已坏；但
debugger 所需的 Journal causal fact 不可信。C0 必须先修复，并用 wrapper -> real recorder ->
store -> reader 的测试闭环替代 fake-only 证明。

### 5.2 live progress 仍是 latest 假相关

`scripts/demo_tui.py::_latest_active_bundle` 扫描所有 scope，读取每个 Bundle 的
`run-summary.json`，过滤 active/suspended，再取 `updated_at` 最大值。
`live_progress_lines` 随后读取该 Bundle 的 `diagnostics/events.jsonl`。

这不是严格意义的 mtime，但因果错误相同：最近更新不等于当前 dispatch 创建的 Bundle。两个并发
run、历史 suspended Bundle 被恢复、启动前失败，都可能串包。

正确规则：

- attach 列表可以按时间排序，因为它只是候选展示；
- 一旦 start/attach 被选择，所有 live/replay/command 必须绑定 exact `bundle_id`；
- 在 exact id 尚不可用时显示“trace 尚未绑定”，不能回退扫描 latest。

### 5.3 现有 `ContinueRun` 语义不可复用

`domain/run_experience.py::ContinueRun` 的文档和字段表明它是接管 recoverable orphan Bundle。
`runtime/bundle_graph.py::BundleGraphExecutor.continue_run` 在 execution exclusion 内打开原
checkpoint，执行 `graph.ainvoke(None)`，然后投影结果并继续到自然 terminal。

Debugger `continue` 则需要 stop policy。若复用同一 `kind="continue"`：

- shared `RunIntent` 将同时表示两种不兼容行为；
- UI label、持久化恢复和远端调用无法判断 operator 意图；
- 未来兼容性和错误恢复变得不可审计。

结论：保留现有 `ContinueRun` 和 REG-023 不变；debugger 使用独立本地 `DebugCommand`，其中
`drive_until` 才对应 UI 的 continue。

### 5.4 原 `step` / `continue` 定义重复

原 plan 把二者都写成推进到“下一个节点边界”。传统 debugger 的非重叠语义应为：

- `step`: 尝试提交一个顶层 logical-node visit，遇到正式 HITL/failure/terminal 则提前停止；
- `continue`: 从当前 boundary 运行到显式 breakpoint、HITL、failure 或 terminal；
- `run`: 新建 run 时进入自动模式，或在无自定义 breakpoint 时持续 drive；
- `pause`: 若某 node 正在执行，只请求在下一个 committed boundary 停止；
- `inspect`: 纯读，不改变 cursor；
- `answer`: 只提交现有 typed human response，不构造 route 或伪造 continuation。

LangGraph 的 durable commit 单位是 checkpoint/superstep。当前顶层图每个 superstep 只出现一个
logical node visit；C4a 应增加 topology guard。若将来出现顶层并行 fan-out，必须显式决定 step
表示“一整个 superstep”还是引入新调度，不能悄悄改变行为。

### 5.5 checkpoint 时间差不是 node duration

`scripts/experiments/tui_trace.py` 能读取每个 checkpoint 的 `created_at`。相邻值在无人暂停的
自动 run 中可作为粗略 wall-clock 间隔，但在 step/HITL 模式会包含：

- operator 阅读卡片的时间；
- 等待输入的时间；
- debugger 暂停到下一命令之间的时间；
- 进程死亡后的停顿。

因此原 E2“相邻差分即耗时”结论撤销。正确事实应由 node wrapper 在一次实际 invocation 内用
monotonic clock 测量，并随 completed/suspended/failed outcome 记录。相邻 checkpoint 时间可作为
`boundary_elapsed` 或审计时间显示，但不得标成 node duration。

### 5.6 泛化 State diff 既泄露又失真

checkpoint 包含 request、profile、work/evidence、messages、artifact refs 等状态。自动把所有变化值
转成 `input_summary/output_delta` 会：

- 暴露原问题、个人偏好、来源内容或模型文本；
- 把 reducer、派生字段和 checkpoint serialization 差异误称为 node 输出；
- 让 TUI 对 State schema 获得隐式依赖。

v1 TraceFrame 应使用闭集安全事实：node、visit/sequence、outcome、route/next、changed field names、
work/attempt/model/tool counts、显式 duration、budget summary、failure category、terminal disposition 和
observation quality。内容只通过 node-specific whitelist 或已授权 artifact/content ref 显式 inspect。

### 5.7 capability attribution 必须写在模型调用 seam

`domain/context.py::NodeExecutionRequest.capability_ref` 是模型调用的真实 capability 来源。
node boundary 只知道 logical phase；一个 node 可能有多个调用和多个 capability。当前
`runtime/node_agent_bridge.py` 的 Journal 记录侧主要收到 `NodeAgentContext`、attempt 和 call ordinal，
不能由 phase 安全还原 capability。

结论：L2 node card 只展示 node/phase。L4 若展示 capability，必须在 bridge 接收
`NodeExecutionRequest` 的调用 seam 写入显式 redacted fact；不得从 checkpoint、文件名或 node 名推断。
这会扩大 observation change 的 causal owner，宜作为独立可选增量，不阻塞基础 C3/C4a/C4b。

### 5.8 lifecycle walkthrough 已漂移

`docs/run-lifecycle-walkthrough.md` 仍把 HITL2 描述为第二个人工停点。当前主 spec 和
`graph/nodes/hitl2/node.py` 明确 real HITL2 是 autonomous continuation，不产生 human prompt。

影响：TUI 和 debugger 的执行语义必须取自当前 spec/domain/runtime，不得以 walkthrough 或归档
战役描述作为执行权威。文档漂移应在相关 change 中顺带修正或单独登记，但不能让 C3/C4重新发明
HITL2 输入。

### 5.9 Journal bounded retention 限制历史 trace

`domain/run_observation.py::MAX_EVENT_RECORDS` 是 256。`RunObservationStore` 达到容量后按 priority
evict，保留 admission、terminal、validation/failure/retry/exhaustion 等 anchors，普通 node
start/success 和普通 model/tool facts 的 priority 最低。manifest 会记录 dropped count/interval，
inspection 将 Journal 标为 incomplete。

这意味着：

- checkpoint 仍能证明顶层 committed boundaries、route/next 和最终 State posture；
- Journal complete 时，duration、attempt 和内层 facts 可与 boundary 对齐；
- 容量或持久化缺口后，projector 不能承诺完整 L3/L4 replay，也不能用 checkpoint 猜 duration；
- live 时曾看到、后来被 retention 淘汰的内层事件，不能在历史界面中继续冒充 durable fact。

C3 应在现有 Journal 内提高 finalized node fact 的 retention priority，使典型 10-20 node run 的
边界 metadata 比普通 start/model-tool success 更稳定；仍超容量时明确 degraded。v1 不为追求无限
trace 再造第二个生命周期 Journal。

### 5.10 HITL resume 会复用 node visit id

`domain/lifecycle.py::make_node_visit_id` 用 `execution_trace` 中已经完成的同名 node 次数生成
`g{generation}-{phase}-a{n}`。GraphInterrupt suspension 不把 node 写成 completed visit，因此下一次
resume 会再次得到同一个 visit id。

所以 `visit_id` 不能作为 TraceFrame 唯一键，也不能把 suspended 当成该 visit 永久唯一的最终卡。
正确模型是 node invocation segment：同一 HITL visit 可先有一至多张 suspended segment，再有
completed segment。committed/suspended frame identity 使用 checkpoint identity；没有 checkpoint 的
failure 使用失败 event sequence。每段显式 duration 相加可得到 active execution time，段与段之间的
人类等待不计入。

### 5.11 Journal completed 不是 checkpoint commit

`graph/builder.py::_node_wrapper.run` 在 node body 返回 dict 后立即记录 node `outcome="completed"`，
之后才验证 work-unit/gate views、执行 gate、合并 update 并 return；LangGraph checkpoint commit 更在
return 之后。若 gate validation 或 checkpoint 前路径失败，Journal 可能出现 started -> completed ->
failed，但没有新的 committed checkpoint。

因此 projector 不得把 node completed event 直接画成 completed boundary。checkpoint 是 commit
authority：

- completed/suspended fact 与新 checkpoint 对齐后，才生成 committed frame；
- completed fact 已有但 checkpoint 尚不可见时显示 `ActiveVisitProjection(committing)`；
- 随后出现 failure 且无 checkpoint 时，只生成 failed frame，可把 node-body-completed 作为子事实；
- 进程消失且既无 checkpoint 又无 failure 时显示 uncertain commit，不猜 completed。

增量 reader 因而需要同时跟踪 checkpoint position 与 Journal high watermark 的 opaque
`TraceReadCursor`；只有 `after_event_sequence` 会漏掉“Journal 写失败但 checkpoint 已提交”的边界。

### 5.12 Intentional debug pause 目前会被看成 orphan

`BundleGraphExecutor._project` 只把 `pending_from_snapshot(snapshot)` 非空的 checkpoint 投影成 human
suspension。`interrupt_after` 的普通 node boundary 没有 pending human request，
`BundleLifecycle.sync_graph_progress` 因而保留 active state；`result_for_state` 又把 active + no pending
定义为 process-death orphan，给出 `legal_next_action=RESUME`。

E4 只证明 graph/checkpointer mechanics，没有证明 Bundle lifecycle 能区分“debugger 有意停在边界”与
“进程已经死亡”。若每步释放 `execution_exclusion` 后没有其他 ownership，现有 natural
`ContinueRun` 或第二进程可以在 operator inspect 时接管并跑向终态。

推荐最窄修复不是新增 public `LifecycleStatus.PAUSED`，也不是伪造 pending input，而是 C4a 增加
Bundle-local、runtime-owned、expiring debug control lease：

- open(start/attach) 原子取得并 heartbeat；
- pause 间保留 control lease，但每个 node 只短暂取得 execution exclusion；
- natural resume 和其他 writer 尊重 live lease，observer inspect 不受阻；
- attach candidate 把 live-owned pause 投影成 busy/read-only；只有 control lease stale 且没有 live
  execution exclusion 时才广告 takeover；
- detach/terminal/cancel 主动释放；进程死亡后按上述双条件 + exact generation/cursor CAS takeover；
- DebugSession 投影 paused-at-boundary，ResearchState/lifecycle status 仍由原 owner 决定。

该 lease 是新的 private cross-process control surface，C4a 必须定义 owner、generation、TTL/heartbeat、
stale detection、takeover、旧 owner fencing 和 recovery evidence。它与现有短期
`execution_exclusion` 语义不同：可以复用 coordinator 的实现模式，不能把同一执行锁跨 operator
pause 长期持有。每次 invocation 的 execution fence 必须覆盖 node body 到 checkpoint commit，并在
长调用期间保持 live/renewed；TTL 到期本身不能授权第二 writer。状态有歧义时只读，不能 takeover。

## 6. 最小实验 E4

### 6.1 方法

使用 fixture graph、`InMemorySaver` 和临时目录，不修改仓库文件，不访问真实模型或网络。实验依次：

1. 用 `interrupt_after=LOGICAL_NODES` 启动；
2. 从第一个 boundary 用 `ainvoke(None)` 继续；
3. 到 HITL1 后提交 typed resume；
4. 在同一 saver/thread 上切回普通连续调用；
5. 检查 snapshot.next、checkpoint 和最终 terminal。

### 6.2 结果

- start 后 bootstrap 提交并暂停，`next=hitl1`；
- step 进入 HITL1 自身 GraphInterrupt，bootstrap 没有被误记为 hitl1 完成；
- typed resume 后 hitl1 完成，并在 `next=topic_planning` 再次暂停；
- 同一 saver/thread 随后切回连续运行并完成；
- 同一 compiled graph 可以逐次调用时传 `interrupt_after`，不需要 compile 两种 graph 语义。

### 6.3 已证明与未证明

已证明：node-boundary interrupt、HITL1 内部 interrupt、typed resume、step -> run 切换在最小 fixture
路径能共存。原计划“步进/连续不能共用同一 config 混跑”被反证。该实验不要求 compiled object
跨进程常驻；正式要求是同一 recipe/compile path 和 durable saver/thread，restart 可重新 compile。

尚未证明：

- refinement 的 `snapshot.tasks` 恢复；
- 进程重启和 stale execution lease；
- 两个 operator/进程同时推进；
- node 执行中死亡后的 started-without-outcome 叙述；
- 未来顶层并行 topology；
- 真实模型长调用期间的 pause 请求。

这些是 C4a 的硬验收，不应再靠 spike 注释代替。

## 7. Authority 与 surface 分级

| 事实或动作 | authority / owner | consumer | 兼容策略 |
| --- | --- | --- | --- |
| route、State、node commit | StateGraph + Bundle lifecycle | runtime、projector | 保持现有主契约；TUI 无写权 |
| durable boundary cursor | checkpoint + exact Bundle identity | driver、projector | 从现有 checkpoint 投影，不复制第二份 authority |
| intentional debug-boundary ownership | runtime expiring debug control lease | driver、lifecycle mutation admission | private cross-process surface；generation/TTL/fencing 明确，不写 ResearchState |
| node/model observation facts | runtime Journal writers | projector、diagnostics | persisted schema；新增值必须 reader 兼容并有真实 store 测试 |
| `TraceFrame` | runtime trace module | TUI、headless tests、未来 adapter | 新的 versioned cross-boundary interface；闭集字段 |
| debug commands | local runtime debug module | Textual adapter、fixture tests | 新的 local-only interface；不进入 reflected public tool |
| UI selection/layout | Textual adapter | operator | adapter-private，可自由演化但不得推断 lifecycle |
| orphan natural resume | 现有 `ContinueRun` / REG-023 | shared experience | 原样保留，不与 debugger continue 合并 |

Persisted `RunEvent` 接受新增 `suspended` 后，新代码仍可读取旧事件，旧 Bundle 不需要重写；但
预变更代码会拒绝新写入的 suspended event，因此这不是双向兼容。C0 必须枚举并同步切换本应用
所有 readers/writers，声明本地 coordinated cutover 与 rollback 限制，同时遵守 REJ-011 对既有
字段/schema version 的要求。`TraceFrame` 从 v1 开始版本化，未知版本 fail closed。

Checkpoint 是 committed boundary/order/route 的 fact authority；Journal 是 bounded causal-detail
authority。Projector 可以在 Journal incomplete 时从 checkpoint 保留边界卡片骨架，但必须让
duration/inner facts 缺失并标 degraded，不能把两种来源说成互相替代。

## 8. 推荐的 deep modules

### 8.1 `RunTraceProjector`

这是工作名，不预先锁死最终类名或文件名。按现有代码 pattern，adapter-facing contract models
可归 domain，I/O/投影 implementation 归 runtime；TUI script 不拥有二者。

外部 interface 只需：

- 接收已经由 Bundle lifecycle 验证的 Bundle ref 和可选 opaque `TraceReadCursor`；
- 返回 versioned、分页、redacted `TracePage`；
- 对 live 和 replay 使用同一投影规则；
- 把缺失、损坏或无法关联表示成显式 quality，不推断成功。

这里的 live 只表示增量读取一个 caller-supplied exact Bundle；projector 不启动 graph，也不扫描
workspace 获取 handle。C3 可用已知 Bundle 做 headless live/replay 等价测试；当前 TUI 的 early
start handle 由 C4a driver 闭环，在此之前 UI 宁可显示 static working。

一张最终 node card 对应一个 committed/suspended boundary 或 non-committed failed segment。有
checkpoint 时以 checkpoint identity 唯一标识；无 checkpoint 的 failure 用失败 event sequence；
visit id 只关联 HITL suspend/resume 多段。projector 单独返回
`ActiveVisitProjection(running | committing | uncertain)`，只有 commit/failure 确定后才转成 card。
这样长 node 有实时反馈，也不会把 pre-checkpoint completed 当成 boundary。`pause_requested` 是 C4a
debug session control projection，不写入 Journal/TraceFrame；TUI 只并列渲染两个 typed projections。

复杂的 checkpoint serde、Journal 对齐、field whitelist、sequence 校验和 gap detection 隐藏在
implementation 内。当前 `scripts/experiments/tui_trace.py` 接受任意路径、compile graph 和直接开
SQLite，只是 spike，不能升级成正式 interface。

### 8.2 `DebugRunDriver`

这也是工作名。contract models 可归 domain，driving implementation 归 runtime；它可以在
`BundleGraphExecutor` 背后或相邻 module 实现，但 interface 必须与现有 `ContinueRun` 分离。

外部 interface 保持小：

- `open(start | attach) -> DebugSessionSnapshot`
- `execute(DebugCommand) -> DebugSessionUpdate`

`DebugCommand` 是 closed union，包含 advance-one、drive-until、pause-request、typed-answer 和 cancel；
每个 mutation command 都带 exact bundle、`expected_cursor` 和 `command_id`。graph compile/config、
execution lease、checkpoint reopen、stop policy 和 stale-cursor denial 都隐藏在 implementation 内。

`DebugRunDriver` 不成为第二 lifecycle owner。它只通过现有 Bundle lifecycle 和 graph recipe 驱动
真实图。删除该 module 时，复杂度会重新散到每个 adapter，因而它是有深度的 module，而不是
pass-through。

intentional boundary pause 期间，它持有可过期 debug control lease，而不是长期占用
`execution_exclusion`。所有 writer admission 都尊重该 lease；observer inspection 不受阻。进程死亡后，
只有 control stale 且没有 live execution exclusion 才能 CAS takeover；旧 owner 通过 generation
fencing 失去写权。一次执行跨过 control TTL 时，仍由 live/renewed execution fence 阻止第二 writer。

## 9. Negative paths 与恢复闭环

| 场景 | 检测 | 行为 | 完成证据 |
| --- | --- | --- | --- |
| 未拿到 exact Bundle | session 无 verified handle | trace/drive fail closed；可显示静态 working | 没有读取其他 Bundle |
| 双击 step | 相同 command id 或 stale cursor | 最多一个 commit；另一请求返回 typed duplicate/stale | cursor 只增加一次 |
| intentional boundary pause | live debug control lease | natural resume/第二 debugger busy；observer 可读 | operator inspect 时无外部推进 |
| 两进程推进 | control lease + execution exclusion + expected cursor | 只有 owner 可取 execution lease；其他 writer fenced | 无双 node visit |
| 长 node 跨 control TTL | live/renewed execution fence | 第二进程保持 busy/read-only；TTL 单独不授权 takeover | 无并发 commit |
| boundary 后进程死 | durable checkpoint + expired control lease + no live execution exclusion | CAS takeover 后 attach 重建同一 cursor | next node 与死前一致；旧 owner fenced |
| node 中进程死 | started 无 matching outcome + last checkpoint | 显示 interrupted/uncertain；按现有恢复规则重入 | 不伪造 completed；最终可收敛或 typed blocked |
| Journal 写失败 | persistence failure / sequence gap | trace quality=degraded | UI 明示缺口，graph authority不受影响 |
| checkpoint 损坏 | lifecycle/checkpointer validation | unavailable，不允许 drive | 无 State mutation |
| pause 发生在模型调用中 | pause flag + 当前无新 boundary | 等到下一 committed boundary | node 内调用不被伪装为已暂停 |
| Gateway 请求 step | capability matrix 不允许 | observer-only typed denial/无控制 | reflected public tool 未扩权 |

Breakpoint 是 debug session 配置，不是 workflow State。v1 可在进程死亡后丢失 breakpoint 设置，但
durable cursor 和 Bundle 必须可恢复；attach 后 operator 可重新设置 breakpoint。若未来要持久化
breakpoint，应单独定义 owner 和 schema，不能写入 ResearchState。

## 10. 被拒方案

1. **每个 Node 一个 CLI**：绕过 `_node_wrapper`，复制 capability、attempt、gate、budget 和 event
   语义，形成第二执行权威。
2. **TUI 直接 compile graph/读任意 SQLite**：把 serde、recipe 和路径知识泄漏到 adapter，无法
   统一 live/replay，也绕过 Bundle validation。
3. **复用 `ContinueRun`**：同一 intent 表示 orphan natural resume 和 debugger stop policy，破坏
   shared contract。
4. **维护 step graph 与 run graph 两个 compiled 变体**：E4 表明同一 compiled graph 已足够；
   双变体增加配置漂移。
5. **latest Bundle 作为 live handle**：并发和失败路径下无因果关联。
6. **checkpoint timestamp 当 node duration**：暂停时间污染测量。
7. **自动展示任意 State value diff**：敏感内容、伪输出和 State schema 耦合。
8. **TUI 任意修改 route/profile/checkpoint**：结果不可重放，污染 canonical Bundle。
9. **C3 同时实现 run driving**：观察 change 与 mutation/recovery change 的验收面混合。
10. **第一版经 Gateway 远程 step**：需要新的远端授权、并发、断线和 public contract；本地
    debugger 尚未闭环前没有必要扩大风险。
11. **假设 Journal 永远完整或新增无限 trace log**：前者忽略 256 条 retention，后者制造第二份
    persisted causal history；v1 用 checkpoint boundary + bounded Journal + degraded disclosure。
12. **step 间无 control ownership，或跨 operator pause 长期占用 execution lease**：前者让
    intentional pause 被当 orphan 接管，后者把 operator 阅读时间变成长执行锁；使用可过期
    control lease + per-invocation execution exclusion/fence。

## 11. C3/C4a/C4b 之外的延后项

- L4 capability attribution：单独 observation 增量，不从 node 推断。
- 从 checkpoint fork 并编辑 State：需要新 Bundle lineage 和污染隔离设计。
- 远端 Gateway debugger：需要显式认证、授权、租约、断线恢复和版本协商。
- 顶层并行 node 的单 visit 调度：当前 topology guard 失效时重新设计。
- 跨 run trace diff、断点条件表达式、录制/回放模型响应：先建立可信 v1 trace 后再评估。

这些延后项不得通过隐藏 flag 或 TUI 私有逻辑提前进入。

## 12. 对原计划实验状态的纠正

| 实验 | 原结论 | 审阅后结论 |
| --- | --- | --- |
| E1 checkpoint replay | 可形成历史帧 | 保留；证明数据可读，不证明正式 interface 或事实安全 |
| E2 checkpoint duration | 绿，相邻 ts 即耗时 | 撤销；step/HITL 停留污染，必须显式测量 |
| E3 blocked/suspended visibility | 绿 | 部分成立；checkpoint 能看停点，但 suspended Journal contract 有真实 store 缺陷 |
| E4 step runtime | 编译绿、运行未知 | graph fixture 核心路径已绿；Bundle lifecycle intentional-pause ownership、refinement/restart/concurrency 仍是 C4a 硬门 |
| E5 TUI 手感 | 未做 | C3 在可信 frame 后调只读卡片/replay；C4b 在可信 driver 后调 mutation interaction，均不得反向定义 runtime contract |

## 13. 交接阅读顺序

没有上下文的实现者按以下顺序工作：

1. 先完整阅读当前 [`../tui_step_progressive_plan.md`](../tui_step_progressive_plan.md)，只把它当
   当前决策和执行权威。
2. 在 propose C0/C3/C4a/C4b 前完整阅读本文对应章节，核对证据仍与代码一致。
3. 阅读当前主 specs，而不是从归档战役或 lifecycle walkthrough 推导执行语义。
4. 用 OpenSpec change 捕获每阶段 contract；每个 change 归档后再推进下一阶段。
5. 新实验若推翻本文，只修改尚未实施的当前 plan，并在进展记录留下证据；不回写本文制造
   历史漂移。
