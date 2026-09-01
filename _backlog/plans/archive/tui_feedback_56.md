# TUI Workflow Debugger 计划一致性反馈

> **已消化并冻结（DIGESTED，2026-09-01）**：本审阅的全部结论已回填当前 plan 与 supporting
> 文档（见下面前置链接），迁入 `archive/` 仅作审阅 provenance，不再更新，也不作为执行权威。
> 任何实施先读 [`../tui_step_progressive_plan.md`](../tui_step_progressive_plan.md)。

> 日期: 2026-09-01
> 对象: 不了解前序讨论、准备继续 OpenSpec 推进的设计/实施者
> 结论状态: 已回填当前 plan 与 supporting 文档；本文是完整审阅反馈，不是执行权威
> 当前唯一执行权威: [../tui_step_progressive_plan.md](../tui_step_progressive_plan.md)
> 目标体验: [tui-workflow-debugger-target-ux.md](tui-workflow-debugger-target-ux.md)

## 1. 结论

新增 target UX 对其他文档有实质影响，但不推翻已定架构和阶段链。它把此前偏“trace/step
能力”的计划补成了完整研发调试体验：一个 launcher 进入同一 TUI，在 exact Bundle 上 New Run、
Step、Continue/Run、HITL、Pause、Inspect、Detach/Attach、Replay，并能查看每次 node-agent
invocation 的初始执行上下文与受控文件系统。这个体验可以由当前计划落地，但前提是六份文档不再
同时声称权威，也不允许旧 campaign 的接口草案混入新 OpenSpec change。

本次审阅后的唯一顺序仍是：

```text
C0 observation truth
  -> C3 observation + Node Context + bounded Files
  -> C4a headless debug driving
  -> C4b Textual adapter + executable launcher
  -> real validation
```

历史 C1 `close-provider-timeout-budget-handback` 和 C2 `add-suspended-run-recovery` 已归档；C0 是
后来插入的 corrective gate，不是编号遗漏，也不是说 C1/C2 无效。

## 2. 文档权威模型

| 文档 | 角色 | 使用规则 |
| --- | --- | --- |
| [当前 plan](../tui_step_progressive_plan.md) | 唯一活跃决策与执行权威 | OpenSpec 阶段、task、owner、gate、no-go 只从这里取 |
| [target UX](tui-workflow-debugger-target-ux.md) | 受控目标体验和验收地图 | 说明最终体验；不声称当前能力，不单独产生 implementation task |
| [grounding review](tui-step-debugger-grounding-review.md) | 冻结到 2026-08-31 的前置证据 | 解释原方案为什么不能直接实施；dated facts 在 propose 前重验 |
| `tui-interactive-campaign*-digested.md` | 冻结历史 provenance（已消化） | 只能了解战役来源；不得复制 unchecked task、类名或接口建议 |
| 主 specs 与应用代码 | 当前已实现事实权威 | 用来复核现状；目标 contract 的改变仍必须走 OpenSpec |

若事实与 plan 冲突，先修 plan 并记录证据，再 propose；不能让 proposal、Textual adapter 或历史文档
自行决定。若 target UX 与 plan 不能双向映射，也先停止 propose 并完成同步修订。

## 3. Target UX 带来的真实新增约束

### 3.1 Node Context 从可选观察项升级为 C3 硬门

旧 grounding review §5.7/§11 把 capability attribution 视为 optional/deferred。新目标体验要求研发者
能解释一个 node 为什么这样运行，因此 C3 必须在 `RuntimeNodeAgentBridge.run_agent` 的初始执行
seam、`agent.ainvoke`/首次 provider call 之前，持久化 versioned `NodeContextSnapshot`：

- exact runtime/base/capability MD；
- initial system/human messages 与 request；
- enforced tool/budget policy；
- virtual mounts、effective read/write roots 与 artifact refs；
- capture quality、source hash/identity 和 replay 所需 opaque ref。

这只覆盖每次 bridge/node-agent invocation 的 initial execution envelope。一次 invocation 内部可能有
多次 provider/tool loop；v1 只保留 bounded counts/safe facts，并明确 raw history `NOT_RETAINED`。
不能把 NodeContextSnapshot 误说成逐 provider-call message replay，也不能捕获 chain-of-thought。

