# Plan: openspec 规则可达性 —— 把"存在但够不着"的治理规则接进执行链

> 类型: 设计 + 执行计划 | 更新: 2026-08-19 | 状态: **待采纳**（决策点 A/B 见 §5）
> 关联: [openspec-materials-feedback-from-bugfix-campaign.md](openspec-materials-feedback-from-bugfix-campaign.md)（战役复盘，本 plan 的证据基底）
> 建议载体: **一个 change** `openspec-rule-reachability`（用户指示单 change；④ 预声明拆分条件）

## 背景 / 现状

003 战役（BUG-047..054，4 change 全流程）实证：openspec 材料分层合理、不冗余，
但三条 mid-flow 最需要的机械规则不在执行链里，作者是从 CLI 报错里学到的：

| 咬人的坑 | 规则现在住哪 | 应该住哪 | 战役实伤 |
|---|---|---|---|
| MODIFIED 块丢原场景 | 仅 `openspec archive` 的报错文本 | change-guidance 机械卡（作者写 delta 时就知道） | 归档咬 2 次，第二次本可避免 |
| 新 requirement ID 漏登记 | 仅 `check_project_reqs.py`（不在任何门禁里） | 写作/润色阶段即红 | REJ-009 漏登记，靠复盘补课 |
| `## Change Focus` MUST | 仅 `config.yaml` rules.proposal（`validate --strict` 不查） | 被 validate 或 polish 链执行 | **4 个 proposal 全部合规绕过** |

三个关键事实（写 plan 前核实，决定方案形态）：

- **F1** `openspec` CLI 是外部 npm 包（v1.9.0，nvm 路径）——**不可改**。原建议③
  "ID 分配进 openspec validate" 只能落地为**本地 enforcement**。
- **F2** `.agents/skills/`（polish / archive 等）是**仓内文件**——skill 的 pass 判据
  可以编辑，这是本地 enforcement 的自然挂点。
- **F3** `check_change_guidance.py` 锁死 `change-guidance/local/deep-research.md` 的
  结构（必需 `## Reader Roles` / `## Line Budgets`、硬编码文件清单）——原建议④
  "路由表单源化"必须连带改 checker，比文档编辑重。
- **F4（顺序约束）** 既有 drift：EXI-001 / LSA-001 / RGL-014 / SCR-006 未登记、
  low-scale-real-auto spec 2 处 violation、`.gitignore` policy 不匹配——**若先把
  checker 纳入归档硬门禁，这些 drift 会把所有后续 change 堵死在归档**。清理必须前置。

## 目标 / 非目标

**目标**：规则可达——作者在写作/润色阶段就被机械规则拦住，而不是归档时被 CLI
后知后觉地咬。具体三条：delta 机械规则成文、governance checker 进归档门禁、
ID 登记在 polish 阶段可查。

**非目标**：不改外部 openspec CLI（F1）；不改任何 runtime 行为（本 plan 全部是
文档/governance/skill 层）；不处理 BUG-055 与 `fix-final-delivery-layout-fragility/`
（并行起草中，零重叠）；不做 registry↔spec-header 的单一来源化生成（那是长期项，
本 plan 只把"双登记"变成机械可见）。

## 方案：change `openspec-rule-reachability`，5 个 task 组

### T0 前置：清既有 drift（阻塞 T2 的硬前提）

逐项调查并修复：4 个未登记 ID（查 git 历史确认是合法分配还是误写，再补
req-registry.yaml + 对应 spec header）、low-scale-real-auto 的 2 处 spec 结构
violation、`.gitignore` entries 与注册 policy 对齐。完成后 5 个 checker 全 0——
这是把 checker 纳入门禁的先决条件（F4）。

### T1 = 建议①：`change-practice.md` 增 "Delta Mechanics" 卡（~15 行）

三条机械规则，全部有战役实证：**(a)** MODIFIED 块必须携带被修改 requirement 的
**全部**原场景（verbatim），新增场景附在后面；**(b)** `### Requirement:` 标题是
语义锚，不得内嵌 ID，ID 只出现在 `> req:` 行 / tasks `@impl` / registry；
**(c)** 新分配 requirement ID = registry 登记 + main spec `> req:` 行**双登记**，
缺一即红。放在 core（而非 local）——这是 OpenSpec 通用机械，不是 Deep Research 特有。

### T2 = 建议②：checker 进归档门禁

`config.yaml` `rules.tasks` 增一条 bullet：归档前跑 5 个 governance checker
（reqs / specs / architecture / change_guidance / req_coverage），**退出码直测**
（管道 `| tail` 会吞退出码——战役中实测踩过，写进 bullet 原文）。
前提 T0 完成；T4 若拆出亦不受影响（本条只引用命令不改其语义）。

### T3 = 建议③的本地形态：ID 可查性前移到 polish 阶段

不可改 CLI（F1），改为：`polish-openspec-change` skill 的 pass 判据清单加一项
"若 delta 引入新 requirement ID：registry 已登记且 main spec header 已同步"
（skill 在仓内，F2）。备选增强：`check_project_reqs.py` 支持单 change 参数便于
快速自查（可选，非阻塞）。

### T4 = 建议④：路由表单源化（**预声明拆分条件**）

`change-guidance/local/deep-research.md` 的 Reader Roles 表与
`deep_research_harness/AGENTS.md`/`docs/README.md` 信息重复，双份会 drift。
做法：表换成指向 harness 单源的指针，local 文件只留 Deep Research 特有内容
（Program form / Line Budgets）。**拆分条件**：F3 所述 checker 的必需 section /
文件清单耦合如果使改动超过 ~半天，T4 拆成独立 change，不拖累 T0–T3 落地。

## 决策点（采纳时拍板）

- **A（T2 门禁强度）**：checker 红是**硬阻断**归档，还是"红即记录、留 unchecked
  task"？倾向硬阻断（治理意义所在），代价是 T0 必须彻底。
- **B（T4 时机）**：随本 change 做，还是缓？倾向**缓/独立 change**——性价比四条
  中最低，且 F3 耦合让它最可能膨胀。

## 验收标准（模拟可测）

1. 造一个缺 `## Change Focus` 的新 proposal → polish 或归档前被本地链抓住
   （战役中是 4 个全部溜过）。
2. 造一个用未登记新 ID 的 delta spec → polish 阶段红（战役中是归档后复盘才发现）。
3. MODIFIED 块故意丢一个场景 → `openspec archive` 仍拦（CLI 既有行为不变），
   但作者在 polish 阶段已从 T1 卡片知道这条规则。
4. T0 后 5 个 checker 退出码全 0，且此后任何 change 归档都保持全 0。

## 执行顺序 / 风险

顺序：T0 → T1 → T2 → T3 →（T4 视决策点 B）。

- [风险：门禁变严拖慢未来 change] → T0 先清零 + 决策点 A 可选"先 warning 一轮
  再 hard"的两步走。
- [风险：skill 是共享目录，改动影响所有 agent 流程] → 只在 pass 判据清单**加一条**，
  不动流程骨架；skill 改动本身也走本 change 的验证。
- [风险：T0 的 4 个 drift ID 调查可能有合法归属争议] → 只登记不重构；争议 ID
  在 card 里留注。
- [规模估计] T0 ≈ 0.5–1h（调查为主）；T1/T2/T3 各 < 1h；T4 视调查。
