# Plan: OpenSpec 产品边界与可移植性最终方案

> 状态：最终方案，待以一个 source Program Change 实施，并由最小 sibling adoption change set 证明
> 更新：2026-08-17
> 范围：仅重构 OpenSpec authoring / governance practice；不修改 Deep Research runtime，不读取或修改 `deerflow/`

## 目标

把本仓库已经验证有效的 change admission、authority、recovery、evidence 和 agent-workflow review
实践整理成可供另一个 DeerFlow / LangGraph agent workflow 采用的版本，同时保持 Deep Research
自己的产品语义、行为规范、项目结构和运行时事实各归其主。

最终承诺不是“新产品只改 `openspec/product/`”，而是：

> 新产品从 `openspec/product/` 进入适配；复制的 portable kernel 与所选 profiles 保持不变；
> 产品语义、行为 specs、项目结构和验证入口由目标仓库在各自 owner 中完成本地绑定。

## 当前仓库上下文

- `deep_research_harness/` 是本仓库应用与 runtime 主体。
- `deerflow/` 是锁定 commit 的上游 submodule，只通过 public API leverage。
- `openspec/specs/` 拥有 approved behavior；存在 active change 时，其单一 owning delta 拥有 pending
  behavior。
- code、typed contracts 和 tests 拥有当前运行时事实与行为证据。
- `openspec/governance/project-structure.toml` 拥有精确项目结构；项目 architecture checker 保护它。
- `deep_research_harness/CONTEXT.md` 当前拥有 Deep Research glossary。
- `openspec/product/deep-research.md` 当前只是产品阅读入口，不是 spec、runtime config 或结构 manifest。

这些 current authorities 在对应 migration change 完成前继续有效。本计划是未来改造的计划权威，
不会仅凭位于 `_backlog/` 就改写现行事实。

## 最终架构

```text
OpenSpec native workflow
  specs / changes / validate
              │
              ▼
Portable Kernel
  owner / focus / authority / evidence / trigger grammar
              │
              ├───────────────┬────────────────────┐
              ▼               ▼                    ▼
 Workflow-Control       Node-Agent           DeerFlow-Downstream
 Profile                Profile              Profile
              └───────────────┴────────────────────┘
                              │ selected by
                              ▼
                    Project-Owned Composition
             config / local routes / checker wrapper
                    /             |              \
                   ▼              ▼               ▼
          Product Front Door   Local Governance   Native Authorities
          product/README.md    manifests/guards   specs/code/tests
```

各层的逐文件 owner 与允许内容由
[`02-boundary-and-file-matrix.md`](openspec-product-boundary-portability/02-boundary-and-file-matrix.md)
唯一规定。

## 最终决定

### D1. `product/` 是产品前门

终态使用 `openspec/product/README.md` 作为稳定入口。它说明产品价值、领域语言 owner、行为 owner、
current-fact owner、启用的 authoring profiles 和项目治理入口，并通过链接路由到这些 owner。

它不复制 requirements、运行时状态、package/import 规则、验证命令或 tool permission。新增
product 文件必须有独立且稳定的事实辖区；不会预建固定 handbook 文件树。

### D2. 行为与当前事实不迁入 `product/`

- approved behavior 留在 main specs；
- pending behavior 留在 active delta；
- current behavior 留在 code、typed contracts 和 tests；
- archive 保留历史文本；
- product context 只做产品导向与 owner 路由。

因此，`specs/` 中出现 Deep Research 语义是正确的，不属于“通用化失败”。

### D3. 可移植单元是 kernel 与显式 profiles

Portable Kernel 只保留所有采用者都需要的最小规则：

- 一个 change 有一个 primary causal owner；
- 相邻 contract 以具体问题进入范围；
- fact authority 与 projection 分离；
- evidence 匹配被改变的决定；
- policy 由 trigger 选择；
- guidance 和 review record 不授予 runtime authority。

