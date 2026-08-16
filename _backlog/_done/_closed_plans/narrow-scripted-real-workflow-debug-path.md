# Plan: 窄而真的三波工作流调试路径

> 类型: 设计 / 复盘（postmortem） | 更新: 2026-08-16

## 背景 / 现状

当前调试路径两极分化：

```
make demo-scripted                 make demo-real-scripted
fixture adapters                   all-real adapters + live model/web
零凭据、很快                       真实问题、慢且付费
图能走通                           三波实际动作能走通
         \                         /
          \       缺失            /
           `-- 窄 scripted-real --'
```

用户需要的不是一份浅层的 topology 演示，而是每次改动后能快速确认：真实 Topic Planning 产生最小
topic，真实 Wave0 执行一个受控 worker，真实 Wave1 接受和评审一份证据，真实 Wave2 综合一次证据，
并且这些动作经由真实的 prompt、bridge、parser、artifact writer、work-unit ledger、gate 和状态机。

当前 `SCRIPTED_REAL_WORKFLOW` 已是测试证据分级的正式概念：真实生产 loop 加短小确定的模型/工具
响应。`ScriptedChatModel` 和 `ScriptedTool` 也已存在，但只服务分散测试，没有完整的 operator
调试入口。`fixture-graph` 则明确替换所有 node adapters，不能替代本计划。

## 决策 / 方案

### 1. 新增独立的 operator-only command，而不是给真实产品加降级开关

建议命名 `make debug-scripted-real-workflow`，实现为一个单独的 composition root 和显式 execution
profile。它不得接受 `demo-real` 的 mode flag、不得读取 `.env`、不得调用真实模型或网络，也不得
作为当前 Primary User route 的一部分。

这样保留两个重要事实：

- `make demo-real` 仍然是 all-real 真机 smoke，不会因为 debug 选项悄悄变成假外部依赖；
- debug command 的 adapter 全为生产 REAL，真实性写为 `SCRIPTED_REAL_WORKFLOW`，而不是冒充
  `LIVE_REAL_DEPENDENCIES` 或笼统标作 fixture。

### 2. 只缩外界与工作量，不缩生产控制路径

保留的真实部分：

- bootstrap、HITL 自动确认、topic planning、Wave0、Wave1、Wave2、HITL2、readiness、final delivery 的生产 adapter 和路由；
- `RuntimeNodeAgentBridge`、production prompts、输出 normalizer/parser、artifact writer、WorkUnitStore、Bundle lifecycle、real gate definitions、Event Journal；
- 所有实际的 candidate admission、validation、review 和 terminal projection。

替换的仅是不可控外界：

- 模型用固定响应序列的 `ScriptedChatModel`；
- `web_search` / `web_fetch` 用固定、最小、无敏感内容的 `ScriptedTool`；
- 时钟、ID 和随机性固定；
- 不读取模型或 Tavily 凭据，不联网。

基线 case 必须强制以下窄预算，不是“希望模型少做一点”：

| 阶段 | 必须动作 | 上限 |
| --- | --- | --- |
| Topic Planning | 生成覆盖一个固定问题的一 topic plan | 1 model response / 1 topic |
| Wave0 | 调用真实 source-intake worker 并接纳一份候选 | 1 WorkSpec / 1 scripted tool response |
| Wave1 | 调用真实 extraction worker，接纳一份新来源并完成两个 critic review | 1 WorkSpec / 固定 critic responses |
| Wave2 | 调用真实 synthesis，物化一条有 backing reference 的 finding | 1 synthesis response |
| 余下生命周期 | 自动通过 HITL2、readiness、final delivery 到终态 | 不进入 rerun 或 targeted-evidence |

所有脚本队列必须严格耗尽：缺少响应、意外的额外模型/工具调用、遗漏某波 action 都让 command
失败。这样“跑得通”不是只看 `execution_trace`，而是验证每个真实动作确实发生。

### 3. 命令输出要表明它证明了什么、没有证明什么

完成输出包含：`composition=all_real_adapters`、`authenticity=scripted_real_workflow`、无网络/无凭据
断言、每波 action counter、Bundle id、Event Journal 检查入口和总耗时。它在 operator log 计划完成后
也应输出日志入口；在此之前最低限度显示逐阶段动作和 Journal sequence。

它只证明生产控制路径对固定合法资料的集成正确，不能证明：

- 真模型是否能理解或遵守 prompt；
- Tavily/网页可用性、真实网页质量、延迟、成本或限流；
- 多 topic 的并发、宽范围资料覆盖、深度研究质量；
- `targeted_evidence`、rerun、provider recovery 等非 happy-path 分支。

这些仍由现有单元/工作流 tests、分阶段 live canaries 和预算明确的 `demo-real` 负责。

### 4. 把 repair 与 targeted 分支做成独立的小 case

基线不得用“为覆盖 repair 而故意失败”的方式拉长运行。第二阶段可增加命名 case：

- `wave0-repair`: 一次非法初始输出后一次合法 repair；
- `wave1-review-invalid`: 一份非法 critic 输出，断言 BUG-029 要求的安全诊断；
- `wave2-targeted`: 一次明确的 unresolved gap，经真实 targeted-evidence 后回到 Wave2。

每个 case 只验证一个分支，单独有 budget、预期 route 和 action counters。它们不允许默认在基线
command 中串行执行。

## 实施顺序与证据

1. 新建独立 OpenSpec change。primary owner 选 `runtime/research.py` 的 recipe/composition 边界，
   临近边界是 `RuntimeNodeAgentBridge` capability 注入、测试 fixture package 和 operator command；
   不修改 `deerflow/`。
2. 先编写基线红测，在真实 adapters 下运行固定 Bundle，断言真实 Wave0/Wave1/Wave2 action counter、
   accepted artifacts、两个 Wave1 reviews、Wave2 finding backing ref、gate route 和完成终态。旧代码没有
   这个 entrypoint，因此测试先红。
3. 添加受控 scenario catalog：固定 profile、单 topic plan、最小合法 Wave0/Wave1/Wave2 JSON、critic
   JSON、final delivery JSON、模型/tool call queue。将脚本放在现有非生产 `src_fake` / test fixture
   边界，生产包只依赖 protocol，不发现这些脚本。
4. 实现 operator command 和单独 composition root。它显式构造 all-real adapters、real gates、真实
   persistence 与 scripted capabilities；不向 `ResearchGraphRecipe.all_real()` 或 `make demo-real` 添加
   用户可选的 fake mode。
5. 添加 CLI contract test：零 `.env`、零网络、脚本耗尽检查、少于 10 秒、输出真实性标签和每波动作。
   失败场景包括漏掉 Wave1 critic、额外工具调用、非法脚本输出和意外进入 targeted/rerun。
6. 将它作为针对 graph/bridge/gate 改动的本地快速调试命令，而不是替代 `make verify`。在稳定后，
   可作为 full-real 回归前必跑的十秒级前置证据。

## 风险 / 取舍

- [把脚本化误称真机] -> 输出和测试明确 `SCRIPTED_REAL_WORKFLOW`；live provider 行为仍需单独证据。
- [为了变快而绕过真实 node] -> 断言所有 adapters 为 REAL、真实 gate/ledger/artifact 都被调用；只允许替换外界 capability。
- [脚本 fixture 漂移，形成假绿] -> prompt/contract 改动触发 scenario 审核；模型和工具队列严格耗尽，缺少或额外调用都失败。
- [debug command 变成产品后门] -> 独立 Make target、无 `demo-real` flag、固定 case、operator-only 文档和零凭据/零网络断言。
- [一条 happy path 掩盖 repair] -> repair/targeted 各有小而独立的 named case，按正在诊断的 bug 选择运行。
- [速度目标被悄悄放宽] -> CLI contract 用可控时钟/timeout 证明小于 10 秒；超时是测试失败，不是跳过。

## 落地关联

本计划解决 BUG-031，并与 BUG-026 至 BUG-030 共用 Event Journal/未来 operator log，但不依赖日志
计划才能先落地。实施已产生 OpenSpec change `scripted-real-workflow-debug-path`（proposal/specs/
design/tasks 齐全，SCR-001..005 + PRS-019 登记）：2026-08-16 红测先行转绿，
`make debug-scripted-real-workflow` 落地（0.9 秒基线），三波 action proof 与 CLI contract 就位。
已有 `fix-active-demo-bundle-projection` change 的 scope 只处理活动 Bundle 投影，没有混入。

## Spike 验证结果（2026-08-16，`tests/integration/spike_scripted_real_workflow.py`）

已用 `ResearchGraphRecipe.all_real(work_unit_store_factory=…, node_agent_bridge_factory=<scripted>)`
+ `BundleGraphExecutor` + 公共控制入口 `run_deep_research(start → HITL1 确认 → resume)` 走通全图：

`bootstrap → hitl1 → hitl1 → topic_planning → wave0 → wave1 → wave2_synthesis → hitl2 → readiness → final_delivery → completed`，
**11 次模型调用 + 2 次 web_search、0 次 web_fetch、0.70s、零凭据零网络**，全部脚本严格耗尽，
terminal completed、2 条 work-unit records、final artifacts 发布。

实测发现（预算表按此修正）：

1. **模型响应必须带 `usage_metadata`（total/output tokens）**——`BudgetMiddleware` 无记账即判
   `usage_unavailable` 失败；脚本模型把 usage 一并固定即可。
2. **时钟不能冻结**：`AttemptRef` 要求 `created_at <= terminal_at`，且真实 wave0 节点硬编码
   `clock=lambda: datetime.now(UTC)`。结论：只固定 ID/随机性，时钟用真实时间（或与节点一致的推进时钟）。
3. **envelope 的 `app_config` 必须是带 local sandbox 配置的真 `AppConfig`**，否则
   `classify_work_unit_storage` 判 `provider_unrecognized`，bootstrap 存储不可用。
4. **wave1 语义底线与 plan 表格不同**：`WAVE1_MINIMUM_NEW_SOURCE_URLS = 2`——extraction 必须提出
   ≥2 个超出 wave0 基线的新来源 URL（原表格"一份新来源"应改为两份）。critic 输出必须与
   extraction 的 `source_ids`/`claim_id` 对齐（BUG-027 枚举：`trust_tier`/`materiality` 闭合值）。
5. **wave2 finding 的 `backing_refs` 必须是已接纳 submission ref（`h_`+43 字符 token），且当前工作
   树（BUG-028 缓解后）wave1 submission 不进入 accepted refs**——finding 需 back 在 wave0 ref 上，
   否则触发 repair。`gaps` 必须为空：`search_required` gap 会路由进 targeted_evidence，而当前
   targeted 路径会抛 `work_unit_gate_view_inconsistent`（BUG-028 待修），基线不得进入。
6. **readiness critic 的 `backing_claim_ids` 必须是已接纳 submission ref**，不是 claim id；verdict
   `ready_substantive` 且无 blocked 即 `pass`。
7. **final composer 输出 `conclusion_order`/`uncertainty_order` 是数组**，且只能包含 composer
   prompt 里给出的 plan 条目 id（`conclusion:N`/`uncertainty:N`），两个列表不得混用。
8. **真实 hitl2 节点是自主决策**（`recommend_hitl2_route`，不产生人机交互）——plan 的"HITL2 自动通过"
   即现状，基线只会有一次 HITL1 挂起；spike 保留了未来若 hitl2 恢复人工决策的 proceed 分支。
9. 脚本模型需要**占位符渲染**：wave2/readiness/composer 的合法 JSON 依赖运行时事实
   （accepted refs、plan 条目 id），从 prompt 文本中正则提取填充，不能全静态。

对实施顺序的影响：步骤 2 的红测应断言 11 次模型调用 / 2 次 web_search / 0 次 web_fetch /
2 条记录 / 两条 wave1 review artifact / wave2 finding backing ref ∈ accepted / completed 终态；
步骤 3 的 scenario catalog 以本次 spike 的 JSON 为最小合法基线（wave1 按 2 个新来源修正）。

