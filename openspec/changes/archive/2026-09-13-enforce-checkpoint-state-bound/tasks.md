## 1. Red tests first (deterministic)

- [x] 1.1 新增 `tests/unit/test_checkpoint_state_bound.py`：用真实 `AsyncSqliteSaver`（temp bundle）先做一次正常写入并记录 `graph.sqlite` 字节，再经同一 saver 直接写入一个 `channel_values` 超过 `MAX_CHECKPOINT_STATE_BYTES` 的 checkpoint，断言抛出类型化 bound 错误且 `graph.sqlite` 字节与写入前完全一致。先跑确认红。`@impl REG-008`
- [x] 1.2 在同文件新增单条 write value 越界用例（`aput_writes` 路径），先红。`@impl REG-008`
- [x] 1.3 新增读侧准入用例：写入一个越界 retained checkpoint，断言 `open_graph_checkpoint`/执行在编译前以不一致 checkpoint 结果拒绝。先红。`@impl REG-008`
- [x] 1.4 新增 bound 关系契约用例：断言 `MAX_WORK_UNIT_BLOCK_BYTES < MAX_CHECKPOINT_STATE_BYTES`，且一个"所有子块合规但聚合越界"的 state 被 whole-state bound 拒绝。先红。
- [x] 1.5 验证 1.1–1.4 全部红：`UV_OFFLINE=1 uv run --no-sync python -m pytest tests/unit/test_checkpoint_state_bound.py -q`。

## 2. domain: one bound, one serializer, one typed error

- [x] 2.1 在 `domain/state.py` 增加部分态容忍的 `validate_checkpoint_values(values)`（schema + legacy + size，不实例化 `ResearchGraphState`，不做字段白名单）与类型化 `CheckpointStateBoundExceeded`；让 `serialize_research_state` 成为其唯一 canonical serializer。`@impl REG-008`
- [x] 2.2 让离线迁移 `scripts/retained_run_data_migration.py` 共享同一 canonical serializer/bound（保留其完整 `ResearchGraphState` 结构校验），删除其重复的 size 计算。`@impl REG-008`
- [x] 2.3 记录校准证据：新增测量脚本/测试，输出 retained store 的 state 尺寸分布并断言阈值余量（当前最大 7,905 B vs 65,536 B）。
- [x] 2.4 验证 1.4 转绿，并跑 `tests/unit/test_state_bounds.py tests/unit/test_state_contracts.py tests/unit/test_state_persistence.py -q`。

## 3. runtime + graph: enforce at write, read, and node boundary

- [x] 3.1 包装 `build_deep_research_checkpoint_serde()`：`dumps_typed` 对整体 checkpoint 的 `channel_values` 做聚合校验、对单条 write value 做更新校验，超限抛 `CheckpointStateBoundExceeded`，且不假设 Deep Research 字段语义（兼容 probe/host 形状）。`@impl REG-008`
- [x] 3.2 `bundle_lifecycle._validate_current_graph_checkpoint` 复用 `validate_checkpoint_values`（读侧编译前拒绝）。`@impl REG-008`
- [x] 3.3 `graph/builder._node_wrapper` 在返回前用同一 helper 校验节点 update，携带 `logical_name`/attempt 归因。`@impl REG-008`
- [x] 3.4 验证 1.1–1.3 转绿：`UV_OFFLINE=1 uv run --no-sync python -m pytest tests/unit/test_checkpoint_state_bound.py -q`；并跑 `tests/graph/ -q`。

## 4. Terminal semantics: blocked with a precise incident

- [x] 4.1 在 `domain/lifecycle.py` 增加关闭集合值 `TerminalReason.INTERNAL_BLOCKED`，并同步投影/映射（`runtime/run_experience`、`domain/run_experience` 及任何枚举 blocked/terminal reason 的词汇或投影，如需要）与契约测试。`@impl REG-008`
- [x] 4.2 `runtime/bundle_graph` 在 `ainvoke` 边界捕获 `CheckpointStateBoundExceeded`，经 lifecycle 写终态 `BLOCKED` + `RunFailureCode.CHECKPOINT_INCONSISTENT` + `TerminalReason.INTERNAL_BLOCKED` + `FailureCertainty.DIRECT` 的 incident 到 Bundle-local `state.json`（不写 graph checkpoint），并暴露类型化 control 结果。`@impl REG-008`
- [x] 4.3 新增状态/投影测试：越界 run 的 `status` 返回 blocked + 精确 incident，无 repair 路由、无自动重启、checkpoint 未被写入。`@impl REG-008`
- [x] 4.4 验证：`UV_OFFLINE=1 uv run --no-sync python -m pytest tests/unit/test_checkpoint_state_bound.py tests/unit/test_lifecycle_observability.py -q`。

## 5. Calibration and regression

- [x] 5.1 跑现有 fixture 全流程与 probe 回归，确认无误伤：`UV_OFFLINE=1 uv run --no-sync python -m pytest tests/graph tests/integration -q`。
- [x] 5.2 确认 `MAX_WORK_UNIT_BLOCK_BYTES` 严格小于聚合上限、且子块合规不构成越界豁免，并有测试守护。
- [x] 5.3 全量门禁：`UV_OFFLINE=1 make verify` 全绿。

## 6. Governance and review obligations

- [x] 6.1 Control-placement plan review（apply agent）：在 apply 时用 design Decisions 的 control-placement 表逐行核对实现落点（写侧 serde / 读侧准入 / node wrapper / 终态映射）与 `non-bypassable` posture，记录一条可执行的 finding 或"无偏差"。done condition：finding 写入 change 的 review 记录且每行有对应实现或显式豁免。
- [x] 6.2 Archive closeout review（archive agent）：从仓库根跑 `python3 openspec/governance/check_project_gate.py --phase closeout`；从 `deep_research_harness/` 独立跑 `UV_OFFLINE=1 make verify`；从仓库根跑 `openspec validate enforce-checkpoint-state-bound --strict` 与 `git diff HEAD --check`（逐条直接量 exit code，不经管道）；记录 `git status --porcelain=v1 --untracked-files=all`、`git ls-files --stage deerflow`、`git submodule status -- deerflow`、`git -C deerflow status --porcelain=v1 --untracked-files=all`，审阅 `git diff --submodule=short`。done condition：以上全部通过且 gitlink 未被 bump。
