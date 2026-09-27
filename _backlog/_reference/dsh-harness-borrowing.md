# DSH Harness 建设思想借鉴总账

> 最后更新: 2026-09-27 | 消化材料：外部 harness（DSH = DeepSeek Harness）建设思想的借鉴记录。
> 定位：记「学了什么、采纳了什么、为什么、明确不借什么」——**借精神，不抄形式**。
> 上游一次会话读完消化；本文是那次消化的沉淀，防止学习只活在会话历史里（静与动第三纪律：动态里的持久事实回写静态层）。

## 来源

- 消化底本：本机 DSH FAQ digest `_faq_on_digested/07_borrowing-dsh-harness-idea/`（answer + 14 章正文 + reference 证据账本；`research.md` 为内部账本未读）。
- 上游仓库：[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)，FAQ 全部原话钉版在 commit `46a7f68b09`（`dsh-v0.1.7-rc.1`）。
- 复核纪律：上游 evolve 后**只复核被本文引用的文件是否变化**，不全文重读；钉版 URL 任何机器都打得开。

## DSH 的三条立场（精华）

1. **agent 是一等参与者**——开发主力是 agent，所以知识必须外置成可发现的入口，不靠口口相传。
2. **规则是可执行的代码**——Agents follow enforced gates far more reliably than prose conventions；每条可机械判断的承诺接一条 exit non-zero 的命令。
3. **每类事实有唯一 owner**——一处一个权威，不重复、不漂移；别处只放 link。

## 对照结论：本仓已到位的部分

十维评估（DSH FAQ 的道五维 + 术五维）在本仓的快照（2026-09-27，文档级走查，非垂直切片实证）：

| 维度 | 档位 | 本仓实物 |
|---|---|---|
| 变更闭环 | 像回事 | OpenSpec 主干 proposal→tasks→红绿→门禁→archive；receipts 新鲜度；UNVERIFIED 标注 |
| 归属 | 像回事 | 根 AGENTS.md 只路由；「guide 不是第二权威」；生成块 + 重渲染纪律 |
| 决策记录 | 像回事，有缝 | `docs/adr/` 28 篇 + 索引↔目录一致性门禁；状态与负知识节已在（本次补缝，见下） |
| 静与动 | 像回事 | checkpoints/ledgers；retained run data inventory + 迁移脚本；`prompt-dump` |
| 正确路径 | 像回事 | Application Focus 表；LLM-Node 六步门；Non-Model Work 分支（本仓原创增强） |
| 入口链 | 像回事 | 根 AGENTS.md 只放常驻规则；`Do not add nested AGENTS.md` 成文 |
| 执行链 | 不适用 | host 层（DSH 拥有自己的 tool pipeline 因为它就是 host）；本仓产品侧已有对应物（policies.py、认知控制合同、run ledger） |
| 反馈 | 像回事 | `test-changed`（聚焦证据）、`mutation-check`（守卫负例控制）、proof receipts |
| Skills | 有但不成体系 | 写法标准未成文（本次补，见下） |
| 披露 | 不适用 | host 层；静态半边已由分层路由覆盖 |

关键读法：本仓的三条「不可谈判约定」几乎就是三条立场的本仓化转写。**评估结论是「精神已在，补几道缝」，不是「从零借鉴」。**

## 本次采纳（借精神的形式）

1. **ADR 取代纪律成文**（→ `deep_research_harness/docs/adr/README.md` 维护纪律节）：反转时新增 + 交叉链接 + 旧记录吸收独有理由后才可完全取代；冻结快照不再作为现行权威。实践已有（ADR-0007 被 0028 取代的 frontmatter 写法），规则此前未成文。
2. **ADR 豁免判据成文**（同上）：存在真实备选与持久取舍才写，**diff 大小无关**；检验法 = 新会话 agent 是否重提被否定的方案。
3. **常驻文档字数预算棘轮**（→ `openspec/governance/check_doc_hygiene.py` 规则 6）：只预算真正常驻的四个入口文件；**按字符计数不按词**（`wc -w` 对中文虚松一个数量级——DSH FAQ 里值钱的一个细节）；上限只降不升，上涨需在清单旁留一行理由。
4. **Skill/流程文档写法标准成文**（→ 本文下一节）：标准 + 对本仓自有 skill 的达标核对。

