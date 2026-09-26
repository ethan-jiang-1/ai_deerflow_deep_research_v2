# Design

## Context

`_classify_proposal_reply`（`graph/nodes/hitl1/node.py`）是提案阶段回复的分类决策点：
现有确定性捷径只覆盖"短语修订"（`_local_phrase_revision` → REVISE_PROPOSAL，零模型），
显式确认则落入语义解析模型调用。2026-09-26 实跑证明该调用在 provider 流式抖动下
成批失败，操作者的显式确认被判"未识别"（完整取证见
`_backlog/plans/demo-real-gateway-closeout.md`）。

## Goals / Non-Goals

**Goals:**

- 显式确认短语零模型映射为 ACCEPT_CURRENT_PROPOSAL，demo 阶梯对链路抖动鲁棒。
- 与 `_local_phrase_revision` 对称的实现形态与测试形态。
- 准入语义零变化：complete-proposal 检查与唯一准入 owner 不动。

**Non-Goals:**

- 不放宽准入、不加可见控件、不动 semantic-intake 提示词与预算。
- 不改驱动脚本（`scripts/demo_real.py`）与 Gateway/observer 路线。
- 不为其他意图（取消、澄清等）新增确定性捷径。

## Decisions

1. **短语表封闭且冻结**（`confirm`、`确认`，模块级 frozen 元组，紧邻
   `_local_phrase_revision` 的短语处理）：精确全匹配（strip 后整体相等，大小写不敏感
   仅对 ASCII），不做子串/混合匹配。备选"正则/模糊匹配"被否——模糊会重新引入歧义，
   正是认知解析存在的理由。
2. **返回 SemanticCandidate 而非直接改状态**：与修订捷径同构，保持"候选 → 确定性
   解析 → 准入 owner"的既有链路；`resolve_semantic_candidate` →
   `admit_research_confirmation` 的 complete-proposal 检查自然处理不完整提案
   （outstanding + 重入 intake），无需捷径自行判断完整性。
3. **大小写处理**：`confirm`/`CONFIRM`/`Confirm` 等价（ASCII casefold）；中文短语
   无大小写问题。
4. **spec 显式化**：ADDED `HIC-005` 而不是"无 delta"——本仓库纪律是行为入 spec；
   虽然契约形状不变，但"哪些输入零模型"是 HITL1 认知边界的一部分，写进 spec 防止
   未来被无意改回。

## Risks / Trade-offs

- [封闭短语表可能漏掉操作者的其他确认说法（"ok"、"yes"）] → 有意为之：表越封闭越
  不歧义；未命中走认知路径，失败分类不变。后续可经 change 增补短语。
- [捷径让部分确认绕过认知评估] → 该"评估"对显式确认没有增值（确定性映射等价于
  控件选择 DirectConfirmation 的既有零模型通路）；认知面保留给一切非显式输入。
- [回滚] → 单分支删除即回滚；spec delta 归档历史可检索。

## Migration Plan

无数据/状态迁移。实现 = 分类入口前置一个封闭短语分支 + 测试；回滚 = 还原该分支。

## Open Questions

（无——短语表范围、实现形态、spec 显式化均已在 proposal/design 定案。）
