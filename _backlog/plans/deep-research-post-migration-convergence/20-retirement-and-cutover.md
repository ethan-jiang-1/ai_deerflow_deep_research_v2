# 20 - Retirement And Cutover

> 角色: public、persisted、cross-boundary 表面的迁移与删除闭环

## 删除判定

一个旧表面只有在下面五个问题都有答案时才能退役：

1. **Target**: 哪个现行 owner/contract 接管其必要行为？
2. **Consumers**: 所有 tracked 和可合理发现的外部消费者是谁？
3. **Data**: 是否存在 persisted Bundle/config/evaluation/diagnostic 数据仍携带旧值？
4. **Negative path**: stale、partial、duplicate、rollback、restart、replay 或未知旧数据怎样处理？
5. **Evidence**: 什么证明新路径生效、旧路径关闭且 guard 能检测复活？

任何一项未知都只能标记 `decision-required`，不能用兼容 fallback 无限延期，也不能直接 clean break。

## Cutover 记录

每个 public/persisted/cross-boundary 候选在 proposal/design 中回答：

| 项 | 内容 |
| --- | --- |
| Surface | 精确字段、enum、配置键、export、命令、路径或接口 |
| Grade | public/persisted、cross-boundary、private 或 wiring |
| Fact/decision authority | 谁定义事实，谁批准 breaking cutover |
| Accountable owner | 谁负责语义、生命周期和升级失败 |
| Current consumers/data | 代码、测试、entry、已知本地/外部数据范围 |
| Target | 唯一新表面及 preserved behavior |
| Strategy | clean break、read-old/write-new、versioned migration 或 explicit rejection |
| Recovery | detection、owner、rollback/forward repair、terminal invariant、evidence |
| Old-entry closure | 删除入口、alias、writer、reader、docs、tests 和 registry 的条件 |

## 首批切换候选

### R1 - Legacy node capability binding

当前 `NodeExecutionRequest` 默认 `capability_binding="legacy"`，但已扫描到的 17 个 production
request builders 都显式使用 `required` capability。需要确认：

- 是否还有 reflection、fixture、evaluation 或外部 import 直接构造默认 request；
- request 是否被持久化或只跨 graph/agents 内部边界；
- 删除 `legacy` 后，缺 capability 是否统一 fail closed；
- 现有 legacy-default 测试应改为 missing-capability rejection，还是保留兼容 reader。

若没有消费者/data，这是优先级最高的最小退役 slice；若存在，先迁移构造者并给旧输入明确拒绝
结果，不保留隐式默认。

### R2 - `full_fake` implementation mode

current recipe 只产生 `fixture | mixed | all_real`，但 `ImplementationMode.FULL_FAKE`、demo
`bind_full_fake` 名称以及 public/skill rejection lists 仍存在。这个表面可能进入 Bundle State 和
外部投影，因此必须先：

- 枚举 current schema readers、retained bundle fixtures 与 public output；
- 决定旧 `full_fake` persisted value 是 read-only legacy、明确 unsupported，还是可安全迁成
  `fixture`；不能假设两者语义等同；
- 保持 current public route 永远不选择 fixture implementation；
- 删除旧 writer 后再考虑删 enum value/reader；负向 guard 可以继续构造旧 wire payload。

### R3 - Research Session / lifecycle binding compatibility

production `domain.run_session` 和 `runtime.run_session` 已不存在；current code 使用 Bundle-local
`RunObservation*`。但 `research-run-session` 与 `research-session-lifecycle-binding` main specs、RUS/RES
IDs 和一组测试仍保留 compatibility semantics。需要分别决定：

- `research-run-session` 是否应迁为 current `run-observation` capability；
- `research-session-lifecycle-binding` 是否还有真实 reader/data，还是其重要不变量应归并到 Run
  Bundle/observation owner 后退役整个 capability；
- 旧 binding/data 的 rejection 是否需要永久 guard，guard 放在哪个 current owner 下；
- stable requirement IDs 按 registry 规则保留/retire，不通过复用 ID 假装 rename。

### R4 - Current and dormant entry surfaces

Dedicated Agent + reflected `deep_research` tool 是 current recommended user route；demo CLI/TUI、
session workbench、cognitive evaluation 是不同 operator/evaluation surfaces；Primary User TUI 与
local-first route 是 dormant。必须逐个确认：

- entry 是否仍被当前 README/Make/config/CI 支持；
- 它服务 Primary User、operator、contributor 还是 evaluator；
- 是否复制另一入口的 lifecycle/control authority；
- dormant concept 是否只有历史价值，还是仍污染 current code/config/tests；
- 删除一个 entry 后，其唯一行为证据由哪个 lower seam 保留。

不能因为不是 primary route 就删除 operator/evaluation tool，也不能因存在测试就默认继续支持。

### R5 - Configuration and path compatibility

`configure.py`、deployment specs、profiles、Docker/CI 和本地 launcher 中的 legacy path/config 检查
可能同时包含有效迁移 reader与已无必要的 fallback。每一项需标明：

- 它是读取旧配置、拒绝旧配置，还是仍写旧配置；
- 已知安装基线和支持窗口；
- dry-run/backup/rollback 能否覆盖 cutover；
- 删除 reader 是否会让现有部署无法诊断或升级。

## 负向路径

每个 cutover 至少考虑实际适用的情况：

- 旧数据存在但新 writer 已部署；
- 新旧字段/配置同时存在且冲突；
- migration 中途失败或进程重启；
- stale client 继续调用旧入口；
- duplicate/replay 导致第二次迁移；
- old reader 被删除后仍有 residual import/config；
- rollback 回到不能读取新数据的版本。

不适用时写理由，不为 private reversible rename 发明状态机。

## Guard 要求

- 每个退役入口至少有一个 known/planted old input 能证明被拒绝或不可导入；
- guard 的扫描范围不能通过把代码移动到未扫描目录来绕过；
- compatibility exception baseline 默认 shrink-only；新增项需有 authority、owner、reason、date、
  narrow scope 和 removal condition；
- quiet guard 不因长期未触发而自动删除；先证明它仍能捕获 planted violation。

## 完成条件

- 所有 public/persisted/cross-boundary 候选有明确 cutover decision；
- target consumer 和 data scope 可枚举，或 residual external risk 被 decision authority 明确接受；
- old writers 和 active entry surfaces 全部关闭；
- read-only legacy reader 若暂留，有固定支持边界和删除触发条件；
- recovery 收敛到唯一 terminal invariant，不靠永久 alias 或 silent fallback；
- post-cutover evidence 同时证明 target path 和 old-path rejection。
