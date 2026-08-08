# Deep Research Module Root Rename — Research

> 决定日期: 2026-07-30 | 研究范围: current `HEAD` 的一手仓库证据
>
> 详细且可复跑的 consumer inventory 见 [impact-scan-2026-07-30.md](impact-scan-2026-07-30.md)。
> 本文记录结论和边界；它不授权实际移动目录。

## 结论

`agent/` 不是 Python、DeerFlow runtime 或上游 distribution 强制要求的目录名；它是本仓库逐步形成并已被
治理、CI、Docker、命令和 retained data 固化的**本地 filesystem contract**。因此可以改名，但绝不是一次
普通文本整理。

已选择的未来 canonical root 是 **`deerflow_research/`**。它具有产品语义、足够唯一、比
`deerflow-deep-research/` 短，并且使用适合 Python 项目语境的下划线。它解决的是 checkout/module seam
的语义歧义；Python 和工具 identity 不随之改变。

| 不变量 | 当前一手来源 | 研究结论 |
| --- | --- | --- |
| distribution | `agent/pyproject.toml`：`name = "deerflow-deep-research"` | 保持不变；editable install 的 directory 改变不会要求改 distribution |
| import package | `agent/src/deerflow_deep_research/` 与 Hatch wheel packages | 保持不变；Python imports 不应因为 root rename 而 churn |
| public tool | `agent/src/deerflow_deep_research/__init__.py` 的 lazy export | 保持 `deep_research`，不扩大 API scope |
| sibling harness relation | `agent/pyproject.toml` 中 `../backend/packages/harness` | 物理 root 改为顶层 sibling 后相对关系仍应成立，真实 move 后以 `uv lock --check` 验证 |

## 为什么改名有实际收益

根 `AGENTS.md` 同时需要解释 DeerFlow 的 agent runtime、lead agent、sub-agents、内部 `agents/` layer 和
这个 downstream project。`agent/` 是其中唯一一个没有产品限定词的 filesystem root。读者在 shell、全文
搜索、IDE workspace 和跨仓库说明中看到 `deerflow_research/` 时能立即判断它是这个 downstream product，
而不会把它误当作通用 agent subsystem。

这不是“名字看上去更好”的唯一理由：独特的 canonical path 使 path-filter、artifact、Docker mount、诊断
位置和 operator command 都有同一个可辨认的 owner。收益只在保留**一个** canonical root 时成立；长期
`agent/` alias 或 symlink 会重新制造两套 interface，抵消收益。

## 影响面事实

在本研究的 current `HEAD` 上：

- `agent/` 下有 516 个 tracked files；
- 299 个 tracked files 含 literal `agent/`，共 1,388 个 occurrences；
- `openspec/governance/project-structure.toml` 有 159 个 `path = "agent/..."` entries；
- `.github/workflows/agent-tests.yml` 同时以 `agent/**` 过滤变更并以 `agent` 为工作目录；另两条 workflow
  使用 `agent` cwd 和 `agent/.reports/...` artifacts；
- `agent/docker/docker-compose.deep-research.yaml` 把 host `../agent/src` mount 到 `/app/agent/src`，并从该
  target 设置 `PYTHONPATH`；
- runtime 将 retained sessions 和 demo diagnostics 定位在 project root 下的 `agent/`（分别见
  `runtime/run_session.py` 与 `runtime/run_diagnostics.py`）；
- `agent/scripts/prepare.py`、root/module docs、main specs、governance checker 与大量 contract tests 将
  path 作为可执行 contract，而不是单纯叙述。

这些量化事实只对该 commit 有效；实际 migration change 开始前必须重新跑审计命令，不能把本次数量当成
永久范围。详细的路径分类、排除 rationale、风险与 test seam 由 companion inventory 保留。

## 关键风险与推荐处置

### 1. Retained local data 不能被 path rename 静默隔离

`RunSessionStore.project_default_root()` 当前构造 `project_root / "agent" /
".deep-research-demo-runs"`，诊断也公开 `agent/.reports/...` relative location。直接移动 tracked source 会让
新代码在新 root 寻找新数据，而旧 run/report 留在旧目录；这可能破坏 resume/inspect，且这些数据被 Git 忽略
不会包含在 rename commit 中。

实际 change 必须先选择并测试一个明确 policy：提供幂等、operator-confirmed migration，或在有严格冲突与
retirement 期限的情况下提供只读 legacy fallback。无论哪种，禁止自动删除、覆盖或提交 `.env`/`.venv`。
`.env` 应由操作者安全迁移或重建，`.venv` 应重建，`.reports` 和 retained run state 需在 migration checklist
中单列。

### 2. Docker 的 host 和 container paths 都是 contract

Compose override 不只写文档路径：它实际 mount source，并以 container `PYTHONPATH` 决定 import origin。
迁移时 host source 必须改为 `../deerflow_research/src`。推荐同步将私有 container target 改为
`/app/deerflow_research/src`，再通过 `docker compose config` 与 existing contract tests 验证；若因为未知
external consumer 保留 `/app/agent/src`，这应是有到期日的兼容决策，而不是遗漏。

### 3. CI 路径修改可能改变 required checks

三个 workflow 的 `paths`、`working-directory` 和 artifact locations 均依赖 root。它们必须随 move 更新；但
workflow filename、display name、job ID/concurrency name 可能被 branch protection、badge 或外部 automation
消费，不能没有查询就一并美化改名。应先保留 status identity，只改真实 filesystem path；获得 external
settings 证据后再决定显示层重命名。

### 4. 全局替换会误改不属于 module root 的语义

搜到的 `agent` 还包括上游 DeerFlow agent、`agents/` implementation layer、lead agent、`.agent/` metadata 和
historical archives。迁移 change 必须以结构 registry / current contract list 为 allowlist，逐类修改；archive
只修复仍指向 current artifact 的链接。最终的 residual scan 要逐条解释，不可用 `sed`/blanket replace。

### 5. 仓库外本地 automation 是真正的兼容边界

本机已观察到 ignored hook 将 bare pytest 转向绝对 `.../agent` path。这个事实证明 scan 不能只看 Git；但
用户特定绝对路径不能提交到 docs 或代码。迁移前 checklist 应要求操作者扫描 `.claude/`、shell aliases、IDE
tasks、local compose wrappers、CI secret/configuration 与 GitHub branch protection。

## 可复跑审计命令

从 repo root 执行；结论必须结合人工分类，不把所有 `agent` 词汇当作 path：

```bash
git ls-files agent
git grep -l -F 'agent/' HEAD
git grep -n -F 'agent/' HEAD
rg -n '^path = "agent/' openspec/governance/project-structure.toml
rg -n 'agent/\\*\\*|working-directory: agent|agent/\\.reports' .github/workflows
rg -n 'Path\\("agent"\\)|/ "agent"|/app/agent|agent/src' \
  agent openspec .github .gitignore AGENTS.md README.md profiles
```

迁移完成后，把上列 path root 改为 `deerflow_research` 复跑，再对遗留 `agent/` 做 allowlist review。加上
`uv lock --check`、architecture checker、module verification、workflow/compose contract tests 和 `docker compose
config`，才能证明 path 改名没有只停在文档层。

## 研究边界

- 本研究不改 `backend/` 或 `frontend/` 的产品边界；若真实 root consumer 出现在其中，只修改该 consumer 的
  filesystem reference，并由 change 明确记录。
- 本研究不建立 alias、symlink 或第二 source tree。
- 本研究不把 archive 历史路径伪装成当前命令。
- 物理 move、数据 policy 的实现和 CI external-setting 核对属于下一份 OpenSpec change 的任务。
