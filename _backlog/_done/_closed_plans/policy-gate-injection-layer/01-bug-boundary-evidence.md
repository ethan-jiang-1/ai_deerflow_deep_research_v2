# 历史 Bug 证据：为什么需要 Control Placement，而不是更多局部补丁

> 主计划：[`../policy-gate-injection-layer.md`](../policy-gate-injection-layer.md)
> 语料范围：`_backlog/_done/_fixed_bugs/BUG-001…012` 与 `_backlog/bugs/BUG-013…016`
> 方法：逐卡读取症状、根因、复现、修复关联，并用对应 Git history 核对关键回归链。
> 结论状态：支持一个**有边界的架构诊断**；不构成全量 regression 统计，也不定义 runtime 行为。

## 1. 要纠正的表述

原案的直觉并非无中生有：最近的 bug 语料确实反复显示，团队在一个已经存在的
semantic / authority / projection 边界上继续加 parser、adapter、gate 或 state 时，常常只修到
一个可见 consumer，随后在相邻路径重新暴露问题。

但更精确的说法不是“传统代码都使错了”或“所有判断都应放 prompt”：

> **已观察到的反复模式是：实现首先需要回答一个有界问题究竟属于认知候选、人类取舍、直接事实、
> deterministic admission、route，还是 projection；没有先回答时，局部修复容易复制 authority、
> 放宽错误 gate，或把需要理解的交互压成 token/parser。正确的落点有时是 bounded cognition，
> 有时恰恰是更窄、更直接的 deterministic owner。**

这正是 `control-placement` 想在 proposal 阶段留下的 review 问信息。它不预设答案是
“prompt”。

## 2. 语料与证据边界

| 项目 | 可证明 | 不可证明 |
| --- | --- | --- |
| 12 张归档卡（`_done/_fixed_bugs/BUG-001～012`） | 过去已经记录和处理的具体 failure / route / projection / fixture 缺口；部分卡记录了最小回归 seam 和 fixing change | 每一张卡的修复一定是唯一或最优解；卡之间可当作独立统计样本 |
| 4 张活跃卡（BUG-013～016） | 当前保留的真实症状、已定位根因、建议的 owner/约束 | 尚未完成的修复已被验证，或所有计划方向都会成功 |
| `git log` 与 `git show 2784429` | BUG-011/012 与 `harden-deep-research-workflow-outcomes` 同一 change 的演进关系；一个 broad guard 曾真实破坏 existing final-delivery gate | 单一 commit 的规模或文件数本身就是质量指标 |
| `test-fast.xml` 的 `2150` | 当前报告含 2150 个 test cases | “2000+ regression”数量或架构根因的比例 |

因此后续 baseline 不从“是否存在模式”开始；案例已经证明模式**存在**。baseline 要回答的是：
它覆盖多少历史 lineage、哪些是 policy 的反例、以及新机制是否真的让早期设计决策改变。

## 3. 已审计的关键 lineage

### 3.1 BUG-001 → BUG-013：字符串/传输修补不等于理解人的确认意图

| 证据链 | 当时修到的层 | 后续暴露的缺口 | 对 placement 的教训 |
| --- | --- | --- | --- |
| BUG-001 修复中文 profile 值、显式“采用建议”操作和零识别反馈；BUG-013 现场输入自然的“确认”仍在三轮后被 `input.invalid_response` 阻断 | parser、adapter 与 correlated typed action；这些 deterministic boundary 本身仍正确 | “确认”处在完整 proposal 之后，是有界的人类语义；把它继续当 profile 字段，或只加同义词，都会把表达意图和合法 state transition 混为一层 | 先分开 `semantic interpretation` 与 `graph admission`：前者只能给封闭 intent candidate，后者仍验证 current proposal、correlation、policy 和 state transition。不能让自由文本直接变 action |

BUG-013 链接的 `deep-research-semantic-hitl-ux-analysis.md` 已明确提出相同边界：
`确认` 的候选含义不等于授权 action；stale / 未广告 action 则仍必须 fail closed。它支持
“需要一个认知/解释位置”的判断，却**不证明必须使用某个 LLM**；实际 owner 应由 future capability
contract 决定。

### 3.2 BUG-006 → BUG-007：先问人是否真的应该做这个决定

| 证据链 | 当时修到的层 | 后续暴露的缺口 | 对 placement 的教训 |
| --- | --- | --- | --- |
| BUG-006 修正了可见 menu 行被输入后从 `response_invalid` 错投影为 `protocol.invalid_result`；BUG-007 随即指出：即使报错正确，用户仍被要求对没有研究上下文的内部 graph route 选择 | presentation / error projection | “把菜单输入正确”没有回答“这个 route 是否应由人选择”；fake HITL2 把 agent/graph 已拥有或根本不存在的分析取舍转嫁给用户 | 先识别真实的人类贡献：偏好、授权、不可逆 trade-off 才进入 HITL；可由已验证状态推导的 route 应由 Agent/graph 完成。人可见文本不是 route authority |

这条链是反例：问题不是把更多自然语言塞给用户，而是减少不正当的人类决策面。它要求
`human-interaction-integrity` 与 `control-placement` 组合 review。

### 3.3 BUG-008 → BUG-010 → BUG-014：局部 retry / presentation 不能替代共享事实 owner

