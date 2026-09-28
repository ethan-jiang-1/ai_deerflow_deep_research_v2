# BUG-077: 调试器组合的 embedded 首屏被 020 侦察屏覆盖——launcher 承诺的工作台从键盘不可达

> 严重级别: P1 | 发现: 2026-09-28 | 状态: 已修复（2026-09-28，change `repair-embedded-tui-first-live-defects`）

## 症状

`./run/tui-workflow-debugger.sh --embedded-smoke`（launcher 注入 `--debug`）启动后，
操作者看到的不是工作台首屏（「姿态: 无调试会话…」+ New Run/Attach/Replay），而是
020 侦察横幅；composer Enter 也被路由进侦察聊天（触发 BUG-076 的 ValidationError），
而不是 `_debug_start`。fixture 调试器无此问题。

## 根因

`scripts/demo_tui.py` `_initialize` 的 mount 路由：`if self.debug_mode:` 先正确渲染
工作台首屏（`_render_no_debug_session`），但随后的 `elif self.mode == "embedded_smoke":`
分支**没有 `debug_mode` 守卫**——embedded+debug（无 attach/replay intent）落进去，
把首屏覆盖成 `_render_recon()` 并置 `_onboarding = True`；输入路由里
`if self._onboarding: await self._handle_onboarding_input(value)` 先于 debug 分支，
composer Enter 从此与驱动无缘。fixture 不进该 elif，所以只在 embedded 组合暴露。
无头探针实证：mount 后 `ONBOARDING: True`、composer placeholder 变成侦察文案。

## 复现

```bash
cd deep_research_harness && ./run/tui-workflow-debugger.sh --embedded-smoke
# 首屏应为「姿态: 无调试会话」工作台；修复前是 020 侦察横幅
```
（无头等价：`tests/integration/test_debugger_entry.py` 的
`test_embedded_debugger_mounts_the_workbench_not_recon`，修复前红。）

## 修复关联

change `openspec/changes/repair-embedded-tui-first-live-defects`：020 recon 分支加
`not self.debug_mode` 守卫——debug 组合保持工作台首屏、`_onboarding` 保持 False、
composer Enter 走 `_debug_start`（与 fixture 工作台一致）。同类先例：
`repair-debugger-cli-entry-conformance` / `repair-debugger-entry-env-conformance`
（BUG-069/070/071/075，"文档承诺、实现缺口" 的入口 conformance 类）。
