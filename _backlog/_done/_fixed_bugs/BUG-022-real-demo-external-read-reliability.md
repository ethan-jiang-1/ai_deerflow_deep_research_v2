# BUG-022: 真实研究演示将瞬态外部读取失败过早终止

> 严重级别: P1 | 发现: 2026-08-02 | 状态: 已修复，已归档

## 症状

历史上的真实 CLI 曾在 HITL1 阶段以 `research.blocked` 终止，而 demo Tavily 的
`web_search` / `web_fetch` 曾会把一次超时、连接中断或临时服务错误直接映射为不可用结果。
当前保留的终态只证明曾在 `hitl1` 阻断，不能反推具体根因；Tavily 的直接读取问题必须在
其独立的确定性 seam 证明。

这会把一次正常的第三方网络抖动放大为整次研究失败或缺失证据，尤其影响需要连续搜索和
抓取的真实 CLI 运行。

## 根因

真实 CLI 路径有两类外部 I/O。此前的战术修复已经：

1. 将 HITL1 零工具模型调用 wall-time 对齐为 60 秒，且没有扩大既有阶段的一次恢复或两次
   brief invocation 上限。
2. 为演示层 Tavily 幂等 `search` / `extract` 加入 60 秒每次尝试、最多三次总尝试和 1/2 秒
   退避的直接读取边界。

剩余工作不是扩大重试范围，而是以 `DPL-009` 完成精确证明与边界收口：只允许 timeout、
transport/protocol、usage-limit、429、500-599 重试；证明退避可取消、异常不会泄漏、同次
search-to-fetch provenance 不变，并由共享 terminal 投影保留已存在的安全类别。

现有 worker 配额不是根因：Wave0/Wave1 各有 900 秒 wall-time、200 次工具调用和 200 万
token 预算。问题发生在单次外部读取的可靠性边界。

## 复现

1. 从 `deerflow_research/` 执行 `bash run/real-research.sh`。
2. 检查保留的 terminal，记录其安全类别、阶段和诊断引用，不将 `research.blocked` 解释为
   某个未证实的 provider 原因。
3. 在 `_build_demo_tavily_tools` 的 Tavily client 中注入一次 `httpx.ReadTimeout`、429 或
   500-599；断言后续尝试按 1/2 秒有界退避。对认证、非 429 4xx、状态 600、未知异常和取消
   断言不会得到额外尝试。

## 修复关联

本 bug 的收口由 OpenSpec change `harden-real-research-external-io` 管理；它不会将 demo
工具重试扩展为 graph、lifecycle 或全局 provider controller。

验收条件：

- HITL1 每次模型调用预算保持 60 秒，既有阶段级一次恢复不扩大。
- Tavily `search` / `extract` 每次尝试保持 60 秒上限；仅 timeout、transport/protocol、
  usage-limit、429 和 500-599 最多尝试三次，使用可取消的 1/2 秒退避。
- 认证、参数/输入、非 429 的 4xx、状态 600、未知异常和取消不重试；保留脱敏 unavailable
  payload 及同次 search-to-fetch URL provenance。
- 确定性测试覆盖分类、恢复、耗尽、退避取消、脱敏和 provenance；其后运行一条有界真实
  canary，再根据记录的安全事实决定关闭或保留本 bug。

## 本次实施证据（2026-08-03）

- `DPL-009` 的聚焦确定性 lane 与 HITL1/CLI 邻接 lane 合计为 `125 passed`；测试资产、需求注册和需求覆盖检查均通过。直接 Tavily seam 已覆盖允许与拒绝的分类、三次上限、60 秒 attempt timeout、1/2 秒可取消退避、脱敏 unavailable payload 和同次 search-to-fetch provenance。
- preflight 通过后仅运行一次 `bash run/real-research.sh`：run `r_YFc9zaYkbQmoU2wU5O0YyNavljOE8I4wc_HiirXlSFE` 返回 `research.blocked`，阶段 `hitl1`，诊断 `diag_YZ_PWs_cyMwf5j5Pr-ke8pVv`。该 run 未到达首次 HITL1 suspension 或后续阶段，且没有执行手工重试。

该 canary 没有到达 Tavily 读取，不能作为外部读取可用性或本 bug 根因的证据。它记录的是独立的 HITL1 阻断，不能覆盖或推翻 Tavily 直接读取边界的确定性结论。

## 关闭证据（2026-08-03）

- 以历史实际实现 `5888c6b:deerflow_research/scripts/_demo_core.py` 做无外网差分回放：向真实 `web_search` tool factory 注入按顺序的 `httpx.ReadTimeout` 与成功 Tavily 响应，旧实现返回 `web_search_unavailable` 且只调用一次；当前实现对同一输入返回正常结果且恰好调用两次。该回放直接覆盖原始“第一次瞬态失败即终止”症状。
- 当前边界回归覆盖瞬态分类、恢复、三次耗尽、60 秒单次 deadline、1/2 秒可取消退避、非瞬态不重试、取消和同次 provenance；针对本 bug 与 HITL1/CLI 邻接边界的选择集为 `24 passed in 1.45s`。

因此本 bug 的直接 I/O 根因已由可重复的红绿差分和回归证据关闭。该结论不承诺 Tavily 永远可用，也不将无关的 `research.blocked@hitl1` 归因为 Tavily。
