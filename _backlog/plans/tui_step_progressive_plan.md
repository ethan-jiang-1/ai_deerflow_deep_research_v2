# TUI Workflow Debugger 递进执行计划

> 类型: 递进执行计划 | 创建: 2026-08-31 | 重写: 2026-08-31
> 状态: 当前唯一活跃 plan；D6-D8 已定，尚未创建 C0/C3/C4a/C4b OpenSpec change
> 当前决策与执行权威: 本文件
> 完整证据与纠错理由: [archive/tui-step-debugger-grounding-review.md](archive/tui-step-debugger-grounding-review.md)
> 历史材料: `archive/tui-interactive-campaign*.md` 只作 provenance，不再定义当前 TUI debugger
> 编号说明: 历史 C1 `close-provider-timeout-budget-handback` 与 C2 `add-suspended-run-recovery` 已归档；
> C0 是本次审阅新增的纠错闸门，不是漏掉 C1/C2，也不表示它们无效。
> 当前用法: 严格按 `C0 -> C3 -> C4a -> C4b -> real validation` 推进；每个 change 归档且 gate 全绿后才进入下一阶段。

任何人 propose、review 或 apply C0/C3/C4a/C4b 前，必须完整阅读本文件；当工作涉及原计划纠错、
Journal/Bundle/checkpoint 权威、E4 实验、被拒方案或延后项时，还必须完整阅读 grounding review。
两者冲突时以本文件为当前决策权威，以主 specs 和 runtime/domain 代码为执行事实权威。

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
| D7 顺序 | **修订后通过** | 已归档 C1/C2 不重开；当前链为 C0 truth -> C3 observation -> C4a headless driving -> C4b TUI adapter |
| D8 定位 | **通过并收窄** | 本地 operator workflow debugger；不是 Primary User product UI，不给 reflected public tool 扩权 |

### 0.3 关键纠错

1. `suspended` outcome 当前被真实 `RunEvent` 拒绝，C0 必须先修复；fake-recorder 绿测不足以
   证明 Journal truth。
2. live trace 必须从 admission/attach 起绑定 exact `bundle_id`；没有 exact handle 时 fail closed，
   不回退 latest-active 扫描。
3. 现有 `ContinueRun` 只表示 orphan natural resume，保持不变；debugger continue 使用独立
   local `DebugCommand`。
4. checkpoint `created_at` 相邻差不能叫 node duration；duration 由 wrapper 对实际 invocation
   显式测量。
5. C3 只做观察投影与只读 trace/replay 呈现；`run`、`step`、`continue`、`pause`、`answer`、
   `attach` 的 runtime 驱动属于 C4a，Textual mutation-command 接线属于 C4b。
6. 同一 compiled graph 可逐次使用 `interrupt_after`，fixture E4 已证明 step -> HITL -> run
   核心路径；正式不变量是同一 recipe/compile path/checkpoint thread，不维护 step 专用拓扑。

## 1. 目标体验与操作语义

### 1.1 两层观察，一个控制粒度

- **L2 顶层边界卡片**：每次 logical-node invocation segment 在 completed/suspended/failed boundary
  形成一张卡，是 v1 唯一可 step 的粒度。普通 node visit 通常一张；HITL resume 会复用 visit id，
  因而同一 visit 可先有 suspended card，再有 completed card。当前 happy path 最短约 9 个 completed
  boundaries，真实 run 通常 10-20 个；C4a 用 topology guard 保证当前每个顶层 superstep 只执行
  一个 logical node。
- **L3/L4 内层叙述**：work unit、attempt、模型和工具调用以只读行跟随。v1 可展示安全计数、
  budget/failure facts 和显式记录的 invocation attribution，但不在模型或工具调用内部暂停。

node 执行期间显示一条 provisional running row：exact node/visit、wall elapsed、最新安全内层 fact
和 pause-requested 状态。wall elapsed 明确不是最终 node duration；只有 boundary commit 或正式
HITL/failure 后才固化 TraceFrame，避免把“仍在跑”叙述成“已完成”。

composer、`/ls`、`/cat`、`/inspect` 可以继续作为 operator workbench 能力；这些命令不得读取
未经 Bundle lifecycle 验证的任意 host path，也不得获得 graph mutation 权。

### 1.2 操作闭集

