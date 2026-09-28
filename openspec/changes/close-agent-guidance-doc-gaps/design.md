# Design — close-agent-guidance-doc-gaps

## Context

三个交付面都是既有指引文档的内容扩展；权威约束来自两个确定性检查器：
`check_doc_hygiene.py`（resident 文档字符预算，棘轮语义：上限只降不升）与
`check_change_guidance.py`（module guide 行数预算：`>=120` 行即告警、`>160` 拒绝）。
`deep_research_harness/AGENTS.md` 当前 7335 字符 / 8200 上限、**119 行**——字符余量 865，
行数余量仅 1。分析来源与产物草稿：`_backlog/plans/dsh-spirit-three-gap-closure.md`。

## Goals / Non-Goals

- Goals：三个 GAP 显式化（机制选择次序 / 持久层地图 / runbook 写法标准）；两个预算全绿且不产生任何新的常驻警告；不新建任何机制、不复制任何权威正文。
- Non-Goals：不改 LLM-Node Authoring Gate 路由（DRC-012）、不改 Information Map/Boundaries/Verification、不改生成块、不改 spec 与检查器、不上调预算、不触碰 `deerflow/`。

## Decisions

1. **GAP 1 采用"折叠列"而非独立 `## Mechanism Ladder` 表**（对 plan 草稿的显式偏离）。
   plan 草稿的独立表约 11 行，会把 guide 推到 130 行——`>=120` 行是**常驻告警**
   （`warning_reached = line_count >= 120`，非排他语义），让此后每次编辑都带着假警报。
   改为在既有 Application Focus 表加第三列 `Try first; escalate when`：0 新行，
   "最低影响机制优先 + 升级条件"逐行落在读者本来就看着的 owner 路由表里。
   plan 验收第 3 条（拿真实症状只看表能答出"先试哪层"）在该形态下依然成立。
   备选（独立表 + 到处削行凑预算）被否：为省警告而删除既有路由内容，损失大于收益。
2. **GAP 2 是链接地图，不是第二权威**。Persistence Layers 每行只放"层 + 变化速度 +
   owner 指针 + 边界一句话"；Run Bundle 契约、Projections 语义、ADR 决策一律链接/指名，
   不复制。同文件小节引用用纯文本（"see … above"），规避 checker 对裸 `#anchor` 的处理
   盲区。检验法照 DSH 02：删掉链接以外的复制正文，信息应当不丢。
3. **GAP 3 锚内容不锚行号**。对照单插在命名规则行（`📐 手册命名规则固定为
   runbook-00X-难度-用途.md`）之后；行号会漂，内容锚不会。
4. **skip_specs: true**（对齐归档先例 `harden-entry-doc-navigation`）：三处交付均为
   指引/导航内容，不建立或修改任何 capability requirement；本 change 的规范语义 backstop
   是 `deep-research-agent-charter` 的既有要求（信息地图边界、行数/字符预算、guide 不是
   第二权威），全部只被满足、不被修改。
5. **预算纪律**：不上调任何上限。AGENTS.md 实施后行数必须仍为 119（或更少），
   字符须 ≤8100（给 8200 上限留 ≥100 余量）。

## Risks / Trade-offs

- 折叠列使 Application Focus 单行加宽（最长行 ≈150 字符）：markdown 无行宽 lint，
  换来 0 新行与常驻告警规避，值得；表格仍是三列可读结构。
- Persistence Layers 若将来被当成第二权威扩充：靠两条既有守卫兜底——内容复读检验法
  写进 tasks 验收；`check_doc_hygiene` 链接规则保证指针不断。
- 对照单本身变成清单病（锁死判断）：六条中四条是现有实践的显式化，且文末带
  "guidance，不是 checklist"声明；机械部分指向真实 target 而非散文步骤。

## Open Questions

(none — 预算语义、锚点位置、policy 选择均已由检查器源码与归档先例裁定。)
