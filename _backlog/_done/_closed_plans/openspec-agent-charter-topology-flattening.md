# Plan: OpenSpec Charter、Policy 与 Guardrail 一级拓扑

> 类型: 设计 / 迁移 | 更新: 2026-08-11 | 状态: 已吸收至 [`rehome-agent-charter-policy-library`](../../openspec/changes/rehome-agent-charter-policy-library/)，待 apply

## 背景 / 现状

当前目录把 Deep Research Charter、九个本地 policy、一个 cross-cutting policy 和一个
可执行 closeout guardrail 分散在下列不均衡层级：

```text
openspec/governance/agent-charter/policies/  # 9 个本地 policy
openspec/policies/                           # 仅 control-placement
openspec/guardrails/                         # README + closeout command
```

这种布局有两个问题：进入 `openspec/` 时，Charter 不是可见的一等入口；更严重的是，所有
policy 的 canonical home 被人为分成“Charter 内”和“external”两组，而它们实际都由同一个
Charter route、Focus Card 和 checker registry 选择。目录层级因此没有表达真实职责。

`guardrails/` 虽然只有 README 和 `selected_change_closeout.py`，但它已经有清晰的不同职责：
它承载可执行的、确定性且非权威的 boundary/evidence contract。不能为了填满目录而把 policy
正文或 registry/checker 移进去；其现有 SCC output-containment 与 task-parser 契约缺陷继续由
独立的 `selected-change-closeout-evidence` change 修复。

本计划取代
[`openspec-extension-readme-restructure.md`](openspec-extension-readme-restructure.md)
中“Charter README 只读、不重构”以及将 DRC terminology correction 单独排队的局部决定。它不
吸收 SCC 代码修复，也不提前做 governance README 的最终导航收口。

## 已确认的目标布局

```text
openspec/
  agent-charter/
    README.md                         # local routing index
    charter.md                        # durable Deep Research principles

  policies/
    README.md                         # single policy-library index
    agent-information-map.md
    authority-and-projections.md
    change-admission.md
    control-and-recovery.md
    human-interaction-integrity.md
    local-context.md
    node-agent-workflow-integrity.md
    participant-outcomes.md
    workflow-outcome-review.md
    control-placement.md

  guardrails/
    README.md                         # executable command contract
    selected_change_closeout.py       # bounded evidence implementation

  governance/                         # registry, structural authority, checkers
```

没有 `openspec/governance/agent-charter/`、没有 `openspec/agent-charter/policies/`，也不保留
redirect 或 duplicate canonical documents。人从 `openspec/` 一眼能区分：原则与路由、policy
正文、可执行 guardrail、以及治理验证机制。

## 单一职责模型

| 目录 | 读者问题 | 允许放入 | 明确不放入 |
|---|---|---|---|
| `agent-charter/` | 我先按什么原则、再选择哪一个 policy？ | Charter、routing index | policy 正文、runtime contract、checker |
| `policies/` | 这个变化应如何被设计/审查？ | 全部十个 trigger-bearing policy 及其唯一索引 | runtime authority、命令实现、第二个 Charter |
| `guardrails/` | 有什么可执行的确定性 boundary/evidence command？ | command、其最小操作契约、bounded evidence format | policy prose、semantic evaluator、archive wrapper |
| `governance/` | 什么是结构/traceability 的 machine-checkable authority？ | registry、TOML inventory、checker、checker navigation | Charter/policy semantics、runtime decision |

`policies/README.md` 不再称自己为 “External Policies”。它应是一个 policy library index，并在表中
明确两类条目：

- **Charter-routed design/admission policies**：现有九个 local policy；
- **Cross-cutting review policy**：`control-placement`，仍有其 closed postures、独立 review
  record 和 conditional task/guidance integration。

这是分类，不是两套 authority。所有十个 policy 都保持 `authority: guidance only`，并仍由
`agent-charter/README.md` 的 Policy Route 选择。

## 拟议 Change

创建 `rehome-agent-charter-policy-library`。这是一个 `wiring` change，primary causal owner 是
`openspec/agent-charter/` 的 local routing topology，且必须修改规格，不能声明
`skip_specs: true`。

Focus Card 的关键边界：

- **Necessary adjacent contracts:** `deep-research-agent-charter` owns canonical Charter/policy
  routing and DRC terminology; `project-structure` plus
  `openspec/governance/project-structure.toml` own required paths;
  `check_agent_charter.py` and its focused contract test own mechanical route conformance.
- **Evidence seam:** focused charter checker/contract test, then governance and complete
  deterministic verification.
- **Not in scope:** `deerflow/`, Harness runtime behavior, policy trigger/posture semantics,
  SCC command behavior, semantic review automation, native archive authority, and archive
  history.
- **Triggered review policies:** `change-admission`, `agent-information-map`.

### 规格与术语义务

同一 change 修改下列 approved requirements，而不是只做 Markdown move：

