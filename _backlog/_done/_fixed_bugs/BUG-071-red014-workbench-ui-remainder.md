# BUG-071: 调试工作台 RED-013/RED-014 剩余面（chooser、命令面板、分栏、候选面）

> 严重级别: P2 | 发现: 2026-09-27 | 状态: 已修复（2026-09-27）

## 症状

RED-013/RED-014 要求的工作台面仍有未交付部分。已交付的是入口/消费子集
（BUG-069 关闭：attach/replay 消费 + 按钮/slash/启动参数三路径等价），以下仍缺：

1. **RED-013 无参组合选择器**：规范要求"无参数启动时 SHALL 进入调试器组合选择器；
   `--fixture` / `--embedded` 预选组合"（research-demo-tui spec:378-380）。现实：
   裸 `./run/tui-workflow-debugger.sh` 落到 gateway 模式（`profile=None`）→ 报
   "A selected local Gateway profile is required"。启动器 help 里的裸调用行已删，
   但选择器本身未实现。（`--embedded` 作为 `--embedded-smoke` 的无歧义前缀可被
   argparse 接受，属可用但未文档化为权威拼写。）
2. **RED-014 命令面板归一**：规范要求"按钮、命令面板动作与 slash 命令归一到同一
   typed adapter action"（spec:402-403）。当前无 `COMMANDS`/Provider，命令面板
   这条等价通路缺失。
3. **RED-014 Node Context 分栏 + coverage strip**：要求独立分栏呈现选中帧的
   node-agent 调用，并带固定 coverage strip（INITIAL CAPTURED / RUNTIME ENFORCED /
   ACTIVITY BOUNDED / OUTCOME OBSERVED-UNAVAILABLE / FILES CURRENT / raw provider
   histories NOT RETAINED）（spec:404-406）。`/context` 目前把内容写进日志区
   （`demo_tui.py` 的 `_debug_render_context`），无独立分栏、无 strip。
4. **RED-014 Files 分栏**：要求消费 `OperatorWorkspaceReader` typed pages
   （`runtime/workspace_reader.py`）；当前未接入 UI。
5. **RED-014 attach 候选面**：要求 Attach 入口给出"有界、经生命周期校验的候选 +
   busy/read-only 与 takeover 姿态"（spec:400-401）。当前 `_debug_attach` 只接受
   composer 里的单个 bundle id，姿态逻辑仅存在于 `open_attach` 内部。

## 修复（2026-09-27，change `complete-debugger-workbench-conformance`）

五项全部落地，每项以 `make tui-journey` 逐步语义断言验证并锁进 `make verify`：

1. **无参 chooser**：交互式菜单；非交互式取文档化默认（fixture 调试器，不读 stdin）；
   `DEBUGGER_COMPOSITION` / `DEBUGGER_PROFILE` 供脚本显式选择。红测覆盖默认 /
   embedded-smoke / gateway 缺 profile（退 2 + 指引）/ gateway 带 profile。
2. **Node Context 分栏 + coverage strip**：`/context` 填充独立 `#node-context`；
   strip 从 `NodeContextView` 自身字段投影（INITIAL/RUNTIME/ACTIVITY/OUTCOME/
   FILES/RAW PROVIDER HISTORIES），空态诚实；strip 由聚焦测试钉住。
3. **attach 候选面 + 姿态**：`/attach`（无参）列出有界候选（最近 5 个 run bundle
   目录，与 operator inventory 同布局）+ 姿态；姿态由 driver 新增只读
   `attach_posture()` 给出（takeover/rebind/busy/unresolvable），候选经生命周期
   校验后才用，绝不自动选"最新"。
4. **命令面板归一**：`WorkbenchCommands` provider 注册三动作，与按钮/slash 同一组
   typed 方法；用真面板无头驱动断言同效。
5. **Files 分栏**：`/files` / `/files <path>` 消费 `OperatorWorkspaceReader` typed
   pages（workspace/uploads=MODEL_READ，outputs=OPERATOR_ONLY），只渲染 alias 与
   相对路径，绝不泄露 host 路径。

**过程中 harness 抓到两个真实缺陷并修复**：attach 候选我按 `bundles/*.json`
记录找（真实布局是 bundle 目录）；`OperatorWorkspaceReader` 对符号链接根
（macOS `/var`→`/private/var`）在 `relative_to` 抛 `ValueError` 而非 typed page
——已把可信根在构造时规范化，并加符号链接根回归测试。

**流程账**：`/cancel`、journey harness、`make tui-journey` 曾超出前一个 change 的
tasks 范围（已在上一版卡片记录）；本次五项全部落在本 change 的 tasks 内。

## 根因

CLS-058 的 `2026-09-02-connect-tui-workflow-debugger` 为部分落地（提交 `e7b0c9e`
自述 "partial apply, plan checkpoint"），其 tasks.md 全部标 [x] 但 UI 面只完成
调试驱动接线与 composer 通路；BUG-069 收尾了入口/消费，其余 UI 面仍缺。

## 流程账（本轮 self-review 发现，记录以备今后遵循）

change `repair-debugger-cli-entry-conformance` 的 tasks.md 只覆盖入口链修复；
`/cancel` 恢复路径、`scripts/tui_journey_probe.py` + `make tui-journey`、
`docs/testing-and-evaluation.md` 的 playbook 节均**超出该 change 的已声明范围**，
属"实现先行"。它们未改变 spec 拥有的行为语义（`/cancel` 映射 driver 既有闭命令
`cancel`+`detach`；harness 是验证资产），故按宪章 §1 的"小改可直提"处理，但今后
同类新增面应**先落到某个 change 的 tasks 或单开 change**，避免账实不符。

## 修复关联

- chooser：裸启动进一个最小组合选择视图（fixture / embedded-smoke / gateway
  profile），或经 change 修订 RED-013 措辞（规范语义变更需人拍板）。
- 命令面板：Textual `App.COMMANDS` + Provider，把三个动作注册为命令，与按钮/slash
  共用同一组 typed 方法。
- 分栏：Node Context 从日志区移到独立分栏 + coverage strip（来源
  `NodeContextStore.page()`）；Files 接入 `OperatorWorkspaceReader` typed pages。
- 候选面：列出 `discover_active` 的候选并呈现 busy/read-only/takeover 姿态。

回归：`make tui-journey` 增断言（选择器路径、命令面板命中、分栏存在且 strip 文本
完整、候选面姿态），并把"日志区视图"的断言替换为分栏断言。
