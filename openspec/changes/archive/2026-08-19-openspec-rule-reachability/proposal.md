## Why

003 战役复盘（`_backlog/_done/_closed_plans/openspec-materials-feedback-from-bugfix-campaign.md`）与只读实测共同证明：机械治理规则**存在但不在执行链里**。规则写进了 `openspec/config.yaml` 与 checker，但 `rules.tasks` 归档前清单只有 `make verify` / `validate --strict` / `git diff --check`；checker 还被 54886b8 有意从 Harness `make verify` 摘除（`check_harness_dependency_direction.py` 未被任何门禁组合）；polish 阶段没有任何 ID 占号/冲突检查，而 registry 正式登记只能发生在 apply——作者只能在归档后被 CLI 或 checker 后知后觉地咬。当前基线：`check_project_reqs.py`、`check_project_specs.py`、`check_project_architecture.py`、`check_project_req_coverage.py` 全红（4 个未登记 ID、2 个 spec 缺 header、`.repro-tmp/` 未注册、REJ-009/SCR-006 无证据），`check_change_guidance.py` 因零 active change 空跑通过。

## What Changes

- 建立 **OpenSpec root governance aggregate**（标准库、零依赖、仓库根运行），组合六个 checker：`check_project_reqs.py`、`check_project_specs.py`、`check_project_architecture.py`、`check_change_guidance.py`、`check_project_req_coverage.py`、`check_harness_dependency_direction.py`。`check_project_gate.py` **只编排与聚合退出码**：它不拥有规则语义、不写 registry、不复刻任何 regex/解析——所有语义判断都留在各自的 component checker 里。
- aggregate 暴露两个 phase：
  - `--phase plan --change <name>`：**只读** admission 检查，**调用既有语义 owner 的 scoped 模式**而非自行解析——`check_change_guidance.py`（Focus Card / Program Focus 文法）、`check_project_specs.py --change <name>`（active delta 的 `> req:` 头声明与 Requirement 标题不内嵌 ID）、`check_project_reqs.py --change <name>` planning 模式（新 ID 与 registry/其它 active delta 的冲突、retired ID 复用，合法新 ID 输出 **reservation** 到 stdout）；MODIFIED 块完整场景保留由 `openspec validate <name> --strict` 执行（archive 原生校验前移，不重复实现）。
  - `--phase closeout`：运行六个默认 component checker 并聚合各自退出码（任一非零即整体非零），**不新增**独立的一致性 checker——registry/delta/main header/evidence 一致性已由 `check_project_reqs.py`、`check_project_specs.py`、`check_project_req_coverage.py` 各自拥有。
- **写入分离**：reservation 仅规划期占号；正式登记 registry 由 apply 的首个相关任务执行；closeout 只检测不一致。避免"polish 要求已登记、而只有 apply 能登记"的循环。
- `openspec/config.yaml`：
  - `rules.specs` 增补 delta mechanics：MODIFIED 携带完整 requirement 与全部存活 scenarios；Requirement 标题是语义锚、不得内嵌 ID；新 ID 必须在 delta 首 heading 前 `> req:` 行声明。
  - `rules.tasks` 增补归档前门禁：跑 aggregate `closeout` + Harness `UV_OFFLINE=1 make verify` + strict validate + diff check，注明退出码直测（管道 `| tail` 会吞退出码）。
  - 修正失效路径 `profiles/workflow-control/workflow-outcome-review.md` → canonical `profiles/workflow-control/workflow-control.md`。仅改动该失效 context 路径字符串；canonical review trigger 名 `workflow-outcome-review`（`rules.proposal` 与 `check_change_guidance.py` 依赖）保持不变，本 change 不增删 `## Workflow Outcome Review` 义务。
- skills 接线（仓内 agent workflow 硬停，**不**声称阻断 native `openspec archive`——外部 CLI v1.9.0 不可改）：
  - `openspec-propose`：生成 artifacts 后必须指向 `/polish-openspec-change <name>`。
  - `polish-openspec-change`：pass 判据增加 `--phase plan` 只读检查；违规报 `not ready`，绝不自行写 registry 或 accepted specs。
  - `openspec-archive-change`：closeout aggregate 非零时停止自身 workflow。
