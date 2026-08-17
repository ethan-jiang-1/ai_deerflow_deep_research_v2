# Plan: OpenSpec 产品边界与可移植性重构结论

> 类型: 分析 / 设计 | 更新: 2026-08-17 | 状态: 待独立 review；尚未创建 OpenSpec change，未授权实施

## 给 Reviewer 的独立上下文

### 这份 review 要判断什么

这是一个**跨产品可移植性方向审查**，不是 Deep Research runtime 的代码审查，也不是要求
现在实现目录迁移。请判断以下主张是否成立、是否过度设计，以及应如何收窄：

> 能否将本仓库已经验证有效的 agent-workflow 变更/治理实践，整理成可供另一个
> DeerFlow / LangGraph node-centric agentic loop 复用的结构；同时把 Deep Research 专有的
> 产品语义集中到 `openspec/product/`，而不破坏 OpenSpec 的 `specs/` / `changes/` 权威模型？

本计划的暂定答案是：可以，但 `openspec/product/` 需要从当前的单页阅读地图演进为“产品上下文
目录”，并配一个只给治理工具使用的实例参数文件；通用 guidance/checker 则必须真正参数化。
这只是待验证的设计方向，**不是已经批准的架构事实**。

### 当前仓库和边界

- 本仓库的应用是 `deep_research_harness/`；它是基于 DeerFlow 的 Deep Research 产品。
- `deerflow/` 是上游 git submodule，只能通过 public API 使用，不能修改，也不需要为本 review
  source-browse；本计划不建议改变这个边界。
- 当前 `openspec/product/deep-research.md` 只有 26 行，是一个非权威阅读地图；它的角色是告诉
  读者到哪里找答案，而不是定义 behavior、runtime facts 或 node authoring。
- 但产品词汇和大量产品语义目前仍主要位于 `deep_research_harness/CONTEXT.md`（483 行）；因此
  复制当前 OpenSpec support tree 到另一产品后，不能只替换 `openspec/product/` 就得到干净的
  产品替换。
- 当前 Change Guidance、authoring config、structure registry 和 checker 中仍有
  `Deep Research`、`deep_research_harness/`、`deerflow/`、具体模块布局、测试根和验证命令等
  实例绑定。它们证明现有项目受保护，但也说明它还不是可直接复用的模板。
- 当前 `openspec list` 没有 active change。本计划与此前的 runtime identifiers/dead-code
  工作无关；review 或后续实现不得把不相关的 runtime 维护混入这一独立 change。

### 当前权威模型（不得在 review 中意外推翻）

| 问题 | 当前/目标中的权威 owner | `product/` 能做什么 | `product/` 不能做什么 |
| --- | --- | --- | --- |
| 已批准或待批准的可观察行为 | `openspec/specs/` 的 main spec 与一个 active delta | 路由到对应 capability | 复制、覆盖或自行新增 requirement |
| 现在运行时做什么、如何证明 | code、typed contracts、tests 和实际运行时 owner | 说明应读哪个 owner | 宣称 current fact、route、state write 或 permission |
| 产品词汇、产品目标、参与者和工作流导向 | 当前主要在 `deep_research_harness/CONTEXT.md`；目标是由 `openspec/product/` 集中入口 | 解释产品并链接权威行为/代码 source | 变成第二份 runtime/config/specification |
| 通用 change/review 实践 | `openspec/change-guidance/` | 按 trigger 路由产品 change | 创建 runtime authority 或产品特有行为 |
| 结构、登记与机械检查 | `openspec/governance/` 及其 owned specs/checkers | 通过 instance profile 告诉 checker 如何定位项目 | 成为 runtime configuration 或绕过 checker |

“产品上下文目录”只是 `openspec/product/` 的职责名称；它**不是**新工具、新格式、运行时目录或
第二套 OpenSpec workflow。

### 已核实的硬事实

以下事实来自当前 checkout；reviewer 可以据此检查本计划是否正确推导，而不是把它们当成建议：

1. `openspec/governance/check_change_guidance.py` 明确要求 `openspec/product/` 的 member set
   恰好为 `deep-research.md`，并对该文件执行 60 行 warning / 80 行 hard failure。
2. `openspec/specs/project-structure/spec.md` 与
   `openspec/governance/project-structure.toml` 同样登记了该单文件 product tree；要扩展为多文件
   产品上下文目录，必须改变 spec、registry、checker 和 negative fixtures，不能只新建文件。
