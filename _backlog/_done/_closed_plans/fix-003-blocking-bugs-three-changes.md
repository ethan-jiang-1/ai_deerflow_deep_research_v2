# Plan: 003 阻断 bug 修复战役 —— 3 个 change 修掉 BUG-047..054

> 类型: 设计 + 执行计划 | 更新: 2026-08-19 | 关联: `_backlog/_done/_fixed_bugs/` BUG-047..054（已全部修复归档）
>
> **状态: ✅ 战役完成（2026-08-19）**。三个 change + 提前的 preserve-failed-run-bundles
> 全部实施、测试门全绿（2123 passed / ruff clean）、归档，主 specs 已同步。
> 真实 003 复跑 `RESULT: PASS`（9 阶段 completed，报告含真实 findings 结论与
> 诚实 Uncertainties 披露）。遗留：BUG-048 第 7 项（state.json/checkpoint
> 自洽投影）为 follow-up——投影面无主 spec，需独立合同决定。

## 背景 / 现状

2026-08-18 晚四次真实 003 run（真实 DeepSeek + Tavily 全自动），四次全部 `RESULT:
FAIL`，但每次失败都**推进了一段并暴露一层新缺陷**：

| Run | 死在哪 | 根因 → 卡 |
|-----|--------|-----------|
| 1 | wave1 model_tool 挂起 28 分钟 | 已知 SDK 挂起（非 bug，runbook §7） |
| 2 | wave2→readiness 循环 4 轮，readiness critic 4 次 `token_admission` 拒绝 | 信封算术矛盾 → **047** |
| 3 | wave2 a3 pre-model 20ms 暴毙 | 无界证据投影顶破 objective 16384 上限 → **049** |
| 4 | 前八节点全通，final_delivery 3 次模型调用全成功却零发布 | 退化 layout 合同 + 零结论 plan → **053/054** |

排障期间另发现观测性与流程缺陷 4 项（**048/050/051/052**）。

**已有资产**：BUG-047/049 的修复已在本地实现（TDD，全量 2105 tests + ruff 过）并经
run 4 验证生效（readiness 首次真正运行、wave2 六条证据不再溢出），**未提交**，
等待收编进正式 change。

**核心判断**：只修 047/049 拿不到 PASS——run 4 证明链路能走到 final_delivery
然后死在 053/054。003 要 PASS，必须同时解决"中途暴毙"（机械层）和"终局零交付"
（语义层）。

## 决策 / 方案：8 张卡 → 3 个 change

分组原则：**因果同类 + 同一批 spec 面**。不是按"好修不好修"，是按"哪几张卡
不一起改就会互相返工"。

---

### Change 1: `fix-request-envelope-coherence`（请求信封一致性）

- **收编卡片**: 047 + 049 + 048 第 5 项（ValidationError 类别保真）
- **Goal**: 任一 prompt 构建器在其声明的最大输入下产出的请求，必须**确定性地**
  同时满足域契约上限与节点 admission 信封——把"上限必须成对推导"固化为一类
  不变量，而不是散落的魔法数字。
- **核心思想**: 047 和 049 是**同一个病**的两处发作：一对必须一致的上限各改各的。
  047 是"admission 信封 8K < 构建器证据投影 8K+脚手架"；049 是"objective 域上限
  16384 < 证据投影无上限"。修法同构：有界投影（确定性截断 + truncated 标记）+
  信封对齐（readiness 16K / final_delivery 24K / wave2 投影拟合 16384 字符与
  46K 字节）+ 不变量测试锁死。048.5 并入是因为没有"类别保真"，下一个同类 bug
  还会伪装成 `candidate_invalid` 排查不出来。
- **Scope**（大部分已实现，change 主要是正式化 + spec 同步）:
  - `runtime/research.py` readiness/final_delivery 预算（本地已改）
  - `wave2_synthesis/prompts.py` 有界投影（本地已改）
  - pre-model 失败带具体类别（新增，小）
  - 两个不变量测试（本地已有）+ 类别保真测试（新增）
- **Spec deltas**: `readiness-node`、`final-delivery-node`、`wave2-synthesis-node`、
  `workflow-failure-outcomes`
- **风险**: 低。行为已被 run 4 验证；纯机械，无语义决策。

---

### Change 2: `honest-degraded-delivery`（诚实降级交付语义）★ 战役核心

- **收编卡片**: 054 + 053 + 050 + 051
- **Goal**: honest gap 不收敛时，run 以**带披露的 completed** 终结并交付真实部分
  结论——兑现 runbook-003 §5.1 的承诺，003 拿到 PASS。
- **核心思想**: 四张卡是**一条语义链**，拆开必返工：
  1. **054 是源头**（交付语义）：证据不完美 ≠ 零交付。高置信、引用完备、直接回答
     问题主干的 finding 必须成为可写结论，gap 同时如实披露——"部分结论 + 强制
     不确定项并存"取代现在的"insufficient → 零结论"。
  2. **053 是终端**（渲染合同）：退化 plan（结论数+不确定项数 ≤ 1）的排序数学上
     唯一，跳过模型直接确定性渲染；不再赌模型回显合成 id `uncertainty:0`。
  3. **050 是兜底**（终态路由）：节点级可降级失败（预算类）交还 gate 走
     degraded-pass 而不是直接 blocked；runbook 5.1 的承诺范围与实现对齐
     （哪个方向对齐是设计决策，见任务）。
  4. **051 搭车**（数据合同）：open-question id 加 work 前缀全局唯一 + 解析处
     碰撞显式处理。与前三项共用 wave1→wave2→交付 disposition 合同，一次改完。
  顺序依赖：054 定了"结论从哪来"，053 才知道"渲染什么"；050 定了"失败怎么终"，
  runbook 才敢写"何时 PASS"。所以必须一个 change。
