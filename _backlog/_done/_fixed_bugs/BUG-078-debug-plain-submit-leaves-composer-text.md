# BUG-078: debug 工作台纯文本提交后 composer 不清空——第二次 Enter 重复提交同一段文字

> 严重级别: P1 | 发现: 2026-09-29 | 状态: 已修复（2026-09-29，change `debugger-hitl-conversation-visibility`）

## 症状

live 窗口（bundle `b_EHlhgNio…`，2026-09-29）观察到的"你: …"回显重复两次、仅一个
"✓ hitl1 提交"：`scripts/demo_tui.py` 的 `on_input_submitted` 在 debug 模式纯文本
路径（非 slash 命令）echo 之后**不清空 composer**——所有 slash/转义路径都清空
（`self.query_one("#composer", Input).value = ""`），唯独普通文本不清。第二次
Enter（双击回车/按键重复/操作者以为没提交又按一次）会把同一段文字原样再提交一遍。

## 危害（不只是回显重复）

第二次提交按**提交时刻的新姿态**路由（`_debug_command` 每次现读 session）：

- 姿态已回到 `awaiting_hitl`（上一条答案被消费但未被接受、节点重问）→ 同一段
  闲聊文字**再消费一轮答案**（现场实证：三条元问题各烧一轮，accepted 轮次耗尽前
  flow 永远停在 hitl1）；
- 姿态已推进到 `paused_at_boundary` → 第二次提交变成 `advance_one`，**静默推进
  一个节点**（embedded 组合下可能直接烧一次真实模型调用）。

两条路径都发生在操作者毫无察觉的情况下（唯一可见信号就是回显多了一行）。

## 根因

`on_input_submitted` 纯文本 debug 分支只 echo + 派发 worker，漏掉与 slash 路径
一致的 composer 清空。清空后第二次 Enter 变为空提交：awaiting_hitl 下打印
"等待 HITL 输入"提示（无害），paused 边界下是 runbook-030 的既定单步节奏
（操作者可预期）。

## 复现

无头红环（修复先行）：`tests/integration/test_demo_tui.py` 的
`test_debug_plain_submit_clears_the_composer`——fixture 调试器推进到 hitl1，
composer 输入回答 + Enter，断言 `composer.value == ""`；修复前残留原文（红）。

## 修复关联

change `debugger-hitl-conversation-visibility`（Stage 1）一并交付；同场的
"已有活跃调试会话/用法"成对消息经无头单击验证为操作者连点（每路径每调用只写
一次），不在本卡范围。
