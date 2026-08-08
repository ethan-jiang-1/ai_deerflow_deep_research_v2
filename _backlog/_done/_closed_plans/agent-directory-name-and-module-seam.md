# Plan: Deep Research Module Root Rename

> 类型: 命名 / 结构迁移准备 | 状态: **Decision confirmed — audit complete, implementation not started** | 更新: 2026-07-30
>
> 证据： [研究结论](agent-directory-name-and-module-seam/research.md) · [current-HEAD 影响清单](agent-directory-name-and-module-seam/impact-scan-2026-07-30.md)

## 已确认的决定

将 Deep Research 的 checkout 内物理 module root 从 **`agent/`** 改为
**`deerflow_research/`**。

这是一个更短、唯一、Python 风格的目录名；在仓库、shell history、全文搜索和多项目工作区中，它能直接
表达“DeerFlow 的 Deep Research module”，不再与 DeerFlow 的泛化 agent、`agents/` layer、graph node
agent 或上游 harness 混淆。下划线是刻意选择：它符合本项目 Python 命名语境，也避免把 filesystem root
伪装成 distribution name。

下列稳定 identity **不改**：

| Identity | 保持值 | 证据 |
| --- | --- | --- |
| Python distribution | `deerflow-deep-research` | `agent/pyproject.toml` 的 `[project].name` |
| import namespace | `deerflow_deep_research` | `agent/src/deerflow_deep_research/` |
| 对外工具名 | `deep_research` | `agent/src/deerflow_deep_research/__init__.py` |

因此这是一次 filesystem / repository-contract migration，而不是 Python package、工具协议或 DeerFlow
upstream API migration。

## 本轮范围与边界

本轮已经完成 current-HEAD 影响审计并更新本计划及研究材料；**不移动任何产品文件**。实际 rename 必须由
一个专门的 OpenSpec change（建议 slug：`rename-deep-research-module-root`）完成，并在其 proposal 中冻结
当时的 inventory。不得把本计划当成直接执行 `git mv` 的授权。

历史 archive 默认保留它记录当时的 `agent/` path；只有仍承担当前导航、命令或校验职责的链接才随迁移更新。
不得对 archives 做全局文本替换，也不得将 generic `agent` 词汇误改为 module path。

## 已审计的影响面

审计基线为 2026-07-30 的 `HEAD`：module 下有 **516** 个 tracked files；有 **299** 个 tracked files、
共 **1,388** 个 literal `agent/` 命中；结构 registry 有 **159** 个枚举的 `agent/` required paths。
数量本身不是替换清单，精确消费者、排除规则和逐项 verification 在附录影响清单中。

| Contract 面 | 已确认的 consumer / 风险 | 迁移 change 的责任 |
| --- | --- | --- |
| 结构治理与 specs | `project-structure.toml`、Agent Charter checker、project/spec/requirement checker、main specs、`openspec/config.yaml` | 先更新 registry/source-test roots，再生成 locator，并更新 checker fixture 与 specs |
| CI | 三个 Deep Research workflow 的 trigger path、working directory 与 artifact path | 更新真实 path；workflow file、display name、job/status context 先与 GitHub branch protection 核对，避免无意断开 required check |
| Docker | nested Compose 的 host mount、container mount、`PYTHONPATH`、说明与测试 | host 端改为 `deerflow_research/src`；明确并统一 container target，而非留下旧名字 |
| Runtime retained state | session default root、diagnostic relative location，以及 ignored `.reports/` / `.deep-research-demo-runs/` | 不丢失、不静默删除；提供明确、可审计且幂等的旧数据迁移/选择策略并测试跨 rename resume 行为 |
| 开发命令、文档与活跃 backlog | root/module guides、README、Make/script messages、profiles、`.gitignore`，以及仍指向当前源码的 active bug/plan | 只替换真实 module path，保留泛化 DeerFlow `agent` 术语；archive 保持当时事实 |
| 测试、fixture 与 release evidence | root-path constants、Docker/CI/release/config/prepare/profile tests、committed attestation fixture | 随 contract 改断言；生成类 evidence 通过其 owning command 重建，不能手改伪造 |
| 本机与外部 automation | ignored `.env`、`.venv`、report/run state；本机 hook 中可能有绝对 `.../agent` path | 有迁移前检查和 operator checklist；不会把用户特定绝对路径提交进仓库 |

## 必须在 proposal/design 中冻结的决定

1. **一次 canonical root。** `git mv agent deerflow_research` 后不保留永久 symlink、alias 或双 source
   root；它们会让 CI、Docker、文档与 retained state 获得两个不等价入口。若临时兼容不可避免，须写明
   consumer、到期时间、删除 verification。
2. **数据优先于外观。** 禁止自动删除或覆盖旧 `agent/` 下的 ignored state。新 default root 指向
   `deerflow_research/`；旧 run/report 的迁移、只读 fallback 或 operator-confirmed copy/move 必须有明确
   选择、冲突规则、幂等性和 rollback 说明。`.env` 由操作者安全复制/重建，`.venv` 重建，不把 secret 或
   virtualenv 纳入 Git migration。
3. **Docker 一致性。** 建议同时采用 `/app/deerflow_research/src` container target 和新的 `PYTHONPATH`，
   因为它是此 compose override 的私有 implementation seam。若保留 `/app/agent/src`，proposal 必须写出
   已验证的 external compatibility consumer 和最终清理点。
4. **CI compatibility 显式检查。** path filter 与 working directory 必改；workflow filename/name/job ID
   是否改名取决于 GitHub required-check、外部 badge 或 automation 的实际 consumer，不能凭美观重命名。
5. **原子可回滚。** 没有通过 migration gate 前，不提交部分 rename；rollback 仅回退 tracked path changes，
   不自动处理已由操作者迁移的本地数据。

## 建议的执行顺序与验收门槛

1. 在新 change 中重新跑影响清单的命令，并确认 inventory 相对本审计没有漂移。
2. 在同一个原子 change 中，以测试先行更新 registry、governance checker、current specs/config、CI、Docker、
   scripts/docs 与 owning tests，并执行 `git mv agent deerflow_research`；只修改 module-path token。
3. 实作并测试 retained-data policy，提供 migration-before/after 的 operator 指引；扫描本地 `.claude`、shell
   aliases、IDE tasks、CI secrets/branch protection 等仓库外消费者。
4. 使用 `git diff --check`、结构 checker、`uv lock --check`，以及 module 的 deterministic verification；运行
   更新后的 workflow/compose contract tests。对 Docker 用 `docker compose config` 验证真实 mount 与
   `PYTHONPATH`，对 CI 用 fixture/parse test 验证 trigger、cwd 与 artifact path。
5. 以严格 allowlist 复扫 current artifacts 中的 `agent/`：剩余命中只能是 generic product terminology、
   deliberately preserved historical evidence，或经设计记录的短期兼容；每个剩余 path 命中都要解释。

## 非目标

- 不改 Python distribution、import namespace、工具协议、backend/ 或 frontend/ 的产品边界。
- 不用 blanket replace 改写 generic `agent`、`agents/`、lead-agent 或历史 archive。
- 不因为物理目录改名创建第二套 module guide、source tree 或长期 shim。

## 交付状态

命名决定和完整影响审计已经进入本计划。下一步是审阅本计划中尚待冻结的 retained-data、Docker 与 CI
compatibility 决策，然后创建上述专用 OpenSpec change；在那之前，`agent/` 仍是当前 canonical path。
