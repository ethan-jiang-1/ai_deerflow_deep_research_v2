# TODO: manual-demo-tui-human-validation

> 状态: 待设计 | 优先级: 低 | 更新: 2026-09-26
> 上游: plan demo-real-gateway-closeout.md（G3 TUI 分诊遗留项，plan 已归档 CLS-060） | 下游: 无

## Why

demo-tui（Gateway + 手动 HITL）路线的**研究层阻塞全部死亡**，剩余唯一未测增量
是"谁来按键盘"：管道 stdin 无法驱动 Textual 输入组件，沙箱禁 openpty。真机已
证明同一研究链在 CLI（demo-real）与 TUI auto（embedded）两路线完成；手动 TUI
的未测增量仅为 **Textual 输入组件 + Gateway** 的组合。

## 现状对齐

- `demo-tui-real-auto`（嵌入式全真 + 自动 HITL）：✅ 通过——"Research completed"，
  report.md + claim-citation-map.json 发布，`_validate_final_artifacts` 通过。
- `session-workbench`：fixture 模式只读投影 UI 正常渲染 ✅。
- `RUN-020.command` 双击启动器已为此场景设计就绪；runbook-020 操作单存在。
- 唯一缺：一次真人（或无头驱动）在真实终端里跑完 HITL1 手动决策。

## Current Direction

两条候选路径，任一完成即关闭本 todo：

1. **真人路线**（设计意图的正路）：用户在真机双击 `RUN-020.command`，按
   runbook-020 在 TUI 里完成 HITL1 问答，验收"Research completed" + 产物发布。
2. **Pilot 无头驱动**：写一个 Textual Pilot 脚本驱动输入组件（如果后续想把
   该路线纳入自动化门禁再做；当前仅为可选项）。

## Design Questions

- 无

## Non-Goals

- 不改研究层代码——CLI 与 TUI auto 两路线已证明研究链健康。
- 不为自动化而自动化——若 Pilot 驱动维护成本高于价值，真人一次性验收即可。

## Next Step

用户在方便时跑一次 `RUN-020.command`（约一个研究周期时长），记录结果；
通过即勾销，失败则按 runbook §6 报 bug。
