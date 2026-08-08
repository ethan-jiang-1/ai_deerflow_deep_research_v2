# Plan: Deep Research Run Bundle Is the Session

> 类型: 设计 | 归档: CLS-013（2026-07-22） | 状态: 四个顺序 Change 均已归档；Gateway/Web 产品接入仍 deferred

## 执行状态

这份 plan 的 **4 个顺序 Change 均已完成并归档**。最后一个 Change 已通过最终离线验证，
并归档于 `openspec/changes/archive/2026-07-22-build-deep-research-session-workbench/`；
本计划因此作为 `CLS-013` 移入 `_done/_closed_plans/`。

| 顺序 | Change | 状态 | 已交付 / 尚缺 |
|---|---|---|---|
| 1 | `establish-deep-research-run-bundle-session-contract` | **已完成**，2026-07-21 归档 | 本地 retained run bundle、manifest、redacted lifecycle trace、`demo-sessions list/inspect/cleanup`、CLI/TUI 统一 inspect view；不提供跨进程 resume |
| 2 | `establish-deep-research-session-lifecycle-binding` | **已完成，2026-07-21 归档** | canonical id 与私有 checkpoint binding、restart read-only reopen verifier、权限/tenant scope；不交付 user-facing operations |
| 3 | `add-deep-research-session-discovery-and-operations` | **已完成，2026-07-21 归档** | 私有 owner/profile discovery、trusted historical resolver、fixed file-SQLite local profile、brokered local CLI/TUI open/status/resume/cancel、recipe/provider drift 拒绝与 retention revocation |
| 4 | `build-deep-research-session-workbench` | **已完成，2026-07-22 归档（17/17 tasks）** | 本地 terminal session workbench、timeline、固定 metadata-only artifact catalog 与 broker-backed HITL 操作；Gateway/Web 产品接入明确 deferred |

### 完成状态与后续范围

前三个 change 已分别证明 retained bundle、checkpoint binding，以及本地的安全 discovery /
operation broker。`build-deep-research-session-workbench` 已完成 17/17 tasks，并归档于
`openspec/changes/archive/2026-07-22-build-deep-research-session-workbench/`：它交付 fixed
durable operation profile 的本地 terminal workbench、broker-authorized timeline 和
metadata-only artifact catalog。由于下游边界，Gateway/Web/upstream terminal 产品接入仍是
需要显式上游授权的后续 Change。

2026-07-21 的 deterministic acceptance 已用 file SQLite 完成真实进程重启后的私有
binding reopen 验证。没有配置或记录任何受批准的 credentialed durable provider，故该
补充验收安全跳过；它不替代也不阻塞本地 SQLite 的确定性证据。

2026-07-22 的 workbench 收尾证据已通过：`profile-preflight`、file-SQLite durability
（`9 passed, 1` 个 deferred Postgres skip）、fresh-process workbench 的
discover/open/timeline/fixed metadata catalog/foreign-denial smoke，以及入口 help 的
固定 authority 边界。根 `make doctor` 已运行，当前仅因既有 `config.yaml` 缺少
`TAVILY_API_KEY` 失败；该根环境缺口不属于本地 file-SQLite change，未在本 change 中修改。
最终 `UV_OFFLINE=1 make verify` 也已通过（fast 1612、integration/blocking-I/O 124、workflow
15 个确定性用例通过）；Change 已完成 archive，计划已关闭。

完成证据：

- `openspec/changes/archive/2026-07-21-establish-deep-research-run-bundle-session-contract/`，提交 `b78a0b9 feat(agent): retain inspectable run bundles`。
- `openspec/changes/archive/2026-07-21-establish-deep-research-session-lifecycle-binding/`，提交 `0b21b03 feat(agent): bind sessions to durable checkpoints`。
- `openspec/changes/archive/2026-07-21-add-deep-research-session-discovery-and-operations/`，提交 `8fff26a feat(agent): add session discovery operations`。
- `openspec/changes/archive/2026-07-22-build-deep-research-session-workbench/`，本次提交包含本地 workbench 实现、规范同步与计划关闭。

### Change 3 实现边界（已完成）

- 发现只从私有 owner/profile index 取得 opaque binding reference；不会扫描 retained
  bundle 目录，也不会把旧的 inspection-only bundle 回填为可操作 session。
- 固定 standalone fake profile 使用 owner-only file SQLite；每个 binding 记录该 profile
  的 recipe-compatibility fingerprint。provider、recipe、owner/profile、binding 或 retained
  bundle 任一不一致都会在 resolver、sandbox 或 graph work 之前变成不可用。
