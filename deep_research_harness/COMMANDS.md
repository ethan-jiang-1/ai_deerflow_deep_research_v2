# COMMANDS — 操作速查（Playbook）

> **一页纸速查：跑什么、用哪条命令、出事看哪。**
> 本文件只是**索引**，不是第二权威：命令的权威是 [`Makefile`](Makefile)，
> 操作细节的权威是各 runbook 与 [`docs/local-operations.md`](docs/local-operations.md)；
> 那里变了这里必须同一 PR 跟着改。
>
> 最后核对: 2026-09-12（对应当日 Makefile 形态）| 阶梯语义: [`docs/runbooks/README.md`](docs/runbooks/README.md)

## 0. 环境准备（一次）

| 命令 | 作用 |
| --- | --- |
| `make install` | `uv sync`（含 operations / demo-tui / demo-real extras） |
| `make entry-preflight` | 检查入口命令环境是否就绪（缺依赖会提示先 install） |

真实跑需要 `.env` 三要素：`DEERFLOW_DEMO_MODEL`（非空 selector）+ 匹配模型凭证
（如 `DEEPSEEK_API_KEY`）+ `TAVILY_API_KEY`。**不在终端检查/打印值**；各真实入口
自带 safe preflight，只报缺失类别。

## 1. 跑法阶梯（选一个跑）

> 命名轴：**001~004 = CLI 全自动**；**01x = 自动简化（真人零操作）/ 02x = 手动**，
> 同 `x` 同例子。原则：从上往下，能过再下一格。
>
> 「双击入口」列的 `RUN-*.command` 是**本地 gitignored 便利件**，新 clone 中不存在；同行的 make target 才是权威入口，launcher 可按 runbook 自建。

| 想跑什么 | 命令 | 双击入口 | 凭证 | 详细操作单 |
| --- | --- | --- | --- | --- |
| 001 图通路 smoke（假数据） | `make soft-bundle DEMO_ARGS="create --name 001-demo --mode 001"` → `… run $ROOT --mode 001` | — | 无 | [runbook-001](docs/runbooks/runbook-001-easiest-fixture-graph.md) |
| 002 scripted 真实链路 | 同上，`--mode 002` | — | 无 | [runbook-002](docs/runbooks/runbook-002-easy-scripted-real.md) |
| 003 真实图全自动（minimal 意图） | 同上，`--mode 003` | — | 三要素+网络 | [runbook-003](docs/runbooks/runbook-003-medium-real-auto.md) |
| 004 真实图全自动（默认意图，找茬用） | 同上，`--mode 004` | — | 三要素+网络 | [runbook-004](docs/runbooks/runbook-004-hard-real-auto.md) |
| 010 TUI 自动全跑（真人零操作） | `make demo-tui-real-auto` | `RUN-010.command` | 三要素+网络 | [runbook-010](docs/runbooks/runbook-010-tui-auto.md) |
| **020 TUI 手动（真人 HITL1）** | `make demo-tui-embedded-smoke` | `RUN-020.command` | 三要素+网络+真人 | [runbook-020](docs/runbooks/runbook-020-tui-manual.md) |
| TUI fixture（零凭证预演） | `make demo-tui-fixture` | — | 无 | — |
| 嵌入式真实图校准（CLI 裸入口） | `make demo-real-embedded-smoke` / `demo-real-scripted` | — | 三要素 | local-operations.md |
| Gateway 观察路线（CLI/TUI） | 先 `make profile-dev PROFILE=demo`，再 `make demo-real PROFILE=demo` 或 `make demo-tui PROFILE=demo` | — | profile 体系 | local-operations.md |
| 调试工作台（节点边界 step/continue + 节点上下文检查） | `./run/tui-workflow-debugger.sh`（或 `make tui-debugger`）；`--fixture` 零凭证、`--attach <id>`/`--replay <id>` 经 lifecycle 校验 | — | 无（fixture） | [runbook-030](docs/runbooks/runbook-030-debugger.md) / [runbook-031](docs/runbooks/runbook-031-debugger-embedded.md) |

