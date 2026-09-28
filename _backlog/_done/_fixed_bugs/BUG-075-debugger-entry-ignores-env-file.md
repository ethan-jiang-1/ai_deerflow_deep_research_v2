# BUG-075: 调试器入口链不加载 .env，文档承诺的 embedded-smoke 前置检查对 .env 用户失效

> 严重级别: P1 | 发现: 2026-09-28 | 状态: 已修复（2026-09-28）

## 症状

操作者按 runbook-031 执行 `cd deep_research_harness && ./run/tui-workflow-debugger.sh --embedded-smoke`，
`.env` 三变量（`DEEPSEEK_API_KEY`、`TAVILY_API_KEY`、`DEERFLOW_DEMO_MODEL`）齐备且网络可达，
首屏仍报：

```
模型配置尚未就绪。
Next: 配置一个受支持的模型后重新开始。
Retryable
Contained Event Journal record is unavailable.
```

（尾行为设计内诚实陈述：preflight 失败发生在任何 bundle 创建之前，`journal_record_created=False`。）

## 根因

两层机制，非配置错误：

1. **入口链缺口**：Makefile demo 目标与 `run/real-research.sh` 都经
   `uv run --env-file .env` 注入；但 canonical 调试器 launcher 直接 `exec python
   scripts/demo_tui.py`，launcher、`demo_tui.py`、`_demo_core.py` 全链路无任何
   显式 `load_dotenv`。`demo_readiness_report(mode="real")` 只读 `os.environ`。
   `demo_tui` 是唯一没有 `.env` 加载包装的 demo 入口。
2. **框架隐式加载锚定错误**（红测构建时发现）：deerflow 框架
   `app_config.py:59` 在 import 时即 `load_dotenv()`（隐式 `find_dotenv`），
   但 file 模式运行时其锚点从框架包目录向上走，够不到 harness 根，反而捞到
   **仓库根的 `.env`**（操作者机器上缺 `DEERFLOW_DEMO_MODEL`）——这解释了为何
   操作者屏幕只报 model_missing 而 web_tool 检查通过。`-c` 模式下 `find_dotenv`
   回退到 cwd，能碰到 harness `.env`——`-c` 探针因此会说谎，回归测试必须用
   file 模式子进程。

差分探针证实：同一就绪检查对裸 launcher 环境读 False，显式
`load_dotenv("<harness>/.env")` 后读 True；app-seam file 模式子进程探针在变量
仅存在于 env 文件时先红（`configuration.model_missing`）、经加载器后绿（`Ready`）。

## 复现

```bash
cd deep_research_harness && ./run/tui-workflow-debugger.sh --embedded-smoke
# 首屏即 configuration.model_missing（.env 三变量在文件中而非 shell export 时必然复现）
```

## 修复关联

change `openspec/changes/repair-debugger-entry-env-conformance`：`_demo_core` 增
`load_local_environment()`（`override=False`，`DEMO_ENV_FILE` 测试 seam），`demo_tui`
app 构造首行调用；红先行的子进程探针锁定（embedded_smoke 从 temp `.env` 单独到达
`Ready`）。同类先例：`repair-debugger-cli-entry-conformance`（BUG-069/070/071 同为
"文档承诺、实现缺口" 的入口 conformance 类）。刻意不扩：`demo_real.py` 两个已文档
入口均已在上游加载 `.env`，无需改动。

## 修复（2026-09-28，change `repair-debugger-entry-env-conformance`）

- 修复：`scripts/_demo_core.py` 新增 `load_local_environment()`；`scripts/demo_tui.py`
  的 `DeepResearchDemoTUI.__init__` 首行调用，全部构造路径（launcher main、无头探针、
  测试）在就绪门读取环境前看到 harness `.env`。
- 红绿证据：file 模式子进程探针先红（`configuration.model_missing` /
  模型配置尚未就绪，与操作者屏幕逐字一致）后绿（`Ready`）；加载器契约单测 4/4
  先 ImportError 后绿。
- 门禁：`UV_OFFLINE=1 make verify` exit 0（2739 fast + 355 integration + 35
  workflow）、`make tui-journey` exit 0、`make debugger-proof` exit 0（五链路全绿）、
  closeout/strict/hygiene/diff-check 全 0；gitlink ceebf97f 未动。
- 已知边界（design Risks）：框架 `find_dotenv` 的隐式加载先于修复运行，故仓库根
  `.env` 与 harness `.env` 对同名键冲突时，launcher 模式下仓库根值胜出（与修复前
  launcher 行为一致）；缺失键——本 bug 的实际失败面——由 harness `.env` 补齐。
