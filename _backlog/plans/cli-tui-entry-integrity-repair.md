# Plan: 恢复 CLI/TUI 入口完整性与可发现性

> 类型: 设计 / 修复计划 | 更新: 2026-08-09 | 状态: Grill 已确认，待建立 OpenSpec changes
>
> 目标: 让每个被称为 fixture、all-real、CLI 或 TUI 的入口真正执行它声明的
> composition，并让人和 coding agent 能在一个简洁入口中理解这些 surface 的角色、
> 运行方式和非目标。

## 背景 / 现状

2026-08-09 对 `deep_research_harness/` 的实际 CLI 巡检发现，参数帮助、fixture
presentation、profile 命令和现有 Textual pilot 测试大多可运行，但关键的 demo execution
contract 已经和代码脱节。最严重的问题不是 presentation 文案，而是 composition 没有接入
真实 research graph。

本计划是分析与实施分组，不是行为 authority。要求行为仍由 OpenSpec 主规格及后续 delta
spec 负责；实际实施必须在 `openspec/changes/` 中逐个 change 完成。

## Grill 已确认决定

> 本节记录设计访谈已经确认的结论，并在本次 Grill 完成后统一写回实施分组。它不替代
> OpenSpec main spec 或后续 owning delta 的行为 authority。

1. **Scripted policy 是共享 runtime capability。** 正常 public 调用仍默认交互式；只有受信任
   runtime context 明确给出 closed non-interactive policy 时，reflected tool 和 standalone demo
   才走同一条 graph-owned automatic policy path。demo 不得自己回答 HITL 或绕过 graph。
2. **拆分当前 Change 1。** `restore-noninteractive-policy-propagation` 先以 runtime policy
   admission/projection 为 primary causal owner；`restore-demo-graph-composition` 随后以
   `scripts/_demo_core.py` 为 primary causal owner。两者均为 P0，后者依赖前者完成 scripted
   real workflow 的完整证明。
3. **普通入口不得隐式修改环境。** `make install` 安装全部受支持的 Harness CLI/TUI extras；
   `make profile-setup` 作为显式 profile setup owner 可以准备环境。其余 demo、profile、
   workbench 和 inspection 命令使用 locked, no-sync 环境；缺少依赖时只报告明确 setup 动作。
4. **入口定位区分当前与规划。** Dedicated Agent + reflected `deep_research` tool 是当前推荐的
   ordinary-language user route；standalone demo TUI 是 contributor/operator visualizer；dedicated
   Primary User TUI 是未来产品方向，不作为当前可运行入口。
5. **Operator CLI 是操作合同，不是 public product CLI。** 它必须对当前 Harness 的 smoke、debug
   与 scriptable operational work 保持可执行的命令和可信 exit semantics，但不承诺对外版本化的
   参数、输出或长期兼容性。
6. **Local Session Workbench 只陈述当前 fixture profile。** 它是固定 local-profile 的 Operator
   Interface，用于有界 observation 与 legal control projection；real local profile 不属于本次计划
   或当前产品能力。
7. **环境隔离与 Entry Surfaces map 分为两个 change。** `stabilize-local-entry-environment` 以
   Makefile/locked environment 为 owner 并证明命令不污染环境；`document-entry-surfaces` 在行为
   repair 后以 README information map 为 owner，证明当前入口定位和文档路由。两者不得互相阻塞。

### 已复现事实