V1 profiles 固定为：

1. `workflow-control`：状态、失败、恢复、人类决定、participant outcome 和 control placement；
2. `node-agent`：LLM-bearing node 的认知职责、tool posture、candidate admission 和 deterministic handoff；
3. `deerflow-downstream`：只使用 public API、普通 downstream work 不修改或默认 source-browse 上游。

三个 profiles 彼此独立启用。一个 change 同时命中多个 trigger 时，必须组合并满足全部相关 policies；
一个 profile 的 review 不能代替另一个。

### D4. 本地 composition 是合法且必要的

`openspec/config.yaml`、`openspec/change-guidance/README.md`、本地 policy registry、entry-document
budgets、Program Focus、项目 module map 和 checker wrapper 都是 project-owned composition。

它们可以出现 Deep Research 名称和本地路径，但只能链接或组合已有 owner，不能复制结构 manifest、
requirements 或 runtime facts。不同产品会修改这些本地文件；这不算 fork portable kernel。

### D5. 不创建产品实例 schema

V1 不创建 `product/instance.yaml` 或等价的万能产品 manifest。source/test roots、package/import
grammar、gitlink、required paths 继续由项目结构治理拥有；verification entry 继续由本地 authoring
route 与 Makefile 拥有。

只有两个真实采用者反复需要同一组、且不与现有 owner 重叠的 machine fields 时，才另行设计最小
governance binding schema。

### D6. Architecture checker 保持项目专有

`check_project_architecture.py` 继续保护 Deep Research 的 package、layer、node grammar、fixture、
wheel 和 gitlink 约束。V1 分享“exact registry + fail-closed checker + planted negative”模式，
不把当前架构参数化成通用 DSL。

只有出现第二个真实代码消费者时，才抽安全路径解析、exact-member 检查等小型 primitives。

### D7. 当前 glossary 不随 portability 改造迁移

`deep_research_harness/CONTEXT.md` 在本计划终态仍是 Deep Research glossary owner。
`product/README.md` 路由到它。任何物理迁移都属于另一个 terminology-record cutover，不是本计划
的 phase，也不是完成 portability 的条件。

### D8. V1 以目标仓库拥有的快照分发

采用者从固定 source revision 复制 allowlisted kernel 与 profiles；复制后由目标仓库拥有，
不自动跟随本仓升级。V1 不提供共享 package、submodule、generator 或 semantic-version
compatibility。

完整 export boundary 和采用证据由
[`03-adoption-contract.md`](openspec-product-boundary-portability/03-adoption-contract.md) 唯一规定。

### D9. 真实 sibling adoption 是发布门槛

合成 fixtures 证明语法、路径、profile optionality 和 planted negatives；真实 sibling product
用真实 changes 证明语义可采用性。没有真实 adoption spike，只能称 portability candidate，
不能称 portable release。

### D10. 用最少的 Change、以可恢复 workstreams 推进

当前仓库只创建一个 Program-form OpenSpec Change；kernel extraction、profile/local composition、
product-front-door cutover、candidate release 和 adoption finding closure 都是该 Change 内按顺序关闭的
workstreams，不各建 Change。真实 sibling 位于另一仓库，优先用一个 target-native Program Change
承载 adoption；若目标治理不支持 multi-owner program，则复用已经 active、且会按 portable practice
实际执行的真实 changes 作为 T1–T3 证据，不为凑数量临时发明语法。历史 archive 只能作为背景证据。

当前仓库的 V1 新建 change budget 硬限制为 **1**；跨仓优选新建总数为 **2**。Target 已经 active
的 feature changes 不计入新建 budget，但必须进入同一 adoption evidence boundary。只有 target 缺少
program form、又没有可复用的 active changes 时，target decision owner 才能批准额外 bounded changes，
并在 adoption evidence 记录原因；source budget 不随之增长。Source Change 在 sibling adoption 通过前保持 active；
adoption finding 在同一个 active Source Change 中修正，不另开补丁 Change。
每个 workstream 保持当前 CLI 和 Deep Research behavior，并有 rollback 或 forward-repair 路径。
顺序、guards、兼容面和完成证据由
[`04-migration-and-proof.md`](openspec-product-boundary-portability/04-migration-and-proof.md) 唯一规定。

