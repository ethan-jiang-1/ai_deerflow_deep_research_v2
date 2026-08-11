# Plan: OpenSpec 治理文档分层与契约修复

> 类型: 分析 / 设计 | 更新: 2026-08-11 | 状态: 已 review，待分组实施

## 背景 / 现状

`openspec/` 下的治理扩展不是一个同质文档集合。四个 README 分属不同层级：

| Surface | 职责 | 本次定位 |
|---|---|---|
| `openspec/governance/README.md` | 治理 registry、policy、checker 的目录导航 | 重构目标 |
| `openspec/guardrails/README.md` | selected-change closeout 命令的最小可执行契约 | 跟随 SCC 功能修复 change |
| `openspec/policies/README.md` | 外部 review policy 索引与非权威边界 | 最小修正，跟随 DRC 术语 change |
| `openspec/governance/agent-charter/README.md` | canonical change/policy routing index | 只读边界参照，不重构 |

去重原则不是“README 只能做索引”，而是：**每份 README 完成自己的读者任务，
不复制由 spec、policy、registry 或另一个 canonical index 拥有的规范语义。**

## Review 后的事实更正

### 1. `planning_home` 不是 attestation 字段

`selected_change_closeout.py` 的 attestation 只有四个必填字段：
`change_name`、`repository_identity`、`base_commit`、`head_commit`。
`planning_home` 是脚本从当前工作目录向上发现 `openspec/changes/` 的运行时概念，
不得加入 JSON contract。实现允许额外 JSON key，因此文档必须写“四个必填字段”，
不能写“只允许四个字段”。

### 2. closeout command 存在独立的 SCC 契约缺陷

这不是 README 重构的一部分，必须单独修复：

- `record-review --output` 当前只要求路径位于 active change root 下，因此可把
  `tasks.md`、`proposal.md` 等 change artifact 当成输出并覆盖，违反 SCC-002 的
  “不得创建、完成或改写 tasks”边界。
- unchecked-task 解析当前接受任意包含 `- [ ]` 的行，不只接受真正的 Markdown
  unchecked task 行。
- `missing-boundary` 与 `invalid-review` 是 stdout JSON result，进程仍返回 0；README
  必须要求调用者解析 `result`，不能依赖 shell exit code 判断 evidence 是否成立。
- “可从 planning home 或其子目录运行”与 root-relative 示例混在一起。最终示例应明确
  假定 cwd 为 planning home；从子目录调用时须自行解析脚本和 output 路径。

决定：用独立 `selected-change-closeout-evidence` OpenSpec change 修复代码、测试和
`guardrails/README.md`，不与 governance/policies 文档整理合并。

### 3. “deferred add-cross-session-cognitive-guardrails” 已失真

同名 change 已完成并归档，交付的是 `Selected Change Closeout Evidence`。当前
`policies/README.md`、`control-placement.md` 与 DRC-009 main spec 仍把一个模糊的
cross-session guardrail 概念描述为 deferred，容易把已交付 evidence capability 与
并不存在的 semantic evaluator / automatic task writer / archive coordinator 混为一谈。

决定：不保留这个延期概念。用独立 `deep-research-agent-charter` OpenSpec change：

- 从 main spec 和 policy 中移除 deferred roadmap 断言；
- 用现在时区分 external design guidance 与已交付 closeout evidence；
- 对 `policies/README.md` 只做最小修正，并链接 canonical Agent Charter index。

### 4. 当前治理验证基线不是全绿

clean worktree 下，`check_project_reqs.py` 与 `check_project_req_coverage.py` 因以下
registry ID 未进入 owning main-spec header 而失败：

`EVH-030`、`WAN-011`、`WAN-012`、`WON-011`、`WON-012`、`WOU-012`。

决定：先单独修复 requirement ownership / coverage baseline，使治理门禁恢复全绿；
后续两个 OpenSpec change 不在已知红线上实施或归档。

### 5. governance 目录 inventory 原计划不完整

- 不是“四个 checker”这么简单：`make governance` 运行四个 root governance checker，
  完整 `make verify` 还运行独立的 `check_project_req_coverage.py`。
- `project-structure.toml` 是 exact structural authority，必须进入导航表。
- governance README 当前没有 `@impl DRC-009`，DRC-009 也不归属这个总索引；不得新增。
- focused contract test 要求 governance README 同时保留 `test-evidence-policy.md` 和
  `evaluation-hardening` 两个 literal pointer。
- 速查表中的“Requirement 标题不得包含 ID”在其他当前文档中没有 owner；删除前先迁移到
  `req-registry.yaml` 的 ID 使用约定。

## 已确认的设计决策

1. 功能 bug 与 README 信息架构拆开，按 causal owner 分组。
2. README 按职责区分：governance 是导航，guardrails 是命令契约，policies 是 policy 索引。
3. 不保留“延期中的跨会话 guardrail”概念。
4. 先修绿 requirement ownership / coverage 基线。
5. 行数只作软目标；完整职责、唯一 owner 和可用性优先。
6. Agent Charter README 是 canonical 边界参照，不是第四个重写目标。
7. Requirement 标题的 ID 约定迁移到 `req-registry.yaml`。
8. “与上游 JS 版差异”压成一句：Python 标准库、零外部依赖。
9. policies README 只做最小修正。

