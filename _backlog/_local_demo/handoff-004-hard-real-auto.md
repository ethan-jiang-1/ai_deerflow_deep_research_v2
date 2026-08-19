# Handoff: Mode 004 hard real-auto 跑通 + change `hard-real-auto`

> 生成: 2026-08-19 | 用途: 新会话 pick up 后继续（004 收尾 / 后续茬处置）
> 位置: 本文件在 `_backlog/_local_demo/`；设计文档在 `_backlog/plans/hard-real-auto-runs.md`（定稿 v2）；实施载体在 `openspec/changes/hard-real-auto/`
>
> **状态: ✅✅ 完成（2026-08-19 深夜）**。全流程达成：plan v2（D1-D4）→
> change `hard-real-auto` 实施 → runbook-004 → 真实 004 全链 PASS
> （`RESULT: PASS` + 真实比较报告）→ 战役途中按 bug 流程连破两个 P0
> （BUG-058 wave1 critic bool 标签、BUG-059 claim ref 别名盲区，均独立
> change 修复 + 实战验证 + 归档）→ 003 复跑回归无恙 → closeout 六项全过 →
> 三 change specs 同步归档 → plan 归档 CLS-051。004 找茬成果与观察记录
> 见下方。

## 目标（一句话）

**把 mode 004（真实 DeepSeek + 真实 Tavily、全自动、默认意图、固定比较题
`Compare China and US EV battery market in 2024.`）端到端跑通**：
`soft-bundle run --mode 004` → `RESULT: PASS` + `final/report.md` 真实比较内容
（China 与 US 双市场覆盖）+ 多 topic 分解观察记录。004 的定位是**找茬**：
撞出的缺陷按 bug 流程处理是产出，不是失败。

## 与 003 的对照（机制遗产全部继承）

| 维度 | 003（minimal 意图） | 004（默认 None 意图） |
| --- | --- | --- |
| 入口声明 | `profile_intent=minimal`（默认） | `--profile-intent none`（显式不声明） |
| planner | `single_topic` 强制 1 topic | 自由 1–8 topics（`MAX_TOPICS=8`） |
| wave2 gate | 预算解析 → 2 轮 | default 1 轮 |
| final layout | ≤1 结论走确定性免模型捷径 | 多结论 → 真实模型排版路径（首次受压） |
| honest gap | 首耗尽降级 pass + 披露 | 同（大概率 1 轮即耗尽降级——预期路径） |

## 实施摘要（已完成部分）

- **A. 意图 flag**（`scripts/demo_real.py`）：`--profile-intent {minimal,none}`，
  argparse 默认 None-sentinel → embedded-smoke `--scripted` 路由上等价 minimal
  （003 行为字节级不变）；`none` → `StartRun(profile_intent=None)`（默认产品
  路径）；显式选择出现在非 embedded-smoke-scripted 路由 → `parser.error`
  （镜像既有 `--profile` 规则）。测试：`tests/integration/test_demo_real.py`
  3 个新用例（默认 minimal 钉死 / none 省略声明 / 路由外拒绝）。
- **B. mode 004**（`scripts/soft_bundle.py`）：`MODE_QUESTIONS["004"]`、
  `cmd_run` 004 分支（`make demo-real-scripted --question "<比较题>"
  --profile-intent none`，绑定/退出码语义共享 003）、verify report 集合
  `{002,003,004}`、inspect 委托集合 `{002,003,004}`。测试：
  `tests/contract/test_soft_bundle_cli.py` 3 个新用例（run 绑定+意图断言 /
  inspect / verify 要求 report）。
- **C. 文档**：`runbook-004-hard-real-auto.md` 新建（含 6.2 subjects 不对称
  观察点、6.3 layout/预算首压观察点）；README 阶梯表 004 行收口（入口定
  embedded smoke，Gateway 自动化移出 001~004）。
- **验证**：`UV_NOLINE make verify` 全绿（2611 fast + 257 integration + 35
  workflow）；002 零成本回归 `RESULT: PASS`；003 contract 回归 62 passed；
  `git diff --stat` 确认零产品 `src/` 改动。
- **Registry**：`HRA: hard-real-auto` 前缀 + `HRA-001` 描述已注册
  （`openspec/governance/req-registry.yaml`，440 IDs 一致）。

## 真实 004 run 战况（2026-08-19 晚，均为证据）

| 尝试 | bundle | 结果 | 判定 |
| --- | --- | --- | --- |
| 1（nohup 19:09） | `b_D09VbYdM...` | 过了 hitl1/wave0/wave1，死于 wave2_synthesis 中途（无终态） | 环境性：后台进程随工具会话回收（教训：用托管 job）。wave1 通过=当时 critic 恰好返回 bool（BUG-058 是概率性触发） |
| 2（bash-1 19:11） | `b_8bfIc_sJr5...` | wave1 六 attempt 后 `research.blocked` | **BUG-058（确定性触发）**：worker 候选 3/3 通过初始验证，source_diagnostic critic 3/3 解析失败 |
| 3（bash-2 20:27，修复后） | `b_K9OuIvAx...` | wave0 六 attempt 后 blocked（`internal.unexpected`×6） | 环境性：a1 挂 38 分钟（已知 SDK 挂起，runbook §7）；a2-a5 合盖断网快速失败；a6 休眠冻结醒来失败（用户确认合盖断网）。非新产品 bug |
| 4（bash-3 21:12，BUG-058 修复后） | `b_sLVVSNG2v8O9...` | wave0/wave1 **均 a1 一次通过**（BUG-058 实战验证 ✓），wave2_synthesis 初始+repair 双双 `synthesis_finding_backing_ref_invalid` → blocked | **BUG-059（确定性）**：模型把 finding 的 backing_refs 指向 evidence 内真实存在的 `claim:w1_c*`，但 `_evidence_aliases` 不提取 `claim_id` → 语义正确的引用被拒 |
| 5（bash-5 23:04，BUG-059 修复后） | `b_cuTRGqwJysx...` | **全链 PASS**：wave0/wave1 a1 → wave2_synthesis a2 → targeted_evidence → hitl2 → readiness → final_delivery completed，`final/report.md` 真实比较内容 + `RESULT: PASS` | **战役达成**（BUG-059 实战验证 ✓） |

