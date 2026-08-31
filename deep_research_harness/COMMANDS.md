# COMMANDS — 操作速查（Playbook）

> **一页纸速查：跑什么、用哪条命令、出事看哪。**
> 本文件只是**索引**，不是第二权威：命令的权威是 [`Makefile`](Makefile)，
> 操作细节的权威是各 runbook 与 [`docs/local-operations.md`](docs/local-operations.md)；
> 那里变了这里必须同一 PR 跟着改。
>
> 最后核对: 2026-08-30（对应当日 Makefile 形态）| 阶梯语义: [`_backlog/_local_demo/README.md`](../_backlog/_local_demo/README.md)

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

| 想跑什么 | 命令 | 双击入口 | 凭证 | 详细操作单 |
| --- | --- | --- | --- | --- |
| 001 图通路 smoke（假数据） | `make soft-bundle DEMO_ARGS="create --name 001-demo --mode 001"` → `… run $ROOT --mode 001` | — | 无 | runbook-001 |
| 002 scripted 真实链路 | 同上，`--mode 002` | — | 无 | runbook-002 |
| 003 真实图全自动（minimal 意图） | 同上，`--mode 003` | — | 三要素+网络 | runbook-003 |
| 004 真实图全自动（默认意图，找茬用） | 同上，`--mode 004` | — | 三要素+网络 | runbook-004 |
| 010 TUI 自动全跑（真人零操作） | `make demo-tui-real-auto` | `RUN-010.command` | 三要素+网络 | runbook-010 |
| **020 TUI 手动（真人 HITL1）** | `make demo-tui-embedded-smoke` | `RUN-020.command` | 三要素+网络+真人 | runbook-020 |
| TUI fixture（零凭证预演） | `make demo-tui-fixture` | — | 无 | — |
| 嵌入式真实图校准（CLI 裸入口） | `make demo-real-embedded-smoke` / `demo-real-scripted` | — | 三要素 | local-operations.md |
| Gateway 观察路线（CLI/TUI） | 先 `make profile-dev PROFILE=demo`，再 `make demo-real PROFILE=demo` 或 `make demo-tui PROFILE=demo` | — | profile 体系 | local-operations.md |

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
| TUI 卡死/断网死亡 | 目前无恢复入口（BUG-064，活跃）；bundle 侧证据仍在盘上 |
| 命令行为与本页不符 | 以 `Makefile` 为准，并修本页 |