| ID | 严重度 | 可执行事实 | 当前合同冲突 |
| --- | --- | --- | --- |
| E1 | P0 | `make demo-real` 通过凭据预检并收到 profile 后约 0.4 秒直接 `completed`，没有 topic planning、model、Tavily、report 或真实 trace | Makefile 声称 full 11-phase actual LLM + Tavily；`demo-pipeline` 和 `research-demo-tui` 要求 all-real recipe |
| E2 | P0 | `make demo-real-scripted` 稳定停在第一个 HITL1，并以“自动策略未能完成图拥有的输入请求”失败 | `research-cli-onboarding` 要求 scripted route 无 stdin，并沿 graph-owned non-interactive policy 到 terminal/fault |
| E3 | P1 | CLI/TUI 渲染 `make demo-sessions DEMO_ARGS="inspect <bundle-id>"`，实际 parser 只接受一个 `<bundle-id>`，命令确定 argparse 失败 | `research-cli-onboarding` 明确要求渲染命令可从 Harness 根执行且只读 |
| E4 | P1 | 干净工作区执行 `uv lock --check` 失败；普通 demo target 会重写 tracked `uv.lock`，并发 `uv run` 还会竞争共享 `.venv` | README 和 `local-operations` 声称命令使用 locked project environment |
| E5 | P1 | CLI/TUI focused suite 为 `85 passed`，但没有发现 E1-E4 | 现有测试对 terminal/命令字符串/recipe 分别断言，没有跨真实 composition seam 验证可执行结果 |
| E6 | 设计缺口 | README、CONTEXT、runtime architecture 和 local operations 都提到入口，但没有一处用一屏说明“谁使用哪个 surface、它执行什么、它不是什么” | 人能找到命令，却难以建立 CLI、demo TUI、未来 Primary TUI、public Agent/tool、workbench 的统一心智模型 |

### 根因图

当前 lifecycle 调用路径：

```text
demo_real.py / demo_tui.py
        |
        v
ResearchRunExperience
        |
        v
DemoLifecycleTransport
        |
        | passes host_factory only
        v
run_deep_research
        |
        | BundleControl receives no BundleGraphExecutor
        v
full-fake lifecycle fallback
        |- start  -> one generic suspension
        `- resume -> completed without research
```

`build_real_demo_recipe()` 和 `build_fixture_demo_recipe()` 都存在，但没有进入上述生产 demo
调用路径。`build_demo_host()` 自己的 docstring 也明确说明它只是 generic probe host，不负责
lifecycle composition。

scripted policy 另有两段丢失：`ResearchRunExperience` 构造了
`non_interactive_policy={auto_profile, auto_proceed}`，但没有同时投影 trusted
`non_interactive=True`，所以 tool admission 不会把该调用当成 non-interactive；即使补齐该
admission，`BundleControl` / `BundleGraphExecutor` 的 start interface 仍没有接收并把 policy
写入 initial graph state。policy 必须从 initial state 随 Bundle checkpoint 保留，后续 resume/refine
继续同一 checkpoint，不能由 presentation context 重新注入。

### 历史结论为何没有保护当前行为

- 已归档 `deep-research-demo-full-pipeline` 明确选择 real 模式经
  `ResearchGraphRecipe` 正路执行；当前 factory 只剩独立单元测试。
- 已关闭 BUG-015 曾记录“渲染 inspection command 后真实执行”的 integration test；当前迁移后
  只剩命令字符串断言，parser 与主规格不再一致。
- `test_scripted_cli_is_stdin_free_and_preserves_explicit_question` stub 了整个
  `ResearchRunExperience` 并直接返回 completed，能证明 presentation 不读 stdin，但不能证明
  transport、BundleControl、executor 或 graph policy。
- recipe 测试只证明 recipe 内 adapter kind 是 all-real，不证明任何入口使用该 recipe。

这是一类 evidence authenticity 回归：各零件分别“存在且测试通过”，组合后的用户合同却不
成立。

## 决策 / 方案

### 决策 1: 把 demo runtime composition 做成一个深 Module

当前 `DemoLifecycleTransport.bind(adapter, host)` 的 interface 允许 caller 传入一个只能处理
probe 的 host，却把它当作 lifecycle 已就绪。该 Module 太浅，caller 必须知道 host、recipe、
executor 和 mode 之间的隐含关系。

目标 interface 应只暴露 caller 真正需要选择的事实：

```text
build demo runtime(mode=fixture|real, adapter)
        -> lifecycle transport ready for Start/Answer/Cancel/Status
