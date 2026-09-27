# AGENTS.md

本仓库 = **跑在 DeerFlow 之上的 deep research 应用**。两层，顺序很重要：

| 层 | 是什么 | 怎么对待 |
|----|--------|---------|
| `deep_research_harness/` | ★ **你的应用**（`src/deerflow_deep_research`、`scripts`、`tests`、`docs`） | 改代码、写测试、跑它——几乎所有工作在这里 |
| `deerflow/` | 被 leverage 的框架（submodule 锁 `ceebf97f` = 上游 v2.1.0） | **只 import，绝不修改、不为排查翻它内部**；理解框架读它的只读指引 `deerflow/AGENTS.md` 与 `deerflow/backend/AGENTS.md` |
| `openspec/` | 设计与准入（specs / changes / governance / change-guidance） | 契约与规范写这里 |
| `_backlog/` | 任务账本（bugs / plans / todos） | 追踪；搬迁按 ritual |

## 去哪里找规则（渐进披露——根目录只路由，不堆细节）

| 你要做的事 | 唯一入口 |
|-----------|---------|
| 改应用代码（选最小 owner、LLM 节点门、验证命令） | [`deep_research_harness/AGENTS.md`](deep_research_harness/AGENTS.md) |
| 设计/准入一个变更（原则、profile、本地绑定、预算） | [`openspec/change-guidance/README.md`](openspec/change-guidance/README.md) |
| 证据 / 门禁 / 测试资产政策 | [`openspec/governance/`](openspec/governance/)（`test-evidence-policy.md` + 组件 checker） |
| 账本 ritual（编号、索引、计数三处一致） | [`_backlog/README.md`](_backlog/README.md) |
| 运行/运维、测试与评测 | harness [`docs/README.md`](deep_research_harness/docs/README.md) |
| 操作者手册阶梯（001–031） | harness [`docs/runbooks/README.md`](deep_research_harness/docs/runbooks/README.md) |
| 产品方向与快速上手 | [`openspec/product/README.md`](openspec/product/README.md) |

## 不可谈判的约定（只列不变量；细则在各自 owner）

1. **契约/行为变更走 OpenSpec 主干**：proposal（含 Change Focus）→ design / tasks →
   红绿测试先行 → 门禁 → archive；**规范语义的改动由人拍板**。
2. **自证后才交回**：能自证的绝不外推，退出码直测；只断言内部状态、或断言快于 UI 自身
   定时器的，视为未验证；结论不得依赖某台机器的工作区现场。
3. **证据高于感觉**：面向操作者的改动交回前须有**新鲜回执**——回执要新于最后一次改动、
   由 runner 写下命令/退出码/revision；**测旅程不只测单元**；**新守卫必须能变红**；本机
   无法验证的部分显式标注 UNVERIFIED。细则：core 原则 7–8 与本地绑定的 Delivery Lanes。
4. **刻意分歧就地写明**：决定不修的"看似 bug"，在原位留理由 + 一条锁定它的测试。
5. **REVIEW 节制**：产品方向/范围、用户保留区（`.agents/skills/`、`.env`、gitignored 便利件）、
   不可逆或越界（改写历史/push/删他人数据/改 `deerflow/`）、规范语义裁决、用户明确要求
   → 请人；其余（代码质量、命名、测试充分性、文档一致性、bug 定位）**自主 review 后直接交付**。
6. **委派是优化不是默认**：仅当省时/专精/上下文隔离明确超过协调成本才派；互相依赖或共享
   可变状态时硬禁并行；产出按契约回报（可验证句柄 + 失败照实说）。

## 运行

```bash
cd deep_research_harness
uv sync
.venv/bin/pip install -e ../deerflow/backend/packages/harness
.venv/bin/python -m pytest tests/
```

## 边界铁律

1. **应用是主角**——一切产出服务于 `deep_research_harness/` 的构建。
2. **框架是背景板**——`deerflow/` 只被 import，从不被改。
3. **根目录刻意很小**——发现自己在框架内部打转，说明范围错了。
