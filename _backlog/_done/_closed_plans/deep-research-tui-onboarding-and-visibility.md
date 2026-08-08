# Plan: Deep Research TUI — 启动引导与阶段可见性

> 类型: 设计 | 更新: 2026-07-19

## 背景 / 现状

`make demo-tui` 进去之后，所有面板一次性渲染——welcome panel、pipeline tracker（显示 welcome 内容）、log 区、输入框——小白不知道看哪里、第一步该做什么。这是当前最核心的瓶颈：**启动体验没做好，后面的交互无从谈起**。

### 当前启动屏幕的问题

1. Welcome 文字塞在 `#pipeline` widget 里（`_welcome_text()` → `id="pipeline"`），和 pipeline tracker 共用同一个视觉区域，信息混淆
2. "Enter a research question ↓" + 预填输入框 + "Ready. Type a question..." 三条引导信息同时出现，互相稀释
3. Pipeline tracker 在 question stage 显示 welcome text 而非 pipeline 状态，角色不清
4. Log 区空白但可见，增加了视觉噪音

### 约束

- TUI 代码在 `agent/scripts/demo_tui.py` + `_demo_core.py`，是 extra layer
- 不能动 `deerflow_deep_research` 包（nodes、graph、runtime、domain/engine）
- 可以加 `extra` 依赖到 `pyproject.toml`
- 交互应该是自然的、有智力的引导，不是填配置表单

### 额外修复：real mode 需要 web tools

`DemoAppConfig.tools = []` 导致 real mode Wave0 找不到搜索工具 → gate_blocked。需要从 `.env` 注入 tools，这是让 real mode 能跑的前提。

## 决策

### 决策 1：启动屏幕 = 单输入模式

启动阶段（question stage）简洁到只有一个动作入口：

1. **一个简短标题**（"Deep Research" 或类似）
2. **一行引导语**："输入你的研究问题，回车开始"
3. **突出的大输入框**，预填一个示例问题

没有 pipeline tracker、没有 log、没有 welcome panel、没有多余信息。小白进来，看到输入框，知道 "哦，输入问题就能开始了"。

Pipeline tracker 和 log 在 start 成功后（进入 hitl1 stage）才逐步展开。

### 决策 2：保持纯文本交互，不做结构化表单

HITL-1 和 HITL-2 维持自由文本 / 选项文本交互，不做下拉选择。交互引导靠**清晰的 prompt 文字 + 具体的例子 + 解释这个选择会影响什么**。

### 决策 3：Pipeline tracker 只在 processing 阶段展示

- Question stage：隐藏
- HITL-1 stage：隐藏（或只显示一行 "等待你确认研究范围…"）
- Processing 阶段（HITL-1 resume 到 HITL-2 之间）：展开 pipeline tracker，展示 phase 进度
- HITL-2 stage：保留 pipeline tracker 但缩小，给决策选项让出视觉空间
- Terminal：展示完成摘要

### 决策 4：fake TUI 用于快速迭代

加 `--fake` flag。fake mode 零依赖、不用 API key、代码路径完全一样（同样的 stage 切换、同样的 UI），只是底层用 `full_fake` recipe。让你和 AI 能在秒级反馈循环里迭代 TUI 交互。

```bash
make demo-tui       # real mode（需要 API key）
make demo-tui-fake  # fake mode（零依赖，迭代交互设计）
```

### 决策 5：现阶段不做 streaming / 节点内部可见性

当前 `run_deep_research()` 是阻塞调用，中间拿不到进度。要让 TUI 在 processing 阶段看到节点内部，需要改 graph 执行路径（`astream_events` 或 callbacks）。这超出了 extra layer 边界风险。先做好启动和阶段引导，后续需要再看。

### 决策 6：修复 DemoAppConfig tool 注入

在 `_demo_core.py` 里检测 `TAVILY_API_KEY`，有则注入 web search tool spec。不改 core tool resolution。

## 实施范围

只动这些文件：

| 文件 | 改动 |
|------|------|
| `agent/scripts/demo_tui.py` | 重写 compose/layout、stage 切换逻辑、启动屏幕 |
| `agent/scripts/_demo_core.py` | 注入 web tools 到 DemoAppConfig |
| `agent/Makefile` | 加 `demo-tui-fake` target |
| `agent/pyproject.toml` | 可能加 demo-tui 的 extra（若需要新 Textual widget 依赖） |

不动 `deerflow_deep_research` 包。

## 风险

- [风险] 加入 pipeline tracker 的动态显示/隐藏后，可能在不同终端尺寸下布局错乱 → 缓解：用 Textual 的 `visible` + `display` 属性而非 mount/remove，CSS 用 fr 单位自适应
- [风险] `--fake` flag 增加维护面 → 缓解：fake 和 real 走完全相同的 UI 代码路径，唯一区别是 `build_demo_recipe(mode=...)` 参数，维护成本约等于零

## 落地

产出一个 OpenSpec change：`improve-deep-research-tui-onboarding`