```

Module implementation 内部负责：

1. fixture mode 构造完整 fixture recipe；
2. real mode 构造 all-real recipe 和 demo-local bridge；
3. demo runtime factory 从 recipe 构造 `BundleGraphExecutor`；
4. lifecycle dispatch 把 executor 注入 `run_deep_research()`；
5. probe host 只保留在确实调用 `infra_probe` 的内部 seam，不再冒充 lifecycle composition；
6. real mode 缺 executor 时 fail closed，绝不退到 full-fake lifecycle 后报告 completed。

具体函数/类型名称由 change 的 design 决定，不要求为一次调用增加多层 pass-through。删除这个
Module 后 composition 复杂度应重新散落到 CLI、TUI 和 tests，说明它确实提供了 depth 与
locality。

### 决策 2: scripted policy 通过一个 typed action-input interface 入图

`scripted` 是 presentation 选择，graph 只应接收可信、闭合的 non-interactive policy。它是
reflected tool 与 standalone demo 共享的 trusted runtime capability：正常 public 调用仍默认
interactive。后续 runtime change 必须恢复从 trusted runtime context 到 initial graph values 的单一路径，
并明确：

- public reflected tool 和 standalone demo 共享同一 admission rule；
- policy 缺失或不完整时保持 `interactive_required`；
- policy 完整时 HITL1/HITL2 按 `runtime-operations` 已有的确定性 auto-profile/auto-proceed
  requirement 执行；当前 HITL2 未消费 `auto_proceed` 也是待修复 implementation gap；
- policy 不赋予 CLI 写 profile、伪造 response 或选择 graph route 的 authority；
- policy 只在 start 时经 typed action input 写入 initial graph state，之后由同一 Bundle checkpoint
  保留；resume/refine 不携带或重建它。

当前 scripted 默认问题“Compare the evidence for two approaches...”没有明确 comparison pair，
按现有 `runtime-operations` 规格本应 non-interactive blocked。默认 scripted question 也要改成
包含两个明确 subject 和支持语言证据的 bounded smoke question，避免修好 policy 后仍由合法
admission 拒绝。

### 决策 3: fixture、real、scripted 三种声明都必须由执行证据证明

- `fixture` 表示 graph 使用完整 fixture recipe，不只是 presentation 没有凭据。
- `real` 表示 graph 使用 all-real node composition；deterministic test 可以替换真正的 external
  model/tool adapter，但不能替换 graph、bridge、assembly 或 lifecycle Module 后仍声称 all-real
  workflow。
- `scripted` 表示 no-stdin policy，不表示 fake graph，也不允许 CLI 自己回答 graph prompt。
- `completed` 必须有 terminal lifecycle state，并且对于 real research 还要有 required final
  delivery/report evidence；一次 generic HITL response 后直接 completed 必须测试失败。

### 决策 4: copyable command 用真实 parser/process 证明

主规格当前选择的 canonical shape 是：

```bash
make demo-sessions DEMO_ARGS="inspect <bundle-id>"
```

因此优先方案是让 `demo_sessions.py` 明确支持 `inspect <bundle-id>`，并把 README 与 local
operations 的一参数示例同步为同一 shape。若讨论后决定删除 verb，则必须先修改 owning
OpenSpec requirement，再统一 renderer、parser、tests 和文档；不能只修字符串。

共享 projection 应同时提供受约束的 command arguments 与展示字符串；测试以 arguments 从
`deep_research_harness/` 启动 subprocess，而不是解析展示字符串或分别断言 renderer 和 parser。

### 决策 5: 只有显式 setup target 可以修改环境

建议的 command-environment interface：

- `make install` 是常规本地依赖同步 owner，并安装所有受支持 CLI/TUI 所需 extras；
- `make profile-setup` 是另一显式 profile setup owner；
- `make lock-check` 在干净 checkout 必须成功且不写文件；
- 普通 demo/profile/workbench/inspection targets 使用 locked、no-sync 环境，运行它们不会修改
  `uv.lock` 或 `.venv`；
- 如果某 target 需要未安装 extra，它应给出 `make install` 的简洁动作，而不是自行同步；
- 并发启动不同 CLI 不会因为多个 `uv run` 同时改共享 `.venv` 而互相破坏；
- refresh lock 只反映当前 editable DeerFlow harness 的已声明 metadata，不修改
  `deerflow/` submodule。

OpenSpec design 必须核实 `uv` 版本兼容和 `--no-sync` 对缺失 extra 的实际错误表现，再锁定
Makefile 细节。目标 invariant 比某个具体 flag 更重要：普通运行不改变项目依赖状态。

## 入口介绍放在哪里

### “看得懂”与“守得住”是两层

系统不应只靠一篇 README “记得 CLI/TUI 很重要”。需要两个互补层次：

1. **Orientation layer:** README 的一屏 surface map 让人和收到 product/demo/operator 任务的
   coding agent 快速知道有哪些入口、面向谁、执行哪种 composition，以及去哪里继续读。
   `AGENTS.md` 只负责把相关任务路由到 README、owning adapter/spec/test seam。
2. **Enforcement layer:** owning OpenSpec specs 声明可观察行为，test-evidence registry 把这些
   入口标为 `public entry` / 对应 authenticity claim，process-level tests 和 release gate 实际
   执行命令。这样漏接 executor、命令不可执行或运行污染 lockfile 会使 gate 变红，而不只是
   文档显得过时。

不建议再创建一份独立的 CLI/TUI YAML/Markdown registry。当前已有 README、OpenSpec、结构
registry 和 evidence metadata；再加一个只有单一 consumer 的浅 interface 只会制造第五份漂移
来源。只有未来至少两个真实 consumer 都需要机器读取同一 entry declaration 时，才重新评估
typed registry seam。

### 推荐默认方案

在 `deep_research_harness/README.md` 前部保留一个简短的 `Entry Surfaces` 表，作为人和 agent
第一次建立心智模型的地方。它应替换或深化当前 `Entry point | Recipe | Boundary` 表，而不是
另加一篇重复 overview。

建议表格只回答五件事：

| Surface | Primary reader/user | Purpose | Composition | Explicit non-goal |
| --- | --- | --- | --- | --- |
| Dedicated Agent + reflected `deep_research` tool | ordinary user / integrating Agent | 推荐的自然语言 lifecycle 入口 | all-real public runtime | 不是 demo 或本地诊断 |
| Operator real CLI | contributor/operator | smoke、debug、scripted operational run | all-real graph | 不是 Primary User product UI |
| Standalone demo TUI | contributor/operator | 可视化验证 shared run experience | real 或显式 fixture | 不是 production Terminal Workbench，也不自动等于未来 dedicated Primary TUI |
| Fixture CLI/TUI | contributor | 零凭据 lifecycle/workflow verification | fixture graph | 不产生真实 research outcome |
| Local session workbench / retained observation | operator | 有界查看和合法控制投影 | selected local profile / read-only observation | 不是 recovery authority 或 filesystem explorer |

详细内容继续分层：

- `README.md`: 一屏产品与入口 orientation，加 Reading Map；不复制完整命令手册。
- `docs/local-operations.md`: 精确命令、前提、exit semantics、凭据和故障操作。
- `docs/runtime-architecture.md`: surface 如何共享 typed Bundle result，以及 composition/authority
  归属；不放逐条运行命令。
- `CONTEXT.md`: 保留 Primary User Interface、Operator Interface、Integration Interface、Host
  Terminal Workbench 等 ubiquitous language；不作为命令目录。
- `AGENTS.md`: 继续只做 focus gate。它已经把 product/demo/operator journey 路由到 README，
  不应再复制一份 CLI/TUI 介绍。
- OpenSpec capability specs: 拥有 required observable behavior，不能由 README 成为第二 authority。

这个放置符合现有 Agent Information Map policy：README 负责 product orientation 和 quick
start，细节留在 focused docs。README 当前 124 行，远低于 200 行 warning，但新增表格后仍应
保持简短。

### 已确认的入口定位

- Dedicated Agent + reflected tool 是当前 recommended ordinary-language user route。
- standalone demo TUI 是 contributor/operator visualizer，不是 current Primary User Interface。
- dedicated Primary User TUI 是未来产品方向，不能写成当前可运行入口。
- Operator CLI 是 current Harness 的操作合同，不是 versioned public product CLI。
- Local Session Workbench 只陈述当前 configured fixture demo profile；real local profile 留给未来
  approved change。

## 实施分组

E5 不是第五个实现 owner：它是每个 change 都必须补齐的 evidence authenticity 缺口。每个 change
先建立自己的 red-capable feedback loop，不能由最后的 project gate 代替。

### Change 1: `restore-noninteractive-policy-propagation`

**目标:** 修复 E2，恢复 shared trusted non-interactive policy 的 admission、initial-state
projection 和 checkpoint durability。

**Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/`
中由 `BundleControl` / `BundleGraphExecutor` 承载的 research action-input 到 graph-state boundary。