1. `DRC-001`：永久 Charter home 从 `openspec/governance/agent-charter/` 改为
   `openspec/agent-charter/`，index 继续是唯一 routing entry。
2. `DRC-005`：Charter 路由 focused policy library，不再暗示 policy 文本必须嵌在 Charter
   tree 内。
3. `DRC-009`：`control-placement` 是 unified library 内的 cross-cutting review policy，
   不再以“external policy”制造第二体系；删除已经失真的
   `add-cross-session-cognitive-guardrails remains deferred` 叙述，准确区分已交付的 selected
   change closeout evidence 与未实现的 semantic evaluator、automatic task writer、archive
   coordinator/blocker。
4. `PRS-009`：exact structural inventory 改为新的 Charter/policy paths，旧树不再是 required
   path。

这不是改变 `control-placement` 的 trigger、四种 posture、review-table shape、task obligation
或 operation guidance；这些保持既有 approved semantics。SCC contract repair 继续以独立 change
修其可执行实现和 `guardrails/README.md`。

## 实施顺序

1. Complete the `rehome-agent-charter-policy-library` change artifacts and modified
   deltas for `deep-research-agent-charter` and `project-structure`; proposal 明确上述
   path/terminology scope 和 SCC exclusion。
2. Use `git mv` to rehome `README.md` and `charter.md` from
   `openspec/governance/agent-charter/` into `openspec/agent-charter/`; move each of the nine
   local policy documents out of `agent-charter/policies/` into `openspec/policies/`.
   `control-placement.md` remains in place. Remove empty old directories and leave no
   compatibility copies.
3. Rebuild both routing surfaces without duplicating prose:
   `agent-charter/README.md` links each policy as `../policies/<name>.md`;
   `policies/README.md` becomes the single categorized library index and links back to the
   Charter route.
4. Update canonical paths in `openspec/config.yaml`, `openspec/CONTEXT.md`,
   `deep_research_harness/AGENTS.md`, `deep_research_harness/README.md`,
   `deep_research_harness/docs/README.md`, `deep_research_harness/CONTEXT.md`,
   `openspec/governance/README.md`, and active planning documentation. Preserve every
   document's existing reader role; this is not a broad documentation rewrite.
5. Update `check_agent_charter.py` and
   `deep_research_harness/tests/contract/test_agent_charter_governance.py` together:
   `CHARTER_ROOT`, `POLICY_REGISTRY`, local/external relative links, fixture trees, and
   expected authoring pointers must use the new topology. The checker keeps validating a
   single policy registry; it does not begin inferring policy applicability or semantic
   quality.
6. Update `project-structure.toml`, its delta/main-spec integration, and any checked
   references to the renamed paths. Search all current non-archive material for the old
   route; archives and `_backlog/_done/` remain historical records and are not rewritten
   solely to modernize a pathname.
7. Keep `guardrails/` unchanged in this change. The next SCC change repairs its command
   containment/parser defects and command README; after both changes, governance README
   navigation cleanup can point to the stable one-level topology.

## 验证

First make the focused contract fixture prove that the old tree alone fails and the new
one-level route passes. Then run:

```bash
python3 openspec/governance/check_agent_charter.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_reqs.py
python3 openspec/governance/check_project_req_coverage.py

cd deep_research_harness
.venv/bin/python -m pytest tests/contract/test_agent_charter_governance.py
make governance
UV_OFFLINE=1 make verify
```

The change must pass `openspec validate rehome-agent-charter-policy-library --strict` and
`git diff --check`. Before archive, inspect a rename-aware scoped diff, assert that active
canonical references contain no `openspec/governance/agent-charter` or
`agent-charter/policies`, and confirm `deerflow/` is untouched.

## 风险 / 取舍

- [The policy library becomes a second Charter] -> Keep only the Charter index responsible
  for selection and durable principles; policy README is an index, not another route table.
- [A move breaks relative links or checker fixtures] -> Maintain one active-reference
  inventory, make legacy-only fixture failure explicit, and run the focused contract test.
- [A legacy tree creates two apparent canonicals] -> Use moves, not copies; structural
  inventory and checker accept only the new paths.
- [Terminology cleanup silently changes policy behavior] -> Preserve triggers, postures,
  record shapes and task/guidance obligations verbatim unless an owning requirement says
  otherwise.
- [Guardrails becomes a generic dumping ground] -> Keep policy prose in `policies/` and
  registry/checkers in `governance/`; only executable, bounded-evidence surfaces enter
  `guardrails/`.
- [Historical evidence is rewritten] -> Exclude archived changes and closed plans from path
  modernization.

## 后续依赖

```text
requirement ownership baseline repair (archived)
                |
                +--> rehome-agent-charter-policy-library
                |      + DRC terminology correction
                |
                +--> selected-change-closeout-evidence repair
                       + guardrails command + focused tests + README

two changes complete
                |
                +--> governance README navigation cleanup
```

The two active changes are independent. The final governance README cleanup waits for both so
it links only stable owners and does not duplicate the policy-library or command contract.
