# `agent/` → `deerflow_research/`：当前 HEAD 影响面盘点

> 快照：2026-07-30，`cc10d42c64bec4b2236b321145a395a0d33ccf07`。  
> 方法：只读当前 HEAD 的源码、测试、CI、Docker、OpenSpec、脚本、忽略规则与 Git 历史；本文件不授权移动目录，也不改写父计划或其研究记录。

## 结论

`deerflow_research/` 是一个语义更明确、可全文精确搜索且符合 Python 项目目录习惯的
canonical checkout 路径。它不是 DeerFlow 上游规定的路径：本仓库在
`c0a66a8e`（2026-07-12，`feat(agent): implement Deep Research change 00 runtime substrate`）才
引入独立项目；当前没有仓库内的顶层 rename 历史。

这不是 Python package rename。保持下列公开 Python 身份不变：

- distribution：`deerflow-deep-research`（[`agent/pyproject.toml:2`](../../../agent/pyproject.toml:2)）；
- import namespace：`deerflow_deep_research`（同文件 `tool.hatch`/wheel 配置，以及
  [`openspec/governance/check_project_architecture.py:28`](../../../openspec/governance/check_project_architecture.py:28)）；
- tool/skill/Agent 名称：`deep_research`、`deep-research-controller`、`deep-research`。

因此，移动本身不会要求调用方改 Python import 或重发包；但它会替换一个已被治理、运行、
CI 和文档消费的 filesystem interface。应作为一个独立的 spec-driven OpenSpec change 执行，
不得与认知循环、graph 或产品行为变更混合。

## 盘点范围与可复现基线

在该 HEAD 上：

| 观察 | 结果 | 可复现命令 |
| --- | ---: | --- |
| tracked 的项目文件 | 516 | `git ls-files agent \| wc -l` |
| 含字面量 `agent/` 的 tracked 文件 / 行 | 299 / 1,388 | `git grep -l -F 'agent/' HEAD`; `git grep -n -F 'agent/' HEAD \| wc -l` |
| 排除 `_backlog/` 与 archived changes 后的文件 / 行 | 88 / 508 | `git grep -l -F 'agent/' HEAD -- ':(exclude)_backlog/**' ':(exclude)openspec/changes/archive/**'` |
| active main spec 含旧路径 | 12 | `git grep -l -F 'agent/' HEAD -- openspec/specs` |
| archive change 文档含旧路径 | 155 | `git grep -l -F 'agent/' HEAD -- openspec/changes/archive` |
| backlog 文档含旧路径 | 56 | `git grep -l -F 'agent/' HEAD -- _backlog` |

这些是审计量而不是“全部替换”的授权。`agent/` 也会出现在 `.agent/`、
`backend/.../agents/`、`lead_agent/` 及普通英文句子中；它们不是本次移动对象。

## 必须随迁移更新的当前 contract

### 治理与 OpenSpec

| Surface | 一手证据 | 迁移动作 |
| --- | --- | --- |
| 结构 registry | [`project-structure.toml:6-12`](../../../openspec/governance/project-structure.toml:6) 的 guide/source/test roots；共 159 条 `path = "agent/..."`（177 条 required paths 总计），另有 node root [`:836`](../../../openspec/governance/project-structure.toml:836) | 将所有 canonical path 改为 `deerflow_research/...`；移动后用 architecture checker 渲染新 `AGENTS.md` 受控块，禁止手改生成块。 |
| Charter checker | [`check_agent_charter.py:24-31`](../../../openspec/governance/check_agent_charter.py:24) 与 [`:87`](../../../openspec/governance/check_agent_charter.py:87) 固定 guide/docs path | 同步改为新根，并更新对应 fixture/contract tests。`check_project_architecture.py` 没有旧根硬编码，正确读取 manifest；只需保持 manifest 正确。 |
| Charter、治理正文与 registry | [`agent-charter/charter.md:4,11`](../../../openspec/governance/agent-charter/charter.md:4)、[`agent-information-map.md:4-24`](../../../openspec/governance/agent-charter/policies/agent-information-map.md:4)、[`architecture-policy.md:14-37`](../../../openspec/governance/architecture-policy.md:14)、[`req-registry.yaml:191-192,210`](../../../openspec/governance/req-registry.yaml:191) | 更新仍具规范/导航效力的路径措辞；不改变 requirement ID、含义或 package 名。 |
| 12 份 active main specs | `deep-research-agent-charter`、`demo-pipeline`、`deployment-configuration`、`evaluation-hardening`、`hitl1-node`、`local-configuration-profiles`、`node-agent-runtime`、`node-prompt-catalog`、`project-structure`、`research-cli-onboarding`、`research-demo-tui`、`research-fake-cli-onboarding` 下的 `spec.md` | 把仍规范性地指向旧根的路径改为新根，尤其 deployment spec 的 host source 与 Docker mount contract。 |
| 当前 authoring 指针 | [`openspec/config.yaml:6,40,68,80`](../../../openspec/config.yaml:6) | 更换产品路径与 `cd` 验证命令。 |

