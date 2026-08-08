# Deep Research Harness 测试资产审计

> 类型: 研究记录 / 决策建议 | 资产盘点快照: 2026-08-07 `5407e9f` | Agent-workflow 复核: `1a8a594`
>
> 范围: 盘点 `deep_research_harness/tests/` 的已跟踪资产、测试选择和本轮可复现运行结果，
> 并复核这些资产是否能证明 public controller、node cognitive program 和 run direction 的真实
> 用户体验。本文先记录事实；是否保留、合并或删除某项资产的策略结论应建立在这些事实之上，
> 而不由文件量本身推出。Agent-native workflow 的一手资料研究见
> [`deep-research-harness-agent-native-workflow-research.md`](deep-research-harness-agent-native-workflow-research.md)。
>
> 落地: 本审计首先作为
> [`deep-research-harness-agent-native-progressive-plan.md`](deep-research-harness-agent-native-progressive-plan.md)
> 的证据输入；该计划只准入单一 OpenSpec change
> [`establish-agent-native-research-direction-loop`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/)
> 承接一个渐进 vertical slice；其 `tasks.md` 是唯一实施 ledger。本报告的广泛 metadata 清扫建议
> 仍是后续审计输入，不在该 change 内顺手执行。

## 资产盘点与方法

### 口径与可复现性

- 文件口径使用 `git ls-files deep_research_harness/tests`，因此不把本机的 `__pycache__`、`.pytest_cache` 或 `.reports` 当成版本化测试资产。快照时 `git status --short --untracked-files=all` 为空；Git 提交为 `5407e9f`。
- `test module` 只指路径匹配 `tests/**/test_*.py` 的 Python 文件；辅助注册表、场景、夹具、包初始化文件不计入该列。pytest item 则是收集后的可执行用例，参数化会使其大于 `def test_*` 的静态数量。
- Python 行数是物理行数，不等于有效代码行，也不把 JSON、Markdown 和 `.gitkeep` 计入 LOC。

基础计数命令及本次输出：

```sh
git rev-parse --short HEAD
# 5407e9f

git ls-files deep_research_harness/tests | wc -l
# 261
git ls-files deep_research_harness/tests | rg '\.py$' | wc -l
# 252
git ls-files deep_research_harness/tests | rg '/test_[^/]+\.py$' | wc -l
# 204
```

目录级文件数与 LOC 使用下列命令生成；该树与上述已跟踪清单在快照时一致：

```sh
for test_dir in assets blocking_io contract domain engine eval fixtures graph integration live scenarios scenarios_suspended unit; do
  find "deep_research_harness/tests/$test_dir" -type f -name '*.py' \
    -exec awk 'FNR == 1 { files++ } { loc++ } END { print files + 0, loc + 0 }' {} +
  find "deep_research_harness/tests/$test_dir" -type f -name 'test_*.py' \
    -exec awk 'FNR == 1 { files++ } { loc++ } END { print files + 0, loc + 0 }' {} +
done
```

### 当前规模

版本化测试树共有 **261 个文件**；其中 **252 个 Python 文件、63,366 LOC**。其中 **204 个 pytest 模块、46,720 LOC**，剩余 **48 个辅助 Python 模块、16,646 LOC**。非 Python 的 9 个文件包括 3 个 provider-shape JSON、5 个 `.gitkeep` 和 1 个暂停场景说明；文件清单可由上面的 Git 命令复现。

| 目录 | Python 文件 | Python LOC | `test_*.py` 模块 | 测试模块 LOC |
| --- | ---: | ---: | ---: | ---: |
| `(root)` | 3 | 67 | 0 | 0 |
| `assets` | 13 | 7,464 | 0 | 0 |
| `blocking_io` | 3 | 428 | 3 | 428 |
| `contract` | 57 | 10,512 | 57 | 10,512 |
| `domain` | 15 | 3,025 | 15 | 3,025 |
| `engine` | 8 | 1,605 | 8 | 1,605 |
| `eval` | 11 | 2,368 | 9 | 1,665 |
| `fixtures` | 10 | 1,428 | 0 | 0 |
| `graph` | 21 | 7,296 | 21 | 7,296 |
| `integration` | 24 | 7,758 | 23 | 7,757 |
| `live` | 6 | 196 | 6 | 196 |
| `scenarios` | 18 | 6,926 | 0 | 0 |
| `scenarios_suspended` | 1 | 57 | 0 | 0 |
| `unit` | 62 | 14,236 | 62 | 14,236 |
| **合计** | **252** | **63,366** | **204** | **46,720** |

`assets` 与 `scenarios` 合计 14,390 LOC（22.7% 的 Python 测试树），加上 `fixtures` 后为 15,818 LOC（25.0%）。这三个目录都没有匹配 `test_*.py` 的文件，因此这里描述的是测试支持/注册表资产的体量，而不是把它们误报为 pytest 模块。

最大的一组支持资产是 `tests/assets/evidence.py`（2,229 LOC）、`tests/scenarios/canaries.py`（1,466 LOC）、`tests/assets/requirement_evidence.py`（1,397 LOC）、`tests/assets/node_agent_capabilities.py`（1,097 LOC）和 `tests/assets/cognitive_program_board.py`（805 LOC）。可复现命令：

```sh
find deep_research_harness/tests/assets deep_research_harness/tests/scenarios \
  -type f -name '*.py' -exec wc -l {} + | sort -nr | sed -n '1,30p'
```

