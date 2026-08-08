# Plan: OpenSpec Policy Layer 与跨 Session 认知 Guardrails

> 类型: 长程架构与交付跟踪 | 当前阶段: 三项 Change 完成、归档并提交 | 更新: 2026-08-02

## 进度与下一步

**目标：** 用三个彼此独立、可归档的 OpenSpec change，把“实现前先澄清
decision / authority / evidence boundary”的 policy，逐步变成能跨 session 回到当前工作的审查证据链。
它降低遗漏相邻 consumer、错误 authority 与无证据 closeout 的风险；不承诺消除所有 regression。

| 顺序 | OpenSpec change | 交付边界 | 当前状态 | 下一关口 |
| --- | --- | --- | --- | --- |
| 1 | [`add-openspec-control-placement-policy`](../../../openspec/changes/archive/2026-08-02-add-openspec-control-placement-policy/) | 外置 policy、Focus Card review、机械 shape check 与证据登记 | **完成、归档、已提交** `8d8a5f5` | 无 |
| 2 | [`add-openspec-operation-guidance`](../../../openspec/changes/archive/2026-08-02-add-openspec-operation-guidance/) | `rules.tasks` obligation、apply/archive advisory guidance 与六项本地 probe | **完成、归档、已提交** `ba122b8` | 无 |
| 3 | [`add-cross-session-cognitive-guardrails`](../../../openspec/changes/archive/2026-08-02-add-cross-session-cognitive-guardrails/) | 经验证 committed range 的有界 review evidence 与非权威 closeout record | **完成、归档、已提交** `e487a60` | 无 |

### 当前 Checklist

- [x] Change 1：实现、验证、归档、提交。
- [x] Change 2：实现、验证、归档、提交；保留其 `missing-boundary` 与 `unclosed` probe 证据。
- [x] Change 3：完成 proposal-contract 文档级 grill。
- [x] Change 3：完成并验证 OpenSpec proposal、specs、design、tasks。
- [x] Change 3：实现、验证、archive-closeout review、原生归档、提交与终态追踪均已完成（`e487a60`）。

**当前状态：** 三个 change 均已完成、归档并提交。Change 3 的 primary implementation/archive commit 为
`e487a60`；focused guardrail fixtures、Charter/config、主规范、结构、证据、strict OpenSpec 和 diff checks 均通过。
完整离线 gate 保留三项既存 integration 基线失败（期待 mapping、实际为 LangGraph `Command`），未在本 change 越界
修复。`backend/`、`frontend/` 保持无改动。

## Change 3 已确认 Contract

1. **可靠边界是前提。** 没有 selected-change boundary 时仅记录 `missing-boundary`；不声称审查 coverage 或
   semantic clearance，也不写 task 或影响 archive。
2. **调用方声明，Git 验证。** 调用者或适配器提供 boundary fact；Git 拥有 commit identity、ancestor relation
   和 diff 的事实；coordinator 不从共享 worktree、路径名单或分支名推断归属。
3. **显式绑定。** attestation 必含 canonical `change_name`、repository identity、`base_commit`、`head_commit`，
   并采用 `base..head` 语义。
4. **最小确定性证明。** 只接受 committed range，且运行时 `HEAD == head`、worktree clean；验证覆盖 valid
   range、缺字段、错误仓库、非祖先、`HEAD` 漂移和 dirty worktree。
5. **不拥有 archive authority。** Change 3 不包装、替代或阻止 native archive；最多产生可审计的
   `review-required` / `inconclusive` evidence record。真实 finding 必须仍是 `tasks.md` 中的普通未完成任务。

## 固定边界

- `operations.apply/archive.guidance` 始终只是 advisory prompt delivery，不执行命令、不完成任务，也不控制
  apply/archive transition。
- 不修改 `backend/`、`frontend/`、DeerFlow runtime authority、graph/state/checkpoint 或 provider 行为。
- 不让模型、policy 文本或 dossier 自动批准认知质量；现有 deterministic owner、capability spec 和人工判断
  保持各自 authority。
- 每个 change 都必须先完成自己的 proposal、design、specs、tasks、验证、归档和提交，才进入下一项。

## 追踪纪律

- 每次 proposal、apply、验证、归档或提交完成后，更新本页的表格、Checklist 和“现在正在做”。
- 本页只保留当前结论与下一步；证据、原案、审查台账和 probe 细节进入下方配套目录。
- 发现新限制时，先更新本页的 Change 3 contract / 状态，再修改 OpenSpec proposal；不得把 advisory guidance
  描述成已有 enforcement。

## 详细依据

| 文档 | 用途 |
| --- | --- |
| [`policy-gate-injection-layer/README.md`](policy-gate-injection-layer/README.md) | 配套材料的阅读顺序和证据纪律 |
| [`policy-gate-injection-layer/00-program-architecture-review.md`](policy-gate-injection-layer/00-program-architecture-review.md) | 原案快照、审查台账与经审查后的架构建议；仅作详细依据，本页是当前状态 authority |
| [`policy-gate-injection-layer/01-bug-boundary-evidence.md`](policy-gate-injection-layer/01-bug-boundary-evidence.md) | BUG-001～016 的边界/authority 证据与反例 |
| [`policy-gate-injection-layer/02-session-drift-borrowing.md`](policy-gate-injection-layer/02-session-drift-borrowing.md) | session-drift feedback loop 的选择性借鉴与限制 |
| [`policy-gate-injection-layer/03-openspec-1.7-operation-guidance.md`](policy-gate-injection-layer/03-openspec-1.7-operation-guidance.md) | OpenSpec operation guidance 的真实 delivery / authority 边界 |
| [`policy-gate-injection-layer/04-three-change-system-program.md`](policy-gate-injection-layer/04-three-change-system-program.md) | 三项 change 的系统目标、分期依据与决策记录 |
| [`policy-gate-injection-layer/05-operation-guidance-probe-evidence.md`](policy-gate-injection-layer/05-operation-guidance-probe-evidence.md) | Change 2 的六项本地 probe、`missing-boundary` 与 `unclosed` 事实 |
