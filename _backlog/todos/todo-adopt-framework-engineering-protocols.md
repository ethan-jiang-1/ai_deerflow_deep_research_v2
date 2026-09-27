# TODO: adopt-framework-engineering-protocols

> 状态: 待设计 | 优先级: 中 | 更新: 2026-09-27（源自 DeerFlow 借力审计；机制级三项）
> 上游: 无（审计产出） | 下游: 无

## Why

2026-09-27 的 DeerFlow 只读指引借力审计（读 `deerflow/AGENTS.md`、
`deerflow/backend/AGENTS.md` 及其指到的 `backend/tests/AGENTS.md`、
`packages/harness/deerflow/AGENTS.md`、`.../subagents/AGENTS.md`）给出 8 条候选；
其中**流程/文档级 5 条已采纳**（测试卫生节、跨面词汇加法演进 + 契约测试规则、
委派与回报契约、刻意分歧留痕），余下 3 条是**机制级**，需要独立设计与排期：

## Current Direction（三项机制）

1. **bounded-run `stop_reason` + 部分可用结果指引**
   （来源 `subagents/AGENTS.md:32`）：任何因预算/上限而结束的 run（subagent 上限、
   eval 预算、live 预算）都应在 run 记录/账本里给出**加法式** `stop_reason` 字段，
   并说明"已产出部分结果可复用"——避免把被截断的 run 读成干净完成。
   落点候选：evaluation 报告契约、live 预算失败路径、账本卡片模板。
2. **评测可复现协议**（来源 `backend/AGENTS.md:96-113`）：外部数据集以不可变
   revision + SHA-256 钉住；**绝不静默下载**；合成/脚本化输入必须标注 synthetic；
   凭证只从具名环境变量读取；model id/参数/prompt/seed/clock 版本化；结果里记录
   config、manifest、dataset、git revision。（本仓离线门与控制摘要已覆盖；缺
   dataset 钉住、禁静默下载、版本化记录。）
3. **waiver 绑定内容哈希**（来源 `deerflow/AGENTS.md:99-108`）：预算/时长豁免除
   reason + owner + expiry 外，还应绑定被审对象的内容哈希、到期后可复核、在门禁
   输出中可见，且**永远不能豁免 blocker 级发现**。（本仓 waiver 机制见
   `docs/testing-and-evaluation.md` 相关小节。）

## Design Questions

- 这三项各自是否需要 spec 面（evaluation-hardening / project-structure）还是纯机制实现？
- `stop_reason` 的 owning 契约在哪层（run 记录 schema？账本卡片？报告契约？）——
  加法演进需按 config.yaml design 规则以契约测试钉住。
- 评测可复现里哪些项对本仓**不适用**（我们不下载数据集；Tavily 是运行时工具而非
  评测数据集）——只采纳真正适用项，避免为对齐而造表面机制。

## Non-Goals

- 不修改 `deerflow/` submodule；不引入为对齐而生的空转机制。
- 不与 BUG-071（工作台 UI conformance）混做——那是用户可见价值，优先级更高。

## Next Step

先出 `openspec explore` 或一份短 design：逐项判定 owning 层与"适用/不适用"，
再决定是否拆成 1–3 个 change 排期。