### 命名、参数化与收集形态

对 204 个测试模块作 AST 静态扫描，得到 1,785 个名称为 `test_*` 的同步/异步函数和 68 个 `class Test*` 定义；源码文本中有 190 处 `@pytest.mark.parametrize`、128 处 `@pytest.mark.asyncio`、13 处 `@pytest.mark.workflow`、2 处直接写出的 `@pytest.mark.requires_llm`。后者不包含 `pytestmark = ...` 的模块级标记。这些都是语法出现次数，不是 pytest item 数，也不能据此推断重复率。

```sh
python3 - <<'PY'
import ast
from pathlib import Path

trees = [
    ast.parse(path.read_text(encoding="utf-8"))
    for path in Path("deep_research_harness/tests").rglob("test_*.py")
]
tests = sum(
    1
    for tree in trees
    for node in ast.walk(tree)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
)
classes = sum(
    1 for tree in trees for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name.startswith("Test")
)
print(tests, classes)
PY
# 1785 68

git ls-files deep_research_harness/tests | rg '/test_[^/]+\.py$' \
  | xargs rg --no-filename '@pytest\.mark\.[A-Za-z_]+' \
  | sed -E 's/.*@pytest\.mark\.([A-Za-z_]+).*/\1/' | sort | uniq -c | sort -nr
# 190 parametrize
# 128 asyncio
#  13 workflow
#   2 requires_llm
```

项目的 marker 与选择器由 `pyproject.toml` 声明，包含 `workflow`、`requires_llm`、`release_e2e`、`postgres` 四种相关标记（`deep_research_harness/pyproject.toml:42-52`）；四个 lane 的路径和表达式集中在 `tests/assets/selection.py:6-14`。

本轮只收集、不执行时，完整 pytest collection 在 2.03 秒内得到 2,509 个 item：

```sh
cd deep_research_harness
env -u VIRTUAL_ENV UV_OFFLINE=1 uv run --extra operations --extra demo-tui \
  python -m pytest --collect-only -q
# 2509 tests collected in 2.03s
```

同一 collection 按目录的实际 item 分布如下，命令以 nodeid 的第一层目录聚合：

```sh
env -u VIRTUAL_ENV UV_OFFLINE=1 uv run --extra operations --extra demo-tui \
  python -m pytest --collect-only -q \
  | awk -F/ '/^tests\// { print $2 }' | sort | uniq -c | sort -nr
# 835 unit; 669 contract; 361 graph; 220 domain; 182 integration;
# 115 engine; 68 eval; 49 live; 10 blocking_io
```

官方 lane 收集结果如下。确定性三条 lane 共 2,460 个 item，live 为 49 个，两者相加等于完整 collection 的 2,509；这与项目声明的非重叠选择关系一致（`deep_research_harness/docs/testing-and-evaluation.md:102-111`，`deep_research_harness/tests/contract/test_test_lane_selection.py:96-108`）。

| lane | 官方选择口径 | 收集结果 | pytest collection 时间 |
| --- | --- | ---: | ---: |
| fast | `tests/contract tests/domain tests/engine tests/unit tests/graph tests/eval`，排除 workflow/live/postgres | 2,266 / 2,268（2 deselected） | 1.91s |
| integration | `tests/integration tests/blocking_io`，同一排除条件 | 178 / 192（14 deselected） | 1.45s |
| workflow | `tests` + `workflow` marker | 16 / 2,509（2,493 deselected） | 2.20s |
| live | `tests/live` + `requires_llm` marker | 49 | 0.94s |

上述表格的可复现形式为：

```sh
env -u VIRTUAL_ENV UV_OFFLINE=1 uv run --extra operations \
  python -m pytest tests/contract tests/domain tests/engine tests/unit tests/graph tests/eval \
  -m 'not (requires_llm or release_e2e or postgres or workflow)' --collect-only -q
```

其余三条 lane 将路径及 marker 换成 `tests/integration tests/blocking_io`、`tests -m 'workflow and not (requires_llm or release_e2e or postgres)'`、`tests/live -m 'requires_llm and not release_e2e'`；这些表达式与 `tests/assets/selection.py:6-14` 完全对应。

### 证据、场景与治理型资产

`tests/assets/evidence.py` 明确定义了三种资产类别、稳定 seam、真实性等级和精确 selector 的 `TestEvidenceClaim`（`deep_research_harness/tests/assets/evidence.py:82-126`）；中央声明表从该文件第 325 行开始。以这些结构化对象而非文件名统计，本快照包含：

| 结构化资产 | 数量 |
| --- | ---: |
| 中央 `TestEvidenceClaim` | 363 |
| code-correctness claim | 302 |
| deterministic-workflow-conformance claim | 16 |
| live-behavioral-evaluation claim | 45 |
| fast / integration / workflow / live 预期选择 | 245 / 57 / 16 / 45 |
| `RequirementImpact` | 136 |
| incident | 13 |
| critical fault | 7 |
| node-conformance 行 | 11 |
| model-workflow coverage 行 | 8 |
| cohort evidence / cognitive-program 行 | 20 / 20 |
| intake-planning / evidence-intake / evidence-judgment / final-composition calibration case | 12 / 12 / 15 / 2 |

这些数字来自本仓库定义的对象，不是外部估算：