3. `openspec/config.yaml`、`openspec/change-guidance/README.md`、`principles.md` 及多份 policy
   同时承载有价值的通用原则和 Deep Research 的路径/术语/具体约束。
4. `check_project_architecture.py`、`check_project_req_coverage.py`、`check_project_specs.py` 不只是
   generic algorithm：它们分别持有 Deep Research source/test roots、package/import structure 或
   vocabulary/test-coverage 假设。
5. 2026-08-15 的 archived change
   `openspec/changes/archive/2026-08-15-separate-product-context-from-generic-openspec-guidance/`
   有意把 product 做成一个小导航页，以降低默认阅读成本；本计划提出的是**新的、尚未采纳的
   下一阶段目标**，不是声称当时的单页设计错误。

### Reviewer 的最小阅读集

请先完整阅读本文件；若要验证结论，按下表的顺序读，不需要扫描整个仓库：

| 优先级 | 文件 | 需要验证的内容 |
| --- | --- | --- |
| 必读 | `openspec/product/deep-research.md` | 当前 product page 的真实范围与非权威边界 |
| 必读 | `openspec/config.yaml` | 哪些 authoring rules 已经写死产品/路径/验证命令 |
| 必读 | `openspec/change-guidance/README.md`、`principles.md` | 哪些原则可泛化，哪些仍是 Deep Research-specific |
| 必读 | `openspec/change-guidance/policies/local-context.md`、`node-agent-workflow-integrity.md`、`agent-information-map.md` | Focus Card、cognitive-first route 与 product/doc binding 的具体耦合 |
| 必读 | `openspec/governance/README.md`、`architecture-policy.md` | governance 的实际职责和 authority boundary |
| 必读 | `openspec/governance/check_change_guidance.py` | 单文件 product tree、路径、line budget 和 Focus Card 的硬编码证据 |
| 必读 | `openspec/governance/check_project_architecture.py`、`check_project_req_coverage.py`、`check_project_specs.py` | 哪些 checker inputs 仍是产品实例数据而非 reusable algorithm |
| 必读 | `openspec/specs/deep-research-agent-charter/spec.md`、`openspec/specs/project-structure/spec.md` | proposed cutover 会改变的现有规范承诺 |
| 背景 | `deep_research_harness/AGENTS.md`、`deep_research_harness/CONTEXT.md` | 应用边界、产品 glossary 与现有 authoring entry surface |
| 仅需核对历史意图 | `openspec/changes/archive/2026-08-15-separate-product-context-from-generic-openspec-guidance/` | 为什么当前 product page 被刻意做小；不要将 archive 当作 current authority |

不需要阅读 `deerflow/` 源码、广泛阅读 archived changes、或检查 Deep Research runtime 实现，
除非 reviewer 发现本计划对一个具体 current fact 的描述与上述最小资料冲突。

### Reviewer 应输出什么

请给出简洁、可行动的设计 review，而非直接写代码或创建 change：

1. **结论**：赞成方向、赞成但需要改动，或不赞成；先说明理由。
2. **关键发现**：按严重度列出 authority、迁移、兼容性、scope 或可验证性问题，并引用具体
   文件/规则。
3. **对目标边界的回答**：哪些内容真的应该在 `product/`，哪些必须继续留在
   `specs/`、`changes/`、`change-guidance/` 或 `governance/`。
4. **对 `instance.yaml` 的判断**：它是否是解决实例绑定的最小机制；若不是，给出更简单且能
   被 checker 消费的替代方案。
5. **验证门槛**：双产品 fixture 是否足够；如果不够，指出最小可证伪的替代验证。
6. **建议的下一步**：若方向成立，给出一个最小独立 OpenSpec change 的边界；若不成立，说明
   应缩减或放弃哪一部分。

reviewer 不应把“可复用”理解为删除本产品的 specs、术语或架构约束；目标是把它们隔离为可替换
的产品输入，而不是抹掉产品差异。

### 需要被挑战的开放问题

- `product/instance.yaml` 是否真的比维持一个独立 project manifest 更好？它会不会把产品上下文
  与结构/工具配置不必要地耦合？
- 产品 glossary 是否必须从 `deep_research_harness/CONTEXT.md` 物理迁到 `openspec/product/`，
  还是只应在 `product/README.md` 集中路由、保留 glossary 原位？避免双写的最小 cutover 是什么？
- `node-agentic-workflow` 应是 reusable opt-in profile，还是现有 Change Guidance policy 已足够，
  不应新增一层 profiles/？