- `demo-sessions` 保留 `list`、`inspect`、`cleanup` 的旧观察语义；仅 fixed profile 的
  `discover`、`open`、`status`、`cancel` 和 `resume --request-id` 会调用 broker。resume
  的原始回答只从 stdin 读取，不进入 argv、manifest、trace、diagnostic 或 projection。
- fake TUI 使用相同 broker projection 和 request id；它不新增历史 session 的本地
  lifecycle controller。没有 Gateway、Web workbench、生产 CLI、MCP、跨用户发现或 artifact
  body viewer。
- retention 在删 bundle 前先撤销 matching binding/index；撤销失败保留 bundle，删除失败把
  已保留 bundle 降级为 inspection-only。通用 checkpoint rows 不在此 change 删除。

## 背景 / 现状

Deep Research 已经有一个以 research_id 为根的 research bundle：

    workspace/deep-research/<research_id>/
      request/
      work/
      evidence/
      synthesis/
      review/
      final/
      diagnostics/

它已经天然接近用户理解的 session：用户进入一个目录，就进入了一次研究；
该目录下可以找到输入、过程产物、最终交付物和诊断。前三个 change 已将 standalone
demo 从 `TemporaryDirectory` 迁移到受限的 retained root，提供安全的本地 inspection、
file-SQLite restart 与 profile-mediated discovery/operations。它们仍不提供 Gateway、Web
或通用 product workbench，因此用户尚不能在所有入口中完整管理研究单元。

这个计划把长期概念说清楚，避免下一阶段再发明一个内存对象、数据库行或
UI-local session 与 run bundle 并存：

    一个 Deep Research run bundle 目录，就是一个用户所说的 session。

session 不是一个抽象名字覆盖一堆分散的数据。它是可以定位、打开、检查、
恢复和清理的 research root。research_id 是其稳定身份；目录是其可操作的
载体；里面的数据共同构成一次研究的可见历史。

## 已有权威与关键约束

当前架构已经明确三种权威，不能为了让 session 看起来简单而破坏它：

| 用户想看到的 session 内容 | 现有权威 | 不可破坏的规则 |
|---|---|---|
| 当前阶段、待回答问题、取消/恢复是否合法 | ResearchState + LangGraph pending interrupt | checkpoint 是唯一执行控制权威 |
| 哪些证据被正式接受 | append-only submission ledger | 文件存在或模型文本不等于被接受 |
| 请求、页面缓存、证据、综合、报告、诊断 | run bundle 文件 | 内容不塞进 checkpoint |

所以“session 里有 state”需要准确落地：对用户而言，session 必须能显示其
状态；对实现而言，不能新增一个 state.json 来与 checkpoint 竞争。可选的
session manifest、索引或状态快照只能是受版本保护的投影/引用，永远不能被
graph 用作恢复或转移依据。若未来需要真正把 checkpoint 物理地放进 session
目录，必须作为 provider/migration 设计完成，而不是悄悄复制状态。

## 决策 / 方案

### 1. Session identity equals run-bundle identity

每个 durable session 使用一个 research_id 和一个 canonical bundle root：

    session id = research_id
    session root = workspace/deep-research/<research_id>/

不会再引入第二个随机 session id、只在 CLI 可见的内存 session、或者只服务
Web 的平行目录。任何入口拿到 research_id 都应能解析到同一个 session root，
并且先通过 trusted scope/containment 检查，不接受用户拼接的路径。

### 2. Directory is the operational unit

后续 CLI/TUI/Web/workbench 的“打开研究”“查看进度”“下载报告”“查看诊断”
都以一个 bundle root 为单位，而不是从散落的临时目录、日志或匿名 checkpoint
里猜测。建议在 bundle 根增加受控的 manifest，而不是另建 session 子目录：

    <research root>/
      manifest.json              # identity, schema, creation, safe references
      request/
      work/
      evidence/
      synthesis/
      review/
      final/
      diagnostics/

manifest 的职责是发现和导航：schema、research_id、创建/更新时间、内容版本、
checkpoint provider reference、可见产物 refs、保留状态。它不保存凭据、原始
prompt、provider body，也不保存可驱动 graph 的 phase cursor。

### 3. State is visible through the session, not duplicated by it

用户打开 session 时，界面应一次性读到：

    bundle root -> manifest/reference -> authoritative checkpoint -> RunView
                 -> artifacts/diagnostics -> timeline and report view

RunView 可以缓存给展示，但恢复、cancel、HITL answer 仍然只经过既有 lifecycle
和 checkpointed pending interrupt。这样“目录就是 session”不会退化成“目录里
有一个经常过期的状态文件”。

需要专门设计下列选择：