```sh
cd deep_research_harness
env -u VIRTUAL_ENV UV_OFFLINE=1 uv run --extra operations python - <<'PY'
from collections import Counter
from tests.assets.evidence import EVIDENCE_CLAIMS
from tests.assets.requirement_evidence import REQUIREMENT_IMPACTS
from tests.assets.inventory import INCIDENTS
from tests.assets.fault_matrix import CRITICAL_FAULTS
from tests.assets.node_conformance import NODE_CONFORMANCE
from tests.assets.workflow_nodes import MODEL_WORKFLOW_COVERAGE
from tests.assets.node_agent_capabilities import COHORT_EVIDENCE, COGNITIVE_PROGRAM_EVIDENCE

print(len(EVIDENCE_CLAIMS), Counter(c.asset_class.value for c in EVIDENCE_CLAIMS))
print(len(REQUIREMENT_IMPACTS), len(INCIDENTS), len(CRITICAL_FAULTS))
print(len(NODE_CONFORMANCE), len(MODEL_WORKFLOW_COVERAGE), len(COHORT_EVIDENCE), len(COGNITIVE_PROGRAM_EVIDENCE))
PY
# 363 Counter({'code-correctness': 302, 'live-behavioral-evaluation': 45,
#              'deterministic-workflow-conformance': 16})
# 136 13 7
# 11 8 20 20
```

这层资产确实不是被动说明文档：`scripts/check_test_assets.py` 先收集四个 lane，再对 claims、requirement impacts、incident、node、fault、workflow、scenario 和 provider-shape 注册表执行连接校验（`deep_research_harness/scripts/check_test_assets.py:341-444`）。例如 requirement impact 验证会拒绝未收集 selector、没有 central claim 的 selector 和不一致 seam（`deep_research_harness/tests/assets/requirement_evidence.py:1120-1165`）；workflow inventory 会将语法发现的 `run_agent` owner 与声明的 workflow coverage 双向比对（`deep_research_harness/tests/assets/workflow_nodes.py:154-209`）。这说明它们是可执行治理/可追溯性资产，而不是运行时业务实现。

为了避免把“名称像治理”误当作语义事实，本审计只将下列内容标为**复核候选**：

- 对 `tests/contract` 按文件名含 `governance|architecture|asset|evidence|inventory|requirement|release|lane|workflow|topology|verification` 的宽松筛选，得到 25 个模块、4,512 LOC。命令为 `find deep_research_harness/tests/contract -type f -name 'test_*.py' | rg '(governance|architecture|asset|evidence|inventory|requirement|release|lane|workflow|topology|verification)'`，再分别 `wc -l`。这是人工复核队列，不是“冗余测试”结论。
- `generated|auto-generated|autogenerated|do not edit` 文本扫描命中 8 个 Python 文件、2,780 LOC。至少两类有明确含义：项目结构测试校验 `AGENTS.md` 的 generated block（`deep_research_harness/tests/contract/test_architecture_governance.py:25-27`、`358-374`），prompt-dump 测试生成并校验本地 review catalog（`deep_research_harness/tests/graph/test_prompt_dump.py:37-52`、`95-120`）。文本命中不证明这些测试文件由生成器产生，只表明它们涉及生成物或生成请求。
- `tests/scenarios_suspended/evh_024_release_acceptance.py` 不采用 pytest 默认文件名且没有 Make/CI 执行路径；它是明确保留的诊断材料（`deep_research_harness/tests/scenarios_suspended/README.md:3-10`）。因此它应从“当前可执行 suite”的分母中单列，而不是混入活跃测试数。

### 运行证据与当前失败

项目约定 `make verify` 为完整确定性 gate，`make test-fast` 为 fast lane，`make test-assets` 为资产治理检查（`deep_research_harness/Makefile:40-41`、`93-98`、`142-143`；`deep_research_harness/docs/testing-and-evaluation.md:9-32`）。本轮实测结果：

| 命令 | 结果 | 时间 / 说明 |
| --- | --- | --- |
| `UV_OFFLINE=1 make test-fast` | 通过 | JUnit 根 suite：`tests="2266" failures="0" errors="0" skipped="0" time="72.512"`；生成文件为被忽略的 `.reports/test-fast.xml` |
| `UV_OFFLINE=1 make test-assets` | 失败，退出码 2 | `real 7.37s`；并非超时 |
| 全量 `pytest --collect-only` | 通过 | `2509 tests collected in 2.03s` |

`test-assets` 的完整失败关键输出如下，应作为当前治理一致性问题单独追踪，而不是被归因为 suite 规模：

```text
unknown deterministic @impl: CES-008,DRH-005,DRH-007,NOA-014,PRS-017,RDO-007,
REG-020,RER-013,RES-006,RSV-004,RUS-007,RWB-008,TOP-008
make: *** [test-assets] Error 1
real 7.37
user 4.08
sys 0.83
```

该命令的通过路径本应打印 incidents、nodes、faults、workflow nodes、central claims 和 deterministic test 总数（`deep_research_harness/scripts/check_test_assets.py:459-467`）；当前在 requirement-evidence 校验前后失败。历史静态记录仍写有 `13 incidents / 1170 tests` 和 `1094 passed`（`deep_research_harness/tests/assets/inventory.py:44-51`），而本轮收集到 2,460 个确定性 item、fast lane 的 JUnit 为 2,266 个；两组数值不同，不能把历史字符串当作当前运行基线。

### 本节边界