| 操作 | 精确定义 | 停止条件 / 约束 |
| --- | --- | --- |
| `start` | 创建 exact debug session 和 Bundle；返回 verified handle 后才开始 live trace | 不靠 workspace 扫描认领 Bundle |
| `step` | 调用当前顶层 logical node 一次 | completed/suspended/failed boundary；不执行第二个顶层 node |
| `continue` | 从当前 boundary 按 stop policy 连续推进 | 指定 node 提交后的 breakpoint、HITL、failure、terminal 或 pause request |
| `run` | 新 run 的自动挡，或无自定义 breakpoint 的连续推进 | 仍逐 boundary commit/emit，可请求 pause |
| `pause` | 请求自动 drive 在下一个 committed boundary 停住 | 不声称能中断正在进行的模型/工具调用 |
| `inspect` | 查看当前/历史 TraceFrame 和授权 content refs | 纯读，不改 cursor、State、route 或 lease |
| `answer` | 对当前正式 HITL request 提交 existing typed response | request id/cursor 必须匹配；HITL2 不发明 prompt |
| `cancel` | 走现有 lifecycle cancel 语义 | TUI 不把本地退出冒充 durable cancel |
| `attach` | 选择 exact recoverable Bundle 并重建 debug session | 不自动推进；现有 orphan `ContinueRun` 仍是另一操作 |

UI label 可以使用 `continue`，domain 内部必须使用独立 `DebugCommand.drive_until` 或等价闭集值，
避免与现有 `RunIntent.ContinueRun(kind="continue")` 冲突。

### 1.3 Operator 能调什么

v1 允许 operator 调整运行节奏、breakpoint、观察深度，并在正式 HITL 上回答。调试发现问题后，
修改代码、prompt/capability/config，再创建新 Bundle 重跑和比较。

v1 不允许原地改 route、profile、checkpoint 或任意 State value。未来若需要 checkpoint fork，必须
创建新 Bundle，记录 parent bundle/cursor 和 debug lineage；原 Bundle 保持可重放。

### 1.4 TUI 可用性验收

TUI 至少稳定呈现：exact bundle/mode/cursor 状态、按 sequence 排列的 timeline、当前卡片、显式
inspect pane 和常驻 composer。卡片默认只显示闭集安全事实；内容按 ref 主动展开。使用 Textual
Pilot/截图在至少 80x24、120x40、160x50 三种终端尺寸验证无重叠、关键状态不被截断、动态内容
不导致控制区跳位。fixture 全流程不需要凭证或网络。

## 2. 权威、modules 与 interface

### 2.1 Authority map

| 事实 / 动作 | 唯一 authority | TUI 的权限 |
| --- | --- | --- |
| route、ResearchState、node commit | StateGraph + Bundle lifecycle | 只消费投影 |
| durable boundary | exact Bundle checkpoint | 只显示 projected cursor |
| lifecycle status、pending input、cancel/recovery admission | 现有 lifecycle/domain contracts | 提交 typed command，不推断 |
| intentional debug-boundary ownership | runtime-owned expiring debug control lease | 展示 lease posture；不能自行续租/接管 |
| redacted node/model facts | runtime Journal writers | 只显示 TraceFrame |
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

### 2.3 `DebugRunDriver` deep module

工作名 `DebugRunDriver` 同样不锁死最终类名；contract models 归 domain，graph/lifecycle driving
implementation 归 runtime。它可以在 `BundleGraphExecutor` 背后或相邻 module 实现，但必须提供
独立于现有 `ContinueRun` 的 debug interface。外部 interface 保持为两类动作：

```text
open(start | attach) -> DebugSessionSnapshot
execute(DebugCommand) -> DebugSessionUpdate
```

mutation command 必须携带 exact bundle、`expected_cursor` 和 `command_id`。implementation 隐藏
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

### 2.4 `BoundaryCursor`、`TraceFrame` 与 active visit

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
non-committed failure 才产生 frame。TUI 不自行配对 Journal 和 checkpoint。

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
- wrapper 显式测得的 `duration_ms`；
- `failure_category`, terminal disposition, pending-input projection；
- `observation_quality = complete | degraded | unavailable` 及 bounded gap reason。

