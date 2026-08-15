# Plan: OpenSpec 引导与治理拓扑收敛

> 类型: 设计 / 迁移 | 更新: 2026-08-15 | 状态: 已完成。OpenSpec `simplify-openspec-support-topology` 已同步主规格、归档并提交为 `188bba5`；治理与 focused gate 通过，`UV_OFFLINE=1 make verify` 的三项 metadata selector 失败经基线比对确认早于本 change。

## 背景 / 现状

OpenSpec 原生表面与本项目扩展目前并列在同一层：

```text
openspec/
  config.yaml          # OpenSpec 原生项目配置
  specs/               # 已批准行为 / 结构规范
  changes/             # 待批准 change
  agent-charter/       # guidance-only 原则与路由
  policies/            # guidance-only policy library
  guardrails/          # 非权威 closeout-evidence command
  governance/          # registry、authority policy、checker
```

四个项目扩展目录各自有历史理由，但目录名没有直接表达权威等级：

- `agent-charter` 容易与产品内 Node Agent 混淆，`charter` 又像最高权威，实际却只提供
  design/admission guidance；
- `policies` 与 `agent-charter` 由同一个 route 和 checker 管理，却作为两个顶层概念并列；
- `guardrails` 听起来像会阻断操作，实际命令只生成 caller-declared、非权威的
  closeout evidence，domain rejection 仍返回进程退出码 0；
- `governance` 才包含 exact registry、authority lifecycle 和 mechanical checker，但并非
  OpenSpec 原生自动加载的目录。

当前还有一个已验证的治理漂移：`project-structure` main spec 声明
`openspec/agent-charter/` 只包含 `README.md` 与 `charter.md`，
`project-structure.toml` 也只登记这两个文件；实际已有 `concepts.md`，而
`check_project_architecture.py` 与 `check_agent_charter.py` 仍然通过。目标迁移必须同时修复
这个“required paths 存在，但额外成员未被拒绝”的检测缺口。

2026-08-15 基线：

- `openspec list --json`：无 active change；
- Git worktree：clean；
- requirement、spec、architecture、agent-charter、requirement-coverage 五个 checker 全绿；
- `openspec/changes/` 下不存在 active `guardrail-evidence/` 持久化数据。

## 目标 / 终态不变量

将项目自有扩展从四个顶层目录收敛为两个，并新增一个极短的 OpenSpec 根导航：

```text
openspec/
  README.md
  config.yaml
  specs/
  changes/

  change-guidance/
    README.md
    principles.md
    node-edit-map.md
    policies/
      agent-information-map.md
      authority-and-projections.md
      change-admission.md
      control-and-recovery.md
      control-placement.md
      human-interaction-integrity.md
      local-context.md
      node-agent-workflow-integrity.md
      participant-outcomes.md
      workflow-outcome-review.md

  governance/
    README.md
    architecture-policy.md
    test-evidence-policy.md
    project-structure.toml
    req-registry.yaml
    check_change_guidance.py
    check_project_architecture.py
    check_project_req_coverage.py
    check_project_reqs.py
    check_project_specs.py
    closeout-evidence/
      README.md
      selected_change_closeout.py
```

终态必须满足：

1. `config.yaml`、`specs/`、`changes/` 的 OpenSpec 原生名称和语义不变；
2. `change-guidance/README.md` 是 guidance 的唯一选择 / 路由入口；
3. 所有十个 canonical policy 保持一个完整 library，不再另设第二个 policy index；
4. `governance/` 只承载项目治理 authority、machine-readable registry、checker，以及明确
   标注为非权威的治理 evidence capability；
5. 现行 `agent-charter/`、`policies/`、`guardrails/` 被完整退休，不留 symlink、redirect、
   duplicate canonical copy 或兼容目录；
6. policy canonical name、trigger、Focus Card 字段、review heading/table、closed posture 与
   operation-guidance authority boundary 不变；