### 运行时、留存与本地状态

| Surface | 一手证据 | 迁移动作 |
| --- | --- | --- |
| 编辑安装与 origin validation | [`scripts/prepare.py:149`](../../../agent/scripts/prepare.py:149) 设置 `root / "agent"`；[`274-281`](../../../agent/scripts/prepare.py:274) 以 `agent/src/...` 验证模块 origin；[`331-342`](../../../agent/scripts/prepare.py:331) 对该目录 `--editable` 安装 | 更新三处及 `test_prepare.py` fixture。否则新路径会在安装或 origin gate 失败。 |
| Reader-interface checker | [`scripts/check_node_workflows.py:14-15`](../../../agent/scripts/check_node_workflows.py:14) 直接使用 repo-relative `agent/src/...` | 改为新根，保持其 `repo_root` API；更新 reader tests。 |
| 诊断显示路径 | [`runtime/run_diagnostics.py:20`](../../../agent/src/deerflow_deep_research/runtime/run_diagnostics.py:20) 将用户可见位置固定为 `agent/.reports/...`；[`demo_real.py:156,181,380`](../../../agent/scripts/demo_real.py:156) 和 [`demo_tui.py:88,113,694`](../../../agent/scripts/demo_tui.py:88) 投影此值 | 同步改常量、CLI/TUI 文案和 `test_run_experience_failures.py:519-520`。真实 journal 用 `_AGENT_ROOT` 定位，移动后会跟随源码；问题是公开/诊断 locator 不能继续说旧路径。 |
| 当前 ignored state | 当前实际目录含 `.env`、`.venv`、`.reports`、`.deep-research-demo-runs`、`.pytest_cache`、`.ruff_cache`、`.agents` 与 `.claude`；根 [`.gitignore:42-47`](../../../.gitignore:42) 忽略 `agent/.reports/` | 迁移窗口须先停止 demo/Gateway/Compose，列出并备份/移动本机 state，后再清理旧根。Git index 不能替代这项操作员确认；不得读出或提交 `.env`/报告/运行 bundle。`profiles/` 是新旧根的 sibling（[`local_profiles.py:111-123`](../../../agent/scripts/local_profiles.py:111)），不应移动。 |
| 项目内相对路径 | `agent/pyproject.toml` 的 `src` layout、`Path(__file__).resolve().parents[...]` 的 scripts/test helpers | 保持 package/source 子树原样即可。这些是相对自身定位，不要求改 distribution/import；迁移后需用测试证实。 |

### Docker、CI 与外部可见自动化

| Surface | 一手证据 | 迁移动作 / 决策 |
| --- | --- | --- |
| Compose host mount | [`docker-compose.deep-research.yaml:9-20,32-33`](../../../agent/docker/docker-compose.deep-research.yaml:9) 的 `../agent/src`、`/app/agent/src`、`PYTHONPATH` | host source **必须**改为 `../deerflow_research/src`。容器 target 是一个需明确批准的接口：推荐同步为 `/app/deerflow_research/src`（命名一致）；技术上可保留 `/app/agent/src` 以减小容器 consumer 变动，但会留下双名。无论选择哪种，更新 compose contract tests 并验证 Gateway 只读挂载、sandbox 无 host source mount。 |
| Deterministic CI | [`agent-tests.yml:6,13,27`](../../../.github/workflows/agent-tests.yml:6) 的 filters 与 working directory | 改 path filters 为 `deerflow_research/**`、working directory 为新根；否则 PR 不触发或 job 不能启动。 |
| Live/release CI 与 artifact path | [`agent-live-evaluation.yml:16,40`](../../../.github/workflows/agent-live-evaluation.yml:16)、[`agent-release-e2e.yml:21,37,62`](../../../.github/workflows/agent-release-e2e.yml:21) | 改 working directory 和 reports artifact source paths；同改 release-attestation source scope 及其 tests。 |
| CI display identity | workflow filename、`name:`、concurrency group、artifact name 都为 `agent-*` | **人工决策**：默认保留，因 branch protection、required check、外部下载脚本可能依赖显示名；只有审计 GitHub ruleset/consumer 后才改名。它们不是 path relocation 的机械任务。 |
| 仓库外消费者 | 当前仓库无法枚举用户 shell history、IDE tasks、bookmarks、clone scripts、Docker volume usage、artifact downloaders 或本地绝对路径。当前 tracked 绝对路径仅在 backlog bug 记录中可见（例如 [`BUG-013:70`](../../bugs/BUG-013-semantic-hitl-input-breaks-first-run.md:70)）。 | **人工决策/发布输入**：确定是否保留旧路径兼容窗口。推荐不建立长期 symlink；发布说明给出新 `cd deerflow_research`、支持窗口与明确 rollback。 |

### 测试、文档与当前产品入口