禁止自动包含任意 State value、泛化 `input_summary/output_delta`、raw model/tool content 或 host path。
node-specific whitelist/content refs 必须复用现有访问和 redaction contract。capability id 只可由
`NodeExecutionRequest.capability_ref` 所在 model-invocation seam 显式写入，不能从 node/phase 推断；
该 L4 能力作为独立可选 observation 增量，不阻塞 C3/C4a/C4b v1。

### 2.5 Adapter capability matrix

| Adapter / mode | Trace replay | Exact live trace | Debug driving |
| --- | --- | --- | --- |
| fixture local | 是 | 是 | 是，C4a 首要验收面 |
| embedded-smoke local | 是 | 是 | 是，fixture 全绿后接线 |
| Gateway/public tool | 有 exact contract 时才可 | 当前不宣称 | 否；保持 observer-only |

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

对应 falsifiable guards：双 Bundle 并发不得串帧；同 command id 重放只 commit 一次；两个 driver
竞争时一个成功、另一个 stale/locked；node 执行时间跨过 control TTL 也不得出现第二 writer；人为
删一条 Journal event 必须出现 degraded；植入任意 checkpoint value 不得自动出现在 TraceFrame。

## 4. OpenSpec change 阶梯

所有代码、persisted schema 或 cross-module interface 变更都走独立 OpenSpec change。下面的表只列
**当前尚未执行的链**；C1/C2 已经完成并归档，所以不会再次出现在待办顺序中：
**propose -> polish/apply-readiness -> TDD apply -> `UV_OFFLINE=1 make verify` -> sync/archive**。
propose 时登记新 requirement ID，并核对当前没有会修改同一 authority 的 active change。

| 顺序 | 建议 change slug | 唯一载荷 | 前置 |
| --- | --- | --- | --- |
| C0 | `repair-run-observation-truth` | suspended Journal truth + fail-closed exact live correlation | 本 plan 已定 |
| C3 | `add-run-trace-projection` | runtime TraceFrame/projector + replay/live presentation | C0 归档 |
| C4a | `add-local-workflow-debug-driving` | DebugRunDriver + control lease + 全部 headless drive/recovery contracts | C3 归档 |
| C4b | `connect-tui-workflow-debugger` | Textual command adapter + fixture/embedded 接线；零新增 runtime 语义 | C4a 归档 |
| 终线 | 无 change | 一次固定问题的真实模型体验/一致性验收 | C4b 归档 + 网络可用 |

编号保留 C3 与 C4a/C4b 中的“4”是为了延续 020 战役账本：历史 C1
`close-provider-timeout-budget-handback` 与 C2
`add-suspended-run-recovery` 已归档。C0 是本次审阅插入的前置修复，不表示回改历史 C2；它通过
新的 corrective change 前进，并保留 C2 的 orphan recovery 行为。C4a/C4b 是同一 driving 阶段的
headless authority 与 presentation adapter 两个独立 cut，不增加新的轴编号。

统一门规则：

- 每个 change 只有“验收全绿并 archive”或“停止后续阶段并回本 plan 收缩范围”两种出口。
- C0/C3/C4a 的 correctness 均由无凭证 fixture/headless tests 证明；C4b 再证明 adapter 接线；真实模型只验证体验和接线，
  不能替代 deterministic contract tests。
- 实验推翻计划时，只修订尚未 propose/apply 的阶段；已归档 change 通过新的 corrective change
  前进，不改历史归档。
- C0 未通过，禁止开始 C3；C3 无法 exact-bind 或无法显式报告 degraded，禁止开始 C4a；C4a
  未归档，禁止开始 C4b。
- 若 C4a 只能靠第二张 graph、TUI 私有 State mutation 或 public tool 扩权实现，立即 no-go。

## 5. C0 - `repair-run-observation-truth` [ ]

目标：在设计卡片之前先修复 observation 事实，并使无法关联的 live narration 宁可缺失也不串包。

### 5.1 Contract tasks

- [ ] 在 propose 前用当前代码重现 `RunEvent(outcome="suspended")` 拒绝，并记录到 change evidence。
- [ ] 扩展 persisted RunEvent outcome 闭集，使 `suspended` 在主 spec 要求的 schema/version 策略下
  可读写；枚举所有 readers/writers 并同步切换。新代码须读取旧 events 且无需数据迁移；旧代码
  会拒绝新 suspended event，proposal 必须声明本地 coordinated cutover 和 rollback 限制。