这里的盘点支持后续讨论测试资产是否过量、哪些是传统确定性程序校验、哪些与模型/提示词行为有关。但现有计数、命名和 timing 不能单独证明“应删哪一类”或“prompt 编程优于传统程序编程”。后续结论需要按每个资产的失效模式、受保护的产品行为、真实性等级和维护成本继续审查；本节不越过该证据边界。

## 审计结论

### 结论先行

**不应该在“提示词编程”与“传统程序编程”之间二选一。** Deep Research 应采用的边界是：认知系统负责提出候选、解释不确定性和生成研究内容；传统确定性系统负责验证、准入、路由、权限、预算、持久化和不可逆副作用。这个分工不是新设想，而是项目 Charter 已经确立的原则：`Cognition proposes; deterministic owners validate, admit, and route`（`openspec/governance/agent-charter/charter.md:63-67`）。

本次审计支持更具体的判断：**当前的投资失衡主要不在“确定性测试总量”，而在“证明测试存在/互相引用正确”的元治理层已经大到接近一个产品子系统，同时真实模型质量的反馈闭环仍然小、手动且部分暂停。** 测试树 63,366 LOC 对生产源码 29,171 LOC 的 2.17 倍，本身不能证明浪费；但仅 `assets + scenarios + fixtures` 已有 15,818 LOC，另有 669/2,509 个已收集 item 位于 `contract`，以及 363 条 central claim、136 条 requirement impact。它们值得逐项挑战其独特风险，而不能继续以“更多可追溯性”为默认理由增长。

同时，**不能据此削减真实的确定性边界和 scripted workflow。** 历史 real-mode 复盘记录了 13 类问题：工具策略、预算、结构化输出、store、配置与状态隔离均被 fake 路径漏过；其中预估至少 8 项可由真实 middleware/policy 加脚本化模型在秒级发现（`_backlog/_done/_closed_plans/test-assets-postmortem-real-mode-integration.md:21-72`）。当前 fast lane 仍能以 72.5 秒通过 2,266 个 item，这说明领域、状态、权限、存储和真实 bridge 的确定性测试具备明确的安全回报，而不是“legacy 垃圾”。

真正欠账的是认知质量验证。标准 `make verify` 有意排除 `requires_llm`，完整 full-real selector 已没有 Make/CI 执行面，且只能在先建立小于十秒的确定性诊断环后才能重启（`deep_research_harness/docs/testing-and-evaluation.md:102-131`；`deep_research_harness/tests/scenarios_suspended/README.md:3-10`）。独立 Cognitive Evaluation Suite 目前只登记 `hitl1-brief@v1` 和 `wave0-worker@v1` 两个 subject，并明确不在 pytest 或 routine CI 中运行（`deep_research_harness/docs/cognitive-evaluation-suite.md:52-59`；`deep_research_harness/evals/control/registry.json:3-16`）。这不足以让提示词、模型版本、检索策略或 agent capability 的改变获得有说服力的结果质量反馈。

### 正确的投资边界

| 层 | 应该由谁决定 | 应保留/新增的证据 | 不应继续膨胀成 |
| --- | --- | --- | --- |
| 确定性控制面 | Python/domain/engine/runtime | Bundle 生命周期、身份和权限、schema、path containment、工具 allowlist、预算、提交/发布、取消与幂等的最小 seam 测试 | 用 prompt 或模型输出来替代安全、授权、状态和副作用的最终判断 |
| Agent workflow | 真实 bridge + scripted model/tool | 一条覆盖真实 middleware、policy、parser、validator、store、gate 的最短可重放工作流，以及最高风险降级路径 | 为每个内部调用、每个 fixture 字段写快照式测试；项目已有定义要求只替换真正外部依赖（`deep_research_harness/docs/testing-and-evaluation.md:76-100`） |
| 认知/提示词程序 | prompt、capability、model/tool 配置和研究任务定义 | 版本化评测 case、重复实跑、硬不变量、质量/成本/延迟观测、人工或受控评审 | 把“prompt 已渲染”“模型返回 JSON”误写成“研究质量已经被证明” |
| 全链路验收 | 受控的 live/release 运行 | 少量有成本上限的真实 canary，用于发现分布、供应商和组合问题；发现后下沉为可重放 regression | 用一次 demo、一次 E2E 或一张登记表代替日常接口和质量验证 |

这张表与现有真实性阶梯一致：scripted real workflow 证明 real bridge/policy/loop/store/gate，live 运行才证明实际模型和工具依赖，full-real 当前仅是暂停的诊断材料（`deep_research_harness/docs/testing-and-evaluation.md:60-89`）。所以所谓“转向 prompt 编程”不应理解为少写程序、多相信 agent；它应理解为把不确定性显式放进可评测的 cognitive program，并继续让确定性代码守住不可绕过的控制面。

### Agent workflow 与 direction 的补充审计

进一步沿真实 DeerFlow composition、public skill、node prompt 和 Run Bundle lifecycle 追踪后，
可以把“认知质量欠账”定位得更具体。

