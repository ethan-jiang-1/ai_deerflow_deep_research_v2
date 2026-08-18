## 1. 测试先行：readiness 降级 run 路由

- [x] 1.1 在 `tests/unit/test_readiness_real.py` 新增用例：state 含
      `degraded_decisions=("wave2_synthesis:exhaustion_degraded",)` 且 bridge
      失败（`_deps(raises=True)`）→ 断言 `route == "pass"`、
      `readiness_blocked_count > 0`、report plan 披露 unresolved gap
- [x] 1.2 新增用例：降级 marker + 候选被拒（unknown/duplicate question 或
      backing ref 越界）→ 断言 `route == "pass"`（非降级 run 保持
      `repair_targeted` 的既有断言不变）
- [x] 1.3 新增用例：降级 marker + 结构性 hard-rule 失败（`_deps(store_fail=True)`）
      → 断言仍 `route == "exhausted"`、`terminal_status == BLOCKED`
- [x] 1.4 运行三个新用例确认红（`pytest tests/unit/test_readiness_real.py`）

## 2. 实现修复

- [x] 2.1 `graph/nodes/readiness/node.py` 路由判定：读
      `exhaustion_degradation_marker("wave2_synthesis") in (state.get("degraded_decisions") or ())`，
      仅在 `not wave2_degraded` 时才路由 `repair_targeted`；结构性失败分支不变
- [x] 2.2 `ruff` 通过；新用例转绿；既有 readiness/gate/honest-delivery 测试
      全部保持绿（非降级行为不变）

## 3. 回归与验证

- [x] 3.1 全量测试：`UV_NO_CACHE=1 make verify`（本机 uv 全局缓存权限限制，
      `UV_OFFLINE=1` 会在 lock-check 失败；等价窄口径：
      `UV_NO_CACHE=1 .venv/bin/python -m pytest tests/unit tests/graph tests/contract`）
- [x] 3.2 `openspec validate fix-readiness-degraded-route --strict` 通过
- [x] 3.3 更新 BUG-044（修复关联指向本 change，注明 BUG-045 为独立前置）
- [ ] 3.4 真实 003 验证 run（可选，需 .env + 网络，约 10+ 分钟）：预期终态
      `completed`、report 存在且 Uncertainties 披露 gap；BUG-045 未修前
      补证循环零产出属预期（诚实降级交付），收敛验证在 BUG-045 change 后