**必要相邻 interface:** `tool.py` 只验证 trusted runtime context；`run_experience.py` 只把
`StartRun(scripted=True)` 投影为该 context；HITL1/HITL2 只消费 checkpointed policy，不能接收
CLI/TUI route authority。

**必须先写红的反馈闭环:** 以 production `run_deep_research()`、实际 `BundleGraphExecutor` 和
controlled external adapters 启动 scripted run，证明 policy 经过 admission 写入 initial graph
state，并在 checkpoint/restart 后仍由 graph 消费。该 test 不经过 demo-specific workaround。

**实施任务:**

- [ ] 记录当前 `non_interactive=True` 缺失、policy 未入 initial state、HITL2 未消费
  `auto_proceed` 的 red evidence。
- [ ] 引入或恢复 closed typed action input，使完整 trusted policy 与 explicit non-interactive
  signal 一起到达 `BundleControl` / `BundleGraphExecutor.start()`。
- [ ] 在 `_initial_graph_state()` 写入 policy；resume/refine 只继续 Bundle checkpoint，不从
  presentation context 重建或覆盖 policy。
- [ ] 实现 `runtime-operations` 已有的 HITL1 auto-profile 和 HITL2 auto-proceed requirement，保留
  comparison/language admission、audit note 和 blocked outcome。
