# Proposal

## Why

以 GDB 为标尺的第三轮挤压只剩一个"像 debugger 但我们还没有"的高价值缺口：**条件断点**。
`/run <节点>` 已能跑到指定节点，但长图连续推进时操作者真正想要的是"**只在出问题的状态
停下**"——比如"推进到 `generation >= 2` 才停""`execution_phase` 一到 wave2 就停"。
没有条件时，断点要么太粗（第一个边界就停），要么逼人反复按 Enter。这是 Stage 3 四候选
中成本/收益比最优的一个：完全复用既有 43 字段白名单、watch 基线比对机制与 `drive_until`
逐边界循环，不触碰图拓扑与 checkpoint 语义。

## What Changes

- `StopPolicy` 契约加法扩展：`condition: BreakpointCondition | None`——一个**确定性、
  无 eval** 的字段比较条件（字段名取自 `BundleLocalState` 类型化字段白名单，运算符
  闭集，字面值为 str/int/bool/None），条件满足才允许条件停点生效。
- 驱动 `drive_until` 循环在既有逐边界状态读取处增加条件判定：`/run <节点> if <条件>`
  在节点已访问且条件满足时才停；`/run if <条件>`（无节点目标）在任一边界条件满足时停。
  条件停点受既有 64 步驱动上界约束，不引入无界推进。
- 工作台 `/run` 语法扩展：`/run [节点] [if <字段><op><值> (and <字段><op><值> ...)]`；
  未知字段/非法运算符/不可解析字面值在**命令解析期**即以类型化拒绝退回（提示可用字段），
  绝不带病上车；`/help` 同步。
- 条件求值是纯函数、全函数（对任意状态返回布尔，不抛异常）；解析与求值都在
  domain 层（typed contract），driver 只消费布尔结果。

## Change Focus

- **Primary module / causal owner**: `domain/debug_driving.py`（`StopPolicy` 扩展 +
  `BreakpointCondition` 契约 + 纯求值器——条件的语义决策点）+
  `runtime/debug_driver.py`（在 `drive_until` 的逐边界状态读取处消费求值结果）+
  `scripts/demo_tui.py`（`/run ... if ...` 解析与拒绝呈现）。
- **Seam classification**: `deterministic-guardrail`——条件是确定性状态比较：白名单
  校验在解析期，求值是纯函数，无认知面、无新 authority、无状态写入。
- **Question**: 操作者能否在连续推进时让驱动"只在指定节点上且状态条件满足处停下"，
  且坏条件在按下回车前就被拒绝？
- **Necessary adjacent/external contracts**: `local-workflow-debug-driving`
  （条件停点语义：何时停、上界约束、解析期拒绝）；`research-demo-tui`（`/run if`
  语法与类型化拒绝渲染、`/help`）。
- **Evidence seam**: 驱动矩阵红绿（条件满足停/不满足继续/坏条件拒绝/64 步上界仍成立）
  + TUI pilot 红绿（`/run <节点> if` 语法、拒绝提示、`/help`）+ 既有门禁
  （`UV_OFFLINE=1 make verify`、`make tui-journey`、`make debugger-proof`）。
- **Not in scope**: 按 work-unit 步进（图侧配合，另立卡排队）；改输入重跑与状态注入
  （状态手术类，明确缓办）；条件中调用方法、访问嵌套路径、正则、or/非逻辑（闭集之外
  一律拒绝）；`deerflow/` 不动。
- **Triggered review policies**: `none: 确定性状态比较与解析期白名单校验，无新
  authority、无认知面变化、无状态写入。`

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `local-workflow-debug-driving`: LDD-010 条件停点（`StopPolicy.condition` 契约、
  逐边界求值时机、解析期白名单拒绝、64 步上界不变）。
- `research-demo-tui`: RED-018 工作台 `/run [节点] if <条件>` 语法、坏条件的类型化
  拒绝与可用字段提示、`/help` 同步。

## Impact

- `domain/debug_driving.py`（`StopPolicy.condition` 加法字段、`BreakpointCondition`
  契约、纯求值器与解析函数）
- `runtime/debug_driver.py`（`drive_until` 条件判定；`DebugCommand.breakpoint` 既有
  通道直接携带扩展后的 `StopPolicy`，命令协议无形状变化）
- `scripts/demo_tui.py`（`/run` 解析扩展 + 拒绝渲染 + `/help`）
- 测试：矩阵条件停点红绿、domain 求值器单测（含全函数性）、pilot 语法红绿
