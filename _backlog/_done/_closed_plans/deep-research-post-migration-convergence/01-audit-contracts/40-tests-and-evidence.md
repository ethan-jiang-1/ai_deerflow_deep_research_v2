# 40 - Tests And Evidence

> 角色: 测试、fixture、scenario、evaluation 与治理资产的减法规则
> 结果落点: `74` 及所有 findings 尾部的“保留负向护栏”；测试减法随 owning Candidate 实施

## 目标

测试清理不是“删除重复测试”，而是让证据只证明 current behavior 和必要的旧路径拒绝。历史实现
已经被替换时，测试不能继续通过旧类名、旧文案、旧 fixture shape 或旧 registry 行把它变成事实上的
兼容承诺。

## 测试 disposition

| 类型 | 默认处理 |
| --- | --- |
| Lowest responsible behavioral evidence | 保留；必要时迁到 target owner 并改为 canonical language |
| Public/persisted contract evidence | cutover 前保留；迁移后证明 target 与 old-input behavior |
| Negative anti-resurrection guard | 保留并明确 `retired/rejected`；验证 planted violation |
| Implementation-shape assertion | target behavior 已覆盖后删除或重写，不保护私有类名/调用次数/文件布局 |
| Duplicate projection test | 保留最接近 fact owner 的一条；其他层只测自己的映射责任 |
| Historical incident regression | 若 current invariant 仍适用，改用 current route；否则归档/删除并记录替代证据 |
| Uncollected/suspended asset | 必须有 owner、restart trigger 和执行路径；否则退出 active test tree |
| Registry/claim row | 只在 selector、owner、risk 仍 current 时保留；禁止 orphan metadata |

## 首批审计对象

### Old terminology assertions

`tests/unit/test_phase_prompt.py` 当时断言已退役的 AI-facing actor identity。若 canonical
identity 改为 Node Cognitive Control Program/Node Agent runtime worker，该测试必须与生产 policy 同批
迁移；不能只 rename 文件而继续断言旧字符串。

### Legacy capability tests

`tests/domain/test_node_agent_capability.py` 证明 `NodeExecutionRequest` 默认 legacy 和 legacy/ref
组合规则。若 production constructors 已全部 required，测试目标应收敛到“missing/invalid capability
fails before agent work”，而不是保留无生产消费者的默认路径。

### Full-fake compatibility

current tests 同时包含：

- current state 不输出 `full_fake`；
- public skill/entry 拒绝 `full_fake`；
- demo transport 方法仍名为 `bind_full_fake`；
- old payload/fixture compatibility。

必须区分 current rejection guard、persisted old-data reader 和只保护旧命名的测试。迁移未关闭前不能
把它们一起删除。

### Session/binding tests

`test_retired_run_session_store_has_no_compatibility_module` 是明确 anti-resurrection guard；它不是旧测试。
相反，以 `test_run_session_contract.py` 命名却实际测试 `RunObservation*` 的 current behavior，是术语迁移
候选。RES compatibility tests 只有在 old binding consumer/data 已关闭并把必要 rejection invariant 移到
current owner 后才能减少。

### Suspended and empty scaffolding

`tests/scenarios_suspended/evh_024_release_acceptance.py`、空 `.gitkeep` 测试目录和不被 Make/CI/pytest
选择的材料需逐项确认：

- 是否有明确 owner 和 restart trigger；
- 是否仍被 current docs/registry 引用；
- 是否应转到 backlog/reference 历史材料；
- 若没有未来决策价值，是否可直接删除。

不把“未收集”自动等同于无价值，也不让 suspended 资产无限留在 active test tree。

### Evidence registries

`tests/assets/`、`tests/scenarios/` 和 evaluation control 资产具有可执行 joins，不能按体量整体裁剪。
每次 owning behavior 退役时同步：

- central evidence claim；
- requirement impact / `@impl`；
- incident/fault/node/workflow/cognitive-program row；
- exact selector 与 lane expectation；
- scenario fixture、provider shape、release attestation scope。

若 registry 行只引用已删 selector或已退役 requirement，checker 必须失败；删除后不能留下“绿色但空输入”。

## 证据保存规则

行为证据要从 implementation identity 中解耦：

```text
old implementation test
  -> identify protected invariant / failure
  -> prove target owner covers invariant
  -> plant old-path violation or stale input
  -> delete old implementation assertion
```

不能先删测试再声称 `make verify` 绿色证明无回归；suite 变小本身不是行为证据。

## Negative-control freshness

每个保留 guard 记录：

- guard owner 和 protected invariant；
- known/planted violation；
- 最后一次确认能 fail 的 change 或测试；
- scope escape 检查；
- 下次触发（相关 path/schema/registry 变化）。

执行方式由具体 OpenSpec change 的 TDD/tasks 决定。本 plan 只要求证据存在，不伪造 red run。

## 测试删除完成条件

每个删除批次必须满足：

- owning behavior 和 negative path 在 target seam 有明确测试；
- 删除的每个 selector 已从所有 registry/join/CI lane/docs 中移除；
- 保留的 old-term match 明确是 old-input/anti-resurrection，不是 current identity；
- test-assets checker 有非空 discovery 或 known-violation smoke，不能空扫描假绿；
- focused red-before-green、相关 lane 和 `make verify` 通过；
- live/release/postgres/real-Gateway 未运行时明确记录证据限制；
- 记录净删除的 tests/fixtures/claims，但不把数量作为质量结论。

## 最终 suite 复核

计划末尾重新检查：

- lane 互斥和收集完整性；
- orphan selector、orphan `@impl` 和 retired requirement evidence；
- duplicate behavior across unit/contract/integration/workflow；
- fixture source 与 production wheel 隔离；
- current entry surface 至少有一条真实 handoff evidence；
- historical release artifacts 不被当前 suite 当作 freshness proof。
