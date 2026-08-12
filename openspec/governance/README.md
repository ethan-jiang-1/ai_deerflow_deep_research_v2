# openspec/governance — OpenSpec 治理导航

> 项目级 OpenSpec 治理扩展（非 OpenSpec 原生）。技术栈为 **Python 标准库**（零外部依赖，
> 永远可跑）。本文件是目录导航：每份治理对象的权威细节由其自有文件拥有，这里只负责
> "何时读哪个"。

## 何时读

| 对象 | 读者问题 | 权威细节位于 |
|------|----------|--------------|
| `req-registry.yaml` | 这条 requirement 的 ID 是否存在、如何分配缩写 / 三态 / 标题？ | [req-registry.yaml](req-registry.yaml) 自身 |
| `architecture-policy.md` | 什么算 active spec、结构权威如何分工？ | [architecture-policy.md](architecture-policy.md) |
| `project-structure.toml` | 精确目录 / import / 节点包清单？ | [project-structure.toml](project-structure.toml) |
| `check_project_reqs.py` | 需求 registry 一致性是否通过？ | 脚本 docstring |
| `check_project_specs.py` | main spec 结构是否有效？ | 脚本 docstring |
| `check_project_architecture.py` | 结构治理是否通过？ | 脚本 docstring |
| `check_agent_charter.py` | charter / policy 路由 / Focus Card 是否通过？ | 脚本 docstring |
| `check_project_req_coverage.py` | 每条 requirement 是否有测试证据？ | 脚本 docstring |
| `test-evidence-policy.md` | 测试证据的 authority、lifecycle、synchronized-change？ | [test-evidence-policy.md](test-evidence-policy.md)；批准语义由 `evaluation-hardening` main spec 拥有 |
| `agent-charter/README.md` | 先按什么原则、再选哪个 policy？ | [agent-charter/README.md](../agent-charter/README.md) |

## Checker 命令

在 repo 根运行（默认扫当前目录；也可传 projectRoot 参数）：

```bash
python3 openspec/governance/check_project_reqs.py
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_agent_charter.py
python3 openspec/governance/check_project_req_coverage.py
```

正常校验路径 `0` = PASS，`1` = 有违规。注意：stderr 也可能包含 non-failing warning
（仍返回 0）；argparse usage error 属于命令用法错误，不属于 0/1 contract。

`config.yaml` 的 `rules.tasks` 把归档前门禁固化为每个 change 的硬性收尾 task。
