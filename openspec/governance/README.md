# openspec/governance — OpenSpec 治理导航

> 项目级 OpenSpec 治理扩展（非 OpenSpec 原生）。技术栈为 **Python 标准库**（零外部依赖，
> 永远可跑）。本文件是目录导航：每份治理对象的权威细节由其自有文件拥有，这里只负责
> "何时读哪个"。

## 何时读

| 对象 | 读者问题 | 权威细节位于 |
|------|----------|--------------|
| `req-registry.yaml` | 这条 requirement 的 ID 是否存在、如何分配缩写 / 三态 / 标题？ | [req-registry.yaml](req-registry.yaml) 自身 |
| `architecture-policy.md` | 什么算 active spec、结构权威如何分工？ | [architecture-policy.md](architecture-policy.md) |
| Project-structure manifest（`project-structure.toml` 契约 + `required-paths.toml` 清单） | 精确目录 / import / 节点包清单？ | [project-structure.toml](project-structure.toml) · [required-paths.toml](required-paths.toml) |
| `check_project_reqs.py` | 需求 registry 一致性是否通过？ | 脚本 docstring |
| `check_project_specs.py` | main spec 结构是否有效？ | 脚本 docstring |
| `check_project_architecture.py` | 结构治理是否通过？ | 脚本 docstring |
| `check_change_guidance.py` | Change Guidance / policy 路由 / Focus Card 是否通过？ | 脚本 docstring |
| `check_project_req_coverage.py` | 应用 requirement 是否有测试证据、OpenSpec 治理 requirement 是否有执行脚本证据？ | 测试或治理脚本 docstring |
| `check_harness_dependency_direction.py` | Harness 是否反向依赖 OpenSpec？ | 脚本 docstring |
| `check_doc_hygiene.py` | 文档层（ADR 索引↔目录 / 入口链相对链接 / 编码换行）是否漂移？ | 脚本 docstring（standalone，非 gate 组件、非 `make verify` 目标） |
| `test-evidence-policy.md` | 测试证据的 authority、lifecycle、synchronized-change？ | [test-evidence-policy.md](test-evidence-policy.md)；批准语义由 `evaluation-hardening` main spec 拥有 |
| `change-guidance/README.md` | 先按什么原则、再选哪个 policy？ | [change-guidance/README.md](../change-guidance/README.md) |

`governance/` is checker and registry navigation, not product documentation. For
Deep Research-specific orientation, leave this directory and read the
[product context](../product/README.md) reading map.

## Checker 命令

在 repo 根运行（默认扫当前目录；也可传 projectRoot 参数）：

```bash
python3 openspec/governance/check_project_reqs.py
python3 openspec/governance/check_project_specs.py
python3 openspec/governance/check_project_architecture.py
python3 openspec/governance/check_change_guidance.py
python3 openspec/governance/check_project_req_coverage.py
python3 openspec/governance/check_harness_dependency_direction.py
```

共六个 component checker。每个 checker 拥有自己规则的全部语义；它们只读、不写
registry，也不修改任何文件。

文档层卫生另有独立 checker（不属于六 component 聚合、不进 `make verify`）：
`python3 openspec/governance/check_doc_hygiene.py`（含 `--self-test` 负例控制）。

## Canonical aggregate gate

`openspec/governance/check_project_gate.py`（标准库、零外部依赖、在 repo 根运行）
只编排并聚合上述六个 component checker 的退出码，不拥有规则语义、不写 registry、
不复刻任何解析。命令：

```bash
python3 openspec/governance/check_project_gate.py --phase plan --change <name>
python3 openspec/governance/check_project_gate.py --phase closeout
```

- `--phase plan --change <name>`：只读 admission 检查。调用各语义 owner 的 scoped
  模式（Change Guidance 检查 Focus Card；specs checker 的 selected-change scope 检查
  delta header 与标题；reqs checker 的 planning scope 检查 reservation/冲突/retired
  reuse；native strict validation 检查 MODIFIED 场景保留）。合法的新 ID 输出为
  `reservation: <id> (capability)`——reservation 只是只读占号提示，非权威、不写文件；
  正式登记 registry 由 apply 任务完成。
- `--phase closeout`：运行六个 component checker 并聚合退出码；任一非零即整体非零，
  并点名失败的 checker。归档 agent workflow 在非零时停止；这是仓内 workflow 的
  确定性门禁，不阻断、不改变直接调用 native `openspec archive`。

正常校验路径 `0` = PASS，`1` = 有违规。注意：stderr 也可能包含 non-failing warning
（仍返回 0）；argparse usage error 属于命令用法错误，不属于 0/1 contract。

**退出码必须直测**：普通管道如 `cmd | tail` 只返回最后一个命令的退出码，会掩盖上游
checker 的非零结果。验证时直接读取命令自身的 exit code（例如 `echo $?` 或脚本内
`subprocess.run(...).returncode`），不要用管道产物判断通过与否。

`config.yaml` 的 `rules.tasks` 把归档前门禁固化为每个 change 的硬性收尾 task。
