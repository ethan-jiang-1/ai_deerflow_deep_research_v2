# BUG-004: checkpoint 依赖未注册类型反序列化，未来将硬失败

> 严重级别: P1 | 发现: 2026-07-22 | 状态: 已修复

## 症状

真实 CLI 在第三次 HITL1 resume 后输出 LangGraph 警告：

```text
Deserializing unregistered type deerflow_deep_research.domain.state.ContentRef from checkpoint.
Deserializing unregistered type deerflow_deep_research.domain.work_units.AttemptStatus from checkpoint.
This will be blocked in a future version.
```

当前运行勉强继续，但依赖升级或 `LANGGRAPH_STRICT_MSGPACK=true` 会把已经写入的 checkpoint 变为不可读，使 resume/status/后续节点失败。

## 根因

ResearchState checkpoint 直接含有项目自定义 `ContentRef` 与 `AttemptStatus` 实例；当前 LangGraph msgpack 解码器允许带警告的未注册反序列化，项目没有显式 allowlist 或把这些值规范化为原生 JSON 类型。该警告发生在真实 checkpoint 恢复路径，不是 CLI 文案问题。

## 复现

```bash
cd /Users/bowhead/ai_deerflow_deep_research/agent
make demo-real DEMO_ARGS='--question "比较锂电池和液流电池在电网储能中的成本、风险与适用场景"'
```

完成至少一次真实 HITL1 resume 后观察 stderr；使用 `LANGGRAPH_STRICT_MSGPACK=true` 的兼容性测试应将当前警告升级为失败。

## 修复关联

纳入 `harden-deep-research-real-cli-intake-and-observability` 的 checkpoint compatibility 任务：先建立 strict-msgpack 红测试，再选择显式最小 allowlist 或原生 JSON state 规范化，并验证旧 checkpoint 的可读性、严格模式、无未注册类型警告和不扩大反序列化信任面。
