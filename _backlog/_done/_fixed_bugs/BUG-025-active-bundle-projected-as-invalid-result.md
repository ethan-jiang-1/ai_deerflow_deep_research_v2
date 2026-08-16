# BUG-025: 进行中的 Bundle 被投影为 `protocol.invalid_result`

> 严重级别: P0 | 发现: 2026-08-15 | 状态: 已修复（2026-08-16）

## 症状

真实 demo 在 `hitl1` 已建立 Run Bundle 后，没有显示可继续的研究确认，而是立刻以
`protocol.invalid_result` 结束。终端提示“不要继续当前运行”，并且缺少可检查的 Event Journal
记录，`make demo-real` 以错误码 1 退出。

## 根因

生命周期边界可以返回带 Bundle 的活动结果，但运行体验层试图把这个非终态结果构造成终态展示
契约。契约验证拒绝了该形状，原本可解释、可继续的 `research.active` 情况被泛化为协议无效。

## 复现

在修复前，对已有活动 Bundle 的本地 demo scope 执行：

```bash
cd deep_research_harness
make demo-real
```

观察返回 `protocol.invalid_result`、已知阶段为 `hitl1`。两次现场运行均出现此现象。

## 修复关联

`openspec/changes/fix-active-demo-bundle-projection/` 已实现把该情况安全投影为
`research.active`，并为 all-real demo 创建新 scope。仍缺一次真实 API 端到端成功回归；不能在
回归前关闭本卡。

2026-08-16 验证：change `fix-active-demo-bundle-projection` 已归档；
`tests/contract/test_run_experience_contract.py` 14 例全过（含
`test_available_active_result_projects_a_safe_non_terminal_fault`，断言 `research.active`
安全投影与 `active` 状态事实）。真实 API 端到端回归仍需一次真凭据 `make demo-real`
真机冒烟，作为常规 canary 跟踪，不阻塞本卡结案。