- **T0 基线收敛**（本 change in-scope 的 expected-red 修复，非 unrelated blocker）：
  - registry 登记 `EXI-001`、`LSA-001`、`SCR-006`；`RGL-014` 是 research-graph-lifecycle 新 requirement 配错前缀，修正为 next-free `REG-022`（active main spec 锚点 + header + registry 同步；archive 历史不改）。
  - `execution-intent`、`low-scale-real-auto` 补 `> req:` header（delta MODIFIED，语义不变）。**header 生命周期**：delta 的 `> req:` 行是规划期声明；main spec 顶层 `> req:` header 修复（EXI-001 / LSA-001 / REG-022）由 apply 作为**显式 metadata 编辑**执行——generic sync skill 不合并顶层 `> req:` header，归档 sync 后须重查 main spec header 完整。
  - `deep_research_harness/.gitignore` 的 `.repro-tmp/` 仍在使用，注册进 `project-structure.toml` ignore policy，不从 `.gitignore` 删除。
  - 为 `EXI-001`、`LSA-001`、`REG-022`、`SCR-006`、`REJ-009` 绑定真实 lowest-responsible test evidence（`@impl` 声明 + 实际断言），不做装饰性标注；evidence 边界如实陈述（见 Evidence seam）。
  - **apply 期暴露的 masked architecture drift**：`.repro-tmp/` 注册后，architecture checker 暴露 `wave2_synthesis/node.py` 直接 import pydantic 的既有违规（第二项 red 根因，此前被 ignore-entry 失败掩盖）。bounded-repair：domain 层新增 `is_structured_validation_error` 谓词、node 改经该谓词，行为不变，不放宽 nodes import policy（见 Impact）。
- `openspec/governance/README.md`：六 checker 清单、aggregate 命令、退出码直测警告。
- accepted contracts 修正（经本 change delta）：
  - `deep-research-agent-charter`（DRC-010）：独立 canonical project governance gate 可因任意 component checker 非零而停止仓内 archive agent workflow；停止权威仅来自确定性 checker 退出码，**不**来自 operation guidance 或 selected-change closeout evidence（二者保持 advisory/non-authoritative）；不阻断、不直接改变 native `openspec archive`；恢复 = 修复所指 finding 后重跑。既有 guidance/selected-change evidence 边界与全部 surviving scenarios 原样保留。DRC-004（Focus Card enforcement）与 DRC-012（单向依赖）语义不变，不 MODIFIED。
  - `evaluation-hardening`（EVH-005）：确立"OpenSpec aggregate 与 Harness `make verify` 并列、Harness 独立无 OpenSpec 依赖"的 gate 模型，消除 accepted spec 与 54886b8 实现的漂移。
  - `project-structure`（PRS-009）：注册 aggregate 为 canonical OpenSpec governance entry（编排-only、不注册 portable 模块为通用 checker）。
  - `research-graph-lifecycle`："Bundle graph checkpoints cross one explicit registered serialization boundary" 锚点 `RGL-014` → `REG-022`（完整保留 requirement 与 scenarios）。
- `deep_research_harness/docs/testing-and-evaluation.md`：修正已删除的 `make test-req-coverage` 引用与旧门禁组成口径；保留 `test_verification_gate_contract.py` 对 Harness 无 governance 依赖的约束。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `deep-research-agent-charter`: DRC-010 MODIFIED——独立 canonical project governance gate 可因任意 component checker 非零而停止仓内 archive agent workflow；该停止权威仅来自确定性 checker 退出码（非 operation guidance / selected-change evidence，二者保持 advisory/non-authoritative）；不阻断、不直接改变 native `openspec archive`；恢复 = 修复所指 finding 后重跑。既有 guidance/selected-change evidence 边界与全部 surviving scenarios 原样保留。DRC-004、DRC-012 语义不变，不 MODIFIED。
- `evaluation-hardening`: EVH-005 门禁组成修正——OpenSpec root governance aggregate（六 checker）与 Harness `UV_OFFLINE=1 make verify` 并列，Harness 保持独立；closeout 红阻断仓内 archive workflow。EVH-032 与其余内容不变。
- `project-structure`: PRS-009 canonical structure 注册 aggregate 为 OpenSpec governance entry（编排-only、退出码传播、plan/closeout 双 phase、单向依赖 `openspec/ -> deep_research_harness/` 不变）。
- `research-graph-lifecycle`: "Bundle graph checkpoints cross one explicit registered serialization boundary" 的 requirement 锚点 `RGL-014` 修正为 `REG-022`，header 与 registry 同步；requirement 正文与全部 scenarios 原样保留。
- `execution-intent`: EXI-001 requirement 正文与 scenarios 原样保留，delta MODIFIED 补 `> req:` header 声明，修复 `missingReqHeader` 结构违规（语义不变；main spec `> req:` header 由 apply 显式 metadata 编辑补齐并归档后重查）。
- `low-scale-real-auto`: LSA-001 requirement 正文与 scenarios 原样保留，delta MODIFIED 补 `> req:` header 声明，修复 `missingReqHeader` 结构违规（语义不变；main spec `> req:` header 由 apply 显式 metadata 编辑补齐并归档后重查）。

