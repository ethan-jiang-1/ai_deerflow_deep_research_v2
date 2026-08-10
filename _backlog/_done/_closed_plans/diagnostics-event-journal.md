# 计划：deep-research 的中间态诊断日志架构（Diagnostics Event Journal）

> 状态: 活跃（设计待实施） | 创建: 2026-08-10 | 类型: 分析/设计 plan
> 实施：由另一个 Agent 按本 plan 落地，走 `openspec/changes/`。

---

## 1. 为什么需要这个（情境）

### 1.1 我们撞到的真实问题

deep-research 的 real demo 跑真实 11 阶段管线。真实模型（deepseek-v4-flash / v4-pro）**不保证满足各节点的严格契约**——每次 run 随机在某节点失败：

| run | 失败点 | 失败类别 |
| --- | --- | --- |
| flash | wave1 | `agent_invocation`（工具窗口超限，已修） |
| v4-pro | topic_planning | `budget.exhausted` |
| v4-pro | wave0 / wave1 | `structured_output` |

诊断这些失败时，我们能读到的是**最终结论**：
```
结果类别: research.blocked
已知阶段: wave1
工作单元失败类别: structured_output
```

但**具体违反了哪条契约**（例如 wave1 校验的 7 条规则里哪条：`new_source_floor_not_met` / `claim_source_ref_foreign` / URL canonical / JSON parse……）——**完全看不到**。那个具体错误消息在代码运行的瞬间存在，但被传给 repair prompt 后丢弃了。

### 1.2 为什么会「找不到任何痕迹」

项目的诊断体系**只记录生命周期/terminal 事实**，没有为「中间态节点细节」设计持久通道：

| 通道 | 设计用途 | demo 里的实际行为 |
| --- | --- | --- |
| `DemoDiagnosticJournal`（records.jsonl） | lifecycle 动作 + terminal 事实 | ✅ 一直能读 |
| observation store（run-summary + events.jsonl） | terminal 观察 | ⚠️ events.jsonl 目前只有 terminal 一条 |
| `event_recorder.record()` | 节点记过程事件 | ❌ **被静默丢弃**——`record_event` 要求 observation manifest 已 publish，而 publish 只在 terminal 投影时发生 |
| `_emit()` / `ProgressEmitter` | node_agent 过程事件 | ❌ **没接线**——demo envelope `progress=None`，调用等于 no-op |
| checkpoint（graph.sqlite） | 全部中间态 | ⚠️ 有，但 msgpack Ext 编码，不是给人/日志读的 |

**结论**：项目把「诊断」设计成**结果层**的事实记录。而真实模型的失败恰恰需要**过程层**的细节才能定位。这是本项目的一个真实盲区——不是没有 log，是**只记结果、不记过程**。

### 1.3 为什么现在必须做

- 诊断当前 wave1 `structured_output` 就得看具体规则，拿不到。
- 今后任何节点失败，同样会「遇到了、不知道、找不到痕迹」。
- 继续往源码塞临时 `print` 不是办法：污染 src、跑一次才知道、不沉淀。
- 一句话：**把「能帮我们工作的 log」做起来，是诊断能力，不是临时插桩。**

---

## 2. 现状诊断体系分析（已核实）

### 2.1 已有的事实记录

- `records.jsonl`（`DemoDiagnosticJournal`）：每条 lifecycle 动作 + terminal 事实，字段 `action/category/certainty/fingerprint/phase/reference/time`。
- observation store：`run-summary.json` + `diagnostics/{events,lifecycle,records}.jsonl`，按 bundle 的 SHA 键组织。
- 检查命令：`make demo-sessions DEMO_ARGS="inspect <bundle>"`（只读，不恢复）。

### 2.2 中间态通道为何失效（关键机制）

- `RunObservationStore.record_event` → `_record_event_sync`：**先读 manifest，manifest 不存在就 return 丢弃**。manifest 由 `publish()` 创建，而 publish 只在 `run_experience._publish_observation`（terminal 投影）时被调。
- `node_agent_bridge._emit` → `self.envelope.progress.emit(...)`：envelope.progress 为 `None` 时直接 return。`DemoAdapter` 构造 envelope 时 `progress=None`。
- `ProgressEmitter` 默认 sink 是 `langgraph.config.get_stream_writer()`，demo 无 stream → no-op。

### 2.3 关联脊（已存在，可直接用）

`bundle_id → generation → phase → work_id → attempt_id` 是完整的事件关联键，工作单元层已经携带。

---

## 3. 设计原则（彻底思考后的结论）

