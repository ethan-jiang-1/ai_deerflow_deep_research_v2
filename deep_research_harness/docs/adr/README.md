# ADR Index — Deep Research Harness 设计决策索引

> 本文件是 `docs/adr/` 的发现层：一条 ADR 一行，负责回答「这个决策归哪条」。权威正文仍是各 ADR 文件本身。
> 生命周期：current = 现行；superseded = 已被更晚的 ADR 取代；rejected = 明确否决；archived = 已归档不再适用。

## 索引

| 编号 | 一句话结论 | 生命周期 |
|------|-----------|---------|
| 0001 | `real-research.sh` 冒烟测试必须用真实模型/网络跑完一个有界、成本受控的研究并产出可读最终报告才算通过。 | current |
| 0002 | Deep Research 有三个入口（专用 TUI 服务 Primary User、CLI 服务运维/调试、API 服务集成），但必须共享同一研究结果与恢复语义。 | current |
| 0003 | 模型、网络服务、凭据等研究服务配置由 Deployment Owner 拥有，研究旅程不要求用户解读 `.env`/提供商名/内部诊断。 | current |
| 0004 | 例行模型/搜索/网络/进程中断是系统恢复工作，用有界超时/重试/可恢复状态重启，触及安全/成本/证据/可用性上限才交回用户。 | current |
| 0005 | 每次新研究开始前 TUI 展示系统提议的方案并请用户接受或调整（轻量确认），而非技术设置屏。 | current |
| 0006 | 研究意外停止时 TUI 分三层披露：默认 plain-language 结果+下一步、按需安全解释、可复制的脱敏 Support Handoff。 | current |
| 0007 | Durable Research Session 曾是跨重启生命周期权威，现由 ADR-0028 的 Run Bundle 模型取代。 | superseded（被 0028 取代） |
| 0008 | 首个生产范围是单本地用户的 Local-First 部署，先跑通 Run Bundle/恢复/Handoff 再谈多用户/共享/跨设备/远程。 | current |
| 0009 | 完成的研究交付可读 Research Outcome（答案/建议+证据来源+范围假设+局限与不确定性），而非仅终止状态。 | current |
| 0010 | 完成的 Run Bundle 保留可读报告，用户可复制/导出为自包含 Markdown，暂不承诺 PDF/在线分享/协作/多用户发布。 | current |
| 0011 | 每个 LLM 节点是「认知控制程序 + 确定性控制边界」两部分程序：Markdown 不拿执行权限，硬代码不定义认知质量。 | current |
| 0012 | LLM 节点先写一份 Node Cognitive Control Contract，再改 prompt/代码/测试/评估；contract 不是第二运行时权威也不是事后散文。 | current |
| 0013 | 认知评估在独立 `evals/` 系统里跑（不进 pytest），专用 Runner 做 preflight/执行/本地留存，不套质量 rubric。 | current |
| 0014 | 认知评估只报 `pass`/`limited`/`inconclusive`/`failed` 四态，limited/inconclusive 永不静默变成通过的自动测试。 | current |
| 0015 | `evals/` 分两层：Python Runner 只准备环境/执行/冻结客观 Bundle，独立多轮评估 Agent 只做质量判断。 | current |
| 0016 | 评估 Agent 是只读评审活动，不是 runtime Controller/图节点，不能改 prompt/代码/rubric/bundle/状态，也不能自主重跑。 | current |
| 0017 | Node Evaluation Runs 是必需主道（每个 LLM 节点一个 bounded smoke scenario），Flow Runs 是低频集成辅道，互不替代。 | current |
| 0018 | 每次评估 Runner 执行都新建私有隔离工作区+不可变 Bundle，不复用之前 checkpoint/artifacts/输入/bundle 命名空间。 | current |
| 0019 | V1 不加 evaluator 专属运行时 Python 控制/图节点/判定引擎，用 Coding Agent + 版本化 Review Protocol 完成多轮评审。 | current |
| 0020 | Runner 单次声明执行、只报 `completed`/`failed`、无重试/attempt 层级/恢复；再试就再调一次产生独立 Bundle。 | current |
| 0021 | Runner 只接受命名/版本化/注册的 Case，记录声明输入+控制身份、实际输出/artifacts、按时间顺序的 Observation Trace。 | current |
| 0022 | Runner 结束于记录 Bundle+两态状态，从不自动调用/排队/选择评估工作流，由人显式选择是否/何时/由谁提交评审。 | current |
| 0023 | Bundle 是不可变执行证据，每次人发起的评估评审存为独立不可变 Review Record，只引用不修改 Bundle。 | current |
| 0024 | Review Record 记录被评估对象（Bundle/Case/控制版本/Contract/Rubric/Protocol）+评估者身份时间+四态结论+证据/置信度/未知，使结果可复核。 | current |
| 0025 | Contract 定义节点持久认知责任与质量标准，versioned Rubric 为单个 Case 细化标准、只供上层评审读、不是 Runner 输入。 | current |
| 0026 | 认知评估套件放在 `deep_research_harness/` 下，控制权威（`evals/control/`）与执行材料（`evals/runs/`）分离，Runner 在 `src/.../runtime/evaluation/`。 | current |
| 0027 | 确认是模型引导的自由文本对话，但模型只能返回候选；Accepted Research Fact 只来自原请求或确定性校验后的显式用户确认。 | current |
| 0028 | `deep_research_harness` 是下游模块根，Run Bundle 是唯一持久所有权边界，无独立 session registry；取代 0007 的 Durable Session 模型。 | current |

