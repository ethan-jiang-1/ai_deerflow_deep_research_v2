# Plan: Real CLI intake and observable run diagnostics

> 类型: 设计 / 复盘（postmortem） | 更新: 2026-07-22

> 实施状态（2026-07-22）：HITL1 intake、CLI/TUI state、canonical locator、retained
> summary/event journal、authorized workbench diagnosis 与 strict-msgpack boundary 已由
> `harden-deep-research-real-cli-intake-and-observability` 实施并通过确定性覆盖。原始
> Wave0 现场的 provider/tool/validator 根因仍须由一次新的真实、脱敏重现确定；不能把
> 可观察性改善误写成根因修复。

> 2026-07-23 补充：`classify-deep-research-wave0-worker-failures` 已将 Wave0 的
> node-agent、结构化输出和 typed validation 边界映射为闭集、脱敏的 attempt 类别，并在
> exhausted terminal 中保留诚实 aggregate；这提升诊断能力，不构成对原现场 provider/tool
> 根因的推断。

## 背景 / 现状

2026-07-22 的真实 CLI 现场 run：

```text
r_SnrIKUGQhUwUIAWyht4dq_zJLGNftutorg24_bhX62E
agent/.deep-research-demo-runs/workspace/deep-research/r_SnrIKUGQhUwUIAWyht4dq_zJLGNftutorg24_bhX62E
```

已核验事实：

1. 用户输入“标准深度”后，没有被 HITL1 解析；随后输入“你来定义吧”同样没有提供可用 profile。该 run 的 `request/profile.json` 是所有偏好为空的 degraded profile。
2. run 不是后台继续执行。最后一条 lifecycle record 是 `2026-07-22T03:59:53Z` 的 `blocked`，阶段为 `wave0`，诊断引用为 `diag_b32706968b70e9c6af20a1b2`；核验时没有该 real CLI 的存活进程。
3. retained bundle 确实存在，但 `demo-sessions inspect` 只能显示目录和文件名。它不显示终态、最后阶段、失败分类、诊断引用、三次 Wave0 attempt 的结果或下一步。同一 terminal 还出现互不关联的 bundle diagnostic ref `diag_b32706968b70e9c6af20a1b2` 与 CLI/global-journal ref `diag_WUApFmNjkJUkMjR2anjrAqg1`。
4. 真实 CLI 的 liveness heartbeat 被同文案去重，操作者无法从终端知道仍在等待、已经结束，还是仅保留了一个不可恢复的历史记录。
5. checkpoint 恢复已出现 LangGraph 的 `ContentRef` 与 `AttemptStatus` 未注册 msgpack 反序列化警告；上游明确说明未来版本或 strict mode 会拒绝它。

关联 bug：

- `BUG-001-hitl1-localized-intake-and-confirmation.md`
- `BUG-002-retained-run-diagnostics-are-not-actionable.md`
- `BUG-003-real-cli-run-state-is-not-observable.md`
- `BUG-004-langgraph-checkpoint-msgpack-registration.md`

## 事实边界

HITL1 输入是传统 Python 控制链，并非交给 node agent 自由理解：

```text
demo_real._ask_answer
  -> ResearchRunExperience._prepare_intent
  -> human_input_response
  -> ResumeResearchHandler
  -> hitl1.parse_profile_response
  -> merge_profile_progress
```

`parse_profile_response` 目前只有英文自由文本同义词。模型生成的建议只被放入 interrupt context；没有稳定地写入 checkpoint profile progress，所以用户无法安全地说“接受建议”。interrupt resume 会重放 node 的 interrupt 前代码，建议不能被当作临时 UI 状态或重新生成后自动接受。

当前 retained record 也不是完整运行日志：它是有界的 lifecycle trace + terminal category。此边界是安全设计的一部分，不能为了可观察性把原始 prompt、用户答案、API key、工具原文、绝对路径、堆栈或 provider payload直接写入 bundle/CLI/TUI。

## 决策 / 方案

### 1. 先建立稳定的 HITL1 intake 契约

