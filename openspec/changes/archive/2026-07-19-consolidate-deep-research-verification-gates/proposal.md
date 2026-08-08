## Why

Deep Research 已经具备完整且互斥的零凭据 deterministic test lanes 和机械化 requirement evidence 检查，但本地、OpenSpec archive 和现有 workflow 定义仍各自维护验证命令，production `@impl` 也未校验未知或已 retired 的 requirement ID。项目当前是单人、本地开发阶段，正适合先建立一个本地权威入口，避免测试资产继续增长后再次出现门禁漂移，而不提前建设多人或远端 CI 基础设施。

## What Changes

- 在 `agent/Makefile` 建立 canonical `make verify`：它以仓库根作为参数运行三个 root governance checker，再组合 lock、lint、test-asset、requirement-coverage，以及 fast、integration、workflow 三条现有零凭据 deterministic lanes；现有 `make test` 保留为三条 pytest selection 的 test-only union。`make install` 以 `uv sync --locked` 同步现有 `operations` 与 `demo-tui` extras，使 canonical gate 的本地依赖可一次准备好并随后离线运行，且 setup 不会先改写 lock 再掩盖 drift。`verify` 将向所有 prerequisite recipe 导出 `UV_NO_SYNC=1`，避免 `uv run` 在验证时隐式同步或改写环境。
- 让 OpenSpec archive guidance 的**deterministic verification**部分只引用 `cd agent && UV_OFFLINE=1 make verify`，不再复制组件命令；change-specific strict `openspec validate <change> --strict`、diff 与边界检查仍是独立的 archive 条件。
- 让两个已有 agent workflow 的 `jobs.deterministic` 以 `uv sync --locked` 准备同一组 extras 后声明式调用一次 `UV_OFFLINE=1 make verify`，并由本地 contract test 锁定该 job-scoped 引用及 `verify` 的精确 prerequisite 集合；同时让 `agent-tests.yml` 的既有 PR/push path filter 监听 `agent-release-e2e.yml`，避免 release workflow 单独变更绕过它的 contract。本 change 不要求 GitHub Actions 实际运行。
- 扩展 requirement-coverage checker，拒绝 `agent/src/**/*.py` 中未知或 registry 已标为 `[DEPRECATED]` 的 production `@impl` ID；仅识别 AST docstring 与 Python comment token，词法/语法错误 fail closed，同时保留当前 test-side alive-requirement coverage 语义。
- 删除失去权威意义且已与 canonical registry 漂移的 tracked `openspec/governance/req-registry.yaml.tmp`。
- 明确远端 runner、branch protection、required checks、secrets、团队审批、发布自动化和其他多人协作治理全部延后。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `evaluation-hardening` (`EVH-009`, `EVH-010`): 将完整零凭据 deterministic aggregate 固定为单一、本地可执行的 canonical gate，并让 requirement traceability 同时机械校验 production-source `@impl` 引用的 registry 有效性。

## Impact

- 受影响的 project-owned surfaces 是 `agent/Makefile`、`openspec/governance/check_project_req_coverage.py`、对应的 agent contract/governance tests、`openspec/config.yaml`、`agent/README.md`、人写的 `agent/AGENTS.md` command guidance、两个现有 `.github/workflows/agent-*.yml` 定义，以及失效临时 registry 文件；不增加依赖，`demo-tui` 已在 lockfile 中且已经是 existing integration lane 的必要 extra。
- 新增测试属于 deterministic contract/governance evidence，最低责任 seam 分别是 Makefile/workflow composition contract 和 requirement-coverage checker。无需 persisted trace replay、live dependency 或 full-system acceptance。
- 实施前会记录 worktree status baseline；最终 boundary evidence 同时检查 tracked diff 与包含 untracked files 的受保护路径 status，避免 `git diff` 漏掉新文件。非受保护且不重叠的脏改动会被保留；若 `backend/` 或 `frontend/` 已经不干净，则改在 clean worktree/获方向后再实施，保证本 change 的 boundary proof 可判定。
- 不改变任何 Deep Research graph node/component、typed state/checkpoint、node-agent role、sandbox artifact、runtime behavior 或 public API。
- `config.yaml`、`extensions_config.json`、public/custom skills、per-user Agent/SOUL、MCP、ACP、DeerFlow task subagents、reflection path 和 runtime mounts 均不使用或修改。`openspec/config.yaml` 仅是 authoring/archive guidance；没有 next-agent-build 或 Gateway restart 影响。
- 不配置或启用远端 CI；workflow 文件只保持未来兼容，不作为本 change 的执行证据或完成条件。新增 path 仅使既有 deterministic contract 在 release-workflow-only 改动时同样被选择，不改变 release workflow 的触发、runner、secret、required-check 或 branch-protection 配置。`make install` 或 workflow setup 准备包含 `operations` 与 `demo-tui` 的 lock-derived agent environment；随后 `UV_OFFLINE=1 make verify` 是本 change 的本地验收命令，且 `verify` 自身不包含 provision/install、live、release、Postgres 或网络测试成员，并向所有 prerequisite recipe 导出 `UV_NO_SYNC=1` 来禁止隐式环境同步。
- 不修改 `backend/` 或 `frontend/`。任何上游 mirror 变更都是另一个 BREAKING escalation。
