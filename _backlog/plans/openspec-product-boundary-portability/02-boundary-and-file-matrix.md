# 边界、Owner 与逐文件处置

> 角色：本计划的内容归属与依赖边界权威  
> 不负责：采用流程与 migration 顺序

## 目标辖区

| 辖区 | 拥有 | 不拥有 |
| --- | --- | --- |
| OpenSpec Native | main specs、active delta、native validate/archive workflow | 本地 architecture、Focus 或 product convention |
| Portable Kernel | primary owner、scope admission、fact/projection、evidence、trigger grammar | 产品语义、framework、paths、IDs、runtime behavior |
| Reusable Profiles | 特定 workflow/host 类别的条件 authoring 与 review obligations | 当前项目是否真的有某个 node、route、tool 或 failure |
| Local Composition | enabled profiles、policy registry、entry paths、budgets、local proposal extensions、verification route | 被链接 owner 的正文 |
| Product Context | 产品价值、参与者/术语 owner、工作流导向和 owner links | requirements、current facts、project structure、runtime config |
| Project Governance | structure/ID registries、local checkers、guard lifecycle、exact inventory | 产品行为和 runtime authority |
| Runtime Authorities | code、typed contracts、tests、state/controller owners | authoring guidance |

本仓终态新增 `openspec/specs/portable-change-guidance/spec.md`，拥有 portable kernel/profile 的
observable authoring contract、export boundary、adoption proof 与 release-claim criteria。
`deep-research-agent-charter` 继续拥有本项目 local composition 和 contributor obligations；
`project-structure` 继续拥有 exact paths/member sets。三者不得互相复制辖区。

允许的依赖方向是：

```text
profiles ──extend──> kernel
                      ▲
                      │ composed by
              local composition
               /      |       \
              ▼       ▼        ▼
         product   governance  native/runtime owners
```

Kernel 与 profiles 不读取或推导本地 product、structure 或 runtime facts。Local composition 只保存
“启用什么、入口在哪、如何路由”，不复制被路由对象的事实正文。

## 内容路由规则

按以下顺序为一段内容选择 owner：

| 问题 | 若答案为“是” | Owner |
| --- | --- | --- |
| 它是否定义 approved 或 pending observable behavior？ | 写 requirement/scenario | main spec 或 active delta |
| 它是否声称系统现在如何运行或如何证明？ | 写 current fact/evidence | code、typed contract、test 或 runtime owner |
| 它是否定义精确 path、package、import、gitlink、ID 或 required member？ | 写 project fact | project governance |
| 它是否解释产品为谁解决什么问题或到哪里理解领域语言？ | 写 product context | `product/` |
| 它是否适用于所有采用者且不含产品、host、layout assumptions？ | 写通用 authoring rule | portable kernel |
| 它是否只适用于一种 workflow/host surface？ | 写有 trigger 的附加 rule | reusable profile |
| 它是否选择 profile、绑定 path/budget 或保留本项目扩展？ | 写 composition | local composition |
| 它是否只记录历史上曾发生什么？ | 保留历史 | archive |

一段内容只能有一个可编辑 owner。其他文件可以给一行目的说明和链接，不能复制规则正文。

## Product Front Door 契约

终态的 `openspec/product/README.md` 必须在一个短页面内回答：

1. 产品服务谁、交付什么价值、明确不是什么；
2. canonical product terminology 在哪里；
3. approved / pending behavior 在哪里；
4. current implementation facts 与 evidence 在哪里；
5. 当前项目启用了哪些 authoring profiles，以及 profiles 不授予 runtime authority；
6. 项目 structure 与 verification 的 owning entry 在哪里。

当前 Deep Research README 继续使用本项目已有的 60 行 warning / 80 行 hard budget；这个数字属于
local information-map policy，不传播为 portable requirement。

额外 product 文件只在以下条件全部成立时增加：

- 存在一个不能由 README 清楚路由的独立产品事实辖区；
- 有明确 fact、editorial 与 lifecycle owner；
- 不复制 spec、runtime、structure 或现有 glossary；
- 被 current structure registry 登记并有 link/freshness evidence。

本计划不新增 outcome、workflow、capability-map、evaluation 或 instance 等固定槽位。当前 Deep
Research glossary 仍由 `deep_research_harness/CONTEXT.md` 拥有。