| Surface | 当前资产真正证明了什么 | 尚未证明、却直接决定 UX 的事实 |
| --- | --- | --- |
| `tests/contract/test_public_skill.py` | committed skill 能被 configure 安装；frontmatter、tool/action 词汇和若干 forbidden strings 符合静态约束 | lead agent 会不会因该 workflow 把自然语言正确分成 start、pending answer、refine、status、cancel 或 clarification |
| `tests/integration/test_public_entry_replay.py` | 给定测试作者预写的 `start` / `resume` tool calls 后，LangChain tool loop、schema 和 result projection 可以接通 | 真实 DeerFlow 是否发现/加载 skill；模型是否自己选对 action；tool result 是否得到 truthful follow-up |
| prompt dump / renderer tests | production renderer 生成了预期 system/user 文本，capability ref 与 tool posture 接得上 | Markdown 中的方法是否让模型在正常、歧义、对抗和 repair case 中稳定做对 |
| lifecycle / reducer tests | refinement text 有界、能写入单槽、不会误消费 pending response，pure consumer 会递增 round | active graph 是否在真实 safe point 消费；两条 direction 是否丢失；ended refine 是否真的继续 graph；研究产物是否变化 |
| node scripted workflows | 真实 bridge、middleware、tool policy、parser、store 和 gate 能处理预先安排的外部响应 | prompt/capability 的认知质量，以及用户约束是否进入了该 node 的实际输入 |

这里有四个会使测试“看起来很绿但 UX 仍然改不过来”的结构性原因：

1. Public controller `SKILL.md` 只有 14 行，静态 contract 还强制 `<= 1400 bytes`。LangChain
   官方 Skills 指南要求 workflow 包含 procedures、decision criteria、examples 和 edge cases，
   并以 progressive disclosure 控制上下文；极小 byte ceiling 与这个目标冲突。长度可有合理预算，
   但不能把 “thin” 当成质量属性。
2. 20 个 runtime-loaded node capability Markdown 合计只有 114 行，而 11 个较完整的
   `workflow.md` 合计 427 行却被规范定义为 non-runtime reader projection。实际 method、branch、
   repair 和 output instructions 仍大量由 Python `prompts.py` 动态拼接，所以认知程序还没有
   单一、真正被 runtime 执行的 Markdown owner。
3. HITL1 的 `custom_notes` 和 `scope_boundaries` 会完整写入 `profile.json`，但
   `profile_state_fields()` 不投影它们，topic planner 也不读取 `profile_ref`；后续 retrieval、
   synthesis 和 delivery prompt 中没有 `custom_notes`。字段存在和 profile artifact 持久化
   不能证明用户备注生效。
4. active `refine` 写入单个 `admitted_refinement`，下一次会 silent overwrite；生产 graph 没有
   active safe-point consumer。ended refine 虽递增 round，public `BundleControl._refine()` 却不
   启动 graph。现有 refinement 测试没有覆盖任何实际 effect path。

因此，本轮最需要的不是更多 keyword、prompt snapshot 或 registry join，而是三组能观察决策与
效果的资产：**controller trajectory、direction effect、node cognitive-program corpus**。它们
仍要复用当前 deterministic/scripted/live 真实性阶梯，不能另造一套平行治理表。

### 资产过量的确切位置

可以做出三个有证据的判断，而不是笼统说“测试太多”。

1. **元治理有明显的维护风险。** `test-assets` 会收集四个 lane，再连接 claims、requirement impacts、incident、node、fault、workflow、scenario 和 provider-shape 多张表（`deep_research_harness/scripts/check_test_assets.py:341-422`）。它在本快照中实际失败，报出 13 个 `unknown deterministic @impl`。根因可直接追到实现：需求收集器只识别 `> req:` 行（`tests/assets/requirement_evidence.py:19-22,1325-1352`），而活跃 main specs 把例如 `CES-008`、`REG-020`、`TOP-008` 放在 requirement 正文末尾（`openspec/specs/cognitive-evaluation-suite/spec.md:177-185`；`openspec/specs/research-graph-lifecycle/spec.md:593-600`；`openspec/specs/topic-planning-node/spec.md:320-326`）。这是一个阻断主验证门的格式双真相，不是模型行为失败。

2. **存在多个描述同一认知工作流的投影，必须核对是否各有不可替代问题。** 当前有 363 central claims、node conformance、workflow coverage、cohort/cognitive-program evidence、board 和 requirement-impact 等结构化层。规范本身要求 registry 只能是可审核的 claim，绝不能代替收集到的行为证据（`openspec/governance/test-evidence-policy.md:19-23`）；`workflow_nodes.py` 也将其称为 traceability join，而非行为证明（`deep_research_harness/docs/testing-and-evaluation.md:91-100`）。因此每一张人工维护表都应回答一个独特的审查问题，否则应由一个 canonical source 生成只读投影或被删除。

3. **live 数量小并不自动代表质量充分。** 本轮 49 个 `requires_llm` item 都在 `tests/live/`：6 个 canary、41 个 calibration item、2 个 preflight；它们不在默认确定性绿灯中。它们有价值，但 six canaries 还明确只覆盖三条 public-entry 短前缀和三条 late-node seed，不证明完整 pipeline（`deep_research_harness/docs/testing-and-evaluation.md:113-125`）。因此减少元数据时，不能反向削减这条稀缺的经验反馈路径。

### 不建议做的事