- **Scope**:
  - `readiness/materializer.py`：部分结论生成（verdict→可写结论映射放宽）
  - `final_delivery/composer.py` + `node.py`：退化 plan 确定性渲染分支
  - `wave2_synthesis/node.py` + gate 交互：可降级失败类别交还 gate（或收窄承诺）
  - `wave1` open-question id 命名 + `wave2_synthesis` 解析
  - runbook-003 §5.1 措辞与实现同步
- **Spec deltas**: `readiness-node`、`final-delivery-node`、`gate-kernel`、
  `research-graph-lifecycle`、`wave1-node`、`wave2-synthesis-node`、
  `low-scale-real-auto`（验收语义）
- **风险**: 中。含两个真设计决策（见"风险"节），需要 grilling/评审；是唯一动
  产品语义的 change。
- **成功判据**: 真实 003 run `RESULT: PASS` + `final/report.md` 含真实结论与
  claim-citation 映射 + Uncertainties 披露未收敛 gap。

---

### Change 3: `run-forensics`（run 取证与观测性）

- **收编卡片**: 048（第 5 项外的 5 项）+ 052
- **Goal**: 出事后能便宜地查清楚——事件自包含、现场可保留、用量可分析。
- **核心思想**: 全部**零研究行为变更**：admission 拒绝事件带 `projected/budget/cap`
  操作数；run-summary 附各 phase 策略信封快照；readiness critic 保守兜底发节点级
  事件；`model_tool completed` 带 usage tokens + 调用序号；state.json 与 checkpoint
  自洽；重跑保留（而非销毁）失败 bundle。排障从"写脚本推断"回到"grep 一行"。
- **Scope**: `agents/middleware.py`（detail 带操作数）、bridge（usage/序号事件）、
  `readiness/node.py`（兜底事件）、run-summary 组装、soft-bundle 清理策略（保留
  最近 N 个或归档 blocked bundle）。
- **Spec deltas**: `run-event-journal`、`runtime-observability`、
  `run-bundle-discovery-and-operations`
- **风险**: 低。唯一要留意 bundle 保留的磁盘占用上限（设 N=3~5 即可）。

---

## 执行顺序（含依赖理由）

```
Change 1  ──►  Change 3 的 052 任务（提前单独做）  ──►  Change 2  ──►  003 复跑 PASS  ──►  归档收尾
```

**每个 change 的固定工作流（用户指令固化）**：

```
openspec-propose（全套 artifacts）
  → polish-openspec-change（至少两轮风险主导打磨，直到 apply-ready；
    validate --strict + git diff --check 过，无未决矛盾才许进 apply）
  → openspec-apply-change（按 tasks 实施，全量测试门）
```

三个 change 按此流程**一口气连续执行**（用户已授权全程），change 之间的 003 真实
run 验证按 runbook §7 重试纪律执行。

1. **Change 1 先行**：消灭"中途暴毙"，且 90% 已实现——成本最低、立即减少后续
   调试噪音。没有它，Change 2 的真实 run 验证根本跑不到 final_delivery。
2. **052 提前**（哪怕 Change 3 整体后置）：调试 Change 2 期间每次重跑都在销毁失败
   现场（run 1-3 的证据已因此丢失）。先装"消防栓"再灭火。
3. **Change 2 收官**：语义核心，需要设计评审（grilling）定两个决策点，然后实施、
   真实 003 复跑拿 PASS。
4. **Change 3 其余**：PASS 之后做（此时才有余裕），或与 Change 2 并行起草。
5. **归档**: 047/049 → change 1；050/051/053/054 → change 2；048/052 → change 3。
   runbook-003 §5.1 按 Change 2 结论改写；handoff-003 状态行更新。

## 风险 / 取舍

- [Change 2 决策点 A：054 的"部分结论"边界] 谁有权判定可写——readiness critic
  （模型）还是 synthesis findings 的确定性映射（规则）？→ 倾向规则映射为主
  （引用完备 + 置信阈值），critic 只做否决；评审时 grilling 敲定。
- [Change 2 决策点 B：050 的承诺方向] 是"节点级失败也走降级"（扩机制），还是
  "runbook 5.1 收窄为仅 gate 路径"（改文档）？→ 倾向扩机制（预算类失败可降级），
  否则 003 的 PASS 依赖模型永远不超预算，太脆。
- [051 改 id 格式会破坏旧 bundle 兼容] → 只影响 graph 内部投影，不落盘对外契约；
  实施时确认无持久化引用即可。
- [三个 change 串行的总时长] → Change 1 半天（已实现）、Change 2 是大头（评审+
  实施+多次真实 run）、Change 3 半天。真实 run 的模型波动（挂起、repair 多轮）
  会拖慢验证——按 runbook §7 重试，不升级为设计问题。
- [Change 2 失败兜底] 若"部分结论"评审不下来，最小可行退路：只做 053（确定性
  渲染）+ 050（降级路由），让 run 以"零结论但 completed + 披露"收场——003 形式
  PASS，054 留待后续。这是下策（报告无真实结论），但保住 PASS 里程碑。

## 落地关联

- Change 1 → `openspec/changes/fix-request-envelope-coherence/`（吸收本地未提交
  修复与两个不变量测试，起草用 `openspec-propose`）
- Change 2 → `openspec/changes/honest-degraded-delivery/`
- Change 3 → `openspec/changes/run-forensics/`
- 本 plan 是三者的总纲；各 change 的 tasks.md 落细节。全部归档后本 plan 移入
  `_done/_closed_plans/`。
