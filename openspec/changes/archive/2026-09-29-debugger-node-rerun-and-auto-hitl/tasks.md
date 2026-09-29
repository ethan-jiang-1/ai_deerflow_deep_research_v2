# Tasks

## 1. 可行性 spike（先于一切实现）

- [x] 1.1 controller 回滚能力评估：**裁决=路线 a 可行**（2026-09-29）。证据：
  `sync_graph_progress` 使 state.json trace 成为图值镜像（回滚=fork+重投影）；
  `AsyncSqliteSaver` 保存完整 checkpoint 历史且 `RootBoundedCheckpointSaver`
  全委托（`aget_state_history` 可用）；attempt 序号在图值内随 fork 回退。
  同 id attempt 重写容忍度由 2.1 红测试实证。
- [x] 1.2 auto-hitl 停止条件：hitl1 未接受时产出类型化 feedback
  （clarification/semantic_invalid/semantic_unavailable，`domain/human_interaction.py`
  枚举 + `interaction_feedback` state 通道），"连续 2 次未接受即停"以纯函数
  `auto_hitl_should_stop` 锁定并可单元测试。

## 2. 红环先行

- [x] 2.1 驱动矩阵：`rerun_node` 重执行断言（trace 新 visit、journal 记账、
      拒绝时边界不变）——红。
- [x] 2.2 驱动矩阵：auto-hitl 策略表（完整提案通过 / 两次未接受回人工 /
      单步永不代答 / HITL2 必停）——红。
- [x] 2.3 TUI pilot：/rerun 入口 + 成本提示 + 代答明示行——红。

## 3. 实现与门禁

- [x] 3.1 `domain/debug_driving.py`：命令集 + StopPolicy.auto_hitl（加法默认）。
- [x] 3.3 `runtime/debug_driver.py` + lifecycle：重跑准入口 + 代答循环（按 1.1 结论）。
- [x] 3.4 `scripts/demo_tui.py`：入口与渲染。
- [x] 3.5 登记 LDD-007/008、RED-016；窄验证 + `make tui-journey`、
      `make debugger-proof`、`UV_OFFLINE=1 make verify` + closeout/strict。
- [x] 3.6 归档 + 账本 + 提交分层；push 需用户点头。

> 注：用户于 2026-09-29 授权全程自主执行（含本路线裁决与实施），apply 依此授权进行。
