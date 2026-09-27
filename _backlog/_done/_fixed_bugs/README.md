# Fixed Bugs Index — 已修复 bug 归档

> 最后更新: 2026-09-27（关闭 BUG-070 调试工作台下一节点投影） | `_backlog/_done/_fixed_bugs/` — 已修复 bug 的归档目录。
> 接收来自 [`../../bugs/`](../../bugs/) 的 bug。`_` 前缀 = coding agent 默认忽略。
>
> **本目录是 bug 编号的唯一权威来源——新 bug 的编号 = 已分配的最大编号 + 1（已修复目录 ∪ 活跃目录）。**

## 接收一个修完的 bug

bug 修完后从 `_backlog/bugs/` 通过 `git mv` 移入本目录：
1. 在本文件表格加一行（ID + Date + Title）
2. 更新下面的 "Next available bug ID"
3. 更新 `../../bugs/README.md`（删掉该 bug）
4. 更新 `../README.md`（计数 +1）

---

| ID | Date | Title |
|----|------|-------|
| BUG-001 | 2026-07-23 | HITL1 localized intake and explicit confirmation |
| BUG-002 | 2026-07-23 | Retained run diagnostics are actionable |
| BUG-003 | 2026-07-23 | Real CLI run state is observable |
| BUG-004 | 2026-07-23 | LangGraph checkpoint msgpack registration |
| BUG-005 | 2026-07-23 | Wave0 real worker failure classification is no longer opaque |
| BUG-006 | 2026-07-24 | `make demo` 将无效 HITL2 选择误报为协议错误 |
| BUG-007 | 2026-07-24 | HITL2 delegates an agent-led route decision to the user |
| BUG-008 | 2026-07-25 | 真实 demo 的模型超时现在有受限恢复和可操作诊断 |
| BUG-009 | 2026-07-25 | HITL2 zero-tool fixture omits the required Wave2 predecessor |
| BUG-010 | 2026-07-26 | Topic planning timeout is reported as an opaque blocked research run |
| BUG-011 | 2026-07-26 | Completed final delivery skips its gate and loses declared repair routes |
| BUG-012 | 2026-07-26 | Terminal CLI diagnostic reference diverges from its retained run bundle |
| BUG-013 | 2026-07-31 | HITL1 natural confirmation is no longer parsed as profile data |
| BUG-014 | 2026-07-31 | Provider timeout diagnostics identify their observed timeout origin |
| BUG-015 | 2026-07-31 | Provider-terminal inspection command is module-local and executable |
| BUG-016 | 2026-07-31 | Supplied terminal diagnostic references are published before projection |
| BUG-017 | 2026-08-02 | Topic planning 的零工具停止被误报为研究工具失败 |
| BUG-018 | 2026-08-02 | Topic planning 的 provider timeout 未被分类为可恢复错误 |
| BUG-019 | 2026-08-02 | 未指定两条比较路线的研究仍可被确认并启动 |
| BUG-020 | 2026-08-02 | 普通确认语仍依赖模型语义分类，导致 HITL1 不稳定 |
| BUG-021 | 2026-08-02 | 研究语言未绑定到用户请求语言 |
| BUG-022 | 2026-08-03 | 真实研究演示的瞬态 Tavily 读取不再首次失败即终止；历史红绿差分证明两次有界恢复。 |
| BUG-023 | 2026-08-03 | HITL1 brief prompt 不再要求 strict schema 禁止的语言字段；历史 prompt/parser 差分证明契约兼容。 |
| BUG-024 | 2026-08-11 | Wave0/Wave1 的模型可见闭合输出 envelope 使真实 demo 通过受影响阶段，且 Journal 保留脱敏的结构化失败证据。 |
| BUG-031 | 2026-08-16 | 缺少窄而真的三波调试路径 |
| BUG-025 | 2026-08-16 | 进行中的 Bundle 被投影为 `protocol.invalid_result` |
| BUG-026 | 2026-08-16 | Gate fatigue 没有区分失败的工作单元 |
| BUG-027 | 2026-08-16 | Wave1 SourceDiagnostic 提示词漏掉枚举契约 |
| BUG-028 | 2026-08-16 | Wave1 `targeted_search` 没有真正的修复路径 |
| BUG-029 | 2026-08-16 | 非法 critic 输出被静默丢弃 |
| BUG-030 | 2026-08-16 | 真机 demo 长时间运行没有实时人类可读轨迹 |
| BUG-032 | 2026-08-17 | uv 缓存读取 `Operation not permitted` 导致 `make demo-scripted` 等本地命令直接挂 |
| BUG-033 | 2026-08-17 | `_backlog/_local_demo` 真机脚本缺少 `PROFILE`，一跑就报 Usage 错误 |
| BUG-034 | 2026-08-18 | `soft-bundle inspect` 对 mode 002（scripted-real）bundle 永远报 unavailable |
| BUG-035 | 2026-08-18 | wave2 honest gap 两轮补证不收敛导致 003 真实 run 必死于 gate blocked（honest-delivery-and-real-run-diagnostics） |
| BUG-036 | 2026-08-18 | demo_real 终端误报 "Event Journal 记录不可用"（journal 投影只覆盖 provider 分支） |
| BUG-037 | 2026-08-18 | langgraph checkpoint "unregistered type" 警告（bundle 图存储未接应用 serde + Wave1OpenQuestionRef 未注册） |
| BUG-038 | 2026-08-18 | 归档 change（13249bb）遗留 eval digest 漂移，`make verify` 在 HEAD 上红（synthesis.py/tool.py 未刷新） |
| BUG-039 | 2026-08-18 | spec 同步的 wave2 有界终态变更留下期望旧 ValueError 的 workflow 测试（归档前未跑该车道） |
| BUG-040 | 2026-08-18 | wave2 修复提示词缺 open-question 处置契约，覆盖类语义错误只能盲修（wave2-synthesis-validation-feedback-contract） |
| BUG-041 | 2026-08-18 | wave2 有界终态吞掉具体验证类别，诊断只剩笼统 output.structured_invalid（wave2-synthesis-validation-feedback-contract） |
| BUG-042 | 2026-08-18 | soft-bundle blocked 终态后不绑定 bundle，inspect/status/verify/phases 全部不可用（soft-bundle-bind-blocked-run-bundle） |
| BUG-043 | 2026-08-18 | wave2 初始提示词输出契约区分度不足，模型镜像了证据里的 wave1 claims 形状（wave2-synthesis-validation-feedback-contract） |
| BUG-044 | 2026-08-18 | 003 real-auto 在 wave2 honest gap 上 research.blocked（gate_blocked），未按 runbook 5.1 降级为 completed（fix-readiness-degraded-route） |
| BUG-045 | 2026-08-18 | targeted_evidence worker 未排序 source_refs，候选校验必败（fix-targeted-evidence-worker） |
| BUG-046 | 2026-08-18 | wave2_synthesis model 前阶段裸 ValueError 崩溃整个 run（fix-wave2-synthesis-bounded-input） |