### 3.2 文件系统成为受控 inspection surface

TUI 需要看 composition 真正暴露的 runtime MD、workspace、Bundle artifacts、evidence 和 report，
但必须通过 runtime-owned `OperatorWorkspaceReader` 和 typed views，而不是 adapter 直接浏览目录：

- Files tree、`/ls`、`/cat`、preview 共用同一个 policy；
- root 必须来自 composition manifest，并标 MODEL READ/WRITE、OPERATOR ONLY、RESTRICTED；
- 不暴露 host path、credential、secret、任意 repo 文件、raw State/checkpoint；
- `workflow.md`/源码导航只能标为 current developer guide，明确 `NOT MODEL VISIBLE`；
- captured bytes/ref 与 current source 分开，显示 MATCH/DRIFT/UNAVAILABLE，不用当前文件重建历史。

### 3.3 Launcher 和整个工作台属于 C4b，而不是第四套 runtime

仓库最终交付一个简单 executable `.sh`；无参数进入 chooser，也支持 fixture/embedded/direct forms。
New Run、Attach、Replay 是同一 TUI 中的动作，不是三个程序。按钮、快捷键、palette 和 slash command
必须归一成同一 typed adapter action。launcher 只做路径、参数、readiness 与进程启动，不扫描 Bundle、
不拥有 lifecycle，也不读 secret 值。

### 3.4 C4a 必须阅读 target UX

原 plan 只要求 C3、C4b、real validation 走读 target UX，这是缺口。C4a 决定 Step/Run stop policy、
breakpoint、Pause、Detach/Attach、lease/fencing 和恢复语义，正是大部分交互体验的 causal owner；现已
加入必读 gate。

## 4. 保持不变的核心架构

1. 只有一张真实 graph/recipe/checkpoint authority。Step 与 Run 只是不同 stop policy，不维护第二张
   step graph，不允许 TUI 私有 State mutation。
2. C3 只拥有 capture/projection/read-side inspection；C4a 拥有 runtime driving；C4b 是薄 Textual
   adapter。删掉 Textual 后，headless fixture tests 仍应能证明 trace/step/recovery。
3. 现有 `ContinueRun` 保留 orphan natural resume 语义。debugger 使用独立 closed `DebugCommand` 和
   `DebugRunDriver`，不能复用或扩写 `ContinueRun`。
4. live trace 必须从 admission/attach 起绑定 exact Bundle；没有 verified handle 就 fail closed，
   绝不回退 latest-active/mtime 扫描。
5. Checkpoint 是 committed boundary/order/route 权威；Journal 是 bounded causal-detail 权威。
   Journal 缺口必须标 degraded，不能虚构完整 trace，也不能另造无限第二事实日志。
6. breakpoint/pause_requested 属于 debug session/control projection，不写 ResearchState；control lease 与
   per-invocation execution exclusion/fence 分开处理。
7. v1 仅支持 local fixture/embedded mutation。Gateway/public reflected tool 保持 observer-only。

## 5. 发现并消除的跨文档冲突

### 5.1 Campaign v5 §10 已失效

旧 §10 仍写 D6-D8 待拍板，并提出以下路径：

- `BundleGraphExecutor.step_run`；
- `ContinueRun` 与 debugger command 共用；
- 泛化 `input_summary/output_delta`；
- C0 之前先做零契约 projector；
- 单独 compile 变体以及“同一 config 不得混跑”；
- 在 generic node delta 上做 capability attribution。

这些都与当前 plan 冲突。campaign 顶部现已加冻结/取代说明，§10 只留作历史，不得执行。

### 5.2 Progress Phase 8 不再是活跃 backlog

旧 progress 声称自己是“唯一活文件”、campaign 是“战略权威”，并保留可勾选 Phase 8。现在它被
明确退役：未勾任务不执行、不迁入 proposal；B1/B2/Gateway observer 遗留只按当前 plan 的并行线
记录。历史进展记录保持不改写。

### 5.3 Grounding review 的证据时点需要显式限定

