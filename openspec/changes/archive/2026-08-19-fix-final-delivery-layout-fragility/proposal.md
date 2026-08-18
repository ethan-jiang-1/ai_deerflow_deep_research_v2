## Why

BUG-055（`_backlog/bugs/BUG-055-final-delivery-layout-admission-observability.md`）：真实
003 run 在 final_delivery 把全部真实研究产出丢在最后一步——模型调用 3/3 全部
completed，但 layout 候选 3/3 被 admission 拒绝（fence/散文包裹或 id 回显偏差），
`node.py` 的 `except Exception` 把具体失败码吞成泛化 `WORK_FAILED`，gate 3 轮
repair 耗尽 → `research.blocked`。同日另一次 run 同样的非退化 plan 一次回显成功
（且 PASS 的那次 run 里 a1 拒、a2 过）：纯模型波动就能决定整个 run 的生死。

三个契约层根因：

1. **layout 排序押在模型回显上**：非退化 plan 的唯一模型自由度是排列
   conclusion/uncertainty 的合成 id——纯排版决定，却拥有 run 级否决权
   （BUG-053 已为退化 plan 承认"排序唯一时不需要模型"，非退化分支没跟进）。
2. **parser 零归一化**：`parse_layout_candidate` 裸 `json.loads`；wave0/wave1
   同样裸解析但靠节点内有界 repair 循环吸收，final_delivery 没有（by design，
   workflow.md："this node has no invented repair branch"），模型输出任何包裹物
   都直接失败。
3. **观测缺口**：REJ-007 只点名 topic_planning/wave0/wave1 必须留 parser
   validation fact，final_delivery 的 layout admission 边界不在名单里——journal
   里 3 次 attempt 没有任何 validation 事件，失败码与"模型实际说了什么形状"
   （fenced/prose/…）无处可查，只能靠 token 数反推。

## What Changes

产品机制上只改 final_delivery 一个节点的失败语义与观测，gate/route/预算不动：

1. **Parser 归一化**：`parse_layout_candidate` 接受三种投递形状——裸 JSON 对象、
   fenced code block、嵌在散文中的 JSON 对象（与 journal 既有
   `FinalResponseShape` 分类学对齐：`json_object`/`fenced`/`embedded_json`）。
   归一化后 admission 仍要求既有精确闭合形状（schema_version=1 + 恰好完整的
   entry id 集合）。
2. **确定性 layout fallback**：非退化 plan 的某次 visit 里，composer 调用失败
   （invocation failure）或候选在归一化后仍不可 admit（parse/admission
   failure）时，该 visit **降级为 plan-order layout**（与退化分支同一构造、
   走同一条 admission/render/publish/readback-verify 路径）并正常发布——排版
   降级不再产生 `WORK_FAILED`、不再消耗 gate repair、不再可能 blocked。
   结构性失败（plan/evidence 读取、render、publish、readback/verify）语义
   不变：无发布 + `WORK_FAILED` → 既有 repair 路径。由此 final_delivery 的
   blocked 仅剩结构性失败一类（与 runbook-003 §5.1 的口径一致）。
3. **观测补齐**：final_delivery 的 composer 候选 parse/admission 边界纳入
   journal validation fact（REJ-007 名单扩展）：`initial` stage + 闭合
   canonical code（既有 `final_layout_*` 错误码原样透出，不再被吞）；
   invocation failure 遵循 REJ-002 既有规则（只留 invocation fact，不发
   validation fact）。不新增 journal 字段、不保留 raw 模型输出（REJ 禁止）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `final-delivery-node`: FID-001 增补归一化解析与 plan-order fallback 语义；
  FID-002 把"malformed/failed candidate → 只进 repair"收窄为"结构性失败 →
  repair；layout 级失败 → 确定性降级发布"。
- `run-event-journal`: REJ-007 的 validation-fact 边界名单加入 final_delivery
  的 composer 候选 parse/admission 边界（闭合 code 集，无 response shape）。

## Change Focus

