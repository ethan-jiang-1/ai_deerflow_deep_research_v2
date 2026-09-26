# Plan: harness 技术债打扫与高信噪比重构

> 类型: 分析 + 执行计划 | 更新: 2026-09-26
> 审计输入: 四路只读审计（fresh-agent 两条链 / 内容腐化 / openspec 约束 / DeerFlow v2.1.0 理解同步），
> 全部关键断言经本会话直接复验（治理 checker 实跑、wave2 离线复现、git 元数据核对）。

## 背景 / 现状

用户关切：fresh agent 视角下两条链（**probe chain** = infra_probe 隔离探测路线；
**task execution chain** = start/resume/status/cancel/refine 生命周期执行链）是否清楚，
渐进式披露是否不多不少，A→B→C 迁移残留有多少，对 DeerFlow v2.1.0 与新版 openspec 的理解是否同步。

**总评（审计结论）：**

- **task execution chain ≈ 8.5/10，是全库强项**（walkthrough + 生成拓扑 + Public Controls + 公开 SKILL.md 全覆盖且与代码一致）。
- **probe chain ≈ 4/10**：代码自述优秀（tool.py → runtime/control.py → runtime/probe.py → graph/infra_probe.py，隔离单节点图 + 独立 checkpoint namespace），但文档只有 2 处一笔带过；被 docs/README 推荐为 runtime 入口索引的 `runtime/README.md` 把 `control.py` 标成"lifecycle 共享 control-plane"（与代码相反）、把 `probe.py` 标成"opt-in dev tooling"（实为公开动作接线）；公开 SKILL.md 里 infra_probe 零出现，但工具 schema 把它列为第一个 advertised action。
- **治理账面一红**：`project-structure.toml:7` 仍锁 `66b9e7f2`，实际 gitlink `ceebf97f`（v2.1.0）。`check_project_gate.py --phase closeout` 唯一红项即此（本会话实跑证实）；它不在 make verify / CI 里（门禁孤儿），下次 archive 必被卡。
- **openspec 结构健康**：57 specs `validate --specs --strict` 全过、0 活跃 change、172 归档与提交一一对应、467 需求 ID 零孤儿；CLI 1.13.1 与 config 兼容；`.agents/skills/` 工作区副本已是 1.13.1（落后的是 git HEAD，未提交）。
- **应用层对 v2.1.0 的代码适配到位**（17 个契约点全绿，pyproject `>=2.1.0,<2.2`、contract test pin 一致）；欠的是文档账面（根 README 两处旧 pin、"旧笔记不随 submodule 分发"与 fork 携带 `_digest/`/`_faq_on_digested/` 244 文件的现实冲突）与流程留痕（bump 未走 change）。

## 决策 / 方案（四阶段，次序即优先级）

### P0 事实裁决与红线修复（小、确定、先行）

1. **gitlink 锁统一**：`project-structure.toml:7-8` → `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7`（走 mini change，见落地关联）；根 `README.md:22、:64` 同步；`openspec/tests/governance/test_split_manifest.py:32` fixture 顺手刷新或注明"任意示例值"。
2. **README.md:22/64 同行的"旧研究笔记不随 submodule 分发"**改为现实表述：笔记由 fork ethan 分支随仓库携带（`_digest/`、`_faq_on_digested/`），仍属只读背景、不作为当前理解来源；根 AGENTS.md 同步微调。
3. **launcher 死链**：`RUN-010.command:84`、`RUN-020.command:9/:105` 改指 `deep_research_harness/docs/runbooks/`（同一文件头部已修过、尾部漏修的迁移残留）。
4. **runtime/README.md 三行**：:29 `control.py` 正名（probe host，lifecycle actions bypass）、:67 `probe.py` 正名（公开 infra_probe 接线，非 opt-in dev tooling）、:17 动作清单补 `infra_probe`。

验收：`check_project_gate.py --phase closeout` 转绿；活体区（排除 archive/_done）`66b9e7f2` 零命中；RUN-* 尾部提示指向存在的文件。

### P1 两条链与渐进式披露（信噪比主体）

