# Progressive Plan: CLI/TUI Entry Integrity Repair

> 类型: 渐进落地计划 | 状态: active -- research 已收敛，尚未创建 OpenSpec change | 更新: 2026-08-09
>
> 目标: 恢复入口所声明的实际 composition，并用逐阶段、可停止、可验证的方式修复
> scripted policy、demo graph、inspection command、local environment 与入口说明。

## 这份 Plan 的角色

这是本议题唯一的进度与 change-admission 清单。研究结论固定在
[`cli-tui-entry-integrity-repair-research.md`](cli-tui-entry-integrity-repair-research.md)：它是
事实、出处和反证的记录；本文件是据此决定**下一步做什么、何时可进入下一步、如何记录进度**。

它不授权直接改产品代码，也不取代 OpenSpec main specs。每个未完成阶段都必须先建立一个
OpenSpec change，再按该 change 的 proposal/design/spec/tasks 实施、验证、同步并归档。

```text
research facts + agreed decisions
              |
              v
Stage 1: runtime policy
              |
              v
Stage 2: demo composition
              |
              +--> Stage 3: inspection command
              |
              +--> Stage 4: local environment
                         |
                         v
Stage 5: entry-surface documentation
                         |
                         v
                    close this plan
```

一次只激活一个 OpenSpec change。Stage 3 和 Stage 4 没有行为因果依赖，但为避免同时改
Makefile、文档和 test gate，默认按本文件编号串行推进。

## 已收敛的决定

这些决定来自原 plan 的已确认产品定位，加上研究中的可证实反例；后续 proposal 应把它们当作
约束，而不是重新从 presentation 文案推导 runtime authority。

| 主题 | 已采用的决定 | 不能做什么 |
| --- | --- | --- |
| Scripted policy | 仅受信任 runtime context 可启用闭合的 non-interactive policy；正常 public 调用仍为 interactive。policy 经 typed action input 进入初始 graph state，随后只由 Bundle checkpoint 持有。 | demo/CLI 不得自己回答 HITL、伪造 profile 或取得 graph route authority。 |
| Full-fake 与 fixture graph | 保留现有 `make demo` / `make demo-scripted` 的 full-fake 合同。fixture graph 必须是一个**新且明确命名**的 verification route；它不得被包装成旧命令的无行为变化修复。 | 不得静默把 full-fake 命令换成 fixture graph，也不得让 README 的“fixture”措辞覆盖 main spec。 |
| Real demo | real CLI/TUI 必须由 demo runtime module 选择 all-real recipe、bridge 和 `BundleGraphExecutor`；少了 executor 必须 fail closed。 | generic probe host 不得冒充 lifecycle composition，也不得以 generic completion 声称完成 research。 |
| Inspection | canonical grammar 是 `make demo-sessions DEMO_ARGS="inspect <bundle-id>"`，并且从 Harness root 可执行、只读。 | renderer、parser、README 与 local operations 不得各自定义不同 grammar。 |
| Local environment | `make install` 和 `make profile-setup` 是显式环境准备 owner。普通入口不许改 `uv.lock` 或 project `.venv`；允许生成各自声明的 ignored run/diagnostic artifacts。 | 不得把 `--locked --no-sync` 当作 fresh-lock guarantee；`--no-sync` 隐含 `--frozen`，因此 fresh-lock 由独立 `make lock-check` 负责。 |
| Surface positioning | Dedicated Agent + reflected `deep_research` tool 是当前普通用户入口；Operator CLI 和 standalone demo TUI 是 contributor/operator surface；Primary User TUI 是计划中的未来产品。 | 不得把 demo TUI 宣布成当前 production Primary User Interface，或把 workbench 扩展为 real-profile / recovery authority。 |

## 进度规则

本文件的 **TODO List 是唯一 checkbox 清单**。它不以讨论、文件存在或单个 unit test 作为完成；
勾选每项时必须在该项末尾追加 OpenSpec change、验证命令和 commit/归档路径（适用时）。

- 只完成当前阶段的 Exit Gate 后，才可创建下一个依赖阶段的 proposal。
- 若 source、main spec、测试和 live observation 互相矛盾，停止勾选并先把结论补回 research；
  文档不得替代行为修复。
- 每个行为 change 都先写最低责任的 red test，再实现 green；真实 provider/model 只能作为
  补充 canary，不能替代 deterministic composition evidence。