1. **每个失败都留痕**：任何节点/attempt/provider/校验失败，都写一条**带具体事实**的事件（具体规则名、错误码、attempt_id、时间戳、阶段）。
2. **可关联、可复述**：一条 run 的完整故事（从准入到 terminal）能按 `bundle_id + generation + phase + work_id + attempt_id` 过滤出来。
3. **单一日志源**：一个 append-only 事件日志，从 bundle 准入写到 terminal，所有事件进同一通道，格式统一、可搜索。
4. **默认脱敏**：复用 `redact`（`build_progress_event` 已用），绝不写 secrets、原始 source body、内部 wire。
5. **纯观察，零 authority**：日志永远不能 resume/cancel/refine，无生命周期控制能力。
6. **入口无关**：捕获点在 graph/engine 共享层（work-unit kernel、node bridge、校验点），demo CLI/TUI 与 product 入口共用同一套事件。
7. **确定性与可验证**：日志内容有 deterministic 契约测试；日志不因缺失而扰动执行（现有 recorder 已保证「observation 不扰动 graph」）。

---

## 4. 架构方向与取舍

### 方案 A：让现有 observation store 成为完整事件日志（推荐主方向）

- **改动**：把 observation 的 publish 时机**提前到 run 准入（start）**，使 `record_event` 中间态落盘；节点在关键点通过 recorder 记具体细节。
- **优点**：复用现有 store / 检查命令 / 关联键；改动最小；recorder 本就是设计好的通道。
- **缺点**：observation store 语义从「terminal 事实」扩展为「过程日志」，需在 spec 里重新界定边界（terminal 仍是权威结论，事件是过程留痕）。

### 方案 B：独立 append-only 事件日志（JSONL）

- **改动**：demo 层为每个 run 建独立 `events.log`，所有事件（lifecycle+node+attempt+provider）写入；捕获点仍在 engine 层，demo 提供 sink。
- **优点**：语义干净（日志就是日志），不碰 observation 的 terminal 语义。
- **缺点**：新通道要建读取命令；与现有 observation 体系并存需明确分工。

### 方案 C：引入 stdlib `logging`

- 项目目前不用 stdlib logging，引入是新模式，且 stdlib logging 不带项目需要的 redact/关联脊/纯观察约束。
- **不推荐作为主通道**；可作为调试期补充。

### 倾向

**A 为主，B 作补充**：以现有 recorder/observation 为主通道（最小复用），核心改动是「publish 提前到 start」+「节点在关键点 record 具体细节」+「progress emitter 接一个 durable sink（落到同一 observation/事件文件）」。最终取舍由实施 Agent 在 change 的 design 阶段定，但必须满足第 3 节原则。

---

## 5. 具体捕获点（示例）

| 捕获点 | 事件内容 |
| --- | --- |
| work-unit kernel | attempt start / worker 完成 / attempt 失败（含 `failure_category`） |
| wave1 worker | **validation 失败**：`category="validation"`, `validation_code=<具体规则>`（如 `wave1_new_source_floor_not_met`）；repair 结果 |
| node bridge（`_emit` 已做） | model 调用 started / completed / budget_exhausted / 超时 |
| topic_planning | `budget.exhausted` 的具体预算维度（token 上限 / wall_time） |
| provider | 重试、超时、provider_category |

关键：**校验失败必须带具体规则名**（wave1 的 `initial_error` 是现成的），这是本次诊断拿不到、最需要的字段。

---

## 6. 验证标准

1. 跑一次真实 demo（v4-pro），在 observation / 事件日志里能读到：wave1 每个失败 attempt 的 `validation_code` = 具体规则名。
2. 一条 run 的完整事件能按 `bundle_id` 过滤成有序故事（准入→各阶段→terminal）。
3. 事件默认脱敏：不出现 secret / 原始 source body / 内部 wire。
4. 日志读取不依赖恢复/控制命令，纯只读。
5. 既有 gate 全绿：`UV_OFFLINE=1 make verify`、`openspec validate --specs`、`git diff HEAD --check`。

---

## 7. 实施范围（交给实施 Agent）

- **范围**：`deep_research_harness` 的 demo + 诊断层（recorder 时序、progress sink、节点捕获点）；`_backlog/plans/` 之外只写 `openspec/changes/<change>/`。
- **必走**：OpenSpec change（proposal/design/tasks/spec delta）→ red test → 实现 → 验证 → 归档。一次只激活一个 change。
- **不改**：graph 行为、lifecycle authority、provider、`deerflow/` submodule、`backend/`、`frontend/`。
- **参考**：本 plan 第 2 节机制、第 3 节原则、第 5 节捕获点、第 6 节验证标准。

## 8. 开放问题（实施前需定）

- observation store 提前 publish 的语义影响（terminal 结论 vs 过程日志如何共存、spec 怎么界定）。
- progress emitter 的 durable sink 具体落哪（observation events / 独立文件）。
- 是否需要独立 events.log（方案 B）还是充分扩展 observation（方案 A）。