- [ ] 增加 interactive、缺失/不完整 policy denial、valid scripted completion、invalid default
  input blocked、checkpoint restart 的 deterministic tests。

**退出条件:** 普通 public start 保持 interactive；受信任 scripted start 在有效输入时不读 stdin；
无效 scripted input truthfully blocks；同一 Bundle 的 restart/resume 不获得新的 policy authority。

### Change 2: `restore-demo-graph-composition`

**目标:** 修复 E1 和 fixture/real composition authenticity；依赖 Change 1 的 runtime policy
contract，但不修改该 contract。

**Primary module / causal owner:** `deep_research_harness/scripts/_demo_core.py` 的 demo runtime
composition Module。

**必要相邻 interface:** `runtime/research.py` 的 recipe factory、`BundleGraphExecutor` 的 trusted
constructor seam、`run_deep_research()` 的 executor injection、以及 shared `ResearchRunExperience`
projection。probe host 仅保留给实际 `infra_probe` 用途。

**必须先写红的反馈闭环:** 通过 production `DemoLifecycleTransport` 和 demo runtime factory 启动两条
路径：fixture mode 穿过 actual fixture graph/HITL；scripted real mode 仅替换 external model/tool
adapter，同时保留 all-real recipe、bridge、graph、BundleControl、checkpoint 和 final delivery。

**实施任务:**

- [ ] 建立上述 composition tests，记录当前 executor 未调用、无 report 或意外 AwaitingInput 的输出。
- [ ] 设计并实现 `build_demo_runtime(mode, adapter)`，在内部选择 recipe、构造 executor 并完成
  transport binding；CLI/TUI 不再组装 host、recipe 或 executor。
- [ ] 删除 lifecycle path 对 probe-only host 的错误依赖，并在 real mode executor 缺失时 fail closed。
- [ ] 把 scripted default question 改成有明确 comparison pair 和 supported-language evidence 的
  bounded smoke input。
- [ ] 让 CLI real、CLI scripted、TUI real、TUI fake 都使用该 Module；保留纯 presentation test，
  但删除其 full-pipeline evidence claim。

**退出条件:** `make demo-scripted` 执行 fixture graph 并给出 truthful fixture outcome；deterministic
scripted-real test 有 actual trace 和 required report evidence；real TUI pilot 不 patch 整个
experience 为结果队列；任一 mode 都不能因漏接 executor 静默换 implementation composition。

### Change 3: `repair-rendered-inspection-command`

**目标:** 修复 E3，并恢复 BUG-015 的 executable-command evidence。

**Primary module / causal owner:** `scripts/demo_sessions.py` 的 read-only inspection command
interface。

**必要相邻 interface:** `_terminal_failure_presentation.py` 只使用 shared structured command
projection 渲染 copyable text；README/local operations 同步该已执行的 canonical command。