- 一个第二产品的 fixture 能否充分证明 portable checker；还是应在真实 sibling repository 做
  adoption spike？两者各自的最低成本和可信度是什么？
- 当前架构 checker 很深地编码了 Deep Research layer/import constraints。应把它参数化、拆成
  generic core + Deep Research adapter，还是承认它本来就是产品 guard，只复用较小的治理子集？
- 除了本计划列出的 source/test roots、词汇和 verification command 外，是否还有被忽略的
  Deep Research binding，使“主要改 `product/`”成为不真实的承诺？

### 非目标和 review 护栏

- 不在此 review 中修改 application code、Deep Research runtime、prompts、graph、state、tests
  或 `deerflow/` submodule。
- 不在此 review 中把 `product/` 变成 main spec、active delta、runtime YAML 或 prompt/tool
  permission source。
- 不以 archive 文本替代 current source of truth，也不删除 archive 来清除旧名词。
- 不要求所有 agent workflow 都有 LLM node；cognitive-first discipline 只应在产品明确选择的
  model-bearing surface 上适用。
- 不因“想复用”而预先设计一个覆盖所有未来产品的万能 schema；每个参数都必须有当前 checker
  consumer 和第二实例的验证理由。

## 结论

可以把这里沉淀成可复用的 DeerFlow / LangGraph agent-workflow 开发实践，但不是把
`Deep Research` 替换成一个占位词就够了。当前分层已经有正确的方向：
`openspec/product/deep-research.md` 把产品导向从 Change Guidance 中分出；但它被明确
限制为一个最多 80 行、仅含一个文件的导航页。因此它不能承载产品本体，也不能让另一个
产品只改这个目录就安全复用其余治理。

推荐的目标是：把 `openspec/product/` 升级为**产品上下文目录 + 实例参数入口**，让它集中
产品语义与产品实例绑定；把 `change-guidance/`、`governance/` 的原则、路由和 checker
逻辑改为无产品名的通用机制；保留 OpenSpec 原生的 `specs/` 与 `changes/` 作为行为要求和
pending delta 的权威位置。这样“改产品”时，读者首先只需进入 `product/`；而改变源码根、
验证命令或架构约束时，也只改该目录里的声明式实例参数，不必复制或编辑治理程序。

这里的“只盯着 `product/` 调整”应理解为**产品适配的唯一入口**，而不是把所有行为规范
物理搬进 `product/`。main spec 和 active delta 必须继续留在 `openspec/specs/` 与
`openspec/changes/`，否则会破坏 OpenSpec 的原生发现、validate 和单一行为权威。

## 已核对的现状

| 现有面 | 已做对的事情 | 可移植性问题 | 目标处置 |
| --- | --- | --- | --- |
| `openspec/product/deep-research.md` | 是非权威的产品阅读地图，不复制 behavior 或 runtime facts | `check_change_guidance.py` 要求它是 `product/` 唯一文件且不超过 80 行，无法成为产品知识入口 | 保留小 `README.md` 地图；放宽目录为受治理的产品上下文目录，不再把整个目录等同于单一短页 |
| `deep_research_harness/CONTEXT.md` | 保存 Deep Research 术语、用户、Run Bundle、研究结果等产品语言 | 大量产品语义仍在 harness 内，另一个产品无法仅改 `openspec/product/` 完成替换 | 将产品语言迁到 `product/domain-language.md`；原路径在一次受控 cutover 后只保留必要入口或改为指针 |
| `change-guidance/` | primary causal owner、最小上下文、事实/投影分离、恢复边界、最低责任证据面很有价值 | 标题、路径、模块表、研究结果、Run Bundle、DeerFlow 限制混进通用 policy | 抽出通用原则；产品具体术语、模块表和作者导航从产品 profile 读取 |
| `openspec/config.yaml` | source-of-truth hierarchy、Focus Card、测试优先级和“不把 guidance 当 authority”都可复用 | 写死 `deep_research_harness/`、`deerflow/`、归档命令和 Deep Research proposal | 只保留通用 authoring contract；实例路径、框架边界、验证入口由 `product/instance.yaml` 提供 |
| `governance/` | registry/checker/closeout-evidence 的“可机械验证、非 runtime authority”模式可复用 | `project-structure.toml` 和多个 checker 写死包名、目录、产品文档名、测试根与词汇 | 保留 checker 算法与 schema；把实例数据改为 profile 驱动，并以第二个 fixture product 证明它确实可移植 |
| `openspec/specs/` 与 active delta | 行为要求由 capability spec/delta 所有，位置符合 OpenSpec | 它们必然包含 Deep Research 行为，不能也不应搬走 | 保留为产品行为的例外：`product/capability-map.md` 只路由到它们，不复制 requirements |