- checkpoint provider 是继续中央化并由 manifest 引用，还是在满足锁、原子性、
  多进程与迁移条件后变成每-session provider；
- manifest 的原子发布、版本兼容、权限/租户绑定和受损恢复策略；
- session root 与 sandbox/workspace/host mount 的关系，确保跨入口时仍满足
  containment，而不是暴露主机路径；
- session 完成、失败、取消后的 retention、导出、归档和垃圾回收。

### 4. Diagnostics belong to the same session eventually

当前 onboarding change 只会给 disposable demo 写一份受限的外部 redacted
diagnostic record，以解决“错误了却完全不知道什么错”的即时问题。长期上，
diagnostics 应进入 session root 的 diagnostics/，与 report、evidence 一样能
被同一次研究的用户和操作者查到。

诊断记录必须保持结构化和最小化：opaque reference、时间、阶段、闭合 failure
category、certainty、redacted fingerprint、恢复建议。原始异常、密钥、用户问题、
网页正文、模型输出和路径不能因为“有日志”而进入可见 session。

### 5. Product surfaces are adapters over the same session

后续入口的关系应是：

    CLI / TUI / Gateway / Web workbench
                 |
                 v
       run-bundle session discovery + RunView
                 |
                 v
    existing lifecycle / checkpoint / ledger / bundle authorities

没有一个入口拥有私有的 phase controller、HITL state machine、artifact index 或
diagnostic vocabulary。当前 change 建立的 ResearchRunExperience 只负责把 lifecycle
投影成统一 RunView；它不是 durable session，必须在此基础上接到真正的
run-bundle session，而不是取而代之。

## 用户旅程目标

1. 用户创建研究，马上得到一个稳定 session reference 和可打开的目录/视图。
2. 中途关闭 CLI/TUI 后，重新打开同一 session，看到准确的“已完成什么、正在等
   什么、为什么停下、下一步做什么”。
3. 用户回答 HITL、取消或重试时，所有入口通过同一 lifecycle 操作同一
   checkpoint，不复制状态。
4. 研究完成后，报告、证据、诊断和版本都在同一个 session 内可检索。
5. session 终止、保留、导出、归档、删除都有明确的 ownership 和 audit 规则。

## 尚未完成的范围

- Gateway/Web/production CLI 的 session discovery、授权与多用户范围；
- 上游授权后的 Gateway/Web/terminal workbench、跨入口流式 event timeline、报告浏览器和 artifact explorer；
- 更广泛的 checkpoint provider 迁移、每-session persistence、retention/GC、导出/归档、共享/协作与多用户权限。

前三个已归档 change 完成了本地 manifest、生命周期 trace、诊断归属、受限保留、
checkpoint binding 与本地 broker operations；它们刻意不把本地能力伪装成 Gateway 或
workbench。第 4 段已提案为本地 terminal workbench，仍必须在这一边界上继续，不能
偷渡第二套状态或 session controller。

## 风险 / 取舍

- [双重状态] → manifest/snapshot 被当作恢复 authority。缓解：checkpoint 和
  pending interrupt 的单一控制权威写入 spec、代码审计与测试；manifest 只存 ref。
- [目录即 session 但无法恢复] → 仅保存内容却没有稳定 checkpoint binding。
  缓解：先完成 manifest/provider binding 与 restart tests，再把任何入口称为
  durable session。
- [诊断泄漏] → 为了可观察性把原始异常或 provider 数据写入 bundle。缓解：闭合
  code + opaque ref + redacted fingerprint，测试扫描 sentinel secrets/paths。
- [入口漂移] → CLI、TUI、Web 再各自建状态机和索引。缓解：所有入口只消费共享
  RunView/session discovery Module，并做相同 fixture contract tests。
- [过早产品化] → 本次首跑修复被 session/workbench 工程吞没。缓解：先完成当前
  OpenSpec 的 shared run experience，再单独立 change，按 durable storage、
  lifecycle binding、session discovery/operations、workbench 四个可验证阶段推进。

## 落地关联

前置的 `improve-deep-research-cli-onboarding-and-observability` 已完成 shared
`ResearchRunExperience`、pending-input projection、safe diagnostics 与 CLI/TUI 迁移。

四个 session Change 已完成并归档。本地 terminal workbench 复用了既有 run-bundle session、
checkpoint binding 与 broker authority，没有另建 Web-local 状态或 artifact index。Gateway/Web
产品接入仍需另立上游授权 Change。

每个 change 都必须以“run bundle directory is the session”为共同词汇，并证明
checkpoint、ledger、content 三种既有权威没有被第二套状态存储替代。
