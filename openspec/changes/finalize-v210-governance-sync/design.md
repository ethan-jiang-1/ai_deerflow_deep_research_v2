# Design

## Context

submodule 本体已在 `ceebf97f`（v2.1.0，ethan tip），contract test pin
`CURRENT_DEERFLOW_PIN` 已同步；只有治理声明值与 spec 措辞停在旧状态。
`check_project_gate.py --phase closeout` 的 `gitlink.index_commit` 红灯是当前唯一
治理阻塞（本 change 的验收基线，`_backlog/plans/harness-tech-debt-cleanup.md`
四路审计有完整取证）。

## Goals / Non-Goals

**Goals:**

- 声明值 = 真实 gitlink，closeout 门转绿，恢复 archive 通道。
- v2.1.0 升级获得可追溯的批准记录（消除未留痕先例）。
- CNI-001 标题条款与 11 个 `workflow.md` 现状一致（改 spec 侧，卡片零改动）。

**Non-Goals:**

- 不给治理门新增门禁挂载或防漂移断言（属 P3 守护机制，另行处理）。
- 不触碰 submodule 本体、运行时代码或测试基线。

## Decisions

1. **更新治理声明，而不是回退 submodule。** 真实研究运行已全面验证 v2.1.0
   （`UV_OFFLINE=1 make verify` 3067+ 绿、live 48/50），回退等于推翻已验证状态；
   且 `da5721d` 适配代码以 v2.1.0 契约为基线。备选"回退 submodule"被否。
2. **CNI-001 改 spec 措辞而非改 11 张卡片。** 卡片的 `# <node> — <职责>` 形式
   信息量更高（节点名 + 职责 vs 固定字面量），且
   `tests/contract/test_node_workflow_reader_interface.py` 锁的就是现状；
   修改 spec 一处 vs 修改 11 处 + 测试。用户已拍板此方向。
3. **本 proposal 兼作升级的追溯批准记录**，而不是另立一份独立决策文档：
   openspec 的 change + archive 本身就是本仓库的决策留痕机制，重复建档案反而
   制造第二权威。
4. **代码侧镜像锚点（`CURRENT_DEERFLOW_PIN`）保持为独立事实**，本 change 只在
   README 注记中互指两者，不引入新的单一权威文件（防漂移断言属 P3）。

## Risks / Trade-offs

- [声明值更新后若有人再动 submodule 而不改声明，门会再红] → 这正是门的设计意图；
  P3 的门禁挂载与双锚点断言负责让它"红得被看见"。
- [CNI 措辞修改使旧字面量搜索落空] → delta 保留完整 requirement 与场景，
  归档历史仍可检索旧措辞。
- [回滚] → 单 commit 还原 toml/spec/README 三处即可；无运行时影响。
