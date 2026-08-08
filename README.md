# ai_deerflow_deep_research_v2

跑在 **DeerFlow** 之上的 deep research 应用：broad question in, evidence-backed gated research report out。

## 布局

```
deep_research_harness/    ★ 你的应用（deep research runtime，基于 deerflow 的 API 构建）
deerflow/                 被 leverage 的框架（submodule @ ethan，含研究笔记 _digest/_faq），只读
openspec/                 设计规格（openspec CLI 管理）
_backlog/                 任务账本
.claude/skills/           grillme 技能集（grilling/tdd/code-review 等）
```

## 快速开始

```bash
cd deep_research_harness
uv sync                                   # 建 venv
.venv/bin/pip install -e ../deerflow/backend/packages/harness   # editable 装框架
.venv/bin/python -m pytest tests/         # 跑测试
```

## 给 Coding Agent

见 [AGENTS.md](AGENTS.md)——重点是：应用是主角，框架只 leverage 不改。

## 备注

- `deerflow/` submodule 需 `git clone --recurse-submodules` 或 `git submodule update --init` 才完整。
- 框架运行时基座：ethan 分支（digest 笔记描述 e5c62cab，submodule 钉在 ethan HEAD）。