## 分组与依赖

```text
requirement ownership baseline repair
                |
                +--> SCC closeout contract fix
                |      + code + focused tests + guardrails README
                |
                +--> DRC terminology correction
                       + main spec + policy + policies README

两条 change 完成后
                |
                +--> governance README navigation cleanup
                       + req-registry wording + backlog indexes
```

不得把三组工作压成一个 OpenSpec change。baseline repair 是前置；SCC 与 DRC change
彼此独立；governance 总索引只在 owning 内容稳定后收口。

## 目标文档结构

### `openspec/governance/README.md`：目录导航

保留或新增：

- 一句目录定位，以及“Python 标准库、零外部依赖”。
- “何时读”表，至少覆盖 `req-registry.yaml`、`architecture-policy.md`、
  `project-structure.toml`、四个 root governance checker、
  `check_project_req_coverage.py`、`test-evidence-policy.md` 和
  `agent-charter/README.md`。
- checker 命令。正常校验路径使用 0/1，但明确 stderr 也可能包含 non-failing warning，
  argparse usage error 不属于 0/1 contract。
- `test-evidence-policy.md` 行必须同时指出 `evaluation-hardening` 是批准语义的 owner。

移出：

- ID 格式、三态、缩写和标题约定，统一由 `req-registry.yaml` 拥有。
- checker 内部 check-name 枚举，由各脚本 docstring 拥有。
- architecture/test-evidence/Agent Charter 的权威分工复述，由各自文件拥有。
- 上游差异清单，仅保留当前“stdlib-only”约束。

### `openspec/guardrails/README.md`：命令契约

跟随 SCC change，至少保留：

- 四个 attestation 必填字段，不添加 `planning_home`，不声称拒绝额外 key。
- `verify-boundary` 与 `record-review` 的 planning-home-root 示例。
- `review-required` 与 `inconclusive` 两种 review payload 及精确字段约束。
- 成功前提：active change、当前 repository、commit ancestry、`HEAD == head`、clean worktree。
- stdout JSON `result` 的四种结果，并明确 domain rejection 仍 exit 0。
- output 只能位于 selected change 的专用 `guardrail-evidence/` 路径。
- receipt、persisted evidence、semantic approval 与 native archive authority 的区别。

### `openspec/policies/README.md`：最小修正

- 保留 scope、authority、Available Policies 表与 Boundary 的当前职责。
- 直接链接 `../governance/agent-charter/README.md` 作为 canonical routing index。
- 删除错误的同名 deferred-change 声明，不引入新的未来 roadmap 名称。
- README 必须继续链接 `control-placement.md`；actual policy 本体继续拥有 trigger 与
  authority 声明。

### `openspec/governance/agent-charter/README.md`：只读边界

- 不改 `## Policy Route`、`Where Rules Belong` 或 policy links。
- governance README 只用一行路由到它，不复述 primary owner、evidence seam 或 adjacent
  contract 规则。
- policies README 只说明 external policy 由它路由，不复制完整 route semantics。

## 受控约束

必须区分机器约束、spec 义务与本计划 scope：

1. `check_agent_charter.py` 对 `deep_research_harness/AGENTS.md`、
   `deep_research_harness/CLAUDE.md`、`openspec/config.yaml` 和
   `deep_research_harness/README.md` 设置预算；本次不改这些 entry surfaces。
2. Agent Charter index 被机器要求链接 `charter.md`、保留 `## Policy Route` 并链接全部
   registered policies。
3. external policies index 被机器要求存在并链接 `control-placement.md`；trigger/authority
   literal 约束属于 actual `control-placement.md`，不是 index 表头。
4. governance README 受 focused contract test 约束，必须保留 test-evidence policy 与
   `evaluation-hardening` owner pointer。
5. 是否创建 OpenSpec change 取决于是否改变批准语义或可观察 command contract，不取决于
   README 是否被某个 checker 扫描。

## 验收

### Baseline repair

```bash
python3 openspec/governance/check_project_reqs.py
python3 openspec/governance/check_project_req_coverage.py
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_agent_charter.py
```

五项必须全绿后才能 apply 后续 change。

### Focused evidence

```bash
cd deep_research_harness
.venv/bin/python -m pytest \
  tests/contract/test_selected_change_closeout.py \
  tests/contract/test_agent_charter_governance.py \
  tests/contract/test_test_evidence_documentation.py
```

### Change 与最终收口

- 两个 active change 分别通过 `openspec validate <change-name> --strict`。
- 完成后运行 `cd deep_research_harness && UV_OFFLINE=1 make verify`。
- 运行 `git diff --check`，并确认未修改 `deerflow/`。
- 计划落地后按 `_backlog/plans/README.md` 的规则关闭并同步索引。
