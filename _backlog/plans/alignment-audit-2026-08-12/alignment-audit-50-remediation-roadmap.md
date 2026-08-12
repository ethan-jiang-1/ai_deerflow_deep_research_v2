# Alignment Audit 50 - Remediation Roadmap

> 类型: 整改路线 / 非实施 change
> 审计日期: 2026-08-12
> 基线: `65df2571108cc6b4b81f55d3ba8542786a810b39`

返回[总览](alignment-audit-00-current-state.md)。本路线只规定依赖、change 边界和验收
条件；当前未创建 active OpenSpec change，也未授权任何具体行为选择。

## 原则

1. **先解冲突，再清词典。** A-003/A-004 未决时，直接改 CONTEXT 只是在冲突两侧中
   擅自选边。
2. **一次迁移一个 authority cluster。** V2 topology 必须同步 config、spec、guide、
   manifest、checker 和 README，不能靠零散文案 PR。
3. **不读取或修改 DeerFlow 源码。** 上游保护采用 gitlink/path/diff evidence。
4. **不把绿色标签升级成语义证明。** A-009 用风险分层映射增强，不建立第二套穷举
   test catalog。
5. **CONTEXT 只做词典。** 行为归 main spec，取舍归 ADR，实施步骤归 change/tasks，
   current/planned 能力归明确 owner。

## 依赖图

```text
R1 Rubric/Runner decision (A-003) -----+
                                       +--> R4 CONTEXT/ADR normalization (A-005..A-008)
R2 Post-loss diagnostic decision (A-004)+

R3 V2 topology migration (A-001/A-002) ----> R5 semantic traceability hardening (A-009)

R1, R2, R3 可分别提案；R4 等 R1/R2，R5 可在 R3 后独立进行。
```

## R1 - 统一 Rubric / Runner 边界

**覆盖 findings:** A-003
**类型:** 行为/权威决策 change
**优先级:** 第一

### 需要决策

只能选择一个可执行合同：

| 方案 | Runner/admission 可读取什么 | 代价 |
| --- | --- | --- |
| Review-only Rubric | 只保留 opaque identity/digest；不解析 criteria；subject fixture 不含 review criteria | 要回退当前 EVH admission 与 typed fixture 设计 |
| Case execution metadata | admission 可验证 criterion IDs 作为 control integrity metadata；Rubric 内容不面向 model、不决定 execution output | 需修改 CES、CONTEXT、ADR 0025，精确定义“execution input” |

当前实现与更新的 EVH requirements 更接近第二种，但审计不代替 proposal 作决定。

### 同步范围

- CES 与 EVH owning requirements；
- `deep_research_harness/CONTEXT.md` 的 Runner、Case、Rubric 词条；
- ADR 0025 状态/措辞；
- typed scenario contracts、control admission、Runner/subject adapter；
- detector tests：必须能让被禁止的 Rubric authority crossing 先 red。

### 完成条件

- 任一 author 只读 CES + EVH 能得到唯一答案；
- Rubric identity、criteria、content、model-facing input、quality verdict 五种概念有明确
  owner，不再用一个 “input” 覆盖所有层；
- focused tests 与 `make verify` 全绿；
- CONTEXT 不新增 SHALL 或实施步骤。

## R2 - 统一 Bundle loss 后诊断合同

**覆盖 findings:** A-004，并约束 A-007 Support Handoff
**类型:** 生命周期/诊断 authority change
**优先级:** 第二

### 推荐基线

保留当前实现选择：所有 retained lifecycle diagnosis 都是 Bundle-local；Bundle loss 后
inspection 返回 unavailable，不读取 external copy。原因是 RUS、REJ、typed store 和
确定性测试已经一致，并且它最符合“Bundle 是唯一 durable Run record”的领域模型。

若产品确实需要 external diagnostic，则必须显式新增：typed owner、retention/redaction、
authorization、inspection result、deletion semantics 与 no-authority tests。不能只保留
一句 “may outlive but cannot authorize”。

### 同步范围

- RER、RUS、REJ main specs；
- External Run Observation、Bundle Loss、Support Handoff 词条；
- ADR 0006 及其状态；
- implementation/tests 仅在最终选择要求改变时调整。

### 完成条件

- Bundle 删除后，三份 main specs 对“磁盘上能否留存、reader 能否读取、UI 能否显示”
  分别给出同一答案；
- 没有 diagnostic、journal、handoff 或 cache 能恢复/选择/授权 Run；
- 删除 Bundle 的 focused tests 覆盖 typed result、inspection 和 fresh start。

## R3 - 迁移 V2 上游拓扑与保护门禁

**覆盖 findings:** A-001、A-002
**类型:** governance / project structure change
**优先级:** 与 R1/R2 可并行，但必须在大规模后续 change 前完成

### 一个 change 内必须同步

- `openspec/config.yaml` context、proposal rule、archive rule；
- `deep_research_harness/AGENTS.md`；
- Charter 与 local-context policy；
- 7 份受影响 main specs，只改作为 root/upstream path 的引用；
- `project-structure.toml` 与 architecture checker；
- selected-change closeout 的 upstream clean/diff evidence；
- `deep_research_harness/README.md` sibling dependency 文案；
- focused detector fixtures/tests。

### 设计约束

- canonical upstream boundary 是 root `deerflow/` gitlink；
- downstream code 仍可通过 public `deerflow.*` API 和 editable harness dependency 使用
  框架；
- ordinary change 不允许修改 gitlink 或 submodule worktree；升级上游必须是另行批准、
  明确拥有 boundary 的 change；
