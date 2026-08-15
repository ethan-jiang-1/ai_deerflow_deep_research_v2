# BUG-018: Topic planning 的 provider timeout 未被分类为可恢复错误

> 严重级别: P1 | 发现: 2026-08-02 | 状态: 活跃

## 症状

topic planning 声明在首个安全 transient provider timeout 后应执行一次受限恢复，
但真实 bridge 产生的 timeout 不携带 `ProviderObservation`，因而节点直接终止。

无网络内存重放以 `topic_planning` 零工具请求驱动 fake node agent 抛出
`httpx.ReadTimeout`，得到：

```text
failure_code=internal.unexpected
provider_observation=False
```

预期应为 `provider.timeout` 且带安全的 provider observation，随后由 topic node
启动它声明的一次自动重试。

## 根因

`RuntimeNodeAgentBridge._is_admitted_provider_request()` 仅在
`context.node_name == "hitl1"` 时返回真。于是 topic planning 的
`httpx.TimeoutException` 被投影为 `internal.unexpected`；即使路径得到
`provider.timeout`，也没有 observation。

topic node 的 `_retry_eligible()` 同时要求 `provider.timeout` 或
`provider.unavailable` 和非空 observation，因此真实 bridge 路径不会进入恢复分支。

这使既有 BUG-010 所覆盖的 topic-planning timeout 恢复在实际 bridge 分类边界重新失效。

## 影响

- provider 暂时慢或不可用时，topic planning 跳过其声明的一次恢复机会。
- 用户只能看到不准确的终态，而不是可操作的 provider 类别和恢复事实。
- 节点规格所要求的 provider-recovery 语义只在手工构造带 observation 的测试 fixture 中成立。

## 复现

在 `RuntimeNodeAgentBridge` 的 unit seam 中，以 `node_name="topic_planning"`、
`tools_enabled=False` 构造请求，并让 fake node agent 抛出 `httpx.ReadTimeout`。
断言 bridge 返回 `provider.timeout`、安全 `ProviderObservation`，再把该结果送入
`topic_planning` node，断言 `run_agent()` 总共调用两次并记录 attempt/retry/exhaustion
事件；当前 bridge 断言为红。

## 修复关联

尚未创建 OpenSpec change。应与 BUG-017 的 failure-projection change 同时定义：
provider 可观察性和恢复资格不得以硬编码 `hitl1` 名称决定，而应由受控的 node
execution policy/phase capability 显式授权。补齐真实 bridge 到 topic node 的集成回归测试。
