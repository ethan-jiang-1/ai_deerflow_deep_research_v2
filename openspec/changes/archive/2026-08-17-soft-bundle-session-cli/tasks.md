# Tasks: soft-bundle-session-cli

## 1. 治理登记

- [x] 1.1 在 `openspec/governance/req-registry.yaml` 登记 `SBC: soft-bundle-session-cli` 前缀与 SBC-001..SBC-005 pending ID
- [x] 1.2 在 `openspec/governance/project-structure.toml` 注册 `deep_research_harness/scripts/soft_bundle.py`、`tests/contract/test_soft_bundle_cli.py` 与相关测试资产路径
- [x] 1.3 跑 `python3 openspec/governance/check_project_reqs.py` 与 `check_project_architecture.py`，确保治理检查通过

## 2. CLI 实现（@impl SBC-001/SBC-002/SBC-003/SBC-004/SBC-005）

- [x] 2.1 新建 `deep_research_harness/scripts/soft_bundle.py`，实现 `create / run / bind / status / path / inspect / phases / list`
- [x] 2.2 `create`：支持 `--root / --name / --question / --mode`；默认 root 为 `.deep-research-demo-runs/workspace/soft-bundles/<generated>/`；幂等；非 soft bundle 目录拒绝
- [x] 2.3 `run --mode 001`：调用 `make demo-scripted`，从 stdout 解析 `Run Bundle: b_xxx`；失败时 fallback `demo-fixture-graph` + mtime
- [x] 2.4 `bind`：只接受 `bundle_id`，解析 repository-relative `bundle_local_path` 并记录
- [x] 2.5 `status / path / inspect / phases / list`：只收 `soft_bundle_root`；`path` 只输出 repository-relative；`inspect` 委托 `make demo-sessions`；`phases` 读取本地记录内容
- [x] 2.6 manifest/记录中不保存绝对 host path；任何 path 都不作为 lifecycle 输入

## 3. 契约测试（@impl SBC-001..SBC-005）

- [x] 3.1 新建 `tests/contract/test_soft_bundle_cli.py`：覆盖 create 幂等、run 绑定、bind 未知 id、path 相对路径、inspect 委托、phases 读取、无 lifecycle authority 行为
- [x] 3.2 确保测试零网络、零凭据、不修改 Harness 核心

## 4. 入口与文档

- [x] 4.1 在 `deep_research_harness/Makefile` 新增独立 target `soft-bundle`，不动既有 target
- [x] 4.2 在 `deep_research_harness/README.md` 或 `docs/local-operations.md` 增加 operator-only CLI 说明，标注非 product 入口

## 5. 收尾

- [x] 5.1 `openspec validate soft-bundle-session-cli --strict` 通过
- [x] 5.2 `git diff --check` 通过
- [x] 5.3 跑相关 `make test-fast` / `make test-contract`，记录证据
- [x] 5.4 用 `.agents/skills/polish-openspec-change/SKILL.md` 完成 apply-ready 打磨后，再执行 apply