| BUG-047 | 2026-08-19 | readiness/final_delivery critic 信封与构建器上限算术矛盾（fix-request-envelope-coherence） |
| BUG-048 | 2026-08-19 | 观测性缺口：admission 操作数/策略信封/critic 兜底/usage/调用序号（run-forensics；第 7 项 follow-up） |
| BUG-049 | 2026-08-19 | wave2 objective 构建超限——44,800 字节封顶推导（fix-request-envelope-coherence） |
| BUG-050 | 2026-08-19 | 节点预算耗尽绕过降级——gate 预算 hand-back（honest-degraded-delivery） |
| BUG-051 | 2026-08-19 | wave1 open-question id 碰撞类型化 + 同文本去重（honest-degraded-delivery） |
| BUG-052 | 2026-08-19 | rerun 摧毁先前 bundle——改为归档保留（preserve-failed-run-bundles） |
| BUG-053 | 2026-08-19 | final_delivery 退化计划确定性渲染不走 composer（honest-degraded-delivery） |
| BUG-054 | 2026-08-19 | 高置信 findings 规则化为结论不被 critic 否决（honest-degraded-delivery） |
| BUG-055 | 2026-08-19 | final_delivery layout 回显 3/3 拒绝致 blocked——归一化+降级+观测（fix-final-delivery-layout-fragility） |
| BUG-056 | 2026-08-19 | readiness 零工具 conformance fake store 未跟随结构性读取扩展（94c8087 已修） |
| BUG-057 | 2026-08-19 | readiness critic cap fallback 误入 gapless repair 自旋——披露降级交付 + 闭合观测 |
| BUG-058 | 2026-08-19 | wave1 source-diagnostic critic bool 字段被真实模型字符串标签击穿，004 必然 blocked（fix-wave1-critic-label-shapes） |
| BUG-059 | 2026-08-19 | wave2 synthesis 别名映射不收录 evidence 内 claim_id，模型引用 claim 被拒（fix-synthesis-claim-ref-aliases） |
| BUG-060 | 2026-08-21 | Demo TUI 把 composer 输入一律按 text 提交，hitl1 language CHOICE 轮无法被合法回答（fix-demo-tui-choice-option） |
| BUG-061 | 2026-08-25 | Demo TUI 缺少 010 自动全跑入口——无 `--auto`/`--scripted` 开关，TUI 一层无法复现 scripted 自动形态（add-demo-tui-auto-entry） |
| BUG-062 | 2026-08-30 | wave2_synthesis 单次 provider.timeout（wall-time 16m22s）无重试即全 run 终局 blocked——瞬态超时拆出 budget-class、预算内有界重试（close-provider-timeout-budget-handback） |
| BUG-063 | 2026-08-30 | HITL interrupt 挂起被 journal 记为 internal.unexpected——挂起/崩溃分类学修正（add-suspended-run-recovery） |
| BUG-064 | 2026-08-30 | 断网/进程死亡无 attach/resume 入口——孤儿 legal_next_action=RESUME + checkpoint 续跑 + TUI attach + 诊断锁（add-suspended-run-recovery） |
| BUG-065 | 2026-08-31 | wheel 排除契约测试全树冷缓存并行首跑一次性假红——`uv build` timeout 60s 在满载下不够（负例控制坐实失败通路），提至 300s |
| BUG-066 | 2026-08-31 | 架构治理检查器干净树即红——`.gitignore` `.uv-cache/` 未同步进 manifest `[ignored_paths]`（sync-structure-registry-ignore-entries） |
| BUG-067 | 2026-09-02 | 治理 closeout 门干净树即红——scripts 重组在两份 README 留下字面 `openspec/` token（依赖方向字面扫描误报）+ PRS-022 无 `@impl` evidence docstring（随 Cpre closeout 解阻修复，零契约面变更） |
| BUG-068 | 2026-09-12 | 归档的两条调试 requirement 缺少确定性证据，closeout 门在干净树即红——LDD-005 的 topology guard 无测试，LDO-008 漏标 `@impl`（repair-debug-requirement-evidence） |
| BUG-069 | 2026-09-27 | 调试工作台 attach/replay 意图未消费、RED-014 三入口未落地——现以 `_debug_attach`/`_debug_replay` 消费 CLI 意图，按钮/slash/启动参数三入口等价（含按钮后归焦 composer），`make tui-journey` 逐步断言 |
| BUG-070 | 2026-09-27 | 调试工作台"下一节点"投影恒空——trace frame 不携带 next_nodes，且该投影字段被卷进 `BoundaryCursor.token()` 写许可导致命令判 `stale`；改为从图状态 `post.next` 线程化进游标，token 只留 durable boundary 身份 |

