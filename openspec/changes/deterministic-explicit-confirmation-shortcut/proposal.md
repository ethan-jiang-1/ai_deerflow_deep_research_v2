# Proposal

## Why

demo-real Gateway 路线的 HITL1 提案确认是认知面：显式确认短语（`confirm`/`确认`）也要经
`_classify_proposal_reply` → 语义解析真模型调用。2026-09-26 六次实跑证明：provider
流式抖动（`stream_chunk_timeout`）会把这些调用全部打断，操作者的显式确认反复被判
"未识别"直至 `input.invalid_response` 终止——demo 阶梯对链路抖动零鲁棒性。节点内已有
对称先例：修订短语走 `_local_phrase_revision` 零模型捷径。显式确认应当获得同等待遇。

## What Changes

- hitl1 节点 `_classify_proposal_reply` 增加与 `_local_phrase_revision` 对称的确定性
  捷径：回复仅由封闭短语表内的显式确认短语构成时，零模型调用返回
  `SemanticCandidate(intent=ACCEPT_CURRENT_PROPOSAL)`。
- 准入语义不变：`admit_research_confirmation` 仍是唯一准入 owner，complete-proposal
  检查照旧（不完整提案保持 outstanding 并重入有界解析）。
- 短语表是冻结的封闭清单（`confirm`、`确认` 及等价显式确认语），不收部分匹配或歧义输入。
- `human-interaction-contract` 增补 ADDED requirement `HIC-005` 把该确定性映射显式化；
  `req-registry.yaml` 注册新 ID；主 spec header 同步。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `human-interaction-contract`: 增补一个 ADDED requirement（`HIC-005`）：显式确认短语
  在完整提案上零模型映射为 accept-current-proposal；既有四个 requirement 原文不变。

## Impact

- `deep_research_harness/src/deerflow_deep_research/graph/nodes/hitl1/node.py`
  （分类入口加确定性分支）与其单元测试（新增零模型断言与短语表用例）。
- `openspec/specs/human-interaction-contract/spec.md`（header + 新 requirement，
  经 delta 归档后）与 `openspec/governance/req-registry.yaml`（注册 `HIC-005`）。
- 不改：提案准入语义、semantic-intake 提示词、可见控件、Gateway/observer 路线、
  其他节点的认知面。
- 验收面：hitl1 单测（stub 计数断言零模型调用）+ 既有 human-interaction 契约测试全绿 +
  `check_project_gate.py --phase closeout`。

## Change Focus

- **Primary module / causal owner:** `hitl1` 节点的 `_classify_proposal_reply`（回复分类决策点）——由它决定一个回复是否还需要认知解析。
- **Seam classification:** deterministic-guardrail —— 封闭短语表上的精确映射是纯确定性分支，它把显式确认挡在认知解析之外，同时把准入决定权留给既有确定性确认 owner（wiring 不改语义、cognitive-program 不新增模型面）。
- **Question:** 哪些显式确认短语可以在零模型调用下解析为 accept-current-proposal，且不放宽 complete-proposal 准入？
- **Necessary adjacent/external contracts:** `human-interaction-contract` HIC-001/004（契约形状与呈现不变）；既有 `_local_phrase_revision` 捷径（对称模式与实现落点）；`admit_research_confirmation`（唯一准入 owner，本 change 不改它）；`AnswerRun` 文本路径（驱动原样传值，本 change 不改驱动）。
- **Evidence seam:** hitl1 节点单测（capabilities stub 的模型调用计数 = 0、短语表正反用例）+ 既有 human-interaction 契约测试 + `check_project_gate.py --phase closeout`。
- **Not in scope:** 提案准入语义任何放宽；新增可见控件；semantic-intake 提示词；嵌入式/Gateway 驱动脚本；其他节点。
- **Triggered review policies:** node-agent-workflow-integrity

## Node Agent Review

| Field | Content |
| --- | --- |
| Surface | hitl1 提案阶段文本回复的分类入口（`_classify_proposal_reply`） |
| Classification | deterministic-guardrail：封闭短语表精确匹配 → 封闭 intent，零模型调用 |
| Bounded cognitive question or no-agent rationale | no-agent（仅对封闭短语）：精确匹配无需认知；不匹配的回复保持既有有界 semantic intake 路径不变 |
| Input authority boundary | 回复文本来自受信 pending-interaction response；不接受隐藏动作 token、部分匹配或歧义输入 |
| Tool posture and runtime enforcer | 不变：intake 零工具；捷径本身不发起任何模型调用 |
| Candidate result and deterministic admission owner | `SemanticCandidate(ACCEPT_CURRENT_PROPOSAL)` → `resolve_semantic_candidate` → `admit_research_confirmation`（complete-proposal 检查）仍是唯一准入 owner |
| Failure owner and bound | 短语表封闭；非匹配回复走既有 intake/repair/失败边界，失败分类与上限不变 |
| Deterministic evidence seam | hitl1 节点单测：stub 模型调用计数为零 + 短语表正反用例 + 既有准入测试 |

边界声明：本 change 不修改 `deerflow/` gitlink，不触碰框架源码；改的是应用侧 hitl1
节点的分类分支与治理/spec 账本。
