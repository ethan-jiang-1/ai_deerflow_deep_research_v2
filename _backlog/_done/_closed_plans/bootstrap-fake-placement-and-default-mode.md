# Plan: Bootstrap Fake Placement And Default Mode

> 类型: 架构分析 | 状态: Closed — superseded by `isolate-fixture-implementations` | 归档: 2026-08-01 | 更新: 2026-07-31

## Closure

This plan's rebased conclusion has been overtaken by the completed OpenSpec change
`isolate-fixture-implementations` (archived 2026-08-01). Deterministic fixtures now
live in the distinct `src_fake/deerflow_deep_research_fixtures` package, production
node packages expose real factories only, and the reflected public lifecycle is
all-real by construction. The historical analysis remains useful only for the
decision it replaced; it is no longer a current baseline or reopen trigger.

## Rebase 结论

保留 `deerflow_research/src/deerflow_deep_research/graph/nodes/bootstrap/fake.py` 与 real
bootstrap factory（`node.py`）同包，保留 package root `NODE_SPEC` 上显式的 `real_factory` /
`fake_factory` 选择，也保留 `ResearchGraphRecipe.create()`、`build_research_graph()` 和 reflected
`deep_research` control surface 的当前 all-fake 默认。

这不再是一个待调查的 bootstrap 布局问题。当前没有 OpenSpec change、文件移动、默认模式修改或
额外 registry metadata 需要实施。

## 原问题怎样被当前工程解决

| 原问题 | 当前 authority / evidence | 结论 |
| --- | --- | --- |
| `fake.py` 是测试 mock、开发 skeleton，还是普通运行实现？ | 根 `AGENTS.md`、`deerflow_research/README.md` 和 lifecycle specs 明确把 `implementation_mode=full_fake` 定义为零凭据、无研究输出的受支持 lifecycle skeleton | 它是显式 fixture adapter，不是假装成真实研究的 fallback |
| fake 与 real 是否应该同包？ | `project-structure` 主规范要求每个 top-level node package colocate deterministic fake，并只从 package root 暴露一个 `NODE_SPEC` | 同包是当前 canonical node interface，不是 bootstrap 特例 |
| 默认 all-fake 是否是意外？ | `ResearchGraphRecipe.create()` 与 `build_research_graph()` 明确默认所有 logical nodes 为 `fake`；主规范、README 和测试都锁定该行为 | 默认是已接受的 product/development contract，不是未决实现细节 |
| fake 会不会被 real 路径静默选中？ | `resolve_implementations()` 只按完整显式 map 选择 adapter，拒绝 missing、unknown、invalid 和 unavailable real selection | 没有已复现的错误选择或 silent fallback |
| 人或 Coding Agent 能否分辨 bootstrap 的职责？ | package-local `workflow.md` 明确标为 deterministic control、intentional controller exclusion，并直接区分 real bundle binding 与 zero-I/O fake | 原可读性症状已由统一 reader interface 吸收 |
| 所有 11 个 real factories 现已可用，是否自动废除 full-fake？ | `deerflow_research/README.md` 将 all-real demo 与 reflected all-fake control surface 分开；mode 只描述 recipe composition，不表示质量或默认推荐 | adapter 可用性不等于默认产品策略改变 |

## 当前 Bootstrap 包目录基线

本计划所说的“folder”是当前唯一的 bootstrap node package：
`deerflow_research/src/deerflow_deep_research/graph/nodes/bootstrap/`。它不是测试 fixture
目录，也不是可独立注册的第二个 module root。

| 文件 | 当前职责 |
| --- | --- |
| `__init__.py` | 唯一公开 surface：导出 `NODE_SPEC`，并将 real/fake factory、typed contracts 与 bootstrap capability 连接起来。 |
| `contracts.py` | package-private request/result contract source。 |
| `fake.py` | 零 I/O 的确定性 fixture adapter；只生成 typed fixture route。 |
| `node.py` | real bootstrap factory；建立并验证 bootstrap bundle，随后给出 typed lifecycle route。 |
| `workflow.md` | reader interface，不是运行时配置或第二份行为 authority。 |

因此 folder 的边界已经与所有 top-level node package 对齐：registry 只读取 package root 的
`NODE_SPEC`，而 builder 只经 implementation map 取得选定 factory。单独移动 `fake.py`、把
`workflow.md` 当作 runtime 输入，或从外部直接 import private factory，都会破坏当前 package contract。

## Module / Seam 判断

`NODE_SPEC` 是 logical node 的小 interface；real 和 fake 是位于同一 seam 的两个 adapter。
implementation map 集中拥有选择，graph/runtime 调用者无需理解两个 implementation 的内部细节。
这满足真实 seam 的条件，而不是为测试制造的假设性抽象。

删除这个 seam 会把 fake/real 选择、capability injection 和 mixed-recipe 兼容重新扩散到 builder、
runtime 和测试调用者。单独把 bootstrap fake 移去测试目录则会破坏所有 node 共用的 package grammar，
却没有减少调用者必须学习的 interface。

## Rebased Scope Card

- **Primary module / causal owner:** `deerflow_research/src/deerflow_deep_research/graph/implementation_map.py` 所拥有的 recipe implementation selection。
- **Question:** 当前没有待改变行为；只有实际 selection failure 或新的产品默认要求才能重新打开。
- **Necessary adjacent/external contracts:** `project-structure` 仅在全体 node package grammar 需要改变时准入；`runtime/research.py` 仅在默认 recipe 的产品行为需要改变时准入。
- **Evidence seam:** `deerflow_research/tests/contract/test_research_node_packages.py`、`deerflow_research/tests/integration/test_bootstrap_lifecycle.py`、`deerflow_research/tests/unit/test_research_runtime_capabilities.py`，以及 default `full_fake` lifecycle tests。
- **Not in scope:** 单独移动 bootstrap fake、删除 full-fake、把 fake 改成隐式 fallback、改变 topology、扩大 fake authority，或修改 `backend/` / `frontend/`。

## 重新打开时必须拆开的三个 Scope

1. **实际选择 defect**：先提供 fake 被错误选择、real 被错误拒绝或 mode 被错误标记的红色复现；
   owner 是 implementation selection，不是目录布局。
2. **产品默认改变**：若 reflected tool 或普通 runtime 应默认 all-real，另开 lifecycle/runtime change，
   明确凭据、provider/tool failure、真实输出、non-interactive 和 transport posture；不能借 bootstrap
   文件位置暗改默认。
3. **统一 node package grammar 改变**：只有所有 logical nodes 的 real/fake seam 都需要重构时，
   才由 `project-structure` change 统一处理；不做 bootstrap-only 例外。

## 非目标

- 不把 package-local fake 认定为生产污染。
- 不为目录整洁增加 metadata、wrapper、alias 或第二 registry。
- 不用“现在有 all-real recipe”推导 reflected public control surface 必须切换默认。
- 不改变 bootstrap 的 bundle-binding、零模型调用、fail-closed 或 typed-route authority。

## 当前处置

本计划经过 rebase 后没有活跃 implementation task。当前设计已有主规范、代码、reader interface
和确定性测试共同拥有；未来只有上述三个独立 trigger 之一出现时，才建立新的 Scope Card。
