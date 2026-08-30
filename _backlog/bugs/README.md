# Active Bugs — 活跃 bug 列表

>
> **bug 编号权威在 `_done/_fixed_bugs/`，新 bug = 最大编号 + 1。** 本文件只列活跃 bug。

## 修完一个 bug 的步骤

1. `git mv bugs/BUG-<NNN>-<slug>.md _done/_fixed_bugs/BUG-<NNN>-<slug>.md`
2. 更新 `_done/_fixed_bugs/README.md`（加表格行 + 更新 Next available bug ID）
3. 更新本文件（删掉该 bug）
4. 更新 `../_done/README.md`（计数 +1）

---

## 活跃列表

| Bug | 标题 | 发现 | 状态 |
|-----|------|------|------|
| [BUG-063](BUG-063-hitl-suspension-journal-mislabel.md) | HITL interrupt 挂起被 journal 记为 internal.unexpected（诊断误导） | 2026-08-30 · 020 战役 B1 监控 | 活跃（并入 C2） |
| [BUG-064](BUG-064-no-attach-resume-after-process-death.md) | 断网/进程死亡即失去 run：无 attach/resume 入口，孤儿 bundle 不可恢复也不可 inspect | 2026-08-30 · 020 战役 B1 第 2 跑 | 活跃（C2 进行中） |

**Next available bug ID: BUG-065**


---



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