7. 根 `AGENTS.md`、根 `CLAUDE.md`、`deerflow/` 与 Deep Research runtime 行为不变；
8. archived changes 与 `_backlog/_done/` 保留历史路径，不因现代化路径而重写；
9. guidance 根和 policy library 的精确成员可被 checker 枚举并以 planted violation 证明；
10. 单一 OpenSpec change `simplify-openspec-support-topology` 归档且最终全量验证通过后，
    本 plan 才可关闭。

## 名称与路径映射

| 当前 | 目标 | 处理 |
|---|---|---|
| `openspec/agent-charter/README.md` | `openspec/change-guidance/README.md` | 移动并吸收现 `policies/README.md` 的唯一有用索引内容 |
| `openspec/agent-charter/charter.md` | `openspec/change-guidance/principles.md` | 只做清晰的人类命名；保留 guidance-only 边界和原则语义 |
| `openspec/agent-charter/concepts.md` | `openspec/change-guidance/node-edit-map.md` | 名称按实际职责收窄；同时纳入 exact inventory |
| `openspec/policies/*.md` | `openspec/change-guidance/policies/*.md` | 十个 policy 一起移动，canonical policy name 不变 |
| `openspec/policies/README.md` | 无独立目标 | 内容并入 guidance root，删除重复 route/index |
| `openspec/guardrails/README.md` | `openspec/governance/closeout-evidence/README.md` | 从模糊 guardrail 改成 capability 实名 |
| `openspec/guardrails/selected_change_closeout.py` | `openspec/governance/closeout-evidence/selected_change_closeout.py` | 命令行为除专用输出目录名外保持不变 |
| `<active change>/guardrail-evidence/` | `<active change>/closeout-evidence/` | SCC-002 持久化 contract clean break |
| `check_agent_charter.py` | `check_change_guidance.py` | checker 名与职责一致 |
| `test_agent_charter_governance.py` | `test_change_guidance_governance.py` | test node id 与 evidence metadata 同步 |
| 无 | `openspec/README.md` | 只解释 native/config/spec/change、guidance、governance 的入口和权威差异 |

`deep-research-agent-charter` capability slug 与 `DRC-*` requirement ID 本轮保留为稳定内部
身份，不尝试做 OpenSpec capability rename。现行、人类可见标题与导航改用
“Deep Research Change Guidance”；registry 描述与 main-spec requirement 标题按新术语同步，
但 capability slug 不迁移。这样避免把信息架构整理扩大成 capability identity 重建。

## 权威与兼容性分级

| Surface | 当前承诺 | Cutover 决策 |
|---|---|---|
| OpenSpec 原生 `config.yaml/specs/changes` | 工具读取的项目工作流表面 | 不改名、不搬迁 |
| guidance Markdown 路径 | 仓库内部 canonical authoring route，由 checker 和文档引用 | 同一 change 内与所有 caller 原子更新；不保留旧入口 |
| policy canonical names / proposal review records | active proposal、checker、main spec 共同依赖的跨边界 contract | 全部保留，只改变文件路径 |
| checker / test / Makefile 命令路径 | 仓库内部机械验证入口 | 与文件移动同一 commit 更新 |
| closeout command path | 仓库内部命令 contract | 无外部发布承诺；所有现行 caller 同步 clean break |
| `guardrail-evidence/` output path | SCC-002 明确规定的持久化路径 | 改为 `closeout-evidence/`；apply 前再次确认无 active 数据，否则停止并补迁移方案 |
| archived artifacts / closed plans | 历史证据 | 保留原文，不参与 current-path residual failure |
| `project-structure.toml` | exact enumerable structure，服从 owning spec | 与该 change 的 PRS delta 同步更新 |

不提供兼容 shim 的理由：这些路径均为仓库内部表面；当前无 active change 和既存 evidence
数据；旧入口继续存在反而会制造第二 canonical route。若正式 apply 前事实发生变化，此 clean
break 决策自动失效，必须重新评估 consumer/data migration。

## OpenSpec 落地方案

只创建一个 OpenSpec change：`simplify-openspec-support-topology`。这次工作的一个因果目标是
把 OpenSpec 项目扩展从四个含混顶层入口收敛为两个有明确权威边界的入口；拆成多个 change
会重复 proposal、review、validation 和 archive 成本，还会产生一个没有独立用户价值的中间
拓扑。因此路径切换、contract 同步和旧入口退休必须在同一个 change 内完成。

