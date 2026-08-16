# Design: 窄而真三波调试组合

## Context

Spike（`tests/integration/spike_scripted_real_workflow.py`，2026-08-16）已验证全 REAL
adapters + 脚本能力的组合可以在 0.7 秒内走完 `bootstrap → hitl1 → hitl1(确认) →
topic_planning → wave0 → wave1 → wave2_synthesis → hitl2(自主) → readiness →
final_delivery → completed`。生产接缝全部存在：`ResearchGraphRecipe.all_real(
work_unit_store_factory=…, node_agent_bridge_factory=…)`、`BundleGraphExecutor`、公共
控制入口 `run_deep_research(start/resume)`、`RuntimeNodeAgentBridge` 的
`model_resolver`/`tools_resolver` 注入点。缺口是正式的 composition 归属、scenario
目录归属和 operator 入口。

## Goals / Non-Goals

**Goals**：一个零凭据、零网络、<10s 的 operator 命令；三波 action proof 红测；脚本
与生产包隔离；真实性标注与"证明什么/不证明什么"输出。

**Non-Goals**：不改生产图代码；不给 demo-real 加开关；不修 BUG-028 的 targeted 路径
（基线明确不进入）；不做 repair/targeted named case（第二阶段，依赖 BUG-028 修复）。

## Decisions

### 1. Scenario 剧本放 `src_fake`，composition 在 launcher（scripts/），测试复用两者

`src_fake/deerflow_deep_research_fixtures/scripted_real/baseline.py` 持有纯数据剧本
（固定问题、HITL1 确认文本、11 条带占位符的模型剧本、工具响应、每波预算声明），仅用
标准库，不触碰生产契约——`fixture_imports.production_contracts` 白名单原样成立。
`scripts/debug_scripted_real_workflow.py` 持有 composition（all_real recipe + scripted
bridge factory + 本地 envelope/adapter + 沙箱 provider 注册）与驱动/输出/`main()`；
scripts/ 是 presentation/launcher 层，`_demo_core` 已在此拥有 DPL-001 的"trusted
runtime composition boundary"，符合治理。测试经 `pythonpath = [".", "src_fake"]` 与
`_scripts_path` 模式（`tests/unit/test_demo_core.py` 先例）import 剧本包与脚本模块。

- 备选：composition 也放 src_fake —— 会要求把 `runtime.research`/`node_agent_bridge`/
  `bundle_graph`/`tool` 及 `deerflow`/`langchain_core` 全部加进 fixture 白名单，等于
  放开"fixture 不得触碰 runtime 组合权"的边界本身，被否。
- 备选：放生产包 —— 违反"生产包只依赖 protocol，不发现脚本"，且污染 Primary 边界。

### 2. 脚本模型 = 占位符模板模型，而非纯静态队列

wave2/readiness/composer 的合法输出依赖运行时事实（accepted submission refs
`h_…43`、composer prompt 的 plan 条目 id）。模型从本次调用收到的 prompt 文本中按
固定模式提取填充（`"wave0":["…"]`、`"submission_ref":"…"`、`conclusion:\d+` 等），
未命中即失败。纯静态 JSON 会因 hash 每次不同而假绿或误红。

### 3. 每波预算按 spike 实测修正 plan 表格

- 模型调用 11 次：hitl1 brief(1) + planning(1) + wave0(2: 工具调用轮 + intake) +
  wave1(2: 工具调用轮 + extraction) + 两个 critic(2) + wave2(1) + readiness(1) +
  composer(1)。
- 工具：2× `web_search`、0× `web_fetch`（脚本模型只发起 web_search）。
- wave1 extraction 必须给出 ≥2 个超出 wave0 基线的新 URL（`WAVE1_MINIMUM_NEW_SOURCE_URLS=2`），
  critics 与 extraction 的 `source_ids`/`claim_id` 对齐（BUG-027 闭合枚举）。
- wave2 finding 的 `backing_refs` 引用 accepted ref；当前工作树 wave1 submission 不进入
  accepted refs（BUG-028 缓解），故 back 在 wave0 ref 上；`gaps` 空，避免进入
  targeted_evidence（其 gate view 当前会抛 `work_unit_gate_view_inconsistent`）。
- readiness `backing_claim_ids` 必须是 accepted submission ref；verdict `ready_substantive`。
- composer 输出两个数组，只含 prompt 提供的条目 id，且两个列表不混用。

### 4. 时钟、ID 与 usage 的脚本化边界

模型响应的 `usage_metadata` 固定（BudgetMiddleware 要求 total/output tokens）。
ID/随机性可固定（token factory 固定即可），**时钟不冻结**：`AttemptRef` 要求
`created_at <= terminal_at`，且 wave0 节点硬编码 `datetime.now(UTC)`；store 时钟用真实
时间保持与节点一致。envelope 的 `app_config` 用带 `LocalSandboxProvider` 的真
`AppConfig`（dummy model 配置，永不解析），否则 `classify_work_unit_storage` 判
`provider_unrecognized`。

### 5. HITL 驱动走真实公共控制入口

用 `run_deep_research(action="start")` → HITL1 交互 → 文本"确认"接受 proposal →
`run_deep_research(action="resume")` → completed。真实 hitl2 是自主决策节点，不产生
交互；组合保留若未来 hitl2 恢复人工决策时的 proceed 分支。

### 6. 红测先行 + CLI contract 测试

- `tests/integration/test_scripted_real_workflow_debug.py`：import 新 composition
  模块（旧代码没有 → 红），驱动固定 Bundle，断言每波 counter、两条 wave1 review
  artifact、wave2 finding backing ref ∈ accepted、trace 相位、completed 终态。
- `tests/contract/test_scripted_real_debug_command.py`：Make target 存在且独立；
  零 `.env`/零网络（屏蔽 `dotenv.load_dotenv` 与 socket）；脚本耗尽即失败（缺一条
  模型响应、多一次工具调用、非法脚本输出、意外进入 targeted/rerun 四类失败用例）；
  <10s 断言（超时即测试失败）。

## Risks / Trade-offs

- [脚本与 prompt/契约漂移形成假绿] → 契约测试含"缺响应/多调用/非法输出"失败用例；
  prompt/contract 改动时红测先红，强制同步 scenario。
- [wave1 底线或路由再变（BUG-028 修复）] → 基线按当前真实路由写死；BUG-028 落地后
  单独更新 scenario 并补 named case，不静默放宽。
- [命令演变成产品后门] → 独立 Make target、operator-only 文档、零凭据/零网络断言、
  输出显式标注 scripted_real_workflow。
- [10 秒目标被悄悄放宽] → CLI contract 用真实时钟断言，超时为测试失败。
- [spike 文件残留] → tasks 明确删除 `tests/integration/spike_scripted_real_workflow.py`。

## Migration Plan

新增文件 + 一个 Make target + 治理登记（project-structure.toml 路径、req-registry
SCR-/PRS-019、前缀 `SCR: scripted-real-workflow-debug`）。无存量行为变更，无回滚面；
失败回退 = 删除新文件与登记条目。

## Open Questions

- 无。repair/targeted named case（`wave0-repair` / `wave1-review-invalid` /
  `wave2-targeted`）刻意留到第二阶段，依赖 BUG-028 与 BUG-029 的独立 change。