**实施任务:**

- [ ] 先写从 structured command arguments 启动的 subprocess red test，当前 `inspect <bundle-id>`
  parser 必须失败。
- [ ] 按 owning spec 实现唯一的 `inspect <bundle-id>` shape；不要保留一参数同义调用。
- [ ] 证明 available observation 返回 0，missing/corrupt 返回 bounded nonzero，且二者均不调用
  graph/provider 或获得 lifecycle authority。
- [ ] 同步 `--help`、CLI/TUI renderer、README、local operations 和 regression link，不改写归档事实。

**退出条件:** 每条 renderer 展示的 inspection command 都由 subprocess contract 执行，文档和
`--help` 完全一致。

### Change 4: `stabilize-local-entry-environment`

**目标:** 修复 E4，使 explicit setup 与 ordinary entry 的环境修改权可验证。

**Primary module / causal owner:** `deep_research_harness/Makefile` 的 local command environment
interface。

**实施任务:**

- [ ] 在不修改 `deerflow/` 的前提下刷新 Harness `uv.lock`，使 clean checkout 的
  `uv lock --check` 成功。
- [ ] 让 `make install` 安装所有受支持 CLI/TUI extras；保留 `make profile-setup` 作为显式 profile
  setup owner。
- [ ] 让普通 demo/profile/workbench/inspection target locked + no-sync；未安装 extra 时提供明确
  setup action，而不是自行同步。
- [ ] 建立 clean-copy/subprocess contract：setup 后逐个运行 `--help`、fixture scripted、profile
  check 和 inspection，并验证 tracked worktree 不变。
- [ ] 增加并发只读/help smoke，证明不会竞争 `.venv`；若某并发模式不支持，命令必须 fail closed
  并指出 setup owner。

**退出条件:** `make install && make lock-check` 在 clean checkout 通过；所有 supported ordinary
entry 之后 tracked worktree 保持干净；相关 tests、`UV_OFFLINE=1 make verify` 与 governance 通过。

### Change 5: `document-entry-surfaces`

**目标:** 修复 E6，在前四个 behavior change 建立事实后，把当前入口定位写成一屏 README
orientation，不创造第二行为 authority。

**Primary module / causal owner:** `deep_research_harness/README.md` 的 information map。

**必要相邻 interface:** 当前 `CONTEXT.md` vocabulary、local operations 的 exact commands、runtime
architecture 的 authority explanation、testing documentation，以及 Agent Information Map governance。

**实施任务:**

- [ ] 将现有 `Entry point | Recipe | Boundary` 表替换或深化为 `Entry Surfaces` 表，逐项说明 primary
  reader/user、purpose、composition 和 explicit non-goal。
- [ ] 将 Dedicated Agent + reflected tool 写为 current recommended route；将 standalone demo TUI、
  Operator CLI、fixture route 和 Local Session Workbench 按已确认的 current facts 描述。
- [ ] 把 planned Primary User TUI 明确标为未来方向，而非 runnable entry；不承诺 real local profile。
- [ ] README 只链接 local operations、runtime architecture 和 testing docs；docs index 保持一个
  focused-document route，不新建 product overview 或 registry。
- [ ] 更新 owning spec/delta 与 evidence registry，使 public entry claim 由 process evidence 而非
  文本存在支撑。

**退出条件:** 新读者在 README 一屏内能区分 current user route、operator CLI、standalone demo TUI、
fixture route 与 workbench，并知道精确命令和架构细节的唯一继续阅读位置。

## 验证梯子

| 层级 | 要证明的 claim | 允许替换 | 不足以替代它的证据 |
| --- | --- | --- | --- |
| Parser/process contract | 渲染命令从文档上下文可执行 | retained observation fixture | 字符串相等、直接调用 parser function |
| Composition integration | mode 选择正确 recipe/executor，policy 入 initial state | clock/random/local external adapters | 独立 recipe kind test、stub experience |
| Deterministic workflow | actual graph/bridge/checkpoint/HITL/final delivery 按序工作 | external model 和 web adapter | hand-built terminal、fixture-only lifecycle |
| TUI pilot | widgets 只消费 shared actual RunUpdate，并能完成对应 workflow | Textual test driver | 静态 render test |
| Live canary | 当前 credentials、model 和 Tavily 接线可到达有界真实 outcome | 无 | preflight 通过、deterministic fake |
| Project gate | lock、governance、lint、所有 deterministic suites 一致 | 无 | focused suite 单独通过 |

