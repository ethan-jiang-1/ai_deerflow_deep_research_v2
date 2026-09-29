# Tasks

## 1. 可行性 spike（先于一切实现）

- [ ] 1.1 controller 回滚能力评估：`execution_trace` 尾帧 + work-unit 记账 +
      evidence 指针能否事务性撤销（读 `runtime/bundle_lifecycle.py`、
      `work_unit_store.py`、journal 不变量；产出：可/不可 + 证据行号）。若不可，
      停下向用户回报降级选项（整代 rerun 快捷方式 vs 放弃节点重跑），不擅自缩范围。
- [ ] 1.2 auto-hitl 停止条件评估：hitl1 对「确认」在提案不完整时的行为
      （ clarification 循环）实证于 fixture/单测，确认"连续 2 次未接受即停"可达。

## 2. 红环先行

- [ ] 2.1 驱动矩阵：`rerun_node` 重执行断言（trace 新 visit、journal 记账、
      拒绝时边界不变）——红。
- [ ] 2.2 驱动矩阵：auto-hitl 策略表（完整提案通过 / 两次未接受回人工 /
      单步永不代答 / HITL2 必停）——红。
- [ ] 2.3 TUI pilot：/rerun 入口 + 成本提示 + 代答明示行——红。

## 3. 实现与门禁

- [ ] 3.1 `domain/debug_driving.py`：命令集 + StopPolicy.auto_hitl（加法默认）。
- [ ] 3.3 `runtime/debug_driver.py` + lifecycle：重跑准入口 + 代答循环（按 1.1 结论）。
- [ ] 3.4 `scripts/demo_tui.py`：入口与渲染。
- [ ] 3.5 登记 LDD-007/008、RED-016；窄验证 + `make tui-journey`、
      `make debugger-proof`、`UV_OFFLINE=1 make verify` + closeout/strict。
- [ ] 3.6 归档 + 账本 + 提交分层；push 需用户点头。

> 注：本 change 处于 propose 阶段，等用户审过设计（尤其 1.1 的路线裁决）再进 apply。
