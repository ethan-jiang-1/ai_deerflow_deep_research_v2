## 1. 测试先行：model 前输入失败有界终止

- [x] 1.1 `tests/graph/test_wave2_synthesis_real.py` 新增用例：state 的
      `wave1_open_questions` 含 accepted Wave1 记录中不存在的 question id →
      断言返回 `route=exhausted`、`terminal_status=blocked`、incident 的
      `validation_category == "synthesis_question_coverage_invalid"`、不抛异常
- [x] 1.2 新增用例：`wave1_open_questions` 投影条目非法（非 ref/非 dict）→
      同上 bounded 结果，`validation_category ==
      "wave1_open_question_projection_invalid"`
- [x] 1.3 运行新用例确认红（当前实现抛裸 ValueError）

## 2. 实现修复

- [x] 2.1 `wave2_synthesis/node.py`：`run()` 的 model 前输入推导段
      （topic_registry → build_synthesis_prompt）包
      `try/except ValueError` → `NodeProblem(code=OUTPUT_STRUCTURED_INVALID,
      phase="wave2_synthesis", certainty=DIRECT, validation_category=...)` →
      `_exhausted_update(...)`；`validation_category` 取 raise 点闭式消息串
      （`synthesis_question_coverage_invalid` 等，须匹配 NodeProblem 的
      `^[a-z]+(?:[._][a-z0-9_]+)*$` pattern），不匹配则回退
      `_synthesis_validation_category`（泛化桶）；CancelledError 显式不吞，
      其余异常保持原传播
- [x] 2.2 ruff 通过；新用例转绿；既有 wave2 测试全部保持绿（happy path 与
      post-model 路径零变化）

## 3. 回归与验证

- [x] 3.1 全量测试：`UV_NO_CACHE=1 make verify`（本机 uv 全局缓存权限限制，
      `UV_OFFLINE=1` 会在 lock-check 失败；等价窄口径：
      `UV_NO_CACHE=1 .venv/bin/python -m pytest tests/unit tests/graph tests/contract`）
- [x] 3.2 `openspec validate fix-wave2-synthesis-bounded-input --strict` 通过
- [ ] 3.3 更新 BUG-046（修复关联指向本 change）；真实 003 验证 run 待跑