Primary causal owner：`project-structure` capability。它拥有目标 topology 与 exact inventory。
`deep-research-agent-charter` 和 `selected-change-closeout-evidence` 是该结构迁移必须同步修改的
adjacent contracts，而不是两个独立交付目标。

proposal 使用普通 Focus Card，不使用 `Program Focus`。两个 adjacent-contract 问题必须写成：

- DRC：authoring route、checker 和人类术语能否随 topology 移动，同时保持 policy 语义与
  guidance-only authority boundary 不变？
- SCC：command/output path 能否随 topology 移动，同时保持其余 I/O、containment、exit-code
  与 non-authority contract 不变？

该 change 的 contract 范围：

- `project-structure`：更新 PRS-009 的 canonical topology、command path 与 exact inventory；
- `deep-research-agent-charter`：更新 DRC-001、DRC-005、DRC-006、DRC-009、DRC-010 的
  guidance 名称、authoring route、command route 与 operation-guidance 指针，不改变原则和
  authority boundary；
- `selected-change-closeout-evidence`：更新 SCC-002 的 command 路径和专用输出目录，保留
  attestation JSON、stdout result、exit-code、task-reference、output containment、
  non-authority 与 native archive boundary 的其余行为；
- `req-registry.yaml`：同步 DRC/PRS/SCC 当前描述中的路径和人类术语，不迁移 capability slug
  或 requirement ID。

同一 change 内分四组 tasks，分组只用于控制实施和验证顺序，不形成独立 change 或中间 archive：

1. **先建立失败证据**：让 topology fixture 只接受目标 tree；让
   `test_selected_change_closeout.py` 只接受新 command/output path，确认当前 tree 失败；
2. **完成物理迁移**：移动 closeout command/README，合并 guidance 与完整 policy library，
   删除重复 index，重命名 guidance checker/test，完整退休三个旧顶层目录；
3. **同步所有 contract 与入口**：一次性更新三份 delta spec、`project-structure.toml`、
   `req-registry.yaml`、`config.yaml`、`openspec/CONTEXT.md`、相对链接、Harness entry docs、
   Makefile、test/evidence selector metadata 和 governance navigation；
4. **证明终态**：重新生成并校验 Harness `AGENTS.md` 的 bounded locator，加入 exact-member、
   legacy-only tree、旧 command/output path 和 output containment 负例，完成 residual audit 与
   全量 verification 后才 archive。

实施中允许测试在 task 边界暂时为红，但不允许把部分迁移状态归档、作为 canonical topology
提交，或为使中间状态通过而引入兼容目录。

## 已扫描影响面

### Canonical spec / registry

- `openspec/specs/deep-research-agent-charter/spec.md`
- `openspec/specs/project-structure/spec.md`
- `openspec/specs/selected-change-closeout-evidence/spec.md`
- `openspec/governance/project-structure.toml`
- `openspec/governance/req-registry.yaml`
- `openspec/CONTEXT.md`

### OpenSpec authoring / guidance / navigation

- `openspec/config.yaml`
- `openspec/agent-charter/{README.md,charter.md,concepts.md}`
- `openspec/policies/README.md` 与十个 policy 文件
- `openspec/guardrails/{README.md,selected_change_closeout.py}`
- `openspec/governance/README.md`
- 新增 `openspec/README.md`

### Downstream entry surfaces

- `deep_research_harness/AGENTS.md`
- `deep_research_harness/README.md`
- `deep_research_harness/docs/README.md`
- `deep_research_harness/Makefile`

`deep_research_harness/CLAUDE.md` 只导入 `AGENTS.md`，当前扫描未发现旧路径；正式 apply
仍需复核，但预期不修改。`deep_research_harness/CONTEXT.md` 是产品 glossary authority，
不因 guidance 文件改名而改定义。

### Checker / tests / evidence metadata

