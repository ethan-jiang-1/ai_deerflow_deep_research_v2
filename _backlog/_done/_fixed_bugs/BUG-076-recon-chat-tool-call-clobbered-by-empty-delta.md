# BUG-076: 侦察聊天首个工具调用轮次死于 ValidationError——DeepSeek 流式空尾部增量覆盖真实调用

> 严重级别: P1 | 发现: 2026-09-28 | 状态: 已修复（2026-09-28，change `repair-embedded-tui-first-live-defects`）

## 症状

embedded 真实 TUI（020 侦察模式）里对侦察助手说话（如「可以执行 ls 看看目录吗？」），
模型发出 tool_call 的轮次直接失败，屏幕只显示 `（侦察对话调用失败: ValidationError）`
——异常消息被 `except Exception` 吞掉，只剩类型名。

## 根因

`scripts/demo_tui.py` `_stream_turn` 的工具调用累积逻辑 vs DeepSeek 真实流式形状
（2026-09-28 无头复现实测，假模型逐字重放）：

1. DeepSeek 在真实 tool_call 增量
   `{name: "list_workspace", args: {}, id: "call_00_…", type: "tool_call", index: 0}`
   之后，会在**同一 index** 再发一个**空尾部增量**
   `{name: "", args: {}, id: None, type: "tool_call", index: 0}`；
2. 按 index 累积 `tool_calls[index] = call` 让空增量**覆盖**真实调用；
3. `ToolMessage(tool_call_id=call.get("id", ""))`——键存在且值为 `None`，`get`
   默认值不生效 → pydantic `ValidationError: tool_call_id Input should be a valid string`。

裸模型 `ainvoke` 不走这条流式解析路径，所以只有 astream 的侦察聊天触发。

## 复现

embedded TUI 侦察模式说一句会触发工具的话；或直接重放
`tests/unit/test_demo_tui_recon_stream.py` 的假模型 chunk 序列（修复前红）。

## 修复关联

change `openspec/changes/repair-embedded-tui-first-live-defects`：流式循环提取为
模块级 `_stream_chat_turn`（可单测、零网络假模型），跳过无名无 id 的空增量、
`tool_call_id` 对 `None` 降级为 `""`；侦察失败行带上异常首行消息（不再只报类型名）。
