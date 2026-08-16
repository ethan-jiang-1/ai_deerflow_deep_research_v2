## Why

Deep Research 的调试路径两极分化：`make demo-scripted` 是零凭据 fixture 图（替换全部节点 adapter，不证明真实生产控制路径），`make demo-real[-scripted]` 是真模型 + 真网页检索（几十秒到几十分钟、花费 API 成本）。每次改动真实图的契约问题，开发者都要付一次完整研究的时间和费用，因此经常只跑浅层测试，无法快速验证三波之间的真实 handoff（BUG-031）。2026-08-16 的 spike（`tests/integration/spike_scripted_real_workflow.py`）已证明：全 REAL adapters + 脚本模型/工具的窄组合能在 0.7 秒内走完三波全生命周期，缺少的只是正式、可维护的 operator 入口。

## What Changes

- 新增 operator-only 命令 `make debug-scripted-real-workflow`（`scripts/debug_scripted_real_workflow.py`）：单独 composition root，显式构造 all-real adapters、all-real gates、真实持久化与脚本化 model/tool capability。
- 新增非生产 scenario catalog（`src_fake` 内）：固定基线剧本——一个 topic plan、一次 Wave0 接纳、一次 Wave1 提取 + 两个 critic review、一条带 accepted backing ref 的 Wave2 finding、自主 HITL2、readiness pass、final delivery 发布；带运行时事实（accepted refs、plan 条目 id）的占位符填充，不伪造值。
- 基线预算硬约束：11 次模型调用、2 次 `web_search`、0 次 `web_fetch`；脚本队列严格耗尽——缺少响应、多余调用、进入 targeted/rerun 都判失败。
- 完成输出声明真实性边界：`composition=all_real_adapters`、`authenticity=scripted_real_workflow`、零网络/零凭据断言、每波 action counter、Bundle id、Event Journal 入口、总耗时。
- 零 `.env`、零网络、零凭据，不读取模型或 Tavily 配置；不修改 `ResearchGraphRecipe.all_real()`，不给 `make demo-real` 加任何 fake mode flag。

## Capabilities

### New Capabilities
- `scripted-real-workflow-debug`: operator-only 的窄而真三波调试组合：真实生产控制路径 + 脚本化外界，其真实性标注、预算、CLI 契约与"证明什么/不证明什么"的输出边界。

### Modified Capabilities
- `project-structure`: 注册本 change 新增的脚本、`src_fake` scenario 模块与测试文件的 canonical 路径。

## Impact

- `deep_research_harness/scripts/debug_scripted_real_workflow.py`（新增，presentation/launcher 层）
- `deep_research_harness/src_fake/deerflow_deep_research_fixtures/`（新增 scripted-real scenario 与 composition 模块）
- `deep_research_harness/tests/`（新增红测/契约测试；spike 文件删除）
- `deep_research_harness/Makefile`（新增一个 target，不动既有 target）
- `openspec/governance/project-structure.toml` 与 `req-registry.yaml`（登记新路径与 SCR-/PRS-019 需求 ID）
- 生产包 `src/deerflow_deep_research/` 无代码改动；`deerflow/` 不修改。

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/debug_scripted_real_workflow.py` owns the scripted-real runtime composition in the presentation layer (mirroring the `demo-pipeline` composition boundary), and `deep_research_harness/src_fake/deerflow_deep_research_fixtures/scripted_real/baseline.py` owns the fixed scenario data; the production recipe seam `runtime/research.py` is consumed unchanged.
- **Seam classification:** wiring because the change connects the existing all-real recipe seam, `RuntimeNodeAgentBridge` model/tool resolvers, `BundleGraphExecutor`, and the public control entry to scripted capabilities without changing any prompt, node cognitive role, gate rule, recovery semantics, or primary route.
- **Question:** Can an operator run the complete production control path against a fixed narrow scripted external world in under ten seconds with zero credentials and zero network, and does the command honestly label its authenticity and prove exactly what it proves?
- **Necessary adjacent/external contracts:** `demo-pipeline` (presentation-layer composition precedent), `node-agent-runtime` and `runtime-integration` (recipe/bridge seams consumed unchanged), `fixture-source-isolation` (scenario data at the non-production boundary), `project-structure` (canonical paths), `run-event-journal` (Journal entry reference in command output); DeerFlow local sandbox/config classes are the only framework surfaces.
- **Evidence seam:** the scripted-real three-wave action proof (`tests/integration/test_scripted_real_workflow_debug.py`) asserting the per-wave counters, accepted records, both Wave1 critic artifacts, the backed Wave2 finding, the completed terminal, and the under-10s wall time; plus the CLI contract test (`tests/contract/test_scripted_real_debug_command.py`) asserting the authenticity labels, zero-env/zero-net behavior, strict exhaustion failure cases, and the <10s contract.
- **Not in scope:** production graph/prompt/gate changes, any `demo-real` mode flag, BUG-028 targeted/rerun path fixes, the repair/targeted named cases, operator-log integration, and any `deerflow/` change.
- **Triggered review policies:** participant-outcomes, change-admission
