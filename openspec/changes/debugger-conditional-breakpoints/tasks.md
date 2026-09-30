# Tasks

## 1. Domain：条件契约、白名单导出、解析与求值（红先于绿）

- [ ] 1.1 RED：`tests/unit/test_debug_break_conditions.py` —— 未知字段/闭集外运算符/坏字面值/含空格字面值的解析拒绝各一例，断言类型化拒绝且永不产出契约（跑红）
- [ ] 1.2 RED：同文件 —— 全函数性：对 None 字段值的序比较返回 False、类型不可比返回 False、`==`/`!=` 对 None/bool/str/int 各语义一例、合取短路（跑红）
- [ ] 1.3 GREEN：`domain/debug_driving.py` 加 `BreakpointCondition`/`Clause` 契约、`StopPolicy.condition` 默认 None、由 `BundleLocalState` 导出的字段白名单、`parse_breakpoint_condition`、纯求值函数；1.1/1.2 转绿
- [ ] 1.4 变异自查：对求值器跑 `make mutation-check`（或等效窄变异），守卫能变红

## 2. Driver：逐边界条件判定

- [ ] 2.1 RED：`tests/integration/test_debug_driver_matrix.py` 新增矩阵行 —— 条件满足即停（有节点目标）/ 条件不满足继续到满足处 / 无节点目标首边界满足即停 / 永不满足走满既有 64 步上界并干净停在已提交边界（跑红）
- [ ] 2.2 GREEN：`runtime/debug_driver.py` 的 `drive_until` 在既有边界 State 读取处消费 `policy.condition`（有节点目标：节点已访问且条件满足才停；无节点目标：条件满足即停）；2.1 转绿
- [ ] 2.3 回归：既有矩阵 107+ 项全绿（`UV_OFFLINE=1 .venv/bin/python -m pytest tests/integration/test_debug_driver_matrix.py -q`）

## 3. TUI：`/run if` 语法、类型化拒绝、`/help`

- [ ] 3.1 RED：`tests/integration/test_demo_tui.py` pilot 用例 —— 合法 `/run <节点> if <字段> >= <值>` 接受并明示条件；`/run <节点> if <未知字段> == 1` 类型化拒绝（点名错误+可用字段）且零驱动启动；`/help` 列出条件语法（跑红）
- [ ] 3.2 GREEN：`scripts/demo_tui.py` 扩展 `/run` 分词：`if` 后子串原样交 domain 解析器，拒绝即渲染；接受时在脉冲/日志明示条件；`/help` 同步；3.1 转绿
- [ ] 3.3 回归：`UV_OFFLINE=1 .venv/bin/python -m pytest tests/integration/test_demo_tui.py -q` 全绿；新命令面同步 `on_input_submitted` 路由（沿用 BUG-078 后的清空语义）

## 4. 门禁与收尾

- [ ] 4.1 `make tui-journey` 与 `make debugger-proof`（15 experiences）全绿
- [ ] 4.2 `UV_OFFLINE=1 make verify` exit 0；`ruff format` 无漂移
- [ ] 4.3 live 快速档 `test_embedded_debugger_rerun_live` 复跑绿（真凭证，确认加法不伤真链路）
- [ ] 4.4 runbook-031 命令面更新（`/run if` 语法 + Stage 3 状态），req id 登记 `openspec/governance/req-registry.yaml`（apply 时）