当前 2026-08-15 的 `separate-product-context-from-generic-openspec-guidance` 已成功完成第一步：
它把“产品是什么”的简短入口从通用导航中切出来。它同时刻意禁止产品目录扩展为 handbook。
本结论不是否定那次改动，而是提出下一阶段：当目标从“减小默认阅读面”变成“跨产品复用”时，
需要把它的单页约束改为一个更明确、仍受边界保护的产品上下文目录。

## 应保留为通用实践的核心

下列规则适合另一个 node-centric agentic loop；它们不依赖 Deep Research 的研究方法或
Run Bundle 模型：

1. **事实与权限各有 owner**：Markdown、LLM 输出、CLI/TUI、诊断和缓存可以投影事实，
   不能成为第二个 state / lifecycle / permission authority。
2. **一个 change 有一个 primary causal owner**：相邻模块以要回答的 contract question
   进入范围，而不是因为“也许有用”就扩大阅读面。
3. **Cognition proposes; deterministic owners decide**：模型和人都提交有界 candidate；
   typed parser、evaluator、materializer 或 controller 决定是否产生 effect。
4. **恢复必须闭合**：失败类别、直接事实 owner、恢复 owner、次数/时间上界、terminal
   disposition 和下一合法动作应可指出，不能让 presentation 偷偷成为 retry controller。
5. **人和 AI 消费同一受控事实**：人类文本可解释，机器接口用稳定字段；两者不靠自然语言
   猜 lifecycle。
6. **证据匹配决策**：先选最低责任的确定性 seam，再因实际 claim 升级到 scenario、真实依赖
   或全流程；文档不是行为证据。
7. **trigger-based guidance**：policy 只在明确触发条件下阅读，且始终比 capability spec 更
   轻，不产生 runtime authority。
8. **认知优先修改面是可选 agentic profile**：对于确有 LLM-bearing node 的产品，先检查
   capability、prompt/context、feedback/repair，再检查 deterministic handoff；对纯确定性或
   非模型 workflow，不强迫生成 prompt 或 agent 义务。

`node-agent-workflow-integrity`、`control-placement`、`workflow-outcome-review` 这三类
review record 特别适合分享给新的 agent workflow；应作为通用的可选 profile，而不是带有
Deep Research 名称、路径和 research-specific outcome 的固定文档。

## 应归入产品上下文目录的内容

以下内容应以产品文件为入口，或由该目录的 instance profile 声明；它们不应再散落在通用
Change Guidance / governance prose 中。“产品上下文目录”只是对 `openspec/product/` 的职责描述，
不是要引入新的机制、格式或工具。

| 类别 | Deep Research 中的例子 | 建议产品 owner |
| --- | --- | --- |
| 产品目标与价值 | research question、evidence、scope、assumptions、uncertainty、Research Outcome | `product/README.md` 与 `product/outcome.md` |
| 领域语言与参与者 | Primary User、Research Confirmation、Run Bundle、Refinement、Research State | `product/domain-language.md` |
| 产品工作流轮廓 | 研究阶段、human decision 的语义、报告/证据边界、产品特有 recovery 语义 | `product/workflow.md`，精确行为仍链接至 capability specs |
| 产品 capability 地图 | 哪些 main spec 共同定义当前产品能力 | `product/capability-map.md`，只列 owner/link，不复制 requirement |
| 产品特有评估标准 | evidence quality、research uncertainty、node cognition 的产品质量要求 | `product/evaluation-posture.md` 或 owning evaluation specs |
| 项目实例绑定 | 应用根、source/test root、package 名、host framework public-API boundary、验证 target、模块角色映射 | `product/instance.yaml` |

`instance.yaml` 是实现“换一个 DeerFlow 产品仍主要改 `product/`”的关键，但它不是 runtime
configuration，也不是行为规范。它只拥有**通用治理如何定位这个产品实例**的声明，例如：

```yaml
schema: product-instance/v1
application:
  root: deep_research_harness
  source_root: deep_research_harness/src/deerflow_deep_research
  test_root: deep_research_harness/tests
framework:
  dependency: deerflow
  access_boundary: public-api-only
navigation:
  domain_language: product/domain-language.md
  workflow: product/workflow.md
verification:
  full_target: "cd deep_research_harness && UV_OFFLINE=1 make verify"
```

