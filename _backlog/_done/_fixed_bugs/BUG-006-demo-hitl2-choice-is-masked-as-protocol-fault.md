# BUG-006: `make demo` 将无效 HITL2 选择误报为协议错误

> 严重级别: P1 | 发现: 2026-07-24 | 状态: 活跃

## 症状

全假独立 CLI 在 HITL2 显示如下可见选项：

```text
proceed: 按当前研究计划继续。
```

将整行粘贴到 `response:` 后，运行以退出码 `1` 停止，并显示：

```text
研究运行返回了无法安全解释的结果。
Next: 不要继续当前运行；请提供诊断引用。
```

同一运行的保留 bundle 仍安全地停在 `hitl2`；它没有损坏检查点或继续图执行。将输入改为纯 option ID `proceed`，同一路径会完成。

这会让用户把界面直接展示的选择理解为可提交值，同时把可恢复的输入错误误导成不可继续的协议故障。

## 根因

`agent/scripts/demo.py` 将 choice 选项渲染成 `<id>: <说明>`，但交互输入契约只接受精确的 option ID。完整显示行在 `runtime/human_input.py` 被正确分类为 `response_invalid`。

`ResumeResearchHandler.execute()` 捕获该输入错误后返回非 record-bearing 的 denial result，其中 `code=response_invalid`，但 `execution_trace=[]`。`ResearchRunExperience._project_result()` 在按 `response_invalid` 映射为 `input.invalid_response` 之前，先验证新结果的 trace 必须延续本地已知 trace。已到达 HITL2 的本地 trace 非空，因此空 trace 触发 `execution_trace_diverged`，外层捕获后将原本准确的输入错误覆盖为 `protocol.invalid_result`。

现有 scripted demo 测试只提供纯 `proceed`，没有覆盖交互 CLI 中的完整可见选项行或“已有 trace + denial result”的投影路径。

## 复现

```bash
cd agent
printf '%s\n' x 'proceed: 按当前研究计划继续。' \
  | env -u VIRTUAL_ENV uv run --extra operations python scripts/demo.py
```

预期结果：choice 输入的格式应明确为 ID；无效值应保留 `input.invalid_response` 语义并给出可重试的下一步。实际结果：显示 `protocol.invalid_result` 的安全解释错误。

对照命令（将第二个输入改为 `proceed`）以退出码 `0` 完成。

## 修复关联

关联 OpenSpec change：`fix-demo-hitl2-choice-fault`（proposal 已创建）。该 change 同时处理：

- choice CLI 的明确输入提示或兼容的显示行归一化；
- 有既有 trace 时对 `response_invalid` denial 的正确投影，不能掩盖为协议错误；
- 一条交互 CLI 回归和一条共享 run-experience 投影回归，分别锁住用户输入与错误分类。
