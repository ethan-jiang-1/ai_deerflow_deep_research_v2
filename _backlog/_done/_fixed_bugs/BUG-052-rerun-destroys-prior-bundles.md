# BUG-052: 重跑清理旧 run bundle——失败现场被销毁，跨 run 取证不可能

> 严重级别: P2 | 发现: 2026-08-18 | 状态: 活跃

## 症状

`soft-bundle run` 输出含 `cleaned prior run bundles`。2026-08-18 晚四次 003 run
后检查磁盘：`scopes/` 下只剩**当前 run** 的 bundle（b_M_sAiRI1…）；run 1/2/3 的
bundle（b_CsmLjjF9…、b_fTetY…、b_Ameegc4A…，含 BUG-047/049 的完整失败证据：
events.jsonl、submissions.jsonl、work results、graph.sqlite）**全部被删除**。

本次三张 P0 卡的原始证据（事件序列、字节实测、checkpoint 解码）全靠排障当时
即时摘录才得以保留；事后复核、跨 run 对比、以及"按 runbook 第 8 节贴日志"的
bug 流程在重跑后即不可执行。

## 根因

run 入口的清理策略按"每次 run 全新开始"设计，把"前次 run bundle"与"前次失败
证据"一并清除。诊断保留语义（`diagnostic_ref` 指向的 bundle 内容）没有比 run
生命周期活得更久——typed incident 引用形同悬空。

## 复现

```bash
cd deep_research_harness
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 003"   # 任意失败
ls .deep-research-demo-runs/workspace/deep-research/scopes/*/      # 记下 bundle
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run <root> --mode 003"   # 重跑
# 前次 bundle 目录已消失
```

## 修复关联

待讨论：保留最近 N 个 run bundle（含失败的），或把 `terminal=blocked` 的 bundle
移入归档目录而非删除；`diagnostic_ref` 的可解析性应至少覆盖活跃 bug 生命周期。

## 修复关联

已由 change `preserve-failed-run-bundles` 落地（2026-08-18）：重跑前受管子树
rename 进 `archive/<name>-<UTC时间戳>`，每名保留最近 3 份；空目录行为不变；
`tests/contract/test_soft_bundle_cli.py` 三个新用例锁死。
