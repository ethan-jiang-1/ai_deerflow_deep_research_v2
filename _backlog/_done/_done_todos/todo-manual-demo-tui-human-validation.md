# TODO: manual-demo-tui-human-validation

> 状态: **已退役（DONE-007，2026-09-27）**——价值收窄至一寸组合缝且本质只能
> 真人执行；退役归宿 = runbook-020 顶部的"验收状态"注记（可选操作员自检）。
> 优先级: 低 | 更新: 2026-09-27
> 上游: plan demo-real-gateway-closeout.md（G3 TUI 分诊遗留项，plan 已归档 CLS-060） | 下游: runbook-020 §验收状态

## 终局处置（2026-09-27）

用户拍板"对齐当前 codebase，该清理的清理掉"。裁决依据（2026-09-26 深夜复审 +
Pilot 覆盖矩阵查证）：

- 未测增量已收窄为唯一组合缝：真实运行时 × 真 Textual 输入组件（两侧各自有
  Pilot 确定性覆盖：`test_demo_tui.py` 组件行为、`test_gateway_demo_tui.py`
  UI 契约，均对 fake 驱动）；
- 该路线在 Entry Surfaces 表明确标注 "Not a current Primary User TUI"；
- Pilot 真组合自动化成本 > 风险（明确不做）；
- 一张挂着的 agent 侧 todo 无法推动"用户方便时按键"，反而污染账面。

处置：runbook-020 顶部加"验收状态"注记——任何操作员跑通一次即在 §7 记录
证据并勾销注记，失败按 §7 报 bug。追踪职责就地转移，todo 关闭。

以下为历史判断记录，供追溯。

## Why

demo-tui（Gateway + 手动 HITL）路线的**研究层阻塞全部死亡**，剩余唯一未测增量
是"谁来按键盘"：管道 stdin 无法驱动 Textual 输入组件，沙箱禁 openpty。真机已
证明同一研究链在 CLI（demo-real）与 TUI auto（embedded）两路线完成。

## 现状对齐（2026-09-26 深夜复审补全）

- `demo-tui-real-auto`（嵌入式全真 + 自动 HITL）：✅ 通过——"Research completed"，
  report.md + claim-citation-map.json 发布，`_validate_final_artifacts` 通过。
- `session-workbench`：fixture 模式只读投影 UI 正常渲染 ✅。
- `RUN-020.command` 双击启动器完好（尾部指向 runbook-020 均有效）。
- **Pilot 覆盖矩阵（新查证）**：两侧各自已有确定性覆盖——
  `test_demo_tui.py` 用 Textual Pilot 驱动输入组件行为（choice prompts、
  visible controls、natural text、cancel intent），但对 fixture/embedded fake；
  `test_gateway_demo_tui.py` 用 Pilot 驱动 gateway 模式 UI 契约（composer 禁用、
  cancel 可见性、fault ≠ completion），但对 fake Gateway client。
  **未测增量收窄为唯一组合缝：真 Gateway × 真 Textual 输入组件**（widget →
  adapter → Gateway transport → 外层 agent → 研究链的一整条真组合）。
- 该路线在 Entry Surfaces 表中明确标注 "Not a current Primary User TUI"
  （操作员/演示便利面，非产品面）。

## Current Direction

**真人路线是唯一值得做的路径**（设计意图的正路）：用户在真机双击
`RUN-020.command`，按 runbook-020 在 TUI 里完成 HITL1 问答，验收
"Research completed" + 产物发布。

**Pilot 无头驱动明确不做**：两侧各自已有 Pilot 覆盖，补真组合自动化脚本的成本
远大于这条"最后一寸"集成缝的风险；不为自动化而自动化。

## 裁决备注（2026-09-26 深夜）

保留为低优先级用户裁量项：成本为零（卡片放着不碍事，launcher/runbook 全就绪），
收益为一寸集成缝的一次性真人证明。若用户对手动 TUI 路线无兴趣，可退役本卡
并把"此路线未做真人验收"标注并入 runbook-020 作可选操作员自检；在此之前不删。

## Non-Goals

- 不改研究层代码——CLI 与 TUI auto 两路线已证明研究链健康。
- 不写 Pilot 真组合自动化（成本 > 风险）。

## Next Step

用户在方便时跑一次 `RUN-020.command`（约一个研究周期时长）：通过即勾销本卡，
失败则按 runbook §6 报 bug；无兴趣则按裁决备注退役。
