# BUG-042: soft-bundle blocked 终态后不绑定 bundle，inspect/status/verify/phases 全部不可用

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 已修复 ✅

## 症状

两次修复后 003 run（均 blocked 终态，`soft-bundle run … --mode 003`）结束后：

- soft-bundle 目录的 `manifest.json` 保持 `current_bundle_id: null`，
  `bundles/` 记录目录缺失；
- 后续 `soft-bundle inspect/status/verify/phases <root>` 全部报错
  `error: current_bundle_id not bound`；
- 只能手工编辑 manifest 补绑 bundle id + `bundle_local_path` 后，runbook 文档的
  检查流程（inspect/verify）才可用（本次排查两次都靠手工补绑）。

runbook-003 明文要求 blocked run 走"inspect 看诊断引用/journal"的证据流程——
工具恰好在最需要诊断的终态上断掉。

## 根因

`scripts/soft_bundle.py` `cmd_run` 的 mode 002/003 分支用 **OR-gate 提前 return**
（`proc.returncode != 0 or bundle_id is None …`）：operator 入口非零退出（blocked →
`make demo-real-scripted` Error 1）时，即使 run 输出已解析出合法 `bundle_id` 且
bundle 目录真实存在，也在 `_record_bundle` 之前返回，manifest 保持
`current_bundle_id: null`、`bundles/` 记录缺失。mode 001 的 AND-gate
（`returncode != 0 AND bundle_id is None`）无此缺陷——已解析 bundle 时无论退出码
都流入绑定。

## 复现

```bash
cd deep_research_harness
ROOT=$(UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="create --name x --mode 003" | sed -n 's/^soft_bundle_root=//p')
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="run $ROOT --mode 003"   # blocked 终态, exit 1
UV_NO_CACHE=1 make soft-bundle DEMO_ARGS="inspect $ROOT"          # -> current_bundle_id not bound
```

## 修复关联

Change `soft-bundle-bind-blocked-run-bundle`（SBC-002 行为变更）：mode 002/003 的
绑定判定改为只看「是否解析到合法 bundle id + 真实 bundle 目录」，不再看退出码；
blocked run 先打印原始失败输出到 stderr、再 `_record_bundle`、再返回 run 自身
非零退出码。共享尾部改为 `return run_exit or (0 if ok else 1)`（mode 001 保持
`run_exit=None`，行为逐字节不变）。确定性测试：
`tests/contract/test_soft_bundle_cli.py` 新增 mode 002/003 非零退出绑定 fixture 与
无可解析 bundle 回归（22 passed）。
