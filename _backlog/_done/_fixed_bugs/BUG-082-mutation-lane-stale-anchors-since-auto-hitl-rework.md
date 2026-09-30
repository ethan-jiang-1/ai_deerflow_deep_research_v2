# BUG-082: mutation-check 两条登记变异自 LDD-008/009 改写后静默失效——守卫 lane 报绿但无牙

> 严重级别: P2 | 发现: 2026-09-29（条件断点 change 的自查轮） | 状态: 已修复（2026-09-29，同轮修复）

## 症状

`make mutation-check` 在 debugger-conditional-breakpoints 自查轮首次重跑时报
"9/11 went red"：`drive-stops-at-hitl` 与 `pause-is-honoured` 两条**既有**条目
无牙（selector 保持绿 / 锚文本 ANCHOR-MISSING）。即：守卫 lane 从 LDD-008/009
两轮会话改写 `drive_until` 循环后就没再跑过（handoff 记录的门禁清单里没有
mutation-check），两轮改动静默破坏了锚，无人察觉。

## 根因

- `drive-stops-at-hitl`：锚文本 `if posture == "awaiting_hitl" and policy.stop_on_hitl:`
  在 LDD-008 auto-hitl 改写中被替换为无条件 `if posture == "awaiting_hitl": break`
  （stop_on_hitl 语义移入 `_settle_hitl` 的代答策略），条目未随代码更新。
- `pause-is-honoured`：锚 `pause_pending = pause_pending or bool(...)` 在 seed
  段与循环段各出现一次（seed 是 LDD-008 加的），条目的 `replace(count=1)` 打在
  seed 段上——真正的循环段守卫仍在，selector 依旧绿。

## 复现

无头：修复前 `make mutation-check` exit 非 0（"a guard stayed green"）；两条
修复后的变异均手工演示过红（删 awaiting_hitl break → hitl 边界测试红；循环段
pause 传递置 False → 单边界停测试红），恢复即绿。

## 修复关联

`tests/mutations/registry.py` 两条锚随当前代码语义更新（含循环段注释块锚定唯一
出现点）；`make mutation-check` 11/11 全红。教训入账：**改写 drive_until 一带的
控制流后必须重跑 `make mutation-check`**——它不在 verify 里，不会自动拦住锚漂移。
