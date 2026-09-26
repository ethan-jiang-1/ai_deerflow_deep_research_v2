# Proposal

## Why

v2.1.0 submodule 升级（`da5721d`）落了代码与 contract-test pin，但治理账面没收口：
`openspec/governance/project-structure.toml` 的 `[upstream_gitlink]` 仍声明旧 commit
`66b9e7f2`，`check_project_gate.py --phase closeout` 因此唯一红灯
（`gitlink.index_commit`），后续任何 archive 都会被卡；同一升级也未留 change 记录，
构成"gitlink bump 不走 change"的未留痕先例。另有一处低危 spec 措辞漂移
（CNI-001 标题条款与 11 个 workflow.md 实际 H1 不符）一并收口。

## What Changes

- 将 `[upstream_gitlink].commit` 从 `66b9e7f2…` 更新为 `ceebf97fc31afbbfe2aadf7c8d82b03c3742d5d7`
  （ethan 分支 tip，= 上游 v2.1.0；submodule 本体已在此 commit，本 change 只对齐治理声明，不动 submodule）。
- 根 `README.md` 框架运行时基座注记（:64）同步为新 commit，并指向 contract test 的
  `CURRENT_DEERFLOW_PIN` 作为镜像锚点。
- 本 proposal 即 v2.1.0 升级（`da5721d`/`4f92b61`/`233e941`/`d1912a0`）的**追溯批准记录**：
  升级当时未走 change，此处补录决策与证据。
- MODIFIED `cognitive-node-interface` CNI-001：标题条款措辞对齐现状
  （卡片 H1 实为 `# <node> — <一句话职责>`），其余条款与场景原样保留。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `cognitive-node-interface`: CNI-001 的自标题条款措辞由固定字面
  `Node — Product Responsibility` 改为"节点名 + 一行产品职责"的规范形式；
  需求其余条款、场景与其它四个 requirement 不变。

## Impact

- `openspec/governance/project-structure.toml`（声明值）
- `openspec/specs/cognitive-node-interface/spec.md`（经 delta 归档后）
- 根 `README.md`（一行注记）
- 验收面：`check_project_gate.py --phase closeout` 转绿、`check_project_architecture.py`
  转绿、`openspec validate --specs --strict` 保持 57/57、
  `openspec/tests/governance/test_split_manifest.py`（fixture 已同步）保持通过。
- 无运行时行为变化；`deerflow/` submodule 本体不动。

## Change Focus

- **Primary module / causal owner:** openspec 治理账面本身——`project-structure.toml` 的 `[upstream_gitlink]` 声明值与 `cognitive-node-interface` CNI-001 标题条款；两个账面事实的语义决定者都是治理/spec 文本，不是任何运行时模块。
- **Seam classification:** wiring —— 纯治理账面与 spec 措辞对齐，无运行时行为、无模型面、无路由或准入变化（wiring：不改任何认知、准入或生命周期语义）。
- **Question:** 治理声明的 upstream 锁值是否等于真实 gitlink（closeout 门可否转绿）？CNI-001 的标题规范形式以哪一方为准？
- **Necessary adjacent/external contracts:** `project-structure` spec（PRS-018 场景定义"声明 = index = nested HEAD = clean"匹配语义，本 change 只改声明值不改语义）；`deep_research_harness/tests/contract/test_deerflow_public_api.py` 的 `CURRENT_DEERFLOW_PIN`（代码侧镜像锚点，已在 da5721d 更新）；`cognitive-node-interface` spec（CNI-001 现行条文，delta 对照基线）。
- **Evidence seam:** `openspec/governance/check_project_gate.py --phase closeout`、`check_project_architecture.py`、`openspec validate --specs --strict`、`openspec/tests/governance/` 三门测试——全部零 API、确定性。
- **Not in scope:** submodule 本体任何变更；v2.1.0 适配代码（已完成并另行提交）；`_backlog/plans/harness-tech-debt-cleanup.md` 的 P1-P3 文档与守护项。
- **Triggered review policies:** none: 纯治理账面对齐与 spec 措辞修正，无认知面、无 workflow outcome、无 node-agent 参与面。

边界声明：普通下游工作不修改也不 source-browse `deerflow/` gitlink；本 change
显式拥有且批准的只是**治理声明值与 README 注记的对齐**——submodule 本体保持
`ceebf97f` 不动，这正是本 change 要记录的边界事实。