- `openspec/governance/check_agent_charter.py`（重命名）
- `deep_research_harness/tests/contract/test_agent_charter_governance.py`（重命名）
- `deep_research_harness/tests/contract/test_selected_change_closeout.py`
- `deep_research_harness/tests/contract/test_verification_gate_contract.py`
- `deep_research_harness/tests/assets/evidence.py`
- `deep_research_harness/tests/assets/requirement_evidence.py`
- architecture、requirement、spec、evidence-documentation 等现有 contract tests，按实际
  diff 选择 focused 回归，不预设无影响。

当前扫描共发现 25 个现行 tracked 文件含旧路径、旧 checker/test 名、`Agent Charter` 或
`Charter Index` 术语；另有 127 个 archived-change / completed-backlog 文件包含历史引用。
后者必须保留，不能通过全仓字符串替换“修正”。`.agents/`、`.github/` 当前未发现上述旧路径
caller。

## 实施顺序

该 change 使用 OpenSpec CLI 创建，不手工新建 `openspec/changes/<name>/`：

1. 重新确认 clean worktree、无 active change、无 active `guardrail-evidence/` 数据；
2. `openspec new change "simplify-openspec-support-topology"`；
3. 按 `openspec status` / `openspec instructions` 生成 proposal、delta specs、design、tasks；
4. proposal 明确 `project-structure` 是 primary owner，DRC/SCC 是必要 adjacent contracts，
   并记录 evidence seam、非目标和 triggered policies；
5. design 固化上面的 clean-break、no-shim、history-preservation 与 rollback 决策；
6. tasks 按“失败证据 -> 物理迁移 -> contract/入口同步 -> 终态证明”四组执行，采用
   red-before-green，先改 focused fixture / detector，再移动 canonical path；
7. 更新 `project-structure.toml` 后运行
   `python3 openspec/governance/check_project_architecture.py --render-guide`，只替换
   `deep_research_harness/AGENTS.md` 的 bounded generated block，并运行 checker 验证同步；
8. 完成 focused tests、current-path residual classification、历史 diff 审计、全量 verification
   和 strict validation；
9. 只有终态 gate 全绿才 archive；归档后复跑 main-spec checker、residual audit 与全量 gate；
10. 记录最终 topology 和历史保留证据，再关闭本 plan。

## 引用扫描与残留分类

正式 apply 前后均扫描 tracked current material，不能依赖普通 `rg` 的 ignore 行为，因为
`openspec/config.yaml` 可能受本机 ignore 配置影响。使用 `git grep` 获取 tracked truth，再用
`rg -v` 排除历史根：

```bash
git grep -n -E \
  'openspec/(agent-charter|policies|guardrails)|agent-charter/(README|charter|concepts)|\.\./(agent-charter|policies)|guardrail-evidence|Agent Charter|Charter Index|check_agent_charter|test_agent_charter_governance|selected_change_closeout' \
  | rg -v '^(openspec/changes/archive/|_backlog/_done/)'
```

每条结果必须归入以下之一：

1. **必须迁移**：current link、command、manifest entry、test selector、Makefile target；
2. **必须语义更新**：main spec、req registry、config guidance、current context；
3. **允许保留的负例**：明确列入 checker/test 的 retired-path 常量或 spec negative scenario；
4. **历史证据**：archive / closed plan，仅由排除规则保留；
5. **本 plan 自述**：实施期间允许记录旧路径，closeout 时随 plan 一起归档。

不能以“搜索结果为零”为验收，因为 legacy negative guard 必须保留。验收是：除显式负例与
历史/本 plan 外，没有可解析的 current link、执行命令或 canonical registry 指向旧路径。

同时正向检查所有目标路径已由 `project-structure.toml` 登记、root/guidance README 可达、
policy registry 与磁盘成员集合相等、closeout command 的 README 示例可执行到目标脚本。

## 验证矩阵

### 单一 change 的 focused gate

```bash
python3 openspec/governance/check_project_reqs.py
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_change_guidance.py
python3 openspec/governance/check_project_req_coverage.py
```

重命名和路径切换完成后运行终态 canonical test node：

```bash
cd deep_research_harness
.venv/bin/python -m pytest \
  tests/contract/test_selected_change_closeout.py \
  tests/contract/test_change_guidance_governance.py \
  tests/contract/test_verification_gate_contract.py \
  tests/contract/test_architecture_governance.py \
  tests/contract/test_test_evidence_documentation.py \
  tests/contract/test_asset_checker_contract.py
```