1. **infra_probe 文档家**：runtime-architecture.md Public Controls 处展开 5-10 行（目的：真实 run 前的 provider durability/sandbox 探测；隔离保证：私有 State、独立 namespace、lifecycle bypass；代码链；失败看哪）；COMMANDS.md §5 补一行；`docs/deep-research-topology.md` 加一句"probe 图是刻意排除在研究 topology 外的第二张隔离图"。
2. **probe 术语消歧段**（一处权威、他处引用）：infra_probe 工具动作/探测图 vs work-unit storage/fs probes vs diagnostics readiness。
3. **IM transport 漂移**：runtime-architecture.md:78 动作集补 `refine`（tool.py:188 实拒 start/resume/refine）。
4. **glossary 入口重排**：`harness/CONTEXT.md` 顶部加"先读 run-lifecycle-walkthrough.md 建立骨架，本文件作词典查阅"；CONTEXT-MAP 把 walkthrough 标为 product context 正门。
5. **Entry Surfaces 表 ↔ CONTEXT.md Entry Interfaces 词条互链**，消除双分类法。
6. **命令表去重**：根/harness README 与 COMMANDS.md 各自收敛（README 留路标，COMMANDS/Makefile 留事实）。
7. **双 host builder 注释**：control.py:20 / probe.py:80 标明谁是生产正身。

### P2 同步工程（v2.1.0 理解 + openspec 现代化）

1. **建 `deep_research_harness/docs/deerflow-contract.md` v2.1.0 契约速查**：Gateway/配置/环境变量/技能/记忆要点（标注框架文档来源 file:line）+ 应用实际 import 的 9 个 `deerflow.*` 深模块依赖清单（受 contract test 保护）+ 两个存疑 env var（`DEER_FLOW_AUTH_DISABLED`、`DEER_FLOW_GATEWAY_HEALTH_URL`）行为验证后归类。定位：速查引用框架文档，框架文档仍是权威。
2. **补录 v2.1.0 迁移决策记录**：da5721d 等四个 commit 的 bump 未走 openspec change，属"未留痕先例"；governance 或 product 补一条批准记录。
3. **CNI-001 标题条款 MODIFIED delta**：spec 要求 H1 `Node — Product Responsibility`，11 个 workflow.md 实际是 `# <node> — <职责>`；其余字段/章节全吻合 → 改 spec 措辞最省。
4. 零项清理：`openspec/product/README.md:18` active-delta 假设改条件式；governance `__pycache__` 清理/补 ignore。
5. `.agents/skills/` 6 个文件：**用户保留区（handoff 指令"永远别碰"）**。事实供用户决策：工作区内容已是 1.13.1 再生成产物（内容最新），HEAD 停在 1.11.0；若用户放行，直接 `git add` 提交即可消除"clone 拿旧技能"的缺口。
6. `_backlog/README.md` 仓库名（v1 旧名）/更新日期刷新；plans/README 归档索引口径注明（36 行索引 vs 70 个文件，pre-CLS 文件未入索引）。

### P3 守护机制（防再腐化）

1. **治理门接入门禁**：把 `check_project_gate.py`（或 imports-only 快档）挂进 CI（agent-tests workflow）或 repo 层 make 步骤——本次 gitlink 红灯能存活至今，正因为它不在任何门禁里。
2. **锚点单一权威**：contract 断言 registry gitlink == `CURRENT_DEERFLOW_PIN`（两处锁值一处改另一处即红），杜绝三重漂移再现。
3. **索引新鲜度抽查**：对 runtime/README 等关键索引行的"docstring wins"规则加 contract test 抽查（本次 control.py/probe.py 双错即此类规则失效实例）。
4. closeout 检查单惯例化一条：`openspec --version` 与技能 frontmatter `generatedBy` 对齐核对。

## 风险 / 取舍

- [P0 走 change 显得重] → closeout 门已经红，下次 archive 反正必须修；mini change 是治理合同（deerflow-downstream profile"gitlink 边界须 proposal 显式拥有"）的既定路径，同时顺手补齐流程留痕。
- [P1 改 7+ 处文档面广] → 每处单点小改、互不依赖；按 fresh-agent 审计清单逐项勾，一次 PR 完成可整体复评。
- [deerflow-contract.md 沦为第二权威] → 头部声明引用关系 + 每条标来源 file:line + 应用侧 contract test 才是硬守护。
- [.agents/skills 与 handoff"别碰"冲突] → 默认不动；这是用户决策点，不是 agent 决策点。

## 落地关联

- P0-1 + P2-2 + P2-3 → 一个 mini openspec change（gitlink bump + v2.1.0 迁移决策补录 + CNI-001 delta），跑通 closeout 门后归档。
- 其余文档/launcher 修正 → 直接 `docs:` 提交（有先例：`docs: relocate runbooks...` 等）。
- P3 → 测试/CI 小改，随 mini change 或独立提交。
- demo-real Gateway 收尾独立成 plan：[demo-real-gateway-closeout.md](demo-real-gateway-closeout.md)（其 G1 诊断闭环与本计划无依赖冲突，可在 P0 之后随时开做）。