Live canary 只运行一条有界问题，并记录 bundle/diagnostic/report outcome。第三方失败是 supplemental
evidence，不把 deterministic green 变成 red；但未执行 graph 或无 report 的假 completed 必须是
release blocker。

## 风险 / 取舍

- [风险] 修复 executor injection 时意外改变 public reflected tool 的 lifecycle authority。
  -> 缓解：typed action input 和 executor seam 由 runtime Module 拥有；demo 只选择已批准 adapter，
  不新增 public 参数或 Bundle selector。
- [风险] fixture demo 从 fallback lifecycle 改为 fixture graph 后，现有输出和快速测试时间变化。
  -> 缓解：以 main spec 的 fixture recipe/trace claim 为准，记录 duration budget；若产品意图已变，
  必须先改 spec，不能让实现静默漂移。
- [风险] scripted 默认自动接受未由用户声明的事实。
  -> 缓解：只使用原始 question 中明确 pair/language 的 smoke input；继续遵守现有 deterministic
  admission 和 degraded-profile rules。
- [风险] 为测试方便把 internal seams 暴露给 CLI/TUI。
  -> 缓解：external model/tool adapter 是内部 seam；测试和 caller 都通过同一个 demo runtime
  interface，不让 CLI 接收 recipe、checkpoint path 或 arbitrary executor。
- [风险] lock refresh 吸收无关 upstream dependency 变化。
  -> 缓解：只基于 pinned DeerFlow submodule 当前 metadata 生成并审查 Harness lock diff，不读取或
  修改 submodule source。
- [风险] README 变成另一本操作手册。
  -> 缓解：只保留一屏 surface map；命令、architecture、testing 分别链接现有 focused owner，
  运行 Agent Information Map governance check。
- [取舍] 五个 change 比一个大修复有额外 OpenSpec 成本。
  -> 理由：runtime policy、demo composition、read-only command、local environment 与 entry
  documentation 有不同 causal owner 和独立 red loop。拆分防止 demo workaround 掩盖 public runtime
  defect，也防止文案或 lockfile 改动掩盖 P0 execution failure。

## 非范围

- 不修改或浏览 `deerflow/` framework source；只使用其已声明 package metadata 和 public
  Harness interface。
- 不把 standalone demo TUI 宣布为 production Primary User Interface。
- 不新增 Gateway/Web/IM surface，不修改 upstream Terminal Workbench。
- 不引入跨 Bundle registry、observation-backed recovery 或 path-based lifecycle authority。
- 不借修 CLI 重写 research graph topology、node prompts、provider policy 或 report quality 标准。
- 不用一次 credentialed success 替代 deterministic composition/workflow evidence。

## 落地关联

建议建立五个 OpenSpec changes：

1. `restore-noninteractive-policy-propagation`
2. `restore-demo-graph-composition`（依赖 1）
3. `repair-rendered-inspection-command`
4. `stabilize-local-entry-environment`
5. `document-entry-surfaces`（依赖 1-4 的已验证当前事实）

实施前先运行 `openspec list --json`，一次只激活一个 repair change。每个 proposal 都需要 Change
Focus card；预计涉及的 main specs 为：

- `demo-pipeline`
- `research-cli-onboarding`
- `research-demo-tui`
- `runtime-operations`
- `research-run-experience`
- `deep-research-harness-run-bundles`
- 文档 change 触发 `deep-research-agent-charter` / Agent Information Map policy

Change 1 必须先完成再开始 Change 2。Change 3 与 Change 4 没有因果依赖，可分别 admission；若
仍维持一次只激活一个 repair change 的工作方式，默认按列出的次序完成。Change 5 最后开始，确保
README 只陈述已验证的当前事实。五个 changes 均归档、main specs 同步、完整 gate 通过后，本 plan
才可移动到 `_backlog/_done/_closed_plans/` 并分配下一个 CLS id。