## 本仓目标 Change Guidance 拓扑

```text
openspec/change-guidance/
├── README.md
├── core/
│   ├── principles.md
│   ├── change-admission.md
│   ├── authority-and-projections.md
│   └── context-selection.md
├── profiles/
│   ├── workflow-control/
│   │   ├── README.md
│   │   ├── control-and-recovery.md
│   │   ├── participant-outcomes.md
│   │   ├── human-interaction-integrity.md
│   │   ├── control-placement.md
│   │   └── workflow-outcome-review.md
│   ├── node-agent/
│   │   ├── README.md
│   │   └── node-agent-workflow-integrity.md
│   └── deerflow-downstream/
│       ├── README.md
│       └── deerflow-downstream-boundary.md
└── local/
    ├── context-and-seams.md
    ├── program-focus.md
    └── agent-information-map.md

openspec/governance/
├── change_guidance_kernel.py
└── check_change_guidance.py
```

职责如下：

- root `change-guidance/README.md` 是当前项目的 local router，只列 enabled profiles、canonical
  policy names 与 trigger；不是 exportable prose。
- `core/` 和选中的 `profiles/` 是 V1 portable prose。
- `local/` 保存 Deep Research 的 module map、全局 seam requirement、Program Focus、operation
  integration、entry-document roles 和 budgets。
- `change_guidance_kernel.py` 是无产品、无路径、无 requirement ID 的纯 parser/validator。
- `check_change_guidance.py` 保持当前 CLI，是本地 composition、filesystem checks 和 compatibility
  wrapper；它向 kernel 传入 enabled profiles、local fields、paths 和 budgets。

V1 不新增通用 TOML/YAML binding。目标仓库写自己的 wrapper；只有重复采用证据支持时才引入最小
machine schema。

任何 target path 或 exact member set 变化，都必须在同一个 owning change 中同步
`deep-research-agent-charter`、`project-structure` main specs、`project-structure.toml`、
`check_change_guidance.py`、focused contract tests、config 与 current entry links。

## 当前 Change Guidance 逐文件处置

| 当前文件或内容 | Target owner | 处置 |
| --- | --- | --- |
| `change-guidance/README.md` | local composition | 重写为本项目 router；只路由 core、enabled profiles 和 local extensions |
| `principles.md`：primary owner、facts、evidence、non-authority | core | 移入 `core/principles.md`，改为产品与 host 中性 |
| `principles.md`：participants/recovery | workflow-control | 分配到对应 profile policies |
| `principles.md`：cognition first | node-agent | 进入 node-agent profile |
| `principles.md`：operation/closeout | local | 进入 `local/program-focus.md` |
| `node-edit-map.md` | node-agent | 改为 `profiles/node-agent/README.md` 的 first-read route |
| `policies/change-admission.md`：ordinary Focus、scope、evidence | core | 移入 `core/change-admission.md` |
| `policies/change-admission.md`：Program Focus | local | 移入 `local/program-focus.md` |
| `policies/local-context.md`：primary owner、minimum context、expansion gate | core | 移入 `core/context-selection.md` |
| `policies/local-context.md`：module table、全局 seam classification | local | 移入 `local/context-and-seams.md` |
| `policies/local-context.md`：Program Context | local | 移入 `local/program-focus.md` |
| `policies/authority-and-projections.md` | core | 去掉 Deep Research facts，保留 owner/projection rule |
| `policies/control-and-recovery.md` | workflow-control | 迁入同名 profile policy |
| `policies/participant-outcomes.md` | workflow-control | 迁入同名 profile policy |
| `policies/human-interaction-integrity.md` | workflow-control | 迁入同名 profile policy |
| `policies/control-placement.md` | workflow-control | 迁入同名 profile policy；Git closeout integration 留 local |
| `policies/workflow-outcome-review.md` | workflow-control | 迁入同名 profile policy |
| `policies/node-agent-workflow-integrity.md` | node-agent | 迁入同名 profile policy |
| `policies/agent-information-map.md` | local | 保留 reader-role、paths、budgets 为本地 policy，不进入 export |
| `config.yaml`、`principles.md`、`local-context.md` 与 Harness guide 中的 DeerFlow public-API/upstream clauses | deerflow-downstream | 收敛通用 host boundary 到 profile；本仓路径、gitlink evidence 与启用选择留 local |