## V1 交付边界

V1 包含：

- 产品中性的 Change Guidance kernel prose；
- `workflow-control`、`node-agent`、`deerflow-downstream` profiles；
- 产品中性的 proposal/review grammar validator；
- 当前仓库的 local composition 与兼容 wrapper；
- 一个真实 sibling product adoption record。

V1 不包含：

- Deep Research specs、changes、archive、glossary、prompts 或 runtime docs；
- `project-structure.toml`、`req-registry.yaml` 或 Deep Research requirement IDs；
- `check_project_architecture.py` 的通用化；
- req/spec/coverage checkers 的跨项目发布；
- 自动升级、共享 package 或 generator；
- glossary relocation。

## 实施工作流

1. **Extract validation seam**：先从 `check_change_guidance.py` 分离纯 validator，并完成 paragraph-level
   ownership ledger；当前 guidance paths 和 prose owners 暂不移动。
2. **Cut over guidance topology**：一次性把 portable prose、profiles 与 local extensions 迁到目标
   拓扑，同步 charter、project-structure spec、manifest、checker、tests、config 和 current links。
3. **Cut over product entry**：原子迁移 `product/deep-research.md` 到 `product/README.md`，同步
   current links、structure registry/spec 和 exact-member guard；glossary 仍在原 owner。
4. **Run sibling adoption**：在真实、结构明显不同的 agent-workflow 项目，用一个 target Program
   Change 或已有真实 changes 完成三种代表性 workstream，证明采用时无需编辑 kernel。
5. **Close findings**：任何要求修改 kernel 的 adoption finding 回到仍 active 的 Source Program
   Change 修正并重新发布 candidate；目标仓库在同一个 adoption change set 中重新 vendoring，不能以
   静默 fork 冒充成功。

## 完成状态

本计划只有在以下结果同时成立时关闭：

- kernel、profiles、local composition、product context 与 native authorities 各有唯一 owner；
- portable export 中没有 Deep Research literals、路径或 `DRC/PRS/EVH @impl` IDs；
- 当前 Deep Research checker CLI、proposal grammar、spec IDs 和 runtime behavior 保持兼容；
- `product/README.md` 是小型前门，且没有成为第二份 spec、structure manifest 或 runtime config；
- architecture checker 未为可移植性弱化；
- core、每个 profile 和 local wrapper 都有可恢复的 planted negative proof；
- 真实 sibling adoption 满足 [采用成功定义](openspec-product-boundary-portability/03-adoption-contract.md)；
- 当前 glossary 仍有唯一 owner；
- `deerflow/` gitlink 与 public-API-only 边界保持不变。

## Reviewer 关注点

另一位 Agent review 本方案时，应重点判断：

1. `02` 是否给每类事实分配了唯一且合适的 owner；
2. portable kernel 是否仍暗含 Deep Research layout、术语或 requirement namespace；
3. `03` 的 adoption contract 是否能在真实 sibling repo 中执行而无需 fork kernel；
4. `04` 是否完整覆盖兼容、失败恢复、旧入口退休和 guard sensitivity；
5. 是否存在更小的 V1 仍能达到相同终态，或任何被遗漏的 cross-boundary consumer。

Reviewer 不需要读取 `deerflow/` 源码，也不应把本计划扩成 runtime、glossary 或 architecture rewrite。

## 文档集

