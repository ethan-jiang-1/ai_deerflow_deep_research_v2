# BUG-071: RED-014 剩余 UI 面——命令面板归一、Node Context 分栏、Files 分栏

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 活跃

## 症状

RED-014 要求调试工作台"第一屏呈现三个显式入口（New Run / Attach / Replay），
按钮、命令面板动作与 slash 命令归一到同一 typed adapter action"，并"呈现 Node
Context 分栏（选中帧的 node-agent 调用 + 固定 coverage strip）"与"Files 分栏
（消费 `OperatorWorkspaceReader` typed pages）"。当前已落地按钮/slash/启动参数
三入口等价与 attach/replay 消费（BUG-069 已关闭），**但仍缺**：

- 命令面板（Textual command palette）动作——第三条等价通路；
- 专门的 Node Context 分栏：现在 `/context` 把捕获信息写进日志区，没有独立分栏，
  也没有 coverage strip（INITIAL CAPTURED / RUNTIME ENFORCED / ACTIVITY BOUNDED /
  OUTCOME OBSERVED-UNAVAILABLE / FILES CURRENT / raw provider histories NOT RETAINED）；
- Files 分栏：`OperatorWorkspaceReader` typed pages 未接入 UI。

## 根因

CLS-058 的 `2026-09-02-connect-tui-workflow-debugger` 为部分落地（提交 `e7b0c9e`
自述 "partial apply, plan checkpoint"）；其 tasks.md 全部标 [x] 但 UI 面只完成
调试驱动接线与 composer 通路。BUG-069 收尾了入口/消费，UI 分栏与命令面板仍缺。

## 复现

```bash
cd deep_research_harness
./run/tui-workflow-debugger.sh --fixture     # 第一屏只有按钮行，无 Node Context / Files 分栏
# Ctrl+P（命令面板）里没有 New Run / Attach / Replay 动作
```

## 修复关联

- 命令面板：Textual `App.COMMANDS` + 自定义 Provider，把三个动作注册为命令，
  与按钮/slash 共用同一组 typed 方法（`_debug_new_run`/`_debug_attach`/`_debug_replay`）。
- Node Context 分栏：把 `_debug_render_context` 的输出从日志区移到独立 `Static`/
  分栏组件，并加上固定 coverage strip（来源：`NodeContextStore.page()` 的 coverage
  字段 + 原始 provider 历史的 NOT RETAINED 声明）。
- Files 分栏：接入 `OperatorWorkspaceReader` typed pages（`runtime/workspace_reader.py`）。

回归：`make tui-journey` 增断言（三个动作在命令面板可命中、分栏存在且 coverage strip
文本完整、Files 分栏读到的页受 reader 约束）。spec 无需 delta（RED-014 条款已在，
属实现追平）。
