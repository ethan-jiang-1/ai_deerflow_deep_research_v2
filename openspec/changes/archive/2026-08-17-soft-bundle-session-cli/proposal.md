## Why

Deep Research Harness 的真实 Run Bundle id 是 `b_<random>`，不透明、随机、不可读。本地跑完 001 后只能靠 `find` 或 `demo-sessions` 手工定位；MD/skill 无法在运行前先拿一个稳定句柄，也无法在运行后通过句柄查回目录、日志、内容。需要一个 operator-only 的 soft bundle CLI，用 `soft_bundle_root` 作为唯一无状态句柄。

## What Changes

- 新增 operator-only CLI `deep_research_harness/scripts/soft_bundle.py`，命令：`create / run / bind / status / path / inspect / phases / list`。
- `soft_bundle_root` 是唯一路由句柄；`name` 只是 `manifest.json` 里的备注；不维护全局映射表。
- `create` 支持 `--root / --name / --question / --mode`；不给 `--root` 时用默认 `.deep-research-demo-runs/workspace/soft-bundles/<generated>/`。
- `run` 复用现有 `make demo-scripted` 等入口，解析真实 `bundle_id`，并记录 repository-relative `bundle_local_path`。
- `bind` 接受 product `deep_research` 已返回的 `bundle_id`，只做 operator 侧记录。
- 所有路径输出都是 repository-relative，不暴露绝对 host path；`path`/记录绝不作 lifecycle 输入。
- 不改 product `deep_research` tool schema，不改 Harness 核心。

## Capabilities

### New Capabilities
- `soft-bundle-session-cli`: operator-only 的 soft bundle CLI，用无状态 root 句柄把 `bundle_id` 与 repository-relative local record location 串起来，并复用现有 demo/session 入口做查询。

### Modified Capabilities
（无）

## Impact

- 新增 `deep_research_harness/scripts/soft_bundle.py`
- 新增 `deep_research_harness/tests/` 契约测试
- 新增 `openspec/governance/req-registry.yaml` 中 `SBC: soft-bundle-session-cli` 前缀与需求 ID
- 更新 `openspec/governance/project-structure.toml` 路径登记
- 新增 Makefile target `soft-bundle`
- 不修改 `src/deerflow_deep_research/`，不修改 `deerflow/`

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/soft_bundle.py`; it owns the operator CLI composition and the root->bundle_id->local-path record boundary.
- **Seam classification:** wiring because it connects existing operator entry surfaces (`make demo-*`, `demo-sessions`) without changing graph, node, lifecycle, model, or tool authority.
- **Question:** Can an operator use a stateless `soft_bundle_root` to create, run, bind, inspect, and query local Deep Research bundles while never exposing absolute host paths or making records a lifecycle authority?
- **Necessary adjacent/external contracts:** `demo-pipeline` (existing Make targets used by run), `run-bundle-discovery-and-operations` and `research-local-session-workbench` and `research-cli-onboarding` (boundaries for path redaction and no lifecycle authority), `run-event-journal` (demo-sessions inspection), `project-structure` (canonical registration). No DeerFlow public interface is changed.
- **Evidence seam:** contract tests for CLI commands covering create idempotency, run parsing, bind, status/path relative-only output, inspect delegation, phases reading, and no-path-as-lifecycle-input guard.
- **Not in scope:** product `deep_research` tool schema changes, history/use (v2), real mode 003/004 in v1, modifying Harness core or `deerflow/`.
- **Triggered review policies:** authority-and-projections, change-admission
