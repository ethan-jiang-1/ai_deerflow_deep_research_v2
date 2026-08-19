# BUG-056: readiness critic 零工具一致性测试在 HEAD 上即失败（route=exhausted 而非 pass）

> 严重级别: P1 | 发现: 2026-08-19 | 修复: 2026-08-19 | 状态: 已修复

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

`dd4c39d` 为 BUG-054 扩展 readiness 的结构性 store 读取后，零工具 conformance
测试里的 fake store 没有同步实现 `read_synthesis_gaps` /
`read_synthesis_findings`。`AttributeError` 被节点的结构性读取边界归一化为
`synthesis_findings_unavailable`，所以 route 如实成为 `exhausted`；不是 critic
预算、gate fatigue 或 BUG-057 的降级语义问题。`94c8087` 已补齐该 fake store，
产品代码无需为 BUG-056 单独修改。

## 复现

```bash
cd deep_research_harness
UV_NO_CACHE=1 .venv/bin/python -m pytest \
  tests/integration/test_zero_tool_node_conformance.py::test_readiness_critic_crosses_real_zero_tool_bridge_and_uses_ledger_projection -x
```

## 修复关联

产品修复已随 `94c8087` 落地；OpenSpec change
`fix-readiness-fallback-degraded-delivery` 记录根因并完成归档。2026-08-19 复核：

```bash
cd deep_research_harness
.venv/bin/python -m pytest \
  tests/integration/test_zero_tool_node_conformance.py::test_readiness_critic_crosses_real_zero_tool_bridge_and_uses_ledger_projection -q
```

结果：`1 passed`；包含本 change 的窄集结果为 `104 passed`，全量
`UV_OFFLINE=1 make verify` 通过。
