# BUG-053: 空结论 plan 下 final_delivery 强制模型回显合成 id——退化排序本可确定性渲染，3/3 次拒绝致 run 终局 blocked

> 严重级别: P1 | 发现: 2026-08-18 | 状态: 活跃

## 症状

第四次真实 003 run（bundle `b_M_sAiRI1A43omX_T5zxECtzyzh7HEMD4bpwT7BHSBVk`，诊断引用
`diag_7bde6dfac6bf1d344930e20e`）：

- 前序全部打通（readiness 一次通过、wave2 a3 通过——BUG-047/049 修复生效），
  `final_delivery` 3 次尝试、**模型调用 3 次全部 completed**（事件 84-93，
  14:16:07→14:16:19），但 `final/report.md` 未发布，终态 `research.blocked`
  @ final_delivery，gate 预算 3 轮耗尽。
- `review/report-plan.json` 实况：`writable_conclusions: []`（空）+
  `mandatory_uncertainties: [1 条 "Unresolved research gap gap:gap_1"]`。

## 根因

`final_delivery/composer.py` + `domain/publication.py` 的 layout 合同：

- 空 conclusions + 1 uncertainty 的 plan 要求模型返回**精确形状**
  `{"schema_version":1,"conclusion_order":[],"uncertainty_order":["uncertainty:0"]}`；
- 合成 id `"uncertainty:0"` 是构建器造的，模型对"无可排序项"的自然回答是空列表
  或省略——`admit_layout_candidate` 按 `final_layout_uncertainties_invalid` 拒绝；
- 3/3 次拒绝 → gate 耗尽 → 整个 run 在最后一步 blocked，**此前全部真实研究产出
  （wave0/wave1/wave2 的真实证据与 findings）随之丢弃**。

设计层问题：**0 个结论 + ≤1 个不确定项的排序是完全确定的**（空序列 + 单元素
序列各自只有一种合法顺序），此退化情形根本不需要模型调用，确定性渲染即可——
现在却把 run 的生死押在模型回显一个合成 token 上。

（模型实际返回内容无处可查——观测缺口，见 BUG-048；本卡根因由合同形状 +
"3 次模型调用均成功但零发布"推定。）

## 复现

任一 readiness 判定"无可写结论但有强制不确定项"的 run（honest gap 不收敛的
常态路径）即进入此退化分支；模型只要不精确回显 `uncertainty:0` 即复现。

## 修复关联

待讨论：退化 plan（结论数 + 不确定项数 ≤ 1 时排序唯一）跳过模型调用直接确定性
渲染；或放宽 admission（顺序不合法但集合相同时接受/规范化）。涉及 FID 契约，
建议进 change 评审。

## 修复关联

已由 change `honest-degraded-delivery` 落地（2026-08-18）：实现与回归见该
change 的 tasks/design；真实 003 复跑验证见 runbook §5.1/§7。
