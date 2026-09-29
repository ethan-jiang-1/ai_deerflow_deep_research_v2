# Tasks

## 1. 红环

- [x] 1.1 矩阵：`set_watch_fields` 接受类型化字段/拒绝未知字段；drive 命中
      `research_depth` 变化即停且快照携带命中、基线推进——红。
- [x] 1.2 pilot：`/bt` 渲染路径与当前位（未知命令现在会被当文本答案消费——红）；
      `/state research_depth` 渲染有界值、未知字段拒绝——红；`/watch research_depth` +
      `/run` 停止 + `⚑ 观察点触发` 渲染——红。

## 2. 实现

- [x] 2.1 `domain/debug_driving.py`：快照加法字段 `watch_hits`。
- [x] 2.2 `runtime/debug_driver.py`：`set_watch_fields`（字段白名单校验）+ 驱动循环
      观察比对（复用断点的 read_state）+ 基线推进 + 快照携带命中。
- [x] 2.3 `scripts/demo_tui.py`：/bt、/state、/watch、/unwatch 路由与渲染；/help 补行。

## 3. 门禁与收尾

- [x] 3.1 登记 LDD-009、RED-016→无、RED-017；spec 同步归档；矩阵/pilot/verify/
      journey/proof 全绿；live 快速档复跑。
- [x] 3.2 分层提交 + push（SSH 恢复后）。

> 注：用户于 2026-09-29 授权全程自主执行，apply 依此授权进行。