- [ ] `_record_node_event` 的所有 observation paths 都保留 suspended，不映成 `failed`；unexpected
  exception 继续是 `failed + internal.unexpected` 并传播。
- [ ] 建立 wrapper -> real Bundle recorder/store -> serialized `events.jsonl` -> reader 集成测试；
  fake recorder test 只保留为局部行为测试，不再作为 REJ-011 唯一证据。
- [ ] 移除 `_latest_active_bundle` 对当前 dispatch live narration 的因果角色。exact id 未知时显示
  unbound/static working，不读最近 Bundle；attach candidate 排序可保留，但选择后必须 exact-bind。
- [ ] 修正与本变更直接相关的 REJ-011 主 spec/test/doc 漂移；不把历史 walkthrough 提升为
  authority，也不把无关文档清理混入 C0。

### 5.2 Falsifiable acceptance

- [ ] 真实 store 中存在 `started -> suspended`，且没有 `internal.unexpected`；reader 返回 suspended。
- [ ] 真 unexpected exception 仍持久化 failed/internal.unexpected，graph 行为不因 observation 改变。
- [ ] 同 workspace 放置两个 active/suspended Bundle，TUI 未拿 exact id 时不显示任一方事件；绑定
  A 后永不出现 B 的 sequence/phase。
- [ ] 植入 observation persistence failure 后，graph/lifecycle 继续按原 authority 工作，诊断明确
  表示 degraded/unavailable，而不是错误 completed。
- [ ] 相关 targeted tests、integration tests、`make verify` 全绿；change 同步主 spec 并归档。

### 5.3 No-go

真实 store 仍丢 suspended、TUI 仍需要 latest 才能显示“实时进度”，或修复要求改变 graph route，
则停止 C3。允许的收缩结果是暂时只显示静态 working 和 exact historical replay。

## 6. C3 - `add-run-trace-projection` [ ]

目标：建立 runtime-owned、versioned、redacted、可分页且 live/replay 同构的 trace module；本阶段
不启动、不推进、不恢复 graph。

### 6.1 Contract tasks

- [ ] 在 delta spec 定义 `TraceFrame`/`TracePage`/`ActiveVisitProjection` 的字段闭集、version、
  ordering、opaque `TraceReadCursor`、pagination/upsert、gap/degraded semantics、redaction 和未知
  版本行为；started 或 pre-checkpoint completed 都不能冒充 committed frame。
- [ ] 在 node wrapper 对每次实际 invocation segment 使用 monotonic clock，随
  completed/suspended/failed fact 写入 bounded `duration_ms`；HITL resume 的多段 active duration
  分别记录，human wait 不在任一段内。checkpoint 间隔只可另名展示，不冒充 node duration。
- [ ] 审核现有 `MAX_EVENT_RECORDS=256` retention：finalized node fact 的优先级高于普通
  start/model-tool success，admission/terminal/failure 等现有 anchors 继续受保护；容量仍不足时
  manifest/TracePage 必须披露 dropped interval/count。
- [ ] 实现 `RunTraceProjector`：只接受 verified Bundle ref；从 checkpoint 投影 boundary cursor，
  从 Journal 读取 causal facts；检测重复、缺口、out-of-order、corrupt 和 unavailable。
- [ ] 同一 projector 支持 historical replay 与 caller-supplied verified Bundle 的 exact live
  incremental read；live 断线后用 opaque TraceReadCursor 重接，输出与完整 replay 一致。C3
  不为获得 handle 而启动 graph；当前 TUI 若尚无 early handle，只展示 replay/static working。
- [ ] 卡片只显示 §2.4 闭集；changed fields 只给名称。内容通过 node-specific whitelist 或现有
  authorized refs inspect，不输出 raw State/model/tool payload。
- [ ] 把 `scripts/experiments/tui_trace.py` 替换为正式 interface tests；脚本删除，或改为不认识
  SQLite/recipe/serde 的薄 adapter。
- [ ] Textual adapter 只消费 TracePage，不 compile graph、不打开 `graph.sqlite`、不扫描 latest。
  将 trace rendering/transport 从 1817 行 `demo_tui.py` 中拆出，避免继续堆 runtime semantics。
