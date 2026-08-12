# Alignment Audit 00 - Current State

> 类型: 现状审计 / 对齐基线
> 审计日期: 2026-08-12
> Git 快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 范围: `deep_research_harness/`、`openspec/specs/`、仓库自有
> `CONTEXT.md` / `CONTEXT-MAP.md`、`openspec/config.yaml` 及其直接治理门禁
> 边界: 未读取或修改 `deerflow/` 源码；未修改应用、main specs、CONTEXT 或治理配置

## 系列导航

| 文档 | 回答的问题 |
| --- | --- |
| **00 - Current State（本文）** | 现在是否对齐、有哪些 findings、各报告是什么关系？ |
| [10 - Spec / Implementation](alignment-audit-10-spec-implementation.md) | main specs 与实现、测试证据是否语义一致？ |
| [20 - Context](alignment-audit-20-context.md) | 三份 `CONTEXT.md` 与 `CONTEXT-MAP.md` 是否仍是准确词典？ |
| [30 - OpenSpec Governance](alignment-audit-30-openspec-governance.md) | `openspec/config.yaml` 的思想、物理边界和门禁是否有历史残渣？ |
| [40 - Verification](alignment-audit-40-verification.md) | 哪些命令通过、它们能证明什么、不能证明什么？ |
| [50 - Remediation Roadmap](alignment-audit-50-remediation-roadmap.md) | 应按什么依赖顺序消除错位，完成条件是什么？ |
| [60 - Progressive Execution Plan](alignment-audit-60-progressive-execution-plan.md) | 如何用逐关 checkbox 和一次一个 OpenSpec change 推进整改？ |

## 结论

**当前不能宣称完全对齐。** 更准确的判断是：

- 实现和确定性测试基线健康，49 份 main specs 的 OpenSpec 结构有效，需求
  ID 注册与测试标签门禁均为绿色。
- 仍有 4 项 P1 级当前权威冲突或治理失效：V2 上游物理边界仍被写成不存在的
  根目录 `backend/` / `frontend/`；对应架构门禁因此会空扫描后通过；两组 main
  specs 对 Rubric/Runner 和 Bundle loss 后诊断留存给出互不兼容的要求。
- 三份仓库自有 `CONTEXT.md` 并非全部错位：根 Host 词典、根
  `CONTEXT-MAP.md` 和 OpenSpec 非权威边界整体正确；主要偏差集中在 541 行的
  `deep_research_harness/CONTEXT.md`，以及 `openspec/CONTEXT.md` 对 policy 数量的
  单数描述。
- `openspec/config.yaml` 的核心思想仍然成立：spec 是 required behavior、运行时
  authority 与 executable contracts 是 current facts、Charter 只提供 guidance、
  Focus Card 约束 scope。但其上游拓扑和 closeout 保护对象是从 V1 带入的历史残渣，
  与当前 git submodule 布局不一致。

因此现状不是“规格坏了”或“实现不可用”，而是：**机械一致性强，语义与治理边界
尚未完全收口。**

## 对齐矩阵

| 对齐面 | 状态 | 主要证据 | 判定 |
| --- | --- | --- | --- |
| main specs 结构 | 绿色 | `openspec validate --specs --strict`: 49/49 | 结构对齐，不代表语义互不冲突 |
| requirement ID 注册 | 绿色 | 392 registered，4 retired，0 orphan，661 occurrences | ID 账本对齐 |
| 确定性实现基线 | 绿色 | `make verify` 全链路退出 0 | 当前实现稳定，但有 4 个 Gateway 用例未执行 |
| spec <-> implementation 语义 | 部分对齐 | A-003、A-004；其余抽查与门禁健康 | 两组当前 main-spec 冲突必须先决策 |
| V2 仓库物理边界 | 不对齐 | 根仅有 `deerflow` gitlink；治理仍保护 `backend/` / `frontend/` | A-001、A-002 |
| 根 Host `CONTEXT.md` | 对齐 | 14 行、2 个术语；只定义 Host/Downstream | 保持 |
| Deep Research `CONTEXT.md` | 部分对齐 | 541 行、68 个术语，尾部另含 6 个设计决策 | A-005、A-006、A-007 |
| OpenSpec `CONTEXT.md` | 基本对齐 | 非运行时权威、统一 policy library 均正确 | A-008 需修正 policy 基数 |
| `CONTEXT-MAP.md` | 对齐 | 三个 bounded context 及关系均正确 | 保持 |
| `openspec/config.yaml` 思想 | 部分对齐 | authority / scope / evidence 原则正确；物理拓扑过期 | A-001、A-002 |
| 自动 traceability | 部分对齐 | 全局 `@impl` 标签完整，语义断言映射非全局强制 | A-009 |

## Finding 注册表

严重度含义：P0 = 当前数据/安全或主流程阻断；P1 = 当前权威冲突或关键治理失效；
P2 = 会误导后续设计、审查或能力判断；P3 = 文档卫生或低风险改进。本次未发现 P0。