| Surface | 一手证据 | 迁移动作 |
| --- | --- | --- |
| Contract tests/fixtures | `test_docker_compose.py:22-29,64,164`、`test_prepare.py:13-61`、`test_agent_charter_governance.py:25-31`、`test_architecture_governance.py:21-96`、`test_import_boundaries.py:25-50`、`test_requirement_test_coverage.py:35-173` | 这些不是普通 assertion 文案，而是根路径/registry fixture；全部切换为新 canonical root，同时保留负向 fixture 的测试意图。 |
| Product tests与操作显示 | `test_live_workflow.py:22`、`test_release_workflow.py:24`、`test_release_attestation.py:35-36`、`tests/assets/release_attestation.py:26`、`test_demo_real.py:283,310,326`、`test_demo_tui.py:453,470`、`test_public_entry_replay.py:16-18` | 更新 report scope、用户可见命令、source fixture path。 |
| Root / project docs | [`AGENTS.md:51,71,115`](../../../AGENTS.md:51)、[`README.md:98`](../../../README.md:98)、[`profiles/README.md:6`](../../../profiles/README.md:6)、[`.gitignore:42,47`](../../../.gitignore:42) | 更新顶层导航、产品说明、profile 操作入口和 ignore path。根 `Makefile`、`scripts/`、根 `docker/`、pre-commit 与 real config 没有本项目顶层旧路径硬编码；不要误改 `config.example.yaml` 的 generic `agents/my-agent` 示例。 |
| Moved-tree docs/scripts | `AGENTS.md` generated locator、`README.md` quick-start、`docs/local-operations.md`、`docs/testing-and-evaluation.md`、`scripts/demo_real.py`、`demo_tui.py`、`demo_sessions.py`、`local_profiles.py`、`Makefile` | 将人可执行 `cd agent`、`agent/.env`、`agent/.reports`、bundle locator 统一为新根；相对 `make` targets 无需重命名。 |
| 活跃 backlog | [`_backlog/bugs/BUG-013...:30-70`](../../bugs/BUG-013-semantic-hitl-input-breaks-first-run.md:30) 仍链接/命令指向当前源码 | 保持该 bug 活跃时更新链接和绝对命令。父 plan/research 和 plans index 也需在获批 rename change 中转为新决定。 |

## 历史材料：保留，不批量重写

`openspec/changes/archive/**` 的 155 份匹配和 `_backlog/_done/**` 的大多数匹配是当时的
审计/交付事实。治理本身规定 archived delta 不替代 active authority（
[`architecture-policy.md:11-12,28`](../../../openspec/governance/architecture-policy.md:11)）。
因此 archive 不做机械 rewrite；在新 change 的 proposal/design 中明确“历史路径仍指向当时的
checkout”。仅更新仍 active 的索引、plan、bug 或运行指针。

## 建议的迁移关卡

1. **准入与冻结**：创建单独 change；确认 `deerflow_research/`、容器 target、旧路径兼容策略、
   CI display-name 策略与 rollback owner。停止使用旧根的进程，盘点忽略的本机 state；不读取 secrets。
2. **先改 contract，再物理移动**：以测试先行更新 structure-manifest/checkers、CI、Docker 和
   runtime literals，确保每个独立 contract 显式指向新根。执行一次原子目录 move，不创建永久 alias。
3. **重建/恢复本地环境**：重新建立新根 `.venv` 或明确移动后验证其 interpreter，恢复被批准的
   `.reports`/retained bundles；不要把 diagnostics、credentials 或 caches 纳入 Git。
4. **验证与发布**：运行下列命令，验证 GitHub workflow path filters 的 PR smoke、compose render
   与 artifact upload；仅在凭证/发布窗口明确选择时运行 live/release lanes。
5. **回滚**：在兼容窗口内，回滚同一 change，恢复经过确认的 local state 与 CI filters；不通过
   长期 `agent/` symlink 掩盖未更新 consumer。

```bash
# Current deterministic governance/product gates after the move
python3 openspec/governance/check_project_reqs.py .
python3 openspec/governance/check_project_specs.py .
python3 openspec/governance/check_project_architecture.py --render-guide .
python3 openspec/governance/check_project_architecture.py .
python3 openspec/governance/check_agent_charter.py .
cd deerflow_research && UV_OFFLINE=1 make verify

# Search only for unintended live old-root consumers; archives remain historical.
cd ..
rg -n -F 'agent/' \
  --glob '!openspec/changes/archive/**' \
  --glob '!_backlog/_done/**' \
  --glob '!deerflow_research/.agents/**' \
  --glob '!deerflow_research/.claude/**' \
  .
git diff --check

# Docker contract: render base first, then evaluate the moved test contract.
docker compose -f docker/docker-compose.yaml \
  -f deerflow_research/docker/docker-compose.deep-research.yaml config
cd deerflow_research && uv run --extra operations pytest tests/contract/test_docker_compose.py
```

最后一条 `rg` 是审计提示而非“零匹配”门槛：`.agent/`、`agents/`、历史 archive 和自然语言
提及需要人工分类，不能以盲目全局替换达成通过。
