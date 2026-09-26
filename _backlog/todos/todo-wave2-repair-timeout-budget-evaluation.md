# TODO: wave2-repair-timeout-budget-evaluation

> 状态: 待设计 | 优先级: 中 | 更新: 2026-09-26
> 上游: plan demo-real-gateway-closeout.md（G3 验收遗留项，plan 已归档 CLS-060） | 下游: 无

## Why

`make test-live` 分诊（2026-09-26）后 live lane 为 49/50 等效。唯一剩余失败
`wave2-synthesis-repair-normal`：两次复现均为 **TimeoutError**——真实模型延迟超出
case 预算。该 case 的校准测试直接传死 `validation_category="parser_invalid"`，
与本会话（2026-09-26）的 G1/G2 改动零交集，即 handoff 48/50 基线里已知的
那 1 个失败。问题不在代码路径，在 case 的 timeout 预算与真实模型延迟的匹配。

## 现状对齐

- 其余 49 个 live case 全部通过（含修复后的 `gateway_forwarding_proof`）。
- 该 case 失败原因两次复现一致 = TimeoutError（非确定性拒绝、非解析错误）。
- G1（schema 反馈闭环，c43fd49）与 G2（final_delivery 基数，3e142ef）均已
  落地并通过真机验收，与本 case 无关。

## Current Direction

评估该 case 的 timeout 预算是否需要走 evaluation 治理调整：

1. 取数：live 跑的 wave2 修复轮实际耗时分布（bundle diagnostics / live 日志）。
2. 对照 case 当前预算值，判断是"预算过紧"还是"该轮模型确实异常慢"。
3. 若调预算 → 评估是否属于 evaluation 治理范畴（scenario 预算是契约面，
   需确认 owning spec 是否枚举该预算，避免直接改数破坏契约测试）。

## Design Questions

- timeout 预算的 owning spec / scenario 契约在哪一层拥有它（case fixture、
  evaluation profile、还是 scenario governance）？
- 调预算 vs 标记 flaky-skip，哪个更诚实？

## Non-Goals

- 不动 wave2 解析/校验代码路径（G1 已修且真机验证过）。
- 不追求 50/50 的账面数字——若模型延迟方差客观存在，诚实记录优于调参凑绿。

## Next Step

下次 live 窗口跑一次该 case 并留存耗时证据，然后决定走 evaluation 治理
调整还是接受为已知方差。
