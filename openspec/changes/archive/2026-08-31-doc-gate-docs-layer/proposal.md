# Proposal: doc-gate-docs-layer

## Change Focus

- **Primary module / causal owner:** `openspec/governance/check_doc_hygiene.py` — PRS-020 拥有「开发 harness 文档层卫生被机械校验」这条决策；本 change 把该 checker 的链接/编码规则范围从 entry-chain 扩到 dev-harness docs 层。
- **Seam classification:** deterministic-guardrail — 语义决策是「docs 层的哪些漂移类被 `exit non-zero` 拒绝」；无认知责任、无产品运行时行为、无 graph/node/state 改动、无新增结构路径。
- **Question:** 已设防的 entry-chain 之外，`deep_research_harness/docs/` 层的相对链接断裂与编码/换行漂移，如何同样在离错误最近处被机器拒绝，而不动摇 PRS-020 已有的边界承诺？
- **Necessary adjacent/external contracts:** `req-registry.yaml`（PRS-020 描述行须与扩围后语义同步，apply 任务承担）；`openspec/governance/README.md`（导航行同步）；`check_doc_hygiene.py` 既有 `--self-test` 契约（扩展而非重建）。
- **Evidence seam:** 扩展后的 `check_doc_hygiene.py --self-test`（docs 层每规则植根违规 → 非零；干净 fixture → 零）+ 真实树「植入 → 红 → 还原」走查 + `check_project_gate.py --phase plan` / `--phase closeout`。
- **Not in scope:** 悬空 prose 片段检测（语义判断，不可机械化，不造假检查器）；ADR index 规则（不变）；line budget（归 `check_change_guidance.py`）；接入 `make verify` 或六 component 聚合（PRS-009 与 application-independence 铁律不变）；`deerflow/`；叙事文档内容（走 `_backlog` todo）。
- **Triggered review policies:** change-admission, authority-and-projections

## Why

PRS-020 的三条规则被（有意）限定在 entry-chain 6 文件内，`deep_research_harness/docs/`
的 8 个顶层文档与 29 个 `adr/` 文件（28 条 ADR + 索引）不在其列。该盲区已被现实击中：
commit `54886b8` 在
`docs/runtime-architecture.md` 删除 OpenSpec 相对链接（PRS-009 de-linking）时留下悬空
prose 片段，doc gate 照绿，直到 2026-08-31 人工评审才被发现并修复。链接/编码类漂移在
docs 层目前仍无机器兜底——这是「不乱发挥」里反馈延迟最高的一档。悬空 prose 片段本身
不可机械化（语义判断），但它的**相邻可机械类**（docs 层坏链接、坏编码、缺尾换行）可以，
且扩围成本极低：全量 37 个 docs markdown 今日已全部通过三条规则（2026-08-31 实测），
扩围是一次零破坏的行为收紧。

## What Changes

- `check_doc_hygiene.py`：新增 docs 层扫描范围常量（`deep_research_harness/docs/*.md`
  与 `deep_research_harness/docs/adr/*.md`，markdown only），把**既有**的相对链接规则与
  UTF-8/尾换行规则应用到该范围；ADR index 规则保持原样（仍只管 `docs/adr` 索引↔目录）。
  附带一条**范围完整性守卫**：docs 树下实际存在的 markdown 与已登记范围求差，多出的
  未登记文档即退出非零——防「新增文件忘登记」的静默欠覆盖。
- `--self-test` 负例控制扩展：docs 层范围内每条适用规则一个植根违规 fixture（坏链接、
  非 UTF-8、缺尾换行），干净 fixture 保持退出 0。
- `req-registry.yaml`：PRS-020 描述行措辞同步（「entry-chain 相对链接」→「entry-chain
  与 docs 层的相对链接/编码漂移」）——apply 任务正式改，planning 不动 registry。
- `openspec/governance/README.md`：`check_doc_hygiene.py` 导航行描述同步。

## Capabilities

### New Capabilities

（无 —— 扩围落在已有 `project-structure` capability 的既有 requirement 上）

### Modified Capabilities

- `project-structure`: **MODIFIED PRS-020** — 链接/编码/换行三条卫生规则的拒绝范围从
  entry-chain 文档扩展到 docs 层文档（`deep_research_harness/docs/**/*.md`）；checker
  登记路径、owner、`--self-test` 义务、非聚合非 `make verify` 边界全部不变。

## Impact

- 代码：`openspec/governance/check_doc_hygiene.py`（扩范围常量 + 范围完整性守卫 + self-test
  fixtures；无新文件）。
- 结构：无新增结构路径（checker 已登记于 `project-structure.toml`，owner 仍 PRS-020）。
- 登记簿：`openspec/governance/req-registry.yaml`（PRS-020 描述行措辞，apply 时）。
- 文档：`openspec/governance/README.md`（导航行描述）。
- 不动：`deep_research_harness/` 运行时代码与测试、`make verify`、`check_project_gate.py`
  六聚合、`architecture-policy.md`、`deerflow/` gitlink。
- 验证门：`check_doc_hygiene.py --self-test`；真实树负例走查（植入 → 红 → 还原）；
  `python3 openspec/governance/check_project_gate.py --phase plan --change 2026-08-31-doc-gate-docs-layer`；
  closeout 后 `--phase closeout`；`cd deep_research_harness && UV_OFFLINE=1 make verify`；
  `openspec validate 2026-08-31-doc-gate-docs-layer --strict` + `git diff HEAD --check`（退出码均直测）。
