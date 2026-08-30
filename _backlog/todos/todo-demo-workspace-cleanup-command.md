# todo: demo workspace 清理命令（`make demo-clean`）

> 优先级: 中 | 创建: 2026-08-30 | 状态: 活跃
> 来源: 020 战役 B1 实跑期间发现（伴随 BUG-064 讨论）；COMMANDS.md §3 已登记现状空缺

## 问题

`.deep-research-demo-runs/` 只增不减（本机现已 67+ bundles），**没有任何
list/cleanup 生命周期命令**——`docs/local-operations.md` 明示"no observation-backed
list, open, discovery, cleanup, or lifecycle-control command"。操作者要么攒着，
要么手 `rm -rf`（有误删证据 bundle 的风险，且会破坏 exact-bundle 基线快照）。

## 期望形态（设计约束）

1. `make demo-workspace-report`（先做只读盘点）：scopes / bundles / terminal
   状态 / 大小 / 时间，一目了然；
2. `make demo-clean`：
   - 默认 **dry-run**（只列将删项）；`CONFIRM=1` 才真删；
   - **永不删非 terminal bundle**（suspended/active 孤儿在 BUG-064 修复后可能可
     resume——清不掉的东西先要能认领）；
   - 可选年龄/状态过滤（如只清 `completed` 且 >7d）；
   - logs 与 workspace 分开清；
3. 清理后提示"基线快照已失效，重跑战役前需重新做 before 快照"。

## 关联

- 与 BUG-064（attach/resume）配套：claim 语义落地前，保守清理；
- 与 exact-bundle 绑定纪律（runbook-020 §3.0/§3.3）互斥面的说明；
- 落地走小 openspec change（operator tooling，无产品契约变化，但 Makefile 是
  公共入口面，值得过一遍 polish）。
