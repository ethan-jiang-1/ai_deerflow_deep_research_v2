# 最终 Review 发现与设计依据

> 角色：supporting evidence  
> 边界：本文件解释最终方案为何成立；决策以[主计划](../openspec-product-boundary-portability.md)和
> [边界矩阵](02-boundary-and-file-matrix.md)为准

## Review 范围

本次 review 核对了：

- `openspec/README.md`、`openspec/CONTEXT.md` 和 `openspec/config.yaml`；
- `openspec/product/`；
- `openspec/change-guidance/` 的入口、principles、node route 与全部 policies；
- `openspec/governance/` 的导航、policies、registries 和 checkers；
- 与产品入口、project structure、agent charter 相关的 main specs；
- 当前 Deep Research glossary owner 与 application boundary。

没有读取 `deerflow/` 源码，也没有把 archived changes 当作 current authority。

## F1. “产品相关 / 非产品相关”不足以决定物理位置

**核实事实**

- required behavior 必须由 `openspec/specs/` 和 active delta 拥有；
- current behavior 必须由 code、typed contracts 和 tests 拥有；
- source/test roots、imports、gitlink 和 required paths 已由
  [`project-structure.toml`](../../../openspec/governance/project-structure.toml) 拥有；
- product page 当前明确是 navigation only。

**设计含义**

产品语义应从 `product/` 进入，但不能把所有带产品名的事实搬进同一目录。最终边界必须按事实类型
分 owner，而不是按字符串是否含 “Deep Research” 二分。具体归属见
[内容路由规则](02-boundary-and-file-matrix.md#内容路由规则)。

## F2. `product/` 适合做稳定前门，不适合做万能实例配置

**核实事实**

[`product/deep-research.md`](../../../openspec/product/deep-research.md) 已能把 glossary、specs、
code/tests 和 node authoring route 分别指向其 owner。
[`check_change_guidance.py`](../../../openspec/governance/check_change_guidance.py) 同时对当前 product
member set 和 attention budget 做机械约束。

**设计含义**

稳定前门能降低采用者的发现成本；source root、test root、framework boundary 和 verification
command 则已有更合适的 project owner。产品目录只保留 Markdown 产品上下文与 owner routing，
不新增 machine instance schema。

## F3. `openspec/config.yaml` 是本地 composition，不是 portable source

**核实事实**

[`openspec/config.yaml`](../../../openspec/config.yaml) 同时包含：

- OpenSpec authoring 的通用 truth discipline；
- Deep Research proposal grammar；
- 本地 application path；
- DeerFlow downstream boundary；
- 当前验证命令和 closeout obligations。

**设计含义**

它的正确角色是把 native rules、portable kernel、enabled profiles 和 local owners 组合给当前
author。它可以有本地名称和链接，但 portable release 不应复制它，也不应要求所有产品逐字一致。

## F4. Change Guidance 的可移植 seam 存在于段落和规则层

**核实事实**

当前文件经常同时承载不同辖区。例如：

- [`principles.md`](../../../openspec/change-guidance/principles.md) 同时含通用 owner/evidence 原则、
  node cognition 和本地 operation guidance；
- [`local-context.md`](../../../openspec/change-guidance/policies/local-context.md) 同时含通用
  context-expansion gate、Deep Research layer map、Program Focus 和 seam classification；
- [`agent-information-map.md`](../../../openspec/change-guidance/policies/agent-information-map.md)
  的 reader-role 模式可借鉴，但路径、角色表和 budgets 都是本地事实。

**设计含义**

不能用“整文件复制”判断 portability。迁移必须先做 paragraph-level ownership ledger，再把规则放入
kernel、profile 或 local composition；每段只能有一个可编辑 owner。

## F5. Profiles 必须同时具有 project enablement 与 per-change trigger

**核实事实**

现有 `node-agent-workflow-integrity`、`workflow-outcome-review` 和 `control-placement` 都是条件
review records。它们描述 authoring/review obligations，不会创建 node、route、tool permission、
retry 或 state writer。

**设计含义**

“仓库启用 profile”只表示该类 policy 可被选择；“change 触发 policy”才产生对应 review record。
两层选择必须分开，disabled profile 不能给普通 change 增加字段或文件义务。

## F6. Architecture checker 是 Deep Research 项目合约

**核实事实**

[`check_project_architecture.py`](../../../openspec/governance/check_project_architecture.py) 和
[`project-structure.toml`](../../../openspec/governance/project-structure.toml) 共同保护：

- `deep_research_harness`、production/fixture package 与 wheel shape；
- `domain / engine / agents / graph / runtime` import policy；
- node package grammar、fixture recipe 和 upstream gitlink；
- 当前项目 exact required-path inventory。

**设计含义**

这些不是可由第二产品“填几个路径”复用的中性规则。V1 保留 checker 本地所有权，只分享 guard
模式；抽公共 primitive 必须等待第二个真实代码消费者。

## F7. Governance extensions 的 portability 程度不同

**核实事实**

- `openspec validate` 已拥有 native proposal/spec/delta validation；
- req registry、Focus Card、project architecture 和 requirement coverage 是本项目扩展；
- `check_project_reqs.py`、`check_project_specs.py`、`check_project_req_coverage.py` 都含本地
  ID、path、terminology 或 test-root assumptions；
- closeout evidence utility 具有独立性，但仍绑定当前 operation contract。

**设计含义**

V1 只抽 Change Guidance kernel 与其纯 validator。其他 checker 留在本地，不因“看起来可复用”
进入 export allowlist；后续每个抽取都必须说明它补 OpenSpec native 的哪个缺口。

## F8. Glossary 迁移是独立 record cutover

**核实事实**

[`deep_research_harness/CONTEXT.md`](../../../deep_research_harness/CONTEXT.md) 已是有多个 current
consumers 的 canonical Deep Research glossary。product map 和 node authoring route 都指向它。

**设计含义**

portability 不需要改变 glossary path。`product/README.md` 继续路由现有 owner；物理迁移若发生，
必须另行枚举 consumers、原子切换 current links、退休旧入口并证明术语完整性。

## F9. 合成 fixture 只能证明机械泛化

**核实事实**

不同 product id、path 和 policy set 的 fixture 能暴露硬编码，但无法证明另一个团队能：

- 选择正确 primary owner；
- 理解 profile trigger；
- 用自己的 specs、structure 和 IDs 组合规则；
- 在不改 kernel 的情况下完成真实 adoption workstreams。

**设计含义**

portability proof 必须由机械 fixtures 和真实 sibling adoption 共同组成。前者验证 validator，
后者验证语义与采用成本。

## F10. 分发形态本身是架构边界

**核实事实**

复制整个 `openspec/` 会连同 Deep Research specs、archive、IDs、glossary 和 architecture guard
一起传播；共享 package 或 generator 又会提前创建跨仓升级与兼容承诺。

**设计含义**

V1 使用固定 revision 的 allowlisted、target-owned snapshot。它先证明内容边界，再决定未来是否
需要发布系统。完整 contract 见 [`03-adoption-contract.md`](03-adoption-contract.md)。

## Review 闭合

以上发现均已在唯一 owner 文件中闭合：

- 内容与文件归属：`02`；
- 分发、采用与真实证明：`03`；
- migration、compatibility、recovery 与 guards：`04`。

本 review 没有遗留会改变 V1 目标的开放设计问题。共享 package、通用 architecture schema 和
glossary relocation 均明确排除在 V1 之外，而不是等待实施者临场选择。
