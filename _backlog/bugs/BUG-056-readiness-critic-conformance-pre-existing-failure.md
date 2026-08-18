# BUG-056: readiness critic 零工具一致性测试在 HEAD 上即失败（route=exhausted 而非 pass）

> 严重级别: P1 | 发现: 2026-08-19 | 状态: 活跃

## 症状

`tests/integration/test_zero_tool_node_conformance.py::test_readiness_critic_crosses_real_zero_tool_bridge_and_uses_ledger_projection`
失败：

- 断言 `update["route"] == "pass"`，实际 `'exhausted'`。
- **在干净 HEAD 上即可复现**（`git stash` 后单测仍失败），与
  `fix-final-delivery-layout-fragility` change 的改动无关（该 change 只动
  final_delivery composer/node 与测试资产引用）。
- 它是当前 `make verify`（test-workflow gate）在全仓范围唯一的红点之一
  （另一个是 ruff format 对 6 个未触碰文件的版本性漂移）。

## 根因

未定位。现象：scripted readiness critic 经真实零工具 bridge 走完后的 gate
评估直接 exhausted（预算/疲劳路径），而非预期 pass。可能与 readiness
critic 的保守回退（`readiness_critic_fallback.*`）或 gate budget seeding
的近期改动有关——需要独立诊断，本卡只登记证据。

## 复现

```bash
cd deep_research_harness
UV_NO_CACHE=1 .venv/bin/python -m pytest \
  tests/integration/test_zero_tool_node_conformance.py::test_readiness_critic_crosses_real_zero_tool_bridge_and_uses_ledger_projection -x
```

## 修复关联

待诊断。注意与 BUG-055 的 change（fix-final-delivery-layout-fragility）区分：
本卡在 HEAD 上已存在，不阻塞该 change 的验收（该 change 范围内全绿）。