| ID | 级别 | 结论 | 主报告 |
| --- | --- | --- | --- |
| A-001 | P1 | V2 的真实上游是根 `deerflow/` gitlink，但 config、guide、Charter、policy、7 份 main specs 和 README 仍复制 V1 `backend/` / `frontend/` 拓扑 | [30](alignment-audit-30-openspec-governance.md#a-001---p1---v2-上游物理边界仍是-v1-叙述) |
| A-002 | P1 | 架构门禁扫描不存在的 `backend` / `frontend` 后成功，closeout 也保护不存在目录；真实 gitlink 没有得到等价的 path/diff 级保护 | [30](alignment-audit-30-openspec-governance.md#a-002---p1---上游边界门禁存在空扫描假绿) |
| A-003 | P1 | CES 禁止 Rubric 成为 execution input，但 EVH 与当前 admission 要求执行场景携带并校验 rubric criteria | [10](alignment-audit-10-spec-implementation.md#a-003---p1---confirmed-mismatch-rubricrunner-execution-boundary-has-two-incompatible-owners) |
| A-004 | P1 | RER 允许外部诊断在 Bundle loss 后留存，RUS/REJ 与当前实现要求 Bundle-local only | [10](alignment-audit-10-spec-implementation.md#a-004---p1---confirmed-mismatch-external-diagnostics-after-bundle-loss) |
| A-005 | P2 | 应用 `CONTEXT.md` 混入 ADR、spec、实施计划和过期 V1 文本，并有 workspace/bundle 物理关系的事实错误 | [20](alignment-audit-20-context.md#a-005---p2---应用-context-越过词典边界) |
| A-006 | P2 | Cognitive Evaluation 词汇对“每个 LLM-bearing node 都有 smoke”及 limited/inconclusive readable report 作了当前过度承诺 | [20](alignment-audit-20-context.md#a-006---p2---cognitive-evaluation-词汇超出当前合同) |
| A-007 | P2 | Report Export、Support Handoff、Local-First TUI 混合了已实现 artifact、未拥有能力与 planned 产品方向 | [20](alignment-audit-20-context.md#a-007---p2---产品能力词汇缺少-currentplanned-分层) |
| A-008 | P2 | OpenSpec 词典/Charter 说选择 one policy，而 main spec、config 和 checker 支持一个 change 选择多个 policy | [20](alignment-audit-20-context.md#a-008---p2---charter-index-的-policy-基数错位) |
| A-009 | P2 | `@impl` 绿色证明 ID 被测试 docstring 引用，不证明每条 requirement/scenario 的断言语义等价 | [10](alignment-audit-10-spec-implementation.md#a-009---p2---coverage-gap-green-requirement-coverage-is-not-semantic-traceability) |

## 已确认对齐的部分

以下内容不应在整改中被误删或推翻：

1. 根 `AGENTS.md` 对两层仓库的描述是当前事实：应用在
   `deep_research_harness/`，框架是只 leverage、不修改的 `deerflow/` submodule。
2. `CONTEXT-MAP.md` 已存在，并正确映射 DeerFlow Host、Deep Research Product、
   OpenSpec Governance 三个 context；不存在“缺少 Context Map”问题。
3. 应用词典已经明确区分 planned `Primary User Interface` 与当前
   `Dedicated Agent + reflected deep_research tool`，这部分与 README 一致。
4. OpenSpec Charter 的 `guidance only; never runtime control` 权威边界已恢复并通过
   checker；审计早期曾见到的缺行属于已修复历史状态，不是当前 finding。
5. `pyproject.toml` 的 editable dependency 已正确指向
   `../deerflow/backend/packages/harness`；错误只在 README 的 Quick Start 文案。
6. 当前没有 active OpenSpec change，所以不存在活动 delta 暂时覆盖 main spec 的
   情况。

## 如何阅读这些报告

```text
00 当前结论
 |
 +-- 10 语义冲突与 traceability 边界 ----+
 |                                      |
 +-- 20 词典/能力时态错位 --------------+--> 50 整改依赖与验收条件
 |                                      |
 +-- 30 V2 拓扑与治理残渣 --------------+
 |
 +-- 40 可复现验证与证据边界
 |
 +-- 60 Progressive checkbox 执行账本（所有实施项初始未勾选）
```

- A-003、A-004 是**决策问题**，不能只靠改代码或改一个文档解决。
- A-001、A-002 是**V2 拓扑迁移问题**，不能通过继续增加
  `backend/` / `frontend/` 文案解决。
- A-005 至 A-008 是**词典权威和能力时态问题**，应在前述语义决策后清理，避免
  先把一个尚未决定的答案写入 `CONTEXT.md`。
- A-009 是**证据强度问题**，不表示有 183 或 248 个未实现需求，也不建议建立第二套
  穷举测试目录。

## 审计限制

- 按仓库边界铁律，本次没有读取 `deerflow/` 源码。对上游的判断只使用根目录
  gitlink、仓库自有说明和 editable dependency 路径。
- 未运行需要真实凭据的 live/release evidence；4 个真实 Gateway 集成测试因本机
  stack 不可用而明确 skip。
- 语义审计聚焦矛盾、所有权和可机器证明边界，不声称逐字人工证明 410 个
  Requirement、1206 个 Scenario 与每个断言完全等价。
- 本系列是现状与整改计划，不是 active OpenSpec change；没有修改当前行为或权威。
