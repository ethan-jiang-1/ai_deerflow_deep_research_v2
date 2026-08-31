# Tasks: doc-gate-docs-layer

## 1. 范围扩张（先契约后实现）

- [x] 1.1 `check_doc_hygiene.py`：新增 `DOC_LAYER_DOCS` 范围构造（`deep_research_harness/docs/*.md` 顶层 + `docs/adr/*.md`，markdown only），docstring 同步声明「docs 层文档适用链接/编码/换行规则，不适用 ADR index 规则」；`@impl PRS-020` 注解保持。
- [x] 1.2 复用既有检查函数把相对链接与 UTF-8/尾换行两规则应用到 `DOC_LAYER_DOCS`（不复制实现）；ADR index 规则范围不变。
- [x] 1.3 范围完整性守卫：glob `docs/**/*.md` 全集与 `DOC_LAYER_DOCS` 求差，存在未登记 markdown 即退出非零并点名文件（防新增文件忘登记的静默欠覆盖）。
- [x] 1.4 跑 `python3 openspec/governance/check_doc_hygiene.py`：真实树当前必须退出 0（2026-08-31 实测 37 个 docs markdown 全绿，扩围不得引入新红）。

## 2. 负例控制扩展

- [x] 2.1 `--self-test`：在 docs 层范围植入违规 fixture——坏相对链接、非 UTF-8、缺尾换行、未登记 markdown——各断言退出非零；干净 fixture 断言 0；原 entry-chain fixtures 原样保留全绿。
- [x] 2.2 真实树负例走查：临时给某个 `docs/*.md` 植入坏链接 → checker 非零（红，报文件名 + 违反规则）→ 还原 → 复绿；退出码直测。

## 3. 登记簿与导航同步

- [x] 3.1 `req-registry.yaml`：PRS-020 描述行措辞同步为覆盖 entry-chain 与 docs 层两范围（仅描述行，ID/owner 不变；本 change 无新增 requirement，无 reservation）。
- [x] 3.2 `openspec/governance/README.md`：`check_doc_hygiene.py` 导航行描述补「含 docs 层」。
- [x] 3.3 确认 `project-structure.toml` 零改动（checker 已登记、owner 仍 PRS-020）；`git diff --stat` 里不出现该文件。

## 4. 收口

- [x] 4.1 `python3 openspec/governance/check_project_gate.py --phase plan --change 2026-08-31-doc-gate-docs-layer` 通过（退出码直测）。
- [x] 4.2 `python3 openspec/governance/check_project_gate.py --phase closeout` 通过（退出码直测）。
- [x] 4.3 `cd deep_research_harness && UV_OFFLINE=1 make verify` 通过（证明 Harness gate 未反向依赖 OpenSpec，application-independence 保持）。
- [x] 4.4 `openspec validate 2026-08-31-doc-gate-docs-layer --strict` 与 `git diff HEAD --check` 通过（退出码直测）。
- [x] 4.5 记录 `git status --porcelain=v1 --untracked-files=all` 与 `git submodule status -- deerflow`（`deerflow/` 零改动，指针未变 `66b9e7f2`）。
