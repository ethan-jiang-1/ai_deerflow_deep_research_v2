# TODO: adopt-framework-engineering-protocols

> 状态: 停靠（仅余一项触发条件；三项判定已完成，无排期动作） | 优先级: 低（触发驱动） | 更新: 2026-09-27（晚间对码审计）
> 上游: 2026-09-27 DeerFlow 只读指引借力审计（8 条候选，流程级 5 条已采纳，机制级 3 条为本卡） | 下游: 项 2 残余并入 [`todo-controller-evaluation-repetition.md`](todo-controller-evaluation-repetition.md)

## Why（2026-09-27 晚间对码审计的结论）

原卡假设三项机制"缺失"并要求先做 explore 判定适用/不适用。当晚逐项对码核对：
两项大头**已存在或大部分已存在**，一项残余很小。原 Next Step 由该审计完成，
判定如下（证据均为当日在库代码/测试，可直接复核）。

## 三项判定

1. **bounded-run `stop_reason` —— 已存在；残余为刻意分歧，留痕不补齐。**
   本仓三层全有：调用层 `BudgetStopReason` 闭合枚举
   （`domain/run_observation.py`，"stopped invocation 的诊断归因"，加法字段，贯穿
   middleware → node_agent_bridge → observation）；生命周期层
   `TerminalReason.GATE_BLOCKED`（预算耗尽，@impl REG-004）；eval 层
   `FailureDetail` 独立码（`execution_resource_bound_exceeded` / `execution_timeout`）。
   上游机制的真正卖点——"加法字段而非新枚举以保护 v1 消费者" + "lead 复用被截断的
   部分结果"——绑定其 subagent/lead 架构，本仓没有 subagent；且本仓 eval 刻意把
   预算截断当**失败**而非"带部分结果的完成"，对证据纪律更诚实。该分歧已由既有
   测试锁定（eval 套件的 failure-code 断言、lifecycle 契约测试）。
2. **评测可复现协议 —— 大头已存在；真缺口一条，已并入 controller-eval todo。**
   案例语料即数据集（仓内 JSON，digest 钉住，执行时 runner 逐项比对）；eval 路径
   零下载；凭证全走具名环境变量（`_MODEL_CREDENTIALS` / `TAVILY_API_KEY`）；
   provider / model / prompt / skill / soul / tool-schema 摘要强制记录且校验。
   真缺口仅：`EvaluationBundleManifest` 不记 git revision —— 已并入
   [`todo-controller-evaluation-repetition.md`](todo-controller-evaluation-repetition.md)
   的 preflight（它真跑起来时才需要，独立修没有消费者）。
3. **waiver 内容哈希 —— 停靠，触发条件驱动。**
   当前零条活跃 waiver（duration 与 command-inventory 两处清单皆空/有防锈）；
   上游哈希绑定解决的问题是"高频变更文件被过期 waiver 掩护"，本仓 waiver 对象是
   稳定选择器与目标名，不存在此问题。**触发条件：第一条真 duration waiver 落地时，
   在当次改动里顺手加"未用即红"防锈（对齐 command-inventory tripwire 的同类机制），
   并届时重评哈希绑定是否需要。**

## Non-Goals

- 不为对齐上游而造表面机制；不修改 `deerflow/`；不为"全维度"补齐项 1 的
  partial-reuse 语义（刻意分歧，理由见上）。

## Next Step

无排期动作。项 3 触发条件发生时（第一条 duration waiver 落地）顺手加防锈；
项 2 残余见下游卡；项 1 关闭。