## Impact

- 新增治理脚本：`openspec/governance/check_project_gate.py`（aggregate，标准库）+ OpenSpec 侧 focused negative fixtures/tests（置于 `openspec/tests/governance/`，不放入 `deep_research_harness/tests`，保持单向依赖）。
- 修改：`openspec/config.yaml`（rules.specs / rules.tasks / stale path）、`openspec/governance/README.md`、`openspec/governance/req-registry.yaml`（登记 4 个 ID）、`openspec/governance/project-structure.toml`（`.repro-tmp/` 加入 `[ignored_paths]` entries + required-path 注册 `check_project_gate.py`、`openspec/tests/governance/` 测试树与全部六个 component checker）、`openspec/specs/deep-research-agent-charter/spec.md`（DRC-010 MODIFIED，经本 change delta + 归档 sync）、`openspec/specs/research-graph-lifecycle/spec.md`（REG-022）、`execution-intent` 与 `low-scale-real-auto` 的 main spec `> req:` header（apply 显式 metadata 编辑）、`.agents/skills/{openspec-propose,polish-openspec-change,openspec-archive-change}/SKILL.md`、`deep_research_harness/tests/**`（REJ-009/REG-022/SCR-006/EXI-001/LSA-001 的 evidence 绑定，task 2.7 的 wave2_synthesis import-boundary focused 测试）、`deep_research_harness/docs/testing-and-evaluation.md`（文档口径）。
- **apply 期暴露的 masked architecture drift（bounded-repair，属本 change）**：`.repro-tmp/` 修复后 architecture checker 暴露出 `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py` 直接 `from pydantic import ValidationError` 的既有 import 违规（`[imports].nodes` 只允许 domain/engine/langgraph；此前被更早失败的 ignore-entry 掩盖）。修复保持行为不变：domain `workflow_outcomes.py` 新增窄谓词 `is_structured_validation_error`，node 改经该谓词识别 pydantic 结构化校验失败（含多行 ValidationError 仍归 `synthesis_request_shape_invalid`），并加 focused 测试；**不**宽限 nodes 层 import policy。这是 apply review 的 bounded-repair finding（见 7.1/4.9），非无关 blocker。
- 明确不改：外部 `openspec` CLI（v1.9.0，不可改）；`deep_research_harness/Makefile`（不恢复 governance target、不新增对 OpenSpec 的依赖）；portable `openspec/change-guidance/core/change-practice.md`（PCG 产品中立与 snapshot 合同）；`deerflow/` gitlink；任何 runtime/API/应用行为（唯一的应用源码触碰是上述 behavior-preserving 的 import-boundary 修复，无行为语义变化）。

## Change Focus

