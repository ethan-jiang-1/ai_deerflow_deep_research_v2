# Tasks

## 1. 红环先行（bug 与行为缺口）

- [x] 1.1 `tests/integration/test_demo_tui.py` 新增
  `test_debug_plain_submit_clears_the_composer`（BUG-078）：fixture 调试器推进到
  hitl1，composer 输入回答 + Enter，断言 `composer.value == ""`；再按一次 Enter
  断言日志无第二次 `你:` 回显、无第二次 `✓ hitl1 提交`。先跑红。
- [x] 1.2 同文件新增 `test_debug_hitl_stop_renders_card_not_payload`：推进到
  hitl1，断言停点渲染含 `→ 等待 hitl1 输入` 首行 + 有界注记/卡片行，且日志中
  **不出现** `context_schema_version` / 原始 context JSON 片段。先跑红（现状
  倾倒 JSON）。
- [x] 1.3 同文件新增 `test_debug_hitl_feedback_and_consumption_visible`（mount
  上下文内直调 `_log_debug_action`，合成带 `prompt`/`last_feedback` 的
  `PendingRequestView`）：断言 `hitl1 回复: <message>` 与
  `回答已消费 · 未被接受 · 剩余 N 轮` 行渲染。先跑红。
- [x] 1.4 `tests/integration/test_debug_driver_matrix.py` 新增投影断言：schema
  context 请求 → `pending_request.prompt` 字段齐全；interrupt 无 interaction 而
  state 有 `interaction_feedback` → `last_feedback` 来自 state。先跑红。

## 2. 投影与契约（green）

- [x] 2.1 `runtime/run_experience.py`：提取模块级
  `project_hitl1_prompt(request, *, request_id) -> PromptView`，`_hitl1_prompt`
  委托；行为不变（既有 run_experience 测试全绿）。
- [x] 2.2 `domain/debug_driving.py`：`PendingRequestView` 增加
  `prompt: PromptView | None = None` 与
  `last_feedback: InteractionFeedback | None = None`（默认 None，加法兼容；
  确认无循环 import）。
- [x] 2.3 `runtime/debug_driver.py::_pending_request_view`：填充 `prompt`
  （调用 2.1 投影）与 `last_feedback`（interaction 优先 → durable state 回退，
  回退读取在构建快照处以只读方式完成，构造失败即放弃不造权威）。
- [x] 2.4 `scripts/demo_tui.py`：
  - `_log_debug_action` awaiting_hitl 分支卡片化渲染（goal/proposed_scope/
    missing/rounds/guidance/example/options；无 card 时 title/mode + 有界注记；
    删除原始 context 倾倒；去重键不变）；
  - `_render_debug_result`：answer 后同节点 awaiting_hitl 再停 → 消费反馈行
    （剩余轮次缺省时省略）+ `hitl1 回复:` 行（有 `last_feedback` 时）；
  - `on_input_submitted` debug 纯文本分支：echo 后清空 composer（BUG-078）；
  - `/help` 与停点文案明示 `确认`/`confirm` 与 `字段: 值` 修订格式。

## 3. 登记、门禁与收尾

- [x] 3.1 登记 `LDD-006`、`RED-015` 进 `openspec/governance/req-registry.yaml`
  （一行式条目，跟既有格式一致）。
- [x] 3.2 窄验证：`uv run --offline pytest tests/integration/test_demo_tui.py -k "debug" tests/integration/test_debug_driver_matrix.py`（红→绿后各跑一次留回执）；
  再 `make tui-journey`、`make debugger-proof`。
- [x] 3.3 全量门禁：`UV_OFFLINE=1 make verify`（deep_research_harness/ 下）；
  仓库根 `python3 openspec/governance/check_project_gate.py --phase closeout`；
  `openspec validate debugger-hitl-conversation-visibility --strict`。
- [x] 3.4 确认 `openspec --version` 与 `.agents/skills/*/SKILL.md` 的
  `generatedBy` 对齐（不对齐则记录 drift 并处置）。
- [x] 3.5 归档：`openspec archive debugger-hitl-conversation-visibility`
  （先 sync/validate，绿后归档）；BUG-078 卡按 ritual 迁
  `_done/_fixed_bugs/` 并更新三处账本计数。
- [x] 3.6 提交分层：`feat(demo)`/`fix(demo)` → `archive(change)` →
  `backlog(账本)`；push 前需用户点头。
