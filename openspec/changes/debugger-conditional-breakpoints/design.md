# Design

## Context

`StopPolicy`（`domain/debug_driving.py`）是停点语义的唯一契约载体，`drive_until`
的逐边界循环已经在每个边界读 durable State（观察点基线比对同源）。43 个类型化字段
白名单已在 `/state`、`/watch` 两处使用（演示侧各自持有字段清单）。`DebugCommand.
breakpoint: StopPolicy | None` 通道现成——命令协议形状不变。参考：观察点
（LDD-009）与 auto-hitl（LDD-008）都在同一循环消费会话级策略。

## Goals / Non-Goals

**Goals:**
- 条件的语义决策收敛到 domain 层：契约 + 解析 + 纯求值，一处拥有。
- 解析期拒绝一切非法条件（未知字段/闭集外运算符/坏字面值），坏条件零机会上车。
- 求值全函数：任何 State 下返回布尔，绝不抛进驱动循环。
- TUI 呈现：接受时明示条件，拒绝时点名错误并给出可用字段。

**Non-Goals:**
- 不做表达式语言（无方法调用、无嵌套路径、无正则、无 or/非）。
- 不改命令协议形状（`DebugCommand` 字段集不动，`breakpoint` 通道复用）。
- 不做 work-unit 步进、改输入重跑、状态注入（proposal Not in scope）。
- 不新增 snapshot 字段（条件停点的"为什么停"由操作者自设条件 + 既有 stop 呈现覆盖）。

## Decisions

1. **条件契约 = 比较元组的合取**（`BreakpointCondition(clauses: tuple[Clause, ...])`，
   `Clause = (field, op, literal)`）。运算符闭集 `== != > < >= <=`；字面值闭集
   str/int/bool/None。选合取而非任意布尔树：覆盖"generation>=2 就停"类真实诉求，
   语法面与求值面都保持可枚举；or/非留待真实需要出现再议（YAGNI，扩展是加法）。
2. **字段白名单单一权威 = domain 侧导出（apply 期修订：收窄为可比较字段）**。现状
   `/state`、`/watch` 的字段清单是演示/驱动侧各自持有的字符串集合；本次把可用于
   条件的类型化字段名集合导出为 domain 层的单一来源——由 `BundleLocalState` 注解
   推导，**只含标量可比较字段**（int/str/bool 及 Optional 变体；StrEnum 字段按 str
   比较——`LogicalPhase` 是 StrEnum，`phase == wave0` 天然可用）。tuple/dict/ref/
   复合字段（如 `execution_trace`、`must_answer_questions`）在**解析期即拒绝**——
   对它们做条件比较永远为 False，与其成为静默陷阱不如类型化拒绝。不重构既有两处
   清单的行为（它们已锁定），只让新校验有权威出处。配套裁决（apply 期）：字面值
   类型必须匹配字段的声明族（`generation == 1x`、`phase == 5`、
   `degraded_profile == maybe` 均为解析期拒绝）——拼写错误在回车前暴露，而不是变成
   一个永不满足的条件把驱动空跑到上界。
3. **求值用原始类型化值，不用 `str()` 化值**。观察点比对用 `str(getattr(...))` 是
   因为它比"变化"；条件要支持 `generation >= 2` 这类序比较，必须拿原始值按字面值
   类型比较。全函数性由解析期闭集保证：字段必在白名单（getattr 有真实类型），
   运算符必在闭集，字面值类型与字段值不可比（str vs int）时按"不可满足"处理返回
   False 而非抛异常——诚实且安全（一个类型不匹配的条件本来就永远拦不住；直接
   构造绕过解析的场景对 `!=` 也归 False，杜绝类型错配条件的第一边界意外停）。
4. **`/run if`（无节点目标）与 `/run <节点> if` 同一通道**。两者都是
   `StopPolicy(breakpoint_after=…, condition=…)` 的取值组合，驱动循环一个判定点：
   `policy.condition` 存在时，节点目标命中需同时满足条件；无节点目标时任一边界
   条件满足即停。不为两者开两条代码路径。
5. **解析器放 domain（纯函数 `parse_breakpoint_condition`），TUI 只做分词**。
   TUI 把 `if` 之后的子串原样交给 domain 解析器，得到契约或类型化拒绝——语法
   权威在 domain，演示层不拥有第二份语法规则。

## Risks / Trade-offs

- [合取表达能力不够]（操作者想要 or/非）→ 闭集拒绝比半吊子表达式语言诚实；扩展
  是契约加法，留待真实诉求。
- [序比较遇到 None 字段值] → 求值器把"与 None 的序比较"归为不可满足（False），
  只有 `==`/`!=` 对 None 有意义；单测锁定。
- [条件永不满足 + auto_hitl] 组合把驱动推到 64 步上界 → 上界是既有安全网，本设计
  刻意不加宽；矩阵用例锁定"上界处干净停在已提交边界"。
- [TUI 分词与 domain 解析的边界]（引号/空格字面值）→ 第一版字面值不支持空格
  （闭集拒绝），需要含空格 str 比较时再加引号规则——记录为已知限制，不悄悄支持。

## Migration Plan

纯加法：新契约字段带默认 None，既有命令/矩阵/fixture 全部不感知。回滚 = revert
单点；无数据迁移、无协议变化。req id（LDD-010 / RED-018）在 apply 时登记
`openspec/governance/req-registry.yaml`。

## Open Questions

（无——语法闭集、求值语义、上界交互均已在上面裁决。）
