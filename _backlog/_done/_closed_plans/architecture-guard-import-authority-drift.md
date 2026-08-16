# Plan: 架构守卫 import matrix 的权威源漂移修复

> 类型: 设计 / 复盘（postmortem） | 更新: 2026-08-16
> 状态: 止血已完成（commit `feb5549`）；根治（方向 B）待开 change

## 背景 / 现状

`check_project_architecture.py` 是项目反复强调的"机械校验权威"（`architecture-policy.md`
把它列为 Mechanical enforcement，`deep_research_harness/AGENTS.md` 的 generated block 也指向它）。
历史上它曾因 import matrix 的"第二真相源"漂移而**变红**，且那次失败恰好暴露了"单一权威"承诺的一处失效。

### 原始证据链（2026-08-16 早前，现已止血）

1. 当时的活跃 change `wire-harness-observability-entrypoints` 的 `tasks.md` task 1.3 打了 `[x]`：
   "Register … the bounded `httpx_sse` runtime import in `project-structure.toml`"。
2. `project-structure.toml:1003` 加了 `httpx_sse`。
3. 但 `check_project_architecture.py:38-45` 里硬编码了另一张 import matrix `REQUIRED_IMPORT_POLICY`，
   其中 runtime 层没有 `httpx_sse`。
4. `check_project_architecture.py:338-343` 拿 toml 的 `[imports]` 逐层比对硬编码表，不一致即抛
   `imports.policy` → 守卫红。

### 现状快照（2026-08-16 复查，commit `feb5549` 之后）

- ✅ 止血已做：`check_project_architecture.py:44` 的 `REQUIRED_IMPORT_POLICY["runtime"]` 现在含
  `httpx_sse`，`python3 openspec/governance/check_project_architecture.py` 真实退出码 0
  （"Architecture governance passed"）。
- ✅ `wire-harness-observability-entrypoints` 已实现并归档：
  `openspec/changes/archive/2026-08-16-wire-harness-observability-entrypoints`。
- ❌ **根因未除**：checker 里仍硬编码着 `REQUIRED_IMPORT_POLICY`，而 `architecture-policy.md:21` 仍明文写
  *"it must not contain an independent directory tree or import matrix"*——矛盾依然成立。
- ❌ `ownership_layers`（`project-structure.toml:19`，5 层）与 `INTERNAL_LAYERS`/`[imports]`
  （6 层，多 `nodes`）的"layer"数量不一致依然存在。

### 为什么这不是"代价高"，而是"不清晰"

- **两套权威打架**：task 账本说"结构契约已注册完成"，机器守卫曾判失败，读者不知道该信谁。
- **存在文档明文禁止的第二真相源**：policy 说不得有独立 import matrix，checker 源码里却有一张，且不在
  registry 里；改结构时没有导航告诉你要同步这处。
- **报错文本指向错误的真相源**：ERROR 说"must match the project-structure requirement"，但列出的期望值来自
  checker 源码，不是 `project-structure.toml`。

### 关联的不一致（同一根因，本次一并记录）

- `harness` 一词同时指 `deerflow/backend/packages/harness`（框架包）与 `deep_research_harness/`（应用目录），
  尽管 CONTEXT.md 在术语层区分了 "Deep Research Harness" vs "DeerFlow Harness"。
- submodule 身份三处三种说法（见根 README/AGENTS.md vs `.gitmodules` vs `git submodule status`），
  运行基座的"当前 commit"无法从文档唯一确定。这条与本 plan 主根因无关，单独立项处理，不混入。

## 决策 / 方案

### 1. 止血 ✅ 已完成（commit `feb5549`）

给 `check_project_architecture.py:44` 的 `REQUIRED_IMPORT_POLICY["runtime"]` 补上 `httpx_sse`，守卫转绿，
`wire-harness-observability-entrypoints` 的 task 5.1 已满足并归档。

这一步只是**承认现状**：checker 目前就是 import matrix 的真相源，toml 是它的投影。根因未除，见方案 2。

