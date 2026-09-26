# DeerFlow v2.1.0 Host Contract — Quick Reference

> 速查，不是第二权威：框架权威在 `deerflow/AGENTS.md` 与 `deerflow/backend/AGENTS.md`
> （及其中链接的框架文档）；本文件把"应用侧实际依赖的契约点"集中索引，每条标注来源。
> 框架升级时：先读框架自带文档，再更新本文件与
> `tests/contract/test_deerflow_public_api.py`（含 `CURRENT_DEERFLOW_PIN`），
> 并按仓库治理流程同步 submodule 声明锁（治理侧账本与 2026-09-26 的归档 change
> 记录了该流程；架构门会比对声明锁与真实 gitlink）。
>
> 基准：submodule `ceebf97f`（ethan tip，= 上游 v2.1.0，2026-09-24 发布）。
> 生成依据：deerflow 自带文档盘点 + 应用侧 grep 交叉验证（2026-09-26）。

## 1. Package & Runtime Basics

| Fact | Value | Source |
| --- | --- | --- |
| Framework package | `deerflow-harness` v2.1.0 at `deerflow/backend/packages/harness/`, import prefix `deerflow.*` | deerflow/backend/packages/harness/pyproject.toml |
| Extension contract | `deerflow-extension-api==0.2.1` (`deerflow_extension_api.*`) | framework deps |
| Python / langgraph | >=3.12 / >=1.2.9,<1.3 | framework deps |
| Gateway entry | FastAPI `app.gateway.app:app` (app-layer, port 8001; `/health` → `service=="deer-flow-gateway"`), embedded LangGraph-compatible runtime (RunManager + run_agent + StreamBridge) | deerflow/backend/AGENTS.md |
| Config | repo-root `config.yaml` + `extensions_config.json` (both gitignored; Gateway refuses to start without the former; hot-editable via Gateway API). Third-party extensions: top-level `plugins:` + `deerflow extensions install/...`, Gateway restart required | deerflow/backend/AGENTS.md |
| Skills | any directory with `SKILL.md` becomes a runtime package boundary; nested SKILL.md no longer registers independently; sandbox keeps `/mnt/skills` projection | deerflow/AGENTS.md (2.1.0 behavior) |
| Memory | pluggable (`memory.manager_class`, `memory.backend_config`); `storage_path` is now a DIRECTORY | backend docs |
| Tracing | every Gateway response carries `X-Trace-Id`; `logging.enhance.enabled` only controls log format | backend docs |

## 2. Environment Variables (v2.1.0 documented set)

`DEER_FLOW_HOME` (default `backend/.deer-flow`), `DEER_FLOW_PROJECT_ROOT`,
`DEER_FLOW_CONFIG_PATH`, `DEER_FLOW_EXTENSIONS_CONFIG_PATH`,
`DEER_FLOW_SKILLS_PATH`, `DEER_FLOW_INTERNAL_AUTH_TOKEN`, `DEER_FLOW_ENV`,
`DEER_FLOW_REPO_ROOT`, `DEER_FLOW_CHANNELS_GATEWAY_URL`.

**Removed in 2.1.0**: `DEER_FLOW_HOST_SKILLS_PATH` / `SKILLS_HOST_PATH`
(host base dir now derives from `DEER_FLOW_HOST_BASE_DIR`).

App-side notes (verified by grep, source: `scripts/prepare.py`, `scripts/configure.py`,
`profiles/README.md`, handoff recipe):

- The demo/Gateway recipe sets `DEER_FLOW_PROJECT_ROOT / _CONFIG_PATH /
  _EXTENSIONS_CONFIG_PATH / _HOME` and `DEER_FLOW_DEEP_RESEARCH_STARTUP_FINGERPRINT`
  (app-defined: startup snapshot from `runtime/startup_snapshot.py`; recalculate and
  restart the Gateway after ANY app-code or profile change, or tool calls fail with
  `bundle.unavailable`).
- `DEER_FLOW_AUTH_DISABLED` (configure.py:430) and `DEER_FLOW_GATEWAY_HEALTH_URL`
  (configure.py:521) are NOT documented by the framework — treat as app-consumed
  until a behavioral check proves otherwise (pending, see plan P2).

## 3. Application-Side Contract Points (all verified consistent on ceebf97f)

| App location | Depends on | Protection |
| --- | --- | --- |
| `pyproject.toml` (`deerflow-harness>=2.1.0,<2.2` + uv editable path source) | package + version floor | lock + `make lock-check` |
| `runtime/startup_snapshot.py:134`, `runtime/diagnostics.py:79` | `deerflow.config.app_config.AppConfig` | `tests/contract/test_deerflow_public_api.py` |
| `runtime/diagnostics.py:169`, `runtime/runtime_adapter.py:100` | `deerflow.config.paths.get_paths` | same |
| `runtime/node_agent_bridge.py:234` | `deerflow.config.get_app_config` | same |
| `runtime/node_agent_bridge.py:154` | `deerflow.models.factory.create_chat_model` | same |
| `runtime/node_agent_bridge.py:227` | `deerflow.tools.tools.get_available_tools` | same |
| `runtime/runtime_adapter.py:94`, `runtime/work_unit_storage_probe.py:280` | `deerflow.sandbox.tools.ensure_sandbox_initialized_async`, `deerflow.sandbox.get_sandbox_provider` | same |
| `runtime/graph_host.py:87` | `deerflow.runtime.checkpointer.async_provider.make_checkpointer` | same |
| `agents/factory.py:34` | `deerflow.agents.factory.create_deerflow_agent` | same |
| `tests/contract/test_deerflow_public_api.py:9-12` | `deerflow.trace_context.get_current_trace_id` (zero-arg) + submodule pin | the pin test itself |
| `docker/docker-compose.deep-research.yaml` | base `deerflow/docker/docker-compose.yaml`; override gateway `uvicorn app.gateway.app:app --port 8001` | compose build |
| `runtime/gateway_observer.py:98,124` | `POST /api/threads`, `/api/threads/{id}/runs/stream` (SSE) | `tests/live/test_gateway_forwarding_proof.py` |

The nine `deerflow.*` deep module paths above are the "undocumented by AGENTS.md"
dependency surface: they ARE covered by `test_deerflow_public_api.py`; extend that
test (do not skip it) when adding a new deep import.

## 4. Submodule Reality Notes

- The ethan fork tip carries 244 tracked `_digest/` / `_faq_on_digested/` files:
  historical research notes, shipped INSIDE the submodule. Read-only background;
  never treat them as current framework truth (root AGENTS.md says the same).
- Upgrade protocol: bump submodule pointer → adapt app layer → update
  `CURRENT_DEERFLOW_PIN` → update the governance-side declared lock through the
  repo's change process → run the repo architecture gate (it compares the
  declared lock against the real gitlink index/HEAD and fails on drift).