| BUG-071 | 2026-09-27 | 调试工作台 RED-013/RED-014 剩余面全部交付——无参 chooser、Node Context 分栏+coverage strip、attach 候选面+姿态、命令面板归一、Files 分栏（change `complete-debugger-workbench-conformance`）；过程中 harness 抓到两个真实缺陷（候选布局、符号链接根 ValueError）并修复 |

| BUG-072 | 2026-09-27 | 操作员清册把已取消 bundle 报成 resumable（根因：调试路径从不发布 lifecycle observation，摘要停在建立事实）＋演示 CLI 测试耦合工作区现场——驱动与恢复取消改为发布观测（LDD-003 同普通运行），演示适配器新增可注入根 `DEERFLOW_DEMO_BUNDLE_ROOT`，测试密封；真实工作区端到端验证报告 59 terminal / 0 non-terminal |

| BUG-073 | 2026-09-27 | 调试驱动 stop policy 三处缺陷：`drive_until` 无视 `stop_on_hitl`（实测一次命令 `_advance` 64 次重入等待节点）、pending pause 返回 `None` 致调用方崩溃、并发 pause 被 `_invoke_once` 静默清除——均已修复并加回归（change `expose-debugger-pending-request-and-capabilities`） |

| BUG-074 | 2026-09-28 | [BUG-074-periodic-entry-scenario-fails-on-credential-free-machines.md](BUG-074-periodic-entry-scenario-fails-on-credential-free-machines.md) | periodic 入口环境场景的 launcher 断言不可能状态(清凭据却断言就绪);经 change `fix-periodic-launcher-credential-bounded` 修复——方案 A(假凭据)被实测否决(topic_planning 真打 API 401),落方案 B(诚实 not-ready 断言);entry-environment workflow 取得史上首个绿灯。 |

**Next available bug ID: BUG-075**

---

## Suspended (未修复，仍在排查)

悬挂 bug 放在 [`../_suspended_bugs/`](../_suspended_bugs/)，尚未确认修复。此处不列。