**BUG-059（已修复）**：`wave2_synthesis/node.py::_evidence_aliases` 只提取
`source_id`/`canonical_url`/`support_refs`/`counter_refs`，不提取 `claim_id`
——wave1 evidence 的一等公民实体是 claims（`claim:w1_c1`...），模型引用它们
语义完全正确却落盲区。真实模型复现（bundle 自带 evidence，24KB 预算无截断）：
19 findings 中 14 个 source_id ref 合法、6 个 `claim:w1_*` 全部落盲区。修复：
提取键加 `claim_id`（一处），伪造 claim id 仍 fail-closed。change
`fix-synthesis-claim-ref-aliases`。

**观察（004 找茬成果）**：一晚连破两个真实形状缺陷（BUG-058 wave1 critic
bool 标签、BUG-059 claim ref 别名盲区）——都是 003 单 topic minimal 路径
踩不到的盲区，印证 004"多结论自由路径找茬"的战役价值。另记环境事实：
`uv build` 契约测试（test_production_wheel_excludes_fixture_package）因
`~/.cache/uv/sdists-v9` 权限（macOS provenance xattr）在**干净树上同样失败**
——环境问题非代码回归，与战役无关，另行处理。

**BUG-058（已修复）**：wave1 source-diagnostic critic 的 `marketing_risk`/
`cross_verification_need` 契约要 bool，wave1 prompt 未声明 boolean（targeted
critic 有 bounds 声明而 wave1 漏了），真实模型返回 `"low"` 标签 → pydantic
ValidationError → 掩码成 `wave1_review_output_invalid` → 必然 blocked。修复
（change `fix-wave1-critic-label-shapes`）：契约边界闭合标签映射（high/yes/
true/elevated/needed/required→true；low/none/no/false/minimal/minor/unlikely/
not_needed→false；medium 等越界值 fail-closed）+ wave1 prompt 补 bounds 声明
（对齐 targeted 先例）+ critic 失败码拆分（`wave1_review_output_shape_invalid`）。
真实模型复验：prompt 声明后模型直接返回 bool，双保险生效。

## 待办（pick up 起点）

**全部完成（2026-08-19 深夜）**：

1. ✅ **4.3**：run #5 全链 PASS（上表）；观察已录——subjects 不对称依旧
   （`['China', 'US EV battery market in 2024.']`）但 findings/gaps 双市场
   覆盖无实际伤害（D2 观察结论：记录不预修）；planner 在自由 1–8 topic
   下实际产出 1 个 wave0 + 1 个 wave1 work unit（topic_registry 空，观察
   点 6.1 结论：广度观察而非断言）；报告诚实披露 3 个 unresolved gaps +
   readiness critic 无可采信 verdict（honest 路径符合 HRA-001 预期）。
2. ✅ **4.4**：003 复跑 PASS（minimal 意图生效：`depth=quick_overview`/
   `cost=minimal` vs 004 空 + degraded——参数化无回归；1 wave0 + 1 wave1
   work unit 单 topic 契约保持；terminal completed）。
3. ✅ **5.2**：closeout 六项 checker 全过（途中修两处治理：nodes 层
   `pydantic` 导入授权入 project-structure.toml；测试 docstring 的
   `@impl` 行不能带 `BUG-05x` 字样——ID 正则会当 requirement 扫）→
   `make verify` 全过 → 三 change strict validate → delta specs 同步
   入主 specs（55 个全过）→ 三 change 归档
   `archive/2026-08-19-{hard-real-auto,fix-wave1-critic-label-shapes,
   fix-synthesis-claim-ref-aliases}` → plan 归档
   `_closed_plans/CLS-051-hard-real-auto-runs.md` → 本文件 ✅。

## 必须知道的坑（本战役新增）

1. **后台跑真实 run 要用托管 job**：bash 工具 `&`+nohup 启动的进程会在
   工具会话结束时被回收（首次 004 因此死于 wave2）；用 `run_in_background`
   参数（job id + `job_output` 收集）。
2. **003/004 不能并发跑**：每次 `run` 先清空 operator workspace 的 run
   bundles（control-environment 设计），并发会互相清场。
3. **UV 全量门要带 `UV_NO_CACHE=1`**：uv 缓存 sdists 权限问题（README 避坑
   节既有记录，`make verify` 的 lock-check 同样受影响）。
4. **kernel Focus Card 格式已演进**：字段必须 `**字段名:**`（冒号在粗体内）
   + 值同行非空 + seam classification 裸值 + canonical 策略名
   （`change-admission` 等）；003 时代的旧格式会被 plan gate 拒绝。

## 会话语境（简短历史）

003 战役完结（handoff-003 ✅✅）→ 用户指出 README 阶梯还有 004（一行占位）→
考古确认 004 = 默认意图比较题找茬 → plan v2（D1 None 意图 / D2 subjects 先跑
观察 / D3 `--profile-intent {minimal,none}` / D4 003 双保险回归，四项用户
收敛）→ change `hard-real-auto`（3 delta specs + HRA-001）→ polish 3 pass
ready → 实施至 4.3（真实 004 首跑进行中）。
