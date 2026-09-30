# Tasks

## 1. Domain：条件契约、白名单导出、解析与求值（红先于绿）

- [x] 1.1 RED：`tests/unit/test_debug_break_conditions.py` —— 未知字段/闭集外运算符/坏字面值/含空格字面值的解析拒绝各一例，断言类型化拒绝且永不产出契约（跑红：ImportError，新 API 首红）
- [x] 1.2 RED：同文件 —— 全函数性：对 None 字段值的序比较返回 False、类型不可比返回 False、`==`/`!=` 对 None/bool/str/int 各语义一例、合取短路（先红后绿）
- [x] 1.3 GREEN：`domain/debug_driving.py` 加 `BreakpointCondition`/`Clause` 契约、`StopPolicy.condition` 默认 None、由 `BundleLocalState` 导出的字段白名单、`parse_breakpoint_condition`、纯求值函数；18/18 绿（白名单收窄为标量+StrEnum 可比较字段，apply 期 design 修订）
- [x] 1.4 变异自查：三个新守卫面登记进 `tests/mutations/registry.py` 并手工演示红
  （求值器类型错配守卫 / 驱动条件消费 / 目标已访问同界守卫）；`make mutation-check`
  11/11 全红

## 5. Apply 期自查轮发现（2026-09-29）

- [x] 5.1 修复驱动判定缺陷：带节点目标时 `elif condition_holds` 会在目标**未访问**、
  条件先满足的边界提前停（违反 spec"目标已访问且条件满足"合取）；红环
  `test_a_condition_holding_before_the_target_visits_does_not_stop` 先红后绿
- [x] 5.2 修复 mutation lane 两条陈旧锚（BUG-082，LDD-008/009 改写 drive 循环后
  静默失效）：`drive-stops-at-hitl` 锚随语义更新、`pause-is-honoured` 锚改用循环段
  注释块唯一定位；两条均手工演示红，11/11 全红；卡在
  `_backlog/_done/_fixed_bugs/BUG-082-…md`

## 2. Driver：逐边界条件判定

- [x] 2.1 RED：`tests/integration/test_debug_driver_matrix.py` 新增 4 矩阵行 —— 无节点目标首边界满足即停 / 目标+真条件停在目标 / 目标+假条件越过目标停在满足边界 / 永不满足跑到底（3 红为行为红，真条件行按设计守护既有语义）
- [x] 2.2 GREEN：`runtime/debug_driver.py` 的 `drive_until` 在既有边界 State 读取处消费 `policy.condition`（有节点目标：节点已访问且条件满足才停；无节点目标：条件满足即停）；4 新行转绿
- [x] 2.3 回归：既有矩阵全绿（38/38，含原 34 项）

## 3. TUI：`/run if` 语法、类型化拒绝、`/help`

- [x] 3.1 RED：`tests/integration/test_demo_tui.py` 三个 pilot 用例 —— `/run wave0 if phase == wave0` 受理并明示条件、停在满足边界；`/run wave0 if not_a_field == 1` 类型化拒绝（点名错误+可用字段）且停点保持；`/help` 列出条件语法（三红）
- [x] 3.2 GREEN：`scripts/demo_tui.py` 扩展 `/run` 分词（regex 分隔 `[节点] if <条件>`，条件子串原样交 domain 解析器）；`_debug_drive` 接受条件、受理时日志明示 + 脉冲标签携带；`/help` 同步；3.1 转绿
- [x] 3.3 回归：三文件全量回归 + ruff format/check 干净

## 4. 门禁与收尾

- [x] 4.1 `make tui-journey`（16 步）与 `make debugger-proof`（15/15 experiences）全绿
- [x] 4.2 `UV_OFFLINE=1 make verify` exit 0（verify: OK）；`ruff format` 无漂移
- [x] 4.3 live 快速档 `test_embedded_debugger_rerun_live` 复跑绿（9.08s，真凭证，加法不伤真链路）
- [x] 4.4 runbook-031 命令面更新（§5c 条件断点 + §8 对照表状态），LDD-010/RED-018 已登记 `openspec/governance/req-registry.yaml`