### 2. 根治（当前唯一待办，另开独立 change）

把 import matrix 收编到单一权威，消除 checker 里的第二真相源。两条路，推荐 B：

- **方向 A（轻，降级方案）**：承认 checker 硬编码矩阵是真相源，反过来改 `architecture-policy.md`，删掉
  "must not contain an independent import matrix"，新增"改 `[imports]` 必须同步改 `REQUIRED_IMPORT_POLICY`"
  指引 + 一个契约测试把两者锁死。
  - 优点：改动小。缺点：保留"两处真相 + 一处防漂移测试"的别扭结构，与"单一权威"自相矛盾。

- **方向 B（根治，推荐）**：`project-structure.toml` 的 `[imports]` 成为唯一权威；checker 只做机制性校验，
  不再硬编码每层允许的 namespace 全集。具体：
  1. 删除 `REQUIRED_IMPORT_POLICY`，改为校验结构性事实：`[imports]` 的 key 集合恰为 `INTERNAL_LAYERS`；
     每个值都是合法顶层 namespace（白名单 = 内层 + `stdlib`/`pydantic`/`deerflow`/`langchain`/
     `langgraph`/`httpx`/`httpx_sse`/`openai`）；层之间引用不存在未声明的层。
  2. `httpx_sse` 并入 namespace 白名单（它已是 locked 依赖）。
  3. 新增/调整契约测试，断言 checker 源码不再含每层 namespace 全集硬编码（防回归到方向 A 的两真相状态）。
  4. 统一 `ownership_layers` 与 `INTERNAL_LAYERS` 语义：要么把 `nodes` 显式标注为"import 层但非所有权层"，
     要么让 `ownership_layers` 也包含 `nodes`。二选一写进 policy，消除"5 层 vs 6 层"歧义。
  - 优点：真正兑现 `architecture-policy.md` 的承诺，回归单一权威。
  - 缺点：动 checker 核心校验逻辑，需回归到现有全量架构测试，成本高于 A。

**当前进度**：方案 1 已随 `wire-harness-observability-entrypoints` 归档完成；下一步是独立 change 做方向 B。
方向 A 只在"方向 B 被判定太重/风险过高"时启用。

## 风险 / 取舍

- [止血被当成已解决，根治无人跟进] -> 本 plan 保留"根治是当前唯一待办"状态，落地关联写明 change 名，
  不因止血已提交而关闭本 plan。
- [方向 B 删硬编码表时误删其他校验] -> 先跑 `make verify` + `check_project_architecture.py` 全量回归，
  保留 `INTERNAL_LAYERS` 与 namespace 白名单语义，只删"每层允许全集"这一层重复事实。
- [namespace 白名单本身又成了第二真相源] -> 白名单只声明"哪些是合法顶层命名空间"（checker 本就该知道的
  机械事实），不声明"每层分别允许什么"（toml 的语义），职责不同，不算重复权威。
- [改 checker 属 governance 边界，触碰需谨慎] -> 走 OpenSpec change，primary owner 选
  `openspec/governance/check_project_architecture.py` 及其契约测试 seam，不碰 `deerflow/`。

## 落地关联

- ✅ **止血已完成**：commit `feb5549` 在 `wire-harness-observability-entrypoints` 内给 checker 的
  `REQUIRED_IMPORT_POLICY["runtime"]` 加了 `httpx_sse`，守卫转绿，该 change 已归档
  （`openspec/changes/archive/2026-08-16-wire-harness-observability-entrypoints`）。
- **下一步**：新开 OpenSpec change（建议 slug 形如 `consolidate-import-matrix-authority`）执行方向 B；
  primary owner = `check_project_architecture.py` + `project-structure.toml` + 对应契约测试。吸收本 plan 的
  结论后可关闭本 plan（`git mv` 到 `_done/_closed_plans/`）。
- **不依赖**：本 plan 与 `runtime-operator-logs-and-live-trace.md`、`narrow-scripted-real-workflow-debug-path.md`
  无耦合，可独立推进。
