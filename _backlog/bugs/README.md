# Active Bugs — 活跃 bug 列表

> 最后更新: 2026-08-15 | `_backlog/bugs/` — 活跃 bug 在此
>
> **bug 编号权威在 `_done/_fixed_bugs/`，新 bug = 最大编号 + 1。** 本文件只列活跃 bug。

## 修完一个 bug 的步骤

1. `git mv bugs/BUG-<NNN>-<slug>.md _done/_fixed_bugs/BUG-<NNN>-<slug>.md`
2. 更新 `_done/_fixed_bugs/README.md`（加表格行 + 更新 Next available bug ID）
3. 更新本文件（删掉该 bug）
4. 更新 `../_done/README.md`（计数 +1）

---

## 活跃列表

| ID | 严重级别 | 发现 | 标题 |
| --- | --- | --- | --- |

| [BUG-025](BUG-025-active-bundle-projected-as-invalid-result.md) | P0 | 2026-08-15 | 进行中的 Bundle 被投影为 `protocol.invalid_result` |
| [BUG-026](BUG-026-gate-fatigue-omits-failed-reference.md) | P0 | 2026-08-15 | Gate fatigue 没有区分失败的工作单元 |
| [BUG-027](BUG-027-wave1-source-diagnostic-enum-contract-omitted.md) | P1 | 2026-08-15 | Wave1 SourceDiagnostic 提示词漏掉枚举契约 |
| [BUG-028](BUG-028-wave1-targeted-search-has-no-repair-path.md) | P1 | 2026-08-15 | Wave1 `targeted_search` 没有真正的修复路径 |
| [BUG-029](BUG-029-invalid-critic-output-is-silently-suppressed.md) | P1 | 2026-08-15 | 非法 critic 输出被静默丢弃 |
| [BUG-030](BUG-030-real-demo-lacks-live-human-readable-trace.md) | P1 | 2026-08-15 | 真机 demo 长时间运行没有实时人类可读轨迹 |
| [BUG-031](BUG-031-no-narrow-real-workflow-debug-path.md) | P1 | 2026-08-15 | 缺少窄而真的三波调试路径 |

**Next available bug ID: BUG-032**

---

## 卡片模板

新建 bug 文件 `BUG-<NNN>-<slug>.md`，`<NNN>` 取 `_done/_fixed_bugs/README.md` 的 Next available ID：

```markdown
# BUG-<NNN>: <一句话标题>

> 严重级别: P0 / P1 / P2 | 发现: 2026-MM-DD | 状态: 活跃

## 症状
观察到什么错误行为（现场、报错、复现路径）。

## 根因
定位到的机制层原因（越到"契约/结构"层越好，避免只描述表象）。

## 复现
最小复现步骤 / 命令 / 输入。

## 修复关联
落地的 OpenSpec change 名称 + 版本；或说明为何拆成更窄的 follow-up。
```

> 约定：严重级别用 `P0`（阻断）/ `P1`（重要）/ `P2`（次要）。把每个 bug 当作**契约探针**——一个具体缺陷往往牵出一整类失败，值得顺藤摸瓜做横切排查，而不是只打一个孤立补丁。