它不能声明 graph route、state write、tool permission、模型角色或当前 runtime fact；这些仍由
spec、typed contract、code 和 test 拥有。若另一产品的 module layout、framework binding 或
验证 target 不同，只修改这个 profile 与它所指向的产品文件；generic checker 不需要 fork。

## 建议的目标拓扑

```text
openspec/
├── README.md                         # 通用 OpenSpec 导航
├── config.yaml                       # 通用 authoring contract；先路由 product profile
├── product/                          # 唯一的产品/实例适配入口
│   ├── README.md                     # <= 80 行的产品阅读地图
│   ├── outcome.md                    # 产品要交付的价值、边界和非目标
│   ├── domain-language.md            # 产品 glossary / actors / lifecycle language
│   ├── workflow.md                   # 产品特有 workflow orientation
│   ├── capability-map.md             # 到 specs/deltas 的非权威路由
│   ├── evaluation-posture.md         # 如产品需要认知/质量评估
│   └── instance.yaml                 # 治理定位用的实例参数，非 runtime config
├── change-guidance/                  # 无产品名的可复用设计/审查实践
│   ├── README.md
│   ├── principles.md
│   ├── profiles/
│   │   └── node-agentic-workflow.md  # 可选：LLM node 的 cognitive-first route
│   └── policies/
├── governance/                       # schema-driven checker、registry protocol、closeout tool
├── specs/                            # OpenSpec 原生：产品 observable behavior 的权威
└── changes/                          # OpenSpec 原生：pending delta 的权威
```

这里 `product/` 不是第二个 `specs/`：它负责让人和工具知道“这是哪种产品、在哪读细节、通用
治理如何定位它”；`specs/` 仍负责“系统必须做什么”。这种分法既保留 OpenSpec 的 native
workflow，也让另一个产品不需要在 `change-guidance/` 中反复清理 Deep Research 残留。

## 必须参数化的现有治理

不参数化以下内容，复制目录后会得到表面通用、实际仍指向 Deep Research 的假模板：

| 当前实现 | 通用化后的输入 | 证明方式 |
| --- | --- | --- |
| `check_change_guidance.py` 的 `deep-research.md`、`deep_research_harness/`、Focus Gate anchors | `product/instance.yaml` 中的产品入口、应用 guide 和可选 agentic profile | 用一个不同 product id / app root 的 fixture profile 跑同一 checker |
| `check_project_architecture.py` 的包名、source root、fixture root、Gitlink 和层规则 | profile 指向的结构 manifest；层规则作为产品选择的 architecture profile | 同一 checker 分别验证 Deep Research 与第二个最小 agent workflow fixture |
| `check_project_req_coverage.py` 的测试根 | `instance.yaml.test_root` | 两个不同测试根都能发现 `@impl` 覆盖与 planted omission |
| `check_project_specs.py` 的历史术语扫描 | 产品 allowlist / retired vocabulary 规则，或独立的 product-language checker | 新产品不用继承 Deep Research 的禁词；Deep Research 仍保留自己的负向 fixture |
| `project-structure.toml` 与 `req-registry.yaml` 的实例数据 | schema 不变，但地址、ID namespace、目录/导入清单从产品 profile 解析 | 迁移前先制造第二套数据；不能只把 Python 文件复制一份 |
| `config.yaml` 的验证命令、DeerFlow 边界和路径 | 抽象的“read instance profile / run declared verification target”规则 | 通用 config 中不再出现 `deep_research_harness` 或 `Deep Research` |

`selected_change_closeout.py` 的“caller-declared Git boundary、只记录非语义证据、绝不替代
native archive”的契约相对通用，可以原样复用；它只需要从 profile 得到 change root 或保持
OpenSpec 默认路径，不应获得产品 runtime authority。

## 迁移原则与不可做的事

- 不把所有 Deep Research 文本机械移动到 `product/`。`openspec/specs/` 的 requirements、
  active delta、代码、typed contracts 和 tests 是合理且必要的产品特异性例外。
- 不让产品上下文目录复制或覆盖 main spec。`capability-map.md` 只能链接，不能重述完整行为。
- 不把 `instance.yaml` 变成 runtime YAML、prompt 权限或 graph configuration；它只能配置
  治理发现和检查器输入。