- 由 Python 维护一个 checkpointed `proposed_profile`，其来源是已校验的 `StructuredBrief`，并与 request id / schema version 关联；它是建议，不是最终 authority。
- 定义显式、封闭的确认动作，例如 `accept_suggestion`，作为带 request id 的 typed human-input action 走既有 direct/broker resume 校验；CLI、TUI 和 authorized workbench 都只消费同一 pending projection 并发送同一 typed response，图仅在建议完整时 materialize 最终 profile。不得用自然语言“你来定义吧”猜测成确认，也不得让普通 text 伪造 action。
- 文本输入仍支持：JSON machine values、英文、以及明确覆盖的中文枚举短语。每一条中文别名须有碰撞测试；不能识别的内容必须返回“未识别任何字段，未消耗本轮输入”，而不是静默进入下一轮。拒绝消息仍写入一个专用 feedback cursor，以便新 request id 从它之后继续取输入；它绝不能进入 accepted consumed ids。为避免无限交互，对同一持续 HITL1 intake 最多连续拒绝三次；前两次可发新 request id 的 JSON 恢复提示，第三次以既有 `gate_blocked`/`input.invalid_response` 终态和 presentation category `profile_input_unrecognized` 停止，绝不降级成空 profile。
- 每次回答后，下一页必须显示“已识别/已采用”“尚缺”“当前建议”、剩余有效回答数和剩余拒绝重试数，并说明当前 request 明示的确认动作。`must_answer` 必须可见，不能作为隐藏必填项。
- 这是受控 input materialization，不让模型决定 route、phase、ledger 或最终 authority。

### 2. 建立用户可读的 run 状态契约

- 每个 CLI dispatch 必须显示 run ID、真实持久性、最近已确认阶段、已用时间和状态时间；只显示 runtime 已经证实的事实，不把“等待结果”伪装成内部节点进度。
- heartbeat 应以固定间隔更新 elapsed/last-confirmed phase，而不是被文案去重吞掉。对于不流式的图，明确说“等待本次生命周期调用返回”，不要说“正在后台研究”。
- 所有 terminal path 都输出统一终态回执：`completed/stopped/cancelled/blocked`、最后阶段、failure category/diagnostic reference（如有）、inspect 命令、以及该 durability 下的恢复语义。
- `same_process` 的终态或 Ctrl-C 必须明确说明：保留 bundle 仅可检查，不表示后台仍在跑，也不表示可跨进程恢复。`restart_durable` 则仅由已授权的 operation profile/workbench 处理。

### 3. 将 retained bundle 变成可诊断现场

在保留的、固定路径的 bundle 中增加一个版本化诊断摘要和有界事件 journal：

- `run-summary.json`：run ID、创建/更新时间、状态、terminal、最后阶段、generation、durability、最后 trace sequence、failure category、diagnostic ref、下一步类别、固定 artifact refs。
- 对每一个新 lifecycle，在进入 graph 前由 trusted UTC minute 与既有 opaque `research_id` 生成并 checkpoint `bundle_directory=YYYYMMDDHHMM_r_<research_id>`。它是唯一 canonical physical root：runtime projection、bootstrap/marker、request/profile、work/attempt、evidence、`ContentRef`、retained session、inspect/cleanup/workbench 必须全部从它派生，不能只改 retained store。`research_id` 仍是唯一的控制、checkpoint namespace、binding 与 inspect 身份。旧 checkpoint 缺失 locator 时只落到 legacy `r_<research_id>`，不迁移；发现同 ID 的多个有效 root 必须 fail closed。
- `diagnostics/events.jsonl`：有界、按 sequence 排序的安全事件。至少覆盖 lifecycle transition、node/worker attempt started/terminal、工具/模型结果的**类别**、validation code、retry/exhaustion、关联关系（research/phase/work/attempt/diagnostic ref）。
- 每条事件使用 UTC timestamp、单调 sequence、`research_id`、phase、component、event type、severity、可选 work/attempt/tool/model call id、duration、closed category 和 correlation id。runtime 以一个窄 `record(closed_event)` seam 在 session lock 内分配 sequence；dispatch、node wrapper、node-agent bridge、work-unit controller 是第一批生产者。provider/tool/pod 不直接写 session 文件；未来 sandbox/pod worker 只能提交同一闭合 envelope，使一个 run 可以按时间线拼回跨进程执行路径。
- `events.jsonl` 是诊断日志而不是业务控制面：事件丢失或 recorder 故障不得改变 graph route、ledger 或 checkpoint；但摘要必须明确指出日志是否完整/不可用，不能静默假装完整。
- 一个 terminal lifecycle 的 bundle/global-journal 引用必须由 runtime deterministic helper 生成并原样贯穿 terminal incident、trace、summary、event、CLI 和 inspect；CLI 不得打印无法由 inspect 查找的孤立 ref。摘要必须声明 event journal 的 `complete`、`incomplete` 或 `unavailable` 状态，不能把缺失日志伪装成完整流水。
- `demo-sessions inspect <run>` 和 workbench 必须读取这些受验证投影并首先显示摘要与相对 locator label；文件清单只是辅助信息，绝不显示 host path。不能让用户从一堆文件名猜当前状态。
- 诊断事件保留稳定错误类别、限制长度的安全摘要、相关 ID、时间和可去重 fingerprint；不保留 exception message、traceback、密钥、用户原文、模型原文、URL query、绝对路径或原始工具响应。开发者若需要更深的临时堆栈，只能通过进程 stderr / 显式 debug session 获取，不能写进 retained product record。

