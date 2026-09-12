# TODO: Wave0 provider/tool/validator root cause reproduction

> 状态: 暂停（未排期） | 优先级: 中 | 更新: 2026-09-12
> 上游: CLS-015（deep-research-real-run-intake-and-observability）| 下游: 无

## Why

CLS-015 把 real CLI intake、lifecycle 可见性、retained summary/event journal、
inspection、strict-msgpack 硬化都做完了，但留下一个证据边界：**Wave0 现场的
provider / tool / validator 根因仍未确定**，须由一次**新的真实、脱敏重现**来定，
不能从 retained 的有界 lifecycle trace 反推。此前只在关闭摘要留字，无独立条目。

## 现状对齐

retained record 是有界 lifecycle trace + terminal category，**不是**完整运行日志——
这是安全设计（不把原始 prompt、用户答案、API key、工具原文、绝对路径、堆栈或
provider payload 写进 bundle/CLI/TUI）。因此根因诊断需要一次受控重现，而非放宽脱敏。

## Current Direction（重启时）

安排一次 credentialed、已脱敏的真实重现，用闭合事件 envelope 采集足够的
provider/tool/validation 事实，再把根因转成 owning contract 或独立 change。

## Non-Goals

- 不为可观察性把原始 prompt / key / 路径 / provider payload 写进 bundle/CLI/TUI。
- 不从现有 retained trace 宣称根因。

## Next Step

无（暂停）。重启条件：明确授权并排期一次脱敏真实重现。