- 不要按目录、LOC、marker 或“看起来像治理”批量删除。项目自己的测试证据策略也明确说数量、目录和静态 metadata 不是真实性代理（`openspec/governance/test-evidence-policy.md:56-58`）。
- 不要把 16 个 workflow item 或高风险的 lifecycle/store/policy 测试迁成 fake topology 测试。历史事故正是这样产生的（`_backlog/_done/_closed_plans/test-assets-postmortem-real-mode-integration.md:91-97`）。
- 不要把 live 评测直接变成每个 PR 的硬质量 gate。当前文档要求先报告主观指标，只有在稳定 baseline 经 review 后才可升级为阈值（`deep_research_harness/docs/testing-and-evaluation.md:127-131`）。
- 不要在没有 OpenSpec change 的情况下偷偷从 `make verify` 移除治理校验。`evaluation-hardening` 规格目前把选择、claims、inventory 和 deterministic/live 的边界定义为受治理行为（`openspec/specs/evaluation-hardening/spec.md:100-148`）。

## 当前落地路线与后续审计

当前 change 从本审计中只拿走能证明第一条 agent-native direction loop 的最小资产，并按以下
闸门推进：

| Change phase | 本报告提供的资产 | 进入下一阶段前必须观察到 |
| --- | --- | --- |
| 0 | requirement-id gate regression、actual DeerFlow loader、same-Bundle rerun feasibility | 当前 gate 恢复；真实 composition 加载 committed skill；现有 rerun 可回到 `topic_planning` |
| 1 | reducer/lifecycle/result matrix | 一个 pending direction 不被覆盖，replay 幂等，pending response 独立，结果不谎报 applied |
| 2 | partial graph、restart/crash、ended/active continuation | 同一 Bundle、一次 generation、terminal-round safe point、旧 evidence/artifacts 保留 |
| 3 | scripted controller handoff、canonical profile/prompt capture、real capability bridge、最短 direction-effect workflow | public workflow 和 topic-planning assignment 的真实 producer-to-consumer handoff |
| 4 | versioned controller/topic-planning cases 与独立 review record | cognitive evidence 按真实层级报告，implementation finding 已回写 task |

广泛的 registry/board/claim consolidation、全部 capability program corpus 和 full-real release 不在
当前 change。这样既避免四个前置 change 的管理成本，也避免用“一个 change”之名同时清扫所有
测试治理。

### 当前 Change Phase 0: 恢复一个可信的验证起点

1. 在当前 change 的第一个 gate 内，只把 13 个已批准但缺失的 id 补到 owning main-spec
   `> req:` declaration，并加 known regression；不让 parser 扫 arbitrary prose，也不借机改变
   evidence semantics。active delta 会暂时让 `DRH-005` / `TOP-008` 可发现，所以 apply 前的即时
   红灯只剩 11 个；archive 前仍须补全全部 13 个 main-spec declarations。验收是
   `UV_OFFLINE=1 make test-assets` 通过。
2. 在修复前冻结新增的人工 evidence registry、impact table 和 node board 条目，除非它们直接保护本次改动的行为风险。先停止增长，才有可能识别重复。
3. 将此次基线作为仪表盘，而非目标配额：2,509 items、fast lane 72.5 秒、49 live items、`test-assets` 当前失败。每月更新一次，并记录哪一项产品风险换来了新增维护面。

### 后续审计: 逐条清理元治理，而不是删测试

本节不属于 `establish-agent-native-research-direction-loop`。只有当前 vertical slice 的真实维护
成本和 evidence gaps 已被观察后，才重新决定是否另行准入；当前 change 不按净删行目标执行。

对 363 条 claim、136 条 impact 和所有 board/inventory 行建立一个一次性的 triage 表，每条只允许四种结果：`keep-behavioral-proof`、`keep-governance-rule`、`derive-from-canonical-source`、`retire-with-replacement`。判断问题固定为：

1. 它是否观察了某个生产行为，还是只验证别的声明存在？
2. 如果只做连接校验，哪个 production contract、OpenSpec requirement 或 central claim 已经是它的 canonical source？
3. 删除后哪个具体 requirement-risk pair 会失去证明？若没有答案，则不应继续手工维护。
4. 若要删除，哪一个仍会被收集的 selector 或生成的 projection 取代它？

现有 `ConsolidationDecision` 的“精确风险对必须有收集到的 replacement proof”思想值得保留（`deep_research_harness/tests/assets/requirement_evidence.py:1168-1281`）；问题是它不应迫使每个读者维护多份手写节点和 selector 投影。优先候选是把 `NodeSpec`/source discovery 作为节点存在性的 source，把一个 central evidence graph 作为 selector/seam/authenticity 的 source，其余 board 只生成用于 review。此处的验收标准应是“每个事实只手写一次”，而不是“删掉多少行”。

同时评估将 metadata checker 与生产 runtime import 解耦：该脚本在导入阶段加载 graph registry/topology（`deep_research_harness/scripts/check_test_assets.py:21-31`），但其中大量校验只需要 AST、OpenSpec 或 structured registry。若能把 runtime-loader 的真实行为留给一个窄 conformance test，把纯 metadata check 改为不导入 LangGraph 的 checker，冷启动与耦合会下降；前提是改动后仍有实际 loader 的行为测试，不能只以静态扫描取代它。

### 当前 Change 选择的三组行为资产

当前 change 实现 public controller、一个 pending/current-round direction 和 `topic_planning` 这一
个 node cognitive program；下述资产模型仍可复用，但不宣称其余 19 个 capability 已覆盖。

#### 2A. Public controller trajectory corpus

Controller 测试要把“工具能被调用”和“模型因 workflow 选对动作”拆开：

