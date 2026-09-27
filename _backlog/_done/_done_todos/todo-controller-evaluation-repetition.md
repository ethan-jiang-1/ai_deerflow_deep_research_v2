# TODO: controller-evaluation-repetition

> 状态: 已完成（2026-09-27，DONE-010；change `run-controller-evaluation-repetition` 两半全部交付并经协议评审） | 优先级: — | 更新: 2026-09-27 深夜
> 上游: [`todo-agent-support-walkthroughs-and-diagnostics.md`](../_done/_done_todos/todo-agent-support-walkthroughs-and-diagnostics.md) 阶段 0 的 go 裁决（证据表 B-3 行） | 下游: 若证实失败 → 独立 change 下沉最窄 deterministic regression

## 完成结论（2026-09-27 深夜，证据见 change 的 `evidence/controller-evaluation-results.md`）

- **controller（public-controller-direction-loop@v1）：failed ×3**——真模型意图映射不可靠：
  动作 8-12/17、load-before-select 关键判据每轮仅 2-4/17、refine 族场景四轮全败、
  infra_probe 漂移 6 次、一次爆调用预算。后续 seam：先诊断技能不重读是模型选择还是组合
  提示问题，再看方向变更场景。
- **topic-planning（topic-planning-direction-loop@v1）：pass ×3**——节点认知程序在真模型下
  全部满足五项语义判据（边界保持、方向对比、对抗文本 containment、歧义不发明、修复守界），
  对抗性 custom notes 被当纯数据、零工具调用、无路由变更。
- **附带产出**：CES-003 manifest 溯源（code_revision）、两个 live subject、手动 runner、
  两处语料预算校准修正（controller 18→50、topic-planning 7→15，均为从未消费的 v1）。

## Why

阶段 0 走查（change `run-agent-support-evidence-walkthroughs`）确认:专用 Agent 路径的
typed surface 闭合、诚实、禁止动作有运行时强制层,**未测得语义失败**;唯一留下的开放
证据问题是 B-3——"模型在已提交 skill 约束下是否自己选对意图"在本地无任何已记录证据
（`evals/runs/` 为空;案例契约要求 live 外部模型）。这恰是已关闭 plan 阶段 2 的命题,
且其评测路线（注册案例 + fail-closed runner + review protocol）已全部就位。

## Current Direction

- **Preflight（并入自 `todo-adopt-framework-engineering-protocols` 项 2 残余，2026-09-27
  审计）**：eval bundle manifest 记录 **git revision**——每次执行的结果绑定到产生它的
  代码版本（`EvaluationBundleManifest` 现缺此字段；语料 digest 钉住、凭证具名环境变量、
  provider/model/prompt 摘要强制记录均已是既有事实，不重复建设）。
- 先做 controller：复用 `public-controller-direction-loop@v1` 与
  `topic-planning-direction-loop@v1` 的真实 loader/受控模型重复评审;覆盖案例声明的
  17+6 场景（新请求、相关答复、同 Run 方向、status、明确 cancel、歧义停手、
  blocked/unavailable 诚实告知）。
- 每次执行记录案例/控制 digest、模型/配置版本、样本数、预算、实际动作、误选/拒绝/
  澄清、失败与未知;评审用现有 `pass/limited/inconclusive/failed`。
- 可复现失效才下沉最窄 deterministic regression,对照改动前后同一案例。
- selected-live ≠ full-real release 证明;不以样本少强设质量阈值,基线不足报 `limited`。

## Design Questions

- 预算与成本边界:（17+6）场景 × repeat 3 ≈ 69 次 live 执行 + 协议要求的人工评审,由人批准后才排期。
  最佳触发时机:controller 相关面（skill/prompt）要改动之前,或要对外做质量声明之前——
  首跑即建立基线,后续改动才有"before"可比。
- ~~与 protocols todo 的"评测可复现协议"相交,先定 owner 与去重~~ **已裁决（2026-09-27
  审计）**:本卡拥有"跑什么与怎么记"——protocols 项 2 的残余（manifest 记 git revision）
  并入本卡 preflight;protocols 卡其余项判定为已存在/停靠,不再构成相交。
- 研究节点质量（wave0/1/2）是否本轮纳入:默认不纳入,除非 controller 层先出结论。

## Non-Goals

- 不重写 prompt、gate 或评测系统;不把 deterministic green 当认知质量;
- 不为"全维度"扩案例;不默跑全链路或输出密钥。

## Next Step

人批准预算与来源边界后,开一个以现有评测路线为唯一 owner 的 OpenSpec change
（先 `openspec explore` 定上述相交 owner 去重）。
