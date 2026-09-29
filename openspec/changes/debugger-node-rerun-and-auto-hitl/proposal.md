# Proposal

## Why

Stage 1（`debugger-hitl-conversation-visibility`，已归档）让操作者在 HITL 停点"看得见
对话"，但调试器仍是只读显微镜：停在一个节点上除了看（/context、/files、/inspect）与
推进外什么都不能做。用户拍板的下一步（2026-09-29）：**(1) 重跑当前节点**（模型抖动/
想再抽一次），**(2) 强制 HITL 通过**（`/run` 连续推进时默认自动「确认」提案、单步模式
可停——"跑通优先 + 可停"）。两者都触碰驱动契约的权威边界，需要设计先行。

## What Changes

- 驱动命令集扩展 `rerun_node`（拟名）：在已停边界上重新执行**刚提交的那个节点**，
  复用同一输入；状态回滚由 lifecycle 准入（controller-owned 字段），驱动不得直写。
- 驱动 drive 策略扩展 `auto_hitl`（拟名）：`drive_until` 撞上 HITL 时以操作者名义合成
  `确认` 答案（走既有 semantic intake），默认开启于连续推进、单步永不自动答；连续
  N 次未推进即停并明示。
- 工作台对应入口与诚实渲染：`/rerun`（或等价）命令、auto-hitl 的每次自动确认在
  日志明示"由 drive 策略代答"，拒绝时回退为人工停点。

## Change Focus

- **Primary module / causal owner**: `src/deerflow_deep_research/runtime/debug_driver.py`
  + `domain/debug_driving.py`（驱动契约与命令语义）；节点重跑的**状态回滚权威**在
  lifecycle/controller（本 change 的核心设计问题即这条边界怎么划）。
- **Seam classification**: `deterministic-guardrail`——不新增模型角色或提示；重跑是
  确定性重执行 + 状态准入；auto-hitl 是操作者显式策略下的确定性代答（复用既有
  semantic intake，不新增认知面）。
- **Question**: 节点重跑由谁准入、回滚到哪里（generation 机制 vs 新增 node 级
  控制路径）？drive 自动确认的权力边界与停止条件是什么？
- **Necessary adjacent/external contracts**:
  - `local-workflow-debug-driving`（LDD-001 闭合命令集要开口子——新命令的语义）；
  - `research-demo-tui`（工作台入口与 auto-hitl 的诚实渲染）；
  - `research-graph-lifecycle`（若走 lifecycle 准入的 node 级控制路径）；
  - `rerun-node` capability（既有 generation 级 rerun——评估复用 vs 区别）。
- **Evidence seam**: 驱动矩阵无头红绿（fixture 图重跑 + auto-hitl 停止条件）+ TUI
  pilot；真实模型下的重跑质量差异**不在**证据范围（那是评测，不是调试器契约）。
- **Not in scope**: 改输入再重跑（编辑 prompt/参数——Stage 3）；注入假结果跳过节点；
  改图组合/中途改道；`deerflow/` 改动。
- **Triggered review policies**: `control-placement`（新增 node 级控制路径 = 新
  authority 落点，需 Control Placement Review 表）。

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `local-workflow-debug-driving`: LDD-001 的闭合命令集扩展 `rerun_node`；
  `drive_until` 增加显式 `auto_hitl` 策略（默认开/单步关/有界停止）。
- `research-demo-tui`: 工作台暴露重跑入口与 auto-hitl 代答的明示渲染。

## Impact

- `deep_research_harness/src/deerflow_deep_research/domain/debug_driving.py`
  （DebugCommandKind + StopPolicy 扩展）
- `deep_research_harness/src/deerflow_deep_research/runtime/debug_driver.py`
  （命令执行 + 状态回滚委托）
- lifecycle/controller（若设计选择 b 路线：新增 node 级重跑准入口）
- `deep_research_harness/scripts/demo_tui.py`（入口 + 渲染）
- 依赖矩阵测试与 tui-journey/debugger-proof 门禁扩项
