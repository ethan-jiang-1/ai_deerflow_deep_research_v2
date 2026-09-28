# Tasks — close-agent-guidance-doc-gaps

## 1. GAP 1 · Application Focus 折叠"先试最低影响机制"列

- [x] 1.1 在 `deep_research_harness/AGENTS.md` 的 Application Focus 表新增第三列
      `Try first; escalate when`：六行各给出该 owner 之前先尝试的最低影响机制与升级条件
      （domain←config/profile 表达；engine←config 旋钮 `timeout`/`max_retries`/开关；
      agents←`config.yaml` 的 model/tool posture；graph←既有 profile/组合旋钮；
      runtime←config/profile 绑定；presentation←既有 result projection）。
      不新增任何行；不改 LLM-Node Authoring Gate、Information Map、Boundaries、
      Verification 与生成块。
- [x] 1.2 预算实测：`wc -l` 仍为 119（实测 119）；`wc -m` ≤8100（实测 7962，余量 238）。
      退出码直测：`python3 openspec/governance/check_doc_hygiene.py` exit 0、
      `python3 openspec/governance/check_change_guidance.py` exit 0 且无
      `entry.line_budget_warning`。

## 2. GAP 2 · runtime-architecture 持久层四层地图

- [x] 2.1 在 `deep_research_harness/docs/runtime-architecture.md` 的
      Projections And Observations 之后、Source And Structural Contract 之前新增
      `## Persistence Layers`：四层表（Rule/map=PR 守护的指引与 ADR；Config=root
      `config.yaml`+`profiles/` 显式 profile check；Fact source=Run Bundle
      State/checkpoints/journal 单写者；Derived=reports/projections/diagnostics 可重建）
      + 三条纪律（派生不存第二份真 → 指向 Projections 节；模型可见 ⟺ 可重建 → 指向
      Node Context Snapshot/`make prompt-dump-check`/runbooks 030/031；会话持久事实
      回写 owner）。同文件小节引用用纯文本，不用裸锚点。
- [x] 2.2 复读自检：本节不含 Run Bundle 契约、Projections 语义或 ADR 决策的复述正文
      （删掉链接/指针以外的正文，事实不丢）；`check_doc_hygiene.py` exit 0（链接规则
      覆盖 `adr/README.md` 相对链接）。

## 3. GAP 3 · runbook 写法对照单

- [x] 3.1 在 `deep_research_harness/docs/runbooks/README.md` 紧跟命名规则行
      （`📐 手册命名规则固定为 runbook-00X-难度-用途.md`）之后新增
      `### 写新 runbook 的对照单`：六条——开头一句话写"何时用这份"；每步给可执行
      命令或可打开入口；判断标准写成规则不写形容词；可机械判断部分指向真实
      make target/checker；文末声明本手册是 guidance 不是 checklist；新增后在本
      README 索引加一行。
- [x] 3.2 `check_doc_hygiene.py` exit 0（该文件在 DOC_LAYER_DOCS 内，链接/编码被扫描）。

## 4. 回执、门禁与收口

- [x] 4.1 新鲜回执（命令 + 退出码 + revision，写入提交信息）：
      `check_doc_hygiene.py --self-test`（既有守卫负例控制）passed；
      `check_doc_hygiene.py` passed；`check_change_guidance.py` passed；
      `check_project_gate.py --phase closeout` exit 0；`UV_OFFLINE=1 make verify` exit 0。
- [ ] 4.2 `git diff --check` 干净；提交信息含上述回执与 revision；不触碰
      `deerflow/`、`openspec/specs/`、governance 检查器与 `_backlog/`。
