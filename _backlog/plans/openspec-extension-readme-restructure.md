# Plan: openspec 扩展目录 README 去重重构

> 类型: 分析 / 设计 | 更新: 2026-08-11 | 状态: 待 review

## 背景 / 现状

`openspec/` 下有三个非 OpenSpec 原生的扩展目录（governance / guardrails / policies），
各自带一份 README。它们是 `deep_research_harness` 项目的治理扩展，`openspec/config.yaml`
是它们的路由入口。

### 三个目录的定位（事实，来自各自 README 顶部声明）

| 目录 | 定位 | 内容物 |
|------|------|--------|
| `openspec/governance/` | 需求可追踪性 + 确定性归档门禁 | `req-registry.yaml`、`architecture-policy.md`、4 个 checker 脚本、`test-evidence-policy.md`、`agent-charter/` |
| `openspec/guardrails/` | 单个选中 change 的有界本地证据命令 | `selected_change_closeout.py`（verify-boundary / record-review 两条命令） |
| `openspec/policies/` | 跨多条本地治理路由的 recurring 设计 review 指引 | `control-placement.md`（被 charter 路由的外部 policy） |

### Review 发现：三份 README 的"索引/复述"比例失衡

| 目录 | 内容密度 | 问题 |
|------|---------|------|
| `governance/README.md` | 重（77 行） | 复述了 5 个页面内容 + 规范本身（ID 缩写规则表、checker 4 查名），没守住索引定位 |
| `guardrails/README.md` | 中（67 行） | 把整个 JSON v1 contract 和两条命令的语义完整复述了一遍 |
| `policies/README.md` | 轻（25 行） | 基本合格；V2 延期声明与 `control-placement.md` 有重复，但该重复是 spec 强制 |

### 重要更正（第一版 plan 声称 guardrails 有契约 bug，已证伪）

第一版计划称 `guardrails/README.md` 的 JSON v1 示例"漏了 `planning_home` 字段，是契约 bug"。
**该声明错误，已撤销。** 证据：

- `selected_change_closeout.py:22-27` 的 `REQUIRED_ATTESTATION_FIELDS` 只有 4 个字段：
  `change_name` / `repository_identity` / `base_commit` / `head_commit`。
- `planning_home` 不是 attestation 字段，而是脚本运行时从 `Path.cwd()` 向上查找的目录
  （`_planning_home()`，`selected_change_closeout.py:65-69`，找 `openspec/changes` 的父目录），
  用于解析 active change 的 root。README 里 "Run commands from the planning home or a
  directory below it" 指的就是这个运行时约定，README 写对了。

结论：guardrails 没有契约 bug。任何 review 若要求"修 planning_home"应直接拒绝。

## 决策 / 方案

按"README 只做索引、细节还给各文件"重构，三份 README 各自独立，可分开做。

### 1. `openspec/governance/README.md` → 索引卡（目标 ≤50 行）

保留：
- 目录定位一句话（需求可追踪性 + 确定性归档门禁，Python 标准库零依赖）。
- **各文件"何时读"表**：`req-registry.yaml` / `architecture-policy.md` / 4 个 checker /
  `test-evidence-policy.md` / `agent-charter/README.md` 各一行，何时读 + 读它解决什么。
- 四个 checker 的运行命令 + 退出码约定（0=PASS / 1=违规，stderr 列明细）。
- 与上游 JS 版的差异（3 条）。
- 保留顶部 `@impl DRC-009`（governance 实现归属，spec 要求）。

移出（还给各自文件）：
- ID 缩写规则表（`custom-tool→CUT` 等）→ `req-registry.yaml` 已自文档化（prefixes 块）。
- checker 4 查的具体名称（`duplicate`/`unregistered`/`orphan`/`reusedRetired`）→ 各脚本 docstring。
- `architecture-policy.md` 的权威分工复述 → 该文件本身。
- `test-evidence-policy.md` 语义复述 → 该文件本身。
- `agent-charter/` 定位复述 → `agent-charter/README.md` 本身。

### 2. `openspec/guardrails/README.md` → 命令使用说明（目标 ≤50 行）

