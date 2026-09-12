# BUG-039: spec 同步的行为变更留下期望旧行为的 workflow 测试

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 已修复（openspec/changes/honest-delivery-and-real-run-diagnostics）

## 症状

干净 HEAD 上 `make test-workflow` 挂 1 个：
`test_wave2_malformed_output_consumes_repair_and_leaves_no_partial_authority
[malformed-output]`，`DID NOT RAISE ValueError("synthesis_output_json_invalid")`。

## 根因

归档 commit `13249bb` 把 wave2 repair 路径的二次解析改为**有界终态**（route
`exhausted` + 类型化 `output.structured_invalid` incident，不再让 ValueError 逃
逸节点边界），且主 spec 已同步（`openspec/specs/wave2-synthesis-node/spec.md`：
"A still-invalid repaired candidate blocks the node"）。但带 `workflow` 标记的集
成测试仍断言旧的未捕获 ValueError 行为；该 change 归档前没跑 workflow 车道，
红灯被带进主线。与 BUG-038 同根：**部分车道绿被当作完成凭证**。

## 复现

`git stash -u` 后 `.venv/bin/python -m pytest tests -m "workflow and not
(requires_llm or release_e2e or periodic)" -q` → 同挂（2026-08-18 实测）。

## 修复关联

在 honest-delivery-and-real-run-diagnostics apply 内按主 spec 更新断言：
`route == "exhausted"`、`terminal_status == "blocked"`、
`latest_incident["code"] == "output.structured_invalid"`、无 synthesis artifact
（保留原有 observation/ledger 断言）。workflow 车道 35 passed。经验沉淀：
`_backlog/_done/_closed_plans/2026-08-18-honest-delivery-apply.md`（spec 语义变更时 grep
全部标记的相关测试；归档前逐车道确认）。