- **Primary module / causal owner**: `deep_research_harness/src/deerflow_deep_research/graph/nodes/final_delivery/`（composer.py 的解析/构造 + node.py 的失败分支）。
- **Seam classification**: deterministic-guardrail——composer 的认知合同不变（仍是零工具、仍只回 layout id 排列）；变的是它周围的确定性边界：归一化解析、降级构造、validation fact 透出。模型分支的存在与形状（advisory 排版建议）不新增任何认知职责。
- **Question**: 一个非退化 readiness plan 的 visit 中，composer 调用或候选失败时，final_delivery 应当在什么条件下交付、留下什么观测、何时仍可 blocked？
- **Necessary adjacent/external contracts**:
  - `run-event-journal`（REJ-002/REJ-007）：validation fact 的闭合字段/stage/code 纪律——本 change 扩名单不改字段。
  - `gate-kernel`（既有 final gate 规则/route/budget）：不改，但降级后 `final_delivery_fresh_view` 规则看到的仍是合法 published view——需确认无隐性耦合。
  - `deep-research-delivery-efficiency`（002 scripted 模板路径）：确认 full-fake/scripted 不经过 real composer 分支，无影响。
- **Evidence seam**: `tests/unit/test_final_delivery_real.py`（节点级：归一化、fallback、结构性失败仍 repair）+ `tests/contract`（journal validation fact 闭合性）+ 真实 003 复跑（runbook §5/§6 验收）。
- **Not in scope**: 不移除非退化 plan 的 composer 调用（FID-001 保留，见 design 的备选讨论）；不改 gate 预算/route_map；不给 wave0/wave1/readiness 等其他节点的裸解析加归一化（它们各有既有吸收机制，另立 change）；不保留 raw 模型输出到任何观测面（REJ/RTO 禁止）；不改 bridge 挂起问题（独立事项）；不改 `deerflow/` gitlink（只 leverage，普通下游工作不修改不翻源）。
- **Triggered review policies**: node-agent-workflow-integrity, workflow-outcome-review

## Node Agent Review

| Surface | Classification |
| --- | --- |
| Surface | final_delivery composer（零工具、单次调用、layout 候选）+ 其确定性解析/admission 边界 |
| Classification | cognitive-program（composer 本身）外包裹 deterministic-guardrail 变更 |
| Bounded cognitive question or no-agent rationale | "给定这些可信 entry id，给出一个排列"——仅排版建议；模型不能决定内容、引用、发布或终态 |
| Input authority boundary | 仍只读 readiness report plan 投影 + 有界 accepted evidence 元数据（`build_final_delivery_request` 不变） |
| Tool posture and runtime enforcer | 零工具、单 invocation（final-delivery-composer policy 不变） |
| Candidate result and deterministic admission owner | 候选=layout 排列；确定性 owner=归一化 parser + `admit_layout_candidate`（闭合集合校验）+ fallback 构造（plan-order） |
| Failure owner and bound | layout 级失败（invocation/parse/admission）→ 同 visit 确定性降级，无重试、无 gate 消耗；结构级失败（读取/render/publish/verify）→ 既有 gate repair（budget 3）→ exhausted blocked |
| Deterministic evidence seam | journal `initial`-stage validation fact（闭合 `final_layout_*` code）+ 既有 model_tool invocation fact；单测断言事件形状 |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Composer invocation 失败（provider/预算） | bridge 的 model_tool invocation fact | 节点内同 visit 确定性 fallback（无模型重试） | 不终态化，继续发布 | 正常 pass 发布；journal 保留 invocation fact | events.jsonl model_tool 失败事件 + 成功 terminal 事件 |
| 候选 parse/admission 失败（归一化后） | journal `initial` validation fact（闭合 code） | 同上：plan-order fallback | 不终态化 | 正常 pass 发布 | validation fact（`final_layout_*`） |
| 结构性失败（plan/evidence 读、render、publish、readback/verify） | gate view（WORK_FAILED/EVIDENCE_INSUFFICIENT） | 既有 gate repair，budget 3 | 耗尽 → blocked（不变） | repair 重试或 exhausted | 既有 gate/journal 事件 |
| 降级发布成功 | journal validation fact（如有） | 无需恢复 | completed（不变） | — | final artifacts + claim-citation-map |

## Impact

- 代码：`deep_research_harness/src/deerflow_deep_research/graph/nodes/final_delivery/composer.py`（归一化解析 + plan-order 构造提取）、`node.py`（失败分支分离 + validation fact）。gate/engine/其他节点零改动。
- 测试：`deep_research_harness/tests/unit/test_final_delivery_real.py`（改写 1 个既有用例 + 新增归一化/降级/观测用例）、journal 契约套件补 1 条。
- 文档：`_backlog/_local_demo/runbook-003-medium-real-auto.md` §5.1/§8 一句口径更新；BUG-055 卡归档。
- 依赖/接口：无新依赖；`FinalDeliveryGateView`、journal 事件 schema、run-summary 均不变；`deerflow/` submodule 零改动（只 leverage）。