保留：
- JSON v1 契约示例（4 字段，**与 `REQUIRED_ATTESTATION_FIELDS` 一致，勿加字段**）。
- 两条命令的用法（verify-boundary / record-review）+ 运行前提（planning home 或其子目录）。
- 行为边界声明（不写 tasks.md、不拦截/替代原生 archive、证据只作 inspection）。

压缩：
- 把"每条命令做了什么"的长段落压缩成命令后的一行结果语义（`boundary-verified` / `missing-boundary` / `review-recorded` / `invalid-review`）。

### 3. `openspec/policies/README.md` → 基本不动

- 仅可选：V2 延期段落措辞微调，避免与 `control-placement.md:55-58` 逐字重复。
- 其余（Available Policies 表、Boundary 声明、顶部 `> authority:` 行）**保持不变**——
  这些都是 `check_agent_charter.py` 的受控锚点（见下）。

## 受控约束（其他 agent review 时必读，改动前必须满足）

以下来自 `openspec/governance/check_agent_charter.py` 与 `openspec/config.yaml`，
**不是建议，是机器强制**：

1. **`check_agent_charter.py` 只对 4 个文件做行数预算**（`LINE_BUDGETS`，
   `check_agent_charter.py:154-159`）：
   `deep_research_harness/AGENTS.md`（≤160 硬上限）、`deep_research_harness/CLAUDE.md`（≤12 硬上限）、
   `openspec/config.yaml`（≤180 硬上限）、`deep_research_harness/README.md`（无硬上限，>200 出 warning）。
   **三份 README 都不在预算内**——本次重构不会触发行数检查，但**不得顺手改动那 4 个文件**。

2. **`openspec/config.yaml` 是受控锚点，本次不动**。`check_agent_charter.py` 要求它包含：
   `## Default Context Boundary`、`not a project manual`、`## Change Focus`、`Primary module / causal owner`、
   `Triggered review policies`、`control-placement`、两条 operation guidance 等字符串
   （`_validate_authoring_pointer`，`check_agent_charter.py:304-416`）。因此 plan 的"上下文"
   不主张修改 config.yaml 的 context 块——它同时是信息地图锚点。

3. **`openspec/policies/` 是被 checker 遍历的受控路由**：`POLICY_REGISTRY` 要求
   `policies/README.md` 链接到 `control-placement.md`，且 `control-placement.md` 必须含
   `> trigger:` 与 `authority: guidance only`（`check_agent_charter.py:118-238`）。
   **policies/README.md 的任何改动不得删掉 Available Policies 表或 authority 声明。**

4. **`> authority: guidance only` 三连是 spec 强制**：`deep-research-agent-charter` spec
   （DRC-009，`specs/deep-research-agent-charter/spec.md:359-376`）要求外部 policy 声明
   非权威边界。出现在 `policies/README.md` 和 `control-placement.md` 属合规，不是冗余。

5. **"V2 add-cross-session-cognitive-guardrails 仍延期"是有意重复**：被 DRC-009 spec 要求
   显式存在（`specs/deep-research-agent-charter/spec.md:365-368` 提及 deferred guardrails）。

## 风险 / 取舍

- [governance README 砍掉 ID 规则表后，读者失去"缩写怎么来"的快速入口]
  → `req-registry.yaml` 的 prefixes 块已有该映射；README 表头保留一行指向。
- [guardrails README 压缩命令语义后，读者不理解结果状态]
  → 保留一行状态枚举（boundary-verified / missing-boundary / review-recorded / invalid-review），
  详情在脚本输出里自解释。
- [重构触发 openspec change 义务？]
  → governance/guardrails 目录有 `@impl DRC-009/010` 归属，但 README 不在
  `check_agent_charter.py` 的受控内容清单里。倾向：纯文档重构、不动 checker 锚点
  → 不必然开 change；若 review 判定为受控内容，则用一个 change 承载三份 README。

## 落地关联

- 本次 plan 先产出三份 README 的目标结构，经 review 后实施。
- 实施顺序：policies（最小）→ guardrails（中）→ governance（最大）。
- 实施后验证：`cd 到 repo 根 && python3 openspec/governance/check_agent_charter.py` 必须 PASS；
  `python3 openspec/governance/check_project_reqs.py` / `check_project_specs.py` /
  `check_project_architecture.py` 应保持 PASS（README 不在其扫描范围，跑一遍确认）。