## 负知识（为什么不走某条路）

以下均为 ADR 正文里明确写出的「否定 / 边界 / 不做」陈述（来源编号 + 原句大意）：

- **0001**：preflight 成功、保留的 run record、或部分图进度，三者单独都不算通过冒烟测试。
- **0002**：CLI 的诊断便利不得定义 Primary User 体验；DeerFlow 现有 Terminal Workbench 是 host chat 界面，不是 Deep Research TUI 的 owner。
- **0003**：研究旅程不得要求用户去解读 `.env`、提供商名或内部诊断才能表达/推进研究意图。
- **0004**：技术诊断保留给 Deployment Owner 与 Smoke Test Operator，不变成用户任务；自动化触及安全/成本/证据/可用性上限前不打扰 Primary User。
- **0005**：不做「猜测问题是否足够清晰、以跳过用户评审」的单独启发式——统一确认边界刻意避免它。
- **0006**：Support Handoff 排除凭据、raw prompt、raw 异常堆栈和私有路径；当前契约不允许外部诊断/Journal/Support Handoff 兜底。
- **0007**：Harness 不设独立 session registry（已被 0028 取代，见 0028）。
- **0008**：在完成保留 Bundle/恢复/Handoff 之前，不宣称多用户授权、共享访问、跨设备同步或远程部署行为。
- **0009**：完成态不只是终止生命周期状态；用户不必检查内部 artifacts 就能理解结果边界。
- **0010**：暂不承诺 PDF 导出、在线分享、协作或多用户发布。
- **0011**：硬代码控制不定义认知质量，Markdown 不能拿执行权限——两层互不替代。
- **0012**：Node Cognitive Control Contract 不是第二运行时权威，也不是事后补的散文。
- **0013**：常规确定性验证不收集这些评估运行；Runner 不套质量 rubric，也不声称一次运行证明持久模型质量。
- **0014**：limited 与 inconclusive 结果永不静默变成通过的自动测试；provider/环境失败不误报为认知失败。
- **0015**：Runner 从不评质量；evaluator 从不改动捕获的执行。
- **0016**：评估 Agent 不能修改生产 prompt/代码/rubric/bundle/运行时状态，也不能自主重跑昂贵的评估执行。
- **0017**：Node 道与 Flow 道互不替代。
- **0018**：不复用之前评估的 checkpoint、artifacts、输入或 bundle 命名空间；可移植脱敏不是当前要求。
- **0019**：V1 不加 evaluator 专属运行时 Python 控制、图节点或 Python 判定引擎（延迟到有反复证据证明需要时）。
- **0020**：Runner 无重试循环、attempt 层级或恢复行为；生产节点恢复仍是生产行为，不由 Runner 承担。
- **0021**：Runner 只接受命名/版本化/注册的 Case；只有上层评审解读观测好坏（node MD 控制否则是黑盒）。
- **0022**：Runner 从不自动调用、排队或选择认知评估工作流。
- **0023**：Review Record 只引用 Bundle，不修改它。
- **0024**：评审结论可复核而非脱离的评估者散文。
- **0025**：Rubric 不是 Runner 输入，只有上层评审读它；Protocol 拥有评审方法与输出形态而非 case 质量判据；rubric 散文/权重/阈值/评估指导/认知判断不进 fixtures、模型输入、执行输出或 Runner 状态。
- **0026**：不混 slow-changing 控制权威与 fast-changing 执行材料；`tests/eval/` 仍是确定性 pytest 覆盖而非认知评估套件。
- **0027**：模型只能返回候选，不允许 prompt、模型默认或推断偏好来授权研究范围。
- **0028**：不改名现有 distribution、`deerflow_deep_research` import 命名空间或 `deep_research` public tool；Harness 无持久 active-Bundle 指针、无独立 Run registry；日志/诊断/审计/元数据只能是 Bundle 外的非权威观测（不得确立存在、选择 Run、授权动作、恢复 State 或阻塞新 Run）；飞行中的 writer 从不被直接重写；检测到 Bundle 被删后 fail closed，从不重建该 Bundle 或持久化替代 Run 状态。

## 维护纪律

- 新增 ADR 时同步在此加一行；`check_doc_hygiene.py` 会校验索引与目录一致（无孤儿、无缺项）。
- 生命周期状态只在有明确证据时标非 current；证据写在该条 ADR 内或引用处。
