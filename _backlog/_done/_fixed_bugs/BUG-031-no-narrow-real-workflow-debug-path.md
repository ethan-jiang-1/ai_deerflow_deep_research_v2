# BUG-031: 缺少窄而真的三波调试路径

> 严重级别: P1 | 发现: 2026-08-15 | 状态: 活跃

## 症状

要判断真实 Wave0、Wave1、Wave2 是否能完成一次正确动作，当前只有两个不合适的入口：

- `make demo-real[-scripted]` 会调用真实模型和网页检索，按完整预算运行，单次可持续几十分钟并产生 API 成本；
- `make demo[-scripted]` 是零凭据 fixture graph，替换了节点 adapter，不能证明真实 node、parser、work-unit、gate 和存储的组合。

结果是每次调试真实图的契约问题，都只能付出一次完整研究的时间和费用；开发者经常因此只跑较浅的
测试，无法快速验证三波之间的实际 handoff。

## 根因

产品入口被有意固定为 all-real，fixture demo 则有意使用完整 fixture recipe。测试中虽已有
`SCRIPTED_REAL_WORKFLOW` 能力和 `ScriptedChatModel` / `ScriptedTool`，但它们分散在单节点或
小范围测试里，尚未形成一个可由操作者执行的、完整但极窄的生产节点调试 composition。

## 复现

从 `deep_research_harness/` 执行以下两条命令并比较其证据边界：

```bash
make demo-real-scripted
make demo-scripted
```

前者要求真实凭据并执行完整真实研究；后者无需凭据但输出 `fixture` composition。当前没有一个
零 API、十秒级、同时经过真实 Wave0/Wave1/Wave2 的第三入口。

## 修复关联

`_backlog/plans/narrow-scripted-real-workflow-debug-path.md` 规定新的 operator-only debug command
及其真实性、预算和观测契约。它必须由独立 OpenSpec change 实现，不能作为 `demo-real` 的隐式
降级开关。