- `deerflow/` 仅通过公开 Harness API 被 leverage；不阅读或修改其源码。
- 每个阶段结束都更新这份 TODO List 的状态、证据链接和“下一个未完成项”；这就是 progress 的
  唯一可读入口。

## TODO List

### Stage 0: 收敛与准入

- [x] 0.1 以第一方 main specs、Harness source/tests 和官方 `uv` 文档完成研究，保留
  [`cli-tui-entry-integrity-repair-research.md`](cli-tui-entry-integrity-repair-research.md)。
- [x] 0.2 将 E1--E4 的静态因果事实与未复现的历史运行数字分开：0.4 秒、`85 passed` 和并发
  `.venv` contention 只作为后续 change 的待重放 evidence，不能写成已重新证明的事实。
- [x] 0.3 选择保守的 full-fake/fixture-graph 分界，以及独立 lock-consistency gate；这两项取代
  原 plan 中与 main spec 或 `uv` 语义冲突的表述。
- [x] 0.4 运行 `openspec list --json`，确认没有 active change 后，为 Stage 1 创建唯一 active
  change；change: `restore-noninteractive-policy-propagation`；proposal:
  [`openspec/changes/restore-noninteractive-policy-propagation/proposal.md`](../../openspec/changes/restore-noninteractive-policy-propagation/proposal.md)；验证:
  `openspec list --json` 和 `openspec status --change restore-noninteractive-policy-propagation --json`。

**Stage 0 Exit Gate:** 研究与本计划不再对同一行为给出相反指令；Stage 1 的 primary owner、
证据 seam、非范围和 acceptance criteria 可以写成一个不依赖 demo workaround 的 proposal。

### Stage 1: Restore Non-interactive Policy Propagation

候选 change: `restore-noninteractive-policy-propagation`。

| Change Focus | 内容 |
| --- | --- |
| Primary module / causal owner | `deep_research_harness/src/deerflow_deep_research/runtime/` 中 `BundleControl` / `BundleGraphExecutor` 的 trusted action-input 到 initial graph-state boundary。 |
| Question | 如何让完整且受信任的 policy 经 validated input 写入一个 Bundle 的初始 graph state，并由同一 checkpoint 在 resume/refine 后继续拥有？ |
| Necessary adjacent contracts | `tool.py` 只做 trusted runtime admission；`run_experience.py` 只投影 scripted intent；HITL1/HITL2 只消费 checkpointed policy。 |
| Evidence seam | production `run_deep_research()` + actual `BundleGraphExecutor` + controlled external adapters 的 deterministic lifecycle test。 |
| Not in scope | demo recipe selection、CLI/TUI presentation、任意 caller-selected graph route、`deerflow/` source。 |

- [x] 1.1 用 `openspec new change` 创建 change，并完成 proposal、design、affected spec delta 和
  tasks；Focus Card 明确 policy 的 trusted input、state writer、checkpoint owner 和 legal
  blocked outcome。change: [`restore-noninteractive-policy-propagation`](../../openspec/changes/restore-noninteractive-policy-propagation/)；验证:
  `openspec status --change restore-noninteractive-policy-propagation` 和
  `openspec validate restore-noninteractive-policy-propagation --strict` （均已通过）；下一项: 1.2。
- [ ] 1.2 先写 red evidence：interactive 调用不受影响；缺失/不完整/非布尔 policy 被拒；完整
  trusted policy 从 tool admission 到 initial graph values；重启/resume 不重新注入 policy。
- [ ] 1.3 实现闭合 validated action input：`ResearchRunExperience` 同时投影 explicit
  `non_interactive=True` 与完整 policy；tool boundary 校验两个 key 都是 `True` 布尔值；executor
  将其一次性写入初始 state。
- [ ] 1.4 实现已拥有 spec 的 graph behavior：HITL1 auto-profile 保留 pair/language admission，
  HITL2 在 `auto_proceed=True` 时 `proceed` 并记录 audit note；无效 scripted input truthfully
  `GATE_BLOCKED`。
- [ ] 1.5 运行 change 的最低责任 tests、strict OpenSpec validation、相关 requirement-evidence
  check；完成后同步 main specs、归档 change，并在此记录证据。

**Stage 1 Exit Gate:** scripted valid input 无 stdin 地走实际 graph-owned path；无效输入被
truthful block；interactive path 和 checkpoint durability 都有 deterministic evidence。没有这一关，
不得开始 Stage 2 的 scripted-real completion claim。

### Stage 2: Restore Demo Graph Composition

候选 change: `restore-demo-graph-composition`；依赖 Stage 1。

