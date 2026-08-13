# Alignment Audit 40 - Verification Record

> 审计日期: 2026-08-12
> Git 快照: `65df2571108cc6b4b81f55d3ba8542786a810b39`
> 执行环境: macOS / Python 3.12.10 / `UV_OFFLINE=1`

返回[总览](alignment-audit-00-current-state.md)。本文件记录可复现的绿色基线及每个门禁
的证明边界；它不是对 A-001 至 A-009 的替代论证。

## 快照与工作范围

写作前确认：

```text
branch: master, ahead of origin/master by 45 commits
HEAD:   65df2571108cc6b4b81f55d3ba8542786a810b39
commit: chore(backlog): close Plan CLS-035 (openspec-agent-charter-topology-flattening)
deerflow gitlink: 66b9e7f21212490cf92fafac137542b9deb06615
active OpenSpec changes: 0
```

本次未读取或修改 `deerflow/` 源码。全量验证只运行应用及仓库自有治理入口。

## 完整应用门禁

执行：

```bash
cd deep_research_harness
UV_OFFLINE=1 make verify
```

最终退出码为 0。分项结果：

| 阶段 | 结果 |
| --- | --- |
| Requirement registry | 392 registered，4 retired，0 orphan；main specs / active deltas 661 occurrences |
| Project spec governance | 49 main spec files，0 violations |
| Architecture governance | passed |
| Agent Charter governance | passed |
| `uv lock --check` | passed，226 packages resolved |
| Ruff lint | passed |
| Ruff format | 474 files already formatted |
| Test asset coverage | passed |
| Requirement-to-test coverage | passed |
| Fast lane | 2494 passed，3 deselected，2 warnings，69.10s |
| Integration lane | 237 passed，4 skipped，32 deselected，16 warnings，287.52s |
| Workflow lane | 35 passed，2784 deselected，42 warnings，17.28s |

测试资产门禁报告：

```text
13 incidents
11 real nodes
7 critical faults
8 model-workflow nodes
400 central claims
2770 deterministic tests
fast=2494, integration=241, workflow=35, live=49
```

这里 `integration=241` 是选中资产数；pytest 最终为 237 passed + 4 skipped。

## Skips 与 warnings

4 个 skip 均来自 `tests/integration/test_gateway_identity.py`，原因是：

```text
real Gateway app stack is unavailable
```

它们不使确定性门禁失败，但意味着本次没有获得真实 Gateway app stack 的集成证据。

warnings 分两类：

- fast lane 的 2 个 Pydantic deprecation warning：测试通过 instance 访问
  `model_fields`；
- integration/workflow 的 Pydantic serializer warnings：测试 runtime context 的
  shape 与声明的 `none` 预期不完全一致。

本审计没有把 warnings 升级为 alignment finding，因为没有观察到行为失败，且用户要求
的是四层对齐现状。它们仍应留在普通技术债账本中，不应被“all passed”隐去。

## OpenSpec 验证

执行：

```bash
openspec list --json
openspec doctor --json
openspec validate --specs --strict
```

结果：

- `list`: `changes: []`，root 为当前仓库；
- `doctor`: `healthy: true`，无 status/error；
- strict validation: 49 passed，0 failed。

main spec 机械盘点：

| 指标 | 数量 |
| --- | ---: |
| main spec files | 49 |
| `### Requirement:` headings | 410 |
| `#### Scenario:` headings | 1206 |
| registered requirement IDs | 392 |
| alive / retired IDs | 388 / 4 |
| main spec / active delta ID occurrences | 661 |

410 个 requirement heading 与 388 个 alive ID 不必一一相等：一个 ID 可以拥有多个
requirement block，一个 block 也可能引用同 capability 的多个 ID。门禁验证的是项目约定
的 ID 所有权与引用，不是标题数相等。

## 每条绿色结果能证明什么

| 绿色结果 | 能证明 | 不能证明 |
| --- | --- | --- |
| OpenSpec strict 49/49 | artifact 可被 OpenSpec 严格解析，结构有效 | 两份 main specs 没有语义矛盾；路径描述符合当前 Git topology |
| doctor healthy | OpenSpec 自身关系/根状态健康 | config 的自然语言没有 V1 残渣 |
| req registry green | ID 已注册、未 orphan、retired 使用受控 | requirement 的每个 scenario 已被正确实现 |
| req coverage green | 每个 alive ID 至少在某个含测试的 docstring `@impl` 中出现 | 注解与具体 assertion 语义绑定；production 每个文件都反向标注 owner |
| architecture green | manifest 当前声明的路径/layer/import 规则通过 | manifest 声明的 upstream roots 真正存在；真实 gitlink 得到保护 |
| charter green | policy registry、Focus Card 与条件表形状满足 checker | change 选择了语义上正确的 policy；Charter 路径词汇真实 |
| 2766 passed tests | 当前被选择的 deterministic behavior 无失败 | 未选择的 live/release/Gateway 行为已验证；所有 spec 互相一致 |

## Traceability 边界复核

`openspec/governance/check_project_req_coverage.py:39-70,138-152` 的算法是：

1. 遍历 `tests/**/test_*.py`；
2. 文件中只要存在 test function，就收集 module/class/function docstring 中的
   `@impl` IDs；
3. 比较 main-spec alive ID set 与收集到的 ID set。

它不会解析 test assertion 的含义，也不要求注解必须位于实际证明该 requirement 的
test function 上。production 注解存在时会校验 unknown/retired，但不是所有 production
文件的必填项。本次盘点 `src/deerflow_deep_research` + `scripts`：

```text
176 Python files total
130 files with @impl
46 files without @impl
```

46 并不等于 46 个 bug；`__init__.py`、纯适配或辅助代码可以由更高层 owner/测试覆盖。
它只说明“实现反向到 spec”不是全局逐文件机器强制。完整分析见
[10 / A-009](alignment-audit-10-spec-implementation.md#a-009---p2---coverage-gap-green-requirement-coverage-is-not-semantic-traceability)。

## 审计期间的基线变化

审计早期曾在一个较早 HEAD 观察到 `check_agent_charter.py` 失败，随后仓库被外部提交
推进，`c4efe6f` 恢复 Charter authority line；当前最终快照 `65df257` 已通过完整门禁。

因此：

- 早期失败不列为当前 finding；
- 所有当前数字均以最终快照重新执行的 `make verify` 为准；
- 后续实现整改前应重新绑定新的 HEAD，不应把本文件的绿色结果无条件外推到未来提交。

## 文档交付校验

系列写完后应再执行：

```bash
git diff --check
git status --porcelain=v1 --untracked-files=all
```

并检查同目录相对链接。该校验只验证本次 Markdown 交付质量，不改变上述应用验证结果。