- architecture checker 不遍历 DeerFlow 源码；
- 根 `backend/` / `frontend/` 不再称 upstream mirrors。对于数据库 backend 等普通
  名词不得误替换。

### 必需 detector

1. manifest 仍声明不存在 upstream root 时失败；
2. `deerflow` missing 或 index mode 非 `160000` 时失败；
3. ordinary selected change 包含 gitlink/submodule diff 时失败；
4. README/guide/config/main spec 中重新出现 canonical V1 root-boundary phrase 时失败；
5. 合法 gitlink 且 downstream-only diff 时通过。

### 完成条件

- 所有 authority 对根 topology 给出同一答案；
- `make verify` 与 strict OpenSpec validation 通过；
- detector 的 red/green fixture 证明不是空扫描；
- 无命令读取 DeerFlow 源码来完成验证。

## R4 - 收口 CONTEXT 与 ADR 状态

**覆盖 findings:** A-005、A-006、A-007、A-008
**依赖:** R1、R2 的决定已归档或已同步 main specs
**类型:** domain language / documentation governance change

### 工作包

1. 删除应用 CONTEXT 尾部 6 个设计章节；保留术语，移除重复 requirement/ADR/task。
2. 修正 Workspace 为 execution-scoped working directory，不承诺 Bundle 是其子目录。
3. 用 registry 实际范围描述 Cognitive Evaluation Suite smoke coverage；未来全节点覆盖
   放 roadmap/spec，不写成 current glossary fact。
4. 对 readable review report 做二选一：由 spec/type/test 实现，或移除词典强制语气。
5. 拆分 `Final Report Artifact`（current）与 `Research Report Export`（planned）；
   Support Handoff、Local-First TUI 同样显式标 planned，除非已有正向 owning spec。
6. 修正 Charter Index：每个 trigger 对应一个 policy，一个 change 可选择多个 policies。
7. 给仍参与 current/planned 叙述的 ADR 增加一致状态元数据，至少复核 0002、0003、
   0006、0008、0010；保留 0007 superseded 模式。

### 完成条件

- 每个 `CONTEXT.md` 条目都是短词典定义 + Avoid，没有顶层实施计划；
- `CONTEXT-MAP.md` 仍只映射三个 context；
- 每个 current capability 都能链接到 owning spec 和真实入口；planned term 明写 planned；
- glossary lint/detector 能拒绝 archived change 名称、`V1 structural change must` 等计划
  语言，而不把普通历史词汇误判为错误。

## R5 - 增强高风险语义 traceability

**覆盖 findings:** A-009
**类型:** evidence governance hardening
**优先级:** R1-R4 后；不阻断当前 bug fix

### 不做什么

- 不要求 388 个 alive IDs 全部复制进 `EVIDENCE_CLAIMS`；
- 不把 183 个无 central claim 或 248 个无 requirement impact 的 ID 称为未实现；
- 不要求每个 production `.py` 都机械添加 `@impl`；
- 不用 LLM 评审替代确定性断言。

### 建议机制

对新建或 materially changed 的高风险 requirement，记录一个 bounded semantic mapping：

```text
requirement id
owning production seam
exact scenario selector
asserted invariant / failure risk
evidence class
```

全局 `@impl` 继续承担廉价 inventory；semantic mapping 只服务 change review、P1/P0
contracts、authority/lifecycle/security boundaries 与周期审计。

### 必需 detector

- module-level `@impl XYZ-001` + 一个与 XYZ 无关的 test 不得满足 stronger mapping；
- selector 必须 exact collected node id，不能是 glob/prefix；
- mapping 的 requirement、seam、selector 与 risk 均必须存在且可解析；
- ordinary low-risk requirement 可以继续只用 `@impl`，避免治理成本失控。

## 建议的 OpenSpec change 切分

| 顺序 | 建议 change slug | 覆盖 | 为什么独立 |
| --- | --- | --- | --- |
| 1 | `reconcile-evaluation-rubric-execution-boundary` | R1 / A-003 | 独立行为决策，影响 evaluation authority |
| 2 | `reconcile-post-loss-diagnostic-retention` | R2 / A-004 | 独立生命周期与隐私/留存决策 |
| 3 | `migrate-v2-upstream-gitlink-governance` | R3 / A-001,A-002 | 结构治理迁移，可独立验证且不读上游源码 |
| 4 | `normalize-context-capability-status` | R4 / A-005..A-008 | 等前两项决策后一次性清词典与 ADR 状态 |
| 5 | `harden-high-risk-semantic-traceability` | R5 / A-009 | 证据机制升级，不应混入行为修复 |

这些 slug 是审计建议，不代表 change 已创建。真正开始时应使用 `openspec new change`，
按当前 schema 生成 proposal/design/specs/tasks，并在每个 change 的 Focus Card 中只声明其
真实 owner 与触发 policies。

## 全部整改后的最终验收

完成不应以“文档都改过”为标准，而应同时满足：

- A-001 至 A-009 各自有 archived change 或明确接受的风险决定；
- 49+ main specs（按当时实际数量）strict valid，且交叉语义审计不再发现 A-003/A-004；
- config、guides、Charter、policies、specs、manifest、README 对 V2 topology 一致；
- upstream detector 对真实错误 red、对合法 gitlink green，且不扫描 DeerFlow 源码；
- 三份 CONTEXT 和 map 只承担各自 domain language；
- `UV_OFFLINE=1 make verify` 在最终 HEAD 退出 0；
- live/Gateway 未执行证据继续被明确标注，不被 deterministic green 掩盖。
