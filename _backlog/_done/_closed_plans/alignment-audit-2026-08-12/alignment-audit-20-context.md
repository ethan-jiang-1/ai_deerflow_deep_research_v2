# Alignment Audit 20 - Context Alignment

> 审计日期: 2026-08-12
> Git 快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 判准: `CONTEXT.md` 是 bounded context 的精炼词典，不是 spec、ADR、路线图、
> 实施计划或当前状态总表

返回[总览](alignment-audit-00-current-state.md)，整改依赖见
[50 - Remediation Roadmap](alignment-audit-50-remediation-roadmap.md)。

## 盘点

排除只读 `deerflow/` 后，仓库自有 context 恰好是：

| 文件 | 行数 / 术语数 | 当前判断 |
| --- | --- | --- |
| `CONTEXT.md` | 14 / 2 | 对齐；只定义 Host Runtime、Downstream Product |
| `deep_research_harness/CONTEXT.md` | 541 / 68 | 部分错位；前 467 行以词典为主，尾部 74 行不是词典 |
| `openspec/CONTEXT.md` | 35 / 6 | 基本对齐；有一处 policy 基数错位 |
| `CONTEXT-MAP.md` | 16 / 不适用 | 对齐；三 context 与关系映射正确 |

这意味着“所有 CONTEXT 都错位”并不成立。问题高度集中在应用词典，且可以按所有权
拆解，而不是整体重写三份文件。

## 对齐项

### 根 Host context

根词典只定义 DeerFlow 提供 Host Runtime、Deep Research 是单独拥有 outcome 的
Downstream Product。它没有把 Host 写成产品，也没有复制上游实现细节；与根
`AGENTS.md:3-25` 的两层边界一致。

### Context Map

`CONTEXT-MAP.md:1-16` 已正确表达：

- DeerFlow Host 提供公共 runtime boundary；
- Deep Research Product 拥有用户研究结果；
- OpenSpec Governance 记录并约束 change，但不扩张 runtime authority。

因此不需要新增第二份 map，也不应把 map 移入某个子目录。

### OpenSpec 非权威边界

`openspec/CONTEXT.md:1-19,26-35` 对 Change、Required Behavior、Cross-Cutting
Review Guidance 与 closeout evidence 的非运行时权威描述，与当前 Charter
`openspec/agent-charter/README.md:1-19` 一致。这是近期 topology flattening 后的
有效模型，不是历史残渣。

### 当前与 planned 用户入口

`deep_research_harness/CONTEXT.md:187-195` 已明确：专用 Primary User TUI 是
planned，当前用户路线是 Dedicated Agent + reflected `deep_research` tool；
`deep_research_harness/README.md:18-27` 给出相同入口分层。这部分应保留。

## Findings

### A-005 - P2 - 应用 CONTEXT 越过词典边界

#### 词典尾部复制了设计决定

`deep_research_harness/CONTEXT.md:468-541` 在分隔线后包含 6 个顶层设计章节：

1. People Initiate Evaluation Review
2. Reviews Are Separate Immutable Records
3. Review Records Are Traceable
4. Rubrics Are Case-Specific Review Authorities
5. Evaluation Control And Run Data Are Separate
6. The Cognitive Control Program Is The First Modification Seam

这些内容分别由 ADR 0022-0026、main specs 和 `local-context` policy 拥有，既没有
词条格式，也重复了行为/设计权威。尤其：

- `CONTEXT.md:515-522` 仍称 “The new Cognitive Evaluation Suite” 和 “The V1
  structural change must explicitly update...”；但 `evals/control`、ignored runs、
  `runtime/evaluation`、结构清单和测试都已经落地。
- `CONTEXT.md:538-540` 直接耦合 archived change 名称。这是历史出处，不是领域语言。

这会让读者无法判断句子是 current fact、approved decision 还是尚待实施的 task。

#### Workspace 的物理关系写错

`CONTEXT.md:336-340` 说 Evaluation Run Workspace “contains ... bundle”。实际
`runtime/evaluation/runner.py:126-131,186-197,230-234` 在同一 execution root 下创建
并列的 `workspace/` 与 `bundle/`。这是小范围事实错误，但说明词典已经开始承担物理
布局说明，因而容易漂移。

#### ADR 状态不充分

应用 ADR 中，ADR 0007 明确带 `status: superseded by ADR-0028`；但至少 ADR 0002、
0003、0006、0008、0010 直接用当前语气描述 TUI、support、deployment 和 export，
没有 current/planned/superseded 状态。词典又引用这些决定的结果，导致旧产品路线
容易被读成当前能力。

#### 修复方向

- 删除 `CONTEXT.md:468-541` 的非词典章节，用 ADR/spec/policy 作为唯一 owner。
- 把 Workspace 词条改成 “execution-scoped working directory”；不要承诺 Bundle
  是其子目录。
- 为仍影响能力叙述的旧 ADR 增加统一状态元数据；状态应表达决定的现行性，不要靠
  文件编号或读者推断。

### A-006 - P2 - Cognitive Evaluation 词汇超出当前合同

#### “每个 LLM-bearing node 都有 smoke” 不是当前事实

`CONTEXT.md:396-401` 无条件声明每个 LLM-Bearing Node 至少有一个 Cognitive
Evaluation Suite smoke scenario。当前一手证据是：

- cognitive program board 在
  `tests/assets/cognitive_program_board.py:109-358` 记录 8 个
  `bounded cognitive program` logical nodes：HITL1、topic planning、Wave0、Wave1、
  Wave2、targeted evidence、readiness、final delivery。