| Change Focus | 内容 |
| --- | --- |
| Primary module / causal owner | `deep_research_harness/scripts/_demo_core.py` 的 demo runtime composition module。 |
| Question | 如何让 real demo 选择并执行 all-real recipe，而明确的新 fixture-graph route 选择 fixture recipe，同时保留旧 full-fake command 的既有合同？ |
| Necessary adjacent contracts | `runtime/research.py` recipe factories、`BundleGraphExecutor` trusted constructor seam、`run_deep_research()` executor injection、Stage 1 policy contract。 |
| Evidence seam | production `DemoLifecycleTransport` + demo runtime factory 的 composition test；external model/web adapter 可替换，graph/bridge/checkpoint/final delivery 不可替换。 |
| Not in scope | 改变 full-fake `make demo*` 合同、给 CLI 暴露 recipe/checkpoint/executor 参数、修改 public tool authority。 |

- [ ] 2.1 创建 change，并先在 proposal/design 中固定新 fixture-graph verification route 的名称、
  `--help`/README 定位和与 full-fake 命令的区别；需要新 requirement 时先写 delta。
- [ ] 2.2 写 red composition tests：transport 当前未注入 executor；real path 的 generic fallback
  不能被报告为 completed；fixture-graph 和 all-real recipe 的选择必须从真实 entry path 观察到。
- [ ] 2.3 实现深的 `build_demo_runtime(mode, adapter)` 类 boundary：在内部选择 recipe、bridge、
  executor 和 transport binding；probe host 只留下真实 `infra_probe` seam。
- [ ] 2.4 修复 scripted-real bounded smoke question，使其含有明确 comparison pair 和 supported
  language evidence；在 controlled external adapters 下证明 actual trace、checkpoint 和 required
  final delivery/report evidence。
- [ ] 2.5 保留 full-fake route 的 existing deterministic behavior，新增 fixture-graph route 的专属
  process/composition evidence；真实 CLI/TUI 都经共享 runtime module，缺 executor fail closed。
- [ ] 2.6 完成 focused tests、strict validation、deterministic project gate 和必要的 bounded live
  canary；同步 specs、归档 change，并在此记录证据。

**Stage 2 Exit Gate:** 每个叫作 real 或 fixture-graph 的入口都实际执行对应 recipe；旧 full-fake
入口仍满足现有 spec；没有 report/terminal evidence 的 generic completion 会使测试失败。

### Stage 3: Repair Rendered Inspection Command

候选 change: `repair-rendered-inspection-command`。

| Change Focus | 内容 |
| --- | --- |
| Primary module / causal owner | `deep_research_harness/scripts/demo_sessions.py` 的 read-only inspection command interface。 |
| Question | 如何让 shared command projection、parser、docs 和 subprocess 共同实现唯一的 `inspect <bundle-id>` grammar？ |
| Evidence seam | 从 `deep_research_harness/` 启动的 real subprocess contract，使用 retained observation fixture。 |
| Not in scope | lifecycle recovery、Bundle discovery、session reference、provider/graph control authority。 |

- [ ] 3.1 创建 change 和 red subprocess test；从 Harness root 执行 renderer 给出的 command，确认
  当前 parser failure 被重现。
- [ ] 3.2 实现唯一 `inspect <bundle-id>` grammar；available observation 返回 0，missing/corrupt
  返回 bounded nonzero，且双方均不创建 graph/provider authority。
- [ ] 3.3 让 renderer、`--help`、README 和 `docs/local-operations.md` 只使用这一个 grammar；
  删除一参数同义形，不保留两套 contract。
- [ ] 3.4 完成 subprocess/read-only regression、strict validation 和 gate；同步 specs、归档 change，
  并在此记录证据。

**Stage 3 Exit Gate:** 人复制 CLI/TUI 显示的 inspection command 即能运行；所有输出仍是有限的
observation，不暗示 resume/retry/recovery。

### Stage 4: Stabilize Local Entry Environment

候选 change: `stabilize-local-entry-environment`。

| Change Focus | 内容 |
| --- | --- |
| Primary module / causal owner | `deep_research_harness/Makefile` 的 local command-environment interface。 |
| Question | 如何让显式 setup 拥有 lock/environment mutation，而 ordinary entry 在已准备环境中不修改 `uv.lock` 或 project `.venv`？ |
| Evidence seam | clean-copy subprocess contract：setup 后依次运行 supported `--help`、fixture/full-fake、profile check 和 inspection，并比较 tracked lock 与 environment state。 |
| Not in scope | 修改 DeerFlow source、让 normal entry 自动 refresh lock/sync、禁止声明的 ignored run artifacts、替换部署工具。 |

