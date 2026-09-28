# close-agent-guidance-doc-gaps

## Change Focus

- **Primary module / causal owner:** agent 指引面本体——`deep_research_harness/AGENTS.md`（module guide）、`deep_research_harness/docs/runtime-architecture.md`、`deep_research_harness/docs/runbooks/README.md`；三处均为指引/导航文档，规范语义 backstop 归 `deep-research-agent-charter` capability（本次不修改其任何要求）。
- **Seam classification:** wiring —— 三处交付全部是 Markdown 指引内容与表格列扩展：无认知面、无人工决策面、无运行时行为、无权限/路由变化；确定性 owner（文档卫生、change guidance、结构检查器）保持权威。
- **Question:** 能否在不新增 module guide 常驻行数（当前 119 行，行数预算 ≥120 即告警，余量仅 1 行）、不改任何运行时代码、不触碰 `deerflow/` 的前提下，把 DSH harness 十维对照剩下的三个文档层 GAP 显式化：机制选择的影响半径次序、静/动持久层分界地图、runbook 写法对照单？
- **Necessary adjacent/external contracts:** `openspec/governance/check_doc_hygiene.py`（字符预算与链接规则的权威执行者，只被满足不被修改）；`openspec/governance/check_change_guidance.py`（module guide 行数预算 120/160 的权威执行者，只被满足不被修改）；`_backlog/plans/dsh-spirit-three-gap-closure.md`（分析来源，其结论被本 change 吸收后按账本 ritual 关闭）。
- **Evidence seam:** `check_doc_hygiene.py --self-test`（既有守卫负例控制）与 `check_doc_hygiene.py`（预算/链接/编码）+ `check_change_guidance.py`（行数预算与 Focus Card）+ `check_project_gate.py --phase closeout`（六组件）+ `UV_OFFLINE=1 make verify`（无关联回归）。
- **Not in scope:** `deerflow/`（submodule，绝不修改）；任何 `src/` 运行时代码与测试；`openspec/specs/` 与治理检查器修改（skip_specs：纯指引内容，无 spec 级行为变化）；任何 doc budget 上限调整（棘轮不动）；`_backlog/`（plan 关闭走账本 ritual，不属本 change）。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

对照 DSH harness FAQ 做十维评估后，本仓约八成维度已就位（变更闭环、归属、决策记录、入口链、反馈等均有机器兜底）；剩下三个 GAP 的共同点是**事实都在、缺显式化**：

1. 现有两张路由表各管一轴——Application Focus 表管"归谁管"，LLM-Node Gate 管"是不是模型的事"——缺第三轴：**同一类行为改动先试哪个机制、何时才许升级**。本仓语境的失败形态：重试/超时明明是 `config.yaml`（models 已有 `timeout`/`max_retries`）与 `profiles/` 的旋钮，agent 却钻进 `engine/`/`graph/` 写死分支，影响半径从一行配置放大到全局行为。
2. 静/动分界的事实分散在五处：规则层走 PR、配置层 `config.yaml`+`profiles/`、事实源 Run Bundle 单写者（ADR-0028 与 runtime-architecture 的 State, Content, And Nodes 节）、派生只读观测（Projections And Observations 节）、"模型可见 ⟺ 可重建"（runbooks 030/031 无推断回放 + `make prompt-dump-check`）。没有一张地图，新 agent 要自己拼，拼错的典型症状是同事实两处存真、回放不出来、会话决定不回写。
3. runbook 写法标准只活在已有文件的示范里，缺一份可对照的写法标准；新写 runbook 易滑向两个病：散文病（"做好验证"式步骤）与清单病（12 步锁死判断）。

## What Changes

- `deep_research_harness/AGENTS.md`：Application Focus 表新增第三列 `Try first; escalate when`——每行给出该 owner 之前应先尝试的最低影响机制与升级条件。**零新增行**（119 行保持，避开 ≥120 行常驻警告；字符预算实测后留 ≥100 余量）。不改 LLM-Node Authoring Gate、Information Map、Boundaries、Verification 与生成块。
- `deep_research_harness/docs/runtime-architecture.md`：在 Projections And Observations 之后、Source And Structural Contract 之前新增 `## Persistence Layers` 一节——四层表（Rule/map / Config / Fact source / Derived，各带变化速度、owner 指针、边界一句话）+ 三条纪律（派生不存第二份真、模型可见 ⟺ 可重建、会话持久事实回写 owner），全部以链接/指针指向既有 owner，不复制 Run Bundle 契约正文。
- `deep_research_harness/docs/runbooks/README.md`：紧跟命名规则行（`📐 手册命名规则固定为 runbook-00X-难度-用途.md`）之后新增 `### 写新 runbook 的对照单`——六条写法标准（触发条件一句话、每步可执行命令、判断标准写成规则、可机械部分指向真实 make target/checker、文末 guidance 声明、新增后索引登记）。
- 非目标：不改 `deerflow/`；不改任何运行时代码与测试；不改 spec 与治理检查器；不上调任何预算上限；不动 `_backlog/`。

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — 三处交付均为指引/导航文档内容，无 spec 级行为变化；与归档 change `harden-entry-doc-navigation` 同类，经 `skip_specs: true` 声明。)

## Impact

- 修改：`deep_research_harness/AGENTS.md`（Application Focus 表 +1 列，0 新行）；`deep_research_harness/docs/runtime-architecture.md`（+Persistence Layers 节）；`deep_research_harness/docs/runbooks/README.md`（+写法对照单小节）。
- 不影响：任何 Python 源码/测试、`openspec/specs/`、governance 检查器、`deerflow/`；AGENTS.md 生成块（PROJECT-STRUCTURE）原样。
- 预算影响：`AGENTS.md` 字符 7335 → ≈7900 / 8200（实施时实测，余量 ≥100），行数 119 → 119；另两份文档在 `DOC_LAYER_DOCS` 内且无字符预算。