- [文档职责与阅读顺序](openspec-product-boundary-portability/README.md)
- [最终 Review 发现与设计依据](openspec-product-boundary-portability/01-review-findings.md)
- [边界、owner 与逐文件处置](openspec-product-boundary-portability/02-boundary-and-file-matrix.md)
- [跨项目采用与分发契约](openspec-product-boundary-portability/03-adoption-contract.md)
- [迁移、兼容、恢复与完成证明](openspec-product-boundary-portability/04-migration-and-proof.md)

## Progress Plan（OpenSpec Change 追踪）

### Tracking 规则

- [ ] 在创建 Change 前，本节是执行准备与阶段状态的 tracking source。
- [ ] 创建 Source Change 后，将细粒度任务写入
  `openspec/changes/make-openspec-practice-portable/tasks.md`；该文件成为 source 执行状态权威，本节只
  同步 workstream gate，不复制细任务状态。
- [ ] 确定 target adoption change set 后，将细粒度任务写入各 owning `tasks.md`；本节只记录跨仓
  T0–T4 与 archive handshake，不复制 target 任务状态。
- [ ] 每次勾选一个 workstream gate 时，在对应 `tasks.md` 或 evidence 中留下可定位的完成证据。

### Change Budget 与 Scope Lock

- [ ] 确认当前仓库只创建一个 Program Change：`make-openspec-practice-portable`。
- [ ] 选定 sibling adoption 形态：优先一个 target-native Program Change
  `adopt-portable-openspec-practice`；若复用已经 active 的真实 changes，记录其 IDs 与 owning scopes，
  并确认它们会按 portable practice 完成而不是事后套表。
- [ ] 冻结当前仓新建 change budget 为 `1`、跨仓优选新建总数为 `2`；source phase、workstream、
  修复轮次均不另建 Change，target 既有 active changes 只作为 adoption workstreams 计入 evidence。
- [ ] 若 target 既无 program form 也无可复用 active changes，由 target decision owner 批准最小额外
  bounded changes，记录不可合并原因；不得为满足数字而创建 shared owner 或临时 program grammar。
- [ ] Source proposal 使用 `## Program Focus`，冻结完整 Candidate / obligation budget、workstream
  顺序、共享 archive invariant 和 recovery rule；不再同时写 ordinary `## Change Focus`。
- [ ] Source capability delta 只包含：新增 `portable-change-guidance`，修改
  `deep-research-agent-charter`，修改 `project-structure`。
- [ ] Source implementation scope 只包含：Change Guidance kernel/profiles/local composition、纯
  validator 与兼容 wrapper、product front-door cutover、相关 governance manifests/checkers、
  authoring entry documents、focused governance tests、export/evidence artifacts。
- [ ] 明确排除：Deep Research runtime behavior、生产代码与 prompts、glossary body/authority 迁移、
  `check_project_architecture.py` 语义通用化、req/spec/coverage checker 发布、共享 package/generator、
  `product/instance.yaml`、archive 重写和任何 `deerflow/` 变更。
- [ ] 冻结 sibling target、decision owner、仓库写入权限与 T0–T4 owners；没有真实 target
  时不创建 Source Change，也不以合成 fixture 降低完成门槛。

### Source Program Change

- [ ] **S0 — Baseline gate**：记录无冲突 active change、current consumers、现有 CLI/grammar、
  exact-member rules、requirement IDs、glossary owner、完整 verification baseline 与 DeerFlow gitlink
  状态；完成后创建并 strict-validate Source Program Change。
- [ ] **S1 — Portable validation seam**：先植入会暴露产品/path/ID 耦合的 red fixtures，再抽取无 repo
  traversal、无 shell、无本地 literal/ID 的纯 validator；兼容 wrapper 的 path、arguments、0/1 semantics
  和当前 proposal outcome 保持不变。
- [ ] **S2 — Guidance topology cutover**：原子迁移 core、三个 opt-in profiles 与 local extensions；同一
  workstream 同步三份 capability deltas、`project-structure.toml`、checker、config、entry links 和
  focused tests，删除旧可编辑 policy paths，不保留 compatibility copy。
