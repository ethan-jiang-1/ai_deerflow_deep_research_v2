# Review: openspec 材料对"修 bug 的 coding agent"的实效 —— 003 战役复盘

> 类型: 反馈/复盘（非执行 plan） | 生成: 2026-08-19 | 证据基底: BUG-047..054 八卡战役——4 个 change 全流程（propose→polish→apply→archive）、2123 测试全绿、真实 003 `RESULT: PASS`
> 评审对象: `openspec/README.md`、`openspec/CONTEXT.md`、`openspec/config.yaml`、`openspec/product/README.md`、`openspec/change-guidance/`（core + local + profiles）、`openspec/governance/`（含 req-registry）

## 一句话结论

**不啰嗦、不冗余——但 mid-flow 最需要的三条机械规则不在我的执行链里，我是从 CLI 错误信息里学到它们的。**
分层本身合理（每个导航文件 ≤45 行、各有明确读者），问题是"需要的时刻发现不了"和"执行链三层互不引用"。

## 实测触点（本次战役的真实记录，不凭印象）

**高频使用**：`openspec` CLI（new / validate --strict / status / archive——核心依赖）；
`polish-openspec-change`、`openspec-archive-change` 两个 skill（流程骨架）；
**specs 本体**（读得最多：MODIFIED 块逐字对齐原场景、`> req:` 行查 ID 占用）。

**全程未读**：`README.md`、`CONTEXT.md`、`product/README.md`、`change-guidance/` 全部、
`governance/README.md`、`config.yaml`。原因：战役中段时工作流已被 plan（用户 codified
的 propose→polish→apply）+ skills 定义，这些"新来者导航"层对 mid-flow agent 无增量信息。
**这是时机问题，不是质量问题**—— newcomers 首次进仓时它们应该有用。

## 咬过我的三处（全部有账可查）

1. **归档校验"MODIFIED 块必须携带全部原场景"咬了 2 次**（final-delivery-node 的
   "Builder-maximal projection stays admissible"、readiness-node 的
   "Builder-maximal evidence stays admissible"）。这条规则只存在于 CLI 错误信息里，
   `change-guidance/core/change-practice.md` 没有写。第二次本可避免。
2. **REJ-009 分配漏登记**：我 grep 了 spec 的 `> req:` 行避开了 REJ-008 撞号，但没查
   `governance/req-registry.yaml`（其规则明说"分配前先查此文件"）→ `check_project_reqs`
   报未登记。且既有 drift（EXI-001/LSA-001/RGL-014/SCR-006 未登记）证明这是系统性缺口：
   **同一事实（ID 已分配）有两个 truth source（spec header + registry），没有任何
   mid-flow 校验桥接**。已补课：REJ-009 登记 + spec header 同步（随本文档提交）。
3. **`config.yaml` rules.proposal 的 `## Change Focus` MUST——我 4 个 proposal 全都没写，
   `validate --strict` 照样全过**。执行链断点：validate 不管 config 规则；
   `check_change_guidance.py` 管，但它不在 config.yaml rules.tasks 的归档前清单里
   （那里只列 make verify / validate --strict / git diff --check）。结果：4 个 change
   全部"合规地"绕过了 Focus Card。这是最值得修的一条——**规则存在但够不着，
   等于给守规矩的人设陷阱**。

另有一个使用层小坑：checker README 声明 0=PASS/1=违规，但用 `cmd | tail` 管道测退出码
会拿到 tail 的 0——我第一次就差点误判全绿。agent 常见错误，值得在 checker 文档加一句
"退出码须直测"。

## 逐材料判定

| 材料 | 判定 | 备注 |
|------|------|------|
| `README.md` / `CONTEXT.md` / `product/README.md` | 无感（但非冗余） | 导航/术语层，mid-flow 无增量；对新会话冷启动应有用 |
| `config.yaml` | **关键规则够不着** | Change Focus MUST 未被 validate/checker 链执行；归档前清单缺 5 个 checker |
| `change-guidance/core` | 缺一条最高频的机械规则 | 场景携带/ID 分配不在内 |
| `change-guidance/local/deep-research.md` | 轻度冗余 | 模块路由表与 `deep_research_harness/AGENTS.md` 重复，双份会 drift |
| `governance/req-registry.yaml` | 设计对、执行断 | 双源无桥接，4 个历史 ID 已 drift |
| specs 本体 + CLI + 两个 skill | **真有用** | 战役骨架，无可挑剔 |

## 建议（按性价比排序，每条独立可立 change）

1. **`change-guidance/core/change-practice.md` 加一节 "Delta mechanics"**（或独立小卡）：
   (a) MODIFIED 块携带全部原场景；(b) scenario 标题是语义锚不得内嵌 ID；(c) 新增
   requirement 需 registry + spec header 双登记。三条全是本次实际踩的坑，各 ~5 行。
2. **config.yaml `rules.tasks` 归档前清单纳入 5 个 governance checker**
   （check_project_reqs/specs/architecture/change_guidance/req_coverage），并注明退出码直测。
3. **ID 分配进 CLI**：`openspec validate` 顺带查 registry——新增 ID 未登记即红。
   长期：registry 与 spec header 单一来源化（其一生成自另一个）。
4. **change-guidance/local 的模块路由表改为指向 `deep_research_harness/AGENTS.md` 单源**，
   本地文件只保留 Deep Research 特有的 Program/Line-budget 内容。

## 待处置的既有 drift（非本次造成，只报不修）

- `req-registry.yaml`：EXI-001、LSA-001、RGL-014、SCR-006 未登记；SCR-006 在
  scripted-real-workflow-debug spec header 里为 foreign ID。
- `check_project_specs`：low-scale-real-auto 2 处 violation。
- `check_project_architecture`：`deep_research_harness/.gitignore` entries 与注册 policy 不匹配。

## 附注

复盘期间发现 `openspec/changes/fix-final-delivery-layout-fragility/`（BUG-053 领域的
后续草稿，含 FID-001/002 delta）在 02:59 新出现——应为并行起草中的活文档，本文档写作时
未触碰。注意它缺 proposal.md，会让 `check_change_guidance` 红。