- **Primary module / causal owner:** `openspec/governance/` 的 project OpenSpec authoring/verification lifecycle——规则语义由六个既有 checker 拥有，新增 aggregate 只编排。
- **Seam classification:** deterministic-guardrail 全部为确定性治理检查与退出码聚合，无模型参与；aggregate 不拥有任何语义判断。
- **Question:** 如何让规划期（propose/polish）与 closeout（archive 前）对机械治理规则的访问成为仓内 agent workflow 的强制可验证步骤，同时不破坏 Harness 独立性、不修改外部 openspec CLI、不把非权威 reservation 伪装成 registry 登记？
- **Necessary adjacent/external contracts:** deep-research-agent-charter（DRC-010 MODIFIED：独立 gate 的停止权威来自确定性 checker 退出码而非 guidance/evidence、native archive 不阻断；DRC-004 Focus Card enforcement 与 DRC-012 单向依赖仅被复用/读取，语义不变）：plan gate 复用既有 Focus Card 检查以不重复实现 charter 语义；portable-change-guidance（PCG-001 kernel 产品中立、PCG-005 snapshot 合同）：delta mechanics 放 config rules.specs 而非 core 以保产品中立与 digest 合同；evaluation-hardening（EVH-005 gate 组成、EVH-010 evidence 机制）：aggregate closeout 与 Harness verify 并列以分离治理与应用 evidence 并保证 closeout 证据一致；project-structure（PRS-006 ignore policy、PRS-009 canonical structure 注册）：.repro-tmp/ 与 aggregate 的注册以进入结构注册表。
- **Evidence seam:** OpenSpec 侧 aggregate 与 scoped component modes 的 focused 测试（negative fixtures：未登记新 ID、retired reuse、active-delta 间 ID 冲突、标题内嵌 ID、空扫描 fail-closed、退出码传播；缺 Focus Card 与 MODIFIED 丢场景目前为 orchestration 传播级模拟，真实 planted 证据另行跟踪，见 task 4.11）+ six-checker closeout 全 0 + `cd deep_research_harness && UV_OFFLINE=1 make verify` 独立绿 + `openspec validate openspec-rule-reachability --strict` + `git diff HEAD --check` + gitlink/子模块零改动。**evidence 边界**：`LSA-001` 的确定性 mode-003 CLI/report contract 测试只证明 wiring 与 report 门禁；minimal-profile single-topic 与两轮 wave2 gate budget 行为由 hitl1/gate integration 组合测试证明（与 EXI-001 同一 seam）；真实 provider/source 行为（真实 report 内容、真实 source URLs）由**保留日期的真实 003 run attestation / 真实 acceptance evidence**（如 runbook-003 记录的真实 `RESULT: PASS`）单独证明——确定性测试不声称证明真实 run，不以 minimal-intent 测试过度主张整个 requirement；`EXI-001` 以 non-interactive intake + HITL profile 构造 + wave2 gate budget 三个测试构成**组合 seam**（分别断言入口接收、profile 消费、gate 解析，联合覆盖 requirement 的三个通道）。
- **Not in scope:** 不改外部 openspec CLI；不恢复 Harness governance target 或让 Harness 依赖 OpenSpec；不改 portable core/change-practice.md；不做 registry↔header 单一来源化生成；不做 Reader Roles/Line Budgets/T4 单源化（本 change 不自动创建后续 change）；不重写已归档 change 历史；不改任何 runtime/应用行为。
- **Triggered review policies:** control-placement

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| 归档前门禁从"manual `make verify` + validate"变为"OpenSpec aggregate closeout（六 checker）+ Harness verify 并列" | 无模型判断；规则语义由既有 checker 拥有，本 change 不新增任何语义判断 | `req-registry.yaml` 是 accepted ID 唯一权威；六个 checker 是各自规则语义 owner；aggregate 只编排与退出码聚合 | bounded-repair | 失败恢复 = 修复后重跑：仓内 archive workflow 在 closeout 非零时停止，作者修复所指的 checker/file 后重跑至全 0；native `openspec archive` 仍可被直接调用（外部 CLI 不可改），故**不宣称全局 non-bypassable**。Harness 独立性（DRC-012/PRS-009 单向依赖）；registry 只增不删不重用；MODIFIED 场景完整性由 `openspec validate --strict` 兜底；reservation 非权威、hard stop 仅限仓内 workflows | 复用六个既有 checker，不新建语义检查；新增一个编排脚本 + scoped component modes，避免"polish 要求已登记而只有 apply 能登记"的循环 | aggregate 自身 focused negative fixtures + six-checker closeout 全 0 + Harness verify 独立绿 |
| ID 分配可查性从"归档后后知后觉"前移到"plan 占号 + closeout 一致性" | 无模型判断；reservation 是只读输出，不构成登记 | registry 登记仅由 apply 的显式任务写入；plan reservation 非权威 | bounded-repair | 失败恢复 = 修复后重跑：plan gate 非零时 polish 报 `not ready`，作者修复 delta/registry/evidence 后重跑；native CLI 可绕过，故不宣称全局 non-bypassable。未登记/冲突/retired reuse 在 plan 阶段红，closeout 阶段整体非零；plan/closeout 双 phase 均只读 | 复用 check_project_reqs 的 registry 解析语义，仅新增 active-change 隔离视图 | plan phase 的 focused tests（collision/retired/header/title）+ closeout 全量 checker 0 退出 |