- [ ] 用 fixture 完成 E5：卡片密度、timeline/inspect/composer 和三种终端尺寸调试；结论写 §L。

### 6.2 Required fixtures and acceptance

- [ ] replay：fixture completed、real-sample completed、BUG-062 blocked、HITL suspended。
- [ ] truth：Journal complete 时，同一 Bundle 的 live incremental 最终 frames 与 full replay 等价；
  active projection 只在 commit/failure 确定后消失。一次多轮 HITL visit 保留每个 suspended segment
  和最后 completed segment，不因 visit id 相同而覆盖。Journal incomplete 时只保证 checkpoint
  boundary identity/order，并明确缺失的 duration/inner facts。
- [ ] commit truth：注入“node body 返回 completed，随后 wrapper/gate 失败且无 checkpoint”；只生成
  failed frame，可保留 node-body-completed 子事实，但不得生成 completed boundary frame。
- [ ] isolation：两个 Bundle 交错写入不串 frame；TraceReadCursor 只消费指定 Bundle。
- [ ] degradation：缺 event、坏 JSON、checkpoint unreadable、started-without-outcome 都得到显式
  quality/uncertain 结果，不推断完成。
- [ ] capacity：用超过 256 条的 fixture 触发 eviction；admission/terminal/failure/finalized-node
  retention 符合 spec，dropped interval 可见，旧卡片不被冒充为完整 causal trace。
- [ ] privacy：向 checkpoint 植入 sentinel question/profile/evidence/message/path，默认 TraceFrame
  和 TUI snapshot 均不出现 sentinel。
- [ ] timing：模拟长时间 operator pause，node `duration_ms` 不包含 pause；boundary timestamps
  可以保留但标签不同。
- [ ] UI：80x24、120x40、160x50 无重叠/关键状态截断；fixture composer 与 inspect 可用。
- [ ] module interface tests、TUI Pilot tests、`make verify` 全绿；spec 同步并归档。

### 6.3 Optional separate increment

若 v1 必须显示 capability attribution，另立 `add-model-invocation-trace-attribution` change，在
`NodeExecutionRequest.capability_ref` 的真实 bridge seam 写 L4 fact。不得把它塞进 node frame，
不得阻塞基础 C3/C4a/C4b，除非新证据证明没有它 debugger 无法完成验收。

### 6.4 No-go / 收缩

若安全且有用的叙述流无法收敛，保留 headless projector 与历史 replay，撤回自动内容卡片；不要
用 raw checkpoint dump 换取“可见性”。C3 未归档，C4a 不开始。

## 7. C4a/C4b - Local workflow debug driving [ ]

目标：先在 C4a 建立独立、可 headless 验收的 local debug drive interface，再由 C4b 把 Textual
接成纯 adapter。现有 shared `RunIntent`、`ContinueRun`、route/profile/HITL admission 保持原义。

### 7.1 C4a `add-local-workflow-debug-driving` tasks

- [ ] 定义 `DebugSessionSnapshot`、`BoundaryCursor`、closed `DebugCommand`、typed update/denial 和
  stop policy；surface 明确 local-only，不进入 reflected public tool。
- [ ] `open(start)` 在任何 live narration 前返回 exact Bundle handle；`open(attach)` 只重建 cursor，
  不等同现有 natural resume，也不自动推进。
- [ ] 定义/实现独立的 expiring debug control lease：open 原子取得，live session heartbeat，
  detach/terminal/cancel 释放。明确 owner、generation、TTL、heartbeat、stale detection 和 fencing；
  lease 是 private control fact，不写 ResearchState，也不复用 suspended/pending-input posture。
- [ ] natural `ContinueRun`、第二 debugger 和其他 mutation path 在 live debug lease 存在时 typed
  deny/busy；status/inspect observer 仍可读。takeover 只在 control lease stale 且无 live
  `execution_exclusion` 时开放，并必须 CAS exact lease generation/cursor；歧义状态保持 read-only。
- [ ] attach candidate projection 区分 live-owned debug pause 与 stale/dead owner：前者只允许
  status/inspect，后者才广告 takeover/attach；候选列表排序不授予控制权。