- 不把当前 `node-edit-map.md` 的研究专用路径照搬为所有项目的硬门槛。它应改为可选择的
  `node-agentic-workflow` profile，产品在 `workflow.md` 中声明何时适用。
- 不删除历史 archive 来“去词汇化”；archive 是历史证据。活跃权威和通用模板才需要 clean。
- 不修改 `deerflow/`。新的产品 profile 只声明“通过 public API 使用 host framework”的边界；
  不把上游实现细节抄进产品或通用 guidance。

## 建议实施顺序

1. 新建一个专门的 OpenSpec change，例如
   `generalize-openspec-product-profile-and-governance`；它只改 documentation/governance，
   不改 Deep Research runtime。
2. 先定义 `product/instance.yaml` schema 和一个第二产品 fixture（可用最小的 incident-triage
   或 task-execution node workflow），先让现有 checker 的硬编码测试变红。
3. 将 checker 算法改为读取 profile；保留 Deep Research profile 的输出不变，并让第二 fixture
   通过。只有这个双实例证明通过，才能声称实践已泛化。
4. 将现有 `product/deep-research.md` 演进为 `product/README.md`，新增产品上下文文件；把
   `deep_research_harness/CONTEXT.md` 的产品 glossary 经一次链接切换迁入，避免长期双写。
5. 从 `config.yaml`、`change-guidance/`、`governance/README.md` 和通用 policies 去除 Deep
   Research 名称、运行路径、研究结果和产品特有命令；用中性的“product / application / host
   framework / declared verification target”替代。
6. 把 LLM node 的认知优先流程改为 opt-in profile；由每个产品的 `workflow.md` 明确是否采用，
   而非以目录或 `run_agent` 调用猜测。
7. 更新 `project-structure` 与 agent-charter 的主 spec、registry、negative fixtures 和 entry
   documents；通过 strict OpenSpec validation、双 profile checker fixture 和各产品的最小验证。
8. 在所有 active authority 已切换后，删除现在“`product/` 只能有一个
   `deep-research.md`”的结构守卫；archive 保持原样。

## 风险与取舍

| 风险 | 缓解 |
| --- | --- |
| 产品上下文目录变成第二份 specification 或巨型 handbook | `README.md` 保持小；每个产品上下文文件声明导航/语言/实例绑定职责；行为只在 main spec/delta |
| 通用化把关键 agentic 安全边界稀释为口号 | 保留明确的 optional node-agent profile、review table 和 deterministic handoff evidence |
| checker 看似 profile-driven，仍暗含 Deep Research 默认值 | 第二个异构 fixture 是发布门槛；没有双实例绿色，不宣称可复用 |
| `instance.yaml` 变成另一个 runtime 配置入口 | checker 拒绝 runtime keys；文档明确它不授予 route、permission、state write 或模型调用 |
| 一次迁移造成 glossary 与 links 双写漂移 | 使用单次 cutover：先加目标 owner 和迁移测试，再替换所有活跃入口；不保留长期 compatibility copy |
| 结构守卫重构范围过大 | 先保留现有 Deep Research 行为和 checker outputs，再最小化参数化；架构 profile 是否通用由第二产品 fixture 验证，而不是预先抽象所有层 |

## 可验收的终态

- 在 `openspec/product/` 内即可找到一个产品的目标、术语、workflow orientation、capability
  路由、评估姿态和实例绑定；普通读者无需先读 Change Guidance 才能理解产品。
- `change-guidance/`、`governance/README.md`、`openspec/config.yaml` 的活跃通用 prose 不再
  写死 `Deep Research`、`deep_research_harness`、Run Bundle、研究 outcome 或具体验证命令。
- `specs/` / `changes/` 仍是唯一的 required behavior / pending behavior authority，产品目录
  不重复 requirements。
- 同一套治理 checker 至少通过 Deep Research 和一个名称、目录、测试根都不同的 node-agent
  workflow fixture；两个 fixture 都包含 planted negative control。
- 另一个 DeerFlow 产品的接入工作以复制 generic practice 后填写 `product/` 上下文/profile
  开始，而不是 fork Python checker、全局替换名词或修改 DeerFlow 源码。

## 落地关联

这是一份架构/可移植性结论，不直接修改当前 Deep Research runtime 或其 OpenSpec 权威。
如果采纳，应由上面的独立 change 承担结构守卫、checker、主 spec、entry 文档与 glossary
cutover；此前的 runtime identifiers/dead-code 工作与本计划无关，不应被混入。