- `evals/control/registry.json:1-53` 注册 8 个 case，但它们覆盖 public controller、
  topic planning、HITL1、Wave0、Wave1、Wave2 subject family；没有 targeted evidence、
  readiness 或 final delivery 的 Suite case。
- CES V1 main spec 只要求 HITL1 与 Wave0：
  `openspec/specs/cognitive-evaluation-suite/spec.md:156-175`。
- branch-local calibration selector 是另一种 evidence seam，不能自动等价于
  Cognitive Evaluation Suite Runner case。

因此该词条把 ADR 0013/0017 的路线目标写成了当前全覆盖事实。应改成当前注册范围，
或明确标注为 target state，并由后续 spec 拥有扩展计划。

#### readable report 不是 Review Record 合同

`CONTEXT.md:417-423` 声明 `limited` 和 `inconclusive` “require a readable report”。
当前合同只要求四态、evidence、confidence、unknowns、owning seam 和 follow-up：

- CES: `openspec/specs/cognitive-evaluation-suite/spec.md:111-154`
- protocol: `evals/control/review_protocol-v1.md:1-6`
- types: `domain/evaluation.py:772-801`
- focused test: `tests/eval/test_cognitive_evaluation_suite.py:544-570`

没有 typed report 字段或 admission rule。这里要么新增 owning spec/type/test，要么从
词典移除 “require”；不能让词典单独创造行为。

#### Rubric/Runner 不是单纯 CONTEXT 错字

`CONTEXT.md:310-334` 选择 Rubric review-only 解释，但 CES 与 EVH main specs 及当前
实现本身互相冲突。该问题是 A-003，详见
[10 - Spec / Implementation](alignment-audit-10-spec-implementation.md#a-003---p1---confirmed-mismatch-rubricrunner-execution-boundary-has-two-incompatible-owners)。
在 A-003 作出设计决策前，不应单独把词典改成任意一侧。

### A-007 - P2 - 产品能力词汇缺少 current/planned 分层

#### Research Report Export

`CONTEXT.md:450-454` 说 Primary User 可 reopen、copy、export Markdown。当前系统确实
产生并保存 `report.md` 与 citation map：

- owning spec: `openspec/specs/final-delivery-node/spec.md:6-25`
- publication: `graph/nodes/final_delivery/node.py:81-105`
- canonical path: `domain/bundle.py:50,161-165`

但这只证明 **final report artifact 已实现**。当前公共生命周期结果
`domain/lifecycle.py:528-553` 不携带 report body/ref；workbench artifact spec
`research-session-artifact-view/spec.md:11-35` 明确 metadata-only，并且不推断 report
路径；当前 public skill 只有 start/resume/status/cancel/refine lifecycle route，没有
Primary User export contract。故“artifact exists”不能推导出“Primary User can export”。

应拆成两个术语或两个状态：当前 `Final Report Artifact` 与 planned
`Research Report Export`。

#### Support Handoff

`CONTEXT.md:443-448` 将 Support Handoff 写成已存在的 bounded summary，但当前没有
独立 typed owner 或正向 main-spec capability；它在 RUS/REJ 中只作为 Bundle loss 后
禁止读取/保留的对象出现。ADR 0006 的 TUI/support 路线也未标状态。

应将它标 planned，或在未来 change 中为 Bundle-local handoff 定义 producer、schema、
redaction、授权 reader 和 evidence。A-004 决策前尤其不能暗示 external retention。

#### Local-First Deployment

`CONTEXT.md:462-465` 说第一个产品 deployment scope 是一位本地用户拥有专用 TUI，
但同文件 `:187-195` 和 README 明确专用 TUI 尚未是 current route。该句描述 ADR 0008
的产品方向，不是已交付界面。应标 planned target scope，或迁回 ADR。

### A-008 - P2 - Charter Index 的 policy 基数错位

`openspec/CONTEXT.md:21-24` 把 Charter Index 定义为从 change 路由到 “one relevant
... policy”；`openspec/agent-charter/README.md:18-19` 也说 “choose one policy”。
然而当前 authoritative/mechanical contract 明确支持一个 change 选择多个 policy：

- `openspec/config.yaml:43-49`: canonical policy names, comma-separated；
- DRC main spec `deep-research-agent-charter/spec.md:419-442`: comma-separated list，
  且 policy 条件可独立叠加；
- checker `check_agent_charter.py:586-633`: `value.split(",")` 后逐个验证。

更精确的语言应是：**每个 trigger 路由到一个 canonical policy；一个 change 可因多个
trigger 选择多个 policy。** 这既保留最小阅读原则，也不与机械合同冲突。

## 建议的词典收口形态

应用 `CONTEXT.md` 不需要按 541 行原地修修补补。建议先做语义决策，再按以下规则收口：

| 内容 | Owner | CONTEXT 中保留什么 |
| --- | --- | --- |
| 领域参与者、Run/Bundle、用户决定、结果 | `CONTEXT.md` + owning specs | 1-3 句稳定术语与 Avoid |
| observable behavior / SHALL | main spec | 只保留术语含义，不复制 requirement |
| hard-to-reverse trade-off | ADR | 词典不复制论证；必要时链接 current ADR |
| current/planned capability | README / capability spec / roadmap | 词条必须显式标时态，不由词典单独承诺 |
| 物理路径与文件清单 | project structure / code | 不放入词典，除非路径本身是稳定领域概念 |
| change admission / seam discipline | OpenSpec policy | 不复制到产品词典尾部 |

验收目标不是“越短越好”，而是每个词条都能回答“这个词是什么意思”，而不需要读者
猜测它同时是不是一个未完成任务。
