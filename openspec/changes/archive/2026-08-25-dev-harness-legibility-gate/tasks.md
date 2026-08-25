# Tasks: dev-harness-legibility-gate

## 1. 规则与负例（先定契约）

- [x] 1.1 写 `openspec/governance/check_doc_hygiene.py` 骨架：docstring 声明三条规则（ADR 索引↔目录、入口链相对链接、UTF-8/结尾换行）与「自包含、非 gate 组件、非 make verify 目标」边界，并带 `@impl PRS-020` 注解（供 `check_project_req_coverage.py` 映射「治理需求→执行脚本证据」）；定义规则常量（ADR 目录/索引、ENTRY_DOCS 清单、忽略 http/https/#锚点）。
- [x] 1.2 实现 `--self-test` 负例控制：干净 fixture 断言退出 0；对每条规则植入一个违规 fixture 断言退出非零。
- [x] 1.3 跑 `python3 openspec/governance/check_doc_hygiene.py --self-test` 确认（此阶段规则未实现时应红，见 2.2 转绿）。

## 2. 实现 checker（绿）

- [x] 2.1 实现三条规则的检测与 `exit non-zero` 报告（失败对象 + 违反规则 + 修正入口）。
- [x] 2.2 跑 `--self-test` 全绿（干净 0，每植入违规非零）。
- [x] 2.3 对真实树做负例走查：临时植入孤儿 ADR（`| 9999 |`）→ checker 非零（红，报 "ADR index lists missing file: 9999"）→ 还原 → 非零消失（绿）；`--self-test` 另覆盖断链与去尾换行两规则。

## 3. 结构登记 + G4 + 导航

- [x] 3.1 在 `project-structure.toml` 登记 `openspec/governance/check_doc_hygiene.py`（`[[required_paths]]`：`kind = "file"`，`owner = "PRS-020"`），并把 `PRS-020` 追加进顶层 `requirement_ids` owner 白名单（apply 中发现的两处登记，缺一即 `owner.unknown`）。
- [x] 3.2 `architecture-policy.md`：把「generated locator block」三处标注为 future plan / not yet implemented —— Authority 表第 15 行、Synchronized Changes 第 3 步（"regenerate the bounded locator"）、以及文末 generated block 段（"bounded by the markers declared in the registry"）；不改 registry/checker，仅消除「prose 声称机器事实」的漂移（G4 诚实化）。
- [x] 3.3 `openspec/governance/README.md` 增一行导航（`check_doc_hygiene.py` → 何时读）+ 命令说明（standalone，非六 component 聚合）。

## 4. 收口

- [x] 4.1 在 `req-registry.yaml` 登记 `PRS-020: project-structure — ...`（apply 正式登记；planning 只 reserve）。
- [x] 4.2 `python3 openspec/governance/check_project_gate.py --phase plan --change dev-harness-legibility-gate` 通过（退出码直测）。
- [x] 4.3 `python3 openspec/governance/check_project_gate.py --phase closeout` 通过（退出码直测）。
- [x] 4.4 `cd deep_research_harness && UV_OFFLINE=1 make verify` 通过（full-access 跑通，exit=0；证明 Harness gate 未反向依赖 OpenSpec）。
- [x] 4.5 `openspec validate dev-harness-legibility-gate --strict` 与 `git diff HEAD --check` 通过（退出码直测）。
- [x] 4.6 记录 `git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status --porcelain=v1 --untracked-files=all`，并 review `git diff --submodule=short`（gitlink 补充证据；`deerflow/` 零改动，指针未变 `66b9e7f2`）。