- [ ] 4.1 创建 change；用受审查的 Harness dependency metadata 刷新 `uv.lock`，使 clean checkout
  的 `uv lock --check` 成功。该 repository update 不是 ordinary runtime command。
- [ ] 4.2 把 `make install` 定义为所有支持的 CLI/TUI extras 的同步 owner（包括 `demo-real`），保留
  `make profile-setup` 的明确 profile setup 职责。
- [ ] 4.3 让普通 entry 使用 no-sync execution，并加快速 deterministic preflight：缺 extra 时只
  指向 `make install`；`make lock-check` 独立检查 freshness，不能依赖 `--no-sync` 或混用 flags
  来伪造检查。
- [ ] 4.4 建立 clean-copy/process regressions，证明普通命令不改 `uv.lock` 或 project `.venv`；
  对被允许的 ignored diagnostics/run bundles 明确列出例外。
- [ ] 4.5 运行并发 read-only/help smoke；若某组合不能并发，明确 fail closed 与 setup action，而不
  报告不可靠的成功。
- [ ] 4.6 完成 lock check、focused environment tests、`UV_OFFLINE=1 make verify`、strict validation，
  同步 specs、归档 change，并在此记录证据。

**Stage 4 Exit Gate:** `make install && make lock-check` 在 clean checkout 通过；普通入口不会
修改 dependency state，且缺依赖时给出明确的 setup action。

### Stage 5: Document Entry Surfaces

候选 change: `document-entry-surfaces`；依赖 Stage 1--4 的已验证当前事实。

| Change Focus | 内容 |
| --- | --- |
| Primary module / causal owner | `deep_research_harness/README.md` 的 product/agent information map。 |
| Question | 如何让首次读者在一屏内区分 current user route、operator CLI、demo TUI、full-fake/fixture-graph verification route 和 local workbench，并前往唯一的细节 owner？ |
| Evidence seam | README routing review + command/document process evidence already established by Stages 2--4。 |
| Not in scope | 新建第二份行为 registry、把 README 变成操作手册、把未来 Primary User TUI 写成 current runnable surface。 |

- [ ] 5.1 创建 documentation change；在 proposal 中引用前四阶段的已归档 evidence，而不把旧计划或
  README 文案当成行为证明。
- [ ] 5.2 用 `Entry Surfaces` 表替换当前过浅的 entry table，逐项给出 primary reader/user、purpose、
  actual composition 与 explicit non-goal。
- [ ] 5.3 将 exact commands 链接到 `docs/local-operations.md`，authority/composition 链接到
  `docs/runtime-architecture.md`，测试/verification 链接到 testing docs；不复制第二份手册。
- [ ] 5.4 校准术语：普通用户走 Dedicated Agent + reflected tool；Operator CLI 非 versioned product
  CLI；demo TUI 是 visualizer；Primary User TUI 是 future；workbench 仅当前 fixture profile。
- [ ] 5.5 运行 information-map/governance checks、link/command evidence、strict validation 和
  deterministic project gate；同步 relevant specs、归档 change，并在此记录证据。

**Stage 5 Exit Gate:** README 没有制造新的 authority，却使新读者和 Coding Agent 能在一屏内选择
正确 surface，并能追到精确命令、架构说明和已验证的行为 contract。

## Completion And Stop Conditions

本计划只有在五个 changes 全部归档、main specs 已同步、每个 Exit Gate 有链接的 deterministic
evidence，并且 `cd deep_research_harness && UV_OFFLINE=1 make verify`、strict OpenSpec validation 与
`git diff HEAD --check` 都通过时才可关闭。

出现以下任一情况时暂停当前阶段，保持后续 checkbox 未勾选，并先更新 research/当前 proposal：

- main spec 要求的行为与已验证实现不相容；
- 为让 demo 通过而需要给 presentation 新的 lifecycle、route 或 checkpoint authority；
- 一个 ordinary command 需要隐式 sync/lock 才能运行；
- “completed” 无法由 actual graph trace 和 required delivery evidence 支撑；
- 需要读取或修改 `deerflow/` source 才能继续。

完成后将本文件移入 `_backlog/_done/_closed_plans/`，按目录流程分配 CLS id；研究笔记保留为
这条计划的第一方审计记录。