### 4. 为真实失败构建可复现闭环

最低验收场景：

| 场景 | 用户/操作者必须能看到 | 证据 |
|---|---|---|
| 中文“标准深度” | 已识别 `depth=standard`，仍缺字段 | domain + HITL lifecycle 测试 |
| 无法解析的回答 | 未消耗回合，明确说明未识别，不丢建议 | graph + CLI 测试 |
| 连续无法解析 | 前两次不消耗有效回合并给 JSON 恢复；第三次以既有 blocked terminal 和可检查 presentation category 停止 | graph + CLI 测试 |
| 接受建议 | checkpointed proposal 被确定性确认 | graph replay 测试 |
| 新 bundle locator | marker、profile、attempt、ledger、`ContentRef`、session inspect 都在同一 `YYYYMMDDHHMM_r_<id>` root | start/bootstrap/work-unit/session + SQLite reopen 测试 |
| Wave0 三次失败 | `blocked@wave0`、每次 attempt 类别、诊断引用、inspect 命令 | real-path fixture/integration 测试 |
| 运行执行流水 | 以时间排序看到 runtime/node/attempt/model/tool/validation/retry/terminal 的安全事件和关联 ID | deterministic event-journal integration 测试 |
| CLI 长等待 | run ID、elapsed、last confirmed phase 持续可见 | deterministic observer/clock 测试 |
| Ctrl-C / 进程结束 | 仅停止本地等待、是否可恢复、bundle 的检查命令 | CLI contract 测试 |
| 敏感错误输入 | 诊断与命令输出不包含密钥、原文、路径、堆栈 | adversarial redaction 测试 |
| strict msgpack checkpoint | 不出现未注册类型警告，旧 checkpoint 可读 | strict-mode integration 测试 |

## 风险 / 取舍

- [把建议当 authority] -> 建议必须经用户显式接受、带 request correlation，且只 materialize 到 profile，不能触及图路由。
- [“更多日志”泄露敏感数据] -> 只记录封闭类别、ID、时间与安全摘要；原始异常保留在进程调试面，不进入 retained record。
- [UI 说的进度大于运行时知道的进度] -> 使用 `last_confirmed_phase`，并明确 dispatch 是 returned-only，不伪造节点级实时进度。
- [在一个 change 混合输入和观测而不可审] -> 保持共享 run-experience/session contracts 的单一变更，但 `tasks.md` 按“intake”“run-state”“diagnostics”“验证”四组拆分，先完成每组的测试与独立验证再打勾。
- [误改上游] -> 仅修改 `agent/`、OpenSpec 与 backlog；不修改 `backend/`、`frontend/`。

## 落地关联

建议新建并实施一个 focused OpenSpec change：

```text
harden-deep-research-real-cli-intake-and-observability
```

change 的 specs/design/tasks 必须吸收三张 bug 卡，并明确 `tasks.md` 的逐项证据。完成后再分别关闭 BUG-001 至 BUG-003；不能只因 UI 文案变化就关闭诊断/可观察性问题。
