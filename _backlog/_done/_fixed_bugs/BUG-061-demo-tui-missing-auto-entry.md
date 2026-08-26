# BUG-061: Demo TUI 缺少 010 自动全跑入口（--auto / scripted start）

> 严重级别: P1 | 发现: 2026-08-21 | 状态: 已修复（2026-08-25）

## 症状

010 runbook 原意是"自动 TUI 全跑"（同一固定问题，真人零操作，TUI 自主跑到
终态），但 `scripts/demo_tui.py` 的 composer 提交永远构造
`StartRun(question=value)`（`scripted=False` 默认，demo_tui.py 原 605 行），
且没有任何 `--auto` / `--scripted` 开关。全自动机制只存在于 CLI
（`make demo-real-scripted` = `demo_real.py --embedded-smoke --scripted`）。
结果：TUI 一层无法复现 010 自动形态，`RUN-010.command` 类入口无从拉起
"自动全跑"。

## 根因

Demo TUI presentation adapter 没有把 graph 已支持的 scripted 起始契约
（`StartRun(scripted=True, profile_intent=None)` → `non_interactive_policy`
`auto_profile` + `auto_proceed`，见 `runtime/run_experience.py::_prepare_intent`）
投影成一个显式入口：`_initialize` 在 preflight 通过后只发布 `Ready` 并等待
composer 输入，缺少"就绪后自动派发固定问题"的分支。

## 复现

```bash
cd deep_research_harness
make demo-tui-embedded-smoke   # 只能手动；没有任何 flag 能自动派发 scripted start
```

期望存在 `make demo-tui-real-auto`（`demo_tui.py --embedded-smoke --auto`），
启动后自动跑完，真人零按键。

## 修复关联

openspec change **`add-demo-tui-auto-entry`**（2026-08-25 闭环：
propose → polish → apply → archive，归档为
`openspec/changes/archive/2026-08-25-add-demo-tui-auto-entry/`）：

- `scripts/demo_tui.py`：新增 `--auto`（仅限 `--embedded-smoke`；`--auto`
  无 `--embedded-smoke` 在 argparse 报错）；`_initialize` 就绪后若
  `mode == "embedded_smoke" and auto`，自动
  `_dispatch(StartRun(question=AUTO_QUESTION, scripted=True, profile_intent=None))`；
  固定问题 = 003 同款 `What is one bounded fact about China's EV battery market in 2024?`；
  banner 标注 `· auto`；parser 构造/校验抽为 `_build_parser`/`_validate_args`
  （demo_sessions 先例，供确定性测试）。
- `Makefile`：新增 `demo-tui-real-auto` target（010 自动入口）。
- `tests/integration/test_demo_tui.py`：3 用例——auto 派发 scripted StartRun
  且直达 Terminal；fixture+auto 仍保持交互；`--auto` 无 `--embedded-smoke`
  argparse 拒绝（apply 阶段补齐 scenario 2 缺口）。
- 契约：delta spec 新增 **RED-010**（research-demo-tui 显式零人工自动入口），
  同步进主 spec；`openspec/governance/req-registry.yaml` 登记 RED-010。

运行笔记：原集成测试两个新用例首次跑失败，根因是 (a) auto dispatch 未限定
`mode == "embedded_smoke"` 导致 fixture 也触发，(b) 测试等待 `Ready` 而 auto
直达 `Terminal`；均已修正。验证：3 auto 用例全绿 +
`UV_OFFLINE=1 make verify` 全绿（fast 2650 + integration 301[4 skipped] + workflow 35）。
