# 00 - Baseline And Audit Contract

> 角色: 可复跑的当前快照与审计口径
> 快照: 2026-08-13 @ `a733d329902e779a108401f1305c937174f6e492`

## 基线结论

本仓库刚完成一次 alignment audit。该审计已经处理当前 main specs、CONTEXT 和治理之间的
已知权威冲突；本计划不重做它。新的问题是：**当前系统即使机械自洽，是否仍携带目标拓扑
不再需要的兼容面、旧名、旧实现与过期证据。**

快照数据用于估算和复跑，不是删除 KPI：

| 指标 | 快照 |
| --- | ---: |
| `deep_research_harness/` tracked files | 610 |
| production `src/` tracked files | 188 |
| production Python LOC | 33,366 |
| tests tracked files | 287 |
| pytest `test_*.py` modules | 220 |
| tests Python LOC | 75,413 |
| main specs | 49 |
| registered requirement IDs | 393（4 retired，0 orphan） |
| active OpenSpec changes | 0 |

计划建立前，五个项目 checker、requirement-to-test coverage、`openspec doctor` 和 49 份 strict
spec validation 均通过。它们证明结构与既定规则自洽，不证明每条既定规则仍值得保留。

## 审计范围

### 主要范围

- `deep_research_harness/src/deerflow_deep_research/`
- `deep_research_harness/src_fake/deerflow_deep_research_fixtures/`
- `deep_research_harness/tests/`
- `deep_research_harness/evals/`
- `deep_research_harness/config/`、`scripts/`、`run/`、当前 docs 与 entry README
- `openspec/specs/`、`config.yaml`、agent-charter、policies、governance、guardrails

### 仅按直接消费者进入范围

- 根 entry docs、`.github/workflows/`、profiles、root config；
- 只有当它们直接调用、挂载、发布或约束 `deep_research_harness/` 时才检查。

### 排除

- `deerflow/` 源码；
- `openspec/changes/archive/` 和 `_backlog/_done/` 的文字统一；
- 本地 `.venv`、`.reports`、cache、凭据与未跟踪运行数据；它们只在明确数据迁移时做不读
  内容的存在性/范围确认。

## 候选分类

每个候选只能在拿到证据后进入以下一种 disposition：

| Disposition | 含义 | 最低证据 |
| --- | --- | --- |
| `retire` | 当前没有合法消费者，目标实现已拥有行为，可直接删除 | current import/call/config scan + focused negative test |
| `migrate-then-retire` | 有 public、persisted 或 cross-boundary promise | consumer/data inventory + cutover + recovery + post-cutover evidence |
| `rename` | 语义不变但当前名称错误或多义 | canonical term decision + all current consumers + compatibility grade |
| `guard-retained` | 内容只用于阻止旧路径复活 | planted/known violation 能被检测；guard scope 不能绕过 |
| `historical` | 当时事实，已不参与当前入口 | current routes 不依赖其内容；必要链接仍可导航 |
| `rejected` | 调查后确认仍是当前必要能力 | owning contract、消费者和证据明确；记录为何不是残留 |
| `decision-required` | 两个目标仍可行，证据不足以选择 | 决策 authority、未知项和下一调查明确 |

不允许使用永久 `keep-for-now`。暂时不能决策时必须写明缺少哪项证据、谁决定、何时重查。

## 表面等级

仓库没有统一兼容等级时，审计使用以下内部比较，不要求产品采用这些标签：

| 等级 | 示例 | 删除要求 |
| --- | --- | --- |
| Public / persisted | reflected tool schema、Bundle State、配置格式、evaluation JSON schema、参与者可见 closed enum | 明确消费者、数据、版本/cutover、失败恢复和授权 |
| Declared cross-boundary | graph/runtime request、node-agent request、fixture/production package seam、Docker/CI mount | owner、所有消费者和协调变更边界 |
| Module-private | helper、private class/function、内部文件名 | focused import/call evidence；保持上层行为 |
| Assembly/wiring | recipe composition、script wiring、Make target | 可自由重塑，但不得改变更高等级承诺或验证选择 |

## 审计单位

以 **authority cluster** 而不是单个命中为单位：

```text
owning requirement
  + typed/public/persisted contract
  + writers and consumers
  + production path and entry surface
  + behavioral and negative evidence
  + registry / docs / glossary projections
```

一个 cluster 内任何一项仍需要旧表面，都不能宣布删除闭环。

## 可复跑扫描

以下命令只生成候选，不直接产生 finding：

```bash
git rev-parse HEAD
git ls-files deep_research_harness

rg -n -i \
  'legacy|deprecated|compatib|fallback|alias|former|old-root|retired|superseded|temporary|transitional' \
  deep_research_harness openspec/specs openspec/agent-charter openspec/policies openspec/governance \
  --glob '!**/__pycache__/**' --glob '!**/.venv/**' --glob '!**/.reports/**'

rg -n -i \
  'phase agent|md controller|full_fake|deerflow_research|research session|run session' \
  deep_research_harness openspec/specs \
  --glob '!**/__pycache__/**'
```

每个命中必须补充：是否当前 tracked source、是否由生产入口可达、是否序列化/公开、是否只在
测试或历史中、owning requirement、消费者、目标术语/路径和 proposed disposition。

## Rot 指标

本计划只跟踪能改变删除决策的指标：

- 当前公开/持久化表面中的 deprecated/compatibility 分支数量；
- canonical concept 与 current alias 数量；
- active negative guard 的最近已知 violation detection；
- tests/assets/scenarios 中没有 current consumer 或 selector 的登记项；
- current docs/entry routes 指向 historical/superseded record 的数量；
- structure/requirement exception baseline 是否只减不增。

指标是健康投影，不是健康本身。产品增长导致的合理新增必须记录 owner 和它退休了什么，或
接受的净增长与复核触发条件。

## 审计关闭条件

P0 审计阶段在以下条件成立时关闭：

- candidate register 覆盖上述范围内的所有高信号命中；
- 每个候选至少有 surface grade、owning cluster、current consumers 和下一证据；
- 当前 entry surface 与 persisted schema 已形成有限清单；
- 没有因字符串相似把不同概念合并，也没有因测试绿色把旧行为自动保留；
- 首个 OpenSpec change 可以从一个最小、独立、可回滚的 cluster 开始。

