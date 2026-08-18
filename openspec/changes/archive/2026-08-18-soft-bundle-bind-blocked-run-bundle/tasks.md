# Tasks: Soft Bundle Binds a Blocked Run's Bundle

## 1. 治理登记

- [x] 1.1 更新 `openspec/governance/req-registry.yaml` 的 `SBC-002`（`soft-bundle-session-cli` — run 解析到合法 bundle id 时无论 operator 入口退出码如何都记录并绑定该 bundle，同时保留非零退出状态与原始失败输出）；不新增 SBC-006（本 change 是对 SBC-002 的行为变更，不是新 requirement）。
- [x] 1.2 跑 `python3 openspec/governance/check_project_reqs.py` 与 `check_project_architecture.py`，确保治理检查通过；如 req-registry 或 project-structure 需要更新路径/条目，按 `architecture-policy.md` 协议补上。

## 2. `cmd_run` 绑定顺序重构（BUG-042）

- [x] 2.1 `scripts/soft_bundle.py`：mode 003 分支 — 移除「非零退出先 return」的早期 return；解析到合法 `bundle_id` 且 `_find_bundle_dir` 解析到真实 bundle 目录后，先 `_record_bundle(root, manifest, bundle_dir)` 并打印 `bound_bundle_id`/`bundle_local_path`，再运行验证（blocked → FAIL），最终返回 `proc.returncode or (0 if ok else 1)`；run 非零退出但 bundle 可解析时，**先把原始 run 输出打到 stderr** 再绑定（保留失败原因）。
- [x] 2.2 `scripts/soft_bundle.py`：mode 002 分支 — 同样移除 OR-gate 提前 return（`proc.returncode != 0 or bundle_id is None or bundle_dir is None or not bundle_dir.exists()`），改为只在「无合法 bundle id / 无 journal 派生 bundle 目录 / 目录不存在」时提前返回并打印原始输出；解析/派生到真实 bundle 目录后即使 run 非零退出也先打印原始输出、再 `_record_bundle`、再返回对应退出码。
- [x] 2.3 确认 mode 001 分支**不改**：其提前 return 是 AND-gate（`proc.returncode != 0 and bundle_id is None`，且该分支经 fallback 后 bundle_id 已保证非 None，实际为死代码），已解析 bundle 时无论退出码都会流入 `_record_bundle`；在提交里注明该分支保持原样。
- [x] 2.4 共享尾部（所有 mode 汇合后的 `return 0 if ok else 1`）改为 `return run_exit or (0 if ok else 1)`：mode 001 保持 `run_exit = None`（行为与今天逐字节一致），mode 002/003 在分支内设 `run_exit = proc.returncode`（保留真实失败退出码而非折叠成 1）。

## 3. 契约测试（red-before-green）

- [x] 3.1 `tests/contract/test_soft_bundle_cli.py`：新增 mode 003 非零退出 fixture — `_run_make` 返回 `returncode=1` 且 stderr/stdout 含 `Run Bundle: b_xxx`、bundle 目录存在；断言 `cmd_run` 仍写入 manifest `current_bundle_id` 与 `bundles/<id>.json`、打印 `bound_bundle_id`、**stderr 仍含原始失败输出**，且返回码非 0（等于 `proc.returncode`）。
- [x] 3.2 新增 mode 002 非零退出 fixture：journal 派生到真实 bundle 目录 + 非零退出 → 绑定并保留非零返回码（若 fixture 桩能力允许 mode 002 的非零路径）。
- [x] 3.3 新增「无可解析 bundle id + 非零退出」回归（mode 003）：不绑定、`current_bundle_id` 不变、原始输出仍打到 stderr。
- [x] 3.4 跑 `cd deep_research_harness && .venv/bin/python -m pytest tests/contract/test_soft_bundle_cli.py`，红变绿且既有用例不回归。

## 4. 文档与收尾

- [x] 4.1 `_backlog/bugs/`：BUG-042 标记修复并 `git mv` 到 `_backlog/_done/_fixed_bugs/`；更新 `_fixed_bugs/README.md` 表格 + Next available bug ID、`_backlog/bugs/README.md` 活跃列表、`_backlog/_done/README.md` 计数。
- [x] 4.2 全量验证：`cd deep_research_harness && UV_OFFLINE=1 make verify`、`openspec validate soft-bundle-bind-blocked-run-bundle --strict`、`git diff HEAD --check` 均通过；`git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status --porcelain=v1 --untracked-files=all` 与 `git diff --submodule=short` 记录为归档证据；`deerflow/` gitlink 不修改。
- [ ] 4.3 （可选，需真机）跑一次 blocked 003 run 后在同一个 root 上 `soft-bundle inspect/status/verify/phases` 可用，并把证据写入 BUG-042 卡。