## 明确不借（负知识：为什么不做 X）

| 不借项 | 理由 |
|---|---|
| 插件图 / capability seam 全家桶 | DSH 造的是 agent host 本体，本仓造的是 host 面前的仓库 + 跑在只读 deerflow 上的应用。借了 = 在 read-only 框架旁造平行机制，正是「没有组合压力时提前造架构」的浪费 |
| 执行链瀑布 / 审批 / 工具体契约 / 注入预算 / compaction / 子代理隔离 | 同上层差异：这些属于 host 运行时（Claude Code、dsh 等），不归仓库所有。本仓只在自己拥有的产品运行时里做等价翻译（已有） |
| 双语 triplet + hash 配对 | 本仓单语，双语平等前提不成立 |
| per-file 100% coverage | 本仓证据观已由 delivery lanes + mutation-check 承载；全量覆盖率是另一套成本结构 |
| 加权批准制度 / Project 标签 | DSH 特定协作规模的产物 |
| ADR 增加 `proposed` 状态 | 本仓 OpenSpec 拥有提案阶段，ADR 在决定被接受时写——生命周期与本仓流程咬合，不抄 DSH 的四态目录 |

## Skill / 流程文档写法标准（六条）

写 `.agents/skills/`、`skills/public/`、runbook 或任何「一类任务怎么做」的流程文档时：

1. **触发条件一句话写进 frontmatter `description`**——「Use when … / Use before …」，把适用时机说全；目录/摘要只暴露 name + description，命中才读正文。
2. **每一步给可执行命令或可打开的文件**，不给「做好验证」这类散文（运行时 skill 的等价物：给出具体工具调用形态）。
3. **判断标准写成规则**，不给形容词；正确形态 = 步骤 + 每步的判断标准，判断留给执行者（防「清单病」：环境一变就卡死在错误步骤上）。
4. **可机械判断的部分下沉到 gate**（exit non-zero 的检查），Skill 只留需要上下文判断的部分。
5. **文末/文中声明边界**：「这是 guidance，不是 checklist」；可机械部分指向 gate 而不是 prose。
6. **命中任务时先读全文再执行**，不从摘要猜——这条纪律写进文档里。

达标核对（2026-09-27）：`skills/public/deep-research-controller/SKILL.md` 六条全过（触发在 frontmatter、意图判定成表、负例清单、边界声明「tool schema … decide whether that action is allowed」、机械合法性下沉 runtime）。`.agents/skills/` 为用户保留区，未核对、未改动。

## 维护

- 本文是留存参考，不是工作件；后续借鉴走 `_backlog/plans/` → `openspec/`。
- 「明确不借」表是负知识：重新提出表中方案前，先读理由；要推翻须新增条目说明反转原因，不删旧条目。

## 遗留与裁决（2026-09-27 复评）

| 候选 | 裁决 | 理由 |
|---|---|---|
| 垂直切片复评（DSH FAQ Phase 1 第二步：挑一笔真实变更做五行走查 + 红灯对照） | **暂缓** | 十维评估已基于实物与门禁运行（checker 全绿 + 自测负例 + 真树负例），切片是评估加深而非新借鉴；收益递减。重启条件：下次大改动前或对某维评分有疑问时 |
| 运行时查询第三面（dump 最终生效配置） | **已有等价物，不另建** | `make prompt-dump` / `prompt-dump-check`（模型可见面）、`make profiles` / `profile-check`、`scripts/configure.py` 已覆盖「问实际状态」 |
| Phase 8 防漂移 verify 脚本 | **已存在并本次增强** | `check_doc_hygiene.py` 即是（UTF-8/换行/链接/索引/scope/backlog/预算），且自带 `--self-test` 负例控制 |
| 把写法标准放进 `.agents/skills/README.md` | **不做** | 用户保留区（REVIEW 节制）；标准已记录于本文，需要时请人再落 |