| 层级 | 资产 | 必须观察 |
| --- | --- | --- |
| Deterministic loader | 用真实 DeerFlow config/storage/activation middleware 载入 committed SOUL + skill | 安装路径、discovery、activation、实际 composed prompt 和 content digest；不能直接把 `SKILL.md` 当完整 `system_prompt` |
| Scripted real handoff | 真实 lead middleware、tool schema、tool loop、typed fake lifecycle result；只 script 外部 model turn | exclusive tool call、参数、result 回到 agent、truthful final text；claim 只到 plumbing/trajectory |
| Live cognitive selection | 真实 composed prompt 和真实模型，工具替换为记录 typed calls/results 的 bounded fake | 模型从自然语言自行选择 action 或 clarification；重复运行后报告正确率、错误类型、成本和延迟 |

第一版 case family 至少覆盖：

| Case | 期望 cognitive action | 硬不变量 |
| --- | --- | --- |
| 新的多源研究请求，无 active Bundle | `start` | sole lifecycle call；无 caller-selected id 或复制问题的参数 |
| 当前 pending subject 的直接回答 | `resume` | answer 只留在 latest user message；不放 tool args |
| suspended 时“顺便重点看监管风险” | `refine` | pending request 不被当成已回答 |
| “现在到哪了” | `status` | 不编造进度或结果 |
| “先停掉这次研究” | `cancel` | 没有 typed success 就不宣称已取消 |
| “这个方向不太对”且无明确 effect | clarification | 不 mutation Bundle，不猜 `cancel` 或 `refine` |
| active Run 期间提出另一件新研究 | conflict/clarification | 不创建第二个 active Bundle |
| 明确继续已知 ended Bundle | `refine` + explicit verified target | 目标不明时不依赖 stale Handle 猜测 |
| Bundle 已删除或 unavailable | truthful unavailable handling | 不从 session、checkpoint、日志或对话记忆恢复 |
| pending subject 与 run direction 混在同一句 | clarification 或经评审的明确拆分策略 | 不用一个 `resume` 同时产生未声明的 refinement effect |

`tests/integration/test_public_entry_replay.py` 可继续作为 scripted handoff，但应改名或改 claim，
诚实标注其 model action 是预写的。controller live cases 应成为 Cognitive Evaluation Suite 的独立
subject，而不是再塞进该 replay。`<= 1400 bytes` 应由“聚焦、可部署、低于批准 token budget”
和实际 loader test 取代；frontmatter、provisioning 与 forbidden authority strings 的静态检查仍保留。

#### 2B. Profile / refinement direction-effect ladder

这组资产必须逐层证明“收到、应用、传到认知程序、改变行为”，不能在第一层就宣称完成：

1. **Domain admission**：第一版只有一个 pending run direction；相同 trusted delivery 幂等，
   不同第二条 typed conflict 并保留第一条；pending response correlation 保持独立；并发、crash
   和重复 delivery 有界且幂等。
2. **Graph safe point**：partial graph 从真实 Bundle-local State 启动，跨 restart 到达批准的 safe
   point，exact-once 标记 direction applied，并记录适用 generation/round/revision。
3. **Trusted projection**：`custom_notes`、`scope_boundaries` 从 canonical profile、current-round
   refinement 从 Bundle State 形成一个 bounded topic-planning assignment；renderer test 证明真实
   planner 收到正确内容，未收到 path、authority 或无关敏感字段。
4. **Scripted mixed workflow**：从 public `refine` 经 real lifecycle、safe point、real node renderer
   到一个真实下游 candidate/gate；它证明 wiring 和 effect route，不宣称模型质量。
5. **Contrastive live eval**：同一个固定 research case 分别运行 baseline 和带 direction 版本，由
   硬不变量加 blinded/受控 rubric 检查 plan、evidence focus 或 final composition 是否遵守方向，
   同时报告质量、成本、延迟与 variance。

ended refinement 另有一条不可省略的 integration case：显式 target 后，同一个 Bundle 的下一
round 必须实际启动并产生 graph progress；旧 artifacts 仍可检查。只断言
`refinement_round == 1` 或 `admitted_refinement is None` 不构成 continuation evidence。

#### 2C. Node cognitive-program corpus

覆盖单位从 pytest 文件改为 **runtime-loaded cognitive program id + version/digest**。先覆盖 public
controller，再为当前 20 个 capability program 按用户风险排序。一个 program 至少要有：

- normal case：完成该角色的核心判断；
- ambiguity/boundary case：保留不确定性，不越权补事实；
- adversarial case：untrusted source 不能改工具、route、authority 或输出契约；
- dependency degradation case：工具/模型受限时诚实降级；
- invalid candidate + repair case：只修允许修的内容，不扩大 scope 或发起未授权 retrieval。

每次执行记录 `subject_id`、case version、capability/prompt digest、model/provider、tool set、输入
artifact digest、hard invariants、quality rubric、tokens/cost/latency 和 diagnostics。执行成功只表示
program 跑完；认知通过由独立 review/approved evaluator 给出。case corpus 与 execution Bundle
是 authority，coverage board 只能从它们生成 projection，不能再手写一套平行“已覆盖”事实。

只在跨 program 的真实风险无法由局部 case 发现时，才新增最短 mixed/full-flow case。full pipeline
负责检查组合、持久化和最终发布，不能替代 controller choice、safe-point effect 或单个 program
质量。现有 16 条 workflow claim 和 49 个 live item 是素材，不是上述三组覆盖已经完成的证明。