| 证据链 | 当时修到的层 | 后续暴露的缺口 | 对 placement 的教训 |
| --- | --- | --- | --- |
| BUG-008 在 HITL1 为直接 `provider.timeout/unavailable` 建立一次 bounded recovery、事件和可执行 fresh-start；BUG-010 发现 topic planning 使用同一 30 秒 policy 却丢失 timeout，降格为泛化 `research.blocked`；BUG-014 又发现 `provider.timeout` 本身无法区分 bridge deadline 与 SDK timeout | 先是 node-local recovery / presentation，后转为 workflow-outcome 与 bridge observation | 相邻 Node Agent / lifecycle consumer 没有消费同一个足以决策的 direct observation，或将其重投影成更弱的 generic result | timeout origin 是 bridge 可直接判定的闭合事实，应由 `ProviderObservation` / deterministic pipeline 保留；HITL、topic-planning、terminal、inspect 只消费各自合法 projection。不要让每个 node 再造 timeout authority |

这不是 prompt 应拥有的内容。它是“复用 direct fact、不要新建平行 state/gate”的正向例子。

### 3.4 BUG-011：为一个 terminal 情形加 broad guard，吞掉另一个既有 gate

BUG-011 是当前语料中最直接的 control-placement regression：
`harden-deep-research-workflow-outcomes` 为 non-success direct terminal 引入了
“任何 `terminal_status` 都跳过 gate”的 broad guard；但 completed final delivery 也在
existing final-delivery gate 前设置该 status，因此 repair / evidence_blocked / pass 三条既有
route 被整个跳过。

修复把 bypass 收窄到 **non-completed direct terminal**，保留 final-delivery gate 的既有 owner。
这正是 proposal 应在写代码前回答的内容：

1. 被改变的是哪一个具体 decision / fact？
2. 哪个 existing evaluator / route 已拥有相邻情形？
3. 哪些 legal recovery route 必须保留？
4. broad condition 避免了什么，新增 condition 又会吞掉什么？

仅有常规 test asset 也没有提前阻止这次错误；最终是 full fake graph route sequence
`repair → evidence_blocked → pass` 暴露了它。这个案例应成为新 policy 的 canonical replay case。

### 3.5 BUG-012 → BUG-016：同一 opaque reference 不等于同一份已发布证据

| 证据链 | 当时修到的层 | 后续暴露的缺口 | 对 placement 的教训 |
| --- | --- | --- | --- |
| BUG-012 解决 terminal CLI 与 retained bundle 独立分配不同 `diagnostic_ref`；BUG-016 发现 provider terminal 已带引用时，`RunSessionStore` 因“引用非空”跳过 record 落盘，却仍把该引用投影到 event / summary / view | shared terminal reference allocation | 引用 identity 一致不表示 diagnostic record 存在；presentation 仅比对 view reference 就声称 `session_bundle` | direct fact 是“exact record 已按该 reference 成功发布”；storage writer 先建立它，view/presentation 才可投影 location。任何 adapter file check 都会复制 storage authority |

这条链说明“加字段/引用”经常只是补了一个 projection。policy 必须要求 direct fact、唯一
writer 与 legal recovery；否则下一次会在“已有字段”分支再次漏掉不变量。

### 3.6 BUG-004 / BUG-009 / BUG-015：测试资产必要，但并不自动等于真实契约

| Bug | 表面上的“有测试” | 实际遗漏 | 对证据策略的教训 |
| --- | --- | --- | --- |
| BUG-004 | 日常 flow 未把 LangGraph 未注册 msgpack warning 当失败 | 真实 checkpoint restore 含 custom types；未来 strict mode 会硬失败 | 需要 production-compatible compatibility seam，而非只看当前“能跑” |
| BUG-009 | zero-tool conformance fixture 仍通过旧前提 | production validator 已要求 `wave2_synthesis` predecessor，fixture 却构造非法 empty trace | fixture 必须构造 legal input state；测试不能替代 contract 的 current predecessor truth |
| BUG-015 | integration test 比较了硬编码 inspection command 字符串 | module rename 后用户实际执行的命令无效，字符串断言仍通过 | 对用户承诺的命令，要在声明的工作目录执行 rendered action；“文本相等”不是行为 proof |

它们是“test asset 不够”的确定性版本：并非不要测试，而是要让 evidence seam 和真实 consumer /
environment / legal input 对齐。认知质量还需要 bounded calibration 与独立 review。

## 4. 从案例到本计划的干预目标

这些案例支持下列最小、可反驳的目标：

1. **阻止继续叠加前先显式化 boundary。** 每个触发 change 必须写出 cognitive candidate（若有）、
   direct fact、deterministic owner/evaluator、posture、protected invariant / legal recovery，以及复用或
   避免的复杂度。
2. **保留已有 owner，而非重新发明 controller。** BUG-011、BUG-012/016 与 BUG-008/010/014 都说明
   纠正往往是收窄、复用、重排写入顺序，而不是再加一层 gate。
3. **让语义问题进入可继续的 review loop。** BUG-001/013、BUG-006/007 不能被 table shape 或 unit
   test 裁决；发现要成为 change-local task，再由下一次 apply/closeout review 继续。
4. **用真实案例评估干预。** 先以本文件的 six lineage 作为 replay corpus，允许 policy 无法提前抓到
   某个案例；这种失败是 policy 的反例，不应被改写成“无关 bug”。

## 5. 它仍然不能证明什么

- 不能量化“边界错位”占全部问题或未来问题的百分比。
- 不能证明某个 prompt、模型、fresh-session challenger 或 rubric 会提升所有认知质量。
- 不能把一个 bug 卡的 root cause 泛化为整个 runtime 的唯一 source of truth。
- 不能授权在没有 OpenSpec change 的情况下迁移 runtime 行为、增加 model role、改变 HITL 或 route。

下一轮 baseline 要按 **lineage 而不是卡片数** 分类：一个祖先问题和其后续残留属于同一链；
每条链记录触发 policy 是否本可在设计时提出正确问题、哪些问题仍只能由 live calibration /
fresh-session challenge / human review 发现。