soft-bundle 辅助动词：`inspect` / `phases` / `status` / `verify`（对同一 `$ROOT`）。

## 2. 观察与检查

| 命令 | 作用 |
| --- | --- |
| `make demo-sessions` | demo 会话/bundle 检查（`DEMO_ARGS="inspect <bundle-id>"` 单查；注意：非 terminal 的 bundle 会被 safe-inspect 拒绝） |
| `make session-workbench` | 本地 Bundle 只读投影（时间线/目录），不是恢复客户端 |
| TUI 日志 | `.deep-research-demo-runs/logs/tui-<pid>.log`（另 `gateway-*.stderr.log`） |

## 3. workspace 与清理

- **bundle 历史是证据**：战役验收用"启动前目录快照 vs 退出后唯一新增"绑定
  （runbook §exact-bundle），对照跑（如 003）依赖历史 bundle——**别随手删**；
- 盘点：`make demo-workspace-report`——只读列出 workspace 内全部 bundle 的
  id / 生命周期状态 / 大小，非 terminal 标注 `resumable`，另给 logs 与 archive 摘要；
- 清理：`make demo-clean` 默认 **dry-run**（只列将删/将留，零删除）；
  `CONFIRM=1 make demo-clean` 才真删，且**只删 terminal bundle**（suspended 等
  非 terminal 可被 attach/resume，永不触碰）；`CONFIRM=1 make demo-clean DEMO_ARGS="--logs"`
  连 logs 一起清（同一确认门）；
- 真删后**必须重新做基线快照**（命令输出会重申），且不要在有进行中 run / 活跃战役时做。

## 4. 验证与开发

| 命令 | 作用 |
| --- | --- |
| `make verify` | 完整门（lock-check + lint + assets + fast + integration + workflow；离线跑加 `UV_OFFLINE=1`） |
| `make test-fast` / `test-integration` / `test-workflow` | 三条主 lane |
| `make test-changed` | 只跑 diff 触及的测试（迭代加速，不入门） |
| `make format` / `lint` | ruff 修/查 |

## 5. 出事看哪

| 症状 | 去处 |
| --- | --- |
| 跑挂了 / 形状怪 | 对应 runbook 的"撞上问题怎么办"节（如 runbook-020 §6） |
| 疑似产品 bug | `_backlog/bugs/`（登记流程见其 README） |
| TUI 卡死/断网死亡 | 用 `--attach <id>` 从 durable checkpoint 恢复（BUG-064 已修，`add-suspended-run-recovery`；`--replay` 只读）；见 [runbook-030](docs/runbooks/runbook-030-debugger.md) |
| 命令行为与本页不符 | 以 `Makefile` 为准，并修本页 |

## 证据与门禁（交付前）

| 命令 | 作用 |
| --- | --- |
| `UV_OFFLINE=1 make verify` | 应用行为、契约与门禁的完整门；绿时打印哨兵 `verify: OK` |
| `make proof LANE=<lane>` | 跑一条已登记 lane 并写下回执（命令/退出码/revision/是否脏树/transcript 摘要）；**脏树只发 provisional**，凭据 lane 记 `unverified` |
| `make proof-status` | 报告哪些回执已过期并给出重跑命令（`PROOF_ARGS="--lane verify"` 可限定） |
| `make mutation-check` | 逐条施加已登记变异并要求对应守卫变红；有守卫不变红即非零退出 |
| `make tui-journey` / `make tui-experiences` / `make debugger-proof` | 交互式 TUI 的逐步、整程与调试工作台证据（后者一条命令跑完五条链路） |

lane 定义在 `proof-lanes.toml`（harness 侧），回执与 transcript 落在 `.proof/`（gitignored）；
关账时治理门会要求覆盖被改动表面的 runner 回执。见已归档 change
`add-evidence-receipts-and-proof-lanes` 与 `bind-closeout-to-proof-receipts`。