这遵循当前 evaluation-hardening 的下降路径：能重放的 provider 发现下沉为 deterministic
regression，不能诚实重放的保留为 bounded live case
（`openspec/specs/evaluation-hardening/spec.md:203-217`）。Cognitive Evaluation Suite 已经正确
区分“执行完成”与“认知通过”（`deep_research_harness/docs/cognitive-evaluation-suite.md:46-50`）；
缺的是 controller/direction/node 的代表性 corpus、重复运行与审查节奏，不是另一张静态登记表。

### 落地后的长期证据责任

| 改动类型 | PR 必须给出的证据 | 定期/手动证据 |
| --- | --- | --- |
| 生命周期、权限、状态、工具 policy、存储、预算 | 最低责任 seam 的确定性测试；需要 loop 时加 scripted workflow | 高风险路径的恢复/并发/耐久性演练 |
| Public controller skill / SOUL | 真实 DeerFlow loader + scripted handoff；更新受影响 intent cases | 固定 controller corpus 的 repeated live run 和错误分类 review |
| Profile 或 run direction | domain/safe-point/projection tests；至少一条到受影响真实 node 的 mixed workflow | contrastive live case，检查方向是否改变 plan/evidence/report |
| Node capability / prompt / model / retrieval 策略 | runtime resource digest、结构化输入/输出和对应 corpus case；证明不会越过控制面 | 受影响 case 的 repeated live run 和人工/受控 rubric review |
| 新功能跨越多个 cognitive programs | 一条最短 mixed real workflow，非关键外部依赖才可 scripted | 有明确上限的 canary；只有组合风险需要时才做 release acceptance |
| 真实运行发现的问题 | 在能重放时补最小 deterministic regression；否则登记 provider-only 理由 | 将 redacted live 诊断加入对应 eval case 的审查队列 |

这会把“trust coding agent”改成可审计的协作：agent 可以提出实现与 prompt，但它不能同时声明质量、构造证明和通过自己的 gate。模型输出、人工判断和运行报告都只是输入；准入和安全事实仍由有界的确定性 owner 决定。

## 成功判据与风险

当前 OpenSpec change 不以“测试行数下降 X%”验收。它必须达到：

- `make test-assets`、requirement coverage 与 fast lane 恢复绿色；格式改变不再产生未知 `@impl` 漂移。
- Public controller 的 committed skill 在真实 DeerFlow composition 中加载；完整 intent matrix 有重复 live observations，预写 tool-call replay 不再被登记为 action-selection proof。
- `custom_notes` / `scope_boundaries` 有 canonical topic-planning projection；active/ended refinement
  都有从 admission 到 terminal-round safe point、真实 graph progress 和 cognitive input 的 effect
  evidence；不同第二条 direction 不能 silent overwrite。
- public controller 与 `topic_planning` 两个 cognitive programs 有 stable id/digest、normal、
  ambiguity/boundary、adversarial 和 repair/degradation cases；真实模型结果与 deterministic pass 分开。

以下仍是长期测试治理目标，不是当前 change 的 archive gate：每一条保留 registry 行说明独有
requirement-risk；重复 projection 由 canonical source 派生或带替换证据退休；其余 active cognitive
program 按风险逐步建立 corpus；真实缺陷持续下沉为 deterministic regression 或 bounded live case。

最大的风险是把“元治理太多”误解成“测试不重要”，重新制造 2026-07-17 fake-only 的盲区。相反方向的风险是继续给每个 concern 再加一张表和一条 checker，最终让治理本身比产品变化更脆弱。上述分期的核心保护是：先让当前 gate 的 source-of-truth 一致，再以具体风险替换重复投影，最后把释放出的注意力投入模型实际效果。

## 研究边界与落地关联

本报告没有生产用户反馈、成规模的真实研究输出样本、成本账单、flake 历史或 mutation score，
因此不能断言某一个 prompt 的实际通过率、某一个测试必然冗余，或当前模型质量达到/低于某个
阈值。它能直接证明的是：验证投资存在结构性失衡；public replay 的 action 是预写的；
`custom_notes` 没进入后续 cognitive input；active refinement 没有 production safe-point consumer；
以及当前 metadata gate 自身存在 source-of-truth 故障。

当前落地不再创建四个前置 changes，而由
[`establish-agent-native-research-direction-loop`](../../../../openspec/changes/archive/2026-08-08-establish-agent-native-research-direction-loop/)
承接一个严格受限的 vertical slice：Phase 0 只修 declaration source；direction 只做单 pending
conflict policy；controller 只改一个 public skill/SOUL；node 只迁移 `topic_planning`；evaluation 只加
这两个 subject 的 bounded cases。广泛 metadata consolidation、全部 node 迁移、finer safe point 和
full-real release 明确延后，并根据这个 slice 的真实收益/维护成本再决定是否值得新 change。

具体 phase、No-Go 和 red-before-green task 见该 change 的 `design.md` 与 `tasks.md`；
[`deep-research-harness-agent-native-progressive-plan.md`](deep-research-harness-agent-native-progressive-plan.md)
是唯一来源计划，保留 causal owner 与 scope reasoning。
`backend/` 与 `frontend/` 继续不在这些 downstream changes 的范围内。本文是分析/准入材料，
不构成代码删除、规格修改或实现授权。