迁移完成时，旧 policy paths 被 current links 全量替换并删除；不保留第二份可编辑正文。

## 当前 OpenSpec 入口逐文件处置

| 当前文件 | 分类 | 终态 |
| --- | --- | --- |
| `openspec/README.md` | local navigation | 继续做短 reading map，指向 `product/README.md`、native、guidance 与 governance |
| `openspec/CONTEXT.md` | local governance glossary | 保持本仓 owner；可供采用者参考，不作为跨仓 authority 复制 |
| `openspec/config.yaml` | local authoring composition | 组合 core/profiles/local routes；允许本地名称与命令，不复制 structure inventory |
| `product/deep-research.md` | product front door | 原子迁移为 `product/README.md`；正文保持 navigation/non-authority |
| `openspec/specs/` | native product behavior | 保持原位；不进入 portable export |
| active `openspec/changes/` | native pending behavior | 保持原位；不进入 portable export |
| `openspec/changes/archive/` | immutable history | 不因通用化改写路径或术语 |

## 当前 Governance 逐文件处置

| 当前文件 | V1 分类 | 终态 |
| --- | --- | --- |
| `governance/README.md` | local navigation | 保持项目 checker/registry 路由；不作为 portable source |
| `architecture-policy.md` | local structure lifecycle | 保持，与本项目 manifest/spec/checker 同步 |
| `project-structure.toml` | exact local fact authority | 保持唯一 structure inventory |
| `req-registry.yaml` | local requirement data | 保持；不传播 Deep Research IDs |
| `test-evidence-policy.md` | local policy | 保持，因为语义受本地 `evaluation-hardening` spec 约束 |
| `check_change_guidance.py` | local wrapper | 保持 CLI path/0-1 semantics；调用新 kernel 并执行本地 checks |
| `change_guidance_kernel.py` | portable validator | 新增；纯输入/输出，无 repo traversal、产品 literal 或本地 IDs |
| `check_project_architecture.py` | Deep Research architecture guard | 保持本地，不参数化为通用 checker |
| `check_project_reqs.py` | local extension | V1 不导出；未来抽取需独立第二消费者 |
| `check_project_specs.py` | local extension | V1 不导出；native shape 与本地 terminology 先保持一体 |
| `check_project_req_coverage.py` | local extension | V1 不导出；source/test roots 继续本地拥有 |
| `closeout-evidence/` | local operation extension | V1 不导出；保持 non-authoritative contract |

## Neutrality 与允许字面量

| 区域 | 允许 | 必须排除 |
| --- | --- | --- |
| core | 中性 owner/fact/evidence/change 术语 | 产品名、framework、local paths、commands、requirement IDs |
| workflow-control profile | 通用 workflow/human/recovery 术语 | Deep Research、DeerFlow、本地 paths/IDs |
| node-agent profile | 通用 model/tool/candidate/admission 术语 | Deep Research、DeerFlow、本地 node names/paths/IDs |
| deerflow-downstream profile | DeerFlow、public API、gitlink/downstream boundary | Deep Research、应用 paths、上游内部实现假设 |
| local composition | 本地名称、paths、budgets、commands、IDs 的链接或选择 | 被链接事实的第二份正文 |
| product context | 产品目标、术语导向、owner links | runtime config、structure manifest、完整 requirements |
| specs/code/tests/governance | 其辖区内的本地事实 | 由 portable 文档反向覆盖 |

Known-literal scan 只是第一层 guard；中性 fixture 与真实 adoption 继续证明没有隐藏的 layout 或语义
耦合。

## 两个单一权威约束

### Project structure

source root、test root、package/import policy、gitlink 和 required paths 只由
`project-structure.toml` 及其 owning spec/checker 链决定。Product、config、profile 和 portable
validator 只能链接该 owner，不能重复字段。

### Profile selection

“仓库启用哪些 profiles”由 local composition 决定；“本 change 触发哪些 policies”由 proposal
根据真实 surface 声明并由 wrapper 校验。Product README 可以解释选择，但不成为 machine selector；
profile enablement 也不能推导 runtime 当前存在某种 node 或 tool。
