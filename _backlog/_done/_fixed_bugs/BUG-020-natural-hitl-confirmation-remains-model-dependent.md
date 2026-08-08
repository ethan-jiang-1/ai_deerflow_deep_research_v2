# BUG-020: 普通确认语仍依赖模型语义分类，导致 HITL1 不稳定

> 严重级别: P1 | 发现: 2026-08-02 | 状态: 活跃

## 症状

界面提示用户可以直接确认当前提案，但普通文本确认（例如“可以，我觉得你说的挺好”）
不会直接触发可信的 `accept_suggestion` action。它还会调用模型进行语义分类，并可能
重试或返回新的 HITL1 suspension。

诊断期间的新鲜 run 在 HITL1 的模型调用先经历 provider timeout/retry；随后自然确认文本
未能稳定推进到 topic planning，而是再次停在 HITL1。数字控件可绕过这条模型分类路径，
但用户无法从自然语言交互中获得同样的确定性。

## 根因

对完整 proposal 的任意 text response，HITL1 都调用 `_classify_proposal_reply()`；
该函数最多执行三次独立的 zero-tool model 调用。没有在模型之前识别有限的中英文
明确确认语，也没有把 visible control 作为首选、无网络的确认通道。

现有自然确认测试由 fake model 直接返回 `accept_current_proposal`，且测试注释已明确
该 fixture 不证明 live language quality。

## 影响

- 最简单的确认动作变成 provider 可靠性和模型判断问题。
- 用户会看到重复澄清、等待或终态，而不是确认后立即推进。
- 中文用户尤其容易把“可以”“好的”“按这个来”等常用语当成明确确认，但系统无法保证。

## 复现

1. 运行 real demo，得到完整 HITL1 proposal。
2. 输入“可以，我觉得你说的挺好”。
3. 比较此路径与输入 `1` 选择 visible control：前者会进入 semantic model invocation，
   后者发出 typed action。

回归测试应覆盖有限的明确确认词（中文和英文）直接转换为 trusted action，且断言该路径
不构造 node-agent request；修改、提问和模糊回复才进入受限 semantic intake。

## 修复关联

尚未创建 OpenSpec change。应作为 human-interaction contract 的 follow-up：保留模型对
修改/问题的解释能力，但把常见明确确认的解析和 visible-control action 绑定做成确定性、
本地可验证的路径。该项与 BUG-019 的范围决策门槛需要共同设计。
