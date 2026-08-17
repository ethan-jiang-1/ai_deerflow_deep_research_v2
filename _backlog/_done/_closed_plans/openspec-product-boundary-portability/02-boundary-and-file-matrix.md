# 边界与文件矩阵

## 内容归属

| 内容 | Owner | Portable |
| --- | --- | --- |
| Change admission、primary owner、scope、authority、evidence | `change-guidance/core/change-practice.md` | 是 |
| 状态、失败、恢复、人类决定、participant outcome、control placement | `profiles/workflow-control/workflow-control.md` | 是，可选 |
| LLM node cognition-versus-code route | `profiles/node-agent/node-agent.md` | 是，可选 |
| DeerFlow public-API-only downstream boundary | `profiles/deerflow-downstream/deerflow-downstream.md` | 是，可选 |
| Deep Research paths、budgets、Program form、information map | `change-guidance/local/deep-research.md` | 否 |
| 产品导向与 owner 路由 | `product/README.md` | 否 |
| Approved/pending behavior | main specs / active delta | 否 |
| Current runtime facts | code、typed contracts、tests | 否 |
| 精确文件和 import 结构 | `governance/project-structure.toml` | 否 |
| 本地 policy enablement 与 CLI | `config.yaml`、`check_change_guidance.py` | 否 |

## 最终文件处置

| 旧路径 | 最终处置 |
| --- | --- |
| `change-guidance/principles.md` | 内容并入 `core/change-practice.md`，旧文件删除 |
| `change-guidance/node-edit-map.md` | 完整语义进入 `profiles/node-agent/node-agent.md`，旧文件删除 |
| `change-guidance/policies/*.md` | 按 owner 合并进 core/profile/local，旧目录删除 |
| `product/deep-research.md` | 迁入 `product/README.md`，旧文件删除 |
| `governance/closeout-evidence/` | 工具与说明提升到 `governance/selected-change-closeout.*` |
| Harness 内 OpenSpec governance tests | 移到 `openspec/tests/governance/` |

## Portable Allowlist

- `openspec/change-guidance/core/**`；
- 明确选择的 `openspec/change-guidance/profiles/<profile>/**`；
- `openspec/governance/change_guidance_kernel.py`。

Product、local、config、specs、changes、archive、tests、evidence、project manifests 和 wrapper 均不在
allowlist 中。

## README 规则

- `change-guidance/README.md`：只做 portable/local 路由；
- `product/README.md`：只做产品入口和 owner 路由；
- 实质 contract 使用独立命名文档；
- 不为每条 policy 创建薄文件。
