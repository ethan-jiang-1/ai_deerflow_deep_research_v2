# Tasks: demo-workspace-cleanup

## 1. 核心纯函数（可参数化，先契约）

- [x] 1.1 `scripts/soft_bundle.py`：新增 `_collect_workspace(runs_root)` 与 `_clean_workspace(runs_root, *, confirm, logs)` 纯函数核心（root 注入，沿 `_archive_run_subtree(runs_root, name)` 可测先例）；terminal 判定 = run-summary.json `status ∈ {completed, stopped, cancelled, blocked}`，不可读 = 非 terminal（fail-closed）。
- [x] 1.2 `report` 语义实现：清单（bundle id / status / 大小 / resumable 标注）+ logs 与 archive 子树摘要 + operator-view（非 authority）声明。
- [x] 1.3 `clean` 语义实现：默认 dry-run 零删除并列 would-delete / would-keep；`CONFIRM=1` 时仅删 terminal bundle 目录**及其** soft-bundle 记录（成对删除，soft-bundles root 保留）；非 terminal 目录零触碰；`--logs` 分离清理（同受 CONFIRM 门）；删除后打印基线失效警示。

## 2. CLI 与公共入口

- [x] 2.1 `soft_bundle.py` argparse 挂 `workspace-report` / `workspace-clean` 子命令（workspace-clean 带 `--logs` 可选旗标；既有 `clean` 动词零改动）。
- [x] 2.2 `Makefile` 新增 `demo-workspace-report` 与 `demo-clean` targets：entry-preflight、`PYTHONPATH=src_fake` 与 UV_NO_CACHE 约定同既有 demo targets、`DEMO_ARGS` 透传。
- [x] 2.3 `.PHONY` 行同步。

## 3. 契约测试

- [x] 3.1 `tests/contract/test_soft_bundle_cli.py` 扩展（tmp-root fixtures，零网络）：report 清单与 resumable 标注；dry-run 零删除并列两侧；CONFIRM=1 只删 terminal 且记录成对删除；非 terminal 目录逐字节不动；不可读状态 = 保留并标注 unknown；logs 分离（无 logs 旗标不删 log；有旗标无 CONFIRM 不删）；基线警示存在。

## 4. 文档同步

- [x] 4.1 `docs/local-operations.md`："no observation-backed list, open, discovery, cleanup, or lifecycle-control command" 现状段改写——盘点/清理缺口由本命令关闭，attach/resume 等生命周期动作仍走既有入口。
- [x] 4.2 `COMMANDS.md` §2/§3：`demo-workspace-report` / `demo-clean` 入表，§3「没有清理命令」段改写（保留「bundle 历史是证据」纪律与基线快照警示）。

## 5. 登记与收口

- [x] 5.1 `req-registry.yaml` 登记 `DPL-014: demo-pipeline — ...`（apply 正式登记）；确认 `project-structure.toml` 零改动（scripts 目录已有登记、无新文件路径）。
- [x] 5.2 真实树走查：`make demo-workspace-report`（67+ 真实 bundle 全量清单）+ `make demo-clean`（dry-run，退出码直测）。
- [x] 5.3 `python3 openspec/governance/check_project_gate.py --phase plan --change 2026-08-31-demo-workspace-cleanup` 通过（退出码直测）。
- [x] 5.4 `python3 openspec/governance/check_project_gate.py --phase closeout` 通过（退出码直测）。
- [x] 5.5 `cd deep_research_harness && UV_OFFLINE=1 make verify` 通过（退出码直测，full-access 供 uv 缓存读）。
- [x] 5.6 `openspec validate 2026-08-31-demo-workspace-cleanup --strict` 与 `git diff HEAD --check` 通过（退出码直测）。
- [x] 5.7 记录 `git status --porcelain=v1 --untracked-files=all` 与 `git submodule status -- deerflow`（`deerflow/` 零改动）。