grounding review 仍是有效的前置技术证据，但它冻结在 target UX 形成之前。现已加 post-freeze
routing note，明确 initial Node Context 的 C3 升级，以及逐 provider-call raw history 仍延后。正文
不回写，避免把 2026-08-31 的判断伪装成当时已经知道 2026-09-01 的决策。

### 5.4 Target UX 不是第二份 plan

target UX 现已增加 change-control：它负责旅程和验收，不负责 runtime ownership 或阶段。实现发现
若改变体验承诺，先回当前 plan；已归档 OpenSpec change 不改写，缺口走新的 corrective change。

## 6. OpenSpec 步步为营的执行协议

每一阶段严格执行：

```text
revalidate facts
  -> openspec propose
  -> polish/apply-readiness
  -> TDD apply
  -> UV_OFFLINE=1 make verify
  -> sync/archive
  -> update current plan checklist/progress
  -> next stage
```

propose 前必须有 source mapping：

- 每个 task 对应当前 plan 的 exact task/acceptance/no-go；
- C3/C4a/C4b 对应 target UX 的 journey、negative path、traceability row 和 UX script；
- C0 对应 observation truth/exact identity 依赖；
- grounding 的 dated fact 已按当前代码/spec 复核；
- 没有从 campaign 历史导入 task；
- 没有未声明的新 owner、persisted surface、权限、graph 变体或 Gateway mutation。

任何 stage 只有两个出口：全部 gate 通过并 archive，或停止后续阶段、回当前 plan 收缩/纠正。真实
模型运行只验证体验和接线，不能替代 fixture/headless deterministic contract tests。

## 7. 各阶段最低完成定义

| 阶段 | 必须证明 | 未满足时 |
| --- | --- | --- |
| C0 | persisted `suspended` truth；exact live correlation；真实 store/readers/writers 一致 | 禁止 C3 |
| C3 | versioned safe TraceFrame；live/replay 同构；NodeContext exact capture；bounded Files；degraded honesty | 禁止 C4a |
| C4a | headless Step/Run/HITL/Pause/Attach/Detach；lease/fencing/idempotency/recovery；one graph | 禁止 C4b |
| C4b | 薄 Textual adapter；executable launcher；command equivalence；终端尺寸/负路径；零新增 runtime 语义 | 禁止 real validation |
| real validation | 同一 TUI 完成调试 run 与新 Bundle 全速 run；证据绑定 exact bundle/cursor | 不宣布完成 |

## 8. No-go 与回退

出现以下任一项立即停止当前方案：

- 需要第二张 graph/第二套 checkpoint authority；
- TUI 直接 compile graph、直接打开任意 SQLite 或修改 raw State；
- adapter 重新实现 lifecycle、lease、serde、redaction 或 path policy；
- 需要 latest Bundle 猜测、generic State diff 或当前源码重建历史 prompt；
- 需要扩权 Gateway/public tool 才能闭环 v1；
- C3 无法 exact-bind，或缺失事实时不能显式 degraded/unavailable；
- C4a 不能在同一 graph 下证明并发 fencing、restart 和 HITL refinement。

允许的收缩结果是可信的 observer/replay TUI，或保留 headless driver 而关闭 mutation adapter；不允许
用好看的 UI 掩盖缺失的 runtime contract。

## 9. 本次一致性修订结果

- 当前 plan 已有明确 authority/read-order 表和 OpenSpec source-mapping gate。
- target UX 已明确自身是受控 acceptance baseline，并加入 drift/corrective-change 规则。
- grounding review 已标出冻结后被部分取代的 capability/NodeContext 结论。
- campaign、campaign progress、campaign review 均已明确冻结/退役；旧 §10/Phase 8 不再可执行。
- C4a 已纳入 target UX 必读范围，避免 driving contract 与交互旅程分离。
- 六份文档现在形成“一个 plan、一个 target、一个 evidence base、三份 provenance”的单向结构，
  不再形成并行计划。

下一步只能是重新检查 `openspec list --json` 与 C0 当前事实，然后创建
`repair-run-observation-truth` proposal；不能从 C3/C4a/C4b 或旧 Phase 8 起步。
本次审计时 `openspec list --json` 返回空 change 列表，没有现存 active change 与这条链冲突。
