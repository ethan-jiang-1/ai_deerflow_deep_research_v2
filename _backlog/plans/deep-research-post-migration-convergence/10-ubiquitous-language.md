# 10 - Ubiquitous Language

> 角色: 当前领域语言收敛路线
> 方法: `domain-modeling`；架构切换边界由 `keel` 补充

## 目标

“一个术语多个说法”需要先拆成两类问题：

1. **同义词泛滥**：同一概念在 glossary、class、field、prompt、spec 和 test 使用不同名称；
2. **概念挤压**：同一个词被用于事实、载体、执行机制或投影等不同概念。

目标不是让所有字符串相同，而是让每个概念有一个 canonical term，并让确实不同的概念保持
边界。例如 `LLM-Bearing Node`、`Node Cognitive Control Program` 和 `Deterministic Control
Boundary` 是三个相关但不同的概念，不能全部机械替换为 `Node Agent`。

## 词典权威

仓库已有三个 bounded contexts：

- root `CONTEXT.md`: DeerFlow Host；
- `deep_research_harness/CONTEXT.md`: Deep Research Product；
- `openspec/CONTEXT.md`: OpenSpec Governance。

产品术语只在 Deep Research Product glossary 定义；OpenSpec 术语不进入产品模型，Host 术语不
冒充下游产品身份。`CONTEXT.md` 只保留术语定义和 `_Avoid_`，不得承担 requirement、迁移步骤、
运行状态账本或大段设计论证。已存在的非词典章节是 review candidate，不因格式偏好自动删除；
只有确认其事实由 spec/ADR 拥有且 current readers 已重路由后才移动或删减。

## 首批术语 cluster

| Cluster | 当前观察 | 需要锁定的 canonical distinction |
| --- | --- | --- |
| Node cognition | glossary 使用 `LLM-Bearing Node` / `Node Cognitive Control Program`；生产文件和模型策略仍使用 `phase agent`；代码广泛使用 `NodeAgent*` | product identity、cognitive program、runtime bridge/request 和旧 mechanism name 各自是什么 |
| Run authority | current model 是 `Deep Research Run` + `Run Bundle` + Bundle-local `Research State`；current specs/tests 仍有 `research-run-session` / `research-session-lifecycle-binding` 名称 | Run、Bundle、State、Run Observation、compatibility binding 的唯一含义 |
| Fixture composition | current recipe 输出 `fixture | mixed | all_real`；persisted enum 仍含 `full_fake`，demo method 仍叫 `bind_full_fake` | fixture evidence、mixed test composition、production recipe 和 retired wire value |
| Observation/diagnosis | `Run Observation` 已替代 retired session store，但 specs/test filenames 仍以 session 命名 | authoritative State、Bundle-local observation、external observation、diagnostic projection |
| Product entry | Dedicated Agent + reflected tool 是 current user route；demo CLI/TUI/workbench/eval 是 operator/evaluation surfaces；Primary User TUI/local-first 标为 dormant | current product route、operator tool、evaluation interface、historical/dormant direction |
| Evaluation | Node/Flow Evaluation Run、Workspace、Bundle、Review Record 与 Deep Research Run Bundle 名称接近 | 每个 evaluation artifact 的 owner、生命周期及与 product Bundle 的禁止等同关系 |

## 决策记录格式

每个 cluster 在实施 change 前形成一张有限表，不创建新的永久术语 registry：

| Concept | Canonical term | Avoided aliases | Owning contract | Code symbols/surfaces | Compatibility action |
| --- | --- | --- | --- | --- | --- |

结论同步回 existing glossary、owning spec、代码和测试。工作表随 change 归档为决策证据，不成为
第四个词典。

## 判断规则

### 同义词

- 选择一个能够表达领域责任而非偶然机制的 canonical term；
- 旧词进入 `_Avoid_`，但只在对当前读者有真实消歧价值时保留；
- private symbol/file 可以原子 rename；序列化字段、enum、CLI text、model-facing policy 需先按
  compatibility grade 决定迁移；
- 不保留永久 alias 只为让旧测试继续通过。

### 多义词

- 先按 fact authority、writer、container、projection 和 lifecycle 分开；
- 若两个概念确实不同，分别命名，不追求一个万能名词；
- `manager/service/controller/session/context` 等泛词必须说明 jurisdiction，否则作为重命名候选；
- “phase”可以是当前 logical phase，不代表 `phase agent` 仍是正确 product identity。

### 测试语言

- 测试名称和 assertion 应描述行为/invariant，而不是退休的类名或实现手段；
- 只有负向测试可在名称或 fixture 中使用旧词，并明确 `retired/legacy/rejected` 意图；
- 模型策略/prompt 的词语属于 AI-facing behavior，不能当作纯注释 rename。

## 已知高信号冲突

1. `agents/phase_prompt.py`、`agents/policies.py`、`agents/factory.py`、
   `runtime/node_agent_bridge.py` docstrings 和 `resources/node_agent/runtime_policy.md` 仍称
   `phase agent`；current glossary 已把 `Phase Agent` 视为退役参考说法。
2. `tests/unit/test_phase_prompt.py` 明确断言 `Deep Research Phase Agent`，因此当前测试在保护旧
   AI-facing identity，而不只是旧文件名。
3. `research-run-session` main spec 的当前正文实际约束 `RunObservation*`，生产 session store 已被
   负向测试证明不存在；capability 名与 current owner 可能已经分离。
4. `research-session-lifecycle-binding` 当前 spec 几乎全部描述旧 binding 不得拥有行为，可能是
   compatibility guard capability，而不是 current product capability。
5. `FULL_FAKE` 是 persisted/public projection 候选旧值，而 current recipe 只产生 `fixture/mixed/all_real`。

以上都是候选，不是本计划直接授权的 rename/delete。

## 同步顺序

```text
resolve concept and owner
  -> decide compatibility/cutover
  -> update owning delta and ADR only when needed
  -> update typed symbols / serialized surfaces / model policy
  -> update behavior tests and negative guards
  -> update CONTEXT glossary and current docs
  -> residual scan with explicit historical/guard allowlist
```

先改 glossary 再等待代码追赶会制造新的双名期；先改代码却不处理 public/persisted name 会静默
破坏消费者。除纯 private rename 外，同一 cluster 应在一个 OpenSpec change 中纵向闭环。

## 完成条件

- 每个首批 cluster 有清楚的 canonical distinction 和 owner；
- current production、spec、test 和 participant/AI-facing surfaces 不再使用未批准 alias；
- `_Avoid_` 只保存仍有消歧价值的旧词，不变成历史词墓地；
- 不同 bounded context 没有复制对方定义；
- residual old-term matches 全部落入 compatibility input、negative guard 或 historical evidence；
- 后续新增 concept 必须说明它退休了什么，或记录净增长、owner 和 review trigger。

