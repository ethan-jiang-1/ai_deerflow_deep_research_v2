# Fixed Bugs Index — 已修复 bug 归档

> 最后更新: 2026-08-11 | `_backlog/_done/_fixed_bugs/` — 已修复 bug 的归档目录。
> 接收来自 [`../../bugs/`](../../bugs/) 的 bug。`_` 前缀 = coding agent 默认忽略。
>
> **本目录是 bug 编号的唯一权威来源——新 bug 的编号 = 本目录最大编号 + 1。**

## 接收一个修完的 bug

bug 修完后从 `_backlog/bugs/` 通过 `git mv` 移入本目录：
1. 在本文件表格加一行（ID + Date + Title）
2. 更新下面的 "Next available bug ID"
3. 更新 `../../bugs/README.md`（删掉该 bug）
4. 更新 `../README.md`（计数 +1）

---

| ID | Date | Title |
|----|------|-------|
| BUG-001 | 2026-07-23 | HITL1 localized intake and explicit confirmation |
| BUG-002 | 2026-07-23 | Retained run diagnostics are actionable |
| BUG-003 | 2026-07-23 | Real CLI run state is observable |
| BUG-004 | 2026-07-23 | LangGraph checkpoint msgpack registration |
| BUG-005 | 2026-07-23 | Wave0 real worker failure classification is no longer opaque |
| BUG-006 | 2026-07-24 | `make demo` 将无效 HITL2 选择误报为协议错误 |
| BUG-007 | 2026-07-24 | HITL2 delegates an agent-led route decision to the user |
| BUG-008 | 2026-07-25 | 真实 demo 的模型超时现在有受限恢复和可操作诊断 |
| BUG-009 | 2026-07-25 | HITL2 zero-tool fixture omits the required Wave2 predecessor |
| BUG-010 | 2026-07-26 | Topic planning timeout is reported as an opaque blocked research run |
| BUG-011 | 2026-07-26 | Completed final delivery skips its gate and loses declared repair routes |
| BUG-012 | 2026-07-26 | Terminal CLI diagnostic reference diverges from its retained run bundle |
| BUG-013 | 2026-07-31 | HITL1 natural confirmation is no longer parsed as profile data |
| BUG-014 | 2026-07-31 | Provider timeout diagnostics identify their observed timeout origin |
| BUG-015 | 2026-07-31 | Provider-terminal inspection command is module-local and executable |
| BUG-016 | 2026-07-31 | Supplied terminal diagnostic references are published before projection |
| BUG-017 | 2026-08-02 | Topic planning 的零工具停止被误报为研究工具失败 |
| BUG-018 | 2026-08-02 | Topic planning 的 provider timeout 未被分类为可恢复错误 |
| BUG-019 | 2026-08-02 | 未指定两条比较路线的研究仍可被确认并启动 |
| BUG-020 | 2026-08-02 | 普通确认语仍依赖模型语义分类，导致 HITL1 不稳定 |
| BUG-021 | 2026-08-02 | 研究语言未绑定到用户请求语言 |
| BUG-022 | 2026-08-03 | 真实研究演示的瞬态 Tavily 读取不再首次失败即终止；历史红绿差分证明两次有界恢复。 |
| BUG-023 | 2026-08-03 | HITL1 brief prompt 不再要求 strict schema 禁止的语言字段；历史 prompt/parser 差分证明契约兼容。 |
| BUG-024 | 2026-08-11 | Wave0/Wave1 的模型可见闭合输出 envelope 使真实 demo 通过受影响阶段，且 Journal 保留脱敏的结构化失败证据。 |
| BUG-031 | 2026-08-16 | 缺少窄而真的三波调试路径 |
| BUG-025 | 2026-08-16 | 进行中的 Bundle 被投影为 `protocol.invalid_result` |
| BUG-026 | 2026-08-16 | Gate fatigue 没有区分失败的工作单元 |
| BUG-027 | 2026-08-16 | Wave1 SourceDiagnostic 提示词漏掉枚举契约 |
| BUG-030 | 2026-08-16 | 真机 demo 长时间运行没有实时人类可读轨迹 |

**Next available bug ID: BUG-032**

---

## Suspended (未修复，仍在排查)

悬挂 bug 放在 [`../_suspended_bugs/`](../_suspended_bugs/)，尚未确认修复。此处不列。
