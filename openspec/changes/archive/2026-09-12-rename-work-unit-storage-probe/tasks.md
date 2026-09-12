# Tasks: rename-work-unit-storage-probe

## 0. 背景发现（先于实施记录）

- [x] 0.1 `deep_research_harness/openspec/config.yaml` 是 `openspec init` 默认模板残留，
      全仓零引用，会 shadow 仓库根 openspec 配置：已删除（同一工作树内的独立清理）。
- [x] 0.2 治理冲突记录：`architecture-policy.md` 规定「语义 requirement 变化时才需要
      owning delta」，但 `check_project_specs.py --change` 曾对无 delta 的 active change
      fail closed。本 change 是 manifest-only 结构同步（无语义变化），因此不伪造 spec
      delta。**已由 `2026-09-12-honor-skip-specs-in-plan-gate` 修复**：checker 现认可
      原生 `skip_specs: true`，本 change `--phase plan` 已 exit 0。
- [x] 0.3 既有漂移记录（与本 change 无关）：`--phase closeout` 曾因 `LDD-005`、`LDO-008`
      两个 uncovered requirement 退出 1。**已由
      `2026-09-12-repair-debug-requirement-evidence` 修复**，closeout 现 exit 0；
      `deep_research_harness/AGENTS.md` 122 行 warning 为既有非阻断提示。

## 1. Manifest 同步（Synchronized Changes 第 2 条）

- [x] 1.1 `git mv .../runtime/work_unit_storage.py .../runtime/work_unit_storage_probe.py`
- [x] 1.2 `openspec/governance/required-paths.toml` PRS-001 路径同步为
      `.../runtime/work_unit_storage_probe.py`（位置与其余路径不变）
- [x] 1.3 `deep_research_harness/AGENTS.md` 生成 locator 无 diff——locator 不枚举 runtime
      单文件；`check_project_architecture.py` 通过

## 2. 重命名与引用同步（Synchronized Changes 第 1/4 条）

- [x] 2.1 `git mv .../tests/unit/test_work_unit_storage.py .../test_work_unit_storage_probe.py`
- [x] 2.2 更新 src 内 import：
      `runtime/{bootstrap_bundle,request_bundle,work_unit_store,diagnostics}.py`
- [x] 2.3 更新 scripts 内 import：`scripts/_demo_core.py`
- [x] 2.4 更新 tests 内 14 处 import（unit/blocking_io/integration/graph/eval）
- [x] 2.5 编译门：`.venv/bin/python -c "import ...runtime.work_unit_storage_probe"` 通过；
      全仓（排除历史 archive 与 `_backlog/_done/`）无旧 dotted 路径残留

## 3. 证据映射同步（Synchronized Changes 第 4 条）

- [x] 3.1 `tests/assets/evidence.py` 的 `live-discovery-workspace-cleanup` selector 同步
- [x] 3.2 `docs/regression-descent.md` `LIVE-20260717-01` 行 selector 同步

## 4. 验证与收口

- [x] 4.1 干净工作树 `python3 openspec/governance/check_project_architecture.py` exit 0
- [x] 4.2 `UV_OFFLINE=1 make verify` exit 0（lint + test-assets + 2694 fast + 325 integration
      + 35 workflow）；`scripts/checks/check_test_assets.py` 解析改名后 selector 通过
- [x] 4.3 `openspec validate 2026-09-12-rename-work-unit-storage-probe --strict` 通过
- [x] 4.4 `git diff HEAD --check` 无输出
- [ ] 4.5 归档本 change（`--phase closeout` 与 `--phase plan` 均已 exit 0，可按
      openspec-archive-change 流程执行）