- [ ] **S3 — Product front-door cutover**：原子将 `product/deep-research.md` 切换为
  `product/README.md`，同步 current consumers、spec/registry/checker 和 negative fixtures；保持 60/80
  本地 budget 与现有 glossary owner，拒绝 machine config、第二 glossary 或第二 specification。
- [ ] **S4 — Candidate release gate**：运行 source 全部门禁，为 allowlist 生成 file digests，记录
  source candidate commit；状态仅标记 `portability candidate`，Source Change 保持 active。

### Sibling Adoption Change Set

- [ ] **T0 — Adoption foundation**：Target adoption change 建立自己的 product front door、specs/changes
  baseline、structure owner、local config/router/wrapper 和 requirement namespace；按 allowlist vendoring
  byte-identical kernel、selected profiles 与 validator。
- [ ] **T1 — Deterministic workstream**：用 target 的真实 deterministic decision surface 证明 core
  owner/evidence route，不触发不相关的 node-agent obligations。
- [ ] **T2 — Node-agent workstream**：用 target 的真实 LLM-bearing surface 闭合 cognitive role、tool
  enforcer、candidate admission、failure bound 与 deterministic proof。
- [ ] **T3 — Human/recovery workstream**：用 target 的真实 human decision 或 recovery surface闭合 typed
  decision、fact/recovery owners、terminal disposition、legal next action 与 deterministic proof。
- [ ] **T4 — Adoption evidence gate**：运行 target 全部门禁与 planted negatives，生成
  `evidence/portable-practice-adoption.md`，记录 source candidate、digests、local files、三个 workstream
  结果、deviations 和 disposition；尚 active 的 target adoption changes 暂不 archive。

### Finding Loop 与 Archive Handshake

- [ ] Target 若必须修改 portable file，将 disposition 设为 `needs-source-fix`；在同一个 active Source
  Change 的所属 workstream 中补 task、修正并发布新 candidate，不新增 source Change。
- [ ] Target 在同一个 adoption change set 中重新 vendoring 新 candidate、重跑受影响 workstreams 和
  evidence；重复直至 portable digests 不再被本地修改且无未关闭 finding，不为修复轮次新增 Change。
- [ ] Target 先提交 passing adoption evidence 并保持 active；Source 引用 target repository、commit
  与 evidence，完成最终 source verification 和 planted-negative review。
- [ ] Source 将已被 target 证明的 candidate commit + export digest 标记为 V1 release，完成全部
  Source tasks 后 archive `make-openspec-practice-portable`。
- [ ] Target 确认所采用 candidate 已被 source ratify，完成 strict validation 后 archive adoption
  change set；若引用 target 原有 active changes，只 archive 已完成且本来应在此时关闭的 owning
  changes，不为 adoption 改写历史 archive 或提前关闭仍有产品任务的 Change。
- [ ] 更新本节所有 stage gates，确认主计划“完成状态”和 `04` 的最终关闭门槛全部有证据后关闭本
  backlog plan。

### Scope 变化规则

- [ ] 新发现若为已批准终态所必需、且仍在上述 Source scope 内：在同一个 Program Change 的 owning
  workstream 增补 task、reason 和 done condition，不新建 Change。
- [ ] 新发现若改变 runtime behavior、glossary authority、Deep Research architecture semantics、
  public/persisted contract，或引入共享发布系统：停止扩 scope，记入独立 backlog；只有本计划完成后
  经明确批准才创建后续 Change。
- [ ] 新发现若使 target 不再是合法真实 adopter：Program decision owner 先 re-scope 或更换 target，
  记录原因与未复用证据；不能用 fixture 替代，也不能在未更新 Program Focus 时静默扩大范围。
- [ ] 任一 workstream 无法恢复到其 terminal invariant 时，整个 Program Change 保持 active，选择
  repair、rollback 或 plan-level re-scope；不 partial archive。
