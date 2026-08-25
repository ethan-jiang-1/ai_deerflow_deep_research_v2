# Proposal: dev-harness-legibility-gate

## Change Focus

- **Primary module / causal owner:** `openspec/governance/` — 开发 harness 文档层的卫生门禁；新增自包含的 `check_doc_hygiene.py`（确定性 checker），PRS-020 拥有「文档层卫生被机械校验」这条结构/行为决策。
- **Seam classification:** deterministic-guardrail — 语义决策是「什么算文档层卫生违规、违规如何被 `exit non-zero` 拒绝」；无认知责任、无产品运行时行为、无 graph/node/state 改动。
- **Question:** 开发 harness 的文档层（根/子树 AGENTS.md、README、`docs/adr` 索引）在 `check_change_guidance.py` 已覆盖的行数预算与 CLAUDE 导入之外，如何把「ADR 索引漂移 / 入口链相对链接断裂 / 编码换行漂移」也变成机器可拒绝？
- **Necessary adjacent/external contracts:** `architecture-policy.md`（其第 15、75–80 行声称的 generated locator block 与 registry/checker/AGENTS.md 现实不符；本 change 把该段标注为 future plan，兑现 Synchronized Changes 对新增结构路径的诚实义务）；`project-structure.toml`（登记新 checker）。
- **Evidence seam:** `check_doc_hygiene.py --self-test` 的负例控制（干净 fixture → 退出 0；每规则植入违规 → 退出非零），外加对真实树的「植入 → 红 → 还原」走查。
- **Not in scope:** 产品运行时行为；`make verify`（保持 application-independent）；`check_project_gate.py` 的六 component 聚合（PRS-009 已规定 closeout SHALL NOT 追加一致性 checker）；`deerflow/` gitlink；ADR 索引正文本身（走 `_backlog` todo，本 change 只校验它不漂）；运行时 inspect 工具 / invariant / 插件图。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

开发 harness 的文档（ADR 索引、入口链相对链接、UTF-8/结尾换行）目前只有 prose 约定，漂移要等 review 才被发现——这是「不乱发挥」里杠杆最高、本仓最缺的一档。`check_change_guidance.py` 已机械强制行数预算与 CLAUDE 导入，但 ADR 索引一致性、相对链接解析、编码/换行仍无机器兜底。

## What Changes

- 新增 `openspec/governance/check_doc_hygiene.py`（自包含、标准库、repo 根运行；含 `--self-test` 负例控制）。
- 新增 `project-structure` requirement **PRS-020**（delta spec 声明），apply 时正式登记 `req-registry.yaml`。
- `project-structure.toml` 登记新 checker（owner PRS-020）。
- `architecture-policy.md`：把「generated locator block」段标注为 future plan（G4 诚实化，兑现 Synchronized Changes 义务）。
- `openspec/governance/README.md` 增一行导航。

## Capabilities

### New Capabilities

（无 —— 新 requirement 归入已有 `project-structure` capability）

### Modified Capabilities

- `project-structure`: 新增 PRS-020 —— 开发 harness 文档层卫生 checker 占据 canonical governance 路径并被机械强制；它不得并入六 component 聚合，也不得接入 `make verify`。

## Impact

- 代码：`openspec/governance/check_doc_hygiene.py`（新，标准库零依赖）。
- 结构：`openspec/governance/project-structure.toml`（+1 行）、`openspec/governance/req-registry.yaml`（apply 时 +PRS-020）。
- 文档：`openspec/governance/architecture-policy.md`（G4 段）、`openspec/governance/README.md`（导航）。
- 不动：`deep_research_harness/` 运行时代码与测试、`make verify`、`check_project_gate.py` 六聚合、`deerflow/`。
- 验证门：`check_doc_hygiene.py --self-test`；`python3 openspec/governance/check_project_gate.py --phase plan --change dev-harness-legibility-gate`；closeout 后 `--phase closeout`；`cd deep_research_harness && UV_OFFLINE=1 make verify`；`openspec validate dev-harness-legibility-gate --strict` + `git diff HEAD --check`（退出码均直测）。