red 阶段可在对应 task 中运行当时被修改的 focused test；archive gate 只接受上面的终态
checker 路径和 canonical test node，不接受旧名称或部分迁移状态。

### OpenSpec / diff gate

```bash
openspec validate simplify-openspec-support-topology --strict
git diff --check
git status --porcelain=v1 --untracked-files=all
git diff --submodule=short
```

### 最终全量 gate

```bash
cd deep_research_harness
UV_OFFLINE=1 make verify
```

并记录：

```bash
git ls-files --stage deerflow
git submodule status -- deerflow
git -C deerflow status --porcelain=v1 --untracked-files=all
```

这些命令只验证 gitlink metadata / nested worktree 范围，不读取或修改 DeerFlow 源码。

## 风险 / 取舍

- [再次出现两个 guidance 路由] -> 只保留 `change-guidance/README.md` 的 route table，删除
  policy index，checker 拒绝旧根与重复 index。
- [嵌套 policies 被认为重现旧设计] -> 旧设计的问题是 policy 被拆成两处；本目标把全部十个
  policy 放在同一个 guidance owner 下，并由 OpenSpec 根 README 提供一等入口。
- [路径迁移改变 policy 语义] -> policy 文件使用 rename-aware diff；除相对链接和人类层术语外，
  trigger、authority boundary、review schema、posture 必须逐项相等。
- [SCC 持久化路径已有消费者] -> apply 前和物理 cutover 前扫描 active changes 与磁盘数据；
  一旦存在，停止 clean break，补 consumer/data migration 和 recovery 方案。
- [checker 仍只验证 presence] -> 增加 exact-member planted violation；没有检测已知额外文件的
  负例，不得宣称 PRS-009 收口。
- [测试文件改名使 evidence selector 静默失效] -> requirement/evidence registries 与 test node id
  同步修改，并运行 collection-aware asset checker。
- [全仓替换破坏历史] -> 只修改 current inventory；archive 与 closed plan 加入明确排除和最终
  diff 审计。
- [能力 slug 与人类术语不一致] -> 明确把 `deep-research-agent-charter` 视为稳定内部 ID；根导航
  只展示 Change Guidance。若未来确需 capability rename，另开独立 migration，不塞入本计划。
- [单一 change 同时触及三份 contract，review 面较大] -> 维持一个 primary owner，按四组 tasks
  和 contract 分区审查；不归档部分状态，也不为中间绿灯引入兼容 tree。

## 失败与回滚

该 change 不修改 runtime state、数据库或 DeerFlow，并必须形成一个可整体 revert 的原子迁移：

- archive 前失败：保持 change active，在该 change 内修复问题或把部分路径 / registry /
  checker 恢复到已提交基线，不归档部分状态；
- archive 后发现 current link 漏迁：新建 focused repair change，不复活旧 canonical copy；
- evidence output 迁移中发现未声明数据：停止写入，保留原数据，重新设计显式 forward
  migration；
- checker 与 registry 不一致：以 owning main spec 决定语义，以 registry 表达 exact current
  enumeration，二者在同一 repair 中收敛。

终态证据是：目标 tree、main specs、registry、checker、focused negative tests、全量 verify 与
residual classification 同时一致；任一单独通过都不足以关闭迁移。

## 落地关联

本 plan 已由 OpenSpec change
[`simplify-openspec-support-topology`](../../../openspec/changes/archive/2026-08-15-simplify-openspec-support-topology/proposal.md)
吸收并完成。该 change 已同步三份 main spec、归档 proposal、delta specs、design 和 tasks，且
提交为 `188bba5`；本 plan 保留为设计和决策的历史记录。其实际落地链路如下：

```text
openspec-support-topology-simplification (本 plan)
              |
              +--> simplify-openspec-support-topology
                     +--> phased tasks + strict validation + apply
                            +--> sync main specs + archive + post-archive verification
                                   +--> commit 188bba5 + close this plan
```