- [ ] 实现 `advance_one`：同一 recipe/compile path、per-invocation `interrupt_after`、同一 durable
  saver/thread；每步获取并释放 `execution_exclusion`，提交最多一个当前 topology 下的 logical node。
  execution fence 必须覆盖 node body、gate 和 checkpoint commit，长调用期间保持 live/renewed；
  restart 可重新 compile，但不得存在 step 专用 topology/recipe。
- [ ] 实现 `drive_until`：到 breakpoint/HITL/failure/terminal/pause 停止；`run` 是 start 时的自动
  stop policy，不复制一套执行逻辑。
- [ ] pause 仅在下一个 committed boundary 生效；正在执行的模型/工具调用显示 running +
  pause-requested，不宣称已中断。
- [ ] answer 复用 existing typed human response/request correlation；HITL1 可多轮，HITL2 保持
  autonomous continuation。
- [ ] mutation command 统一校验 exact bundle、expected cursor、command id；处理 duplicate、stale、
  active lease 和 out-of-order。
- [ ] attach/restart 从 durable checkpoint 重建；started-without-outcome 保持 uncertain，按现有
  work-unit/lifecycle recovery 收敛。
- [ ] 增加 topology guard：当前一个顶层 superstep 只有一个 logical visit。guard 失败时阻止 step
  contract 漂移，要求重新设计并行语义。

### 7.2 C4a falsifiable acceptance matrix

| Journey | 必须证明 |
| --- | --- |
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
| failure | node exception、blocked terminal、observation degraded 都停在可解释状态 |
| privacy/authority | TUI command 无 route/profile/State 任意写入口；public Gateway surface 未变化 |

- [ ] fixture/headless matrix 全绿；真实模型不是这些断言的唯一证据。
- [ ] driver/control-lease module interface tests、multiprocess tests、`make verify` 全绿；delta 同步主
  spec，C4a 归档。归档前 Textual 不调用新 mutation interface。

### 7.3 C4b `connect-tui-workflow-debugger` tasks and acceptance

- [ ] Textual 只消费 C3 TracePage 与 C4a DebugSession updates，只提交 closed DebugCommand；不直接
  compile graph、操作 lease、读 checkpoint 或推断 lifecycle。
- [ ] 提供明确 mode/cursor/breakpoint/control-lease/pause 状态，以及
  step/continue/run/inspect/answer/cancel/detach；重复输入显示 C4a typed duplicate/stale/busy。
- [ ] attach UI 区分 live-owned busy/read-only 与 stale takeover candidate；选择前零 mutation。
- [ ] 同步 `docs/run-lifecycle-walkthrough.md`：HITL1 是正式人工停点，当前 real HITL2 是
  autonomous continuation；TUI 不显示第二个人工 answer 控件。
- [ ] fixture Textual Pilot 覆盖完整 step journey、模式切换、按钮/命令重复触发、长卡片、三种
  terminal size/resize、pause requested、stale/busy denial 和 detach/reattach。
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
  → 收口后按治理把 `archive/` 四份 TUI 文件整组 `git mv` 进 `../_done/_closed_plans/`
  （plan ID 从 CLS-058 起）并同步 README 索引

## 9. Dated grounding 与实验状态

完整证据、代码位置、最小实验过程和被拒方案见
[grounding review](archive/tui-step-debugger-grounding-review.md)。本节只保留会直接影响执行顺序的
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
- `openspec list --json` 在 2026-08-31 plan 重写时为空；propose C0 前仍须重新检查。

## 10. 提案前交接清单

接手者创建任何 change 前逐项确认：

- [ ] 完整阅读本 plan 与 grounding review，并检查 git 中是否已有 overlapping active change。
- [ ] 重新运行该阶段的最小反证，确认 dated evidence 未因代码变化失效。
- [ ] 在 proposal/design/tasks/spec 中逐项映射本阶段 tasks、negative paths、acceptance 和 no-go。
- [ ] 明确 surface：persisted RunEvent、versioned TraceFrame、local DebugCommand，分别给出兼容策略。
- [ ] tests 穿过正式 module interface；fake-only 或 UI snapshot-only 不能证明 runtime contract。
- [ ] 保持 `deerflow/` submodule 只读；实现只发生在 `deep_research_harness/` 与对应 specs/tests。
- [ ] change 归档后更新本文件 checklist 与 §L；未归档前不开始下一阶段。

## L. 进展记录（append-only）

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
